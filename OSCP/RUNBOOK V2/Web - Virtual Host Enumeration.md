# Web - Virtual Host Enumeration

**Step 5A of 50 · Universal**

*Discover applications selected by the HTTP Host header, add a confirmed name locally, and enumerate the newly visible site.*

## When to use this page

Use this page when the web server returns the same placeholder for every path, the write-up mentions a hostname, or the service appears to route by virtual host. A virtual host is a separate website selected by the HTTP `Host` header even when all sites share one IP address.

## Find candidate hostnames

> **Why:** Gobuster sends each word as a Host header and `--append-domain` adds the supplied domain; look for responses whose status or size differs from the baseline.
```bash
gobuster vhost -u http://$BoxIP/ -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --domain $Domain --append-domain -o $BoxDir/nmap/vhosts.txt
```

## Add a confirmed host locally

> **Why:** This command maps the confirmed virtual-host name to the target IP so browsers and command-line tools send the expected Host header.
```bash
echo "$BoxIP $FQDN" | sudo tee -a /etc/hosts
```

## Re-enumerate the site

> **Why:** These requests verify that the new Host header returns a different application before you spend time on its paths and vulnerabilities.
```bash
curl -s -H "Host: $FQDN" http://$BoxIP/ | tee $BoxDir/loot/$FQDN-index.html
feroxbuster -u "http://$FQDN/" -w /usr/share/wordlists/dirb/common.txt -o $BoxDir/nmap/$FQDN-ferox.txt
```

## Example output

```text
Found: admin.$Domain (Status: 200) [Size: different]
```

## What did you get?

- [ ] A host returns a different status, size, or title → **Run `echo '$BoxIP $VHost' | sudo tee -a /etc/hosts`, run `curl -I http://$VHost/`, and go to Step 5 · [[Linux - Web Enum]] or Step 23 · [[Windows - Web Enum]]**
- [ ] Every candidate matches the baseline → **Treat vhost discovery as a dead end for this wordlist; return to Step 5 · [[Linux - Web Enum]] or Step 23 · [[Windows - Web Enum]]**
- [ ] The name resolves but the site is unchanged → **Run `curl -i -H 'Host: $VHost' http://$BoxIP/` and `curl -ik -H 'Host: $VHost' https://$BoxIP/`, then compare the titles again**

## Notes

Use `$Domain` and `$FQDN` only after they are confirmed from the service scan, certificate, DNS, or application content. Do not add speculative names permanently to `/etc/hosts`.

## Gotcha

> [!warning] 💡
> A `200` response alone is not a hit because many servers return the same default page for unknown hosts. Compare response size, title, redirects, and body content with the baseline.

## Additional routing

- [ ] A distinct virtual host is confirmed → **Re-enumerate it through Step 5 · [[Linux - Web Enum]] or Step 23 · [[Windows - Web Enum]]**
- [ ] No distinct host is found → **Return to the originating web-enumeration stage and continue with paths and versions**
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
