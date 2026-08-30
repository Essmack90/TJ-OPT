# Linux - Shell Stabilise

**Step 12 of 50 · Linux**

*Turn a basic shell into a usable terminal before local enumeration.*

## Run this

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

- [ ] The shell has job control and usable input → **Go to Step 13 · [[Linux - Local Enum]]**
- [ ] Python 3 is missing → **Try `python -c` or `script -qc /bin/bash /dev/null`, then reassess**
- [ ] The terminal is garbled → **Run `reset`, then retry this page**

## Notes

Press Ctrl+Z before `stty raw -echo; fg`, then press Enter once.

## Gotcha

> [!warning] 💡
> The stty command changes your local terminal. Keep the recovery command `reset` ready.
