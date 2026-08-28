---
tags: [oscp, runbook, close-out]
---

# Box Close-Out Checklist

*Run this before `boxdone`. In order. Every box.*

---

## 1. Screenshots

```bash
ls $BoxDir/screenshots/
```

- [ ] `box-started.png`
- [ ] `nmap-allports.png`
- [ ] `nmap-services.png`
- [ ] `foothold.png` — whoami + id + hostname in one frame
- [ ] `root-flag.png` — cat proof.txt visible
- [ ] `PROOF-$BoxName.png` — whoami + hostname + flag all in one frame

---

## 2. Loot

```bash
cat $BoxDir/loot/flags.txt
cat $BoxDir/loot/creds.txt
```

- [ ] Root flag in flags.txt
- [ ] User flag in flags.txt (if the box had one)
- [ ] Any creds found are in creds.txt

---

## 3. Log → Vault

```bash
cp $BoxDir/$BoxName.log ~/Documents/Obsidian/main-vault/OSCP/BOXES/BOX\ LOGS/$BoxName.log
```

- [ ] Log copied (no error)

---

## 4. Write-Up

- [ ] `OSCP/BOXES/WRITE UPS/<N>. $BoxName.md` exists and is complete
- [ ] Vault Update Checklist at the bottom of the write-up is filled in

---

## 5. Runbook Stage Notes

For every stage note you used this box:

- [ ] Stage note exists (create it now if not)
- [ ] Winning command row added to the table
- [ ] `box_sources:` frontmatter updated to include this box

---

## 6. Module Notes

For every module whose technique you used:

- [ ] Box added to `## 🎯 Related Boxes to Practice` with: name, platform, why relevant, wikilink

---

## 7. Master Index

```
OSCP/BOXES/MASTER BOX LIST.md
```

- [ ] Box row checked off `[x]`
- [ ] Completion row added to the completed boxes table

---

## 8. Master Index (Runbook)

```
OSCP/RUNBOOK/00 - Master Index.md
```

- [ ] Any new stage notes created this box are linked

---

## 9. FAQ

- [ ] Any wall-hit or non-obvious fix from this box added to `FAQ - Quick Answers.md`

---

## 10. boxdone

```bash
boxdone
```

---

*Done. Next box: `/boxes`*
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
