---
tags: [module, nmap, nse, scripting, advanced, practical]
module: "Nmap Scripting Engine (NSE)"
level: advanced
---

# Nmap Scripting Engine - Complete Reference #nse #scripting #advanced

## NSE Script Categories Deep Dive #categories

| Category | Description | Risk Level | Common Scripts |
|----------|-------------|------------|----------------|
| auth | Authentication credential testing | Safe | http-basic-auth, smb-enum-users |
| broadcast | Host discovery via broadcasting | Safe | broadcast-dhcp-discover, broadcast-ping |
| brute | Brute-force login attempts | Intrusive | http-brute, mysql-brute, smb-brute |
| default | Default scripts (-sC) | Safe | 40+ common safe scripts |
| discovery | Service and host discovery | Safe | dns-srv-enum, smb-enum-shares |
| dos | Denial of Service testing | Dangerous | http-slowloris, smb-flood |
| exploit | Exploit known vulnerabilities | Dangerous | smb-vuln-ms17-010, http-vuln-* |
| external | Use external services | Safe | whois, dns-blacklist |
| fuzzer | Send malformed data | Intrusive | dns-fuzz, http-fuzz |
| intrusive | May affect target | Intrusive | All potentially disruptive |
| malware | Check for infections | Safe | http-malware-host, smtp-strangeport |
| safe | Won't harm target | Safe | All informational only |
| version | Extended version detection | Safe | banner, skypev2-version |
| vuln | Vulnerability detection | Safe | Numerous vulnerability checks |

---

## Script Selection Syntax #syntax

| Pattern | Example | Description |
|---------|---------|-------------|
| --script category | --script vuln | Run all scripts in category |
| --script "category1 or category2" | --script "discovery or safe" | Run scripts from either category |
| --script script1,script2 | --script http-enum,http-title | Run specific scripts |
| --script "not intrusive" | --script "not intrusive" | Exclude intrusive scripts |
| --script "default or safe" | --script "default or safe" | Run default and safe scripts |
| --script-args | --script-args http-useragent=Mozilla | Pass arguments to scripts |

---

## Advanced Script Usage Examples #examples

### Example 1: Comprehensive SMTP Enumeration

sudo nmap 10.129.2.28 -p 25 --script banner,smtp-commands,smtp-enum-users,smtp-vuln-* --script-args smtp-enum-users.methods={VRFY}

PORT   STATE SERVICE
25/tcp open  smtp
|_banner: 220 inlane ESMTP Postfix (Ubuntu)
|_smtp-commands: inlane, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8,
| smtp-enum-users: VRFY method found, attempting to enumerate users
|   RCPT method not supported
|   root: valid
|   admin: valid
|   test: valid
|_  info: valid

**What we learned:** VRFY command works, valid users identified!

### Example 2: WordPress Vulnerability Assessment

sudo nmap 10.129.2.28 -p 80,443 -sV --script http-wordpress-* --script-args http-wordpress-enum.search-limit=100

PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.29
| http-wordpress-enum:
|   Search limited to 100
|   admin found
|   editor found
|   author found
|_  contributor found
| http-wordpress-users:
|   Username found: admin
|   Username found: editor
|_  Username found: author
| http-wordpress-brute:
|   Accounts:
|     admin:password123 - Valid credentials
|_  Statistics: Performed 100 guesses in 10 seconds

**Critical finding:** Weak credentials discovered!

### Example 3: SMB Vulnerability Scanning

sudo nmap 10.129.2.28 -p 445 --script smb-vuln-* --script-args unsafe=1

PORT    STATE SERVICE
445/tcp open  microsoft-ds

Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (MS17-010)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|     Risk factor: HIGH
|       A critical remote code execution vulnerability exists in Microsoft SMBv1
|        servers (ms17-010).
|_          https://technet.microsoft.com/en-us/library/security/ms17-010.aspx

**Critical finding:** EternalBlue vulnerability present!

---

## Script Arguments #arguments

Many scripts accept arguments to customize behavior.

### Syntax

--script-args <arg1>=<value1>,<arg2>=<value2>

### Common Script Arguments

| Script | Arguments | Purpose |
|--------|-----------|---------|
| http-enum | http-enum.fingerprintfile | Custom fingerprint file |
| http-wordpress-enum | http-wordpress-enum.search-limit | Max users to find |
| smb-enum-shares | smb-enum-shares.maxdepth | Recursion depth |
| dns-brute | dns-brute.domain | Domain to brute force |
| http-brute | http-brute.path, http-brute.threads | Target path, thread count |

### Example with Multiple Arguments

sudo nmap 10.129.2.28 -p 80 --script http-brute --script-args http-brute.path=/wp-login.php,http-brute.threads=5,userdb=/usr/share/wordlists/users.txt,passdb=/usr/share/wordlists/rockyou.txt

---

## Script Updates and Management #updates

