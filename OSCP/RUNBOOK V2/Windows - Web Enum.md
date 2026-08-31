je# Windows - Web Enum

**Step 23 of 50 · Windows**

*Find IIS paths, login pages, uploads, and version information.*

## Run this

```bash
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x html,txt,php -t 30 -o $BoxDir/nmap/ferox.txt
nikto -h http://$BoxIP/
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/ | tee $BoxDir/loot/index.html
```

## Example output

```

200  GET  /
301  GET  /admin  -> /admin/
200  GET  /upload.aspx
...
```
## What did you get?

- [ ] A login page is found → **Test default credentials (`admin:admin`, `admin:password`, `admin:<appname>`), log in, read all page source for username leaks (HTML comments), then continue down this list**
- [ ] An XML form is found in the app source → **Go to Step 24 · [[Windows - XXE]]**
- [ ] A file upload is found → **Follow the file-upload path**
- [ ] Interesting content or a version is found → **Go to Step 26 · [[Windows - Exploit Search]]**
- [ ] Nothing useful appears → **Go to Step 25 · [[Windows - SMB Enum]]**

## Notes

Read the page source as well as the rendered page.

## Gotcha

> [!warning] 💡
> A 403 response still proves that the path exists.
