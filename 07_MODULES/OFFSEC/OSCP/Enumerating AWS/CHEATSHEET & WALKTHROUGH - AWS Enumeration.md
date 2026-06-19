# Enumerating AWS Cloud Infrastructure - Cheat Sheet & Walkthrough

## Table of Contents
1. [Reconnaissance of Cloud Resources on the Internet](#1-reconnaissance-of-cloud-resources-on-the-internet)
2. [Reconnaissance via Cloud Service Provider's API](#2-reconnaissance-via-cloud-service-providers-api)
3. [Initial IAM Reconnaissance](#3-initial-iam-reconnaissance)
4. [IAM Resources Enumeration](#4-iam-resources-enumeration)
5. [Quick Reference](#5-quick-reference)

---

## 1. Reconnaissance of Cloud Resources on the Internet

### 1.1 Lab Setup

#### Configure DNS
```bash
# Check current DNS
cat /etc/resolv.conf

# Add lab DNS server
sudo nano /etc/resolv.conf
nameserver 44.205.254.229  # Lab DNS IP
nameserver 1.1.1.1

# Test DNS configuration
host www.offseclab.io 44.205.254.229
host www.offseclab.io

# Reset DNS
sudo systemctl restart NetworkManager
```

### 1.2 Domain Reconnaissance

#### DNS Queries
```bash
# Query nameserver records
host -t ns offseclab.io

# Get A record
host www.offseclab.io

# Reverse DNS
host 52.70.117.69

# WHOIS information
whois offseclab.io | grep "Registrant Organization"
whois 52.70.117.69 | grep "OrgName"
```

#### Automated DNS Enumeration
```bash
dnsenum offseclab.io --threads 100
```

**Key Findings**:
- Name servers: `*.awsdns-00.com` → AWS Route53
- Public IP: `52.70.117.69` → AWS EC2
- Reverse DNS: `ec2-52-70-117-69.compute-1.amazonaws.com`

### 1.3 Service-Specific Domains

#### Common CSP URLs

| AWS | Azure | GCP |
|-----|-------|-----|
| `s3.amazonaws.com` | `web.core.windows.net` | `appspot.com` |
| `awsapps.com` | `file.core.windows.net` | `storage.googleapis.com` |
| | `blob.core.windows.net` | |
| | `azurewebsites.net` | |
| | `cloudapp.net` | |

#### S3 Bucket Enumeration

**Identify Bucket from Website**:
1. Open Developer Tools (F12)
2. Network tab
3. Reload page
4. Look for `s3.amazonaws.com` requests

**Example URL**:
```
https://s3.amazonaws.com/offseclab-assets-public-axevtewi/sites/www/images/saphire.jpg
```

**Bucket Structure**:
```
Bucket Name: offseclab-assets-public-axevtewi
Object Key: sites/www/images/saphire.jpg
```

**Check Bucket Permissions**:
```bash
# Browse bucket URL
http://offseclab-assets-public-axevtewi.s3.amazonaws.com/

# XML Response Codes
# AccessDenied → Private bucket
# NoSuchBucket → Bucket doesn't exist
# XML Listing → Publicly readable
```

#### Automated Bucket Enumeration with cloud-enum
```bash
# Install
sudo apt install cloud-enum

# Quick scan
cloud_enum -k offseclab-assets-public-axevtewi -qs --disable-azure --disable-gcp

# Custom keyfile
for key in "public" "private" "dev" "prod" "development" "production"; do 
    echo "offseclab-assets-$key-axevtewi"
done | tee /tmp/keyfile.txt

cloud_enum -kf /tmp/keyfile.txt -qs --disable-azure --disable-gcp
```

---

## 2. Reconnaissance via Cloud Service Provider's API

### 2.1 AWS CLI Setup

```bash
# Install AWS CLI
sudo apt install awscli

# Configure profile
aws configure --profile attacker
# Input: Access Key ID, Secret Access Key, region (us-east-1), format (json)

# Test authentication
aws --profile attacker sts get-caller-identity
```

### 2.2 Publicly Shared Resources

#### AMI (Amazon Machine Images)
```bash
# List public AMIs owned by AWS
aws --profile attacker ec2 describe-images --owners amazon --executable-users all

# Filter by description
aws --profile attacker ec2 describe-images --executable-users all \
    --filters "Name=description,Values=*Offseclab*"

# Filter by name
aws --profile attacker ec2 describe-images --executable-users all \
    --filters "Name=name,Values=*Offseclab*"
```

#### EBS Snapshots
```bash
# Filter snapshots by description
aws --profile attacker ec2 describe-snapshots \
    --filters "Name=description,Values=*offseclab*"
```

### 2.3 Obtaining Account IDs from S3 Buckets

#### Extract Bucket Name
```bash
curl -s www.offseclab.io | grep -o -P 'offseclab-assets-public-\w{8}'
```

#### Create Enumeration User
```bash
# Create IAM user
aws --profile attacker iam create-user --user-name enum

# Create access keys
aws --profile attacker iam create-access-key --user-name enum

# Configure profile
aws configure --profile enum
```

#### Policy-Based Account ID Enumeration
```json
// policy-s3-read.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:ListBucket", "s3:GetObject"],
            "Resource": "*",
            "Condition": {
                "StringLike": {"s3:ResourceAccount": ["1*"]}
            }
        }
    ]
}
```

```bash
# Apply policy
aws --profile attacker iam put-user-policy \
    --user-name enum \
    --policy-name s3-read \
    --policy-document file://policy-s3-read.json

# Test access
aws --profile enum s3 ls offseclab-assets-private-kaykoour

# Change condition (1* → 12* → 123* ...)
```

### 2.4 Enumerating IAM Users in Other Accounts

#### Create Test Bucket
```bash
aws --profile attacker s3 mb s3://offseclab-dummy-bucket-$RANDOM-$RANDOM-$RANDOM
```

#### Resource-Based Policy Test
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": ["arn:aws:iam::123456789012:user/cloudadmin"]
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::offseclab-dummy-bucket-28967-25641-13328"
        }
    ]
}
```

```bash
# Apply policy (valid principal → success)
aws --profile attacker s3api put-bucket-policy \
    --bucket offseclab-dummy-bucket-28967-25641-13328 \
    --policy file://grant-s3-bucket-read.json

# Apply policy (invalid principal → MalformedPolicy error)
aws --profile attacker s3api put-bucket-policy \
    --bucket offseclab-dummy-bucket-28967-25641-13328 \
    --policy file://grant-s3-bucket-read-userDoNotExist.json
```

#### Pacu Role Enumeration
```bash
# Install pacu
sudo apt install pacu

# Start pacu
pacu

# Import keys
Pacu > import_keys attacker

# List modules
Pacu > ls

# Run role enumeration
Pacu > run iam__enum_roles --word-list /tmp/role-names.txt --account-id 123456789012
```

---

## 3. Initial IAM Reconnaissance

### 3.1 Examining Compromised Credentials

```bash
# Configure target profile
aws configure --profile target

# Get identity info
aws --profile target sts get-caller-identity

# Get account ID from access key (stealthy)
aws --profile challenge sts get-access-key-info --access-key-id AKIAQOMAIGYUVEHJ7WXM
```

#### Stealthy Info Gathering
```bash
# Invoke nonexistent Lambda (data event - not logged by default)
aws --profile target lambda invoke \
    --function-name arn:aws:lambda:us-east-1:123456789012:function:nonexistent-function \
    outfile

# Error reveals account ID and identity
```

#### CloudTrail Evasion
```bash
# Execute in different region to avoid logging
aws --profile target sts get-caller-identity --region us-east-2
```

### 3.2 Scoping IAM Permissions

#### List Policies
```bash
# Inline policies (directly attached)
aws --profile target iam list-user-policies --user-name clouddesk-plove

# Managed policies (attached)
aws --profile target iam list-attached-user-policies --user-name clouddesk-plove

# List groups
aws --profile target iam list-groups-for-user --user-name clouddesk-plove

# Group policies
aws --profile target iam list-group-policies --group-name support
aws --profile target iam list-attached-group-policies --group-name support
```

#### Read Policy Document
```bash
# List policy versions
aws --profile target iam list-policy-versions \
    --policy-arn "arn:aws:iam::aws:policy/job-function/SupportUser"

# Get policy version
aws --profile target iam get-policy-version \
    --policy-arn arn:aws:iam::aws:policy/job-function/SupportUser \
    --version-id v8
```

---

## 4. IAM Resources Enumeration

### 4.1 IAM Commands Reference

| Command | Purpose |
|---------|---------|
| `iam get-account-summary` | IAM quotas and usage |
| `iam list-users` | List all IAM users |
| `iam list-groups` | List all groups |
| `iam list-roles` | List all roles |
| `iam list-policies --scope Local --only-attached` | Customer managed policies |
| `iam get-account-authorization-details` | Full IAM snapshot |
| `iam get-policy-version` | Read policy document |
| `iam list-attached-user-policies` | Policies attached to user |
| `iam list-groups-for-user` | User's group memberships |

### 4.2 Querying with JMESPath

```bash
# List all usernames
aws --profile target iam get-account-authorization-details --filter User \
    --query "UserDetailList[].UserName"

# Multiple fields (array)
aws --profile target iam get-account-authorization-details --filter User \
    --query "UserDetailList[0].[UserName,Path,GroupList]"

# Multiple fields (object)
aws --profile target iam get-account-authorization-details --filter User \
    --query "UserDetailList[0].{Name: UserName, Path: Path, Groups: GroupList}"

# Filter by username
aws --profile target iam get-account-authorization-details --filter User \
    --query "UserDetailList[?contains(UserName, 'admin')].{Name: UserName}"

# Filter by path
aws --profile target iam get-account-authorization-details --filter User Group \
    --query "{Users: UserDetailList[?Path=='/admin/'].UserName, \
              Groups: GroupDetailList[?Path=='/admin/'].{Name: GroupName}}"
```

### 4.3 Pacu Automation

```bash
# Start pacu
pacu

# Create session
> What would you like to name this new session? enumlab

# Import keys
> import_keys target

# List modules
> ls

# Enumerate IAM
> run iam__enum_users_roles_policies_groups

# View collected data
> services
> data IAM

# Bruteforce permissions
> run iam__bruteforce_permissions
```

### 4.4 Extracting Insights

#### Identify Privileged Users
```bash
# Users in admin groups
aws --profile target iam get-account-authorization-details --filter User Group \
    --query "UserDetailList[?contains(GroupList, 'admin')].UserName"

# Users with AdministratorAccess policy
aws --profile target iam get-account-authorization-details --filter Group \
    --query "GroupDetailList[?contains(AttachedManagedPolicies[].PolicyName, 'AdministratorAccess')].GroupName"
```

#### Identify Attack Paths
```bash
# Users who can create access keys
aws --profile target iam get-account-authorization-details --filter LocalManagedPolicy \
    --query "Policies[?contains(PolicyVersionList[].Document.Statement[].Action, 'iam:CreateAccessKey')].PolicyName"

# Groups with dangerous permissions
aws --profile target iam get-account-authorization-details --filter Group \
    --query "GroupDetailList[?AttachedManagedPolicies[].PolicyName=='amethyst_admin'].GroupName"
```

---

## 5. Quick Reference

### AWS CLI Profiles
```bash
# Create profile
aws configure --profile NAME

# Use profile
aws --profile NAME service command
```

### IAM Policy Structure
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow|Deny",
            "Action": "service:action",
            "Resource": "arn:aws:service:region:account:resource",
            "Condition": {
                "StringEquals": {"key": "value"}
            }
        }
    ]
}
```

### Common IAM Actions

| Action | Purpose |
|--------|---------|
| `iam:Get*` | Read IAM information |
| `iam:List*` | List IAM resources |
| `iam:CreateAccessKey` | Generate credentials |
| `iam:AddUserToGroup` | Modify group membership |
| `iam:PassRole` | Pass role to services |
| `sts:AssumeRole` | Assume IAM role |

### Key Takeaways

| Concept                       | Key Point                               |
| ----------------------------- | --------------------------------------- |
| **DNS Recon**                 | Identify cloud provider from NS records |
| **S3 Buckets**                | Check for public listing permissions    |
| **cloud-enum**                | Automated bucket enumeration            |
| **Account ID**                | Extract from public AMIs                |
| **Bucket Account ID**         | Use IAM conditions to brute force       |
| **Cross-Account Enumeration** | Use resource policies                   |
| **Stealth**                   | Use data events or wrong regions        |
| **IAM Scoping**               | Check user/group policies               |
| **JMESPath**                  | Filter JSON responses                   |
| **Pacu**                      | Automated AWS enumeration               |
| **ABAC**                      | Tags as authorization attributes        |