### Update Script Database

sudo nmap --script-updatedb

This updates the script database and downloads new scripts.

### Script Locations

| Location | Purpose |
|----------|---------|
| /usr/share/nmap/scripts/ | System scripts |
| ~/.nmap/scripts/ | User scripts |
| --script /path/to/script.nse | Custom script path |

### Install Custom Scripts

wget https://raw.githubusercontent.com/cldrn/nmap-nse-scripts/master/scripts/http-vuln-cve2021-12345.nse
sudo cp http-vuln-cve2021-12345.nse /usr/share/nmap/scripts/
sudo nmap --script-updatedb

---

## Writing Custom NSE Scripts #scripting

### Basic Script Template

description = [[
Brief description of what the script does
]]

author = "Your Name"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = {"discovery", "safe"}

portrule = function(host, port)
    return port.protocol == "tcp" and port.number == 80
end

action = function(host, port)
    local socket = nmap.new_socket()
    local status = socket:connect(host, port)
    -- Add your logic here
    socket:close()
    return "Script executed successfully"
end

### Script Components

| Component | Purpose |
|-----------|---------|
| description | What the script does |
| author | Script creator |
| license | Distribution terms |
| categories | Which categories it belongs to |
| portrule | When to run (port condition) |
| hostrule | When to run (host condition) |
| action | Main script logic |

---

## Performance Optimization #performance

### Script Timing Control

| Option | Effect |
|--------|--------|
| --script-trace | Show script execution details |
| --script-updatedb | Update script database |
| --script-args-timeout | Timeout for script arguments |
| --host-timeout | Max time per host |

### Parallel Script Execution

sudo nmap --min-hostgroup 64 --max-hostgroup 64 -p 80 --script http-* target.com

### Focused Script Scanning

Instead of running all scripts in a category, target specific ones:

sudo nmap -p 445 --script smb-vuln-ms17-010,smb-vuln-cve-2017-7494 target.com

---

## Integration with Other Tools #integration

### Export Results for Metasploit

sudo nmap -sV -oX scan.xml target.com
msfconsole
db_import scan.xml
hosts
services

### Export for Searchsploit

grep "Service Version" scan.xml | while read line; do
    searchsploit "$line"
done

### Generate HTML Report

sudo nmap -sV --script vuln -oX vuln-scan.xml target.com
xsltproc vuln-scan.xml -o vuln-report.html

---

## NSE Script Categories Quick Reference #cheatsheet

| Need | Category | Example Scripts |
|------|----------|-----------------|
| Find users | auth, brute | smb-enum-users, http-enum |
| Map network | broadcast | broadcast-ping, broadcast-dhcp |
| Find vulns | vuln, exploit | smb-vuln-*, http-vuln-* |
| Get versions | version, default | banner, http-title |
| Discover services | discovery | smb-enum-shares, dns-srv-enum |
| Test passwords | brute | http-brute, mysql-brute |
| Check malware | malware | http-malware-host |
| Full audit | -A or default | Aggressive scan |

---

## Practical Workflow Examples #workflow

### Workflow 1: Initial Discovery

sudo nmap -sS -p- -T4 target.com -oA discovery
sudo nmap -sV -p $(grep open discovery.gnmap | cut -d' ' -f2 | cut -d'/' -f1 | tr '\n' ',') --script default,safe target.com -oA service-enum

### Workflow 2: Vulnerability Assessment

sudo nmap -sV --script vuln --script-args unsafe=1 target.com -oA vuln-scan

### Workflow 3: Targeted Exploit Check

sudo nmap -p 445 --script smb-vuln-* --script-args unsafe=1 target.com

### Workflow 4: Web Application Deep Dive

sudo nmap -p 80,443 -sV --script http-* --script-args http-enum.fingerprintfile=/usr/share/nmap/nselib/data/http-fingerprints.lst target.com

---

## Alternative Tools #alternatives

| Tool | Purpose | When to Use |
|------|---------|-------------|
| [[nikto]] | Web vulnerability scanner | Web server focus |
| [[wpscan]] | WordPress specific | WordPress targets |
| [[gobuster]] | Directory enumeration | Web content discovery |
| [[searchsploit]] | Exploit searching | After version detection |
| [[metasploit]] | Exploitation | After vulnerability identification |

---

## Key Takeaways #keypoints

- NSE has 14 categories covering all testing phases
- Use --script category for broad coverage
- Use specific script names for targeted testing
- The vuln category automatically checks vulnerability databases
- Script arguments customize behavior for your needs
- -A combines multiple scans for efficiency
- Always understand script safety before running
- Update scripts regularly with --script-updatedb
- Combine NSE with other tools for complete assessments
- Over 600 scripts are available - you don't need to memorize them all
- The official documentation at https://nmap.org/nsedoc/index.html lists every script and its usage
- Export results to other tools (Metasploit, searchsploit) for deeper analysis
