# OSCP - Kali Setup & Admin Cheat Sheet

> **Everything you need to set up your Kali VM, connect to VPN, install tools, and manage your environment for OSCP**

---

## Table of Contents

1. [Kali VM Setup & Initial Configuration](#1-kali-vm-setup--initial-configuration)
2. [VPN Configuration & Troubleshooting](#2-vpn-configuration--troubleshooting)
3. [Essential Tool Installation](#3-essential-tool-installation)
4. [Wordlists & Resources](#4-wordlists--resources)
5. [Service Management](#5-service-management)
6. [File & Directory Management](#6-file--directory-management)
7. [SSH & Remote Access](#7-ssh--remote-access)
8. [Shell Configuration & Customization](#8-shell-configuration--customization)
9. [Troubleshooting Common Issues](#9-troubleshooting-common-issues)
10. [Workstation & Lab Management](#10-workstation--lab-management)
11. [Exam-Day Admin Checklist](#11-exam-day-admin-checklist)
12. [Quick Reference Cards](#12-quick-reference-cards)

---

## 1. Kali VM Setup & Initial Configuration

### 1.1 System Updates

```bash
# Update package lists
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Full distribution upgrade
sudo apt dist-upgrade -y

# Clean up unnecessary packages
sudo apt autoremove -y
sudo apt autoclean

# Check kernel version
uname -a

# Check Kali version
lsb_release -a
cat /etc/os-release
```

### 1.2 Network Configuration

#### Static IP Configuration
```bash
# List available connections
nmcli connection show

# Modify connection
sudo nmcli connection modify "Wired connection 1" ipv4.addresses 192.168.1.100/24
sudo nmcli connection modify "Wired connection 1" ipv4.gateway 192.168.1.1
sudo nmcli connection modify "Wired connection 1" ipv4.dns "8.8.8.8,1.1.1.1"
sudo nmcli connection modify "Wired connection 1" ipv4.method manual
sudo nmcli connection down "Wired connection 1" && sudo nmcli connection up "Wired connection 1"

# Or use /etc/network/interfaces
sudo nano /etc/network/interfaces
# auto eth0
# iface eth0 inet static
# address 192.168.1.100
# netmask 255.255.255.0
# gateway 192.168.1.1
# dns-nameservers 8.8.8.8 1.1.1.1
```

#### DNS Configuration
```bash
# View current DNS
cat /etc/resolv.conf

# Add DNS server (temporary)
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf

# Permanent DNS via NetworkManager
sudo nmcli connection modify "Wired connection 1" ipv4.dns "8.8.8.8,1.1.1.1"

# Or via /etc/systemd/resolved.conf
sudo nano /etc/systemd/resolved.conf
# DNS=8.8.8.8 1.1.1.1
# FallbackDNS=1.0.0.1
```

#### /etc/hosts Management
```bash
# Add host entries
echo "192.168.50.100   target.local" | sudo tee -a /etc/hosts

# View hosts file
cat /etc/hosts

# Edit hosts file
sudo nano /etc/hosts
```

### 1.3 User Management

```bash
# Change password
passwd

# Add new user
sudo adduser username
sudo useradd -m -s /bin/bash username

# Add user to sudo group
sudo usermod -aG sudo username

# Delete user
sudo userdel -r username

# List users
cat /etc/passwd
getent passwd
```

### 1.4 System Settings

```bash
# Timezone
sudo timedatectl set-timezone America/New_York
sudo dpkg-reconfigure tzdata

# Date/Time sync
sudo timedatectl set-ntp true
sudo systemctl enable systemd-timesyncd
sudo systemctl start systemd-timesyncd

# Hostname
sudo hostnamectl set-hostname kali-desktop
echo "kali-desktop" | sudo tee /etc/hostname

# Check system status
systemctl status
systemctl list-units --type=service
```

---

## 2. VPN Configuration & Troubleshooting

### 2.1 OpenVPN Setup

```bash
# Install OpenVPN
sudo apt install openvpn openvpn-systemd-resolved

# Connect to VPN
sudo openvpn --config /path/to/your.ovpn

# Or run in background
sudo openvpn --config /path/to/your.ovpn --daemon

# Check connection
ifconfig tun0
ip addr show tun0
```

### 2.2 VPN Profile Setup (./vpn.ovpn)

```bash
# Create a convenience script
nano ~/vpn.sh
chmod +x ~/vpn.sh

# Content:
#!/bin/bash
sudo openvpn --config /path/to/your.ovpn

# Or with password
sudo openvpn --config /path/to/your.ovpn --auth-user-pass /path/to/auth.txt

# auth.txt format:
# username
# password
```

### 2.3 VPN Troubleshooting

```bash
# Check if VPN is connected
ip addr show tun0
ping -c 4 10.0.0.1  # Your VPN gateway

# Check routing
route -n
ip route

# DNS issues
# Add to /etc/resolv.conf
nameserver 8.8.8.8
nameserver 1.1.1.1

# Fix DNS for OpenVPN
sudo apt install openvpn-systemd-resolved

# Kill stuck VPN processes
sudo killall openvpn

# Restart network
sudo systemctl restart NetworkManager

# Check logs
sudo tail -f /var/log/syslog | grep openvpn
sudo journalctl -u openvpn -f

# Reset VPN interface
sudo ip link set tun0 down
sudo ip link set tun0 up
```

### 2.4 Multiple VPN Connections

```bash
# Connect to multiple VPNs (different networks)
sudo openvpn --config lab1.ovpn --daemon
sudo openvpn --config lab2.ovpn --daemon

# Check routing for multiple
ip route show

# Specific tun interfaces
ip addr show tun0
ip addr show tun1
```

---

## 3. Essential Tool Installation

### 3.1 Base Tools

```bash
# Metasploit Framework
sudo apt install metasploit-framework

# Initialize database
sudo msfdb init
sudo msfdb start

# Nmap
sudo apt install nmap

# OpenVAS (for vulnerability scanning)
sudo apt install openvas
sudo gvm-setup
sudo gvm-start

# Hydra
sudo apt install hydra

# John the Ripper
sudo apt install john

# Hashcat
sudo apt install hashcat

# SQLmap
sudo apt install sqlmap

# Burp Suite (Community)
sudo apt install burpsuite

# Wireshark
sudo apt install wireshark

# Responder
sudo apt install responder

# Impacket
sudo apt install impacket-scripts
pip3 install impacket

# BloodHound
sudo apt install bloodhound
```

### 3.2 Web Application Tools

```bash
# Gobuster
sudo apt install gobuster

# Dirb
sudo apt install dirb

# WPScan
sudo apt install wpscan

# Nikto
sudo apt install nikto

# WhatWeb
sudo apt install whatweb

# Feroxbuster
sudo apt install feroxbuster

# ffuf
sudo apt install ffuf

# Sublist3r
sudo apt install sublist3r

# Eyewitness
sudo apt install eyewitness
```

### 3.3 Windows Tools

```bash
# Mimikatz
wget https://github.com/gentilkiwi/mimikatz/releases/latest/download/mimikatz_trunk.zip
unzip mimikatz_trunk.zip

# PowerView
git clone https://github.com/PowerShellMafia/PowerSploit.git

# SharpHound
wget https://github.com/BloodHoundAD/SharpHound/releases/latest/download/SharpHound.zip

# Rubeus
wget https://github.com/GhostPack/Rubeus/releases/latest/download/Rubeus.zip

# Sysinternals
wget https://download.sysinternals.com/files/SysinternalsSuite.zip
unzip SysinternalsSuite.zip

# Plink (PuTTY)
sudo apt install putty-tools

# evil-winrm
sudo apt install evil-winrm

# CrackMapExec
sudo apt install crackmapexec

# Impacket (already installed but ensure latest)
pip3 install impacket
```

### 3.4 Privilege Escalation Tools

```bash
# LinPEAS
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh

# winPEAS
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASx64.exe
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/winPEASx86.exe

# PowerUp
wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1

# Linux Smart Enumeration
wget https://github.com/diego-treitos/linux-smart-enumeration/releases/latest/download/lse.sh
chmod +x lse.sh

# Unix PrivEsc Check
sudo apt install unix-privesc-check
```

### 3.5 Reconnaissance Tools

```bash
# AutoRecon
sudo apt install autorecon

# Enum4Linux
sudo apt install enum4linux

# DNSEnum
sudo apt install dnsenum

# DNSRecon
sudo apt install dnsrecon

# SNMP tools
sudo apt install snmp snmp-mibs-downloader onesixtyone

# SMTP tools
sudo apt install swaks

# SMB tools
sudo apt install smbclient smbmap cifs-utils

# FTP tools
sudo apt install ftp
```

### 3.6 Shell & Transfer Tools

```bash
# Python HTTP server
# (Built-in, no install needed)

# Netcat
sudo apt install netcat-openbsd

# Ncat
sudo apt install ncat

# Socat
sudo apt install socat

# Chisel
wget https://github.com/jpillora/chisel/releases/latest/download/chisel_linux_amd64.gz
gunzip chisel_linux_amd64.gz
chmod +x chisel_linux_amd64
sudo mv chisel_linux_amd64 /usr/local/bin/chisel

# Powercat
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 .
```

### 3.7 Installing via Python (pip)

```bash
# Ensure pip is installed
sudo apt install python3-pip

# Upgrade pip
python3 -m pip install --upgrade pip

# Install Python tools
pip3 install --user requests beautifulsoup4
pip3 install --user pycryptodome
pip3 install --user termcolor
pip3 install --user colorama
pip3 install --user shodan

# Install Python network tools
pip3 install --user scapy
pip3 install --user python-nmap

# Install impacket (latest)
pip3 install --user impacket

# Install pacu (AWS enumeration)
sudo apt install pacu
```

### 3.8 Installing via Git

```bash
# Create tools directory
mkdir ~/tools
cd ~/tools

# Git clone common repos
git clone https://github.com/PowerShellMafia/PowerSploit.git
git clone https://github.com/BloodHoundAD/BloodHound.git
git clone https://github.com/SecureAuthCorp/impacket.git
git clone https://github.com/gentilkiwi/mimikatz.git
git clone https://github.com/carlospolop/PEASS-ng.git
git clone https://github.com/danielmiessler/SecLists.git
git clone https://github.com/Tib3rius/AutoRecon.git
git clone https://github.com/rebootuser/LinEnum.git
git clone https://github.com/411Hall/JAWS.git
git clone https://github.com/fortra/impacket.git
```

---

## 4. Wordlists & Resources

### 4.1 Install Wordlists

```bash
# Install default wordlists
sudo apt install wordlists

# Install SecLists
sudo apt install seclists

# Install rockyou
sudo apt install rockyou

# Unzip rockyou if needed
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# Install dirb wordlists
sudo apt install dirb

# Check wordlist locations
ls -la /usr/share/wordlists/
```

### 4.2 Custom Wordlists

```bash
# Create a username list from a company website
cewl http://target.com -w usernames.txt

# Create a password list with crunch
crunch 8 10 abcdefghijklmnopqrstuvwxyz1234567890 -o passwords.txt

# Combine and deduplicate
cat wordlist1.txt wordlist2.txt > combined.txt
sort -u combined.txt > unique.txt

# RSMangler for password mutations
rsmangler --input base_passwords.txt --output mangled.txt

# Generate default credentials
python3 /usr/share/wordlists/seclists/Passwords/Default-Credentials/` + '...'
```

### 4.3 Quick Reference - Wordlist Locations

```bash
/usr/share/wordlists/rockyou.txt
/usr/share/wordlists/dirb/common.txt
/usr/share/wordlists/dirb/big.txt
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
/usr/share/wordlists/fasttrack.txt
/usr/share/wordlists/nmap.lst
/usr/share/seclists/Discovery/DNS/
/usr/share/seclists/Usernames/
/usr/share/seclists/Passwords/
/usr/share/seclists/Web-Content/
```

---

## 5. Service Management

### 5.1 Database Services

#### PostgreSQL (Metasploit)
```bash
# Start database
sudo systemctl start postgresql
sudo service postgresql start

# Enable at boot
sudo systemctl enable postgresql
sudo update-rc.d postgresql enable

# Check status
sudo systemctl status postgresql

# Reset Metasploit DB
sudo msfdb init
sudo msfdb start
sudo msfdb stop
sudo msfdb reinit
```

#### MySQL/MariaDB
```bash
# Install
sudo apt install mariadb-server

# Start
sudo systemctl start mariadb

# Secure installation
sudo mysql_secure_installation

# Access
sudo mysql -u root -p

# Common commands
SHOW DATABASES;
CREATE DATABASE dbname;
USE dbname;
SHOW TABLES;
```

### 5.2 Web Services

#### Apache
```bash
# Install
sudo apt install apache2

# Start
sudo systemctl start apache2
sudo systemctl enable apache2

# Web root
/var/www/html/

# Logs
sudo tail -f /var/log/apache2/access.log
sudo tail -f /var/log/apache2/error.log

# Restart
sudo systemctl restart apache2
```

#### Python HTTP Server
```bash
# Python 3
python3 -m http.server 80
python3 -m http.server 443

# Python 2
python -m SimpleHTTPServer 80

# With specific directory
cd /path/to/share && python3 -m http.server 80
```

### 5.3 SSH Service

```bash
# Start SSH server
sudo systemctl start ssh
sudo service ssh start

# Enable at boot
sudo systemctl enable ssh
sudo update-rc.d ssh enable

# Check status
sudo systemctl status ssh

# SSH config
sudo nano /etc/ssh/sshd_config

# Restart after changes
sudo systemctl restart ssh
```

### 5.4 Database Management

```bash
# Neo4j (BloodHound)
sudo neo4j start
sudo neo4j stop
sudo neo4j status
sudo neo4j console

# Default credentials
# Username: neo4j
# Password: neo4j

# Reset Neo4j password
# Access http://localhost:7474
```

### 5.5 Service Quick Reference

| Service | Start | Stop | Status |
|---------|-------|------|--------|
| postgresql | `sudo systemctl start postgresql` | `sudo systemctl stop postgresql` | `sudo systemctl status postgresql` |
| ssh | `sudo systemctl start ssh` | `sudo systemctl stop ssh` | `sudo systemctl status ssh` |
| apache2 | `sudo systemctl start apache2` | `sudo systemctl stop apache2` | `sudo systemctl status apache2` |
| neo4j | `sudo neo4j start` | `sudo neo4j stop` | `sudo neo4j status` |
| NetworkManager | `sudo systemctl start NetworkManager` | `sudo systemctl stop NetworkManager` | `sudo systemctl status NetworkManager` |

---

## 6. File & Directory Management

### 6.1 Directory Structure for OSCP

```bash
# Create organized workspace
mkdir -p ~/oscp/{labs,notes,tools,wordlists,payloads,results,reports}

# Create lab structure
mkdir -p ~/oscp/labs/target1/{recon,exploit,post}
mkdir -p ~/oscp/labs/target2/{recon,exploit,post}

# Create notes structure
mkdir -p ~/oscp/notes/{linux,windows,active-directory,web-app,methodology}

# Create results structure
mkdir -p ~/oscp/results/{scans,screenshots,credentials,hashes}
```

### 6.2 File Operations

```bash
# Copy with progress
rsync -av --progress source/ destination/

# Copy multiple files with find
find /path -name "*.txt" -exec cp {} /dest/ \;

# Move files
mv source destination

# Rename
mv oldname newname

# Delete with pattern
rm -rf /path/*.bak

# Find and delete
find /path -type f -name "*.log" -delete

# File permissions
chmod 755 file
chmod +x script.sh
chmod 600 private_key
chmod 700 directory

# Ownership
chown user:group file
chown -R user:group directory
```

### 6.3 Archiving & Compression

```bash
# Create tar
tar -czf archive.tar.gz /path/to/dir
tar -cvf archive.tar /path/to/dir

# Extract tar
tar -xzf archive.tar.gz
tar -xvf archive.tar

# Create zip
zip -r archive.zip /path/to/dir

# Extract zip
unzip archive.zip -d /dest/dir

# Create gzip
gzip file.txt

# Extract gzip
gunzip file.txt.gz
```

### 6.4 Mounting & Drives

```bash
# List disks
lsblk
fdisk -l

# Mount drive
sudo mount /dev/sdb1 /mnt/usb

# Unmount
sudo umount /mnt/usb

# Mount NFS
sudo mount -t nfs 192.168.0.1:/share /mnt/nfs

# Mount SMB
sudo mount -t cifs //192.168.0.1/share /mnt/smb -o username=user
```

---

## 7. SSH & Remote Access

### 7.1 SSH Key Management

```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -C "kali@oscp"
ssh-keygen -t ed25519 -C "kali@oscp"

# View public key
cat ~/.ssh/id_rsa.pub

# Copy public key to server
ssh-copy-id user@192.168.0.1

# Manual copy
cat ~/.ssh/id_rsa.pub | ssh user@192.168.0.1 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 7.2 SSH Config (~/.ssh/config)

```bash
# Create config file
nano ~/.ssh/config

# Example config
Host target
    HostName 192.168.0.1
    User username
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host proxy
    HostName 192.168.0.2
    User user
    ProxyCommand ssh -W %h:%p jump

# SSH with config
ssh target
```

### 7.3 SSH Tunneling

```bash
# Local port forward
ssh -L 8080:internal_host:80 user@jump_host

# Remote port forward
ssh -R 8080:localhost:80 user@external_host

# Dynamic SOCKS proxy
ssh -D 1080 user@jump_host

# Reverse SOCKS
ssh -R 1080 user@external_host

# SSH with password
sshpass -p 'password' ssh user@192.168.0.1
```

### 7.4 SCP File Transfer

```bash
# Copy to remote
scp local_file user@192.168.0.1:/remote/path/

# Copy from remote
scp user@192.168.0.1:/remote/file /local/path/

# Copy directory recursively
scp -r /local/dir user@192.168.0.1:/remote/dir/

# Copy with port
scp -P 2222 file user@192.168.0.1:/remote/
```

---

## 8. Shell Configuration & Customization

### 8.1 Bashrc Customization

```bash
# Edit .bashrc
nano ~/.bashrc

# Add aliases
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias df='df -h'
alias du='du -h'

# Add path
export PATH=$PATH:~/tools

# Reload .bashrc
source ~/.bashrc
```

### 8.2 ZSH Configuration (Oh-My-Zsh)

```bash
# Install Oh-My-Zsh
sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Change default shell
chsh -s $(which zsh)

# Install plugins
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# Add to .zshrc
plugins=(git zsh-autosuggestions zsh-syntax-highlighting)
```

### 8.3 Terminal Multiplexers

#### tmux
```bash
# Install
sudo apt install tmux

# Start new session
tmux new -s session_name

# Detach
Ctrl+b d

# List sessions
tmux ls

# Attach to session
tmux attach -t session_name

# Kill session
tmux kill-session -t session_name

# Split panes
Ctrl+b " (horizontal)
Ctrl+b % (vertical)

# Navigate panes
Ctrl+b arrow keys

# Create new window
Ctrl+b c

# Navigate windows
Ctrl+b n (next)
Ctrl+b p (previous)
```

#### screen
```bash
# Start new screen
screen -S session_name

# Detach
Ctrl+a d

# List sessions
screen -ls

# Attach
screen -r session_name

# Kill session
screen -X -S session_name quit
```

---

## 9. Troubleshooting Common Issues

### 9.1 Network Issues

```bash
# DNS resolution issues
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf

# Reset network
sudo systemctl restart NetworkManager

# Check interfaces
ip addr show
ifconfig -a

# Check routing
ip route show
route -n

# Check connectivity
ping -c 4 8.8.8.8
ping -c 4 google.com

# Release/Renew DHCP
sudo dhclient -r
sudo dhclient
```

### 9.2 VPN Issues

```bash
# Check if VPN is connected
ifconfig tun0
ip addr show tun0

# Kill stuck VPN
sudo killall openvpn

# Reconnect VPN
sudo openvpn --config /path/to/your.ovpn

# Check logs
sudo tail -f /var/log/syslog | grep openvpn

# DNS issues with VPN
sudo apt install openvpn-systemd-resolved
```

### 9.3 Tool Issues

```bash
# Metasploit database issues
sudo msfdb reinit
sudo msfdb start

# Fix missing dependencies
sudo apt install --fix-broken
sudo apt install --fix-missing

# Fix Python packages
pip3 install --upgrade pip
pip3 install --force-reinstall package_name

# Fix PATH issues
export PATH=$PATH:/path/to/tool
echo 'export PATH=$PATH:/path/to/tool' >> ~/.bashrc
```

### 9.4 Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER ~/oscp/
sudo chmod -R 755 ~/oscp/

# Fix sudo
sudo visudo

# Fix SSH permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/authorized_keys
```

### 9.5 Performance Issues

```bash
# Check memory
free -h
htop

# Check disk space
df -h
du -sh ~/*

# Clear cache
sudo apt clean
sudo apt autoclean
sudo apt autoremove

# Clear ~/.cache
rm -rf ~/.cache/*

# Kill unnecessary processes
sudo pkill process_name
```

---

## 10. Workstation & Lab Management

### 10.1 Snapshot & Backup Management

```bash
# Take a snapshot of VM (VirtualBox)
VBoxManage snapshot "Kali" take "Pre-OSCP"

# Restore snapshot (VirtualBox)
VBoxManage snapshot "Kali" restore "Pre-OSCP"

# Create backup of important files
tar -czf backup_oscp_$(date +%Y%m%d).tar.gz ~/oscp/ ~/.ssh/

# Backup Metasploit database
sudo pg_dump -U msf msf > msf_backup.sql
```

### 10.2 Clean Up After Labs

```bash
# Remove temp files
rm -rf /tmp/*

# Clear bash history
history -c
> ~/.bash_history

# Clear logs
sudo journalctl --rotate
sudo journalctl --vacuum-time=1s

# Clear browser history
rm -rf ~/.cache/mozilla/firefox/*.default/cache2/*
rm -rf ~/.cache/mozilla/firefox/*.default/offlinecache/*

# Remove downloaded tools
rm -rf ~/tools/

# Remove lab files
rm -rf ~/oscp/labs/*
```

### 10.3 Screen Recording & Notes

```bash
# Record terminal session
script -a session_$(date +%Y%m%d_%H%M%S).log

# Stop recording
exit

# Take screenshots
gnome-screenshot -a -c  # Area to clipboard
gnome-screenshot -w -f screenshot.png  # Window

# Import screenshots to markdown
# Use: [![screenshot](screenshot.png)](screenshot.png)
```

### 10.4 Password Management

```bash
# KeepassXC
sudo apt install keepassxc

# Password database
# ~/.keepass/database.kdbx

# Credentials file template
cat > ~/oscp/credentials.txt << EOF
# Target: 192.168.0.1
# Date: $(date)
#
# SSH: user:password
# Web: admin:password
# SMB: user:password
#
EOF
```

---

## 11. Exam-Day Admin Checklist

### 11.1 Before the Exam

- [ ] **System preparation**
  - [ ] Update Kali: `sudo apt update && sudo apt upgrade -y`
  - [ ] Install missing tools
  - [ ] Verify VPN connection
  - [ ] Test internet connection
  - [ ] Verify microphone/camera
  - [ ] Test screen sharing

- [ ] **Environment setup**
  - [ ] Create `~/oscp/` directory structure
  - [ ] Copy VPN config to convenient location
  - [ ] Start Metasploit DB: `sudo msfdb start`
  - [ ] Start Neo4j: `sudo neo4j start`
  - [ ] Configure `/etc/hosts`
  - [ ] Set up tmux/screen sessions

- [ ] **Backup & Recovery**
  - [ ] Take VM snapshot
  - [ ] Backup SSH keys
  - [ ] Backup notes from practice
  - [ ] Have offline documentation ready

- [ ] **Workspace setup**
  - [ ] tmux/screen with split panes
  - [ ] Browser with tabs ready
  - [ ] Notes application open
  - [ ] Credentials file open

### 11.2 During the Exam

- [ ] **Connect VPN**:
  ```bash
  sudo openvpn --config /path/to/exam.ovpn
  ```

- [ ] **Verify Connection**:
  ```bash
  ifconfig tun0
  ping -c 4 10.0.0.1
  ```

- [ ] **Start Important Services**:
  ```bash
  sudo msfdb start
  sudo neo4j start
  sudo systemctl start postgresql
  ```

- [ ] **Begin Enumeration**:
  - Run initial Nmap scans
  - Start AutoRecon
  - Document everything

- [ ] **Maintain Notes**:
  ```bash
  # Start a session log
  script -a exam_session_$(date +%H%M).log
  ```

### 11.3 After the Exam

- [ ] **Cleanup**
  - [ ] Disconnect VPN
  - [ ] Close all sessions
  - [ ] Organize notes
  - [ ] Take VM snapshot (post-exam)
  - [ ] Backup important files

- [ ] **Report Preparation**
  - [ ] Screenshots ready
  - [ ] Commands documented
  - [ ] Findings organized
  - [ ] Proof of exploit captured

---

## 12. Quick Reference Cards

### 12.1 Common Admin Commands

| Task | Command |
|------|---------|
| Update system | `sudo apt update && sudo apt upgrade -y` |
| Install tool | `sudo apt install toolname` |
| Start service | `sudo systemctl start servicename` |
| Check service | `sudo systemctl status servicename` |
| Start VPN | `sudo openvpn --config file.ovpn` |
| Check VPN | `ip addr show tun0` |
| Search file | `find / -name "filename" 2>/dev/null` |
| Search content | `grep -r "pattern" /path/ 2>/dev/null` |
| HTTP server | `python3 -m http.server 80` |
| SMB server | `impacket-smbserver -smb2support share /var/www/html` |
| SSH | `ssh user@host` |
| SCP | `scp file user@host:/path/` |
| Screen record | `script -a session.log` |

### 12.2 Paths & Locations

```bash
# Important paths
~/oscp/                    # Main OSCP workspace
/usr/share/wordlists/      # Wordlists
/usr/share/exploitdb/      # Exploit-DB
/usr/share/nmap/scripts/   # NSE scripts
/usr/share/metasploit-framework/  # Metasploit
/var/www/html/              # Apache webroot
/etc/ssh/sshd_config        # SSH config
/etc/resolv.conf            # DNS config
/var/log/                   # System logs
```

### 12.3 Custom Scripts for Admin Tasks

```bash
# ~/oscp_start.sh - Start all services
#!/bin/bash
echo "Starting OSCP environment..."
sudo msfdb start
sudo neo4j start
sudo systemctl start postgresql
echo "All services started"

# ~/oscp_clean.sh - Clean temp files
#!/bin/bash
echo "Cleaning temp files..."
rm -rf /tmp/*
rm -rf ~/oscp/temp/*
echo "Done"

# ~/oscp_backup.sh - Backup important files
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf ~/backup_oscp_$DATE.tar.gz ~/oscp/ ~/.ssh/ ~/tools/
echo "Backup created: backup_oscp_$DATE.tar.gz"
```

---

**Remember**: A well-configured Kali VM can save hours during the exam. Take time to set up your environment properly before the exam starts. Practice with your tools and know where everything is located.

> "Preparation is the key to success" - Offensive Security