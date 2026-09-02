# Inveigh

Windows-native LLMNR/NBT-NS poisoning tool. The PowerShell equivalent of Responder: runs on a compromised Windows host to capture NTLMv2 challenge-responses from the local network segment without needing Kali connectivity.

Cross-links: [[23. Attacking Active Directory Authentication|AD.3]], [[Active Directory (Breakdowns)]]

---

## What problem it solves

Responder requires a Kali machine on the target network. If you have a Windows foothold but Kali isn't on the segment (or you haven't set up a pivot yet), Inveigh poisons LLMNR and NetBIOS-NS from that Windows host directly. Same protocol, same captured hashes, different platform.

## Install

```powershell
# Download Inveigh.ps1 from GitHub
# https://github.com/Kevin-Robertson/Inveigh

# No install needed — just import and run
Import-Module .\Inveigh.ps1
```

## Usage

```powershell
# Start poisoning: -NBNS Y adds NetBIOS-NS poisoning on top of LLMNR
Invoke-Inveigh Y -NBNS Y -ConsoleOutput Y -FileOutput Y
# Ctrl+C to stop

# Read captured hashes from the log file
type Inveigh-NTLMv2.txt
```

Crack on Kali:
```bash
hashcat -m 5600 inveigh_hashes.txt /usr/share/wordlists/rockyou.txt
```

## Caveats

- Requires local admin on the Windows host to bind to ports 80/445/5355.
- Script-block logging (PowerShell event 4104) captures the import and invocation, consider `-ExecutionPolicy Bypass` or the C# `InveighZero` variant for operational security.
- Only poisons the network segment the Windows host is on. If the target subnet is segmented, you won't capture hashes from other subnets.
- Same LLMNR poisoning detection rules apply, blue team running Responder/Inveigh-detection scripts will see the fake responses.

#### Tags: #ModernTooling #Inveigh #LLMNR #NBTNS #NTLMv2 #WindowsPoison #ActiveDirectory #HTBSupplementary
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Inveigh supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Inveigh is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
inveigh --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
