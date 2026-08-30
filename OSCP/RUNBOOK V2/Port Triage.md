# Port Triage

**Step 2 of 50 · Universal**

*Read the full-port result and decide whether the target is an AD domain controller, standalone Windows host, or Linux host.*

## Run this

```bash
sed -n '1,240p' $BoxDir/nmap/allports.txt
```

## Example output

Linux box:
```
22/tcp  open  ssh
80/tcp  open  http
```

Standalone Windows (no AD ports — web + SMB + RDP):
```
80/tcp   open  http
443/tcp  open  https
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server
```

Web-only (no SSH, no SMB, no AD):
```
80/tcp  open  http
443/tcp open  https
```

AD / Domain Controller (the combination of 88 + 389 + 445 is the tell):
```
53/tcp   open  domain
88/tcp   open  kerberos-sec
389/tcp  open  ldap
445/tcp  open  microsoft-ds
5985/tcp open  wsman
```
## What did you get?

- [ ] Ports 53, 88, 389, 445, or 5985 are open together → **Treat it as AD and go to Step 34 · [[AD - Service Scan]]**
- [ ] Windows services are open but the AD set is absent → **Treat it as standalone Windows and go to Step 22 · [[Windows - Service Scan]]**
- [ ] SSH or common Linux services are open → **Treat it as Linux and go to Step 3 · [[Linux - Service Scan]]**
- [ ] Only web ports are open → **Go to Step 5 · [[Linux - Web Enum]] or Step 23 · [[Windows - Web Enum]] based on the service scan**

## Notes

Port 88 is Kerberos. Ports 389 and 3268 are LDAP or Global Catalog. Port 5985 is WinRM.

## Gotcha

> [!warning] 💡
> Do not decide the operating system from one port. Use the service combination and confirm it with the service scan.
