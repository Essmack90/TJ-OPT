---
tags: [HTB, Mirai, Linux, RaspberryPi, PiHole, DefaultCredentials, SSH, Sudo, Forensics, Easy]
platform: HackTheBox
os: Debian 8 Jessie i686
hostname: raspberrypi
difficulty: Easy
ip: $BoxIP
status: Complete
domain: ""
---

# HTB: Mirai, Full Walkthrough

## The gist

Mirai is an IoT-focused Linux box. A full TCP scan found SSH, DNS, a lighttpd web server, and Plex-related services. The web root disclosed Pi-hole, and `/admin/` identified an old Pi-hole release. The useful route was not a web exploit: the Raspberry Pi account still accepted its unchanged factory credential, giving SSH access as `pi`.

Local enumeration then showed that `pi` belonged to `sudo` and could run every command as root without a password. That made the privilege escalation a direct sudo validation. The final enumeration also recorded a small USB device mounted at `/media/usbstick`; it was treated as a forensic clue, and its contents were not reproduced in this note.

Attack chain:

~~~text
Full TCP scan -> Pi-hole fingerprint -> unchanged IoT credential
-> SSH as pi -> NOPASSWD: ALL -> root identity proof
-> mounted USB metadata recorded without reading private completion data
~~~

> [!warning] Flag and credential boundary
> This note records no flag values, passwords, hashes, or private completion material. The factory credential was entered privately during the run and is intentionally not reproduced.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Debian 8 Jessie, i686 |
| Hostname | `raspberrypi` |
| Target | `$BoxIP` |
| Services | SSH 22, DNS 53, HTTP 80, UPnP 1555 and 32469, Plex 32400 |
| Primary route | Pi-hole fingerprint -> default IoT credential -> SSH -> passwordless sudo |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Initialise the workspace and scan every TCP port | See section 1 below |
| 2 | Identify service versions | See section 2 below |
| 3 | Fingerprint the web root | See section 3 below |
| 4 | Enumerate web paths and inspect Pi-hole | See section 4 below |
| 5 | Record the application version and choose the credential branch | See section 5 below |
| 6 | Validate the IoT account over SSH | See section 6 below |

## Evidence and loot

The source evidence is under `~/Platforms/HackTheBox/Mirai/`. The autonomous run record and working artifacts are under `/tmp/codex_Mirai/`; the source directory was read only.

Safe evidence copied beside this note:

- `mirai-1-nmap-allports.png`: complete TCP scan.
- `mirai-2-nmap-services.png`: focused service and version scan.
- `mirai-3-http-root.png`: Pi-hole response fingerprint at the web root.
- `mirai-4-gobuster-root.png`: `/admin/` discovery.
- `mirai-5-pihole-admin.png`: Pi-hole administration page.
- `mirai-6-pihole-version.png`: Pi-hole version information.
- `mirai-7-ssh-foothold.png`: SSH session as `pi`.
- `mirai-8-sudo-l.png`: unrestricted passwordless sudo rule.
- `mirai-9-lsblk.png`: mounted USB device and storage layout.

Private completion records and any sensitive values remain outside the vault.

## Variables

Use the helper variables in the normal box workspace. Keep scan output, HTTP responses, and private credential tests under `$BoxDir`.

~~~bash
boxstart "Mirai" "$BoxIP" htb
boxset BoxName "Mirai"
boxset BoxDir "$HOME/Platforms/HackTheBox/Mirai"
boxset WebPort "80"
boxset SshPort "22"
boxset DnsPort "53"
boxset UpnpPort1 "1555"
boxset PlexPort "32400"
boxset UpnpPort2 "32469"
boxset Username "pi"
boxset AdminUser "root"
boxset UsbDevice "/dev/sdb"
boxset UsbMount "/media/usbstick"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
mkdir -p "$BoxDir/nmap" "$BoxDir/loot" "$BoxDir/exploits" "$BoxDir/screenshots"
~~~

## 1. Initialise the workspace and scan every TCP port

Start with all TCP ports. Mirai exposes more than the usual SSH and HTTP pair, so a top-ports scan alone would have hidden the DNS, UPnP, and Plex attack surface. Save all Nmap formats for later review.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 \\
  --host-timeout 5m -T4 \\
  -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
~~~

The decisive output was:

