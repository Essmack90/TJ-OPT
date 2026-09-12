# Modern Tooling

Use the modern tool only when it shortens a confirmed task. Keep Nmap, curl, LDAP, and manual proof as the fallback when a tool is missing, noisy, or gives an ambiguous result.

## Fast loop

### Run this

~~~bash
command -v rustscan nmap httpx-toolkit feroxbuster ffuf burpsuite netexec \
  bloodhound-python bloodhound bloodyAD john
~~~

### Example output

~~~text
/usr/bin/rustscan
/usr/bin/feroxbuster
/usr/bin/netexec
~~~

### What did you get?

- [ ] Faster replacement exists -> **Use the matching command below and save its raw output.**
- [ ] Tool is missing -> **Use the adjacent Nmap, curl, LDAP, or manual fallback.**
- [ ] BloodHound data is ready -> **Open the GUI, select one exact edge, then return to [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]].**
- [ ] Burp is needed -> **Capture one real request, send it to Repeater, and change one field at a time.**
- [ ] Tool output is ambiguous -> **Stop the shortcut and confirm with the manual command.**

### Open next

Return to the service or privilege page that requested the tool. This page is a command switchboard, not a separate exploitation branch.

## Tool check

~~~bash
command -v rustscan nmap httpx-toolkit feroxbuster ffuf burpsuite netexec \
  bloodhound-python bloodhound bloodyAD john
~~~

## Fast replacements

| Task                         | Fast command                                                                            | Confirm with                              |                                |
| ---------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------ |
| Port discovery               | `rustscan -a "$BoxIP" --ulimit 5000 -- -Pn -n -sC -sV`                                  | Nmap saved service scan                   |                                |
| HTTP probing                 | `httpx-toolkit -u "$WebURL" -sc -title -tech-detect -server`                            | curl headers and body                     |                                |
| Recursive web discovery      | `feroxbuster -u "$WebURL/" -w "$Wordlist" -x php,txt,html -t 30`                        | curl the promising path                   |                                |
| Filtered web fuzzing         | `ffuf -u "$WebURL/FUZZ" -w "$Wordlist" -ac -of json`                                    | Burp Repeater or curl                     |                                |
| Request discovery and replay | `burpsuite &`                                                                           | saved raw request and response            |                                |
| SMB and WinRM validation     | `netexec smb "$BoxIP" -u "$Username" -p "$Password"`                                    | `netexec winrm` or Evil-WinRM             |                                |
| AD graph collection          | `bloodhound-python -d "$Domain" -u "$Username" -p "$Password" -ns "$DCIP" -c All --zip` | BloodHound GUI and LDAP                   |                                |
| AD object and ACL operation  | `bloodyAD --help` then exact supported action                                           | LDAP or BloodHound before and after       |                                |
| Offline hash cracking        | `john --wordlist="$Wordlist" "$HashFile"`                                               | service authentication once               |                                |
| Linux prioritisation         | `"$LinPEAS" 2>&1                                                                        | tee "$BoxDir/loot/linpeas.txt"`           | reproduce the finding manually |
| Windows prioritisation       | `& "$WinPEAS" quiet cmdfast`                                                            | identity, ACL, service, and task commands |                                |

## BloodHound GUI loop

~~~bash
sudo neo4j start
bloodhound --no-sandbox &
~~~

Import the ZIP, search the current principal, inspect the shortest path to a privileged target, and record the exact object and edge. Validate the edge before writing to AD. Use [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]] for the command branch.

## Burp Suite loop

1. Start Burp and configure the browser proxy.
2. Browse the confirmed application path once.
3. Send the request to Repeater.
4. Change one method, header, parameter, or body field at a time.
5. Save the response that proves the branch under `$BoxDir/loot/`.

Use the dedicated guide when the browser proxy or certificate is the problem: [[05_BURP_SUITE_COMPLETE_GUIDE/05_BURP_SUITE_COMPLETE_GUIDE|Burp Suite guide]].

## When not to use the shortcut

- Do not run several recursive scanners against a fragile service.
- Do not treat a BloodHound edge as proof until the exact ACL or authentication result is confirmed.
- Do not let LinPEAS or WinPEAS replace identity, permission, and execution checks.
- Do not use a framework exploit when a reviewed standalone proof is available.

## Source pages

- [[OSCP/MODERN TOOLING/Rustscan|RustScan]]
- [[OSCP/MODERN TOOLING/Feroxbuster|Feroxbuster]]
- [[OSCP/MODERN TOOLING/Ffuf|Ffuf]]
- [[OSCP/MODERN TOOLING/Httpx|ProjectDiscovery httpx]]
- [[OSCP/MODERN TOOLING/NetExec|NetExec]]
- [[OSCP/MODERN TOOLING/BloodHound-Python|BloodHound-Python]]
- [[OSCP/MODERN TOOLING/BloodyAD|BloodyAD]]
- [[OSCP/MODERN TOOLING/LinPEAS|LinPEAS]]
- [[OSCP/MODULES/17. Windows Privilege Escalation|Windows Privilege Escalation module]] -- WinPEAS remains the fast Windows enumeration option
