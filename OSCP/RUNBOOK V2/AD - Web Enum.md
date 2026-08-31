# AD - Web Enum

**Step 37 of 50 · AD**

*Use the IIS site as a username source when anonymous AD enumeration is dry.*

## Run this

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

- [ ] An About or Team page lists people → **Derive likely usernames and go to Step 38 · [[AD - AS-REP Roasting]]**
- [ ] A login page is found → **Test known or default credentials, then return to credential validation**
- [ ] Interesting files or directories are found → **Read and loot them, then reassess the foothold path**
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
