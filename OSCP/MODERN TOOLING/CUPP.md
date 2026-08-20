# CUPP

**What it is:** Common User Passwords Profiler. Generates personalised password wordlists from OSINT data about a specific target person. Interactive mode (`-i`) walks you through prompts for name, nickname, birthdate, partner, pet, company, and keywords, then produces mutations with leet-speak, special-char suffixes, and numeric suffixes.

**Install:**
```bash
sudo apt install cupp -y
# Or from source:
git clone https://github.com/Mebus/cupp.git && cd cupp
```

**Interactive mode:**
```bash
cupp -i
# Prompts walk through: first name, surname, nickname, birthdate, partner details, pet, company
# End options: special chars? / random numbers? / leet mode?
# Output: firstname.txt (commonly 20,000–50,000 entries)
```

**Filter output to match a known password policy:**
```bash
# Example: >= 6 chars, uppercase, lowercase, digit, 2 special chars
grep -E '^.{6,}$' jane.txt \
  | grep -E '[A-Z]' \
  | grep -E '[a-z]' \
  | grep -E '[0-9]' \
  | grep -E '([!@#$%^&*].*){2,}' \
  > jane-filtered.txt
```

**When to use:** targeted attacks where you have OSINT on a person (name, birthday, relationships, employer). Pair with [[Username-anarchy]] for the username list and Hydra/Medusa for the attack.

**Module source:** [[Login Brute Forcing (HTB Supplementary)#LBF.6. Custom Wordlists (CUPP + username-anarchy + grep filtering)|LBF.6]]
**Command Appendix:** [[Password Attacks#CUPP (Targeted Password Wordlist Generation)|Password Attacks. CUPP section]]
