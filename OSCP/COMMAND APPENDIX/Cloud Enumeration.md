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
