# Web and Services

Use one fast fingerprint, one recursive content scan, and Burp Suite for request discovery or replay. Save every response that changes the branch. Stop scanning once a real path, form, API, source archive, credential, or upload mechanism is identified.

## Fast loop

### Run this

~~~bash
boxset WebURL "http://$BoxIP:$WebPort"
httpx-toolkit -u "$WebURL" -sc -title -tech-detect -server -o "$BoxDir/loot/httpx.txt"
curl -sS -i --max-time 30 "$WebURL/" | tee "$BoxDir/loot/http-root.txt"
feroxbuster -u "$WebURL/" -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html,bak,old,zip -t 30 -o "$BoxDir/nmap/ferox.txt"
~~~

### Example output

~~~text
200  GET  /login
301  GET  /admin  -> /admin/
200  GET  /robots.txt
~~~

### What did you get?

- [ ] CMS or framework fingerprint -> **Open the matching CMS row below and then [[OSCP/RUNBOOK V2/Linux - CMS Check|CMS Check]].**
- [ ] Login, API, or unusual method response -> **Start Burp, send the request to Repeater, and test one change at a time.**
- [ ] Upload form -> **Open [[OSCP/RUNBOOK V2/Linux - File Upload|Linux File Upload]] or [[OSCP/RUNBOOK V2/Windows - Web - FTP Upload|Windows FTP Upload]].**
- [ ] File parameter or XML input -> **Open [[OSCP/RUNBOOK V2/Linux - LFI|Linux LFI]] or [[OSCP/RUNBOOK V2/Windows - XXE|Windows XXE]].**
- [ ] Source archive, JAR, or backup -> **Save it, then open [[OSCP/RUNBOOK V2/Linux - Binary Analysis|Binary Analysis]] or [[OSCP/RUNBOOK V2/Linux - Credential Search|Credential Search]].**
- [ ] SQL-looking or command-shaped input -> **Confirm manually, then open the matching row below.**
- [ ] Known static path works but scanning is slow -> **Run the slow-response check below; do not restart the VPN based on application timing alone.**
- [ ] No useful path -> **Run vhost fuzzing, then return to [[OSCP/EXAM RUNBOOK/07 - Branch Matrix|Branch Matrix]].**

### Open next

Use Burp for request discovery and replay, then follow the first matching application row. If a shell arrives, open the Linux or Windows fast path.

## 1. Fingerprint

~~~bash
boxset WebURL "http://$BoxIP:$WebPort"
httpx-toolkit -u "$WebURL" -sc -title -tech-detect -server -o "$BoxDir/loot/httpx.txt"
curl -sS -i --max-time 30 "$WebURL/" | tee "$BoxDir/loot/http-root.txt"
~~~

## 2. Fast content discovery

~~~bash
feroxbuster -u "$WebURL/" -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html,bak,old,zip -t 30 -o "$BoxDir/nmap/ferox.txt"
~~~

If the target is fragile, use a smaller thread count and manual requests instead of running several scanners at once:

~~~bash
ffuf -u "$WebURL/FUZZ" -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -e .php,.txt,.html -ac -t 20 -of json -o "$BoxDir/loot/ffuf.json"
~~~

## 3. Burp fast path

~~~bash
burpsuite &
curl --proxy 127.0.0.1:8080 -sS "$WebURL/$Path" -o "$BoxDir/loot/burp-response.txt"
~~~

Use Burp Proxy to capture the real request, Repeater to change one parameter at a time, and Site map to preserve discovered routes. Use the response code, reflected value, timing, and body length as branch evidence.

## 4. Hostname and vhost branch

~~~bash
ffuf -u "http://$BoxIP:$WebPort/" -H "Host: FUZZ.$Domain" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -fs "$BaselineSize" -of json -o "$BoxDir/loot/vhosts.json"
~~~

Set `$FQDN` only after a response differs from the baseline, then add the mapping through the normal hosts workflow before re-running the request.

## 5. Application branches

| Finding | Next command or page |
|---|---|
| WordPress | `wpscan --url "$WebURL" --enumerate u,vp,vt`; then [[OSCP/RUNBOOK V2/Linux - CMS Check\|Linux - CMS Check]] |
| Drupal, Joomla, or another CMS | Fingerprint the exact version; open [[OSCP/RUNBOOK V2/Linux - CMS Check\|Linux - CMS Check]] |
| REST or JSON endpoint | Capture in Burp, replay with curl, and compare 200, 401, 403, 404, and 405 responses |
| File parameter | Test `/etc/passwd` or the Windows hosts file, then open [[OSCP/RUNBOOK V2/Linux - LFI\|Linux - LFI]] |
| Upload form | Capture the multipart request, test extension and MIME controls, then open [[OSCP/RUNBOOK V2/Linux - File Upload\|Linux - File Upload]] |
| SQL-looking parameter | Confirm manually and open [[OSCP/RUNBOOK V2/Linux - SQLi\|Linux - SQLi]] |
| Shell metacharacter or command field | Test harmless output and open [[OSCP/RUNBOOK V2/Linux - Command Injection\|Linux - Command Injection]] |
| Source archive or compiled artifact | Download it into loot, then open [[OSCP/RUNBOOK V2/Linux - Binary Analysis\|Linux - Binary Analysis]] or [[OSCP/RUNBOOK V2/Linux - Credential Search\|Linux - Credential Search]] |
| Java plugin or Minecraft web artifact | Use `jar tf`, `javap`, and the [[OSCP/BOXES/WRITE UPS/Linux/Blocky\|Blocky]] pattern |

## 6. Slow response branch

~~~bash
curl -sS --max-time 60 -o /dev/null \
  -w 'code=%{http_code} connect=%{time_connect} start=%{time_starttransfer} total=%{time_total}\n' \
  "$WebURL/$Path"
~~~

If a known static path works but a dynamic API or scanner is slow, increase the request timeout, lower concurrency, and continue with confirmed paths. Do not restart the VPN solely because of an application timeout.

## Detailed routes

- [[OSCP/RUNBOOK V2/Linux - Web Enum|RUNBOOK V2 Linux Web Enum]]
- [[OSCP/RUNBOOK V2/Web - Virtual Host Enumeration|RUNBOOK V2 VHost Enumeration]]
- [[OSCP/COMMAND APPENDIX/Web Applications|Web Applications Command Appendix]]
- [[OSCP/DECISION TREE/Web Applications (Decision Tree)|Web Applications Decision Tree]]
- [[05_BURP_SUITE_COMPLETE_GUIDE/05_BURP_SUITE_COMPLETE_GUIDE|Burp Suite guide]]
