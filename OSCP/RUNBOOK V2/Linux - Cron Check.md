# Linux - Cron Check

**Step 16 of 50 · Linux**

*Find root scheduled jobs and determine whether their scripts or arguments are writable.*

## Run this

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

- [ ] A root job runs a writable script → **Modify it safely and trigger the job**
- [ ] A wildcard is passed to a root command → **Check the wildcard-injection path**
- [ ] No useful job is found → **Go to Step 17 · [[Linux - Credential Search]]**

## Notes

A cron job is a scheduled command. Confirm the run user and the exact script path.

## Gotcha

> [!warning] 💡
> Do not overwrite a live system file without recording its original contents for restoration.
