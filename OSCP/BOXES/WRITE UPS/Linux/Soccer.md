# Soccer

- **OS:** Linux (NGINX, Express/WebSockets, MySQL, Tiny File Manager)
- **Entry vector:** Directory enumeration exposed Tiny File Manager. Its default administrative credential opened an authenticated upload boundary; the public `soc-player` vhost exposed a ticket checker over WebSockets.
- **Credential transition:** The numeric WebSocket ticket identifier was boolean-SQL-injectable. A bounded extractor recovered the player account credential, which was validated over SSH.
- **Privilege escalation:** `/usr/local/bin/doas` permitted passwordless `/usr/bin/dstat`, and `/usr/local/share/dstat` was writable by the player group. A temporary Python dstat plugin created a privileged shell proof.
- **Flags:** User and root flags were submitted on HTB; values intentionally omitted.
- **Cleanup:** Removed the temporary dstat plugin and SUID shell from the target; local credential material and flag files are removed after submission.
