### Workflow 1: Testing a New Web App (30 minutes)
```
# STEP 1: Configure proxy and turn off intercept
Burp -> Proxy -> Intercept -> Intercept is off
# STEP 2: Browse the application
# Click through all pages, submit forms, use all functionality
# This populates Proxy History
# STEP 3: Review Proxy History
Proxy -> HTTP History
# Right-click -> Send interesting requests to Repeater
# STEP 4: Spider/Discover content
Right-click on site -> Engagement tools -> Discover content
# Or use Intruder with directory wordlist
# STEP 5: Scan interesting parameters
Send to Intruder, fuzz for:
- SQL injection (error-based first)
- XSS
- LFI
- Command injection
# STEP 6: Check for IDOR
Change ID parameters (id=1 to id=2) in Repeater
# STEP 7: Check for auth bypass
Try admin' OR '1'='1 in login forms
```

### Workflow 2: Finding SQL Injection (15 minutes)

```
# STEP 1: Find parameters
Proxy History -> Look for ?id=, ?page=, ?cat=, etc.
# STEP 2: Send to Repeater
Right-click -> Send to Repeater
# STEP 3: Test each parameter
Add ' and look for error messages
Use Intruder with SQL payload list
# STEP 4: Confirm with boolean test
1 AND 1=1 vs 1 AND 1=2
# STEP 5: Find column count
UNION SELECT NULL, NULL, NULL...
# STEP 6: Extract data
UNION SELECT database(), user(), version()
```

### Workflow 3: Brute Forcing Login (20 minutes)

```
# STEP 1: Capture login request
Intercept ON -> Login -> Forward
# STEP 2: Send to Intruder
Right-click -> Send to Intruder
# STEP 3: Set attack type
Cluster Bomb (if multiple parameters)
Sniper (if only one parameter)
# STEP 4: Set positions
§user§=admin&§pass§=password
# STEP 5: Load payloads
Users: admin, root, administrator
Passwords: rockyou.txt (first 50)
# STEP 6: Analyze results
Look for different status code/length
302 redirect usually means success
```

### Workflow 4: Finding Hidden Content (15 minutes)

```
# STEP 1: Right-click on site
Engagement tools -> Discover content
# STEP 2: Configure
Type: Directory and file
Wordlist: /usr/share/wordlists/dirb/common.txt
Extensions: php,asp,aspx,jsp,html,txt
# STEP 3: Run discovery
Wait for results
# STEP 4: Review findings
Send interesting results to Repeater
```
