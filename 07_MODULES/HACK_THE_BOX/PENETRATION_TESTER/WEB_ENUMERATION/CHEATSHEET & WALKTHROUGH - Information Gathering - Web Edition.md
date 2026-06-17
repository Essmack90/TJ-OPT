# Cheat Sheet

---

Web reconnaissance is the first step in any security assessment or penetration testing engagement. It's akin to a detective's initial investigation, meticulously gathering clues and evidence about a target before formulating a plan of action. In the digital realm, this translates to accumulating information about a website or web application to identify potential vulnerabilities, security misconfigurations, and valuable assets.

The primary goals of web reconnaissance revolve around gaining a comprehensive understanding of the target's digital footprint. This includes:

- `Identifying Assets`: Discovering all associated domains, subdomains, and IP addresses provides a map of the target's online presence.
- `Uncovering Hidden Information`: Web reconnaissance aims to uncover directories, files, and technologies that are not readily apparent and could serve as entry points for an attacker.
- `Analyzing the Attack Surface`: By identifying open ports, running services, and software versions, you can assess the potential vulnerabilities and weaknesses of the target.
- `Gathering Intelligence`: Collecting information about employees, email addresses, and technologies used can aid in social engineering attacks or identifying specific vulnerabilities associated with certain software.

Web reconnaissance can be conducted using either active or passive techniques, each with its own advantages and drawbacks:

| Type                   | Description                                                  | Risk of Detection | Examples                                                     |
| ---------------------- | ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------ |
| Active Reconnaissance  | Involves directly interacting with the target system, such as sending probes or requests. | Higher            | Port scanning, vulnerability scanning, network mapping       |
| Passive Reconnaissance | Gathers information without directly interacting with the target, relying on publicly available data. | Lower             | Search engine queries, WHOIS lookups, DNS enumeration, web archive analysis, social media |

## WHOIS

WHOIS is a query and response protocol used to retrieve information about domain names, IP addresses, and other internet resources. It's essentially a directory service that details who owns a domain, when it was registered, contact information, and more. In the context of web reconnaissance, WHOIS lookups can be a valuable source of information, potentially revealing the identity of the website owner, their contact information, and other details that could be used for further investigation or social engineering attacks.

For example, if you wanted to find out who owns the domain `example.com`, you could run the following command in your terminal:

```bash
whois example.com
```

This would return a wealth of information, including the registrar, registration, and expiration dates, nameservers, and contact information for the domain owner.

However, it's important to note that WHOIS data can be inaccurate or intentionally obscured, so it's always wise to verify the information from multiple sources. Privacy services can also mask the true owner of a domain, making it more difficult to obtain accurate information through WHOIS.

## DNS

The Domain Name System (DNS) functions as the internet's GPS, translating user-friendly domain names into the numerical IP addresses computers use to communicate. Like GPS converting a destination's name into coordinates, DNS ensures your browser reaches the correct website by matching its name with its IP address. This eliminates memorizing complex numerical addresses, making web navigation seamless and efficient.

The `dig` command allows you to query DNS servers directly, retrieving specific information about domain names. For instance, if you want to find the IP address associated with `example.com`, you can execute the following command:

```bash
dig example.com A
```

This command instructs `dig` to query the DNS for the `A` record (which maps a hostname to an IPv4 address) of `example.com`. The output will typically include the requested IP address, along with additional details about the query and response. By mastering the `dig` command and understanding the various DNS record types, you gain the ability to extract valuable information about a target's infrastructure and online presence.

DNS servers store various types of records, each serving a specific purpose:

| Record Type | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| A           | Maps a hostname to an IPv4 address.                          |
| AAAA        | Maps a hostname to an IPv6 address.                          |
| CNAME       | Creates an alias for a hostname, pointing it to another hostname. |
| MX          | Specifies mail servers responsible for handling email for the domain. |
| NS          | Delegates a DNS zone to a specific authoritative name server. |
| TXT         | Stores arbitrary text information.                           |
| SOA         | Contains administrative information about a DNS zone.        |

## Subdomains

Subdomains are essentially extensions of a primary domain name, often used to organize different sections or services within a website. For example, a company might use `mail.example.com` for their email server or `blog.example.com` for their blog.

From a reconnaissance perspective, subdomains are incredibly valuable. They can expose additional attack surfaces, reveal hidden services, and provide clues about the internal structure of a target's network. Subdomains might host development servers, staging environments, or even forgotten applications that haven't been properly secured.

The process of discovering subdomains is known as subdomain enumeration. There are two main approaches to subdomain enumeration:

| Approach              | Description                                                  | Examples                                                  |
| --------------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| `Active Enumeration`  | Directly interacts with the target's DNS servers or utilizes tools to probe for subdomains. | Brute-forcing, DNS zone transfers                         |
| `Passive Enumeration` | Collects information about subdomains without directly interacting with the target, relying on public sources. | Certificate Transparency (CT) logs, search engine queries |

`Active enumeration` can be more thorough but carries a higher risk of detection. Conversely, `passive enumeration` is stealthier but may not uncover all subdomains. Combining both techniques can significantly increase the likelihood of discovering a comprehensive list of subdomains associated with your target, expanding your understanding of their online presence and potential vulnerabilities.

### Subdomain Brute-Forcing

Subdomain brute-forcing is a proactive technique used in web reconnaissance to uncover subdomains that may not be readily apparent through passive methods. It involves systematically generating many potential subdomain names and testing them against the target's DNS server to see if they exist. This approach can unveil hidden subdomains that may host valuable information, development servers, or vulnerable applications.

One of the most versatile tools for subdomain brute-forcing is `dnsenum`. This powerful command-line tool combines various DNS enumeration techniques, including dictionary-based brute-forcing, to uncover subdomains associated with your target.

To use `dnsenum` for subdomain brute-forcing, you'll typically provide it with the target domain and a wordlist containing potential subdomain names. The tool will then systematically query the DNS server for each potential subdomain and report any that exist.

For example, the following command would attempt to brute-force subdomains of `example.com` using a wordlist named `subdomains.txt`:

```bash
dnsenum example.com -f subdomains.txt
```

### Zone Transfers

DNS zone transfers, also known as AXFR (Asynchronous Full Transfer) requests, offer a potential goldmine of information for web reconnaissance. A zone transfer is a mechanism for replicating DNS data across servers. When a zone transfer is successful, it provides a complete copy of the DNS zone file, which contains a wealth of details about the target domain.

This zone file lists all the domain's subdomains, their associated IP addresses, mail server configurations, and other DNS records. This is akin to obtaining a blueprint of the target's DNS infrastructure for a reconnaissance expert.

To attempt a zone transfer, you can use the `dig` command with the `axfr` (full zone transfer) option. For example, to request a zone transfer from the DNS server `ns1.example.com` for the domain `example.com`, you would execute:

```bash
dig @ns1.example.com example.com axfr
```

However, zone transfers are not always permitted. Many DNS servers are configured to restrict zone transfers to authorized secondary servers only. Misconfigured servers, though, may allow zone transfers from any source, inadvertently exposing sensitive information.

