# Command Injections Module

![[cheatsheat-Command Injections]]

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Detection|Question 1|Please match the requested format.|
|Injecting Commands|Question 1|17|
|Other Injection Operators|Question 1||
|Identifying Filters|Question 1|new-line|
|Bypassing Space Filters|Question 1|1613|
|Bypassing Other Blacklisted Characters|Question 1|1nj3c70r|
|Bypassing Blacklisted Commands|Question 1|HTB{b451c_f1l73r5_w0n7_570p_m3}|
|Advanced Command Obfuscation|Question 1|/usr/share/mysql/debian_create_root_user.sql|
|Skills Assessment|Question 1|HTB{c0mm4nd3r_1nj3c70r}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Detection

## Question 1

### "Try adding any of the injection operators after the ip in IP field. What did the error message say?"

After spawning the target machine and visiting its website's root webpage, students need to provide `;` as input to the IP field to get the error message `Please match the requested format.`:

![Command_Injections_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_1.png)

Answer: `Please match the requested format.`

# Injecting Commands

## Question 1

### "Review the HTML source code of the page to find where the front-end input validation is happening. On which line number is it?"

After spawning the target machine and visiting its website's root webpage, students need to view its source by clicking `CTRL` + `U` to then find the Regex pattern on line 17:

![Command_Injections_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_2.png)

Answer: `17`

# Other Injection Operators

## Question 1

### "Try the using remaining three injection operators (new-line, &, |), and see how each works and how the output differs. Which of them only shows the output of the injected command?"

After spawning the target machine and visiting its website's root webpage, students need to use `Burp Suite` or `ZAP` to intercept the request made after clicking the `Check` button and try the three operators. Students will find out that the `|` operators is the one that shows the output of the injected command:

![Command_Injections_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_3.png)

Additionally, students can refer to the `Command Injection Methods` table in the `Detection` section to find that the `Pipe` operator shows only the second output:

![Command_Injections_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_4.png)

Answer: `|`

# Identifying Filters

## Question 1

### "Try all other injection operators (new-line, &, |), to see if any of them is not blacklisted. Which operator is not blacklisted by the web application?"

After spawning the target machine and visiting its website's root webpage, students need to use `Burp Suite` or `ZAP` to intercept the request made after clicking the `Check` button and try the three operators. Students will find out that the `new-line` (i.e., `%0a`) character is not blacklisted:

Code: shell

```shell
127.0.0.1%0a
```

![Command_Injections_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_5.png)

Answer: `new-line`

# Bypassing Space Filters

## Question 1

### "Use what you learned in this section to execute the command 'ls -la'. What is the size of the 'index.php' file?"

After spawning the target machine and visiting its website's root webpage, students need to use `Burp Suite` or `ZAP` to intercept the request made after clicking the `Check` button. Students can use payloads that bypass the space filters such as `$IFS` or `%09`:

```shell-session
ls$IFS-la
ls%09-la
```

Using `ls$IFS-la`, students will find out that size of `index.php` is `1613` (bytes):

![Command_Injections_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_6.png)

Answer: `1613`

# Bypassing Other Blacklisted Characters

## Question 1

### "Use what you learned in this section to find name of the user in the '/home' folder. What user did you find?"

After spawning the target machine and visiting its website's root webpage, students need to use `Burp Suite` or `ZAP` to intercept the request made after clicking the `Check` button. Students can use payloads that bypass the space filters such as `$IFS` or `%09` and `${PATH:0:1}` to bypass the forward slash character filter, finding the user `1nj3c70r`:

```shell-session
ip=127.0.0.1%0als$IFS${PATH:0:1}home
```

![Command_Injections_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_7.png)

Answer: `1nj3c70r`

# Bypassing Blacklisted Commands

## Question 1

### "Use what you learned in this section find the content of flag.txt in the home folder of the user you previously found."

After spawning the target machine and visiting its website's root webpage, students need to use `Burp Suite` or `ZAP` to intercept the request made after clicking the `Check` button. Students can use payloads that bypass the space filters such as `$IFS` or `%09`, `${PATH:0:1}` to bypass the forward slash character filter, and add two apostrophes on the `cat` command to bypass its blacklisting filter such that it becomes `c'a't`. Students will attain the flag `HTB{b451c_f1l73r5_w0n7_570p_m3}`:

```shell-session
ip=127.0.0.1%0ac'a't${IFS}${PATH:0:1}home${PATH:0:1}1nj3c70r${PATH:0:1}flag.txt
```

![Command_Injections_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_8.png)

Answer: `HTB{b451c_f1l73r5_w0n7_570p_m3}`

# Advanced Command Obfuscation

## Question 1

### "Find the output of the following command using one of the techniques you learned in this section: find /usr/share/ | grep root | grep mysql | tail -n 1"

