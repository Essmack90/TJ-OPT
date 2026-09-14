# Evidence and Clean Down

Capture proof as soon as a branch succeeds. Keep raw scans, requests, credentials, hashes, binaries, screenshots, and flags in the box workspace or private temporary loot. Do not copy secret values into the exam runbook.

## Fast loop

### Run this

~~~bash
date -Is | tee -a "$BoxDir/loot/timeline.txt"
find "$BoxDir/nmap" "$BoxDir/loot" -maxdepth 2 -type f -print 2>/dev/null | sort
sha256sum "$BoxDir"/nmap/* "$BoxDir"/loot/* 2>/dev/null | tee "$BoxDir/loot/evidence-sha256.txt"
shot nmap-services
shot foothold
shot privesc-finding
shot root-shell
boxdone
htblog
~~~

### Example output

~~~text
$Timestamp $Identity $Hostname
$BoxDir/loot/evidence-sha256.txt
~~~

### What did you get?

- [ ] Proof, hashes, timeline, and cleanup evidence are saved -> **Update the matching exam page and write-up route.**
- [ ] A listener, payload, task, service, or AD change remains -> **Reverse it, verify the rollback, then rerun the evidence block.**
- [ ] A required proof frame is missing -> **Reproduce only the final proof command and run the relevant `shot` command.**
- [ ] `boxdone` or `htblog` fails -> **Preserve the workspace and fix the helper state before closing the box.**

### Open next

The box is complete only after proof is private, target changes are reversed or recorded, and the runbook update is linked to the write-up.

## Evidence minimum

~~~bash
find "$BoxDir/nmap" "$BoxDir/loot" -maxdepth 2 -type f -print 2>/dev/null | sort
sha256sum "$BoxDir"/nmap/* "$BoxDir"/loot/* 2>/dev/null | tee "$BoxDir/loot/evidence-sha256.txt"
~~~

Capture the minimum proof set with the existing helper:

~~~bash
shot nmap-allports
shot nmap-services
shot foothold
shot privesc-finding
shot root-shell
~~~

For exam proof, include the identity, hostname, and required proof output in one frame. Use [[OSCP/REFERENCE CARDS/OSCP Habits - Screenshot & Loot|OSCP Screenshot and Loot habits]] for the exact helper conventions.

## Target cleanup

Remove only artifacts created during this run, using variables recorded in the timeline:

~~~bash
ssh "$Username@$BoxIP" "rm -f '$RemoteArtifact'"
~~~

On Windows, remove only the recorded payload, task, service, or output file:

~~~powershell
Remove-Item -Force "$RemoteArtifact"
~~~

For AD, reverse every controlled change and verify it:

~~~bash
bloodyAD --help
netexec ldap "$DCIP" -u "$Username" -p "$Password" -d "$Domain"
~~~

Use [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux Clean Down]], [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows Clean Down]], or [[OSCP/RUNBOOK V2/AD - Clean Down|AD Clean Down]] for the exact rollback command.

## Close the box

~~~bash
date -Is | tee -a "$BoxDir/loot/timeline.txt"
boxdone
htblog
~~~

Do not claim closeout until the listener is stopped, target-side changes are reversed or recorded, the proof evidence is private, and the workspace path is known.

### Shocker evidence boundary

For a CGI callback route, retain the full Nmap and Gobuster outputs, the harmless identity response, the listener connection, the sudo rule, and the root identity proof in the private workspace. If no target-side payload file was created, record that explicitly. Keep flag values and any flag-containing screenshot outside the vault.

See [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] and [[OSCP/RUNBOOK V2/Linux - Shellshock CGI|Linux Shellshock CGI]].

## Update the runbook

After the box, add the successful branch, the one decisive output clue, and any tool-specific gotcha to the appropriate exam page. Link the write-up, detailed RUNBOOK V2 stage, module, decision tree, and modern-tooling note. Keep the stripped-down page command-first.

## Related references

- [[OSCP/RUNBOOK V2/00 - Follow-Along Controller|RUNBOOK V2 Controller]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux Clean Down]]
- [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows Clean Down]]
- [[OSCP/RUNBOOK V2/AD - Clean Down|AD Clean Down]]
- [[OSCP/OSCP COMMAND MASTER CHEATSHEET|Command Master Cheatsheet]]
