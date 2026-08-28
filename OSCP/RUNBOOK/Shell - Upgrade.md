---
tags: [oscp, shell, upgrade, runbook]
box_sources: [Pelican]
---

# Shell — Upgrade

*You have a dumb shell (no TTY, no job control, Ctrl+C kills nc). Goal: get a fully interactive shell.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `python3 -c 'import pty;pty.spawn("/bin/bash")'` | Prompt changes to `user@host:/$` with proper formatting | python3 is installed (most modern Linux) | Run this first. Sets up a PTY so the shell behaves like a real terminal. Then follow with the stty steps below. | stty step → [[Shell - Stabilise]] | Try `python -c '...'` (Python 2), or `script -qc /bin/bash /dev/null` |
| Background + stty raw: `Ctrl+Z` then `stty raw -echo; fg` | Terminal looks frozen — press Enter once | After PTY spawn | `stty raw -echo` puts your Kali terminal into raw mode so keystrokes pass through directly. `fg` brings nc back. | `export TERM=xterm` | If shell dies, `reset` restores your Kali terminal |
| `export TERM=xterm` | Tab completion and arrow keys start working | After stty step | Sets the terminal type so the remote shell knows how to handle input. Also try `export SHELL=/bin/bash`. | Next stage | — |

---

## Full Stabilisation Sequence

Run these in order. Do not skip steps.

```bash
# 1. On the target (in the dumb shell):
python3 -c 'import pty;pty.spawn("/bin/bash")'

# 2. In Kali — press Ctrl+Z to background nc, then:
stty raw -echo; fg
# Terminal looks frozen. Press Enter once.

# 3. Back in the shell on target:
export TERM=xterm
```

After this: Ctrl+C sends interrupt to the remote process (not your nc session), tab completion works, and arrow keys work.

---

## If python3 is Not Available

Try in order:
```bash
python -c 'import pty;pty.spawn("/bin/bash")'
script -qc /bin/bash /dev/null
/usr/bin/script -qc /bin/bash /dev/null
```

---

## Recovering Your Terminal After a Crash

If your shell dies mid-stabilisation and your Kali terminal is broken (no echo, garbled):

```bash
reset
```

Or type blindly: `stty sane` then Enter.

---

## Screenshot Prompt

> This step is infrastructure — no dedicated screenshot. The foothold shot covers the shell arriving; the first useful command you run after stabilisation is the next shot moment.

---

**Module:** [[09. Common Web Application Attacks|Common Web Application Attacks]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
