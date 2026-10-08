# Manager

- **Platform:** Hack The Box
- **OS:** Windows — Active Directory and AD CS
- **Difficulty:** Medium

## Entry vector

RID cycling exposed the domain users. A username-equals-password spray produced a valid domain account, which provided Windows-authenticated access to MSSQL. `xp_dirtree` enumerated the IIS web root and exposed a downloadable website backup. The backup configuration contained a domain credential that enabled WinRM access as Raven.

## Privilege escalation

Certipy enumeration identified an ESC7 condition: Raven had ManageCA on the `manager-DC01-CA`. The CA was configured to allow the SubCA template, but Raven initially lacked the certificate-manager bit needed to approve requests. After adding the officer permission in the CA security descriptor, a SubCA request for the Administrator UPN could be approved and retrieved. Certificate authentication yielded Administrator access, completing the pass-the-hash path.

## Kill chain

1. Anonymous/RID user enumeration
2. Username-equals-password spray
3. MSSQL Windows authentication and `xp_dirtree`
4. IIS backup download and configuration credential recovery
5. WinRM foothold
6. AD CS ESC7 ManageCA abuse
7. Administrator certificate authentication and pass-the-hash

## Notes

- Keep credentials and flag values out of shared write-ups.
- The CA ACL change is part of the box-state mutation and may require a reset to restore the original challenge state.
