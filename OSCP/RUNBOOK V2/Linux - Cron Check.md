# Linux - Cron Check

**Step 16 of 50 · Linux**

*Find root scheduled jobs and determine whether their scripts or arguments are writable.*

## Run this

> **Why:** This command gathers the linux cron check evidence needed to decide which documented route applies next.
```bash
cat /etc/crontab
ls -la /etc/cron.*
```

## Example output

```

# /etc/crontab
*/5 * * * * root /opt/scripts/backup.sh
$ ls -l /opt/scripts/backup.sh
-rwxrwxr-x 1 root devs ... backup.sh
```
## What did you get?

- [ ] A root job runs a writable script → **Set `$ScriptPath` to the displayed script path, run `ls -la $ScriptPath`, edit it with `nano $ScriptPath`, then wait for the schedule or run the documented trigger command**
- [ ] A wildcard is passed to a root command → **Go to Step 14 · [[Linux - Sudo Check]] and create the documented checkpoint filenames in the command's working directory**
- [ ] No useful job is found → **Go to Step 17 · [[Linux - Credential Search]]**

## Notes

A cron job is a scheduled command. Confirm the run user and the exact script path.

## Gotcha

> [!warning] 💡
> Do not overwrite a live system file without recording its original contents for restoration.
## Seen in
- *(no write-up yet)*

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
