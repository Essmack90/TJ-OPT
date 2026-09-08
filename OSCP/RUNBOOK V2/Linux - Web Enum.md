# Linux - Web Enum

**Step 5 of 50 · Linux**

*Find hidden paths, login pages, uploads, CMS clues, and readable files on the web server.*

> [!tip] 💡 Follow-along mode
> You are here after the service scan found HTTP or HTTPS. Confirm `$WebPort` first, run the small discovery block, then choose exactly one row under **What did you get?**. For the full blank-slate route, return to [[00 - Follow-Along Controller]] Step 4.

## Run this

> **Why:** Manual source review finds clues that a directory scanner cannot, while low-thread content discovery reduces the chance of taking down an older or custom service.
```bash
curl -i "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/index.headers.txt"
curl -sS "http://$BoxIP:$WebPort/" -o "$BoxDir/loot/index.html"
whatweb "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/whatweb.txt"
curl -i "http://$BoxIP:$WebPort/robots.txt" | tee "$BoxDir/loot/robots.txt"
grep -Ein 'version|generator|powered|admin|login|upload|debug|api|comment' "$BoxDir/loot/index.html"
gobuster dir -u "http://$BoxIP:$WebPort/" -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,bak,old,zip -t 10 -o "$BoxDir/nmap/gobuster.txt"
```

> [!tip] ⚡ More efficient path
> If you only need quick content discovery after the manual checks, use one `feroxbuster` command with a saved output file. Do not run Gobuster, Feroxbuster, and Nikto simultaneously against a fragile target.

```bash
feroxbuster -u "http://$BoxIP:$WebPort/" -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,bak,old,zip -t 20 -o "$BoxDir/nmap/ferox.txt"
```

> [!tip] 🛠️ Alternative tool
> Use `ffuf` when you need response-size filtering or parameter discovery. `-ac` calibrates the normal response so you do not manually guess a page size:

