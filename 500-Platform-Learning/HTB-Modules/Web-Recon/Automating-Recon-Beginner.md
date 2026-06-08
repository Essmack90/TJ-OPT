---
tags: [module/web-recon, automation, finalrecon, recon-ng, theharvester, spiderfoot, osint, level/beginner]
---

# Automating Recon - Beginner's Guide

## Why Automate Reconnaissance?

Manual recon works, but automation makes it faster, broader, and more consistent.

| Why | What It Gives You |
|-----|-------------------|
| Efficiency | Machines work faster than humans |
| Scalability | Scan hundreds of targets at once |
| Consistency | Same process every time |
| Comprehensive | Never forget a step |
| Integration | Tools can talk to each other |

**The Rule:** Automate the boring stuff so you can focus on the interesting stuff.

---

## What Can You Automate?

| Task | Tools |
|------|-------|
| DNS enumeration | dnsenum, dnsrecon |
| Subdomain discovery | subfinder, amass |
| Web crawling | katana, gospider |
| Port scanning | nmap, masscan |
| Technology detection | whatweb, wappalyzer |
| Directory brute force | gobuster, ffuf |
| OSINT gathering | theHarvester, recon-ng |

---

## Reconnaissance Frameworks

Frameworks combine multiple tools into one workflow.

| Framework | Description | Best For |
|-----------|-------------|----------|
| FinalRecon | Python-based, modular | All-in-one web recon |
| Recon-ng | Professional framework | Modular OSINT |
| theHarvester | Email/subdomain discovery | OSINT gathering |
| SpiderFoot | Automated OSINT | Comprehensive intel |
| OSINT Framework | Collection of tools | Reference |

---

## FinalRecon - All-in-One Web Recon

FinalRecon is a Python-based reconnaissance tool that combines multiple modules into one.

### Installing FinalRecon

git clone https://github.com/thewhiteh4t/FinalRecon.git
cd FinalRecon
pip3 install -r requirements.txt
chmod +x ./finalrecon.py

### Checking Help

./finalrecon.py --help

Output shows all available modules.

### Basic Syntax

./finalrecon.py --url http://target.com [options]

---

## FinalRecon Modules

| Option | What It Does |
|--------|--------------|
| --headers | Get HTTP headers |
| --sslinfo | SSL certificate info |
| --whois | Whois lookup |
| --crawl | Crawl the website |
| --dns | DNS enumeration |
| --sub | Subdomain enumeration |
| --dir | Directory brute force |
| --wayback | Wayback Machine URLs |
| --ps | Fast port scan |
| --full | Run everything |

---

## Example: Headers + Whois

./finalrecon.py --headers --whois --url http://inlanefreight.com

Output:

 ______  __   __   __   ______   __
/\  ___\/\ \ /\ "-.\ \ /\  __ \ /\ \
\ \  __\\ \ \\ \ \-.  \\ \  __ \\ \ \____
 \ \_\   \ \_\\ \_\\"\_\\ \_\ \_\\ \_____\
  \/_/    \/_/ \/_/ \/_/ \/_/\/_/ \/_____/
 ______   ______   ______   ______   __   __
/\  == \ /\  ___\ /\  ___\ /\  __ \ /\ "-.\ \
\ \  __< \ \  __\ \ \ \____\ \ \/\ \\ \ \-.  \
 \ \_\ \_\\ \_____\\ \_____\\ \_____\\ \_\\"\_\
  \/_/ /_/ \/_____/ \/_____/ \/_____/ \/_/ \/_/

[>] Created By   : thewhiteh4t
[>] Version      : 1.1.6

[+] Target : http://inlanefreight.com

[+] IP Address : 134.209.24.248

[!] Headers :

Date : Tue, 11 Jun 2024 10:08:00 GMT
Server : Apache/2.4.41 (Ubuntu)
Link : <https://www.inlanefreight.com/index.php/wp-json/>; rel="https://api.w.org/"
Content-Type : text/html; charset=UTF-8

[!] Whois Lookup :

   Domain Name: INLANEFREIGHT.COM
   Creation Date: 2019-08-05T22:43:09Z
   Registry Expiry Date: 2024-08-05T22:43:09Z
   Registrar: Amazon Registrar, Inc.
   Name Server: NS-1303.AWSDNS-34.ORG
   Name Server: NS-1580.AWSDNS-05.CO.UK

[+] Completed in 0:00:00.257780

---

## What FinalRecon Revealed

| Module | Information Found |
|--------|-------------------|
| Headers | Apache/2.4.41 (Ubuntu), WordPress |
| Whois | Amazon Registrar, AWS name servers |
| IP | 134.209.24.248 |

All from two simple flags.

---

## Other Reconnaissance Tools

### theHarvester - Email Discovery

git clone https://github.com/laramies/theHarvester.git
cd theHarvester
python3 -m pip install -r requirements/base.txt

Basic usage:
python3 theHarvester.py -d target.com -b google

### Recon-ng - Professional Framework

Install:
git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng
pip3 install -r REQUIREMENTS

Run:
./recon-ng

### SpiderFoot - Automated OSINT

docker pull spiderfoot
docker run -p 5001:5001 spiderfoot

Then visit http://localhost:5001

---

## Key Takeaways

- Automation makes recon faster and more consistent
- FinalRecon combines multiple modules in one tool
- Always check headers, whois, and SSL info first
- theHarvester finds emails from public sources
- Recon-ng is a professional-grade framework
- SpiderFoot automates OSINT collection
- Start with simple modules, then add complexity
- Automation doesn't replace understanding
- Always verify automated findings manually
- Document everything
- Build your own automation workflows