### Virtual Hosts

Virtual hosting is a technique that allows multiple websites to share a single IP address. Each website is associated with a unique hostname, which is used to direct incoming requests to the correct site. This can be a cost-effective way for organizations to host multiple websites on a single server, but it can also create a challenge for web reconnaissance.

Since multiple websites share the same IP address, simply scanning the IP won't reveal all the hosted sites. You need a tool that can test different hostnames against the IP address to see which ones respond.

Gobuster is a versatile tool that can be used for various types of brute-forcing, including virtual host discovery. Its `vhost` mode is designed to enumerate virtual hosts by sending requests to the target IP address with different hostnames. If a virtual host is configured for a specific hostname, Gobuster will receive a response from the web server.

To use Gobuster to brute-force virtual hosts, you'll need a wordlist containing potential hostnames. Here's an example command:

```bash
gobuster vhost -u http://192.0.2.1 -w hostnames.txt
```

In this example, `-u` specifies the target IP address, and `-w` specifies the wordlist file. Gobuster will then systematically try each hostname in the wordlist and report any that results in a valid response from the web server.

### Certificate Transparency (CT) Logs

Certificate Transparency (CT) logs offer a treasure trove of subdomain information for passive reconnaissance. These publicly accessible logs record SSL/TLS certificates issued for domains and their subdomains, serving as a security measure to prevent fraudulent certificates. For reconnaissance, they offer a window into potentially overlooked subdomains.

The `crt.sh` website provides a searchable interface for CT logs. To efficiently extract subdomains using `crt.sh` within your terminal, you can use a command like this:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```

This command fetches JSON-formatted data from `crt.sh` for `example.com` (the `%` is a wildcard), extracts domain names using `jq`, removes any wildcard prefixes (`*.`) with `sed`, and finally sorts and deduplicates the results.

## Web Crawling

Web crawling is the automated exploration of a website's structure. A web crawler, or spider, systematically navigates through web pages by following links, mimicking a user's browsing behavior. This process maps out the site's architecture and gathers valuable information embedded within the pages.

A crucial file that guides web crawlers is `robots.txt`. This file resides in a website's root directory and dictates which areas are off-limits for crawlers. Analyzing `robots.txt` can reveal hidden directories or sensitive areas that the website owner doesn't want to be indexed by search engines.

`Scrapy` is a powerful and efficient Python framework for large-scale web crawling and scraping projects. It provides a structured approach to defining crawling rules, extracting data, and handling various output formats.

Here's a basic Scrapy spider example to extract links from `example.com`:

```python
import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"
    start_urls = ['http://example.com/']

    def parse(self, response):
        for link in response.css('a::attr(href)').getall():
            if any(link.endswith(ext) for ext in self.interesting_extensions):
                yield {"file": link}
            elif not link.startswith("#") and not link.startswith("mailto:"):
                yield response.follow(link, callback=self.parse)
```

After running the Scrapy spider, you'll have a file containing scraped data (e.g., `example_data.json`). You can analyze these results using standard command-line tools. For instance, to extract all links:

```bash
jq -r '.[] | select(.file != null) | .file' example_data.json | sort -u
```

This command uses `jq` to extract links, `awk` to isolate file extensions, `sort` to order them, and `uniq -c` to count their occurrences. By scrutinizing the extracted data, you can identify patterns, anomalies, or sensitive files that might be of interest for further investigation.

## Search Engine Discovery

Leveraging search engines for reconnaissance involves utilizing their vast indexes of web content to uncover information about your target. This passive technique, often referred to as Open Source Intelligence (OSINT) gathering, can yield valuable insights without directly interacting with the target's systems.

By employing advanced search operators and specialized queries known as "Google Dorks," you can pinpoint specific information buried within search results. Here's a table of some useful search operators for web reconnaissance:

| Operator        | Description                                           | Example                              |
| --------------- | ----------------------------------------------------- | ------------------------------------ |
| `site:`         | Restricts search results to a specific website.       | `site:example.com "password reset"`  |
| `inurl:`        | Searches for a specific term in the URL of a page.    | `inurl:admin login`                  |
| `filetype:`     | Limits results to files of a specific type.           | `filetype:pdf "confidential report"` |
| `intitle:`      | Searches for a term within the title of a page.       | `intitle:"index of" /backup`         |
| `cache:`        | Shows the cached version of a webpage.                | `cache:example.com`                  |
| `"search term"` | Searches for the exact phrase within quotation marks. | `"internal error" site:example.com`  |
| `OR`            | Combines multiple search terms.                       | `inurl:admin OR inurl:login`         |
| `-`             | Excludes specific terms from search results.          | `inurl:admin -intext:wordpress`      |

By creatively combining these operators and crafting targeted queries, you can uncover sensitive documents, exposed directories, login pages, and other valuable information that may aid in your reconnaissance efforts.

## Web Archives

Web archives are digital repositories that store snapshots of websites across time, providing a historical record of their evolution. Among these archives, the Wayback Machine is the most comprehensive and accessible resource for web reconnaissance.

The Wayback Machine, a project by the Internet Archive, has been archiving the web for over two decades, capturing billions of web pages from across the globe. This massive historical data collection can be an invaluable resource for security researchers and investigators.

| Feature                | Description                                                  | Use Case in Reconnaissance                                   |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `Historical Snapshots` | View past versions of websites, including pages, content, and design changes. | Identify past website content or functionality that is no longer available. |
| `Hidden Directories`   | Explore directories and files that may have been removed or hidden from the current version of the website. | Discover sensitive information or backups that were inadvertently left accessible in previous versions. |
| `Content Changes`      | Track changes in website content, including text, images, and links. | Identify patterns in content updates and assess the evolution of a website's security posture. |

By leveraging the Wayback Machine, you can gain a historical perspective on your target's online presence, potentially revealing vulnerabilities that may have been overlooked in the current version of the website.

# Information Gathering - Web Edition Module

|Section|Question Number|Answer|
|---|---|---|
|Utilizing WHOIS|Question 1|292|
|Utilizing WHOIS|Question 2|admin@dnstinations.com|
|Digging DNS|Question 1|134.209.24.248|
|Digging DNS|Question 2|inlanefreight.com|
|Digging DNS|Question 3|smtpin.vvv.facebook.com.|
|Subdomain Bruteforcing|Question 1|my.inlanefreight.com|
|DNS Zone Transfers|Question 1|22|
|DNS Zone Transfers|Question 2|10.10.34.2|
|DNS Zone Transfers|Question 3|10.10.200.14|
|Virtual Hosts|Question 1|web17611.inlanefreight.htb|
|Virtual Hosts|Question 2|vm5.inlanefreight.htb|
|Virtual Hosts|Question 3|browse.inlanefreight.htb|
|Virtual Hosts|Question 4|admin.inlanefreight.htb|
|Virtual Hosts|Question 5|support.inlanefreight.htb|
|Fingerprinting|Question 1|2.4.41|
|Fingerprinting|Question 2|Joomla|
|Fingerprinting|Question 3|Ubuntu|
|Creepy Crawlies|Question 1|inlanefreight-comp133.s3.amazonaws.htb|
|Web Archives|Question 1|74|
|Web Archives|Question 2|3054|
|Web Archives|Question 3|http://site.aboutface.com/|
|Web Archives|Question 4|Palm 0rganizer|
|Web Archives|Question 5|http://google.stanford.edu/|
|Web Archives|Question 6|17-December-99|
|Web Archives|Question 7|104155|
|Skills Assessment|Question 1|468|
|Skills Assessment|Question 2|nginx|
|Skills Assessment|Question 3|e963d863ee0e82ba7080fbf558ca0d3f|
|Skills Assessment|Question 4|1337testing@inlanefreight.htb|
|Skills Assessment|Question 5|ba988b835be4aa97d068941dc852ff33|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Utilizing WHOIS

## Question 1

### "Perform a WHOIS lookup against the paypal.com domain. What is the registrar Internet Assigned Numbers Authority (IANA) ID number?"

Students need to run `whois` against the `paypal.com` domain. However, given the vast amount of information returned by the command, students may want to pipe the results into `grep`, to see the data regarding `IANA` specifically:

Code: shell

```shell
whois paypal.com | grep IANA
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ whois paypal.com | grep IANA

   Registrar IANA ID: {hidden}
