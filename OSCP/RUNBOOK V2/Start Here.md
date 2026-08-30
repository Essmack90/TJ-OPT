# Start Here

**Step 1 of 50 · Universal**

*Initialise the box workspace, set the variables, and run the full TCP scan.*

## Run this

```bash
boxstart $BoxName $BoxIP htb
boxset BoxName $BoxName
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/$BoxName
boxset Domain $Domain
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oN $BoxDir/nmap/allports.txt
```

## Example output

```

[+] Box workspace ready: $BoxName
[+] Target: 10.10.10.1
...
Nmap scan completed
22/tcp open ssh
80/tcp open http
```
## What did you get?

- [ ] The scan is still running → **Wait for it to finish, then go to Step 2 · [[Port Triage]]**
- [ ] Ports are listed in the output → **Go to Step 2 · [[Port Triage]]**
- [ ] The target is unreachable → **Check the VPN and `$BoxIP`, then rerun this page**

## Notes

Keep all scan output under `$BoxDir/nmap/` and keep credentials in `$BoxDir/loot/`.

## Gotcha

> [!warning] 💡
> `boxstart` may not be available in every environment. If it fails, create `$BoxDir/nmap`, `$BoxDir/loot`, `$BoxDir/www`, and `$BoxDir/screenshots` manually before continuing.
