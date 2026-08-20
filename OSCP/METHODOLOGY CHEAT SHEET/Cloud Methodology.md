# Cloud Methodology (AWS)

Part of [[METHODOLOGY CHEAT SHEET]]. Phase-ordered attack framework for AWS cloud targets, from zero knowledge to privilege escalation. For pure syntax see [[Cloud Enumeration]] (Command Appendix). For symptom-based triage see [[Cloud Enumeration (Decision Tree)]].

#AWS #Cloud #IAM #S3 #Methodology

---

## Prerequisites

- AWS CLI installed (`sudo apt install awscli`)
- Your own AWS account (free tier) for API-recon phases, some cross-account techniques require it
- Pacu installed (`pip3 install pacu` or `sudo apt install pacu`)

Always use named profiles, never the default profile when juggling multiple credential sets:

```bash
aws configure --profile <name>   # creates/updates ~/.aws/credentials [<name>]
aws sts get-caller-identity --profile <name>   # verify who you are
```

---

## Phase 1: External Recon (No Auth Required)

**Goal:** learn as much as possible about the target's cloud footprint from public data only.

### 1.1 DNS Recon

```bash
# 1. Identify the DNS provider (awsdns = AWS Route53)
host -t ns <domain>
whois <ns-hostname> | grep "Registrant Organization"   # → Amazon Technologies = confirmed Route53

# 2. Resolve main hostnames → EC2 PTR prefix confirms EC2 hosting
host www.<domain>
host <ip>   # → ec2-X-X-X-X.compute-1.amazonaws.com

# 3. Reverse whois on the IP
whois <ip> | grep "OrgName"   # → Amazon Technologies Inc.

# 4. TXT records — flags/data sometimes hidden inside SPF/verification strings
dig TXT <domain> @<lab_dns_ip>
# Look for non-standard strings concatenated into otherwise-legit-looking records

# 5. Subdomain brute force
dnsenum <domain> --threads 100
# Zone transfers will fail on Route53 (AXFR record query failed: corrupt packet) — expected
```

### 1.2 S3 Bucket Discovery

```bash
# Find bucket names from site assets
curl -s http://<site_ip> -H "Host: www.<domain>" | grep -o '<org>-[^/"]*'
# Or browse in Firefox: DevTools → Network tab → filter by s3.amazonaws.com requests

# Test bucket ACL by removing the object key from the URL
curl -s "https://s3.amazonaws.com/<bucket-name>/"
# XML listing = OPEN (public read), AccessDenied = private, NoSuchBucket = doesn't exist

# Enumerate related buckets by naming convention
# Pattern: <org>-<type>-<env>-<random_suffix>
# The random suffix is often the same across all org buckets

# Automated with cloud_enum
cloud_enum -k <known-bucket-name> --quickscan --disable-azure --disable-gcp
cloud_enum -kf /tmp/keyfile.txt -qs --disable-azure --disable-gcp
```

> 🔧 Technique: objects inside a bucket can be publicly accessible even if the bucket itself is not publicly listable. Always try direct object-path access (`aws s3 cp s3://bucket/object -`) even when the bucket returns `AccessDenied` on listing.

---

## Phase 2: API Recon (Attacker Has Their Own AWS Account)

**Goal:** use the CSP's own public API to enumerate the target's resources cross-account.

### 2.1 Find Public AMIs → Leaks Account ID

```bash
# Filter by name/description keyword (much faster than --owners amazon)
aws ec2 describe-images --executable-users all \
  --filters "Name=name,Values=*<target-keyword>*" --profile attacker

# OwnerId in the result = target's 12-digit AWS Account ID
```

### 2.2 Account ID Oracle via S3 ResourceAccount Condition

Uses the IAM policy condition `s3:ResourceAccount StringLike` to binary-search the account ID one digit at a time. Leaves no trace in the **target's** CloudTrail, all events appear only in the attacker's account.

```bash
# Create an IAM user with no permissions in your attacker account
aws iam create-user --user-name enum --profile attacker
aws iam create-access-key --user-name enum --profile attacker
aws configure --profile enum   # enter the enum user's keys

# Apply a test policy to the enum user checking if account starts with "0"
# (See [[Enumerating AWS Cloud Infrastructure#25.3.3]] for full policy JSON)
aws iam put-user-policy --user-name enum --policy-name s3-read \
  --policy-document file://policy-s3-read.json --profile attacker

# Test: Success = first digit is 0, AccessDenied = not 0
aws s3 ls <target-public-bucket> --profile enum

# Change "0*" → "1*" → "10*" → etc. until all 12 digits confirmed
```