After spawning the target machine and visiting its website's root webpage, students need to use `Burp Suite` or `ZAP` to intercept the request made after clicking the `Check` button. Since the `pipe` operator is in the command, students need to use the third method which encodes all characters. Thus, students first need to base64-encode the command:

Code: shell

```shell
echo -n 'find /usr/share/ | grep root | tail -n 1' | base64
```

```shell-session
┌─[us-academy-1]─[10.10.14.7]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ echo -n 'find /usr/share/ | grep root | grep mysql | tail -n 1' | base64

ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=
```

Subsequently, students then need to create a command that will decode the encoded base64 string in a sub-shell and then pass it to `bash` to be executed:

```shell-session
bash<<<$(base64 -d<<<ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=)
```

At last, students need to bypass the space character filter by using either `%09` or `$IFS`, use the `new-line` operator `%0a` to separate the payload from the IP address, and forward the modified intercepted request. Students will attain the output `/usr/share/mysql/debian_create_root_user.sql`:

```shell-session
ip=127.0.0.1%0abash<<<$(base64%09-d<<<ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=)
```

![Command_Injections_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_9.png)

Answer: `/usr/share/mysql/debian_create_root_user.sql`

# Skills Assessment

## Question 1

### "What is the content of '/flag.txt'?"

After spawning the target machine, students need to navigate to its website's root webpage and login with the credentials `guest:guest`:

![Command_Injections_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_10.png)

Once signed in to the web-based file manager, students will find several files and a folder, with the former having four clickable buttons, `Preview`, `Copy to...`, `Direct link`, and `Download`. Out of the four, the `Copy to...` button seems the most plausible to be an attack vector, as the backend will need to use system commands such as `mv`, `move`, or `cp`. Clicking on `Copy to...` on a file will redirect students to a new page with two main options `Copy` and `Move`, while also being able to choose the destination folder:

![Command_Injections_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_11.png)

![Command_Injections_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_12.png)

If students select the destination folder `tmp` and click on `Copy`, injecting characters in the URL, no indication of command execution will appear. Therefore, students need to test the `Move` functionality. Clicking `Move` on a file without the selecting the `tmp` folder as the destination folder will throw the following error:

![Command_Injections_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_13.png)

Thus, most probably, the backend is using a `mv` command, and if an error occurs, it prints it out; therefore, this may be abused to capture command output, however, students need to ensure that the original `mv` command fails, otherwise error messages may not be displayed. Additionally, students need to use an injection operator that will show either both or only the second command, even if the first fails, which rules out the operator `&&`, however, any other operator may be used.

Students then need to run `Burp Suite`, set `FoxyProxy` to the preconfigured option "BURP", and then click on `Move` with no destination folder to move a file, same as done previously:

![Command_Injections_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_14.png)

Students need to send the intercepted request to `Repeater` (`Ctrl` + `R`) and send the request:

![Command_Injections_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_15.png)

After receiving the response, students will find the same error message in line 732:

![Command_Injections_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_16.png)

Students will notice that there are two GET parameters being passed in the request, `to` and `from`. Trying to inject different injection operators in both parameters, students will receive the error message "Malicious request denied!":

![Command_Injections_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_17.png)

However, when injecting the `&` operator, students will notice that it passes by, as the developers may have thought that it is required for URLs, and thus whitelisted it:

![Command_Injections_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_18.png)

Thus, students need to use this injection operator, however, it must be URL encoded, i.e., `%26`. Subsequently, students need to determine which parameter to be used for the injections, and in this case, either can be used, since both constitute the command being run by the backend, as seen by the printed error previously. Students need to inject `& cat /flag.txt` to read the flag file; to bypass white-space, students can either use `$IFS` or `%09`, and to bypass slashes, students need to use `${PATH:0:1}`, therefore, the payload can either be `$IFS%26c"a"t$IFS${PATH:0:1}flag.txt`, or `$IFS%26b"a"sh<<<$(base64%09-d<<<Y2F0IC9mbGFnLnR4dA==)`.

With the former payload, the URL parameters will be `/index.php?to=tmp$IFS%26c"a"t$IFS${PATH:0:1}flag.txt&from=51459716.txt&finish=1&move=1`:

![Command_Injections_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_19.png)

While with the the latter payload, the URL parameters will be `/index.php?to=tmp$IFS%26b"a"sh<<<$(base64%09-d<<<Y2F0IC9mbGFnLnR4dA==)&from=51459716.txt&finish=1&move=1`. Students will attain the flag `HTB{c0mm4nd3r_1nj3c70r}` with either payloads.:

![Command_Injections_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/43/Command_Injections_Walkthrough_Image_20.png)

Answer: `HTB{c0mm4nd3r_1nj3c70r}`