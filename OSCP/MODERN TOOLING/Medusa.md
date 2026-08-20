# Medusa

**What it is:** A fast, modular parallel brute-force tool for network services. Alternative to Hydra. Particularly reliable for FTP on slow targets.

**Install (Kali — usually pre-installed):**
```bash
which medusa || sudo apt install medusa -y
```

**Core syntax:** `medusa -h HOST -n PORT -u USER -P WORDLIST -M MODULE -t THREADS`

```bash
# SSH brute-force (single user)
medusa -h TARGET -n PORT -u sshuser -P passwords.txt -M ssh -t 3

# FTP brute-force (single user, localhost)
medusa -h 127.0.0.1 -u ftpuser -P passwords.txt -M ftp -t 5

# FTP with username list (| grep to suppress noise)
medusa -h 127.0.0.1 -U usernames.txt -P passwords.txt -M ftp -t 5 | grep "ACCOUNT FOUND"
```

**Flag differences from Hydra:**
| | Medusa | Hydra equivalent |
|--|--------|-----------------|
| Single username | `-u USER` | `-l USER` |
| Username list | `-U FILE` | `-L FILE` |
| Port | `-n PORT` | `-s PORT` or `ssh://HOST:PORT` |
| Auto-stop on hit | automatic | `-f` flag required |

**Supported modules:** ssh, ftp, http, https-get, https-post-form, smb, mssql, mysql, pop3, smtp, telnet, vnc, rdp (and more, `medusa -d` lists all available)

**Module source:** [[Login Brute Forcing (HTB Supplementary)#LBF.5. Web Services. Medusa (SSH + Internal FTP Pivot)|LBF.5]]
**Command Appendix:** [[Password Attacks#Medusa (SSH and FTP brute-force)|Password Attacks. Medusa section]]
