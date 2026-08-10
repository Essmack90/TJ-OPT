# Client-Side Attacks, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Windows library file mechanics and `.lnk` payload tricks from [[Client-Side Attacks]]. See that page for the entry format.

---

## Why a Windows library file's tags aren't arbitrary strings

**The tags that look like they should just be labels:**
```xml
<name>@windows.storage.dll,-34582</name>
<iconReference>imageres.dll,-1003</iconReference>
<templateInfo>
<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
</templateInfo>
```

**Piece by piece:**
- `<name>@windows.storage.dll,-34582</name>` → this isn't a free-text name field. It's a **DLL + string-resource-index reference**, the `@` prefix and comma-separated negative index is Windows' standard indirect-string format (`@dllname,-resourceID`), used all over the OS wherever a UI label needs to be localized rather than hardcoded. `-34582` points at whatever localized string Microsoft shipped at that index inside `windows.storage.dll`. `@shell32.dll,-34575` is the other commonly-cited option for the same purpose, chosen against here specifically because a text-based filter scanning attachment contents for the literal substring "shell32" would flag it, `windows.storage.dll` doesn't carry that same red flag.
- `<iconReference>imageres.dll,-1003</iconReference>` → same indirect-reference format, no `@` prefix this time (icon references and string references use slightly different syntax within the same schema). `imageres.dll` ships hundreds of Windows' built-in icons, `-1002` and `-1003` happen to be the Documents and Pictures folder icons respectively. Nothing here is guessable without Microsoft's own resource-index documentation, they're arbitrary numeric offsets into a compiled binary's resource table.
- `<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>` → a GUID from Windows' `KNOWNFOLDERID` enumeration, identifies which built-in folder "template" (which columns/sort order Explorer shows by default) this library should mimic. This specific GUID is the Documents folder type. Every other built-in folder type (Pictures, Music, Videos, Generic) has its own fixed GUID in the same enum, picking the wrong one doesn't break functionality, it just makes the fake library look subtly "off" to a target who's used to how their own folders normally look.

**Where this comes from:** [Microsoft's Library Description Schema reference](https://learn.microsoft.com/en-us/windows/win32/shell/library-schema-entry) documents the overall three-part structure, the [`name` element page](https://learn.microsoft.com/en-us/windows/win32/shell/schema-library-name) documents the indirect-string format specifically, and the [`KNOWNFOLDERID` reference](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid) has the full GUID list for swapping in a different folder type.

**Where to look in the response:** none of this is discoverable by trial and error from the XML alone, the tag names give no hint that their values are DLL-resource lookups rather than plain strings. Reach for the schema docs directly rather than guessing at value formats.

🔁 **Seen in:** [[Client-Side Attacks#Step 2: Build the Windows library file's XML|Client-Side Attacks, 12.3.1 Step 2]].

#### Tags: #WindowsLibraryFiles #LibraryMs #XML #IndirectStringReference #CommandBreakdowns

---

## The 255-vs-4096 character gap in a `.lnk` shortcut's target field

**What a target field looks like once padded:**
```
powershell.exe -c "IEX(...)" ; rem <long boring benign-looking padding text past character 255>
```

**Piece by piece:**
- Windows Explorer's shortcut **Properties** dialog only *displays* the first ~255 characters of the "Target" field, a UI limitation carried over from the original `.lnk` binary format's legacy path-length assumptions.
- The actual underlying target field a `.lnk` file can store is much larger, up to 4096 characters, Explorer just doesn't render past the display limit in that one dialog.
- Padding the real (malicious) command with a delimiter (`;` on Windows, since `cmd`/PowerShell both treat it as a command separator) followed by a long, boring, plausible-looking string pushes the real payload past character 255. Anyone who right-clicks the shortcut and checks Properties out of caution sees only the harmless-looking prefix or suffix, not the full 4096-character reality.
- This is a **UI-trust gap, not a technical bypass**: nothing about execution changes, the full string still runs exactly as written when double-clicked. It only defeats a *human* skimming Properties before running it, not any actual technical inspection (a `.lnk` parser reading the raw binary field would still see everything).

**Where this comes from:** general `.lnk` file format knowledge (well documented in malware-analysis writeups on LNK-based phishing campaigns), not a single canonical reference page, the practical takeaway (255 visible vs 4096 actual) is what matters, not a specific citation.

**Where to look in the response:** if reviewing a suspicious shortcut yourself, don't trust the Properties dialog's Target field at face value, use `Get-Content` on the raw `.lnk` binary or a dedicated `.lnk` parser to see the full stored target string.

🔁 **Seen in:** [[Client-Side Attacks#Step 4: Build the `.lnk` shortcut payload (the actual reverse-shell trigger)|Client-Side Attacks, 12.3.1 Step 4]].

#### Tags: #LNKShortcut #UITrustGap #SocialEngineering #CommandBreakdowns

---

## Why `.docx` silently kills a macro, and why testing live hides it

**The mistake, twice in a row:**
```
File → Save As → mymacro.docx (default format, left unchanged)
```
followed by building/testing the macro in that same still-open Word session, seeing it fire correctly, and concluding the file works.

**Piece by piece:**
- `.docx` (and the older `.doc`'s modern sibling formats generally) is Microsoft's **Open XML** format, and as a deliberate security measure, Word **will not save VBA project content into a plain `.docx` container at all**. There's no error, no warning dialog, no truncation message, the save operation just succeeds and quietly omits the macro. The saved file on disk ends up indistinguishable from a document that never had a macro to begin with.
- `.doc` (legacy binary format) and `.docm` (the XML-based "macro-enabled" variant) are the two formats that actually have a defined place in their structure to store VBA project data. Saving to either of those persists the macro correctly.
- **Why testing live doesn't catch this:** a macro that's already loaded into Word's current in-memory VBA project (because you just wrote/edited it in the VBA editor) keeps running from that in-memory state for the rest of the session, completely independent of what did or didn't get written to disk on the last save. `AutoOpen`/`Document_Open` firing correctly *right after you built it* only proves the macro works as code, it proves nothing about whether the **saved file** actually contains it. The only test that actually proves persistence: fully close the Word application (not just the document window, the whole `WINWORD.EXE` process), then reopen the file fresh from disk. If it still fires after that, the save genuinely worked.

**Where this comes from:** documented Office behavior (Microsoft's own file-format documentation on `.docx` vs `.docm`), reinforced here by hitting the exact same mistake twice, undetected both times, specifically because the live-session test gave a false positive.

**Where to look in the response:** there's no HTTP response or terminal output that reveals this, the failure is entirely silent at save time. The only reliable signal is a listener staying quiet after a genuinely cold reopen of the delivered file, treat that specifically (not just "nothing happened when I clicked it once") as the trigger to go check the file's actual saved extension before chasing any other theory (network, VM state, watcher-script behavior, etc).

🔁 **Seen in:** [[Client-Side Attacks#Lab 2 (VM #2, TICKETS): delivering the macro to a simulated user|Client-Side Attacks, 12.2.3 Lab 2]], the correction note.

#### Tags: #WordMacros #DocVsDocx #MacroPersistence #FalsePositiveTesting #CommandBreakdowns

---

## **Outstanding**
- [ ] CVE-2025-24054/24071 (NTLM leak via `.library-ms` UNC path, no `.lnk` needed) internals, once actually exercised hands-on rather than just referenced.
