# Linux - Port Forwarding

**Step 20 of 50 · Linux**

*Forward an internal service to your Kali machine so you can attack it with local tools.*

## Run this

First confirm what is listening internally after you have a shell:

```bash
ss -tnlp
netstat -tnlp 2>/dev/null
```

Then open an SSH local forward from Kali (requires SSH access to the target):

```bash
# Forward target's internal port 8080 to your local port 8888
ssh -L 8888:127.0.0.1:8080 $Username@$BoxIP -i $BoxDir/loot/${Username}_id_rsa -N
```

Access the forwarded service:

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

- [ ] An internal HTTP service is found → **Forward it and enumerate with feroxbuster + curl**
- [ ] A login panel is found on the internal service → **Test default credentials, then look for injection or command execution**
- [ ] Command injection is found on the internal service → **Send a reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The internal service leaks credentials → **Validate them on SSH or the main application**
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

## Windows localhost service

The same SSH local forward works when the remote target is Windows. Use the recovered Windows account and forward the service from the target loopback to a free local port.

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
