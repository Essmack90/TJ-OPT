---
tags: [module/file-transfers, encryption, openssl, aes, powershell, data-protection, level/beginner]
---

# Protected File Transfers - Beginner's Guide

## Why Encrypt File Transfers?

During penetration tests, you'll often handle sensitive data:

- User lists and credentials
- NTDS.dit files (domain password hashes)
- Network infrastructure details
- Active Directory information

**The Risk:** If this data is intercepted during transfer, it could be leaked.

**The Rule:** Always encrypt sensitive data before transferring it.

---

## IMPORTANT: Professional Responsibility

> "Unless specifically requested by a client, we do not recommend exfiltrating data such as Personally Identifiable Information (PII), financial data (i.e., credit card numbers), trade secrets, etc., from a client environment."

If you need to test Data Loss Prevention (DLP) controls:
- Create dummy data that mimics the real data
- Don't use actual customer information
- Get explicit written permission

**Data leakage during a penetration test could have severe consequences for the penetration tester, their company, and the client.**

---

## When to Encrypt

| Situation | Action |
|-----------|--------|
| Transferring credentials | ALWAYS encrypt |
| Exfiltrating enumeration data | Encrypt if sensitive |
| Downloading NTDS.dit | ALWAYS encrypt |
| Testing DLP controls | Use dummy data |
| Any data you wouldn't want public | Encrypt it |

---

## Method 1: Windows File Encryption with PowerShell

### The Invoke-AESEncryption Script

This PowerShell script encrypts files and strings using AES encryption.

### Download the Script

Save this as Invoke-AESEncryption.ps1:

function Invoke-AESEncryption {
    [CmdletBinding()]
    [OutputType([string])]
    Param
    (
        [Parameter(Mandatory = $true)]
        [ValidateSet('Encrypt', 'Decrypt')]
        [String]$Mode,

        [Parameter(Mandatory = $true)]
        [String]$Key,

        [Parameter(Mandatory = $true, ParameterSetName = "CryptText")]
        [String]$Text,

        [Parameter(Mandatory = $true, ParameterSetName = "CryptFile")]
        [String]$Path
    )

    Begin {
        $shaManaged = New-Object System.Security.Cryptography.SHA256Managed
        $aesManaged = New-Object System.Security.Cryptography.AesManaged
        $aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
        $aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::Zeros
        $aesManaged.BlockSize = 128
        $aesManaged.KeySize = 256
    }

    Process {
        $aesManaged.Key = $shaManaged.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Key))

        switch ($Mode) {
            'Encrypt' {
                if ($Text) {$plainBytes = [System.Text.Encoding]::UTF8.GetBytes($Text)}
                
                if ($Path) {
                    $File = Get-Item -Path $Path -ErrorAction SilentlyContinue
                    if (!$File.FullName) {
                        Write-Error -Message "File not found!"
                        break
                    }
                    $plainBytes = [System.IO.File]::ReadAllBytes($File.FullName)
                    $outPath = $File.FullName + ".aes"
                }

                $encryptor = $aesManaged.CreateEncryptor()
                $encryptedBytes = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)
                $encryptedBytes = $aesManaged.IV + $encryptedBytes
                $aesManaged.Dispose()

                if ($Text) {return [System.Convert]::ToBase64String($encryptedBytes)}
                
                if ($Path) {
                    [System.IO.File]::WriteAllBytes($outPath, $encryptedBytes)
                    (Get-Item $outPath).LastWriteTime = $File.LastWriteTime
                    return "File encrypted to $outPath"
                }
            }

            'Decrypt' {
                if ($Text) {$cipherBytes = [System.Convert]::FromBase64String($Text)}
                
                if ($Path) {
                    $File = Get-Item -Path $Path -ErrorAction SilentlyContinue
                    if (!$File.FullName) {
                        Write-Error -Message "File not found!"
                        break
                    }
                    $cipherBytes = [System.IO.File]::ReadAllBytes($File.FullName)
                    $outPath = $File.FullName -replace ".aes"
                }

                $aesManaged.IV = $cipherBytes[0..15]
                $decryptor = $aesManaged.CreateDecryptor()
                $decryptedBytes = $decryptor.TransformFinalBlock($cipherBytes, 16, $cipherBytes.Length - 16)
                $aesManaged.Dispose()

                if ($Text) {return [System.Text.Encoding]::UTF8.GetString($decryptedBytes).Trim([char]0)}
                
                if ($Path) {
                    [System.IO.File]::WriteAllBytes($outPath, $decryptedBytes)
                    (Get-Item $outPath).LastWriteTime = $File.LastWriteTime
                    return "File decrypted to $outPath"
                }
            }
        }
    }

    End {
        $shaManaged.Dispose()
        $aesManaged.Dispose()
    }
}

