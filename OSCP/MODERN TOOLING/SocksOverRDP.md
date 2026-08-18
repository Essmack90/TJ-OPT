# SocksOverRDP

Windows-only tool that tunnels SOCKS proxy traffic through an established RDP (Remote Desktop Protocol) virtual channel. Designed for environments where the pivot host only allows RDP connections inbound and has no SSH, HTTP, or other tunnel capability. Requires Proxifier on the pivot host to route new outbound connections through the SOCKS channel.

Cross-links: [[Pivoting, Tunneling, and Port Forwarding (HTB Supplementary)#PT.7 SocksOverRDP + Proxifier|PT.7]], [[Port Redirection and SSH Tunneling (Command Appendix)#SocksOverRDP + Proxifier (Windows-Only Multi-Hop via RDP)|Command Appendix]]

---

## What problem it solves

When a Windows pivot host is accessible via RDP but nothing else (SSH blocked, HTTP blocked, no outbound TCP), SocksOverRDP injects a plugin DLL into the `mstsc.exe` RDP client on Kali. The DLL opens a local SOCKS listener on Kali (port 1080) and forwards connections through the RDP virtual channel to a server component (`SocksOverRDP-Server.exe`) running on the pivot. Proxifier on the pivot routes new RDP sessions and other connections through this channel.

## Install

Download the release zip from GitHub: [https://github.com/nccgroup/SocksOverRDP](https://github.com/nccgroup/SocksOverRDP)

Two components:
- `SocksOverRDP-Plugin.dll` — the Kali-side plugin (loaded into `mstsc.exe`)
- `SocksOverRDP-Server.exe` — the pivot-side server component

## Usage

**On Kali (before connecting via RDP):**
```cmd
# Register the DLL plugin into the Windows registry (runs in Wine or on a Windows Kali session)
regsvr32.exe SocksOverRDP-Plugin.dll
```

**Launch mstsc.exe.** The plugin intercepts the RDP session and creates a local SOCKS listener on `127.0.0.1:1080` once the session connects.

**Transfer `SocksOverRDP-Server.exe` to the pivot host** (e.g. via the RDP session's clipboard or shared drive).

**On the pivot host (inside the RDP session):**
```cmd
# Run the server component — it waits for connections from the plugin via the RDP virtual channel
SocksOverRDP-Server.exe
```

**On Kali:** the plugin reports "SOCKS server listening on 127.0.0.1:1080" once the virtual channel handshakes.

**Configure Proxifier on the pivot** to route connections to the next internal hop through the SOCKS proxy (pointing back to Kali's 127.0.0.1:1080 via the RDP channel).

## Caveats

- **Windows Defender flags both the DLL and the server EXE.** Must be disabled or AV excluded before the tool will run.
- Requires admin rights on the pivot host to register the DLL and run the server.
- The SOCKS proxy opens on Kali's loopback, not a public IP, so tools running on Kali use `proxychains socks5 127.0.0.1 1080`.
- Multiple RDP hops are possible: each hop adds another SocksOverRDP layer, but latency compounds quickly.
- Not stealthy: AV flags, admin required, and visible in process list as mstsc.exe + SocksOverRDP-Server.exe.

#### Tags: #ModernTooling #SocksOverRDP #Proxifier #Pivoting #RDP #Windows #HTBSupplementary
