# Using Web Proxies Module

![[cheatsheat-Using Web Proxies]]

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Intercepting Web Requests|Question 1|HTB{1n73rc3p73d_1n_7h3_m1ddl3}|
|Repeating Requests|Question 1|HTB{qu1ckly_r3p3471n6_r3qu3575}|
|Encoding/Decoding|Question 1|HTB{3nc0d1n6_n1nj4}|
|Proxying Tools|Question 1|msf test file|
|Burp Intruder|Question 1|HTB{burp_1n7rud3r_fuzz3r!}|
|ZAP Fuzzer|Question 1|HTB{fuzz1n6_my_f1r57_c00k13}|
|ZAP Scanner|Question 1|HTB{5c4nn3r5_f1nd_vuln5_w3_m155}|
|Skills Assessment - Using Web Proxies|Question 1|HTB{d154bl3d_bu770n5_w0n7_570p_m3}|
|Skills Assessment - Using Web Proxies|Question 2|3dac93b8cd250aa8c1a36fffc79a17a|
|Skills Assessment - Using Web Proxies|Question 3|HTB{burp_1n7rud3r_n1nj4!}|
|Skills Assessment - Using Web Proxies|Question 4|CFIDE|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Intercepting Web Requests

## Question 1

### "Try intercepting the ping request on the server shown above, and change the post data similarly to what we did in this section. Change the command read flag.txt"

After spawning the target machine and navigating to its websites's root page, students need to run either `Burp Suite` or `ZAP` (`Burp Suite` will be used for this question; students also need to make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`), and then provide any number (such as 1) in the IP field and click on "Ping":

![Using_Web_Proxies_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_1.png)

Students then need to open `Burp Suite` and send the intercepted `POST` request to the endpoint `/ping` to `Repeater` (`Ctrl + R`):

![Using_Web_Proxies_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_2.png)

Then, students need to change the value of the `ip` parameter to be `;cat flag.txt` instead of the value they supplied from the front end and URL-encode it by highlighting it and clicking/pressing `Ctrl + U`:

Code: shell

```shell
ip=%3bcat+flag.txt
```

![Using_Web_Proxies_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_3.png)

At last, students need to send the modified request to attain the flag `HTB{1n73rc3p73d_1n_7h3_m1ddl3}` in the response:

![Using_Web_Proxies_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_4.png)

Answer: `HTB{1n73rc3p73d_1n_7h3_m1ddl3}`

# Repeating Requests

## Question 1

### "Try using request repeating to be able to quickly test commands. With that, try looking for the other flag"

After spawning the target machine and navigating to its website's root page, students need to run either `Burp Suite` or `ZAP` (`Burp Suite` will be used for this question; students also need to make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`), and then provide any number (such as 1) in the IP field and click on "Ping":

![Using_Web_Proxies_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_5.png)

Students then need to open `Burp Suite` and send the intercepted `POST` request to `/ping` to `Repeater` (`Ctrl + R`):

![Using_Web_Proxies_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_6.png)

Then, students need to use the `ls` command after the semi-colon and perform a path traversal to list the contents of the root directory:

Code: shell

```shell
ip=;ls+../../../
```

![Using_Web_Proxies_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_7.png)

From the response, students will notice that the flag file "flag.txt" exists in the root directory; therefore, they need to use `cat` to print out its contents, finding it to be `HTB{qu1ckly_r3p3471n6_r3qu3575}`:

Code: shell

```shell
ip=;cat /flag.txt
```

![Using_Web_Proxies_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_8.png)

Answer: `HTB{qu1ckly_r3p3471n6_r3qu3575}`

# Encoding/Decoding

## Question 1

### "The string found in the attached file has been encoded several times with various encoders. Try to use the decoding tools we discussed to decode it and get the flag."

