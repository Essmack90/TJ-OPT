# FAQ — Quick Answers

*One-line answers + a link. Not here to explain, here to route.*

---

## Ground Rules (read this first)

**No Metasploit for initial exploitation during OSCP practice.** Manual techniques only unless the module explicitly teaches MSF. Same for sqlmap, learn the injection by hand first.

**Ask twice rule.** If you're stuck and ask how to proceed:
- First answer = which module or stage note to check.
- Second ask = actual technique walkthrough.
This is intentional. The goal is to make the module knowledge stick, not to be handed steps.

**When to take a screenshot:** [[OSCP Habits - Screenshot & Loot]] has the full checklist. The short version: any time something *works*, screenshot it before moving on.

**When to store loot:** immediately on finding it, creds, hashes, keys, flags. Don't rely on terminal history.

---

## Discovery

### "I've got open ports, what now?"
→ [[Port Scan - Results Triage]], triage by service, then pick a lane

### "Nmap is taking forever"
→ `nmap -p- --min-rate 10000 $BoxIP` first pass, then `-sC -sV -p <ports>` on what comes back

### "I can see a web port, where do I start?"
→ [[HTTP - Initial Recon]], browser first, then dir brute

### "I only see one open port and it's not obvious"
→ [[Port Scan - Results Triage]], add UDP: `sudo nmap -sU --top-ports 20 $BoxIP`

### "How do I know what version something is running?"
→ `nmap -sV` on the port, then searchsploit or [HackTricks](https://book.hacktricks.xyz) for that service + version

---

## Footprinting

### "SMB is open, what can I do without creds?"
→ [[SMB - Null Session]], null session listing first

### "FTP is open, worth trying?"
→ [[FTP - Anonymous]], anonymous login first, always

### "There's a web app — how do I find the hidden stuff?"
→ [[HTTP - Directory Brute]], run a dir brute, recurse into anything that returns 200/301

### "I think it's running WordPress / Joomla / Drupal"
→ [[HTTP - CMS Detection]], check `/wp-login.php`, `wpscan`, `droopescan`

### "There are vhosts / subdomains — how do I find them?"
→ [[HTTP - Subdomain Enum]] ← [[06. Information Gathering|Information Gathering]]

---

## Foothold

### "I've got a shell but it's rubbish, how do I make it not rubbish?"
→ [[Shell - Upgrade]], `python3 -c 'import pty;pty.spawn("/bin/bash")'` → Ctrl+Z → `stty raw -echo; fg`

### "I've got creds but nowhere obvious to use them"
→ [[Port Scan - Results Triage]], spray across SSH, SMB, RDP, WinRM, HTTP login forms

### "I found a file upload, can I get a shell from it?"
→ [[Foothold - File Upload]], check what extensions are blocked and where files land

### "I found what looks like command injection"
→ [[Web App - Command Injection]], test with `; id`, `| id`, `&& id`, backticks

### "The box has a CVE — where do I start?"
→ [[13. Locating Public Exploits|Locating Public Exploits]], `searchsploit`, GitHub, [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings). Read the exploit before running it.

---

## PrivEsc

### "I'm on Linux, where do I even start?"
→ [[PrivEsc Linux - Initial Enum]], `linpeas.sh` first, then `sudo -l`, SUID, cron

### "I'm on Windows, where do I even start?"
→ [[PrivEsc Windows - Initial Enum]], `winPEAS.exe` first, then services, scheduled tasks, unquoted paths

### "sudo -l shows something but I don't know what to do with it"
→ [GTFOBins](https://gtfobins.github.io), search the binary, pick the `sudo` section

### "I can see a service running as SYSTEM/root"
→ [[PrivEsc Windows - Services]] or [[PrivEsc Linux - Writable Config]], is the binary or config writable?

### "There's a cronjob / scheduled task"
→ [[PrivEsc Linux - Cron]] / [[PrivEsc Windows - Scheduled Tasks]], can you write the target script/binary?

### "I've got a hash, how do I use it?"
→ [[16. Password Attacks|Password Attacks]], crack with hashcat (identify type with hash-identifier first) or pass-the-hash if NTLM

---

## Web App

### "There's a login form"
→ Try `admin:admin`, `admin:password`, `admin:$BoxName` first, then [[Web App - SQLi]] for bypass

### "I think it's LFI"
→ [[Web App - LFI]], start with `../../../etc/passwd`, escalate to log poisoning or PHP wrappers

### "I think it's SQLi — where do I inject?"
→ [[Web App - SQLi]], test manually with `'`, `"`, `'--`, `1=1--` before anything else

### "The app is making outbound requests to something I control"
→ [[Web App - SSRF]], probe `http://127.0.0.1:PORT`, internal services, cloud metadata endpoint

### "I need to encode/decode/transform something weird"
→ [CyberChef](https://gchq.github.io/CyberChef/), it does everything

---

## Troubleshooting

### "My reverse shell won't connect back"
→ Confirm `$LocalIP` is `tun0` not `eth0`, listener is up, try port 443 or 80 if egress is filtered

### "The exploit runs but nothing happens"
→ Check architecture (x86 vs x64), check AV/defender, try a different payload type, [RevShells](https://www.revshells.com) for alternatives

### "I can't transfer a file to the target"
→ [[17. Windows Privilege Escalation]], python HTTP server + curl/wget/iwr, or base64 encode it

### "I'm completely stuck and have been on this for a while"
→ Back to [[Port Scan - Results Triage]], missed port? missed vhost? missed parameter? check [ippsec.rocks](https://ippsec.rocks) for the box name or a technique keyword