```bash
ffuf -u "http://$BoxIP:$WebPort/FUZZ" -w /usr/share/wordlists/dirb/common.txt -e .php,.txt,.html,.bak -ac -t 20 -o "$BoxDir/nmap/ffuf.json" -of json
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
- [ ] Interesting files are found → **Run `curl -sS "http://$BoxIP:$WebPort/$Path" -o "$BoxDir/loot/$Filename"`, then go to Step 17 · [[Linux - Credential Search]]**
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

## Downloaded server or client binary

Some static pages disclose a custom service binary instead of an application login. Save the response and download the archive exactly as linked; the README may define a terminator or warn that the service is single-shot.

> **Why:** A local copy allows safe debugging and prevents repeated network probes from consuming a fragile service before the exploit is ready.
```bash
curl -sS "http://$BoxIP:$WebPort/" -o "$BoxDir/loot/index.html"
wget "http://$BoxIP:$WebPort/$Path" -O "$BoxDir/loot/$Archive"
unzip -l "$BoxDir/loot/$Archive"
unzip -d "$BoxDir/loot/$Directory" "$BoxDir/loot/$Archive"
cat "$BoxDir/loot/$Directory/README.txt"
file "$BoxDir/loot/$Directory/$File"
```

> [!warning] 💡
> If the README requires a null terminator or warns that the server crashes after requests, start the callback listener before the first exploit attempt and do not use readiness probes.

## Additional routing

- [ ] A downloadable PE or custom server is found → **Read its README, run `file $BoxDir/loot/$File`, then go to Step 7B · [[Linux - Binary Analysis]] before exploit selection**
- [ ] Only ordinary web files are found → **Continue with the existing content-discovery branches**

## Exposed development files and web shells

Treat directories such as `/dev/` as application content, not harmless developer leftovers. A readable PHP web shell is command execution even when the page has no login or upload form. Save the source, then prove execution with a harmless identity command before requesting a callback.

> **Why:** This request retrieves the exposed file and confirms its command parameter and execution identity without sending a shell payload first.
```bash
curl -sS "http://$BoxIP:$WebPort/$Path" -o "$BoxDir/loot/$Filename"
grep -Ein 'cmd|command|POST|GET|shell_exec|system|passthru' "$BoxDir/loot/$Filename"
curl -sS -X POST --data-urlencode 'cmd=id' "http://$BoxIP:$WebPort/$Path"
```

> [!warning] 💡
> Do not assume a page named `phpbash` is safe to browse interactively. Preserve the source, use a harmless `id` probe, and move to Step 8A · [[Linux - Command Injection]] for the callback path.

## Additional routing

- [ ] A readable PHP web shell or command parameter is found → **Save the source with `curl`, submit `cmd=id` using `--data-urlencode`, then go to Step 8A · [[Linux - Command Injection]]**
- [ ] The path is readable but execution is disabled → **Record the source as loot and continue ordinary content discovery**

## Source archives and backup review

When enumeration finds a downloadable archive under a backup or development path, save it locally before testing the application further. Source often reveals upload field names, filename transformations, cron paths, and command sinks that directory brute forcing cannot show.

> **Why:** These commands preserve the archive and expose its file list and source without executing anything on the target.
```bash
mkdir -p "$BoxDir/loot/source"
curl -sS "http://$BoxIP:$WebPort/$Path" -o "$BoxDir/loot/backup.tar"
tar -tvf "$BoxDir/loot/backup.tar"
tar -xf "$BoxDir/loot/backup.tar" -C "$BoxDir/loot/source"
grep -RniE 'upload|move_uploaded_file|exec\(|system\(|cron|crontab|filename|mime' "$BoxDir/loot/source"
```

## Additional routing

- [ ] A source archive exposes an upload handler → **Go to Step 9 · [[Linux - File Upload]] and preserve the exact multipart field and filename logic**
- [ ] Source passes a filename into a shell command → **Go to Step 8A · [[Linux - Command Injection]] and test with a harmless marker first**
- [ ] Source reveals a scheduled job or user home path → **Record it as local-enumeration loot, then go to Step 13 · [[Linux - Local Enum]] after a shell lands**

## Application file listings and backup files

When a custom PHP homepage names test scripts, request each path directly and inspect any directory-listing endpoint. A readable backup may contain credentials even when no login form is present.

```bash
curl -sS "http://$BoxIP:$WebPort/listfiles.php"
curl -sS "http://$BoxIP:$WebPort/$Path" -o "$BoxDir/loot/$Filename"
```

> [!warning] 💡
> Save long responses before decoding them. Keep the decoded credential or token in private loot and redact screenshots.

## Additional routing

- [ ] A file listing exposes a backup or credential-bearing text file → **Save it to `$BoxDir/loot/`, then go to Step 17 · [[Linux - Credential Search]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Cockpit|Cockpit]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- HTML comment and README exposed Nibbleblog
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- Gobuster found the music site, whose source linked to OpenNetAdmin
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- homepage disclosed the downloadable Dawn PE server
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- exposed `/dev/phpbash.php` provided command execution as the web user
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- Stark Hotel source exposed room.php and the WAF behaviour
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- WhatWeb and Gobuster identified Magento paths and a readable configuration file
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- Gobuster found a source backup, upload endpoint, upload listing, and upload directory
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- Gobuster and homepage review found PHP test pages, listfiles.php, and pwdbackup.txt
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- robots.txt and Gobuster exposed dotfiles, shell history, `/taxes`, and an SSH key directory
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- robots.txt and Gobuster exposed WordPress and Monstra; REST API and aggressive WPScan identified the useful plugin branch
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- Gobuster and Apache indexing exposed `/dev/`, `hype_key`, and developer notes
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- cautious content discovery and Nostromo home-directory mapping exposed the protected archive path
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- HTML attacker clue and a clue-specific PHP-shell wordlist exposed SmEvK

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Binary Analysis]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
