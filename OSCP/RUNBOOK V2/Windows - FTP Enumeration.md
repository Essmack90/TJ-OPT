# Windows - FTP Enumeration

**Windows standalone supplement**

Anonymous FTP can expose more than a normal upload folder. Treat the FTP root as a possible view of the Windows filesystem.

## Run this

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

- **Windows paths are visible:** inspect application data under `ProgramData`.
- **Only a small folder is visible:** list files and look for backups, exports, or configuration files.

## Run this

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