Registrar IANA ID: {hidden}
```

Answer: 292

# Utilizing WHOIS

## Question 2

### "What is the admin email contact for the tesla.com domain (also in-scope for the Tesla bug bounty program)?"

Students need to run `whois` against the `tesla.com` domain, piping the output into `grep` so they may look for all records referring to `admin`:

Code: shell

```shell
whois tesla.com | grep "admin"
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ whois tesla.com | grep "admin"

Registrant Email: {hidden}
Admin Email: {hidden}
Tech Email: {hidden}
```

Answer: `admin@dnstinations.com`

# Digging DNS

## Question 1

### "Which IP address maps to inlanefreight.com?"

Students need to use `dig` to find the IP address of `inlanefreight.com`, utilizing the `+short` option to keep the output concise, and relevant information clearly visible:

Code: shell

```shell
dig +short inlanefreight.com
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dig +short inlanefreight.com

{hidden}
```

Answer: `134.209.24.248`

# Digging DNS

## Question 2

### "Which domain is returned when querying the PTR record for 134.209.24.248?"

Referring to the previous section (DNS), students will recall that the `PTR` record is used for reverse DNS lookups, mapping an IP address to a hostname:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_1.png)

Then, referring to either the section's chart of **Common dig Commands**, or the [dig man pages](https://manpages.debian.org/bullseye/bind9-dnsutils/dig.1.en.html#x), students will come to realize the best course of action is to use `dig` with the `-x` option:

Code: shell

```shell
dig -x 134.209.24.248
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dig -x 134.209.24.248

; <<>> DiG 9.18.12-1~bpo11+1-Debian <<>> -x 134.209.24.248
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 41004
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;248.24.209.134.in-addr.arpa.	IN	PTR

;; ANSWER SECTION:
248.24.209.134.in-addr.arpa. 1800 IN	PTR	{hidden}.com.

;; Query time: 10 msec
;; SERVER: 1.1.1.1#53(1.1.1.1) (UDP)
;; WHEN: Tue Jun 18 21:37:35 BST 2024
;; MSG SIZE  rcvd: 87
```

Answer: `inlanefreight.com`

# Digging DNS

## Question 3

### "What is the full domain returned when you query the mail records for facebook.com?"

Students need to use the `dig` command to query for `MX` records of the `facebook.com` domain:

Code: shell

```shell
dig MX facebook.com
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dig MX facebook.com

; <<>> DiG 9.18.12-1~bpo11+1-Debian <<>> MX facebook.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 4885
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;facebook.com.			IN	MX

;; ANSWER SECTION:
facebook.com.		3600	IN	MX	10 {hidden}.

;; Query time: 6 msec
;; SERVER: 1.1.1.1#53(1.1.1.1) (UDP)
;; WHEN: Tue Jun 18 21:39:10 BST 2024
;; MSG SIZE  rcvd: 68
```

Answer: `smtpin.vvv.facebook.com`

# Subdomain Bruteforcing

## Question 1

### "Using the known subdomains for inlanefreight.com (www, ns1, ns2, ns3, blog, support, customer), find any missing subdomains by brute-forcing possible domain names. Provide your answer with the complete subdomain, e.g., www.inlanefreight.com."

Students need to use the `dnsenum` tool, supplying the [subdomains-top1million-20000.txt](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-20000.txt) wordlist from [SecLists](https://github.com/danielmiessler/SecLists) to bruteforce the subdomains of `inlanefreight.com`:

Code: shell

```shell
dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt

dnsenum VERSION:1.2.6

-----   inlanefreight.com   -----

<SNIP>

Google Results:
________________

blog.inlanefreight.com.                  300      IN    A        134.209.24.248

Brute forcing with /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt:
___________________________________________________________________________________

www.inlanefreight.com.                   300      IN    A        134.209.24.248
ns1.inlanefreight.com.                   300      IN    A        178.128.39.165
ns2.inlanefreight.com.                   300      IN    A        206.189.119.186
ns3.inlanefreight.com.                   300      IN    A        134.209.24.248
support.inlanefreight.com.               300      IN    A        134.209.24.248
{hidden}.inlanefreight.com.              300      IN    A        134.209.24.248
customer.inlanefreight.com.              300      IN    A        134.209.24.248
WWW.inlanefreight.com.                   300      IN    A        134.209.24.248
NS1.inlanefreight.com.                   300      IN    A        178.128.39.165
NS2.inlanefreight.com.                   300      IN    A        206.189.119.186
NS3.inlanefreight.com.                   300      IN    A        134.209.24.248
```

Answer: `my.inlanefreight.com`

# DNS Zone Transfers

## Question 1

### "After performing a zone transfer for the domain inlanefreight.htb on the target system, how many DNS records are retrieved from the target system's name server? Provide your answer as an integer, e.g, 123."

Students need to use the `dig` command to request a full zone transfer (`axfr`) from the DNS server responsible for `inlanefreight.htb`:

Code: shell

```shell
dig axfr inlanefreight.htb @STMIP
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dig axfr inlanefreight.htb @10.129.182.161