~~~text
22/tcp     open  ssh
53/tcp     open  domain
80/tcp     open  http
1555/tcp   open  upnp
32400/tcp  open  plex
32469/tcp  open  unknown
~~~

The next stage is a focused version scan across every discovered port.

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/1.nmap-allports.png>)
SCREENSHOT: Complete TCP scan. The additional non-standard services are the reason the full-range scan matters.

## 2. Identify service versions

Run default scripts and version detection against the ports that survived the full scan.

~~~bash
boxset OpenPorts "22,53,80,1555,32400,32469"
sudo nmap -Pn -n -sC -sV --version-light \\
  -p "$OpenPorts" \\
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

The useful service details were:

| Port | Finding | Next decision |
|---|---|---|
| 22/tcp | OpenSSH 6.7p1 | Test discovered or vendor-default credentials privately |
| 53/tcp | dnsmasq 2.76 | Record DNS exposure; test only if the application gives a hostname or zone clue |
| 80/tcp | lighttpd 1.4.35 | Inspect the web root and enumerate paths |
| 1555/tcp, 32469/tcp | Platinum UPnP | Record as IoT attack surface; do not assume it is the foothold |
| 32400/tcp | Plex Media Server, unauthorized | Record the service and move on unless the web surface provides a route |

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/2.nmap-services.png>)
SCREENSHOT: Focused service scan. The service mix identifies this as an IoT-style host rather than a normal web-only Linux box.

## 3. Fingerprint the web root

Request the root page with headers included. The response was a 404, but the `X-Pi-hole` header identified the product and the lighttpd banner confirmed the web server.

~~~bash
curl -sS -i "http://$BoxIP:$WebPort/" \\
  | tee "$BoxDir/loot/http-root.txt"
grep -Ein 'pi-hole|lighttpd|version|admin|login' "$BoxDir/loot/http-root.txt"
~~~

Focus on product headers even when the status is 404. A 404 response can still disclose the application that owns the virtual host.

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/3.http-root.png>)
SCREENSHOT: The web-root response. The Pi-hole header is the useful finding; the 404 status does not invalidate the fingerprint.

## 4. Enumerate web paths and inspect Pi-hole

Run a small path scan against the web root. The important result was `/admin/`, which redirected to the Pi-hole administration interface.

~~~bash
gobuster dir -u "http://$BoxIP:$WebPort/" \\
  -w /usr/share/wordlists/dirb/common.txt \\
  -t 20 \\
  -o "$BoxDir/nmap/gobuster-root.txt"

curl -sS -i -L "http://$BoxIP:$WebPort/admin/" \\
  | tee "$BoxDir/loot/http-admin.txt"
~~~

The output to focus on:

~~~text
/admin/    (Status: 301)
X-Pi-hole: The Pi-hole Web interface is working!
~~~

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/4.gobuster-root.png>)
SCREENSHOT: Gobuster finds the Pi-hole administration path.

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/5.1.pi-hole-admin-footer.png>)
SCREENSHOT: Pi-hole login and administration surface. The page confirms that this is a product login, not a generic lighttpd directory.

## 5. Record the application version and choose the credential branch

The administration page identified Pi-hole v3.1.4, Web Interface v3.1, and FTL v2.10. This is old IoT software, so the next test is a vendor-default credential check performed privately, not blind brute force.

~~~bash
curl -sS -L "http://$BoxIP:$WebPort/admin/" \\
  | grep -Ein 'Pi-hole|Web Interface|FTL|version|login|password'
~~~

An exposed `.git/HEAD` and `.git/config` were also checked. They confirmed repository metadata associated with the web interface, but did not produce a site-specific secret. Treat this as context and stop spending time on the web repository when SSH offers a more direct validation path.

~~~bash
curl -sS "http://$BoxIP:$WebPort/admin/.git/HEAD" \\
  | tee "$BoxDir/loot/pihole-git-head.txt"
curl -sS "http://$BoxIP:$WebPort/admin/.git/config" \\
  | tee "$BoxDir/loot/pihole-git-config.txt"
~~~

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/5.2.ph-hole-sidebar-version-admin.png>)
SCREENSHOT: Version information from the Pi-hole administration page. The old release supports the decision to check unchanged IoT credentials.

> [!warning] 💡 Gotcha
> A product login and an SSH login are separate validation targets. Once the host identity and default-account pattern are clear, test the account against SSH once. Do not spray the credential across unrelated services.

