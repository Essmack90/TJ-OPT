# Kiterunner

API-aware endpoint brute-forcer from Assetnote. Instead of a plain wordlist of paths, it uses wordlists compiled from real-world OpenAPI/Swagger specs, so it guesses realistic API route shapes (methods, parameters, versioned paths) rather than generic web-directory names.

---

## What it replaces, and why it's faster

[[08. Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]] teaches manual API probing, trying `/api/v1/`, `/api/v2/`, guessing endpoint names and HTTP methods by hand based on what the app's own JS/docs hint at. Kiterunner automates exactly that guessing process using a wordlist built from tens of thousands of real API specs, and crucially, it tries the *correct HTTP method* per route (`POST`/`PUT`/`DELETE`, not just `GET`), which a plain gobuster/ffuf path-only wordlist won't do.

## Install

```bash
git clone https://github.com/assetnote/kiterunner.git
cd kiterunner
make build
# wordlists (the .kite files) are a separate download, linked from the repo's README
```

## Usage

```bash
# Scan against a compiled API wordlist
kr scan -w routes-large.kite -u http://<target>

# Brute-force mode: build routes from a plain wordlist instead of the pre-compiled .kite format
kr brute wordlist.txt -u http://<target>

# Narrow to a specific API path depth (avoid an overwhelming result set on a large target)
kr scan -w routes-large.kite -u http://<target> --max-depth 2
```
*`kr scan` is the fast path once you have a `.kite` wordlist, `kr brute` works from a plain text wordlist if you don't. Output includes the method + path + response code for every hit, exactly the "does this endpoint exist and what verb does it accept" question 8.3.3 walks through manually.*

## Where this applies in the vault

- [[08. Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3, Enumerating and Abusing APIs]], directly replaces the manual endpoint-guessing workflow

#### Tags: #ModernTooling #Kiterunner #APIEnumeration #ContentDiscovery
