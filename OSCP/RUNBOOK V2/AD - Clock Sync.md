# AD - Clock Sync

**Step 35 of 50 · AD**

*Synchronise with the domain controller before running Kerberos tools.*

## Run this

```bash
sudo timedatectl set-ntp false
sudo ntpdate $BoxIP
ping -c 1 $BoxIP
```

## Example output

```

$ sudo ntpdate 10.10.10.1
adjust time server 10.10.10.1 offset +25200.0 sec
```
## What did you get?

- [ ] The clock stepped by a large value → **Reconnect the VPN if needed, then go to Step 36 · [[AD - Anonymous Enum]]**
- [ ] The offset is already under five minutes → **Go to Step 36 · [[AD - Anonymous Enum]]**
- [ ] `ntpdate` cannot synchronise → **Check `$BoxIP` and reachability, then go to Step 2 · [[Port Triage]]**

If `sudo ntpdate` is unavailable, use faketime to run Kerberos tools without changing the system clock:

```bash
FakeTime=$(ntpdate -q $BoxIP | awk '{print $1, $2; exit}')
faketime "$FakeTime" GetNPUsers.py $Domain/ -dc-ip $BoxIP -usersfile $BoxDir/loot/users.txt -no-pass -request -format hashcat -outputfile $BoxDir/loot/asrep.txt
```

## Gotcha

> [!warning] 💡
> A large time step can drop the VPN. Always ping `$BoxIP` after syncing and reconnect before the next page.

> [!warning] 💡
> `faketime` wraps a single command with a spoofed clock without changing the system time — useful when VPN stability is a concern or `sudo` is unavailable for `ntpdate`. The format must match what the tool expects (`YYYY-MM-DD HH:MM:SS`).

## Fallback when NTP fails

If `ntpdate` returns no eligible servers, use the offset reported by nmap and adjust the local clock manually. Replace the example offset with the value you observed.

```bash
sudo date -s "$(date -d '+6 hours 59 minutes 59 seconds' '+%Y-%m-%d %H:%M:%S')"
date
ping -c 1 $BoxIP
```

Reconnect the VPN if the time step disconnects it, then continue to Step 36.
