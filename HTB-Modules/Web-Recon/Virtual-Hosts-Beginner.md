---
tags: [module/web-recon, vhosts, virtual-hosts, web-servers, gobuster, level/beginner]
---

# Virtual Hosts - Beginner's Guide

## What are Virtual Hosts?

Virtual hosting allows a single web server to host multiple websites or applications. Think of it like an apartment building - one physical address (IP) but many different apartments (websites) inside.

A web server with virtual hosts can serve:
- example.com
- blog.example.com
- shop.example.com
- completely-different-site.org

All from the same server.

---

## How Virtual Hosts Work

### The Host Header

When your browser requests a website, it sends an HTTP request that includes a `Host` header:

GET / HTTP/1.1
Host: www.example.com

This header tells the web server WHICH website you want to see.

### The Server's Decision

1. Browser sends request to IP address
2. Server looks at the Host header
3. Server checks its virtual host configuration
4. Server serves the correct website content

---

## VHosts vs Subdomains

| | Subdomains | Virtual Hosts |
|------|------------|---------------|
| What they are | DNS entries (blog.example.com) | Server configurations |
| Where they live | DNS records | Web server config files |
| Can they exist without DNS? | No - need DNS to resolve | Yes - can be internal only |
| Example | mail.example.com has its own IP | Same IP serves different sites |

**Key Point:** A subdomain MUST have a DNS record. A virtual host can exist without one - you just need to know the hostname to access it.

---

## Types of Virtual Hosting

### 1. Name-Based Virtual Hosting (Most Common)

Relies on the Host header to distinguish sites.

<VirtualHost *:80>
    ServerName www.example1.com
    DocumentRoot /var/www/example1
</VirtualHost>

<VirtualHost *:80>
    ServerName www.example2.org
    DocumentRoot /var/www/example2
</VirtualHost>

**Pros:** One IP can host unlimited sites
**Cons:** Requires Host header support

### 2. IP-Based Virtual Hosting

Each site gets its own IP address.

<VirtualHost 192.168.1.10:80>
    ServerName www.example1.com
    DocumentRoot /var/www/example1
</VirtualHost>

<VirtualHost 192.168.1.11:80>
    ServerName www.example2.org
    DocumentRoot /var/www/example2
</VirtualHost>

**Pros:** Works with any protocol
**Cons:** Needs multiple IPs (expensive)

### 3. Port-Based Virtual Hosting

Different sites on different ports.

<VirtualHost *:80>
    ServerName www.example.com
    DocumentRoot /var/www/site1
</VirtualHost>

<VirtualHost *:8080>
    ServerName www.example.com
    DocumentRoot /var/www/site2
</VirtualHost>

**Pros:** One IP, multiple sites
**Cons:** Users need to specify port in URL

---

## Why VHosts Matter for Pentesters

| Why | What You Find |
|-----|---------------|
| Hidden sites | Development servers, staging environments |
| Internal applications | Admin panels, internal tools |
| Legacy systems | Old versions with vulnerabilities |
| Non-DNS hosts | Sites that don't appear in DNS records |

---

## Discovering Virtual Hosts

### Manual Method - Hosts File

If you know or suspect a hostname, you can add it to your hosts file:

/etc/hosts (Linux/Mac)
192.168.1.10    dev.internal-site.com
192.168.1.10    staging.example.com

C:\Windows\System32\drivers\etc\hosts (Windows)
192.168.1.10    dev.internal-site.com
192.168.1.10    staging.example.com

Then visit http://dev.internal-site.com in your browser.

### Automated Method - Gobuster

Gobuster is a tool that can brute-force virtual hosts by testing different Host headers.

#### Basic Gobuster VHost Command

gobuster vhost -u http://192.168.1.10 -w /path/to/wordlist.txt --append-domain

#### Command Breakdown

| Option | What It Does |
|--------|--------------|
| `vhost` | Use vhost enumeration mode |
| `-u http://IP` | Target IP address |
| `-w wordlist.txt` | Wordlist of potential hostnames |
| `--append-domain` | Append base domain to each word |

#### Example with SecLists

gobuster vhost -u http://inlanefreight.htb:81 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain

---

## Understanding Gobuster Output

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:81
[+] Method:          GET
[+] Threads:         10
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
[+] Append Domain:   true
===============================================================
Starting gobuster in VHOST enumeration mode
===============================================================
Found: forum.inlanefreight.htb:81 Status: 200 [Size: 100]
[...]
Progress: 114441 / 114442 (100.00%)
===============================================================
Finished
===============================================================

### What the Output Tells You

| Found Line | Meaning |
|------------|---------|
| forum.inlanefreight.htb | Discovered virtual host |
| Status: 200 | HTTP 200 OK - site exists |
| [Size: 100] | Response size (helps filter false positives) |

---

## Useful Gobuster Options

| Option | Description |
|--------|-------------|
| `-t 50` | Increase threads for faster scanning |
| `-k` | Ignore SSL/TLS certificate errors |
| `-o output.txt` | Save results to a file |
| `-r` | Follow redirects |
| `--user-agent "Mozilla/5.0"` | Set custom User-Agent |

---

## Key Takeaways

- Virtual hosts allow one server to host multiple websites
- The Host header tells the server which site to serve
- Subdomains need DNS, VHosts don't necessarily
- VHost discovery can reveal hidden sites and applications
- Gobuster is the go-to tool for vhost enumeration
- Always check for non-DNS hosts during recon
- Manual hosts file entries can access hidden vhosts
- Different response sizes help filter false positives
- Be careful with scan speed - it can be detected
- Document all discovered vhosts for further testing
