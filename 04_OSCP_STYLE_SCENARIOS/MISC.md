## QUICK REFERENCE - COMMON PATHS TO ROOT
```
| Initial Access | Privesc Method | Success Rate | Time |
|----------------|----------------|--------------|------|
| www-data | SUID binary | High | 15min |
| Low-priv user | Sudo misconfig | High | 10min |
| Web shell | Kernel exploit | Medium | 30min |
| Database access | UDF/RCE | Medium | 45min |
| FTP access | SSH key in files | High | 20min |
| SMB share | Cron job abuse | High | 30min |
| NFS mount | SSH key injection | High | 15min |
| Tomcat | WAR deployment | High | 20min |
| Redis | SSH key write | High | 15min |
| Jenkins | Script console | High | 15min |
```

## THE OSCP FORMULA
```
# Every box follows this pattern:
1. ENUMERATE (find the door)
2. EXPLOIT (open the door)
3. ENUMERATE AGAIN (find the next door)
4. PRIVESC (get to the top)
5. LOOT (get the flags)

# If stuck for >30 minutes:
1. Rerun enumeration (you missed something)
2. Check different service (web not working? try SMB)
3. Try default credentials (admin:admin, root:root)
4. Read writeups (for practice boxes, not exam)
5. Take a break (walk away, come back fresh)
```

| Scenario | Initial Vector | Privesc Method | Difficulty |
|----------|----------------|----------------|------------|
| SUID Find | Web shell | SUID binary | Easy |
| SMB Anonymous | SMB share | SSH key + sudo | Easy |
| SQLi to SYSTEM | SQL injection | JuicyPotato | Medium |
| Kerberoasting | Domain user | DCSync | Hard |
| File Upload | Web upload | Content-Type bypass | Easy |
| NFS no_root_squash | NFS export | SSH key injection | Easy |
| WordPress | Plugin vuln | Docker escape | Medium |
| AlwaysInstallElevated | Low-priv shell | MSI installer | Easy |
| Tomcat Manager | Default creds | systemctl sudo | Medium |
| Redis Unauth | Redis | SSH key write | Easy |
| RPC to NFS | RPC | Backup file creds | Medium |
| X11 Forwarding | SSH -X | Keystroke capture | Medium |
| Tar Wildcard | Low-priv shell | Cron injection | Medium |
| JWT Tampering | Web API | Secret cracking | Medium |
| Log Poisoning | LFI | PATH hijack | Medium |
| SSH Pivot | Edge host | Internal network | Hard |
| Kernel Exploit | Low-priv shell | DirtyPipe | Easy |
| Cron Hijack | Web shell | World-writable cron | Easy |
| Memory Dump | Low-priv shell | Process memory | Medium |
| GraphQL | Web API | Introspection | Medium |
| WebDAV | Write access | Symlink attack | Medium |
| WebSocket | Web app | Token leakage | Medium |
| Pickle Deserialization | Cookie | RCE | Medium |
| Default Creds | Multiple services | Password reuse | Easy |

## OSCP EXAM SUCCESS FORMULA

```bash
# For EVERY box, run this sequence:

1. ENUMERATION PHASE (30-60 min)
   nmap -sC -sV -p- $TARGET
   gobuster dir -u http://$TARGET -w /usr/share/wordlists/dirb/common.txt
   enum4linux -a $TARGET
   smbclient -N -L //$TARGET
   nikto -h http://$TARGET

2. VULNERABILITY IDENTIFICATION (15-30 min)
   python3 vuln_scan.py --xml nmap.xml
   searchsploit $SERVICE $VERSION

3. EXPLOITATION (30-60 min)
   # Start with easiest: default creds, anonymous access
   # Then known exploits
   # Then manual enumeration

4. PRIVILEGE ESCALATION (30-60 min)
   python3 privesc_checklist.py --all
   # Check SUID, sudo -l, cron jobs, writable files

5. LOOT COLLECTION (15 min)
   python3 loot_parser.py --output loot.json
   find / -name "*.txt" 2>/dev/null | grep -E "user|root|flag|proof"

6. REPORTING (ongoing)
   python3 report_builder.py -t $TARGET --name "$NAME" --loot loot.json