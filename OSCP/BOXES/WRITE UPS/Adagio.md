# Adagio

- **Box:** Adagio
- **Operating system:** Windows Active Directory
- **Status:** Complete

## Entry vector

AS-REP roasting exposed an account with Kerberos pre-authentication disabled. The roastable account was cracked offline and used to obtain the initial `jparsons` foothold over WinRM.

## Lateral movement

An exposed development credential led to a bounded spray against the domain. The reused credential identified `rsamal`, which became the sacrificial account for the delegation path.

## Privilege escalation

ACL review showed that `swalker` had `GenericWrite` over the domain controller computer object (`DC$`). The standard machine-account RBCD path was not available, and a normal S4U flow with the SPN-less user was not forwardable.

The working path was SPN-less RBCD/U2U: configure resource-based constrained delegation, obtain an RC4 TGT for the sacrificial account, extract the TGT session key, temporarily use that key as the account's NT hash, and request U2U S4U2Self/S4U2Proxy material while impersonating Administrator. The resulting service ticket provided access to the domain controller as the privileged user.

## Cleanup and reset note

Temporary delegation entries, SPNs, and shadow credentials were removed. The `rsamal`, `swalker`, and `rnolan` passwords were changed during testing. Their original values could not be restored because of password history, so the box now requires a reset before those original account states can be recovered.
