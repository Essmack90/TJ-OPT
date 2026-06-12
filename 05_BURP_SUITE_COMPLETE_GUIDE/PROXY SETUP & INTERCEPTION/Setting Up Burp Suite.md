```
# 1. Start Burp Suite
burpsuite

# 2. Set up proxy listener
Proxy -> Options -> Add -> 127.0.0.1:8080

# 3. Install Burp Certificate (for HTTPS)
Proxy -> Options -> Import/Export CA Certificate -> Export -> burp.crt

# 4. Configure browser to use proxy
# Firefox: Settings -> Network Settings -> Manual Proxy -> 127.0.0.1:8080

# 5. Turn off intercept to start (Intercept is OFF unless you see the button)
# Intercept button should say "Intercept is off"
```

### Intercept ON/OFF - What Happens

|Intercept Status|What Happens|
|---|---|
|OFF (default)|Requests flow through Burp silently, you see them in HTTP History|
|ON|Requests pause until you click "Forward" or "Drop"|

### Capturing Your First Request

```
```bash

# Step 1: Turn Intercept ON
# Click "Intercept" button until it says "Intercept is on"
# Step 2: Browse to http://target.com
# Browser will hang - request is paused in Burp
# Step 3: View request in Burp
# You'll see:

┌─────────────────────────────────────────────────────────────────────────────┐  
│ REQUEST (Intercepted) │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ GET / HTTP/1.1 │  
│ Host: [target.com](https://target.com) │  
│ User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) │  
│ Accept: text/html,application/xhtml+xml │  
│ Accept-Language: en-US,en;q=0.9 │  
│ Accept-Encoding: gzip, deflate │  
│ Connection: keep-alive │  
│ Upgrade-Insecure-Requests: 1 │  
│ │  
│ [empty body for GET request] │  
└───────────────────────────────────────────────────────────────────────────
```