; <<>> DiG 9.18.12-1~bpo11+1-Debian <<>> axfr inlanefreight.htb @10.129.182.161
;; global options: +cmd
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
inlanefreight.htb.	604800	IN	NS	ns.inlanefreight.htb.
admin.inlanefreight.htb. 604800	IN	A	10.10.34.2
ftp.admin.inlanefreight.htb. 604800 IN	A	{hidden}
careers.inlanefreight.htb. 604800 IN	A	10.10.34.50
dc1.inlanefreight.htb.	604800	IN	A	10.10.34.16
dc2.inlanefreight.htb.	604800	IN	A	10.10.34.11
internal.inlanefreight.htb. 604800 IN	A	127.0.0.1
admin.internal.inlanefreight.htb. 604800 IN A	10.10.1.11
wsus.internal.inlanefreight.htb. 604800	IN A	10.10.1.240
ir.inlanefreight.htb.	604800	IN	A	10.10.45.5
dev.ir.inlanefreight.htb. 604800 IN	A	10.10.45.6
ns.inlanefreight.htb.	604800	IN	A	127.0.0.1
resources.inlanefreight.htb. 604800 IN	A	10.10.34.100
securemessaging.inlanefreight.htb. 604800 IN A	10.10.34.52
test1.inlanefreight.htb. 604800	IN	A	10.10.34.101
us.inlanefreight.htb.	604800	IN	A	10.10.200.5
cluster14.us.inlanefreight.htb.	604800 IN A	{hidden}
messagecenter.us.inlanefreight.htb. 604800 IN A	10.10.200.10
ww02.inlanefreight.htb.	604800	IN	A	10.10.34.112
www1.inlanefreight.htb.	604800	IN	A	10.10.34.111
inlanefreight.htb.	604800	IN	SOA	inlanefreight.htb. root.inlanefreight.htb. 2 604800 86400 2419200 604800
;; Query time: 10 msec
;; SERVER: 10.129.182.161#53(10.129.182.161) (TCP)
;; WHEN: Tue Jun 18 22:38:57 BST 2024
;; XFR size: {hidden} records (messages 1, bytes 594)
```

Answer: `22`

# DNS Zone Transfers

## Question 2

### "Within the zone record transferred above, find the ip address for ftp.admin.inlanefreight.htb. Respond only with the IP address, eg 127.0.0.1"

Students need to examine the results of the initial zone transfer. Or, as another option, students may repeat the zone transfer; this time piping the output into `grep` so they may easily identify the `A` record for `ftp.admin.inlanefreight.htb`:

Code: shell

```shell
dig axfr inlanefreight.htb @STMIP | grep "ftp.admin.inlanefreight.htb"
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dig axfr inlanefreight.htb @10.129.182.161 | grep "ftp.admin.inlanefreight.htb"

ftp.admin.inlanefreight.htb. 604800 IN	A	{hidden}
```

Answer: `10.10.34.2`

# DNS Zone Transfers

## Question 3

### "Within the same zone record, identify the largest IP address allocated within the 10.10.200 IP range. Respond with the full IP address, eg 10.10.200.1"

Students need to closely examine the results of the initial zone transfer. Or, as another option, students may repeat the zone transfer; this time piping the output into `grep` so they may easily identify the the largest IP within the `10.10.200` range:

Code: shell

```shell
dig axfr inlanefreight.htb @STMIP | grep "10.10.200"
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-0iwkw8pk4p]─[~]
└──╼ [★]$ dig axfr inlanefreight.htb @10.129.182.161 | grep "10.10.200"

us.inlanefreight.htb.	604800	IN	A	10.10.200.5
cluster14.us.inlanefreight.htb.	604800 IN A	10.10.200.{hidden}
messagecenter.us.inlanefreight.htb. 604800 IN A	10.10.200.10
```

Answer: `10.10.200.14`

# Virtual Hosts

## Question 1

### "Brute-force vhosts on the target system. What is the full subdomain that is prefixed with "web"? Answer using the full domain, e.g. "x.inlanefreight.htb""

To begin, students need to first modify their `/etc/hosts` file, tying the `inlanefreight.htb` domain to the IP of the spawned target:

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb' >> /etc/hosts" 
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.63.201 inlanefreight.htb' >> /etc/hosts" 
```

Students need to use `gobuster` to fuzz the `inlanefreight.htb` domain for additional `vhosts`, supplying the [subdomains-top1million-20000.txt](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-20000.txt) wordlist from [SecLists](https://github.com/danielmiessler/SecLists) using the `--append-domain` parameter:

Code: shell

```shell
gobuster vhost -u http://inlanefreight.htb:STMPO/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ gobuster vhost -u http://inlanefreight.htb:41578 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:41578
[+] Method:          GET
[+] Threads:         10
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/19 00:50:59 Starting gobuster in VHOST enumeration mode
===============================================================
Found: blog.inlanefreight.htb:54698 (Status: 200) [Size: 98]
Found: forum.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 104]
Found: {hiddem}.inlanefreight.htb:54698 (Status: 200) [Size: 96]     
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 102] 
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 106]
                                                                 
===============================================================
2024/06/19 00:53:34 Finished
===============================================================
```

Answer: `web17611.inlanefreight.htb`

# Virtual Hosts

## Question 2

### "Brute-force vhosts on the target system. What is the full subdomain that is prefixed with "vm"? Answer using the full domain, e.g. "x.inlanefreight.htb""

Students need to examine the output of the previous `gobuster` scan, looking for the `vhost` that is prefixed with the letters `vm`.

Or, if students are starting from a fresh Pwnbox / newly spawned target machine, they need to re-run the same command as they did previously for the first challenge question (ensuring that `inlanefreight.htb` has also been added to their `hosts` file):

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb' >> /etc/hosts" 
gobuster vhost -u http://inlanefreight.htb:STMPO/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.63.201 inlanefreight.htb' >> /etc/hosts" 

┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ gobuster vhost -u http://inlanefreight.htb:54698/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:41578
[+] Method:          GET
[+] Threads:         10
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/19 00:50:59 Starting gobuster in VHOST enumeration mode
===============================================================
Found: blog.inlanefreight.htb:54698 (Status: 200) [Size: 98]
Found: forum.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 104]
Found: {hiddem}.inlanefreight.htb:54698 (Status: 200) [Size: 96]     
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 102] 
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 106]
                                                                 
===============================================================
2024/06/19 00:53:34 Finished
===============================================================
```

Answer: `vm5.inlanefreight.htb`

# Virtual Hosts

## Question 3

### "Brute-force vhosts on the target system. What is the full subdomain that is prefixed with "br"? Answer using the full domain, e.g. "x.inlanefreight.htb""

Students need to examine the output of the previous `gobuster` scan, looking for the `vhost` that is prefixed with the letters `br`.

Or, if students are starting from a fresh Pwnbox / newly spawned target machine, they need to re-run the same command as they did previously for the first challenge question (ensuring that `inlanefreight.htb` has also been added to their `hosts` file):

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb' >> /etc/hosts"
gobuster vhost -u http://inlanefreight.htb:STMPO/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.63.201 inlanefreight.htb' >> /etc/hosts"

┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ gobuster vhost -u http://inlanefreight.htb:41578 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:41578
[+] Method:          GET
[+] Threads:         10
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/19 00:50:59 Starting gobuster in VHOST enumeration mode
===============================================================
Found: blog.inlanefreight.htb:54698 (Status: 200) [Size: 98]
Found: forum.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 104]
Found: {hiddem}.inlanefreight.htb:54698 (Status: 200) [Size: 96]     
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 102] 
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 106]
                                                                 
===============================================================
2024/06/19 00:53:34 Finished
===============================================================
```

