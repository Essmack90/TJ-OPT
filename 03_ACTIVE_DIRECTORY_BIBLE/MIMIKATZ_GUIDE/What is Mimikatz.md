Mimikatz is a post-exploitation tool that extracts plaintext passwords, hashes, PINs, and Kerberos tickets from Windows memory. Created by Benjamin Delpy (@gentilkiwi). It's the SINGLE MOST IMPORTANT tool for AD post-exploitation.

**WARNING for OSCP:** Mimikatz often triggers AV/EDR. You need to know how to bypass or use alternatives.

---

## SECTION 1: DOWNLOAD & SETUP

### Downloading Mimikatz

```bash
# On Kali (already installed)
locate mimikatz
# /usr/share/windows-resources/mimikatz/

# Or download latest
cd ~/oscp/tools/
wget https://github.com/gentilkiwi/mimikatz/releases/download/2.2.0-20220919/mimikatz_trunk.zip
unzip mimikatz_trunk.zip
cd mimikatz_trunk/x64/

# Files you need:
# mimikatz.exe - 64-bit version (use this most of the time)
# mimikatz_x86.exe - 32-bit version