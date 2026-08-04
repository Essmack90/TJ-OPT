# Web Applications — Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for XSS, command injection, vhost pivots, WordPress, and APIs. (SQL injection has its own area: [[SQL Injection & Databases (Decision Tree)]]. Traversal/LFI/RFI: [[File Inclusion & Traversal (Decision Tree)]]. Upload forms: [[File Upload Attacks (Decision Tree)]].)

---

### Found an input field that reflects your input back into the page
→ Test with `< > ' " { } ;` and see what survives unencoded
→ See [[Introduction to Web Application Attacks#8.4.3. Identifying XSS Vulnerabilities|8.4.3]]
→ Got a hit? Basic PoC and privesc-via-XSS walkthrough: [[Introduction to Web Application Attacks#8.4.4. Basic XSS|8.4.4]] and [[Introduction to Web Application Attacks#8.4.5. Privilege Escalation via XSS|8.4.5]]

### Found a form/field whose value looks like an OS command (a URL for `git clone`, a filename passed to some system tool, etc)
→ Try replacing the value entirely with a harmless command (`id`, `ipconfig`). Filtered? Confirm the expected command alone still works, then chain a second one with a URL-encoded `;` (`%3B`), `&&`, or (CMD) `&`
→ `git version` (or equivalent) output tells you Windows vs Linux in one shot
→ On Windows, use PetSerAl's one-liner to check CMD vs PowerShell before picking a reverse shell syntax
→ See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]]

### Found a field with no obvious command hint (no `git clone`-style placeholder), but it feels off
→ Work through injection types systematically rather than guessing: try arithmetic (`1%2B1`, is it evaluated to `2`?), then template syntax (`{{7*7}}`, is it `49`?), then shell metacharacters (backticks, `$()`). Watch for **any change in behavior**, not just a direct hit, a response going blank instead of echoing your literal input is itself a signal something's being evaluated
→ See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 case study 3]] for the full walkthrough of this exact reasoning process

### A character in your payload disappears from the reflected response entirely (not HTML-escaped, just gone)
→ That's active filtering of that specific character, not passive echoing. Common culprit: `"` stripped while `'` survives. Switch quote style in your payload rather than assuming the whole injection point is dead

### A site's own content mentions another hostname/domain you haven't scanned yet
→ Classic vhost pivot: the real vulnerable app often lives on a name-based virtual host the landing page just happens to link to or mention in its text. Add it to `/etc/hosts` pointing at the same IP and check it directly
```bash
echo "<target-ip> <other-hostname>" | sudo tee -a /etc/hosts
curl http://<other-hostname>/
```
→ See [[SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Alvida Coffee's landing page linking to `alvida-eatery.local`, the actual WordPress target)

### Found a WordPress site and need to find the actual vulnerability
→ Fingerprint every installed plugin's version via its `readme.txt` (`curl http://<target>/wp-content/plugins/<name>/readme.txt`, no auth needed), then `searchsploit <plugin name>` for each one until something matches
→ Unauthenticated SQLi in a plugin usually routes through the shared `wp-admin/admin-ajax.php?action=<name>` endpoint regardless of login state
→ See [[Web Applications#WordPress|Command Appendix's WordPress section]] and [[SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Perfect Survey plugin, CVE-2021-24762)

### Got WordPress admin creds, but Appearance/Plugin Editor says "Unable to communicate back with site... PHP change was reverted"
→ That's WP's built-in fatal-error-protection: it saves your edit, then does a loopback HTTP request to itself to check for a fatal error before committing. On isolated lab networks the server often can't loop back to its own hostname, so the check always fails and the edit gets silently reverted
→ Go around it with plugin upload instead (**Plugins → Add New → Upload Plugin**), which has no such live-check at upload time. A single-file plugin with just a `Plugin Name:` header comment and your payload code is enough
→ See [[Web Applications#WordPress|Command Appendix's WordPress section]] for the exact zip/upload steps

### Found a REST API (or suspect one)
→ Brute force versioned paths (`gobuster` with a `{GOBUSTER}/v1` pattern file)
→ Probe with `curl`, watch for `405` vs `404` (405 means the path exists, wrong HTTP method)
→ Check for mass assignment (extra fields like `"admin":"True"` in a register/create request)
→ See [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]]