> 🔍 Worth remembering generally: Tool `s3-account-search` (Nick Frichette) automates this with IAM roles instead of users, same principle, faster. See [hackingthe.cloud](https://hackingthe.cloud/aws/enumeration/account_id_from_s3_bucket/).

### 2.3 IAM User/Role Existence Oracle via Trust Policy

```bash
# Create a bucket in attacker account, apply a bucket policy with target ARN as Principal
# AWS validates the Principal ARN — invalid = MalformedPolicy error, valid = success
aws s3 mb s3://attacker-dummy-$RANDOM --profile attacker
# Edit grant-s3-bucket-read.json with the target ARN, then:
aws s3api put-bucket-policy --bucket attacker-dummy-XXXXX \
  --policy file://grant-s3-bucket-read.json --profile attacker
# Success = ARN exists. MalformedPolicy = ARN doesn't exist.
```

### 2.4 Role Enumeration + Assumption with Pacu

```bash
# Build a role name wordlist
for gem in ruby amethyst sapphire; do
  for role in lab_admin security_auditor content_creator; do
    echo "${gem}-${role}"
  done
done > /tmp/roles.txt

# In Pacu
pacu
# → create session, import_keys <profile>
run iam__enum_roles --account-id <target-account-id> --word-list /tmp/roles.txt
# Pacu: MalformedPolicy = role doesn't exist, Success = exists, Credentials dumped = assumable
```

---

## Phase 3: Post-Compromise IAM Recon (With IAM Credentials)

**Goal:** scope what you can do, minimise CloudTrail footprint.

### 3.1 Identity Triage

```bash
# Noisiest but most reliable — always logged
aws sts get-caller-identity --profile <compromised>
# → UserId / Account / Arn (username, path, account ID)

# Quiet: account lookup from key ID only — logs in caller's account
aws sts get-access-key-info --access-key-id AKIA... --profile attacker

# Stealthy: Lambda invoke error leaks identity via error message, logged as data event (not event history)
aws lambda invoke --function-name arn:aws:lambda:us-east-1:<acct>:function:nonexistent outfile \
  --profile <compromised>
```

### 3.2 Scope Permissions

```bash
# Check inline + managed policies on the user
aws iam list-user-policies --user-name <user> --profile <compromised>          # inline
aws iam list-attached-user-policies --user-name <user> --profile <compromised>  # managed

# Check group memberships → inherited policies
aws iam list-groups-for-user --user-name <user> --profile <compromised>

# Read each policy document
aws iam list-policy-versions --policy-arn <arn> --profile <compromised>
aws iam get-policy-version --policy-arn <arn> --version-id v1 --profile <compromised>

# Single-call full IAM snapshot (least log noise)
aws iam get-account-authorization-details \
  --filter User Group LocalManagedPolicy \
  --no-cli-pager --profile <compromised> > /tmp/iam-dump.json
```

### 3.3 Analyse IAM Dump with jq

```bash
# Show each user with their groups, attached policies, and inline policies
jq '.UserDetailList[] | {user: .UserName, groups: .GroupList, attached: [.AttachedManagedPolicies[].PolicyName], inline: [(.UserPolicyList // [])[].PolicyName]}' /tmp/iam-dump.json

# Find users with non-empty attached policies (potential misconfigs)
jq '.UserDetailList[] | select(.AttachedManagedPolicies | length > 0) | {user: .UserName, policies: [.AttachedManagedPolicies[].PolicyName]}' /tmp/iam-dump.json

# Read a specific policy document
jq '.Policies[] | select(.PolicyName == "<name>") | .PolicyVersionList[].Document' /tmp/iam-dump.json
```

---

## Phase 4: Privilege Escalation

**Goal:** find a path to higher-privilege credentials.

### Dangerous IAM Permissions (Privesc Vectors)

| Permission | Privesc Path |
|-----------|-------------|
| `iam:CreateAccessKey` on `Resource: *` | Create new access keys for any user, including admins |
| `iam:CreateLoginProfile` / `iam:UpdateLoginProfile` | Set/reset console password for any user |
| `iam:AttachUserPolicy` | Attach AdministratorAccess to yourself |
| `iam:PutUserPolicy` | Create inline admin policy on yourself |
| `iam:CreatePolicyVersion` | Create a new version of a managed policy with admin rights, set as default |
| `iam:SetDefaultPolicyVersion` | Promote an existing non-default version that has more permissions |
| `iam:PassRole` + `ec2:RunInstances` | Launch EC2 with an admin role attached → steal credentials from instance metadata |
| `iam:PassRole` + `lambda:CreateFunction` | Create Lambda with admin role → invoke to execute as that role |
| `iam:UpdateAssumeRolePolicy` | Add yourself as a trusted principal to any role's trust policy |

### ABAC Pitfall

When tags are used as IAM conditions (Attribute-Based Access Control), a policy scoped to `Project: amethyst` gives access to **any** resource with that tag, including admin users accidentally tagged with the project name. Find it:

```bash
# Find policies with tag-based conditions
jq '.Policies[].PolicyVersionList[].Document.Statement[] | select(.Condition != null)' /tmp/iam-dump.json

# Find admin users tagged with project names
jq '.UserDetailList[] | select(.Tags != null) | {user: .UserName, tags: .Tags}' /tmp/iam-dump.json
```

**External resources:**
- [HackTricks. AWS IAM PrivEsc (GitHub)](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-cloud/aws-security/aws-privilege-escalation/)
- [Rhino Security Labs. 21 IAM PrivEsc Techniques](https://github.com/RhinoSecurityLabs/AWS-IAM-Privilege-Escalation)
- [PayloadsAllTheThings. Cloud AWS Pentest](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Cloud%20-%20AWS%20Pentest.md)
