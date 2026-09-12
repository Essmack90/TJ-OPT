# Exam Runbook Controller

Use this page for every exam-style box. It is deliberately short: initialise the workspace, run recon, select one branch, record proof, and close cleanly.

## Fast loop

### Run this

~~~bash
boxstart "$BoxName" "$BoxIP" "$Provider"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset SSHPort 22
boxset Lport 4444
printf 'Target=%s Local=%s Workspace=%s\n' "$BoxIP" "$LocalIP" "$BoxDir"
~~~

### Example output

~~~text
Target=$BoxIP Local=$LocalIP Workspace=$BoxDir
~~~

### What did you get?

- [ ] Target, VPN address, and workspace are populated -> **Open [[OSCP/EXAM RUNBOOK/01 - Recon and Triage|Recon and Triage]].**
- [ ] Any value is empty -> **Fix the VPN or `boxstart` state, then run this block again.**
- [ ] The box is already loaded in another terminal -> **Run `boxload`, confirm the variables, then open recon.**

### Open next

Do not choose an exploit from the description. The next page is [[OSCP/EXAM RUNBOOK/01 - Recon and Triage|Recon and Triage]].

## 0. Initialise

Set `BoxName`, `BoxIP`, and `Provider` in the shell before running this block. For a manual run, use the normal helper workspace. For an agent run, keep the workspace under the private temporary directory defined in [[OSCP/RUNBOOK V2/00 - Follow-Along Controller|RUNBOOK V2 Controller]].

~~~bash
boxstart "$BoxName" "$BoxIP" "$Provider"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset SSHPort 22
boxset Lport 4444
~~~

## 1. Recon

Open [[OSCP/EXAM RUNBOOK/01 - Recon and Triage|Recon and Triage]]. Do not start exploitation until the service list is saved.

## 2. Select the branch

| Finding | Open next |
|---|---|
| HTTP or HTTPS | [[OSCP/EXAM RUNBOOK/02 - Web and Services\|Web and Services]] |
| Linux service set or SSH foothold | [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path\|Linux Fast Path]] |
| Windows service set or Windows shell | [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path\|Windows Fast Path]] |
| LDAP, Kerberos, SMB domain clues, or supplied domain credentials | [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path\|Active Directory Fast Path]] |
| Multiple branches | [[OSCP/EXAM RUNBOOK/07 - Branch Matrix\|Branch Matrix]] |

## 3. Proof loop

After every meaningful result:

~~~bash
date -Is | tee -a "$BoxDir/loot/timeline.txt"
hostname 2>/dev/null | tee -a "$BoxDir/loot/timeline.txt"
~~~

Record the exact command, output file, credential source, shell identity, and next branch. Keep secret values in private loot only.

## 4. Closeout

Open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]] after proof collection. Do not leave listeners, uploaded files, modified scheduled tasks, or AD delegation changes behind.

## Links

- Detailed controller: [[OSCP/RUNBOOK V2/00 - Follow-Along Controller|RUNBOOK V2 Controller]]
- Output interpretation: [[OSCP/RUNBOOK V2/How to Read Output|How to Read Output]]
- Exploit editing: [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing and Resource Guide]]
