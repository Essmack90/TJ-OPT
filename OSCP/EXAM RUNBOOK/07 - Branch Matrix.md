# Branch Matrix

Use this page when the primary route does not immediately produce a foothold. Choose the row from observed output, run one confirming command, and follow one linked branch. For the complete write-up-by-write-up route map, open [[OSCP/EXAM RUNBOOK/10 - Scenario Matrix|Scenario Matrix]].

## Fast loop

### Run this

Run the single `Confirm` command in the row that matches the saved evidence. Do not run every row.

### Example output

~~~text
HTTP/1.1 200 OK
Server: $Product
~~~

### What did you get?

- [ ] A row confirms the finding -> **Follow its route and save the confirming output.**
- [ ] The result is a timeout -> **Measure a known static path and lower concurrency.**
- [ ] Authentication fails -> **Recheck account format, domain, protocol, and clock.**
- [ ] No row matches -> **Return to [[OSCP/EXAM RUNBOOK/01 - Recon and Triage|Recon and Triage]] and rescan the exact service.**

### Open next

Open the linked route in the matching row below. After a shell lands, return to the Linux, Windows, or AD fast path.

## Network and service branches

| Evidence | Confirm | Route |
|---|---|---|
| Open web port | `curl -sS -i "$WebURL/"` | [[OSCP/EXAM RUNBOOK/02 - Web and Services\|Web and Services]] |
| HTTP works but scans time out | `curl --max-time 60 -w '%{time_total}\n' "$WebURL/$Path"` | lower concurrency and continue manually |
| FTP allows anonymous access | `ftp "$BoxIP"` | download files; inspect for credentials, web-root paths, or source |
| DNS is open and hostname is known | `dig axfr "$Domain" @"$DCIP"` | add discovered names and return to web vhost enumeration |
| SNMP responds | `snmpwalk -v2c -c "$Community" "$BoxIP"` | inspect usernames, processes, and configuration clues |
| UDP 500 or 4500 is open | `ike-scan "$BoxIP"` | [[OSCP/RUNBOOK V2/Windows - IKE-IPSec Transport\|Windows - IKE-IPSec Transport]] |
| SMB or WinRM accepts credentials | `netexec smb "$BoxIP" -u "$Username" -p "$Password"` | [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path\|Windows Fast Path]] |
| LDAP or Kerberos is open | `netexec ldap "$DCIP" -u "$Username" -p "$Password" -d "$Domain"` | [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path\|Active Directory Fast Path]] |

## Web branches

| Evidence | Confirm | Route |
|---|---|---|
| CMS fingerprint | `whatweb "$WebURL"` | CMS-specific page in [[OSCP/EXAM RUNBOOK/02 - Web and Services\|Web and Services]] |
| Rejetto HttpFileServer 2.3 | `searchsploit "Rejetto HttpFileServer 2.3"` | review Exploit-DB 49125, then [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path\|Windows Fast Path]] |
| REST or JSON route | replay in Burp Repeater and curl | compare methods and authorization; follow API branch |
| File parameter | request `/etc/passwd` or the Windows hosts file | [[OSCP/RUNBOOK V2/Linux - LFI\|Linux - LFI]] or [[OSCP/RUNBOOK V2/Windows - XXE\|Windows - XXE]] |
| Upload form | save the multipart request | [[OSCP/RUNBOOK V2/Linux - File Upload\|Linux - File Upload]] or [[OSCP/RUNBOOK V2/Windows - Web - FTP Upload\|Windows - Web - FTP Upload]] |
| Source archive or JAR | `file "$BoxDir/loot/$File"` | [[OSCP/RUNBOOK V2/Linux - Binary Analysis\|Linux - Binary Analysis]] and [[OSCP/RUNBOOK V2/Linux - Credential Search\|Linux - Credential Search]] |
| SQL-looking input | compare harmless true and false conditions | [[OSCP/RUNBOOK V2/Linux - SQLi\|Linux - SQLi]] |
| Command-shaped input | compare harmless output before callback work | [[OSCP/RUNBOOK V2/Linux - Command Injection\|Linux - Command Injection]] |
| CGI directory or executable script | request the script and prove execution with a harmless identity command | [[OSCP/RUNBOOK V2/Linux - Shellshock CGI\|Linux - Shellshock CGI]] |

## Shell and privilege branches

| Evidence | Confirm | Route |
|---|---|---|
| Linux shell | `id; hostname; sudo -l` | [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path\|Linux Fast Path]] |
| Windows shell | `whoami /all` | [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path\|Windows Fast Path]] |
| Old Windows build and kernel candidates | `systeminfo` then Sherlock | reject candidates whose CPU or architecture prerequisites fail; see [[#T52 - Windows patch triage and MS16-098\|T52]] |
| Direct all-command sudo | `sudo -l` | `sudo -i`, then prove identity |
| SeImpersonatePrivilege | `whoami /priv` | [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse\|Windows - SeImpersonate Abuse]] |
| Writable root service, task, or cron | ownership plus trigger check | matching service or scheduler page |
| SUID or capability | `find / -perm -4000 -type f 2>/dev/null; getcap -r / 2>/dev/null` | [[OSCP/RUNBOOK V2/Linux - SUID Check\|Linux - SUID Check]] |
| AD graph edge | exact object and permission in BloodHound | [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path\|Active Directory Fast Path]] |

## Failure rules

- **Timeout:** measure a known static path, then tune the tool.
- **Authentication failure:** recheck account format, domain, protocol, and time before trying another password.
- **Exploit crash:** stop sending requests, preserve output, and reset once before retrying.
- **Callback failure:** verify listener interface, route, payload architecture, and target egress.
- **Ambiguous privilege result:** run the identity command again inside the new context before branching.
