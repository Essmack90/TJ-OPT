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

**Module source:** [[16. Password Attacks|LBF.5]]
**Command Appendix:** [[16. Password Attacks#Medusa (SSH and FTP brute-force)|Password Attacks. Medusa section]]
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Medusa supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Medusa is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Install

Use the package or project installation method available on Kali. For an apt package, the pattern is:

~~~bash
sudo apt install medusa
~~~

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
medusa --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
