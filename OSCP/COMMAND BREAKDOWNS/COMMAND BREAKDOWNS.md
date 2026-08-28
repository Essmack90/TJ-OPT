# Command Breakdowns

The other hub docs tell you *what* to run. This one explains *why it works*, piece by piece, and where you'd actually go find the pieces yourself if you were staring at a target with no note to copy from.

Not a syntax reference like [[COMMAND APPENDIX]], not phase-ordered like [[METHODOLOGY CHEAT SHEET]], not symptom-ordered like [[DECISION TREE]]. This is the "explain it like I've never seen this before" layer underneath all three. When a command looks like line noise (nested subqueries, weird hex encoding, chained pipes), it gets a full teardown here.

Split into one file per area, same categories as the module topics, so it grows alongside the vault instead of becoming one giant unreadable file.

## Areas

- [[SQL Injection (Breakdowns)|SQL Injection]] — error-based extraction, UNION payloads, blind SQLi logic, `LOAD_FILE`/`INTO OUTFILE`, MSSQL `xp_cmdshell`, sqlmap internals, `xp_dirtree` UNC hash coercion, `EXECUTE...AT` linked server nested `''` quoting.
- [[File Inclusion & Traversal (Breakdowns)|File Inclusion & Traversal]] — `--path-as-is` traversal, encoding bypasses, PHP wrappers, null-byte tricks, mechanical secret extraction.
- [[Shells & Payloads (Breakdowns)|Shells & Payloads]] — CMD/PowerShell polyglots, shell-wrapping gotchas, encoding requirements, mkfifo bind shell named-pipe loop mechanics.
- [[Antivirus Evasion (Breakdowns)|Antivirus Evasion]] — PowerShell AV-bypass flag semantics, staged vs stageless payload mechanics, wine32/Wine prefix requirements for Shellter.
- [[Web Applications (Breakdowns)|Web Applications]] — WordPress XSS-to-admin chains, mass assignment, plugin metadata abuse; ffuf two-step filtering + -ac auto-calibrate + -mr regex match teardown.
- [[Reconnaissance & Enumeration (Breakdowns)|Reconnaissance & Enumeration]] — output-wrangling tricks (negative grep, greppable-format parsing, LOLBAS port scanning).
- [[Privilege Escalation & Local Exploitation (Breakdowns)|Privilege Escalation & Local Exploitation]] — cron glob gotchas, LOLBAS downloaders, JuicyPotato/CLSID mechanics. (No matching [[COMMAND APPENDIX]] area yet, standing in until the Privesc modules are formally covered.)
- [[Phishing (Breakdowns)|Phishing]] — why `wget` can't clone JS-driven pages, BeautifulSoup vs raw string-replace fragility, the `127.0.0.1`-breaks-cross-machine gotcha.
- [[Client-Side Attacks (Breakdowns)|Client-Side Attacks]] — Windows library file XML tag semantics (DLL-resource indirect references), the 255-vs-4096 character `.lnk` Properties-hiding gap.
- [[Locating Public Exploits (Breakdowns)|Locating Public Exploits]] — Apache JAMES directory-traversal-to-`bash_completion.d` RCE, patching a hardcoded exploit port before running it.
- [[Fixing Exploits (Breakdowns)|Fixing Exploits]] — why cross-compiled Windows exploits need `-lws2_32`, mechanical shellcode-from-file swaps.
- [[Buffer Overflow & Memory Corruption (Breakdowns)|Buffer Overflow & Memory Corruption]] — the Sync Breeze off-by-one `malloc`/`strcat` bug, SEH pop/pop/ret redirect mechanics, why a target crash after an uncaught payload is a good sign not a bad one.
- [[File Upload Attacks (Breakdowns)|File Upload Attacks]] — filename-based shell metacharacter injection (elFinder CVE-2019-9194).
- [[Password Attacks (Breakdowns)|Password Attacks]] — Hydra http-post-form three-field syntax, Mimikatz privilege chain (why SeDebugPrivilege → token::elevate → lsadump::sam and the Server 2022 schtask workaround), PowerShell -enc UTF-16LE encoding requirement, memssp SSPI-layer intercept timing, UNC filename injection via Go's filepath.Join on Windows, Hashcat mask attack character-class placeholders (-a 3), BitLocker VHD chain (losetup + dislocker + mount, why three tools).
- [[Pivoting & Tunneling (Breakdowns)|Pivoting & Tunneling]] — Socat -ddd/fork flag mechanics, SSH remote dynamic single-socket -R argument (OpenSSH 7.6+ client required), Plink echo-y pipe trick for non-TTY host key acceptance, nmap -sT/-Pn/-n trio requirement through proxychains (LD_PRELOAD hooking limitation), PTY upgrade before SSH from a reverse shell (isatty() gate and StrictHostKeyChecking caveat), Meterpreter autoroute + socks_proxy chain (why it replaces SSH -D, VERSION 4a vs socks5, traffic path), ptunnel-ng static build (autogen.sh sed patch, LDFLAGS=-static, why static linking for pivot host transfer).

