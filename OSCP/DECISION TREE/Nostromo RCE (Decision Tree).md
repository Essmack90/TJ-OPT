# Nostromo RCE (Decision Tree)

## Nostromo branch

```text
Nmap identifies Nostromo 1.9.6
            |
            v
SearchSploit 47837 and review the PoC
            |
            +-- local Python error --> inspect and repair only the local copy
            |
            v
Run harmless `id`
            |
            +-- no response --> check service health and exact target port
            |
            +-- `uid=` response --> RCE confirmed as service account
            |
            v
Start listener and request callback
            |
            +-- no callback --> verify VPN IP, listener, egress, and payload
            |
            v
Read `/var/nostromo/conf/nhttpd.conf`
            |
            +-- `.htpasswd` and `homedirs_public` disclosed --> extract hash privately
            |
            v
Crack Basic-auth record offline
            |
            +-- protected `~user` path returns 401 --> authenticate once and download archive
            |
            v
Archive contains encrypted SSH key
            |
            v
`ssh2john` + John, validate with `ssh-keygen -y`
            |
            v
SSH foothold
            |
            v
Read user scripts and exact sudo arguments
            |
            +-- `journalctl` allowed only with arguments --> reproduce exact invocation
            |
            v
Pager opens
            |
            v
Enter `!/bin/bash`, then verify `id`
```

## Triage table

| Evidence | Next branch |
|---|---|
| Nostromo 1.9.6 | [[OSCP/RUNBOOK V2/Linux - Nostromo RCE|Nostromo RCE]] |
| RCE as `www-data` | Read service configuration and route to credential search |
| Basic-auth 401 under `~user` | Find `.htpasswd` from the Nostromo configuration |
| Encrypted `id_rsa` | `ssh2john`, John, key validation, then SSH |
| User helper calls sudo with fixed arguments | Reproduce the exact command, not a generic binary call |
| `journalctl` pager | Use the pager escape and confirm root with `id` |

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- Nostromo version-to-RCE branch followed by archive, SSH, and pager escalation

## Related pages

- [[OSCP/RUNBOOK V2/Linux - Nostromo RCE|Linux - Nostromo RCE]]
- [[OSCP/COMMAND APPENDIX/Nostromo RCE|Nostromo RCE command appendix]]
- [[OSCP/COMMAND BREAKDOWNS/Nostromo RCE (Breakdowns)|Nostromo RCE command breakdowns]]
