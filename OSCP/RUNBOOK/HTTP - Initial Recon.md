---
tags: [oscp, http, recon, runbook]
box_sources: [Pelican, Pebbles]
---

# HTTP — Initial Recon

*You've found an HTTP port. Goal: identify what's running, confirm it's reachable, and decide which sub-track to pursue.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| Browse to `http://$BoxIP:$WebPort/` in Firefox | Page title, app name, login form, or error message | Always — first thing | Read the page source too (`Ctrl+U`). Headers, comments, and meta tags often leak version info or framework. | Sub-track below | Try HTTPS (`https://`) if HTTP is blank |
| `curl -I http://$BoxIP:$WebPort/` | `Server:`, `X-Powered-By:`, `Location:` headers | Quick header check without a browser | `-I` is HEAD only. If there's a redirect, `Location:` tells you where to go next. Add `-L` to follow it. | Check redirect target | Try `-k` for HTTPS |
| `curl -L http://$BoxIP:$WebPort/` | Final page content after following redirects | Redirect chains (nginx → Jetty, etc.) | nginx on one port often proxies to an app on another. Check the `Location:` header — it names the real service. | Browse to the final URL | — |
| `whatweb http://$BoxIP:$WebPort/` | CMS, framework, version strings | Quick tech fingerprint | Faster than manual header reading. Flag unusual or old versions immediately → searchsploit them. | [[HTTP - CMS Detection]] if CMS found | — |

---

## Sub-track Decision

After identifying what's on the port:

| What you see | Where to go |
|---|---|
| Login form | Try default creds first. Then check for known CVEs in the app version. |
| Directory listing | Browse manually. Look for config files, backups, `.git/`. |
| CMS (WordPress, Joomla, etc.) | [[HTTP - CMS Detection]] |
| Admin UI (Exhibitor, Tomcat Manager, etc.) | Check for default creds. Check for known unauthenticated vulnerabilities. Searchsploit the version. |
| Custom web app | [[HTTP - Directory Brute]] then [[Web App - Command Injection]], [[Web App - LFI]], etc. |
| 403 / 404 everywhere | [[HTTP - Directory Brute]] — the interesting path may just not be at `/` |

---

## Pelican example (what caught the flag)

nginx on port 8081 returned a redirect:
```
Location: http://192.168.119.98:8080/exhibitor/v1/ui/index.html
```

Following the redirect revealed the **Exhibitor for ZooKeeper** admin UI — unauthenticated, running on Jetty on port 8080. The URL structure (`/exhibitor/v1/`) confirmed the exact application, and the version (ZooKeeper 3.4.6, built 2014) pointed to known vulnerabilities.

> Always follow redirects and read `Location:` headers — nginx on one port, app on another, is a common pattern.

---

**Module:** [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]], [[06. Information Gathering|Information Gathering]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
