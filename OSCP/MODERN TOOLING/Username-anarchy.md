# username-anarchy

Generates realistic username format candidates from a list of real names. Outputs combinations like `john.smith`, `jsmith`, `smithj`, `john`, `j.smith`, etc., to use as input for kerbrute userenum or Hydra spray.

---

## What it replaces, and why it's faster

Manual construction of username candidates from a list of names (e.g. scraped from LinkedIn or a company website) is error-prone and misses formats. username-anarchy applies every common enterprise username convention to every name in your input list, producing a candidate file ready for kerbrute in seconds.

## Install

```bash
# Clone from GitHub
git clone https://github.com/urbanadventurer/username-anarchy
cd username-anarchy
```

## Usage

```bash
# Generate all formats for a single name
ruby username-anarchy.rb John Smith

# Generate from a file (first + last on each line, or space-separated)
ruby username-anarchy.rb -i names.txt > candidate_users.txt

# Pipe directly to kerbrute
ruby username-anarchy.rb -i names.txt | kerbrute userenum -d corp.local --dc 192.168.1.10 --stdin
```

**Input format for `-i`:** one name per line, first and last space-separated:
```
John Smith
Jane Doe
Bob Admin
```

**Output:** one candidate per line — `john`, `smith`, `john.smith`, `j.smith`, `jsmith`, `smithj`, `johns`, etc.

> 🔍 **Sourcing the name list:** company websites often list staff names on About/Team pages. LinkedIn with `site:linkedin.com/in "Company Name"` Google dork works too. Or pull `exiftool -a -u *.pdf` from any publicly available company documents (Author field often contains names).

## Where this applies in the vault

- [[Active Directory Methodology#Step 1: Username Enumeration (before spraying)|AD Methodology, Phase 2 Step 1]]
- [[Password Attacks (HTB Supplementary)#PA.21 username-anarchy|PA.21]]
- [[Secrets & Credentials (Decision Tree)#Need to validate a list of potential AD usernames before spraying|Decision Tree]]

🔁 [[Kerbrute]] (the validation step after username generation), [[Password Attacks (HTB Supplementary)#PA.21|PA.21]]

#### Tags: #ModernTooling #usernameAnarchy #ActiveDirectory #UsernameGeneration #PasswordSpray
