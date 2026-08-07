# ffuf

"Fuzz Faster U Fool," a fast, general-purpose web fuzzer written in Go. Not just directory brute-forcing, the `FUZZ` keyword can go anywhere: a URL path, a header value, a POST body, a parameter value.

---

## What it replaces, and why it's faster

A few different manual moments across the vault get faster with this one tool:
- [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]'s manual traversal-depth guessing (`curl` with `../../../etc/passwd`, adding more `../` by hand and re-running each time) becomes one `ffuf` run that tries every depth/payload from a wordlist at once.
- [[Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3]]'s directory brute force, same swap as [[Feroxbuster]] covers, `ffuf` is the more flexible option when the fuzz point isn't just a URL path (a header, a POST field, a cookie value).

## Install

```bash
sudo apt install ffuf
# or: go install github.com/ffuf/ffuf/v2@latest
```

## Usage

```bash
# Directory brute force (gobuster/feroxbuster equivalent)
ffuf -u http://<target>/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Fuzz a traversal-depth payload list instead of a fixed number of ../
ffuf -u "http://<target>/index.php?page=FUZZ" -w traversal-payloads.txt -mc 200

# Fuzz a POST body field
ffuf -u http://<target>/login -X POST -d "user=admin&pass=FUZZ" -H "Content-Type: application/x-www-form-urlencoded" -w rockyou.txt

# Filter out the noise: hide a specific response size (e.g. the "not found" page's consistent size)
ffuf -u http://<target>/FUZZ -w wordlist.txt -fs 4242
```
*The `FUZZ` keyword is the whole trick, drop it anywhere in the URL/header/body and that's the injection point ffuf iterates the wordlist through. `-mc`/`-fc` (match/filter by status code) and `-fs` (filter by response size) are what make the output usable instead of drowning in false positives.*

## Where this applies in the vault

- [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]], fuzzing traversal depth/payloads instead of manually incrementing `../`
- [[Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3]], as a more flexible alternative to gobuster when the fuzz point isn't a plain URL path
- [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], could fuzz a list of extension-bypass variants (`.pHP`, `.phps`, `.php7`, etc) in one pass instead of trying them one at a time by hand

#### Tags: #ModernTooling #Ffuf #Fuzzing #DirectoryBruteForce #DirectoryTraversal
