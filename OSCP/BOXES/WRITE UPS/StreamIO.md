# StreamIO

## Scope

- Platform: HackTheBox
- OS: Windows Server / Active Directory
- Target: StreamIO

## Entry vector

The initial web service was an IIS-hosted StreamIO application. A second HTTPS
virtual host exposed a movie-search endpoint. The search input was vulnerable
to boolean-based SQL injection, which allowed the application database's
`users` table and password hashes to be enumerated. Cracking a recovered
application credential provided the first authenticated web access.

## Web application chain

The authenticated admin area exposed an include parameter. `php://filter` was
used to read PHP source safely and identify the vulnerable evaluation path.
An attacker-controlled PHP file supplied through the remote-include path gave
command execution in the web application's context.

## Database and lateral movement

The recovered PHP source disclosed the MSSQL connection details. SQLCMD was
used through the application execution path to enumerate databases and locate
the backup application's user data. A second credential recovered from that
data enabled the next Windows account context.

## Browser credential recovery

Host enumeration identified a Firefox profile. The profile's `logins.json`,
`key4.db`, and `cert9.db` were copied for offline review and decoded with a
local NSS password reader. The recovered account was then used for directory
authorization checks.

## Active Directory escalation

BloodHound and LDAP were used to validate the account-control relationship to
the Core Staff group. The account's control over the group was converted into
membership, and the resulting group permission on the domain controller was
confirmed as `ReadLAPSPassword`. LDAP then returned the local Administrator
password from the LAPS attribute. The Administrator WinRM session provided the
privileged proof.

## Evidence and cleanup

Keep the original scan, web source, SQL enumeration, BloodHound collection, and
LDAP output in the box loot directory. Do not store passwords, hashes, or flag
values in this write-up. Temporary group membership and ACL changes were
reverted after verification.
