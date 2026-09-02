# AD - Web Enum

**Step 37 of 50 · AD**

*Use the IIS site as a username source when anonymous AD enumeration is dry.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x html,txt,php -t 30 -o $BoxDir/nmap/ferox.txt
curl -s http://$BoxIP/about.html | tee $BoxDir/loot/about.html
```

## Example output

```

200  GET  /about.html
200  GET  /contact.html
About: Example Person
...
```
## What did you get?

- [ ] An About or Team page lists people → **Write the names to `$BoxDir/loot/users.txt`, then go to Step 38 · [[AD - AS-REP Roasting]]**
- [ ] A login page is found → **Submit the known or documented default credential once, then go to Step 40 · [[AD - Credential Validation]] if it succeeds**
- [ ] Interesting files or directories are found → **Run `curl -O http://$BoxIP/$Path` for each authorized file, save the output, then return to Step 40 · [[AD - Credential Validation]] with any credential found**
- [ ] An editable LDAP or directory server address field exposes a service account username → **Go to Step 37A · [[AD - LDAP Passback]]**
- [ ] No useful web content appears → **Go to Step 38 · [[AD - AS-REP Roasting]] with any candidate usernames you have**

## Notes

Try first-initial plus surname when the site lists full names.

## Gotcha

> [!warning] 💡
> Read the page source as well as the visible page. Comments and hidden text can contain names or paths.

## External Resources

- [HackTricks, Active Directory Methodology](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html)
- [PayloadsAllTheThings, Active Directory Attack](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
## Seen in
- *(no write-up yet)*

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
