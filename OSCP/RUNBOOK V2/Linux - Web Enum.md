# Linux - Web Enum

**Step 5 of 50 · Linux**

*Find hidden paths, login pages, uploads, CMS clues, and readable files on the web server.*

## Run this

> **Why:** This targeted scan identifies the service, version, and default-script clues needed to choose the next enumeration path.
```bash
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -t 40 -o $BoxDir/nmap/ferox.txt
nikto -h http://$BoxIP/
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/admin
curl -s http://$BoxIP/login
```

## Example output

```

200  GET  /login.php
301  GET  /admin  -> /admin/
200  GET  /robots.txt
...
```
## What did you get?

- [ ] A CMS is identified → **Go to Step 6 · [[Linux - CMS Check]]**
- [ ] A login page is found → **Submit each known credential once, record the HTTP result, then go to Step 10 · [[Linux - Exploit Search]] if no login succeeds**
- [ ] A file upload is found → **Go to Step 9 · [[Linux - File Upload]] and submit the harmless test file described there**
- [ ] A parameter reflects shell metacharacters or a diagnostic action → **Go to Step 8A · [[Linux - Command Injection]]**
- [ ] A contact form or feedback queue is reviewed by an administrator bot → **Go to Step 8B · [[Linux - Stored XSS]]**
- [ ] Interesting files are found → **Run `curl -s http://$BoxIP/$Path -o $BoxDir/loot/$Filename`, then go to Step 17 · [[Linux - Credential Search]]**
- [ ] Nothing useful appears → **Go to Step 10 · [[Linux - Exploit Search]]**

## Notes

Run the web checks against the actual web port if it is not 80.

## Gotcha

> [!warning] 💡
> A 403 response still proves that a path exists. Record it instead of discarding it.

## Management-panel credential reuse

When a web scan finds Cockpit on port 9090 or Webmin on port 10000, test already-validated OS credentials against the panel. Cockpit and Webmin are management interfaces; a successful login may expose a browser-based terminal without a separate web exploit.

> **Why:** These requests check the management-panel login endpoints over HTTPS; look for a redirect to the authenticated dashboard rather than trusting a generic `200` page.
```bash
# Use the discovered panel port and a credential already found elsewhere.
curl -sk -u "$Username:$Password" "https://$BoxIP:9090/"
curl -sk -u "$Username:$Password" "https://$BoxIP:10000/"
```

## Additional routing

- [ ] Cockpit or Webmin accepts the validated OS credential → **In Cockpit click Terminal in the left sidebar, or in Webmin click Tools then Command Shell; run `id`, then go to Step 12 · [[Linux - Shell Stabilise]] or Step 13 · [[Linux - Local Enum]]**
- [ ] The panel is present but rejects the credential → **Do not brute-force blindly; return to Step 17 · [[Linux - Credential Search]]**
- [ ] No management panel is found → **Continue with the existing web enumeration branches**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/11. Sea|Sea]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/10. Cockpit|Cockpit]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/7. Nibbles|Nibbles]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- HTML comment and README exposed Nibbleblog
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- Gobuster found the music site, whose source linked to OpenNetAdmin

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
