---
tags: [module, nmap, nse, scripting, beginner]
module: "Nmap Scripting Engine (NSE)"
level: beginner
---

# Nmap Scripting Engine (NSE) - Beginner's Guide #nse #scripting #beginner

## What is NSE? #core

The Nmap Scripting Engine (NSE) is one of Nmap's most powerful features. It allows us to write and run scripts (in the Lua programming language) that automate interactions with network services.

Think of NSE scripts as **automated tools** that can:
- Test for vulnerabilities
- Grab banners
- Enumerate users
- Brute-force credentials
- Discover hidden information
- And much more

There are over 600 scripts available, covering virtually every common service.

---

## NSE Script Categories #categories

NSE scripts are organized into 14 categories. Each category serves a different purpose.

| Category | Description | Example Use |
|----------|-------------|-------------|
| auth | Authentication credential testing | Check for default passwords |
| broadcast | Host discovery via broadcasting | Find hosts on local network |
| brute | Brute-force login attempts | Try common passwords |
| default | Default scripts (-sC) | Basic safe enumeration |
| discovery | Service and host discovery | Find additional information |
| dos | Denial of Service testing | Check for DoS vulnerabilities (use carefully!) |
| exploit | Exploit known vulnerabilities | Attempt to gain access |
| external | Use external services | Query DNS, whois, etc. |
| fuzzer | Send malformed data | Find bugs (can be slow) |
| intrusive | May affect target | Could crash services |
| malware | Check for infections | Detect known malware |
| safe | Won't harm target | Information gathering only |
| version | Extended version detection | Identify service versions |
| vuln | Vulnerability detection | Check for known CVEs |

### Important Note on Script Safety

- **safe scripts** are designed to never harm the target
- **intrusive scripts** could potentially crash services
- **dos scripts** are intentionally disruptive - use only in lab environments
- Always understand what a script does before running it

---

## How to Use NSE Scripts #usage

### Method 1: Default Scripts (-sC)

The easiest way to start is with the default scripts. These are a collection of safe, commonly useful scripts.

sudo nmap 10.129.2.28 -sC

This is equivalent to:
sudo nmap 10.129.2.28 --script default

### Method 2: Script Category

Run all scripts in a specific category:

sudo nmap 10.129.2.28 --script vuln
sudo nmap 10.129.2.28 --script discovery
sudo nmap 10.129.2.28 --script safe

### Method 3: Specific Script Names

Run one or more specific scripts by name:

sudo nmap 10.129.2.28 -p 25 --script banner,smtp-commands

### Method 4: Aggressive Scan (-A)

The -A option combines multiple scans:
- Service detection (-sV)
- OS detection (-O)
- Traceroute (--traceroute)
- Default NSE scripts (-sC)

sudo nmap 10.129.2.28 -p 80 -A

---

## Example 1: SMTP Scripts #example

Let's target the SMTP server on port 25 with two specific scripts:

sudo nmap 10.129.2.28 -p 25 --script banner,smtp-commands

Nmap scan report for 10.129.2.28
PORT   STATE SERVICE
25/tcp open  smtp
|_banner: 220 inlane ESMTP Postfix (Ubuntu)
|_smtp-commands: inlane, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8,

### What We Learned

| Script | Information Gained |
|--------|-------------------|
| banner | Ubuntu Linux confirmed |
| smtp-commands | Supported commands: VRFY, ETRN, STARTTLS, etc. |

The VRFY command is particularly interesting - it can be used to verify if usernames exist on the system!

---

## Example 2: Aggressive Web Scan #example

Now let's scan the web server on port 80 with the aggressive option:

sudo nmap 10.129.2.28 -p 80 -A

PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-generator: WordPress 5.3.4
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: blog.inlanefreight.com

Warning: OSScan results may be unreliable...
Aggressive OS guesses: Linux 2.6.32 (96%), Linux 3.2 - 4.9 (96%)

### What We Learned

- **Web Server:** Apache 2.4.29 on Ubuntu
- **Web Application:** WordPress 5.3.4
- **Site Title:** blog.inlanefreight.com
- **OS:** Linux (96% confidence)

This is a treasure trove of information from a single command!

---

## Example 3: Vulnerability Assessment with vuln Category #example

Now let's use the vuln category to check for known vulnerabilities:

sudo nmap 10.129.2.28 -p 80 -sV --script vuln

PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))

| http-enum:
|   /wp-login.php: Possible admin folder
|   /readme.html: Wordpress version: 2
|   /: WordPress version: 5.3.4
|   /wp-login.php: Wordpress login page.

| http-wordpress-users:
|   Username found: admin

| vulners:
|   cpe:/a:apache:http_server:2.4.29:
|     	CVE-2019-0211	7.2	https://vulners.com/cve/CVE-2019-0211
|     	CVE-2018-1312	6.8	https://vulners.com/cve/CVE-2018-1312
|     	CVE-2017-15715	6.8	https://vulners.com/cve/CVE-2017-15715

### Critical Findings

| Finding | Implication |
|---------|-------------|
| WordPress version 5.3.4 | May have known vulnerabilities |
| Admin user found | Potential brute-force target |
| Apache CVEs listed | Known vulnerabilities to check |

This scan automatically:
1. Enumerated the WordPress installation
2. Discovered a username (admin)
3. Checked vulnerability databases
4. Listed relevant CVEs with scores

---

## NSE Script Locations #scripts

All NSE scripts are stored locally on your system:

ls /usr/share/nmap/scripts/
ls /usr/share/nmap/scripts/ | grep http
ls /usr/share/nmap/scripts/ | grep smb

You can browse this directory to see what's available (over 600 scripts!).

### Script Help

To learn what a specific script does:

nmap --script-help http-enum
nmap --script-help smb-vuln-ms17-010

---

## Key Takeaways #keypoints

- NSE scripts automate service interaction and vulnerability detection
- 14 categories cover everything from safe discovery to active exploitation
- Use -sC for default safe scripts
- Use --script category to run all scripts in a category
- Use --script script1,script2 to run specific scripts
- The -A option combines -sV, -O, --traceroute, and -sC
- The vuln category automatically checks for known vulnerabilities
- Always understand what a script does before running intrusive ones
- Scripts are stored in /usr/share/nmap/scripts/
- Use --script-help to learn about any script
- The official documentation at https://nmap.org/nsedoc/index.html lists all 600+ scripts