Students first need to download the file [encoded_flag.zip](https://academy.hackthebox.com/storage/modules/110/encoded_flag.zip), unzip it, and print out the encoded flag:

Code: shell

```shell
wget https://academy.hackthebox.com/storage/modules/110/encoded_flag.zip
unzip encoded_flag.zip
cat encoded_flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.76]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/modules/110/encoded_flag.zip

--2022-07-19 04:21:28--  https://academy.hackthebox.com/storage/modules/110/encoded_flag.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 104.18.20.126, 104.18.21.126, 2606:4700::6812:147e, ...
Connecting to academy.hackthebox.com (academy.hackthebox.com)|104.18.20.126|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 340 [application/zip]
Saving to: ‘encoded_flag.zip’

encoded_flag.zip    100%[===================>]     340  --.-KB/s    in 0s      

2022-07-19 04:21:28 (6.26 MB/s) - ‘encoded_flag.zip’ saved [340/340]

┌─[us-academy-1]─[10.10.14.76]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ unzip encoded_flag.zip 
Archive:  encoded_flag.zip
  inflating: encoded_flag.txt
┌─[us-academy-1]─[10.10.14.76]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat encoded_flag.txt

VTJ4U1VrNUZjRlZXVkVKTFZrWkdOVk5zVW10aFZYQlZWRmh3UzFaR2NITlRiRkphWld0d1ZWUllaRXRXUm10M1UyeFNUbVZGY0ZWWGJYaExWa1V3ZVZOc1VsZGlWWEJWVjIxNFMxWkZNVFJUYkZKaFlrVndWVmR0YUV0V1JUQjNVMnhTYTJGM1BUMD0=
```

Students will notice that the flag ends in `=`, thus, it is most probably base64-encoded. Therefore, students need to copy the encoded flag and paste it into `Burp Suite`'s `Decoder` and decode it as Base64:

![Using_Web_Proxies_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_9.png)

Subsequently, students will also notice that the decoded string is also base64-encoded:

![Using_Web_Proxies_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_10.png)

Therefore, students will need to perform base64 decoding on the encoded string four times, and at last, they will find a URL-encoded string:

![Using_Web_Proxies_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_11.png)

Thus, students need to decode the string as a URL-encoded string to attain the flag `HTB{3nc0d1n6_n1nj4}`:

![Using_Web_Proxies_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_12.png)

Answer: `HTB{3nc0d1n6_n1nj4}`

# Proxying Tools

## Question 1

### "Try running 'auxiliary/scanner/http/http\_put' in metasploit on any website, while having the traffic routed through Burp. Once you view the requests sent, what is the last line in the request?"

Students first need to launch `msfconsole` and use the `auxiliary/scanner/http/http_put` module:

Code: shell

```shell
msfconsole -q
use auxiliary/scanner/http/http_put
```

```shell-session
┌─[us-academy-1]─[10.10.14.76]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ msfconsole -q

msf6 > use auxiliary/scanner/http/http_put 
msf6 auxiliary(scanner/http/http_put) >
```

Subsequently, students need to set the `PROXIES`, `RHOSTS`, and `RPORT` options, making sure that `PROXIES` is set to the same IP and port that `Burp Suite` listens on (the defaults being `127.0.0.1:8080`), while for the other two options, any actual website's IP address and port 443 would suffice:

Code: shell

```shell
set PROXIES HTTP:127.0.0.1:8080
set RHOSTS STMIP
set RPORT 443
```

```shell-session
msf6 auxiliary(scanner/http/http_put) > set PROXIES HTTP:127.0.0.1:8080

PROXIES => HTTP:127.0.0.1:8080
msf6 auxiliary(scanner/http/http_put) > set RHOSTS 104.18.20.126

RHOSTS => 104.18.20.126
msf6 auxiliary(scanner/http/http_put) > set RPORT 443

RPORT => 443
```

Students now need to open `Burp Suite` and make sure that the proxy is intercepting requests and then run the `msfconsole` module with the `run` or `exploit` command:

Code: shell

```shell
run
```

```shell-session
msf6 auxiliary(scanner/http/http_put) > run
```

Afterward, students will notice that `Burp Suite` has intercepted the `msfconsole` request sent, and the last line in the request is on line 8, `msf test file`:

![Using_Web_Proxies_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_13.png)

Answer: `msf test file`

# Burp Intruder

## Question 1

### "Use Burp Intruder to fuzz for '.html' files under the /admin directory, to find a file containing the flag."

After spawning the target machine, students need to run `Burp Suite`, make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`, and then navigate to the `/admin/` directory to capture the request in `Burp Suite`:

![Using_Web_Proxies_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_14.png)

Students then need to send the intercepted request to `Intruder` by pressing `Ctrl + I`, and set the first line of the request in the `Position` tab to:

Code: shell

```shell
GET /admin/§FILE§.html HTTP/1.1
```

![Using_Web_Proxies_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_15.png)

Subsequently, students need to move to the `Payloads` tab and load the wordlist `/opt/useful/SecLists/Discovery/Web-Content/common.txt`:

![Using_Web_Proxies_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_16.png)

At last, students need to click on `Start Attack` and wait for a bit until a request with the 200 status appears, in which they will find the flag `HTB{burp_1n7rud3r_fuzz3r!}` within its response:

![Using_Web_Proxies_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_17.png)

Answer: `HTB{burp_1n7rud3r_fuzz3r!}`

# ZAP Fuzzer

## Question 1

### "The directory we found above sets the cookie to the md5 hash of the username, as we can see the md5 cookie in the request for the (guest) user. Visit '/skills/' to get a request with a cookie, then try to use ZAP Fuzzer to fuzz the cookie for different md5 hashed usernames to get the flag. (You may use the wordlist: /opt/useful/SecLists/Usernames/top-usernames-shortlist.txt)"

After spawning the target machine, students need to navigate to the `/skills/` directory, run `ZAP`, make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`, refresh the page on `/skills/` to capture the request in `ZAP` and view the cookie within the request:

![Using_Web_Proxies_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_18.png)

Students need to right-click on the request and select `Attack` -> `Fuzz`:

![Using_Web_Proxies_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_19.png)

Afterward, students need to select the value after `cookie=` and click on `Add` -> `Add`:

![Using_Web_Proxies_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_20.png)

![Using_Web_Proxies_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_21.png)

Subsequently, students need to choose `File` for `Type` and load the `/opt/useful/SecLists/Usernames/top-usernames-shortlist.txt` wordlist after clicking on `Select`:

![Using_Web_Proxies_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_22.png)

![Using_Web_Proxies_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_23.png)

After the wordlist is loaded, students need to click on `Add`:

![Using_Web_Proxies_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_24.png)

Subsequently, students need to click on `Processors`:

![Using_Web_Proxies_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_25.png)

And then click on `Add`:

![Using_Web_Proxies_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_26.png)

For `Type`, students need to choose `MD5 Hash` and then click on `Add`:

![Using_Web_Proxies_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_27.png)

After clicking on the two subsequent `OK` buttons, students need to click on `Start Fuzzer`:

![Using_Web_Proxies_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_28.png)

After fuzzing has finished, students need to sort the responses by body size and will find that one of the responses has a response size of 450 bytes; viewing the response body will reveal the flag `HTB{fuzz1n6_my_f1r57_c00k13}`:

![Using_Web_Proxies_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_29.png)

Answer: `HTB{fuzz1n6_my_f1r57_c00k13}`

# ZAP Scanner

## Question 1

### "Run ZAP Scanner on the exercise above to identify directories and potential vulnerabilities. Once you find the high-level vulnerability, try to use it to read the flag at '/flag.txt'"

After spawning the target machine, students need to run `ZAP`, make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`, and capture a request to the machine's website root page by navigating to it:

![Using_Web_Proxies_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_30.png)

Then, students need to right-click on the request and select `Attack` -> `Spider`:

![Using_Web_Proxies_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_31.png)

Students can keep the default configurations as is and click on `Start Scan`:

![Using_Web_Proxies_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_32.png)

Once the scan has finished, students need to click on the website's folder and click on `Attack` -> `Active Scan`:

![Using_Web_Proxies_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_33.png)

Students can keep the default configurations as is and click on `Start Scan`:

![Using_Web_Proxies_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_34.png)

Students need not to wait until the scan finishes completely, instead, once they see 1 for the `High Priority Alerts` flag, they need to click on `Alerts`:

![Using_Web_Proxies_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_35.png)

Subsequently, students will find that the vulnerability is a `Remote OS Command Injection`:

![Using_Web_Proxies_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_36.png)

Then, students need to right-click on the `GET` request under `Remote OS Command Injection` and click on `Open/Resend with Request Editor...`:

![Using_Web_Proxies_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_37.png)

The payload used for the original request prints out the contents of the `/etc/passwd` file:

![Using_Web_Proxies_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_38.png)

However, students need to change the payload so that it prints out the contents of the flag file "flag.txt", making sure that the whitespace is URL-encoded:

Code: shell

```shell
;cat%20/flag.txt
```

![Using_Web_Proxies_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_39.png)

After clicking on `Send`, students will find the flag `HTB{5c4nn3r5_f1nd_vuln5_w3_m155}` within the response:

![Using_Web_Proxies_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_40.png)

Answer: `HTB{5c4nn3r5_f1nd_vuln5_w3_m155}`

# Skills Assessment - Using Web Proxies

## Question 1

### "The /lucky.php page has a button that appears to be disabled. Try to enable the button, and then click it to get the flag."

After spawning the target machine, students need to navigate to its website's `/lucky.php` page and notice that the "Click for a chance to win a flag!" button is disabled:

![Using_Web_Proxies_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_41.png)

Therefore, students need to run `ZAP` (`Burp Suite` can also be used), make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`, and refresh the page on `/lucky.php` to capture the request in `ZAP`. When viewing the response for the `GET` response sent to `/lucky.php`, students will notice that the button has the attribute `disabled`:

![Using_Web_Proxies_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_42.png)

Therefore, students need to open `Replacer` by clicking `Ctrl + R` and then `Add...`:

![Using_Web_Proxies_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_43.png)

Subsequently, students need to set `Match Type` to `Response Body String`, `Match String` to `disabled>`, `Replacement String` to `>`, check `Enable`, and click on `Save`:

![Using_Web_Proxies_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_44.png)

Then, students need to select the `GET` request and click on `Open/Resend with Request Editor...`:

![Using_Web_Proxies_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_45.png)

For easier usability, students can click on `Combined display for header and body`, `Request shown above Response` for the `Request` tab, and `Combined display for header and body` for the `Response` tab:

![Using_Web_Proxies_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_46.png)

Thereafter, after clicking `Send`, students will notice that the response body no longer contains `disabled`:

![Using_Web_Proxies_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_47.png)

Thus, students now need to right-click on the response and choose `Open URL in System Browser`, to notice that they can click the button as it is not disabled anymore (in case it is, it might be from cached pages, thus, students can press `Ctrl + Shift + R` to force refresh the page):

![Using_Web_Proxies_Walkthrough_Image_48.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_48.png)

![Using_Web_Proxies_Walkthrough_Image_49.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_49.png)

After clicking on the button around 8 times, students will attain the flag `HTB{d154bl3d_bu770n5_w0n7_570p_m3}`:

![Using_Web_Proxies_Walkthrough_Image_50.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_50.png)

Answer: `HTB{d154bl3d_bu770n5_w0n7_570p_m3}`

# Skills Assessment - Using Web Proxies

## Question 2

### "The /admin.php page uses a cookie that has been encoded multiple time. Try to decode the cookie until you get a value with 31-characters. Submit the value as the answer."

After spawning the target machine, students need to run `ZAP` (`Burp Suite` can also be used), make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`, and navigate to `/admin.php` to capture the request in `ZAP` and notice the cookie value within the `Cookie` header:

![Using_Web_Proxies_Walkthrough_Image_51.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_51.png)

Students need to select the hash after `cookie=`, right-click and select `Encode/Decode/Hash...`:

![Using_Web_Proxies_Walkthrough_Image_52.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_52.png)

Then, students need to click on the `Decode` tab and copy the `ASCII Hex Decode` value then paste it in the `Text to be encoded/decode/hashed`. The `Base64 Decode` will contain the 31-characters value `3dac93b8cd250aa8c1a36fffc79a17a`::

![Using_Web_Proxies_Walkthrough_Image_53.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_53.png)

Answer: `3dac93b8cd250aa8c1a36fffc79a17a`

# Skills Assessment - Using Web Proxies

## Question 3

### "Once you decode the cookie, you will notice that it is only 31 characters long, which appears to be an md5 hash missing its last character. So, try to fuzz the last character of the decoded md5 cookie with all alpha-numeric characters, while encoding each request with the encoding methods you identified above. (You may use the "alphanum-case.txt" wordlist from SecLists for the payload)"

After spawning the target machine, students need to run `Burp Suite` (`ZAP` can also be used, however, it is more involved as it lacks an `ASCII-Hex` fuzzer processor, meaning that students are required to create a script for it manually), make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in `Firefox`, and navigate to `/admin.php` to capture the request in `Burp Suite` and notice the cookie value within the `Cookie` header. Students need to right-click on it and select `Send to Intruder`:

![Using_Web_Proxies_Walkthrough_Image_54.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_54.png)

Within `Intruder`, students first need to click on `Clear §`, replace the default cookie with the `MD5` hash `3dac93b8cd250aa8c1a36fffc79a17a` attained in the previous question, select it, and click on `Add §`:

![Using_Web_Proxies_Walkthrough_Image_55.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_55.png)

Subsequently, students need to click on the `Payloads` tab then on `Load ...` under `Payload Options` and load the file `alphanum-case.txt` from `/opt/useful/SecLists/Fuzzing/`:

![Using_Web_Proxies_Walkthrough_Image_56.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_56.png)

Then, under `Payload Processing`, students need to click on `Add`, select `Add prefix` as the processing rule, and paste in the `MD5` hash `3dac93b8cd250aa8c1a36fffc79a17a` for `Prefix`:

![Using_Web_Proxies_Walkthrough_Image_57.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_57.png)

Additionally, students need to add the `Base64-encode` and `Encode as ASCII hex` processing rules:

![Using_Web_Proxies_Walkthrough_Image_58.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_58.png)

![Using_Web_Proxies_Walkthrough_Image_59.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_59.png)

Thereafter, students need to click on `Start attack`:

![Using_Web_Proxies_Walkthrough_Image_60.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_60.png)

After fuzzing has completed, students can click on the `Length` column to sort by response size, and any response with the size of 1248 will contain the flag `HTB{burp_1n7rud3r_n1nj4!}` on line 42 in the response body:

![Using_Web_Proxies_Walkthrough_Image_61.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_61.png)

Answer: `HTB{burp_1n7rud3r_n1nj4!}`

# Skills Assessment - Using Web Proxies

## Question 4

### "You are using the 'auxiliary/scanner/http/coldfusion_locale_traversal' tool within Metasploit, but it is not working properly for you. You decide to capture the request sent by Metasploit so you can manually verify it and repeat it. Once you capture the request, what is the 'XXXXX' directory being called in '/XXXXX/administrator/..'?"

Students first need to launch `msfconsole`:

Code: shell

```shell
msfconsole -q
```

```shell-session
┌─[eu-academy-1]─[10.10.14.153]─[htb-ac413848@htb-xx2fcfymke]─[~]
└──╼ [★]$ msfconsole -q

[msf](Jobs:0 Agents:0) >>
```

Subsequently, students need to use the module `auxiliary/scanner/http/coldfusion_locale_traversal`:

Code: shell

```shell
use auxiliary/scanner/http/coldfusion_locale_traversal
```

```shell-session
[msf](Jobs:0 Agents:0) >> use auxiliary/scanner/http/coldfusion_locale_traversal
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/coldfusion_locale_traversal) >>
```

Then students need to set `PROXIES` to be the same as the one `Burp Suite`/`ZAP` listens on, while for `RHOST` and `RPORT` any random valid values can be used:

Code: shell

```shell
set PROXIES HTTP:127.0.0.1:8080
set RHOST STMIP
set RPORT STMPO
```

```shell-session
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/coldfusion_locale_traversal) >> set PROXIES HTTP:127.0.0.1:8080

PROXIES => HTTP:127.0.0.1:8080
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/coldfusion_locale_traversal) >> set RHOSTS 159.65.63.151
RHOSTS => 159.65.63.151
[msf](Jobs:0 Agents:0) auxiliary(scanner/http/coldfusion_locale_traversal) >> set RPORT 31845
RPORT => 31845
```

Before running the exploit, students need to make sure that `Burp Suite`/`ZAP` are intercepting requests, and then run the exploit:

Code: shell

```shell
run
```

```shell-session
auxiliary(scanner/http/coldfusion_locale_traversal) >> run
```

From the intercepted request, students will know that the directory the `msfconsole` module is sending a request to is `CFIDE`:

![Using_Web_Proxies_Walkthrough_Image_62.png](https://academy.hackthebox.com/storage/walkthroughs/56/Using_Web_Proxies_Walkthrough_Image_62.png)

Answer: `CFIDE`