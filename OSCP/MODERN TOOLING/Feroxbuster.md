# Feroxbuster

Fast, recursive content-discovery tool written in Rust. Officially packaged in Kali.

---

## What it replaces, and why it's faster

[[Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3]] teaches `gobuster dir`, which finds files/directories at one level and stops there, any subdirectory it finds needs a separate manual re-run pointed at the new path. Feroxbuster automatically recurses into every directory it discovers, in the same run, and can also extract links out of HTML/JS responses to find additional paths gobuster's pure wordlist approach would miss entirely.

## Install

```bash
sudo apt install feroxbuster
```

## Usage

```bash
# Basic recursive scan, extensions included
feroxbuster -u http://<target> -w /usr/share/wordlists/dirb/common.txt -x php,txt,html

# Cap recursion depth (avoid runaway scans on a deep site)
feroxbuster -u http://<target> -w wordlist.txt --depth 3

# Extract additional links from response bodies too, not just the wordlist
feroxbuster -u http://<target> -w wordlist.txt --extract-links
```
*`gobuster`'s flags (`-u`, `-w`, `-x`) map almost directly, this is close to a drop-in replacement for the module's own gobuster commands, just faster and automatically recursive instead of needing a second manual invocation per discovered subdirectory.*

## Where this applies in the vault

- [[Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3, Directory Brute Force with Gobuster]]
- Every `gobuster dir` invocation across [[Common Web Application Attacks]] (9.1.2, 9.3.1, etc), same swap applies anywhere the module reaches for gobuster
- [[Fixing Exploits#Module Exercise VM #2: elFinder web application|Fixing Exploits, Module Exercise VM #2]], a concrete case where the manual two-pass approach (find `/seclab/`, then a second `gobuster` scoped inside it to find elFinder's actual files) cost a full extra round trip, exactly what feroxbuster's recursion would have collapsed into one run

#### Tags: #ModernTooling #Feroxbuster #DirectoryBruteForce #ContentDiscovery #Gobuster