Answer: `browse.inlanefreight.htb`

# Virtual Hosts

## Question 4

### "Brute-force vhosts on the target system. What is the full subdomain that is prefixed with "a"? Answer using the full domain, e.g. "x.inlanefreight.htb""

Students need to examine the output of the previous `gobuster` scan, looking for the `vhost` that is prefixed with the letter `a`.

Or, if students are starting from a fresh Pwnbox / newly spawned target machine, they need to re-run the same command as they did previously for the first challenge question (ensuring that `inlanefreight.htb` has also been added to their `hosts` file):

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb' >> /etc/hosts"
gobuster vhost -u http://inlanefreight.htb:STMPO/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.63.201 inlanefreight.htb' >> /etc/hosts"

┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ gobuster vhost -u http://inlanefreight.htb:41578 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:41578
[+] Method:          GET
[+] Threads:         10
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/19 00:50:59 Starting gobuster in VHOST enumeration mode
===============================================================
Found: blog.inlanefreight.htb:54698 (Status: 200) [Size: 98]
Found: forum.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 104]
Found: {hiddem}.inlanefreight.htb:54698 (Status: 200) [Size: 96]     
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 102] 
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 106]
                                                                 
===============================================================
2024/06/19 00:53:34 Finished
===============================================================
```

Answer: `admin.inlanefreight.htb`

# Virtual Hosts

## Question 5

### "Brute-force vhosts on the target system. What is the full subdomain that is prefixed with "su"? Answer using the full domain, e.g. "x.inlanefreight.htb""

Students need to examine the output of the previous `gobuster` scan, looking for the `vhost` that is prefixed with the letters `su`.

Or, if students are starting from a fresh Pwnbox / newly spawned target machine, they need to re-run the same command as they did previously for the first challenge question (ensuring that `inlanefreight.htb` has also been added to their `hosts` file):

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb' >> /etc/hosts"
gobuster vhost -u http://inlanefreight.htb:STMPO/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.63.201 inlanefreight.htb' >> /etc/hosts"

┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ gobuster vhost -u http://inlanefreight.htb:41578 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:41578
[+] Method:          GET
[+] Threads:         10
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/19 00:50:59 Starting gobuster in VHOST enumeration mode
===============================================================
Found: blog.inlanefreight.htb:54698 (Status: 200) [Size: 98]
Found: forum.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 100]
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 104]
Found: {hiddem}.inlanefreight.htb:54698 (Status: 200) [Size: 96]     
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 102] 
Found: {hidden}.inlanefreight.htb:54698 (Status: 200) [Size: 106]
                                                                 
===============================================================
2024/06/19 00:53:34 Finished
===============================================================
```

Answer: `support.inlanefreight.htb`

# Fingerprinting

## Question 1

### "Determine the Apache version running on app.inlanefreight.local on the target system. (Format: 0.0.0)"

Students first need to add entries for `app.inlanefreight.local` and `dev.inlanefreight.local` to their `hosts` file:

Code: shell

```shell
sudo sh -c "echo 'STMIP app.inlanefreight.local dev.inlanefreight.local' >> /etc/hosts" 
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ sudo sh -c "echo '10.129.122.20 app.inlanefreight.local dev.inlanefreight.local' >> /etc/hosts" 
```

Then, students need to run the `curl` command against `http://app.inlanefreight.local`, while providing the `-I` option to view the response headers:

Code: shell

```shell
curl -I http://app.inlanefreight.local
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ curl -I http://app.inlanefreight.local

HTTP/1.1 200 OK
Date: Wed, 19 Jun 2024 00:47:15 GMT
Server: Apache/{hidden} (Ubuntu)
Set-Cookie: 72af8f2b24261272e581a49f5c56de40=i3oatc7erbqjnl9g5c9su5896e; path=/; HttpOnly
Permissions-Policy: interest-cohort=()
Expires: Wed, 17 Aug 2005 00:00:00 GMT
Last-Modified: Wed, 19 Jun 2024 00:47:15 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Content-Type: text/html; charset=utf-8
```

Answer: `2.4.41`

# Fingerprinting

## Question 2

### "Which CMS is used on app.inlanefreight.local on the target system? Respond with the name only, e.g., WordPress."

Students need to open `Firefox`, browse to `http://app.inlanefreight.local`, and then check `Wappalyzer`. Students will notice that no `CMS` is detected initially, although by visiting the `Author Login` page, it will now be detected. This happens because `Wappalyzer` constantly tries to fingerprint technologies on every new visited URL, and it manages to identify which `CMS` is currently in use:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_2.png)

Alternatively, students can `cURL` the page and use `grep` for a tag used by default in many popular CMS. This tag is the `<meta name="generator">`, which is an HTML metadata element used to declare which software or CMS was used to generate the page.

Code: shell

```shell
curl -s http://app.inlanefreight.local/index.php | grep '<meta name="generator"'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-c8gdienlaz]─[~]
└──╼ [★]$ curl -s http://app.inlanefreight.local/index.php | grep '<meta name="generator"'

<meta name="generator" content="{hidden} - Open Source Content Management" />
```

Answer: `Joomla`

# Fingerprinting

## Question 3

### "On which operating system is the dev.inlanefreight.local webserver running in the target system? Respond with the name only, e.g., Debian."

Students need to run `nikto` against `http://dev.inlanefreight.local`, providing the `-Tuning b` option to identify outdated software and insecure files:

Code: shell

```shell
nikto -h http://dev.inlanefreight.local -Tuning b
```

```shell-session
┌─[us-academy-4]─[10.10.15.189]─[htb-ac-594497@htb-uxjsovx20u]─[~]
└──╼ [★]$ nikto -h http://dev.inlanefreight.local -Tuning b

- Nikto v2.1.6
---------------------------------------------------------------------------
+ Target IP:          10.129.122.20
+ Target Hostname:    dev.inlanefreight.local
+ Target Port:        80
+ Start Time:         2024-06-19 02:05:11 (GMT1)
---------------------------------------------------------------------------
+ Server: Apache/2.4.41 ({Hidden})

<SNIP>

+ Entry '/tmp/' in robots.txt returned a non-forbidden or redirect HTTP code (200)
+ "robots.txt" contains 14 entries which should be manually viewed.
+ Web Server returns a valid response with junk HTTP methods, this may cause false positives.
+ OSVDB-3092: /LICENSE.txt: License file found may identify site software.
+ 1304 requests: 0 error(s) and 18 item(s) reported on remote host
+ End Time:           2024-06-19 02:05:27 (GMT1) (16 seconds)
---------------------------------------------------------------------------
+ 1 host(s) tested
```

Answer: `Ubuntu`

# Creepy Crawlies

## Question 1

### "After spidering inlanefreight.com, identify the location where future reports will be stored. Respond with the full domain, e.g., files.inlanefreight.com."

To begin, students need to install the `scrapy` python library:

Code: shell

```shell
pip3 install scrapy --break-system-packages
```

