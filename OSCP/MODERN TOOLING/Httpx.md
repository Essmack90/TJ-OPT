# httpx (ProjectDiscovery)

Fast, multi-purpose HTTP probing toolkit. Not to be confused with the Python `httpx` library, this is ProjectDiscovery's standalone Go CLI tool.

---

## What it replaces, and why it's faster

[[Introduction to Web Application Attacks#8.2.1. Fingerprinting Web Servers with Nmap|8.2.1]] and [[Introduction to Web Application Attacks#8.2.2. Technology Stack Identification with Wappalyzer|8.2.2]] fingerprint one target at a time, `nmap`'s service detection for the server banner, Wappalyzer (browser extension) for the tech stack, both single-host, both requiring a human to look at each result. `httpx` probes a whole list of hosts/URLs at once and reports status code, title, tech stack, and more, in one pass, genuinely useful once there's more than a single target to fingerprint (a subdomain list, a CIDR range of web servers, CIDR being the slash notation like `192.168.1.0/24` that specifies an entire block of IP addresses at once).

## Install

```bash
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
# or: sudo apt install httpx-toolkit  (Kali's package name avoids a clash with an unrelated 'httpx' package)
```

## Usage

```bash
# Probe a single target, get status/title/tech-stack in one line
echo <target> | httpx-toolkit -sc -title -tech-detect

# Probe a whole list of hosts at once
cat hosts.txt | httpx-toolkit -sc -title -tech-detect -o results.txt

# Just check what's alive on a subnet before doing anything else
cat cidr_hosts.txt | httpx-toolkit -silent
```
*`-sc` (status code), `-title` (page title), `-tech-detect` (Wappalyzer-style stack fingerprinting, built in, no browser extension needed) are the three flags that cover most of what 8.2.1/8.2.2 do manually per host, just piped through a target list instead of eyeballed one at a time.*

## Where this applies in the vault

- [[Introduction to Web Application Attacks#8.2.1. Fingerprinting Web Servers with Nmap|8.2.1]] and [[Introduction to Web Application Attacks#8.2.2. Technology Stack Identification with Wappalyzer|8.2.2]], as the at-scale version of the same fingerprinting goal

#### Tags: #ModernTooling #Httpx #ProjectDiscovery #Fingerprinting #TechStackDetection
