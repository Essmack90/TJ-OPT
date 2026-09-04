# Linux - CMS Check
*Identify the CMS and check its version, plugins, and themes for a direct path.*

## Run this

**Step 6 of 50 · Linux**

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s http://$BoxIP/ | tee $BoxDir/loot/index.html
wpscan --url http://$BoxIP/ --enumerate ap,at,u
droopescan scan --url http://$BoxIP/
curl -s http://$BoxIP/ | grep -iE 'version|generator|wordpress|joomla|drupal|zenphoto'
```

## Example output

 > *Example shape only: the droopescan command is not yet verified against a real box.*
```
[+] WordPress detected
[+] Version: 6.x
[+] Interesting plugin: example-plugin
...
```
## What did you get?

- [ ] A known CMS CVE is found → **Go to Step 10 · [[Linux - Exploit Search]]**
- [ ] An outdated plugin or component is found → **Go to Step 10 · [[Linux - Exploit Search]]**
- [ ] Default credentials are possible → **Submit the documented default username and password once, then go to Step 10 · [[Linux - Exploit Search]] if the login succeeds**
- [ ] Nibbleblog 4.0.3 is identified → **Use the authenticated `my_image` plugin request from Step 10 · [[Linux - Exploit Search]] and trigger `/content/private/plugins/my_image/image.php` after upload**
- [ ] No CMS path is confirmed → **Return to Step 5 · [[Linux - Web Enum]]**

## Notes

The scanner must match the CMS. Do not run WPScan against a non-WordPress application.

## Gotcha

> [!warning] 💡
> Some scanner combinations are not directly demonstrated in the current box write-ups. Confirm the exact scanner options before exam use.

> [!warning]
> Command not yet verified against a real box. Confirm the exact `droopescan` command and scanner options before relying on this in an exam.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Zenphoto|Zenphoto]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- Nibbleblog 4.0.3 README and My Image plugin upload
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- OpenNetAdmin 18.1.1 version identification
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- WhatWeb confirmed the Magento CMS and legacy installation layout

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
