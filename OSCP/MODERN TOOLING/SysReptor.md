# SysReptor

#reporting #oscp #pentest #sysreptor

**What it is:** Web-based penetration testing report writing platform. Has official OSCP report templates. Generates clean PDF reports. Used instead of writing reports from scratch in Word/Markdown.

**Cloud:** [cloud.sysreptor.com](https://cloud.sysreptor.com), free tier, no install, OSCP templates built in
**Self-hosted:** [github.com/Syslifters/sysreptor](https://github.com/Syslifters/sysreptor). Docker-based, full control

---

## When to Use

At the end of every box or exam attempt. Replaces [[Box Report Template]] as the actual output tool, use the template to collect your notes during the box, then populate SysReptor for the final PDF.

---

## Basic Cloud Workflow

1. Sign up at cloud.sysreptor.com
2. **New Project** → select template (OSCP or generic pentest)
3. Fill in per-machine findings:
   - Executive summary
   - Attack narrative (chronological)
   - Vulnerability details (name, CVSS, description, evidence, remediation)
   - Proof screenshots (whoami + hostname + flag in one frame)
4. Export → PDF

---

## Self-Hosted Setup (Kali + Docker)

```bash
# Confirm Docker is available
docker --version

# Clone and deploy
git clone https://github.com/Syslifters/sysreptor.git
cd sysreptor/deploy
# Follow README for docker compose setup
```

---

## OSCP Report Requirements (what SysReptor helps satisfy)

- Per-machine: high-level summary, attack steps, proof screenshot
- Proof screenshot must show: `whoami`/`id` → root/SYSTEM, `hostname`, flag content, **all in one frame**
- Every finding needs screenshot evidence
- Remediation recommendation per vulnerability

---

## Tips

- Populate it while the box is fresh, don't leave it until the day before the exam
- The proof screenshot is non-negotiable, take it before closing the shell
- OSCP template in cloud version matches the official exam report format

**Related:** [[Box Report Template]], [[OSCP Habits - Screenshot & Loot]]
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

SysReptor supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

SysReptor is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Install

Use the package or project installation method available on Kali. For an apt package, the pattern is:

~~~bash
sudo apt install sysreptor
~~~

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
sysreptor --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