- [[Active Directory (Breakdowns)]] — PSCredential chain for multi-hop ACL abuse (ConvertTo-SecureString/New-Object PSCredential/-Credential context), Set-DomainObject SPN for targeted Kerberoast (why any valid SPN string works, cleanup required), ExtraSids Rubeus golden /sids: flag (why WITHIN_FOREST trusts don't filter ExtraSids, /rc4 vs /aes256, /ptt loading), dsquery LDAP filter for disabled admin accounts (1.2.840.113556.1.4.803 bitwise AND OID, UAC bit 2 = ACCOUNTDISABLE, adminCount >= 1 = SD Propagator marker), LDAPSearch function (DirectoryEntry + DirectorySearcher + samAccountType=805306368 filter — why not Get-ADUser, how to unravel nested group chains via properties.member, attribute hunting in properties.description), kerberos::golden silver ticket flags (/ptt vs .kirbi, /sid without RID, /target vs /domain, /service class matching, /rc4 = SPN account hash not krbtgt, /user arbitrary claim, why PAC validation rarely enforced — Module 23), lsadump::dcsync DRSUAPI mechanics (IDL_DRSGetNCChanges API, why no DC check on caller identity, required rights, krbtgt priority, aes256_hmac vs NTLM for SIEM noise — Module 23), sekurlsa::pth (NTLM-hash-as-credential for new process, /run:powershell, local vs network auth token scope difference — Module 23), New-CimSession -Protocol DCOM + Invoke-CimMethod Win32_Process.Create (why DCOM vs WSMAN, Session 0 spawn, ReturnValue=0 success signal — Module 24), vshadow.exe -nw -p + copy GLOBALROOT device path chain (why -nw skips writers, -p keeps copy alive, GLOBALROOT device namespace bypasses file lock, Boot Key in SYSTEM hive required for secretsdump LOCAL — Module 24)
- [[Metasploit Framework (Breakdowns)|Metasploit Framework]] — msfvenom flag semantics (staged vs non-staged slash/underscore distinction, -f format options), msfconsole -r resource script launch, multi/handler advanced options (AutoRunScript/ExitOnSession/run -z -j), getsystem technique breakdown (Named Pipe Impersonation/token duplication, required privileges), migrate PID (privilege rule: can't migrate up), execute -H -f notepad (hidden process spawning), load kiwi + creds_msv (LSASS MSV1_0 dump, NTLM hash format for PtH), autoroute (subnet discovery from routing table, bind_tcp requirement for second-hop), portfwd add -l/-p/-r flags, set SSL false (wrong-version-number NiFi/HTTPS gotcha)
- [[Cloud Enumeration (Breakdowns)|Cloud Enumeration]] — `describe-snapshots --query "Snapshots[?VolumeSize==\`1\`]"` JMESPath backtick literal semantics (string vs number comparison), jq `.UserDetailList[]` with `// []` null-safe fallback (why GroupList is a plain string array not objects), `aws s3 cp s3://... -` stdout destination + `2>/dev/null || echo "not found"` loop pattern, `curl -H "Host:"` virtual host bypass for hitting EC2 IP directly without DNS config, `aws configure set aws_session_token` for writing temp credentials without re-running interactive configure

---

## Entry format

Every breakdown in every area file follows this shape:

```markdown
## <Plain-English name for the technique>

**Full command:**
​```bash
<the actual command, copy-pasted from the box it was used on>
​```

**Piece by piece:**
- `<fragment>` → <why this fragment exists, what happens if you remove it, what it exploits>
- `<fragment>` → <...>

**Where this comes from:** <which reference site/page/section teaches this pattern, specifically enough to find it again, not just "check HackTricks">

**Where to look in the response:** <exactly what part of the raw output/HTML/terminal you scan for, and what it looks like buried in the noise>

🔁 **Seen in:** [[<Module or Box note>#<heading>|<context>]]
```

**Why this shape:** a command is only useful if you know which part to change for a different target and which part is fixed grammar. "Piece by piece" answers that. "Where this comes from" and "where to look in the response" exist because the hardest part of OSCP isn't memorizing payloads, it's knowing *which page of which reference to open* and *which line of a huge response actually matters*, so both get called out explicitly rather than assumed.

#### Tags: #CommandBreakdowns #Methodology
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for payload troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