```shell-session
┌─[us-academy-4]─[10.10.14.162]─[htb-ac-594497@htb-zitpukxi6x]─[~]
└──╼ [★]$ pip3 install scrapy --break-system-packages

Collecting scrapy
  Downloading Scrapy-2.11.2-py2.py3-none-any.whl (290 kB)
     |████████████████████████████████| 290 kB 37.4 MB/s 
Collecting PyDispatcher>=2.0.5
  Downloading PyDispatcher-2.0.7-py3-none-any.whl (12 kB)
Collecting tldextract
  Downloading tldextract-5.1.2-py3-none-any.whl (97 kB)
     |████████████████████████████████| 97 kB 19.5 MB/s 
     
<SNIP>

Successfully installed PyDispatcher-2.0.7 cssselect-1.2.0 defusedxml-0.7.1 itemadapter-0.9.0 itemloaders-1.3.1 parsel-1.9.1 protego-0.3.1 queuelib-1.7.0 requests-file-2.1.0 scrapy-2.11.2 tldextract-5.1.2 w3lib-2.2.1
```

Next, students need download the provided scrapy spider, `ReconSpider`, and extract it to their current working directory:

Code: shell

```shell
wget https://academy.hackthebox.com/storage/modules/279/ReconSpider.zip
unzip ReconSpider.zip 
```

```shell-session
┌─[us-academy-4]─[10.10.14.162]─[htb-ac-594497@htb-zitpukxi6x]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/modules/279/ReconSpider.zip

--2024-06-20 21:06:41--  https://academy.hackthebox.com/storage/modules/279/ReconSpider.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 104.18.20.126, 104.18.21.126, 2606:4700::6812:147e, ...
Connecting to academy.hackthebox.com (academy.hackthebox.com)|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1706 (1.7K) [application/zip]
Saving to: ‘ReconSpider.zip’

ReconSpider.zip     100%[===================>]   1.67K  --.-KB/s    in 0s      

2024-06-20 21:06:41 (23.9 MB/s) - ‘ReconSpider.zip’ saved [1706/1706]

┌─[us-academy-4]─[10.10.14.162]─[htb-ac-594497@htb-zitpukxi6x]─[~]
└──╼ [★]$ unzip ReconSpider.zip 

Archive:  ReconSpider.zip
  inflating: ReconSpider.py   
```

Now armed with the `ReconSpider.py`, students need to crawl the `inlanefreight.com` domain:

Code: shell

```shell
python3 ReconSpider.py http://inlanefreight.com
```

```shell-session
┌─[us-academy-4]─[10.10.14.162]─[htb-ac-594497@htb-zitpukxi6x]─[~]
└──╼ [★]$ python3 ReconSpider.py http://inlanefreight.com

2024-06-20 21:11:14 [scrapy.utils.log] INFO: Scrapy 2.11.2 started (bot: scrapybot)
2024-06-20 21:11:14 [scrapy.utils.log] INFO: Versions: lxml 4.6.3.0, libxml2 2.9.10, cssselect 1.2.0, parsel 1.9.1, w3lib 2.2.1, Twisted 20.3.0, Python 3.9.2 (default, Feb 28 2021, 17:03:44) - [GCC 10.2.1 20210110], pyOpenSSL 23.1.1 (OpenSSL 3.1.0 14 Mar 2023), cryptography 40.0.1, Platform Linux-6.1.0-1parrot1-amd64-x86_64-with-glibc2.31
2024-06-20 21:11:14 [scrapy.addons] INFO: Enabled addons:
[]
2024-06-20 21:11:14 [py.warnings] WARNING: /home/htb-ac-594497/.local/lib/python3.9/site-packages/scrapy/utils/request.py:254: ScrapyDeprecationWarning: '2.6' is a deprecated value for the 'REQUEST_FINGERPRINTER_IMPLEMENTATION' setting.

<SNIP>

2024-06-20 21:11:18 [scrapy.core.engine] INFO: Spider closed (finished)
```

After running `ReconSpider.py`, the data will be saved to a JSON file, `results.json`. Students need to explore its contents, specifically focusing on the data found under the "`comments`" key:

Code: shell

```shell
cat results.json | jq '.comments'
```

```shell-session
┌─[us-academy-4]─[10.10.14.162]─[htb-ac-594497@htb-zitpukxi6x]─[~]
└──╼ [★]$ cat results.json | jq '.comments'

[
  "<!-- /Navigation -->",
  "<!--==================== feature-product ====================-->",
  "<!-- #secondary -->",
  "<!-- #masthead -->",
  "<!--==================== transportex-FOOTER AREA ====================-->",
  "<!--/overlay-->",
  "<!-- change Jeremy's email to jeremy-ceo@inlanefreight.com -->",
  "<!-- TO-DO: change the location of future reports to {hidden} -->",
  "<!--\nSkip to content<div class=\"wrapper\">\n<header class=\"transportex-trhead\">\n\t<!--==================== Header ====================-->",
  "<!-- Blog Area -->",
  "<!-- Logo -->",
  "<!-- Navigation -->",
  "<!-- /navbar-toggle -->",
  "<!-- navbar-toggle -->",
  "<!--Sidebar Area-->",
  "<!--==================== TOP BAR ====================-->",
  "<!-- Right nav -->",
  "<!-- /Right nav -->"
]
```

Answer: `inlanefreight-comp133.s3.amazonaws.htb`

# Web Archives

## Question 1

### "How many Pen Testing Labs did HackTheBox have on the 8th August 2018? Answer with an integer, eg 1234."

To begin, students must first open `Firefox` and browse to the [Internet Archive's Wayback Machine](https://web.archive.org/). Subsequently, students need to do a search for `https://www.hackthebox.eu/en`, followed by selecting `August 8, 2018` from the `Calendar` view:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_3.png)

After clicking any of the saved snapshots from `August 8, 2018`, students will be redirected to the archived version of `Hack the Box`. Continuing to scroll down and explore the page, students will eventually find the section labeled `[ Pen Testing Labs]`:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_4.png)

Answer: `74`

# Web Archives

## Question 2

### "How many members did HackTheBox have on the 10th June 2017? Answer with an integer, eg 1234."

