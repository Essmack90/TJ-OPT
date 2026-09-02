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

**Module source:** [[16. Password Attacks|LBF.6]]
**Command Appendix:** [[16. Password Attacks#CUPP (Targeted Password Wordlist Generation)|Password Attacks. CUPP section]]
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

CUPP supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

CUPP is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Install

Use the package or project installation method available on Kali. For an apt package, the pattern is:

~~~bash
sudo apt install cupp
~~~

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
cupp --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
