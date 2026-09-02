# Linux - Cron Check

**Step 16 of 50 · Linux**

*Find root scheduled jobs and determine whether their scripts or arguments are writable.*

## Run this

> **Why:** This command gathers the linux cron check evidence needed to decide which documented route applies next.
```bash
cat /etc/crontab
ls -la /etc/cron.*
find / -type f -writable 2>/dev/null | grep -E '^/(scripts|opt|etc/cron|var/www)'
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
- [ ] A writable script has root-owned output → **Run `cat $ScriptPath`, `stat $ScriptPath $OutputPath`, save the original locally, then make one controlled test and wait for the next scheduler interval**
- [ ] A wildcard is passed to a root command → **Go to Step 14 · [[Linux - Sudo Check]] and create the documented checkpoint filenames in the command's working directory**
- [ ] No useful job is found → **Go to Step 17 · [[Linux - Credential Search]]**

## Notes

A cron job is a scheduled command. Confirm the run user and the exact script path.

## Gotcha

> [!warning] 💡
> Do not overwrite a live system file without recording its original contents for restoration.

> [!warning] 💡
> A root-owned output file or a changed modification time is useful execution evidence. Confirm the owner with `stat`; do not infer root execution from a writable script alone.

## Writable script with scheduled output

When a scheduler runs a script owned by the current user, preserve the original content before testing. A harmless controlled payload can create a temporary proof artifact; after verification, restore the exact original bytes and compare the file hash.

> **Why:** These commands establish the baseline, make the temporary change explicit, and provide timestamped proof of scheduled execution.
```bash
cat $ScriptPath | tee $BoxDir/loot/$ScriptName.original
stat $ScriptPath $OutputPath
# Replace only the script body required for the authorized test.
stat $OutputPath
```

> [!warning] 💡
> Do not delete a pre-existing root-owned output file as cleanup. Restore only artifacts created by the test and verify the original script content and permissions afterward.

## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- writable script executed by the root scheduler and confirmed with root-owned output

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
