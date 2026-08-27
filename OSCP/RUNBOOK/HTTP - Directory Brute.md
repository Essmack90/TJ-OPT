---
tags: [oscp, http, directory-brute, runbook]
box_sources: [Zenphoto]
---

# HTTP — Directory Brute

*Root of the web server looks empty or returns a placeholder. Brute force directories to find hidden paths.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `gobuster dir -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -o gobuster-root.txt` | `/test (Status: 301)` or similar | Web server is up | Start with `common.txt` — fast and hits most standard paths. Note 301 (redirect) and 200 (direct hit). Ignore 403 (forbidden but exists). | Browse each found path: `curl -s http://$BoxIP/<path>/` | Nothing found → try bigger wordlist |
| `gobuster dir -u http://$BoxIP/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -o gobuster-medium.txt` | Additional paths | common.txt found nothing | Slower but much broader. Use when common.txt misses. | Browse found paths | Nothing → check vhosts, try other ports |
| `gobuster dir -u http://$BoxIP/<path>/ -w /usr/share/wordlists/dirb/common.txt -o gobuster-<path>.txt` | Subdirectory hits | Found a path worth recursing into | Recurse into each interesting directory found. | Browse each subpath | Nothing → move to next found directory |

---

## Why dir busting matters

A bare root page ("UNDER CONSTRUCTION", 404, blank) does not mean there's nothing there. Applications are often installed under a subdirectory:
- `/wordpress/` — WordPress
- `/test/` — dev/test installs
- `/admin/` — admin panels
- `/phpmyadmin/` — database UIs
- `/backup/` — backup files

Dir busting finds these. It is non-optional on any HTTP port.

---

## Zenphoto Example

```bash
gobuster dir -u http://192.168.183.41/ -w /usr/share/wordlists/dirb/common.txt -o gobuster-root.txt
# Found: /test (Status: 301) --> http://192.168.183.41/test/
```

Root returned "UNDER CONSTRUCTION". `/test/` contained Zenphoto 1.4.1.4 — the entire attack surface.

---

## Module Links

[[08. Introduction to Web Application Attacks]] | [[06. Information Gathering]]
