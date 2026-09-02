# Linux - Shell Stabilise

**Step 12 of 50 · Linux**

*Turn a basic shell into a usable terminal before local enumeration.*

## Run this

1. Spawn a PTY (pseudo-terminal, a session that behaves like a normal terminal) with Python.
2. Press `Ctrl+Z` to suspend the remote shell and return briefly to your local terminal.
3. Run `stty raw -echo`, then type `fg` and press Enter once to resume the shell without local echo.
4. Set `TERM` so full-screen terminal programs know which terminal features are available.

> **Why:** This command sequence upgrades the connection into a usable terminal with job control, keyboard editing, and reliable local-enumeration commands.
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
stty raw -echo; fg
export TERM=xterm
```

## Example output

```

$ python3 -c 'import pty;pty.spawn("/bin/bash")'
username@host:/$ export TERM=xterm
username@host:/$
```
## What did you get?

- [ ] The shell has job control and usable input → **Run `id`, then go to Step 13 · [[Linux - Local Enum]]**
- [ ] Python 3 is missing → **Run `python -c 'import pty; pty.spawn("/bin/bash")'` or `script -qc /bin/bash /dev/null`, then run `id` and reassess**
- [ ] The terminal is garbled → **Run `reset`, press Enter, run `stty rows 40 columns 120`, and retry this page**

## Notes

Press Ctrl+Z before `stty raw -echo; fg`, then press Enter once.

## Gotcha

> [!warning] 💡
> The stty command changes your local terminal. Keep the recovery command `reset` ready.
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- Python PTY and stty foreground recovery
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- Python PTY and stty foreground recovery
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- Python PTY stabilised the overflow callback shell
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- Python PTY and `fg` recovered the phpbash callback shell

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
