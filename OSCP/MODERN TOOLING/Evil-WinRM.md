# evil-winrm

**What it is:** a full-featured WinRM shell client. Speeds up the remote Windows shell workflow over using raw `winrs` or PowerShell's own `Enter-PSSession` for everything.

**What it replaces / improves over:** `winrs` (basic, no file transfer), raw `Enter-PSSession` (awkward in scripts, no upload/download built in). evil-winrm adds file upload/download, tab completion, Kerberos auth, pass-the-hash, HTTPS support, and pre-loaded scripts (PowerView, PowerUp, etc.) all in one client.

**What it does NOT replace:** understanding why WinRM works, what ports it uses (5985 HTTP / 5986 HTTPS), and what privileges are needed to access it (target user must be in Remote Management Users or local Administrators). Those fundamentals are in [[Windows Privilege Escalation#17.1.2 Situational Awareness|17.1.2]] and [[Password Attacks]].

---

## When to reach for it

- You have credentials (cleartext or NTLM hash) for a Windows user who is in `Remote Management Users` or local `Administrators`
- Target has port 5985 or 5986 open
- You need to upload tools, download output files, or run enumeration scripts -- evil-winrm's built-ins beat wrestling with PowerShell download cradles every time

## Basic usage

```bash
# Password auth
evil-winrm -i <target-ip> -u <username> -p <password>

# NTLM hash (pass-the-hash)
evil-winrm -i <target-ip> -u <username> -H <NTLM-hash>

# HTTPS (port 5986)
evil-winrm -i <target-ip> -u <username> -p <password> -S

# Pre-load a PowerShell script (accessible as a function after connecting)
evil-winrm -i <target-ip> -u <username> -p <password> -s /path/to/PowerUp.ps1
```

## File transfer (from within the session)

```
# Upload to current remote directory (or specify full remote path):
upload /home/kali/tool.exe
upload /home/kali/tool.exe tool.exe

# Download from remote to Kali current directory:
download C:\Path\to\file.txt
download C:\Path\to\file.txt /home/kali/output.txt
```

**Upload path gotcha:** when specifying a full Windows path as the destination (e.g., `upload tool.exe C:\Services\tool.exe`), some versions of evil-winrm mis-parse the `C:\` prefix and produce a malformed path. Safest approach: `cd` to the target directory first, then upload with just the filename as the destination. This lands the file in the current directory without path parsing issues.

## Source

- GitHub: [github.com/Hackplayers/evil-winrm](https://github.com/Hackplayers/evil-winrm)
- Pre-installed on Kali: `evil-winrm`

**Modules:** [[Windows Privilege Escalation#17.1.2 Situational Awareness|17.1.2]], [[Password Attacks#16.3. Pass-the-Hash|Password Attacks 16.3]], throughout Module 17 lab sessions.

#### Tags: #ModernTooling #EvilWinRM #WinRM #WindowsPrivesc #Module17 #Module16