Students need continue to use [Wayback Machine](https://web.archive.org/), doing another search for `https://www.hackthebox.eu/en`, albeit this time selecting `June 10, 2017` from the `Calendar` view:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_5.png)

Choosing any of the three snapshots, students will be redirected to the archived version of `Hack the Box`. Again, students need to scroll down; upon reaching the `[ members ]` section, the total number of registered users will be displayed.

Answer: `3054`

# Web Archives

## Question 3

### "Going back to March 2002, what website did the facebook.com domain redirect too? Answer with the full domain, eg http://www.facebook.com/"

Students need use [Wayback Machine](https://web.archive.org/), searching for `facebook.com` and examining the lone snapshot found on `March 28, 2002`:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_6.png)

Following the redirect, students will find that they are taken to a different website altogether:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_7.png)

Therefore, students need to submit the full domain name the website as their answer.

Answer: `http://site.aboutface.com/`

# Web Archives

## Question 4

### "According to the paypal.com website in October 1999, what could you use to "beam money to anyone"? Answer with the product name, eg My Device, remove the ™ from your answer."

Students need use [Wayback Machine](https://web.archive.org/) to search for `paypal.com`, then examine any of the four snapshots available on `October 13, 1999`:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_8.png)

Answer: `Palm 0rganizer`

# Web Archives

## Question 5

### "Going back to November 1998 on google.com, what address hosted the non-alpha "Google Search Engine Prototype" of Google? Answer with the full address, eg http://google.com"

Students need use [Wayback Machine](https://web.archive.org/) to search for `google.com`, then examine any of the four snapshots seen on on `November 11, 1998`:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_9.png)

Students will be taken to a page containing a simple HTML header, `Welcome to Google`, along with two hyperlinks. Subsequently, students need to click the `Google Search Engine Prototype` link, and then observe the domain name:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_10.png)

Answer: `http://google.stanford.edu/`

# Web Archives

## Question 6

### "Going back to March 2000 on www.iana.org, when exacty was the site last updated? Answer with the date in the footer, eg 11-March-99"

Students need use [Wayback Machine](https://web.archive.org/) to search for `www.iana.org`, then examine the snapshot seen on on `March 3, 2000`:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_11.png)

Answer: `17-December-99`

# Web Archives

## Question 7

### "According to wikipedia.com snapshot taken on February 9, 2003, how many articles were they already working on in the English version? Answer with the number they state without any commas, e.g., 100000, not 100,000."

Students need to use the [Wayback Machine](https://web.archive.org/) to search for `wikipedia.com`, where they will then examine the snapshot seen on `February 9, 2003`:

![Information_Gathering_-_Web_Edition_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/49/Information_Gathering_-_Web_Edition_Walkthrough_Image_12.png)

Answer: `104155`

# Skills Assessment

## Question 1

### "What is the IANA ID of the registrar of the inlanefreight.com domain?"

Students need to perform a `whois` lookup on the `inlanefreight.com` domain, piping the results into `grep` so they may easily find the `IANA ID` of the registrar:

Code: shell

```shell
whois inlanefreight.com | grep IANA
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-ccbetqvkvg]─[~]
└──╼ [★]$ whois inlanefreight.com | grep IANA

   Registrar IANA ID: {hidden}
Registrar IANA ID: {hidden}
```

Answer: `468`

# Skills Assessment

## Question 2

### "What http server software is powering the inlanefreight.htb site on the target system? Respond with the name of the software, not the version, e.g., Apache."

Students need to first add the entry for `inlanefreight.htb` to their `/etc/hosts` file:

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb' >> /etc/hosts"
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-ccbetqvkvg]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.50.45 inlanefreight.htb' >> /etc/hosts"
```

Then, students need to run the `curl` command against `http://inlanefreight.htb:STMPO`, supplying the `-I` option to view only the response headers:

Code: shell

```shell
curl -I http://inlanefreight.htb:STMPO
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-ccbetqvkvg]─[~]
└──╼ [★]$ curl -I http://inlanefreight.htb:37705

HTTP/1.1 200 OK
Server: {hidden}/1.26.1
Date: Fri, 21 Jun 2024 21:14:55 GMT
Content-Type: text/html
Content-Length: 120
Last-Modified: Fri, 07 Jun 2024 14:56:31 GMT
Connection: keep-alive
ETag: "66631f9f-78"
Accept-Ranges: bytes
```

Answer: `nginx`

# Skills Assessment

## Question 3

### "What is the API key in the hidden admin directory that you have discovered on the target system?"

Students need to use `gobuster`, and proceed to fuzz the `inlanefreight.htb` domain for additional vhosts:

Code: shell

```shell
gobuster vhost -u http://inlanefreight.htb:SMTPO -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 60 --append-domain
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-envoycaulr]─[~]
└──╼ [★]$ gobuster vhost -u http://inlanefreight.htb:58825 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 60 --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://inlanefreight.htb:49765
[+] Method:          GET
[+] Threads:         60
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/22 00:31:00 Starting gobuster in VHOST enumeration mode
===============================================================
Found: web1337.inlanefreight.htb:58825 (Status: 200) [Size: 104]
                                                                
===============================================================
2024/06/22 00:33:28 Finished
===============================================================
```

After a few moments, a new virtual host will be revealed: `web1337.inlanefreight.htb`, which students need to then add to their `hosts` file:

Code: shell

```shell
sudo sh -c "echo 'STMIP web1337.inlanefreight.htb' >> /etc/hosts"
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-envoycaulr]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.54.176 web1337.inlanefreight.htb' >> /etc/hosts"
```

Furthermore, students need to enumerate the contents of the `robots.txt` file found on the `web1337.inlanefreight.htb` vhost:

Code: shell

```shell
curl http://web1337.inlanefreight.htb:STMPO/robots.txt
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-txguqg3mxx]─[~]
└──╼ [★]$ curl http://web1337.inlanefreight.htb:46840/robots.txt

User-agent: *
Allow: /index.html
Allow: /index-2.html
Allow: /index-3.html
Disallow: /admin_h1dd3n
```

Of particular interest is the single `Disallow` directive, which applies to all User Agents, and prevents them from crawling the `/admin_h1dd3n` page.

Therefore, students need to enumerate page further; starting by using `curl -I` to make a `HEAD` request and viewing the response headers:

Code: shell

```shell
curl -I http://web1337.inlanefreight.htb:STMPO/admin_h1dd3n
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-txguqg3mxx]─[~]
└──╼ [★]$ curl -I http://web1337.inlanefreight.htb:46840/admin_h1dd3n

HTTP/1.1 301 Moved Permanently
Server: nginx/1.26.1
Date: Sat, 22 Jun 2024 17:25:19 GMT
Content-Type: text/html
Content-Length: 169
Location: http://web1337.inlanefreight.htb/admin_h1dd3n/
Connection: keep-alive
```

Examining the response closely, students will find the HTTP Response Code: `301 Moved Permanently`, with the `Location` set to `http://web1337.inlanefreight.htb/admin_h1dd3n/`.

Subsequently, students need make a `GET` request to the aforementioned `/admin_h1dd3n/` endpoint:

Code: shell

```shell
curl http://web1337.inlanefreight.htb:STMPO/admin_h1dd3n/
```

```shell-session
┌─[us-academy-4]─[10.10.14.3]─[htb-ac-594497@htb-txguqg3mxx]─[~]
└──╼ [★]$ curl http://web1337.inlanefreight.htb:46840/admin_h1dd3n/

<!DOCTYPE html><html><head><title>web1337 admin</title></head><body><h1>Welcome to web1337 admin site</h1><h2>The admin panel is currently under maintenance, but the API is still accessible with the key {hidden}</h2></body></html>
```

Students may note that In URLs, the presence of a trailing slash typically indicates that the resource is a directory, while the absence of a trailing slash usually suggests a file. However, this is not a strict rule and can vary based on how the web server is configured; with this scenario being an exception to the rule.

Answer: `e963d863ee0e82ba7080fbf558ca0d3f`

# Skills Assessment

## Question 4

### "After crawling the inlanefreight.htb domain on the target system, what is the email address you have found? Respond with the full email, e.g., mail@inlanefreight.htb."

To begin, students need to add entries for both `inlanefreight.htb` and`web1337.inlanefreight.htb` to their `/etc/hosts` file:

Code: shell

```shell
sudo sh -c "echo 'STMIP inlanefreight.htb web1337.inlanefreight.htb' >> /etc/hosts"
```

```shell-session
┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.54.176 inlanefreight.htb web1337.inlanefreight.htb' >> /etc/hosts"
```

Then, students need to continue fuzzing for virtual hosts, this time targeting `web1337.inlanefreight.htb`:

Code: shell

```shell
gobuster vhost -u http://web1337.inlanefreight.htb:STMPO -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 60 --append-domain
```

```shell-session
┌─[us-academy-1]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ gobuster vhost -u http://web1337.inlanefreight.htb:49765 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 60 --append-domain

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:             http://web1337.inlanefreight.htb:49765
[+] Method:          GET
[+] Threads:         60
[+] Wordlist:        /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
[+] User Agent:      gobuster/3.6
[+] Timeout:         10s
[+] Append Domain:   true
===============================================================
2024/06/22 04:28:53 Starting gobuster in VHOST enumeration mode
===============================================================
Found: dev.web1337.inlanefreight.htb:52590 (Status: 200) [Size: 123]
```

In just a few moments, students will see `dev.web1337.inlanefreight.htb` appear in the `gobuster` output; a compelling candidate for a web crawler. Students need to add `dev.web1337.inlanefreight.htb` to their hosts file:

Code: shell

```shell
sudo sh -c "echo 'STMIP dev.web1337.inlanefreight.htb' >> /etc/hosts"
```

```shell-session
┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ sudo sh -c "echo '94.237.54.176 dev.web1337.inlanefreight.htb' >> /etc/hosts"
```

Now, students need install the `Scrapy` python library, along with the `ReconSpider.py` crawler (previously showcased in the `Creepy Crawlies` section):

Code: shell

```shell
pip3 install scrapy --break-system-packages
wget https://academy.hackthebox.com/storage/modules/279/ReconSpider.zip ; unzip ReconSpider.zip
```

```shell-session
┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ pip3 install scrapy --break-system-packages

Collecting scrapy
  Downloading Scrapy-2.11.2-py2.py3-none-any.whl (290 kB)
     |████████████████████████████████| 290 kB 28.7 MB/s 
Requirement already satisfied: setuptools in /usr/lib/python3/dist-packages (from scrapy) (66.1.1)
<SNIP>
Successfully installed PyDispatcher-2.0.7 cssselect-1.2.0 defusedxml-0.7.1 itemadapter-0.9.0 itemloaders-1.3.1 parsel-1.9.1 protego-0.3.1 queuelib-1.7.0 requests-file-2.1.0 scrapy-2.11.2 tldextract-5.1.2 w3lib-2.2.1

┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/modules/279/ReconSpider.zip ; unzip ReconSpider.zip

--2024-06-24 02:22:36--  https://academy.hackthebox.com/storage/modules/279/ReconSpider.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 104.18.20.126, 104.18.21.126, 2606:4700::6812:147e, ...
Connecting to academy.hackthebox.com (academy.hackthebox.com)|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1706 (1.7K) [application/zip]
Saving to: ‘ReconSpider.zip’

ReconSpider.zip     100%[==================>]   1.67K  --.-KB/s    in 0s      

2024-06-24 02:22:36 (30.9 MB/s) - ‘ReconSpider.zip’ saved [1706/1706]

Archive:  ReconSpider.zip
  inflating: ReconSpider.py       
```

Now, students need to use `ReconSpider.py` to crawl the recently discovered `dev.web1337.inlanefreight.htb` virtual host:

Code: shell

```shell
python3 ReconSpider.py http://dev.web1337.inlanefreight.htb:STMPO
```

```shell-session
┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ python3 ReconSpider.py http://dev.web1337.inlanefreight.htb:52590

2024-06-24 04:48:53 [scrapy.utils.log] INFO: Scrapy 2.11.2 started (bot: scrapybot)
2024-06-24 04:48:53 [scrapy.utils.log] INFO: Versions: lxml 4.6.3.0, libxml2 2.9.10, cssselect 1.2.0, parsel 1.9.1, w3lib 2.2.1, Twisted 20.3.0, Python 3.9.2 (default, Feb 28 2021, 17:03:44) - [GCC 10.2.1 20210110], pyOpenSSL 23.1.1 (OpenSSL 3.1.0 14 Mar 2023), cryptography 40.0.1, Platform Linux-6.1.0-1parrot1-amd64-x86_64-with-glibc2.31
2024-06-24 04:48:53 [scrapy.addons] INFO: Enabled addons:
<SNIP>
2024-06-24 04:49:11 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 31487,
 'downloader/request_count': 100,
 'downloader/request_method_count/GET': 100,
 'downloader/response_bytes': 34099,
 'downloader/response_count': 100,
 'downloader/response_status_count/200': 100,
 'elapsed_time_seconds': 17.719844,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2024, 6, 24, 3, 49, 11, 489386, tzinfo=datetime.timezone.utc),
 'log_count/INFO': 10,
 'log_count/WARNING': 1,
 'memusage/max': 67969024,
 'memusage/startup': 67969024,
 'request_depth_max': 99,
 'response_received_count': 100,
 'scheduler/dequeued': 100,
 'scheduler/dequeued/memory': 100,
 'scheduler/enqueued': 100,
 'scheduler/enqueued/memory': 100,
 'start_time': datetime.datetime(2024, 6, 24, 3, 48, 53, 769542, tzinfo=datetime.timezone.utc)}
2024-06-24 04:49:11 [scrapy.core.engine] INFO: Spider closed (finished)
```

At last, students need to analyze any email addresses that were identified and saved into the `results.json` file:

Code: shell

```shell
cat results.json | jq '.emails'
```

```shell-session
┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ cat results.json | jq '.emails'

[
  "{hidden}"
]
```

Answer: `1337testing@inlanefreight.htb`

# Skills Assessment

## Question 5

### "What is the API key the inlanefreight.htb developers will be changing too?"

Students need to analyze the data saved to the `results.json` file, after successfully crawling the `dev.web1337.inlanefreight.htb` virtual host during the previous question. Specifically, students need to focus on any `comments` that were found by the crawler:

```shell
cat results.json | jq '.comments'
```

```shell-session
┌─[us-academy-4]─[10.10.14.50]─[htb-ac-594497@htb-jq82a8ul9t]─[~]
└──╼ [★]$ cat results.json | jq '.comments'

[
  "<!-- Remember to change the API key to {hidden} -->"
]
```

Answer: `ba988b835be4aa97d068941dc852ff33`