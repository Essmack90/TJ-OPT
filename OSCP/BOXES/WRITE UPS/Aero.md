# Aero

- **OS:** Windows 11 standalone (21H2 / build 22000)
- **Entry vector:** CVE-2023-38146 (ThemeBleed). A malicious `.theme` file references an attacker-controlled SMB share; the three-stage ThemeBleed exchange loads a callback DLL and provides command execution as the low-privileged web user.
- **Privilege escalation:** CVE-2023-28252 (CLFS). The existing CLFS proof of concept required the build-specific token offset for Windows 11 build 22000 and a target-compatible statically linked binary. Running it from the initial foothold changed the process token to SYSTEM.

## Evidence chain

1. Enumerate the exposed HTTP service and identify the Aero Theme Hub upload form.
2. Host ThemeBleed stages over SMB and upload a `.theme` pointing to the share.
3. Use one-shot PowerShell execution for reliable evidence collection and artifact staging.
4. Confirm the target build, adapt/compile the CLFS PoC for the build, and execute it.
5. Remove dropped binaries and temporary files from the target after proof collection.

## Notes

- Keep the SMB stage server anonymous and scoped to the authorized target only.
- MinGW's C++ runtime must be linked statically when the target does not have the runtime DLLs.
- The token offset is version-dependent; validate the exact Windows build before running the PoC.