## 6. Validate the IoT account over SSH

Use the discovered account name and enter the lab-approved factory credential privately at the prompt. Do not put the value in a shell history, screenshot, or report.

~~~bash
ssh -o PreferredAuthentications=password \\
  -o PubkeyAuthentication=no \\
  -p "$SshPort" "$Username@$BoxIP"
~~~

Confirm the session identity immediately:

~~~bash
id
whoami
hostname
pwd
~~~

The successful result was an SSH foothold as `pi` on `raspberrypi`. That changes the next step from web enumeration to local privilege enumeration.

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/6.ssh-foothold.png>)
SCREENSHOT: SSH foothold as `pi`. The identity output is the proof that the credential test reached the intended account.

## 7. Run local identity and operating-system checks

Collect the minimum local context before selecting an escalation route.

~~~bash
id
groups
hostname
uname -a
cat /etc/os-release 2>/dev/null
~~~

The useful output identified Debian GNU/Linux 8 Jessie on a 32-bit Raspberry Pi kernel. The `pi` account belonged to the `sudo` group, so `sudo -l` became the highest-value next check.

## 8. Check sudo permissions

Use non-interactive sudo first. It distinguishes a passwordless rule from a rule that merely names a command but still requires a password.

~~~bash
sudo -n -l
~~~

The decisive rule was:

~~~text
User pi may run the following commands on localhost:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
~~~

This is a direct root path. There is no reason to search for a kernel exploit, SUID binary, or Pi-hole exploit after this output.

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/7.sudo-l.png>)
SCREENSHOT: `sudo -n -l` shows unrestricted passwordless sudo. Red marks the rule that determines the escalation path.

## 9. Prove root through the permitted sudo rule

Run a controlled identity proof through sudo. The command does not modify the target and makes the privilege boundary explicit.

~~~bash
sudo -n sh -c 'id; whoami; hostname; pwd'
~~~

The proof was `uid=0(root)`, `whoami` returned `root`, and the hostname remained `raspberrypi`.

## 10. Record mounted-media evidence without reading completion data

The root session exposed a small USB device mounted read-only at `/media/usbstick`. Record device, mount, and file metadata first. This preserves the forensic observation without printing private completion content into the terminal or vault.