### Import the Module

Import-Module .\Invoke-AESEncryption.ps1

### Encrypt a File

Invoke-AESEncryption -Mode Encrypt -Key "p4ssw0rd" -Path .\scan-results.txt

Output:
File encrypted to C:\htb\scan-results.txt.aes

### Decrypt a File

Invoke-AESEncryption -Mode Decrypt -Key "p4ssw0rd" -Path .\scan-results.txt.aes

### Encrypt Text (Not File)

Invoke-AESEncryption -Mode Encrypt -Key "p4ssw0rd" -Text "Secret Text"

This returns a Base64 encoded string.

### Decrypt Text

Invoke-AESEncryption -Mode Decrypt -Key "p4ssw0rd" -Text "LtxcRelxrDLrDB9rBD6JrfX/czKjZ2CUJkrg++kAMfs="

---

## Method 2: Linux File Encryption with OpenSSL

OpenSSL is installed on most Linux systems.

### Encrypt a File

openssl enc -aes256 -iter 100000 -pbkdf2 -in /etc/passwd -out passwd.enc

You'll be prompted for a password.

Options explained:
- -aes256: AES-256 encryption
- -iter 100000: 100,000 iterations (makes brute-force harder)
- -pbkdf2: Use Password-Based Key Derivation Function 2
- -in: Input file
- -out: Output file

### Decrypt a File

openssl enc -d -aes256 -iter 100000 -pbkdf2 -in passwd.enc -out passwd

Options explained:
- -d: Decrypt mode

### Encrypt with Password in Command (Not Recommended)

openssl enc -aes256 -iter 100000 -pbkdf2 -in file.txt -out file.enc -pass pass:YourPassword

**Warning:** This exposes the password in command history. Use interactive prompts instead.

---

## Method 3: Transfer Encrypted Files

Once encrypted, you can transfer using any method:

### Via HTTP

# On your machine (server)
python3 -m http.server 8000

# On target (download encrypted file)
wget http://YOUR-IP:8000/passwd.enc

### Via Netcat

# On target (receiver)
nc -lvnp 4444 > passwd.enc

# On your machine (sender)
nc -q 0 TARGET-IP 4444 < passwd.enc

### Via SCP (Secure)

scp passwd.enc user@target:/tmp/

---

## Password Security

> "Using very strong and unique passwords for encryption for every company where a penetration test is performed is essential. This is to prevent sensitive files and information from being decrypted using one single password that may have been leaked and cracked by a third party."

### Password Best Practices

| Do | Don't |
|----|-------|
| Use unique password per client | Reuse the same password |
| Use strong passwords (20+ chars) | Use simple passwords |
| Store passwords securely | Write them in plain text |
| Use password manager | Email passwords |

---

## Key Takeaways

- Always encrypt sensitive data before transfer
- Use Invoke-AESEncryption.ps1 on Windows
- Use OpenSSL on Linux
- Strong, unique passwords per client
- Never exfiltrate real PII without permission
- Use dummy data for DLP testing
- Data leakage has serious consequences
- Encrypt first, transfer second
- Professional responsibility is paramount
- Practice these techniques in the lab
