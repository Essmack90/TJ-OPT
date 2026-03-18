---
tags: [module/web-recon, fingerprinting, wappalyzer, whatweb, nikto, wafw00f, level/beginner]
---

# Fingerprinting - Beginner's Guide

## What is Fingerprinting?

Fingerprinting is the process of identifying the technologies powering a website or web application. Just like a human fingerprint uniquely identifies a person, the digital signatures of web servers, operating systems, and software components reveal critical information about a target.

Think of it as figuring out what a building is made of before you try to break in.

---

## Why Fingerprinting Matters

| Why | What It Tells You |
|-----|-------------------|
| Targeted attacks | Focus on exploits that actually work |
| Misconfigurations | Outdated software, default settings |
| Prioritization | Which targets are most vulnerable |
| Building a profile | Complete picture of the technology stack |

**The Rule:** You can't exploit what you don't understand.

---

## What Fingerprinting Reveals

| Information | Example |
|-------------|---------|
| Web Server | Apache, Nginx, IIS |
| Version | Apache 2.4.41, Nginx 1.18.0 |
| Operating System | Ubuntu, CentOS, Windows Server |
| CMS | WordPress, Joomla, Drupal |
| Programming Language | PHP, Python, Ruby, ASP.NET |
| Frameworks | Laravel, Django, Rails |
| JavaScript Libraries | jQuery, React, Vue |
| Analytics | Google Analytics, Matomo |
| Hosting Provider | AWS, DigitalOcean, On-premise |
| WAF | Cloudflare, Wordfence, ModSecurity |

---

## Fingerprinting Techniques

### 1. Banner Grabbing

Servers often announce themselves in banners.

```bash
# Get HTTP headers only
curl -I http://example.com
Example Output
bash
HTTP/1.1 200 OK
Server: Apache/2.4.41 (Ubuntu)
X-Powered-By: PHP/7.4.3
This immediately tells us:
- Web Server: Apache 2.4.41
- OS: Ubuntu
- Backend Language: PHP 7.4.3
2. Analysing HTTP Headers
Headers contain valuable clues:
Header	What It Reveals
Server	Web server software
X-Powered-By	Scripting language/framework
X-AspNet-Version	ASP.NET version
Set-Cookie	Session cookie names (PHPSESSID = PHP)
Link	WordPress often reveals itself
3. Probing for Specific Responses
Sending special requests can trigger unique responses:
- 404 error pages differ between servers
- Certain paths reveal CMS (wp-admin, admin, etc.)
- File extensions reveal technologies (.php, .asp, .aspx)
4. Analysing Page Content
Look at the HTML source:
- Meta tags
- Comments
- JavaScript includes
- CSS includes
- Copyright notices
Popular Fingerprinting Tools
Tool	Description	Best For
Wappalyzer	Browser extension	Quick, visual identification
BuiltWith	Web service	Detailed technology reports
WhatWeb	Command-line	Automated scanning
Nikto	Web server scanner	Vulnerability + fingerprinting
wafw00f	WAF detection	Identifying firewalls
Netcraft	Web service	Complete profiling
Banner Grabbing with curl
Basic Header Fetch
bash
curl -I https://inlanefreight.com
Output:
HTTP/1.1 200 OK
Date: Fri, 31 May 2024 12:12:26 GMT
Server: Apache/2.4.41 (Ubuntu)
Link: <https://www.inlanefreight.com/index.php/wp-json/>; rel="https://api.w.org/"
Content-Type: text/html; charset=UTF-8
What We Learned
Finding	Meaning
Apache/2.4.41	Web server and version
Ubuntu	Operating system
wp-json	WordPress API endpoint
WordPress Detection
The `wp-` prefix is a dead giveaway for WordPress.

Following Redirects
bash
# First request
curl -I inlanefreight.com
HTTP/1.1 301 Moved Permanently
Server: Apache/2.4.41 (Ubuntu)
Location: https://inlanefreight.com/

# Second request
curl -I https://inlanefreight.com
HTTP/1.1 301 Moved Permanently
Server: Apache/2.4.41 (Ubuntu)
X-Redirect-By: WordPress
Location: https://www.inlanefreight.com/

# Third request
curl -I https://www.inlanefreight.com
HTTP/1.1 200 OK
Server: Apache/2.4.41 (Ubuntu)
Link: <https://www.inlanefreight.com/index.php/wp-json/>; rel="https://api.w.org/"
Each redirect reveals more information until we finally see WordPress.

WAF Detection with wafw00f
What is a WAF?
A Web Application Firewall (WAF) protects websites from attacks. It can block our probes, so we need to know if one exists.

Installing wafw00f
bash
pip3 install git+https://github.com/EnableSecurity/wafw00f
Using wafw00f
bash
wafw00f inlanefreight.com
Output:
[*] Checking https://inlanefreight.com
[+] The site https://inlanefreight.com is behind Wordfence (Defiant) WAF.
This tells us the site is protected by Wordfence WAF - important to know for future testing.

Nikto Web Server Scanner
Nikto is a powerful scanner that identifies outdated software and misconfigurations.

Installing Nikto
bash
sudo apt update && sudo apt install -y perl
git clone https://github.com/sullo/nikto
cd nikto/program
chmod +x ./nikto.pl
Basic Nikto Fingerprint Scan
bash
nikto -h inlanefreight.com -Tuning b
The `-Tuning b` flag tells Nikto to run ONLY software identification modules.

Nikto Output Example
- Nikto v2.5.0
---------------------------------------------------------------------------
+ Target IP:          134.209.24.248
+ Target Hostname:    www.inlanefreight.com
---------------------------------------------------------------------------
+ Server: Apache/2.4.41 (Ubuntu)
+ /: The X-Content-Type-Options header is not set.
+ /index.php?: Uncommon header 'x-redirect-by' found, with contents: WordPress.
+ /license.txt: License file found may identify site software.
+ /: A Wordpress installation was found.
+ /wp-login.php: Wordpress login found.
Key Findings
Finding	Meaning
Apache/2.4.41 (Ubuntu)	Web server and OS
x-redirect-by: WordPress	WordPress confirmed
/wp-login.php	WordPress login page exposed
license.txt	May reveal software version
Key Takeaways
Fingerprinting identifies the technologies powering a website

Banner grabbing with curl is the simplest technique

HTTP headers reveal server software, versions, and frameworks

WordPress sites often expose themselves (wp- paths, headers)

wafw00f detects Web Application Firewalls

Nikto combines fingerprinting with vulnerability checking

Always check for WAFs before deeper scanning

Follow redirects - they often reveal more information

Combine multiple tools for complete picture

Document everything - build a technology profile
