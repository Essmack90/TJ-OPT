# Linux - Port Forwarding

**Step 20 of 50 · Linux**

*Forward an internal service to your Kali machine so you can attack it with local tools.*

## Run this

First confirm what is listening internally after you have a shell:

> **Why:** This SSH connection tests the recovered credential or reaches a legacy daemon using the compatibility options it requires.
```bash
ss -tnlp
netstat -tnlp 2>/dev/null
```

Then open an SSH local forward from Kali (requires SSH access to the target):

> **Why:** This content scan tests likely paths or hostnames to find hidden pages, files, or virtual hosts that are not linked from the homepage.
```bash
# Forward target's internal port 8080 to your local port 8888
ssh -L 8888:127.0.0.1:8080 $Username@$BoxIP -i $BoxDir/loot/${Username}_id_rsa -N
```

Access the forwarded service:

> **Why:** This content scan tests likely paths or hostnames to find hidden pages, files, or virtual hosts that are not linked from the homepage.
```bash
curl -s http://127.0.0.1:8888/
feroxbuster -u http://127.0.0.1:8888/ -w /usr/share/wordlists/dirb/common.txt
```

## Example output

Internal service found:

```
LISTEN 0 128 127.0.0.1:8080  0.0.0.0:*
```

Tunnel open (no output — `-N` means no command):

```
# SSH stays open in the foreground, access 127.0.0.1:8888 from Kali
```

Service responds through tunnel:

```
HTTP/1.1 200 OK
<html>Internal monitoring panel...
```

## What did you get?

- [ ] An internal HTTP service is found → **Run `ssh -L $LocalPort:127.0.0.1:$RemotePort $Username@$BoxIP`, then run `curl -i http://127.0.0.1:$LocalPort/` and `feroxbuster -u http://127.0.0.1:$LocalPort/ -w /usr/share/wordlists/dirb/common.txt`**
- [ ] A login panel is found on the internal service → **Open `http://127.0.0.1:$LocalPort/` in the browser, submit documented default credentials once, and inspect the authenticated page for injection or command-execution inputs**
- [ ] Command injection is found on the internal service → **Send a reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The internal service leaks credentials → **Run `ssh $Username@$BoxIP` with `$Password`, or submit the values to the main application, then record whether authentication succeeds**
- [ ] No useful service is listening internally → **Go to Step 17 · [[Linux - Credential Search]]**

## Notes

SSH local port forwarding (`-L`) binds a port on your Kali machine and tunnels traffic through the SSH connection to a port on the target. The target sees the traffic as coming from localhost, which bypasses any external firewall rules.

Use `-N` to keep the tunnel open without executing a remote command. Run the tunnel in a separate terminal so you can continue working.

If SSH key authentication is needed, point `-i` at the key you extracted during foothold.

## Gotcha

> [!warning] 💡
> The forwarded port on your machine (`8888`) is separate from the target port (`8080`). Tools like feroxbuster must target `127.0.0.1:8888` — not `$BoxIP:8080`, which is not accessible externally.

> [!warning] 💡
> If the internal service requires an authenticated session, capture its cookie after logging in through the tunnel and reuse it for further requests.

## Loopback service re-enumeration

After gaining a shell, repeat local listening-service checks because services bound to `127.0.0.1` are invisible to an external Nmap scan. `localhost` means the target machine itself, not Kali.

> **Why:** These commands list TCP listeners and request a local HTTP service; look for a process bound to `127.0.0.1` and a valid response from its port.
```bash
# Check target-side listeners, then test the discovered local web port.
ss -tlnp
curl -s http://127.0.0.1:$WebPort/
```

> **Why:** This SSH `-L` option binds a Kali port and forwards it through the SSH session to the target’s loopback service; a `200`, `302`, or application title confirms the tunnel.
```bash
# Local port 8888 is only an example; choose an unused Kali port.
ssh -L 8888:127.0.0.1:$WebPort $Username@$BoxIP -N
curl -s http://127.0.0.1:8888/
```

> **Why:** These requests enumerate the newly reachable service through the tunnel, where Kali can now use normal web tools against it.
```bash
feroxbuster -u http://127.0.0.1:8888/ -w /usr/share/wordlists/dirb/common.txt
curl -s http://127.0.0.1:8888/robots.txt
```

## Additional routing

- [ ] A loopback web service responds → **Re-enumerate it and go to Step 5 · [[Linux - Web Enum]] or Step 8A · [[Linux - Command Injection]]**
- [ ] The tunnel cannot connect → **Confirm SSH access, choose a free local port, and verify the target-side port from `ss`**
- [ ] No useful listener exists → **Return to Step 17 · [[Linux - Credential Search]]**

## Windows localhost service

The same SSH local forward works when the remote target is Windows. Use the recovered Windows account and forward the service from the target loopback to a free local port.

> **Why:** This SSH connection tests the recovered credential or reaches a legacy daemon using the compatibility options it requires.
~~~bash
ssh -L $TunnelPort:127.0.0.1:$RemotePort $Username@$BoxIP -N
curl -sk https://127.0.0.1:$TunnelPort/ -o /dev/null -w "%{http_code}\n"
~~~

The first value is the local listening port. The second value is the service port on the target. A 302, 200, or other expected application response confirms that the tunnel is working.

> [!warning] 💡
> The tunnel still prompts for the SSH password even with -N. The option prevents a remote shell from opening; it does not skip authentication. Keep the tunnel terminal running while you use the forwarded service.

## External Resources

| Resource | Link |
|---|---|
| HackTricks — Port Forwarding | https://book.hacktricks.xyz/generic-methodologies-and-resources/tunneling-and-port-forwarding |
| PayloadsAllTheThings — Port Forwarding | https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Network%20Discovery.md |

## Additional routing

- [ ] The forwarded service returns a distinct application → **Re-enumerate it through the local tunnel and follow its matching service stage**
- [ ] The tunnel connects but the service is unchanged or closed → **Check the remote loopback port and return to Step 13 · [[Linux - Local Enum]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
