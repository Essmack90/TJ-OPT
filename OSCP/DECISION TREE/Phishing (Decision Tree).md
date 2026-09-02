# Phishing, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for building and delivering a credential-phishing campaign.

---

### Need to clone a target's login page, and it looks broken/static once served locally
→ `wget` only grabs raw HTML/JS, it doesn't execute anything, this breaks on any page whose interactive elements (or CSRF protection) depend on JavaScript actually running
→ Switch to SingleFile CLI instead, it drives real headless Chromium and captures the fully-rendered page
→ See [[11. Phishing Basics#11.3.2. Cloning a Legitimate Website|11.3.2]] and [[Phishing (Breakdowns)#Why wget alone can't clone a modern login page|Command Breakdowns]]

### A Python script that's supposed to modify a cloned page's HTML runs clean ("Done") but nothing actually changed
→ If the script uses raw string-replace (`html.replace('id="foo"'...)`) and the target HTML's actual attribute quoting/order doesn't match exactly what the script expects, `.replace()` silently does nothing, no error, script "succeeds," nothing happens
→ Check what's actually in the file first: `grep -o 'id="foo"' file.html` vs `grep -o 'id=foo' file.html` (quoted vs unquoted)
→ Fix: use BeautifulSoup's `.find(id=...)` + attribute assignment instead of string-replace, it parses the HTML properly so quoting/order don't matter
→ See [[11. Phishing Basics#11.3.3. Cleaning Up the Clone|11.3.3]] and [[Phishing (Breakdowns)#BeautifulSoup's attribute API vs. raw string-replace for patching a clone|Command Breakdowns]]

### A cloned phishing page's login/credential-capture works when you test it yourself, but never fires once a real target on another machine tries it
→ Check for hardcoded `127.0.0.1` anywhere in the payload (form `action`, JS fetch URLs, etc). `127.0.0.1` always means "this same machine," so a victim's browser resolves it to *their* machine, not yours
→ Replace with your actual routable IP (VPN/`tun0` address), `grep` first to confirm exactly what you're about to change before blind-replacing
→ Same root-cause family as the `python3 -m http.server` wrong-directory gotcha and `curl --data` vs `--data-urlencode`, "works on localhost, breaks for real" is a recurring class of bug
→ See [[11. Phishing Basics#11.3.5. Crafting the Phishing Email|11.3.5]] and [[Phishing (Breakdowns)#Why 127.0.0.1 breaks once a real victim machine is involved|Command Breakdowns]]

### Need a pretext that will actually pass a target's scrutiny
→ Find something the target organization already sends routinely (check a compromised mailbox's Sent folder for a real example if you have one), then have an LLM rewrite/extend it in the same voice rather than writing from scratch
→ Keep sender domain, writing tone, and any linked page's look-and-feel all consistent, mismatches between any of these are what break trust
→ See [[11. Phishing Basics#11.1.1. Email Phishing|11.1.1]] and [[11. Phishing Basics#11.3.1. Creating a Zoom Credential Phishing Pretext|11.3.1]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/06. Information Gathering]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
