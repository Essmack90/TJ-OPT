# Linux - CMS Check
*Identify the CMS and check its version, plugins, and themes for a direct path.*

## Run this

**Step 6 of 50 · Linux**

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
- [ ] Default credentials are possible → **Test them, then go to credential validation**
- [ ] No CMS path is confirmed → **Return to Step 5 · [[Linux - Web Enum]]**

## Notes

The scanner must match the CMS. Do not run WPScan against a non-WordPress application.

## Gotcha

> [!warning] 💡
> Some scanner combinations are not directly demonstrated in the current box write-ups. Confirm the exact scanner options before exam use.

> [!warning]
> Command not yet verified against a real box. Confirm the exact `droopescan` command and scanner options before relying on this in an exam.
