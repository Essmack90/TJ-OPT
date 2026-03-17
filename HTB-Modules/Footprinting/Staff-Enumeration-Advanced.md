---
tags: [module/footprinting, staff, osint, linkedin, github, level/advanced, practical]
---

# Staff Enumeration - Practical Application

## Complete Staff Enumeration Workflow

Phase 1: Job Posting Analysis
Phase 2: LinkedIn Employee Identification
Phase 3: GitHub Profile Discovery
Phase 4: Code and Credential Hunting
Phase 5: Cross-Reference and Correlation
Phase 6: Technology Stack Mapping
Phase 7: Attack Surface Expansion

---

## Phase 1: Job Posting Analysis

### Automated Job Posting Scraping

Save as `job-scraper.sh`:

#!/bin/bash
COMPANY=$1
curl -s "https://www.linkedin.com/jobs/search/?keywords=$COMPANY" | grep -o 'job/[0-9]*' | sort -u

### Job Posting Tech Stack Extractor

Create a list of technologies to look for:

languages=("Java" "C#" "C++" "Python" "PHP" "Ruby" "JavaScript" "TypeScript" "Go" "Rust")
frameworks=("Django" "Flask" "Spring" "ASP.NET" "React" "Angular" "Vue" "Node.js" "Express")
databases=("PostgreSQL" "MySQL" "SQL Server" "Oracle" "MongoDB" "Redis" "Elasticsearch" "Cassandra")
devops=("Docker" "Kubernetes" "Jenkins" "GitLab" "Terraform" "Ansible" "AWS" "Azure" "GCP")
security=("CISSP" "OSCP" "CEH" "CompTIA Security+" "OWASP" "penetration testing" "vulnerability assessment")

### Real-World Example Analysis

From the module's job posting:

Required Skills:
Java, C#, C++, Python, Ruby, PHP, Perl
PostgreSQL, MySQL, SQL Server, Oracle
Flask, Django, Spring, ASP.NET MVC
pytest, JUnit, NUnit, xUnit
Git, SVN, Mercurial, Perforce
Atlassian Suite (Confluence, Jira, Bitbucket)
Docker, Kubernetes
Redis, NumPy

### Technology Inference

| Technology | Inferred Infrastructure |
|------------|------------------------|
| Java, C# | Enterprise applications, Windows servers |
| Python | Web apps, automation scripts |
| PostgreSQL, MySQL | SQL databases, potential injection points |
| Django, Flask | Python web apps - check Django misconfigs |
| Spring | Java web apps - check Spring Boot actuators |
| ASP.NET | Windows web servers - IIS |
| Docker, Kubernetes | Containerized environment |
| Jira, Confluence | Atlassian instances - check for open access |
| Redis | In-memory database - check for auth bypass |
| Git, SVN | Source control - exposed repos? |

---

## Phase 2: LinkedIn Employee Identification

### LinkedIn Search Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| company: | Current company | company:"InlaneFreight" |
| past_company: | Past company | past_company:"InlaneFreight" |
| title: | Job title | title:"Software Engineer" |
| school: | Education | school:"University of Berlin" |
| location: | Geographic | location:"Germany" |

### LinkedIn Search URL Patterns

Current employees:
https://www.linkedin.com/search/results/people/?currentCompany=%5B"12345"%5D

Past employees:
https://www.linkedin.com/search/results/people/?pastCompany=%5B"12345"%5D

By title:
https://www.linkedin.com/search/results/people/?title="Software%20Engineer"

### Employee Role Categories

| Role Type | What They Know |
|-----------|----------------|
| Developers | Code, frameworks, databases |
| DevOps | Infrastructure, cloud, containers |
| Security | Defenses, tools, measures |
| IT Support | Internal systems, access |
| Management | Roadmaps, priorities |
| HR | Employees, structure |

### Target Priority

High Value Employees:
- Lead Developers (know architecture)
- DevOps Engineers (know infrastructure)
- Security Engineers (know defenses)
- CISO/CTO (know everything)

Medium Value:
- Developers (know code)
- IT Support (know internal systems)
- Project Managers (know timelines)

Low Value:
- Sales (know customers, not tech)
- Marketing (know public stuff)
- Admin (know people, not tech)

---

## Phase 3: GitHub Profile Discovery

### Find Employees on GitHub

Search patterns:
"Company Name" in GitHub bio
"@company.com" in GitHub email
Company name in repositories
Filenames containing company name

### GitHub Search Queries

Find company employees:
org:CompanyName
CompanyName in:email
CompanyName in:bio
CompanyName in:readme