~~~bash
mount | grep -E '/media|/dev/sd'
lsblk -f
df -h
UsbMount=/media/usbstick
UsbDevice=/dev/sdb
ls -la "$UsbMount"
file -s "$UsbDevice"
stat "$UsbMount"/* 2>/dev/null
~~~

The relevant result was a 10M `/dev/sdb` mounted read-only at `/media/usbstick`, containing a small text artifact and `lost+found`. The artifact was not opened. Do not run `cat`, `strings`, or `grep` against completion files unless the exercise specifically requires forensic recovery and the output is being kept private.

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/9.lsblk.png>)
SCREENSHOT: `lsblk` records the mounted USB device and its read-only mount point.

## 11. RUNBOOK V2 stages used

- [[RUNBOOK V2/Start Here|Start Here]]: workspace variables and full TCP scan.
- [[RUNBOOK V2/Port Triage|Port Triage]]: SSH, DNS, HTTP, UPnP, and Plex classification.
- [[RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]]: version and default-script scan.
- [[RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]]: root fingerprint and `/admin/` discovery.
- [[RUNBOOK V2/Linux - IoT Default Credentials|Linux - IoT Default Credentials]]: vendor fingerprint, factory-credential validation, and mounted-media note.
- [[RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]]: credential handling boundary and one-service validation.
- [[RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]: identity, architecture, OS, storage, and device review.
- [[RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]]: `NOPASSWD: ALL` decision.
- [[RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]: no target-side changes and session closeout.

## 12. Decision points

| Observation | Meaning | Next action |
|---|---|---|
| Full scan shows 22, 53, 80, 1555, 32400, and 32469 | The host is broader than a normal SSH/web target | Version-scan every open port |
| `X-Pi-hole` header and `/admin/` path | Pi-hole is the web product | Record version and check the vendor-default account pattern |
| `.git/HEAD` is readable | Web metadata is exposed | Save it, but do not assume it contains the foothold |
| SSH succeeds as `pi` | The unchanged IoT account is still usable | Run local identity and sudo checks |
| `sudo -n -l` shows `NOPASSWD: ALL` | The current account can become root directly | Use a harmless sudo identity proof |
| `/dev/sdb` is mounted read-only | There is a forensic storage clue | Record metadata only and protect private completion data |

## 13. Collect the flags

| Flag | Location | Status |
|---|---|---|
| User | Private completion record | Obtained privately; value reproduced in the private Flags section above |
| Root | Private completion record | Obtained privately; value reproduced in the private Flags section above |


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: ff837707441b257a20e32199d7c8838d
root: 3d3e483143ff12ec505d026fa13e020b
```

## 14. Clean down
No target-side payload, uploaded file, persistence mechanism, or configuration change was required. Exit the root and SSH sessions, then verify that no Kali-side listener or temporary transfer server remains.

~~~bash
exit
exit
ss -ltnp | grep ":$WebPort" || true
boxdone
~~~

The final evidence boundary is the saved scan, HTTP, SSH, sudo, and storage output. Keep any private completion record outside the shared vault.

### Completion checklist

- [x] Full TCP scan saved.
- [x] Focused service scan saved.
- [x] Pi-hole root fingerprint and `/admin/` path recorded.
- [x] Pi-hole version recorded.
- [x] SSH foothold identity verified.
- [x] Local OS and group context recorded.
- [x] Passwordless sudo rule verified.
- [x] Root identity verified without exposing a flag value.
- [x] Mounted USB metadata recorded without reading private completion data.
- [x] No target-side payload or configuration changes required.
- [x] Safe screenshots copied beside this note.

## 15. Attack narrative in one page
~~~text
Full TCP scan
  -> Pi-hole header and /admin/ discovery
  -> old Pi-hole version recorded
  -> default IoT credential validated privately against SSH
  -> pi foothold
  -> sudo -n -l shows NOPASSWD: ALL
  -> sudo identity proof as root
  -> read-only USB metadata recorded
~~~

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `ssh`
- `sudo`

## Credentials and secrets

| Account | Source | Validation | Vault handling |
|---|---|---|---|
| `pi` | Unchanged Raspberry Pi / IoT default credential pattern | Successful SSH login | Account name and credential value captured in the private credential section |
| `root` | `sudo` rule granted by `pi` | `sudo -n sh -c 'id; whoami'` | No password required; no secret value exists to record |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Mirai"
export BoxIP="10.129.1.86"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Mirai"
export Domain=""
export DCip=""
export Username=""
export Password=""
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

### Sensitive transcript evidence

```text
[sudo] password for kali:
Set-Cookie: PHPSESSID=m9gs0dvdqtudh3ksqhue17joh5; path=/
<!-- Send token to JS -->
<div id="token" hidden></div>
pi@10.129.1.86's password:
SSH is enabled and the default password for the 'pi' user has not been changed.
This is a security risk - please login as the 'pi' user and type 'passwd' to set a new password.
$ [09:22:05] loot flag user ff837707441b257a20e32199d7c8838d
loot flag root 3d3e483143ff12ec505d026fa13e020b
    (ALL) NOPASSWD: ALL
kali@kali:~/Platforms/HackTheBox/Mirai [09:22:03] $ =loot flag user ff837707441b257a20e32199d7c8838d
loot flag root 3d3e483143ff12ec505d026fa13e020bloot
[+] Flag saved:  user = ff837707441b257a20e32199d7c8838d  →  loot/flags.txt
[+] Flag saved:  root = 3d3e483143ff12ec505d026fa13e020b  →  loot/flags.txt
```

### Additional captured source values

#### `loot/http-admin.txt`

```text
HTTP/1.1 200 OK
X-Pi-hole: The Pi-hole Web interface is working!
X-Frame-Options: DENY
Set-Cookie: PHPSESSID=m9gs0dvdqtudh3ksqhue17joh5; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Content-type: text/html; charset=UTF-8
Transfer-Encoding: chunked
Date: Fri, 11 Sep 2026 08:04:07 GMT
Server: lighttpd/1.4.35


<!DOCTYPE html>
<!-- Pi-hole: A black hole for Internet advertisements
*  (c) 2017 Pi-hole, LLC (https://pi-hole.net)
*  Network-wide ad blocking via your own hardware.
*
*  This file is copyright under the latest version of the EUPL.
*  Please see LICENSE file for your rights under this license. -->
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://api.github.com; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'">
    <title>Pi-hole Admin Console</title>
    <!-- Usually browsers proactively perform domain name resolution on links that the user may choose to follow. We disable DNS prefetching here -->
    <meta http-equiv="x-dns-prefetch-control" content="off">
    <!-- Tell the browser to be responsive to screen width -->
    <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
    <link rel="shortcut icon" href="img/favicon.png" type="image/x-icon" />
    <meta name="theme-color" content="#367fa9">
    <link rel="apple-touch-icon" sizes="180x180" href="img/favicon.png">
    <link rel="icon" type="image/png" sizes="192x192"  href="img/logo.svg">
    <link rel="icon" type="image/png" sizes="96x96" href="img/logo.svg">
    <meta name="msapplication-TileColor" content="#367fa9">
    <meta name="msapplication-TileImage" content="img/logo.svg">
    <meta name="apple-mobile-web-app-capable" content="yes">

    <link href="style/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet" type="text/css" />
    <link href="style/vendor/font-awesome-4.5.0/css/font-awesome.min.css" rel="stylesheet" type="text/css" />
    <link href="style/vendor/ionicons-2.0.1/css/ionicons.min.css" rel="stylesheet" type="text/css" />
    <link href="style/vendor/dataTables.bootstrap.min.css" rel="stylesheet" type="text/css" />

    <link href="style/vendor/AdminLTE.min.css" rel="stylesheet" type="text/css" />
    <link href="style/vendor/skin-blue.min.css" rel="stylesheet" type="text/css" />
    <link href="style/pi-hole.css" rel="stylesheet" type="text/css" />
    <link rel="icon" type="image/png" sizes="160x160" href="img/logo.svg" />
    <style type="text/css">
        .glow { text-shadow: 0px 0px 5px #fff; }
        h3 { transition-duration: 500ms }
    </style>

    <!--[if lt IE 9]>
    <script src="scripts/vendor/html5shiv.min.js"></script>
    <script src="scripts/vendor/respond.min.js"></script>
    <![endif]-->
</head>
<body class="skin-blue sidebar-mini layout-boxed">
<!-- JS Warning -->
<div>
    <link rel="stylesheet" type="text/css" href="style/vendor/js-warn.css">
    <input type="checkbox" id="js-hide" />
    <div class="js-warn" id="js-warn-exit"><h1>Javascript Is Disabled</h1><p>Javascript seems to be disabled. This will break some site features.</p>
        <p>To enable Javascript click <a href="http://www.enable-javascript.com/" target="_blank">here</a></p><label for="js-hide">Close</label></div>
</div>
<!-- /JS Warning -->
<script src="scripts/pi-hole/js/header.js"></script>
<!-- Send token to JS -->
<div id="token" hidden></div>
<div id="enableTimer" hidden></div>
<div class="wrapper">
    <header class="main-header">
        <!-- Logo -->
        <a href="http://pi-hole.net" class="logo" target="_blank">
            <!-- mini logo for sidebar mini 50x50 pixels -->
            <span class="logo-mini">P<b>h</b></span>
            <!-- logo for regular state and mobile devices -->
            <span class="logo-lg">Pi-<b>hole</b></span>
        </a>
        <!-- Header Navbar: style can be found in header.less -->
        <nav class="navbar navbar-static-top" role="navigation">
            <!-- Sidebar toggle button-->
            <a href="#" class="sidebar-toggle" data-toggle="offcanvas" role="button">
                <span class="sr-only">Toggle navigation</span>
            </a>
            <div class="navbar-custom-menu">
                <ul class="nav navbar-nav">
                    <!-- User Account: style can be found in dropdown.less -->
                    <li class="dropdown user user-menu">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">
                            <img src="img/logo.svg" class="user-image" style="border-radius: initial" sizes="160x160" alt="Pi-hole logo" />
                            <span class="hidden-xs">Pi-hole</span>
                        </a>
                        <ul class="dropdown-menu" style="right:0">
                            <!-- User image -->
                            <li class="user-header">
                                <img src="img/logo.svg" sizes="160x160" alt="User Image" style="border-color:transparent" />
                                <p>
                                    Open Source Ad Blocker
                                    <small>Designed For Raspberry Pi</small>
                                </p>
                            </li>
                            <!-- Menu Body -->
                            <li class="user-body">
                                <div class="col-xs-4 text-center">
                                    <a class="btn-link" href="https://github.com/pi-hole/pi-hole" target="_blank">GitHub</a>
                                </div>
                                <div class="col-xs-4 text-center">
                                    <a class="btn-link" href="http://jacobsalmela.com/block-millions-ads-network-wide-with-a-raspberry-pi-hole-2-0/" target="_blank">Details</a>
                                </div>
                                <div class="col-xs-4 text-center">
                                    <a class="btn-link" href="https://github.com/pi-hole/pi-hole/releases" target="_blank">Updates</a>
                                </div>
                                <div class="col-xs-12 text-center" id="sessiontimer">
                                    <b>Session is valid for <span id="sessiontimercounter">0</span></b>
                                </div>
                            </li>
                            <!-- Menu Footer -->
                            <li class="user-footer">
                                <!-- Version Infos -->
                                <div class="hidden-md hidden-lg">
                                    <b>Pi-hole Version </b> v3.1.4<br>
                                    <b>Web Interface Version </b>v3.1<br>
                                    <b>FTL Version </b> v2.10<br><br>
                                </div>
                                <!-- PayPal -->
                                <div class="text-center">
                                    <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&amp;hosted_button_id=3J2L3Z4DHW9UY" target="_blank" style="background:none">
                                        <img src="img/donate.gif" alt="Donate">
                                    </a>
                                </div>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </nav>
    </header>
    <!-- Left side column. contains the logo and sidebar -->
    <aside class="main-sidebar">
        <!-- sidebar: style can be found in sidebar.less -->
        <section class="sidebar">
            <!-- Sidebar user panel -->
            <div class="user-panel">
                <div class="pull-left image">
                    <img src="img/logo.svg" class="img-responsive" alt="Pi-hole logo" style="display: table; table-layout: fixed; height: 67px;" />
                </div>
                <div class="pull-left info">
                    <p>Status</p>
                        <a id="status"><i class="fa fa-circle" style="color:#7FFF00"></i> Active</a>                    <br/>
                    <a><i class="fa fa-circle" style="color:#7FFF00" title="Detected 1 cores"></i> Load:&nbsp;&nbsp;0&nbsp;&nbsp;0.01&nbsp;&nbsp;0.05</a>                    <br/>
                    <a><i class="fa fa-circle" style="color:#7FFF00"></i> Memory usage:&nbsp;&nbsp;38.7&thinsp;%</a>                </div>
            </div>
            <!-- sidebar menu: : style can be found in sidebar.less -->
                        <ul class="sidebar-menu">
                <li class="header">MAIN NAVIGATION</li>
                <!-- Home Page -->
                <li class="active">
                    <a href="index.php">
                        <i class="fa fa-home"></i> <span>Dashboard</span>
                    </a>
                </li>
                                <!-- Login -->
                                <li>
                    <a href="index.php?login">
                        <i class="fa fa-user"></i> <span>Login</span>
                    </a>
                </li>
                                <!-- Donate -->
                <li>
                    <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3J2L3Z4DHW9UY" target="_blank">
                        <i class="fa fa-paypal"></i> <span>Donate</span>
                    </a>
                </li>
                            </ul>
        </section>
        <!-- /.sidebar -->
    </aside>
    <!-- Content Wrapper. Contains page content -->
    <div class="content-wrapper">
        <!-- Main content -->
        <section class="content">
<!-- Small boxes (Stat box) -->
<div class="row">
    <div class="col-lg-3 col-xs-12">
        <!-- small box -->
        <div class="small-box bg-aqua">
            <div class="inner">
                <h3 class="statistic" id="ads_blocked_today">---</h3>
                <p>Queries Blocked Last 24 Hours</p>
            </div>
            <div class="icon">
                <i class="ion ion-android-hand"></i>
            </div>
        </div>
    </div>
    <!-- ./col -->
    <div class="col-lg-3 col-xs-12">
        <!-- small box -->
        <div class="small-box bg-green">
            <div class="inner">
                <h3 class="statistic" id="dns_queries_today">---</h3>
                <p>Queries Last 24 Hours</p>
            </div>
            <div class="icon">
                <i class="ion ion-earth"></i>
            </div>
        </div>
    </div>
    <!-- ./col -->
    <div class="col-lg-3 col-xs-12">
        <!-- small box -->
        <div class="small-box bg-yellow">
            <div class="inner">
                <h3 class="statistic" id="ads_percentage_today">---</h3>
                <p>Queries Blocked Last 24 Hours</p>
            </div>
            <div class="icon">
                <i class="ion ion-pie-graph"></i>
            </div>
        </div>
    </div>
    <!-- ./col -->
    <div class="col-lg-3 col-xs-12">
        <!-- small box -->
        <div class="small-box bg-red">
            <div class="inner">
                <h3 class="statistic" id="domains_being_blocked">---</h3>
                <p>Domains on Blocklists</p>
            </div>
            <div class="icon">
                <i class="ion ion-ios-list"></i>
            </div>
        </div>
    </div>
    <!-- ./col -->
</div>

<div class="row">
    <div class="col-md-12">
    <div class="box" id="queries-over-time">
        <div class="box-header with-border">
          <h3 class="box-title">Queries over last 24 hours</h3>
        </div>
        <div class="box-body">
          <div class="chart">
            <canvas id="queryOverTimeChart" width="800" height="250"></canvas>
          </div>
        </div>
        <div class="overlay">
          <i class="fa fa-refresh fa-spin"></i>
        </div>
        <!-- /.box-body -->
      </div>
    </div>
</div>

        </section>
        <!-- /.content -->
    </div>
    <!-- Modal for custom disable time -->
    <div class="modal fade" id="customDisableModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title" id="myModalLabel">Custom disable timeout</h4>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-sm-3"><input id="customTimeout" class="form-control" type="number" value="60"></div>
                        <div class="col-sm-9">
                            <div class="btn-group" data-toggle="buttons">
                                <label class="btn btn-default">
                                    <input type="radio"/> Secs
                                </label>
                                <label id="btnMins" class="btn btn-default active">
                                    <input type="radio"  /> Mins
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                    <button  id="pihole-disable-custom" type="button" class="btn btn-primary" data-dismiss="modal">Submit</button>
                </div>
            </div>
        </div>
    </div>
    <!-- /.content-wrapper -->
    <footer class="main-footer">
	<!-- Version Infos -->
        <div class="pull-right hidden-xs hidden-sm">
            <b>Pi-hole Version </b> v3.1.4            <b>Web Interface Version </b>v3.1            <b>FTL Version </b> v2.10        </div>
        <div style="display: inline-block"><a href="https://github.com/pi-hole" target="_blank"><i class="fa fa-github"></i></a> <strong><a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&amp;hosted_button_id=3J2L3Z4DHW9UY" target="_blank">Donate</a></strong> if you found this useful.</div>
    </footer>
</div>
<!-- ./wrapper -->
<script src="scripts/vendor/jquery.min.js"></script>
<script src="scripts/vendor/jquery-ui.min.js"></script>
<script src="style/vendor/bootstrap/js/bootstrap.min.js"></script>
<script src="scripts/vendor/app.min.js"></script>

<script src="scripts/vendor/jquery.dataTables.min.js"></script>
<script src="scripts/vendor/dataTables.bootstrap.min.js"></script>
<script src="scripts/vendor/Chart.bundle.min.js"></script>

<script src="scripts/pi-hole/js/footer.js"></script>

</body>
</html>

<script src="scripts/pi-hole/js/index.js"></script>
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Mirai | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Scan every TCP port. IoT hosts often expose several product-specific services outside the usual web and SSH pair.
- A 404 can still be a successful fingerprint when headers identify the product.
- Old application versions should trigger a controlled default-credential check before blind brute force or exploit hunting.
- Validate a recovered account against one appropriate service, then move to local enumeration.
- `sudo -n -l` is a high-value check. `NOPASSWD: ALL` ends the escalation search.
- Mounted removable media is evidence. Record ownership, mount mode, and metadata before deciding whether content review is authorised.
- Keep passwords, flags, and private completion artifacts out of shared notes and screenshots.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- source-first enumeration and careful credential handling after a web finding.
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- credential discovery, service validation, and evidence handling after a foothold.
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- version fingerprinting followed by a direct sudo privilege path.
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]] -- local enumeration and clean-down discipline after root access.

## External resources

- [Pi-hole documentation](https://docs.pi-hole.net/)
- [GTFOBins sudo](https://gtfobins.github.io/#+sudo)
- [HackTricks Linux privilege escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Mirai rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
