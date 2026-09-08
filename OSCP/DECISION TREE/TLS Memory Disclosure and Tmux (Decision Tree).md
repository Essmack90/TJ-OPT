# TLS Memory Disclosure and Tmux, Decision Tree

## HTTPS service exposes an old TLS stack

```text
443/tcp open https
        |
        v
nmap --script ssl-heartbleed
        |
        +--> vulnerable -> save a reviewed Heartbleed response
        |                 -> inspect type 24 and excess length
        |                 -> repeat a bounded number of times if needed
        |                 -> filter locally for application clues
        |
        +--> not vulnerable or no excess data -> record the negative result
                                      -> return to web and credential enumeration
```

Use a Heartbleed-aware client for exploitation. `openssl s_client` is a TLS
diagnostic tool and cannot substitute for the malformed heartbeat request.

## SSH foothold exposes a privileged local session

```text
low-privilege Linux shell
        |
        v
find / -type s -ls 2>/dev/null
        |
        v
root-owned socket with current-user group access?
        |
        +--> yes -> tmux -S $TmuxSocket ls
        |          -> attach-session -t 0
        |          -> id / whoami
        |
        +--> no -> continue sudo, SUID, capabilities, cron, credential, and kernel checks
```

The socket mode is the decision point. A root-owned filename without readable
or writable access is only an observation, not an escalation.

## Related stages

- [[RUNBOOK V2/Linux - Heartbleed|Linux - Heartbleed]]
- [[RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Tmux Session Hijack|Linux - Tmux Session Hijack]]
- [[RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- Heartbleed disclosure followed by tmux session access

