# Support

- **Box:** Support
- **Operating system:** Windows Active Directory
- **Status:** Complete

## Entry vector

Anonymous SMB access exposed the `support-tools` share. `UserInfo.exe` was recovered from the archive and its .NET code revealed an XOR/base64-protected LDAP bind credential.

## Foothold

LDAP enumeration with the recovered bind account exposed the `support` user's plaintext password in the `info` attribute. That credential provided WinRM access as `support`.

## Privilege escalation

BloodHound showed the `Shared Support Accounts` group had `GenericAll` over `DC$`, and `support` was a member. With the domain's default MachineAccountQuota, a temporary machine account was created, RBCD was written on `DC$`, and standard S4U2Self/S4U2Proxy requested an Administrator service ticket. The ticket was used for privileged access and proof retrieval.

## Cleanup

The RBCD entry was removed and the temporary machine account was deleted. The temporary Kerberos cache, binary analysis files, credential extracts, flag captures, and other local transfer artifacts were removed or redacted from the run evidence.