Find company-related repos:
"CompanyName" filename:.env
"CompanyName" filename:config
"CompanyName" extension:pem
"CompanyName" extension:key
"CompanyName" extension:sql

### Automated GitHub Search

Requires GitHub token.

#!/bin/bash
COMPANY=$1
TOKEN="your_github_token"

curl -H "Authorization: token $TOKEN" \
     "https://api.github.com/search/code?q=$COMPANY+extension:env" | jq '.items[] | {name: .name, path: .path, repo: .repository.html_url}'

### What to Hunt For

| File Pattern | Contains |
|--------------|----------|
| .env | Database credentials, API keys |
| config.* | Configuration settings |
| *.pem, *.key | SSL/SSH private keys |
| *.sql | Database dumps |
| Dockerfile | Container configuration |
| docker-compose.yml | Full stack config |
| Jenkinsfile | CI/CD pipeline |
| .aws/credentials | AWS keys |
| id_rsa | SSH private key |

---

## Phase 4: Code and Credential Hunting

### JWT Token Discovery

JWT tokens in code can grant access.

Look for:
jwt.encode(
JWT_SECRET
eyJ (JWT token start)

Test found tokens:
curl -H "Authorization: Bearer TOKEN" https://target.com/api

### API Key Discovery

Look for patterns:
api_key = 
API_KEY = 
aws_access_key_id = 
AZURE_STORAGE_KEY = 
sk_live_ (Stripe)
AKIA (AWS key prefix)

### Hardcoded Credentials

Search for:
password =
passwd =
pwd =
db_password =
connection_string =

### SSH Key Discovery

id_rsa files:
-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----

When found:
chmod 600 id_rsa
ssh -i id_rsa root@target.com
ssh -i id_rsa ec2-user@target.com
ssh -i id_rsa ubuntu@target.com

---

## Phase 5: Cross-Reference and Correlation

### Employee to Technology Mapping

| Employee | Title | Skills | GitHub | Inferred Tech |
|----------|-------|--------|--------|---------------|
| John Doe | Lead Dev | Java, Spring | john/demo-app | Spring Boot |
| Jane Smith | DevOps | AWS, K8s | jane/terraform | AWS EKS |
| Bob Wilson | Security | Python, Django | bob/sec-tools | Django app |

### LinkedIn to GitHub Linking

Look for:
- GitHub links in LinkedIn profiles
- Personal website links
- Email addresses (name@company.com)
- Username patterns (first.last, flast)

### Technology Stack Compilation

Create a master list:

# Backend
- Java (Spring Boot)
- Python (Django, Flask)
- C# (ASP.NET)

# Databases
- PostgreSQL
- MySQL
- Redis

# Infrastructure
- AWS (EC2, S3)
- Docker
- Kubernetes

# Security
- JWT auth
- OAuth
- Cloudflare

---

## Phase 6: Technology Stack Mapping

### From Job Postings

| Tech | Use | Attack Vector |
|------|-----|---------------|
| Django | Web app | Django misconfigs, debug mode |
| Spring | Java app | Spring Boot actuators |
| JWT | Auth | Weak secrets, alg none |
| Redis | Cache | No auth, SSRF |
| Docker | Containers | Container escapes |
| Kubernetes | Orchestration | K8s misconfigs |
| AWS | Cloud | S3 buckets, IAM |

### From Employee Profiles

If multiple employees mention same tech:
- It's core to the company
- Heavily used
- Likely deployed in production

### From GitHub Repos

Check for:
- Version numbers in requirements.txt
- Configuration examples
- Database schemas
- API endpoints
- Authentication flows

---

## Phase 7: Attack Surface Expansion

### Tech-Specific Attack Vectors

| Technology | Check For |
|------------|-----------|
| Django | DEBUG=True, admin panel, SQL injection |
| Flask | Debug mode, secret key, SSTI |
| Spring | Actuators, /env, /heapdump |
| JWT | alg:none, weak secret, kid injection |
| Redis | No auth, public exposure |
| AWS S3 | Public buckets, listing enabled |
| Kubernetes | Public API, anonymous auth |
| Docker | Registry exposure, socket |

### Create Target List

From tech stack, build targets:

Web Applications:
- main-site.com (Django)
- api.company.com (Spring)
- admin.company.com (maybe Flask)

Infrastructure:
- s3.amazonaws.com/company-bucket
- redis.company.com:6379
- k8s-api.company.com:6443

Atlassian:
- jira.company.com
- confluence.company.com
- bitbucket.company.com

---

## Real-World Example Analysis

From the module's job posting and employee profiles:

### Job Posting Tech Stack
- Java, C#, Python
- PostgreSQL, MySQL, Oracle
- Flask, Django, Spring, ASP.NET
- Docker, Kubernetes
- Atlassian Suite
- Redis

### Employee 1 Profile
- W3C specs, Web components
- React, Svelte, AngularJS
- GitHub link with open source projects

### Employee 2 Profile
- Vice President Software Engineer
- Led CRM mobile app development
- Delivered BrokerVotes system
- Skills: Java, React, Elastic, Kafka

### Compiled Attack Surface

1. Web Apps:
   - Django app (main site)
   - Spring app (API?)
   - React frontend (maybe SPA)

2. Databases:
   - PostgreSQL (main DB)
   - MySQL (legacy?)
   - Oracle (enterprise)

3. Infrastructure:
   - Docker containers
   - Kubernetes cluster
   - Redis cache

4. Atlassian:
   - Jira (project mgmt)
   - Confluence (wiki)
   - Bitbucket (code)

5. Custom Apps:
   - CRM mobile app (API)
   - BrokerVotes system (web app)

6. Employee GitHub:
   - Open source projects
   - Possibly work-related code
   - Might contain credentials

---

## Complete Automation Script

Save as `staff-enum.sh`:

#!/bin/bash
COMPANY=$1
OUTPUT_DIR="staff-enum-$COMPANY"
mkdir -p $OUTPUT_DIR

echo "[*] Starting staff enumeration for $COMPANY"

echo "[*] Searching LinkedIn for employees..."
echo "Visit: https://www.linkedin.com/search/results/people/?keywords=$COMPANY" > $OUTPUT_DIR/linkedin.txt

echo "[*] Searching GitHub for company repos..."
echo "Visit: https://github.com/search?q=$COMPANY&type=code" >> $OUTPUT_DIR/github.txt

echo "[*] Technologies to hunt for:" > $OUTPUT_DIR/tech-stack.txt
echo "Languages: Java, C#, Python, PHP, Ruby, JavaScript, TypeScript" >> $OUTPUT_DIR/tech-stack.txt
echo "Frameworks: Django, Flask, Spring, ASP.NET, React, Angular, Vue" >> $OUTPUT_DIR/tech-stack.txt
echo "Databases: PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis" >> $OUTPUT_DIR/tech-stack.txt
echo "DevOps: Docker, Kubernetes, AWS, Azure, GCP, Jenkins" >> $OUTPUT_DIR/tech-stack.txt
echo "Security: JWT, OAuth, SAML, Cloudflare, WAF" >> $OUTPUT_DIR/tech-stack.txt

echo "[*] Creating attack surface list..."
cat > $OUTPUT_DIR/attack-surface.txt << 'INNER'
Potential Targets:
- main.$COMPANY (main website)
- api.$COMPANY (API endpoints)
- admin.$COMPANY (admin panel)
- dev.$COMPANY (development)
- jira.$COMPANY (Jira)
- confluence.$COMPANY (Confluence)
- bitbucket.$COMPANY (Bitbucket)
- git.$COMPANY (Git server)
- jenkins.$COMPANY (Jenkins)
- docker.$COMPANY (Docker registry)
- k8s.$COMPANY (Kubernetes API)
- s3.amazonaws.com/$COMPANY (AWS S3)
- $COMPANY.blob.core.windows.net (Azure)
- $COMPANY.storage.googleapis.com (GCP)
INNER

echo "[*] Staff enumeration complete. Results in $OUTPUT_DIR/"
echo "Check LinkedIn, GitHub, and tech stack manually."

---

## Key Takeaways

- Job postings are the ultimate tech spec document
- LinkedIn reveals employee roles and skills
- GitHub can leak code and credentials
- Cross-reference multiple employees for consensus
- Build a complete technology stack inventory
- Map technologies to specific attack vectors
- Create target list from tech stack
- One employee's mistake can compromise everything
- JWT tokens in public repos = instant access
- SSH keys in public repos = system access
- Document everything for the final report

---

## Quick Reference Card

JOB POSTINGS:
    Extract languages, frameworks, databases, tools
    Build tech stack inventory
    Note security requirements

LINKEDIN:
    Search current/past employees
    Filter by title and skills
    Note projects and technologies

GITHUB:
    Search company name
    Hunt for .env, config, .key, .pem, .sql
    Look for hardcoded credentials

ATTACK SURFACE:
    main.$company
    api.$company
    admin.$company
    dev.$company
    jira.$company
    confluence.$company
    bitbucket.$company
    jenkins.$company
    docker.$company
    s3.amazonaws.com/$company
    $company.blob.core.windows.net
    $company.storage.googleapis.com
