# Web Requests & Delivery, Command Appendix

Part of [[COMMAND APPENDIX]]. General-purpose request crafting and payload hosting, used across almost every other area in this appendix.

---

## Curl: Web Requests and Payload Delivery

```bash
# Basic GET
curl http://<target>/<path>

# POST with form data (raw, NOT auto-encoded, watch out for &/=/spaces in the value)
curl -X POST --data 'key=value' http://<target>/<path>

# POST with proper percent-encoding (use whenever the value has &, =, spaces, or quotes)
curl -X POST --data-urlencode 'key=value with spaces & symbols' http://<target>/<path>

# Save raw response to a file instead of printing it (needed before extracting a multi-line secret)
curl -s "http://<target>/<path>" -o raw_response.txt

# Route a request through Burp for logging/replay
curl --proxy 127.0.0.1:8080 http://<target>/<path>

# Force curl to send the literal path as-is (don't let curl "clean up" ../ sequences itself)
curl --path-as-is "http://<target>/<traversal-path>"
```
See [[09. Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]] (mechanical secret extraction), [[09. Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] (`--data-urlencode` lesson), [[07. Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]] (`--path-as-is`).

#### Tags: #Curl #DataUrlencode #PathAsIs

---

## Python HTTP Server

```bash
cd <directory-to-serve>   # ALWAYS cd here immediately before starting, it serves whatever dir it's launched from
python3 -m http.server 80
```
**Known gotcha:** if restarted later from a different working directory, it silently serves the wrong files (a request for your payload 404s instead of erroring loudly). Check the access log shows a `200` for your payload's filename before assuming a listener is broken.

See [[09. Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3 troubleshooting box]].

#### Tags: #PythonHttpServer

---

## **Outstanding**
This area grows alongside the modules. Whenever a new request-crafting or payload-hosting pattern comes up (wget, openssl s_client, socat as a relay, etc), add it here with a link back to the source section.
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
