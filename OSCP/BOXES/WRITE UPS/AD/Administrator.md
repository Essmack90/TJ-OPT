# Administrator

**Platform:** Hack The Box  
**OS:** Windows / Active Directory  
**Status:** Complete  
**Target:** `administrator.htb` (target values kept in the box session)

## Kill chain stub

1. Enumerated the domain controller services and collected BloodHound data with the supplied Olivia account.
2. Followed the `GenericAll` edge from Olivia to Michael and changed Michael's password with the authorised ACL path.
3. Followed Michael's `ForceChangePassword` edge to Benjamin, reset Benjamin, and accessed the FTP share.
4. Downloaded `Backup.psafe3`, converted and cracked it offline, then reviewed the Password Safe entries without recording their values.
5. Validated the recovered Emily credential and accessed Emily's home directory for the user flag.
6. Used Emily's `GenericWrite` edge over Ethan to set a temporary SPN, request a targeted TGS, remove the SPN, and crack the ticket offline.
7. Used Ethan's domain replication privilege for a scoped DCSync and recovered the Administrator NTLM material.
8. Validated the LM:NT pass-the-hash workflow with Evil-WinRM and read the Administrator desktop flag.

## Evidence and lessons

- BloodHound relationship edges were the decision points; each password change was validated before moving on.
- Password Safe and Kerberos artefacts were kept offline and redacted from the run log.
- The local clock was seven hours behind the lab controller; the targeted Kerberos request used a bounded, local time wrapper rather than changing system time.
- Preserve LM:NT formatting when moving from DCSync output to PsExec or Evil-WinRM.

## Follow-up

- Re-run the chain without the guided questions and write the exact BloodHound queries used for each edge.
- Add a detection note for password resets, temporary SPNs, DCSync, and pass-the-hash authentication.
