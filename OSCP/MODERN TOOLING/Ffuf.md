# Ffuf

**What it is:** A fast web fuzzer written in Go. Replaces the `FUZZ` keyword in a URL, header, or POST body with wordlist entries and reports which responses differ from the baseline. Covers directory/page discovery, extension fuzzing, recursive scanning, sub-domain and vhost enumeration, and GET/POST parameter + value brute-forcing in one tool.

**Install (Kali — usually pre-installed):**
```bash
which ffuf || sudo apt install ffuf -y
# Or latest release from GitHub:
# go install github.com/ffuf/ffuf/v2@latest
```

**Key flags:**
| Flag | Purpose |
|------|---------|
| `-w wordlist:FUZZ` | Wordlist. `:FUZZ` names the injection point (default keyword is `FUZZ`). |
| `-u URL` | Target. Put `FUZZ` wherever you're injecting. |
| `-e .php,.html` | Append extensions to each wordlist word. |
| `-recursion -recursion-depth 1` | Auto-recurse into found directories. |
| `-H 'Host: FUZZ.domain.htb'` | Custom header. Use for vhost fuzzing. |
| `-X POST -d 'param=FUZZ'` | POST body fuzzing. |
| `-fs N` | Filter by response size (exclude N bytes). |
| `-fw N` / `-fl N` | Filter by word or line count. |
| `-ac` | Auto-calibrate: ffuf determines the noise baseline automatically. |
| `-mr "regex"` | Only show responses whose body matches the regex. |
| `-t 100` | 100 threads (default 40). |
| `-s` | Silent mode (results only). |

**Common wordlists (Kali path `/usr/share/seclists/`, HTB Pwnbox `/opt/useful/SecLists/`):**
- `Discovery/Web-Content/directory-list-2.3-small.txt` — directory/page names
- `Discovery/Web-Content/web-extensions.txt` — file extensions
- `Discovery/DNS/subdomains-top1million-5000.txt` — sub-domain/vhost names
- `Discovery/Web-Content/burp-parameter-names.txt` — GET/POST parameter names
- `Usernames/Names/names.txt` — username values

**vs. Gobuster:** Ffuf is faster, supports recursive scanning, extension fuzzing in a single pass, POST body fuzzing, and flexible response filtering (`-ac`, `-mr`). Gobuster's `dir`/`dns`/`vhost` modes require separate invocations for each mode. For OSCP web targets, ffuf is generally the better first-reach tool.

**Module source:** [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]
**Command Appendix:** [[Reconnaissance & Enumeration#Ffuf (Web Fuzzer)|Recon & Enumeration. Ffuf section]]
**Decision Tree:** [[Web Applications (Decision Tree)#You have a web target IP and need to start enumerating it|Web App DT, target enumeration flow]]
**Command Breakdowns:** [[Web Applications (Breakdowns)#Ffuf two-step filtering and the -ac shortcut|Ffuf filtering teardown]]
