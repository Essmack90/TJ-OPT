# Linux - FTP Enumeration

**Step 3A of 50 · Linux**

*Test anonymous FTP, list and download exposed files, and distinguish an empty service from a blocked FTP data channel.*

## When to use this page

Use this page when the service scan identifies FTP on port 21. FTP has a control connection for commands and a separate data connection for directory listings and transfers, so authentication can succeed while listings still fail.

## Anonymous login and listing

> **Why:** This command tests the conventional anonymous account without sending a password; look for a directory listing or a clear permission error.
```bash
ftp $BoxIP
```

> **Why:** This non-interactive request checks whether the anonymous account can list the root directory; save any filenames for individual downloads.
```bash
curl -s ftp://$BoxIP/
```

## Download interesting files

> **Why:** This command downloads a discovered file into private loot so you can inspect backups and configuration without repeatedly querying the target.
```bash
curl -s -o $BoxDir/loot/ftp-file "ftp://$BoxIP/path/to/file"
```

## Data-channel troubleshooting

If login works but `ls` hangs, try passive mode first. Passive mode asks the server for a data port that your client connects to; active mode asks the server to connect back to you and is often blocked by a firewall.

> **Why:** This command enables passive mode and tests a listing through the client’s data connection; success means the server returned filenames.
```bash
lftp -e "set ftp:passive-mode true; cls -la; quit" ftp://anonymous:@$BoxIP
```

> **Why:** This verbose client output shows whether the control login succeeds and whether the negotiated passive data port is reachable; look for the server’s `227 Entering Passive Mode` response.
```bash
curl -v ftp://$BoxIP/ 2>&1 | sed -n '/< 220/,/< 226/p'
```

## Example output

```text
230 Login successful.
227 Entering Passive Mode (...)
550 Failed to open file.
```

## What did you get?

- [ ] Anonymous login and listing work → **Run `wget -m ftp://anonymous:@$BoxIP/ -P $BoxDir/loot/ftp`, inspect the downloaded files, then go to Step 17 · [[Linux - Credential Search]]**
- [ ] Login works but listing hangs → **Run `ftp -p $BoxIP`, enter the anonymous login, run `passive`, then run `ls`; if it still hangs, run `ip route get $BoxIP` and retry once**
- [ ] A file returns `550` → **Run `ls` to confirm the filename and `get $Filename`; if it returns `550` again, record the file as unreadable and try the next listed file**
- [ ] Anonymous access is denied → **Run `ftp $BoxIP` with the recovered username and password once; if it is rejected, return to Step 5 · [[Linux - Web Enum]]**
- [ ] No useful files are exposed → **Go to Step 10 · [[Linux - Exploit Search]]**

## Notes

FTP is a file-transfer protocol. Anonymous access is useful only when the server grants directory or file permissions; a successful banner alone is not a foothold.

## Gotcha

> [!warning] 💡
> Avoid brute-forcing FTP until anonymous access and the service version have been checked. Passive-mode failures can be caused by firewalls, NAT, or a server-side passive-port range.

## Additional routing

- [ ] Files are readable → **Inspect them for credentials and go to Step 17 · [[Linux - Credential Search]]**
- [ ] FTP exposes no useful data → **Return to Step 5 · [[Linux - Web Enum]] or Step 10 · [[Linux - Exploit Search]]**
## Seen in
- *(no write-up yet)*

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
