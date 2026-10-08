# Intelligence

- **Platform:** Hack The Box
- **OS:** Windows / Active Directory
- **Difficulty:** Medium

## Entry vector

Enumerate the date-based PDF upload names on the web service. Download the documents and inspect their PDF metadata with ExifTool to recover domain usernames. The PDF content exposes the organization’s default-user password pattern; validate it with a careful password spray.

## Foothold

Use the recovered domain credential to access the permitted Windows management surface and retrieve the initial user proof from the user profile.

## Lateral movement

Read the IT share and inspect the scheduled PowerShell monitor. It makes authenticated web requests to hostnames found in the AD-integrated DNS zone. Add a controlled DNS A record pointing at the assessment host, then capture the resulting NTLMv2 challenge/response with Responder. Crack the capture offline and use the recovered account for the next directory query.

## Privilege escalation

The recovered account can read a group Managed Service Account secret. Extract the gMSA NT hash, inspect its constrained-delegation target, and use S4U delegation to obtain an Administrator service ticket. Access the DC with the ticket and collect privileged proof.

## Notes

- Keep captured hashes, passwords, tickets, and flags out of shared notes.
- Remove temporary DNS records, listeners, tickets, and local loot after the run.
