---
tags: [module/footprinting, staff, osint, linkedin, level/beginner]
---

# Staff Enumeration - Beginner's Guide

## Why Staff Enumeration Matters

Employees are a goldmine of information. Their profiles, job postings, and shared content reveal:

- Technologies the company uses
- Programming languages and frameworks
- Databases and infrastructure
- Security measures
- Potential vulnerabilities

Think of employees as walking documentation of the company's entire tech stack.

---

## Source 1: Job Postings

Job postings are the BEST source of technical information. Companies literally tell you what they use.

### What to Look For

| Category | Examples |
|----------|----------|
| Programming Languages | Java, C#, Python, PHP, Ruby, JavaScript |
| Web Frameworks | Django, Flask, Spring, ASP.NET, React, Angular |
| Databases | PostgreSQL, MySQL, Oracle, SQL Server, MongoDB |
| DevOps Tools | Docker, Kubernetes, Jenkins, Git |
| Cloud Services | AWS, Azure, GCP |
| Atlassian Suite | Jira, Confluence, Bitbucket |
| Testing Frameworks | pytest, JUnit, NUnit |
| Version Control | Git, SVN, Mercurial, Perforce |

### Example Job Posting Analysis

Required Skills:
- 3-10+ years experience
- Java, C#, C++, Python
- PostgreSQL, MySQL, SQL Server, Oracle
- Flask, Django, Spring, ASP.NET MVC
- pytest, JUnit, NUnit
- Git, SVN, Mercurial
- Docker, Kubernetes (desired)
- Atlassian Suite (desired)

### What This Tells Us

| Finding | Implication |
|---------|-------------|
| Java, C#, Python | Multiple tech stacks - complex environment |
| Multiple databases | Data diversity, potential SQL injection points |
| Django, Flask | Python web apps - check for Django misconfigs |
| Docker, Kubernetes | Containerized environment - potential container escapes |
| Atlassian Suite | Jira/Confluence instances - possible open instances |
| Git, SVN | Source control - potential exposed repos |

---

## Source 2: LinkedIn Employee Profiles

LinkedIn is a treasure trove. Employees list their skills, projects, and technologies.

### Search Filters

LinkedIn allows filtering by:
- Current companies
- Past companies
- Locations
- Schools
- Industry
- Profile language
- Name and title
- Connections

### What to Look For in Profiles

| Profile Section | What It Reveals |
|-----------------|-----------------|
| About | Personal interests, focus areas |
| Experience | Projects they worked on, technologies used |
| Skills | Endorsed technologies, expertise level |
| Education | Academic background, potential weak spots |
| Projects | Specific applications, code repos |
| Recommendations | Client details, project scope |

### Example Profile Analysis

Profile shows:
- Vice President Software Engineer
- Associate Software Engineer
- Leading CRM mobile app development
- Delivered BrokerVotes system
- Skills: Java, React, Slang, Elastic, Kafka

### What This Tells Us

| Finding | Implication |
|---------|-------------|
| CRM mobile app | Mobile backend to test |
| BrokerVotes system | Custom application, likely web-based |
| Java | Spring framework possible |
| React | Frontend, check for client-side vulns |
| Elastic | Elasticsearch cluster, maybe exposed |
| Kafka | Message queue, potential misconfigs |

---

## Source 3: Employee GitHub Repositories

Many developers have public GitHub repos. They often contain:

- Code samples
- Personal projects
- Work-related snippets
- Configuration files
- Hardcoded credentials
- JWT tokens
- API keys

### What to Look For in GitHub

| Item | Risk |
|------|------|
| Hardcoded API keys | Critical - immediate access |
| JWT tokens | Authentication bypass |
| .env files | Database credentials |
| config files | Service configurations |
| Database dumps | All data |
| SSH keys | System access |
| Employee email | Phishing target |
| Company name in code | Links to employer |

### Example GitHub Discovery

From an employee's public repo:
- Personal email address
- JWT token in code
- Reference to internal project

The JWT token might still be valid. Could grant access to internal applications.

---

## Source 4: Employee Blogs and Technical Writing

Employees often blog about their work. This reveals:
- Technologies they're learning
- Problems they're solving
- Conferences they attend
- Tools they recommend
- Security measures they implement

---

## Source 5: Conference Talks and Presentations

Employees who speak at conferences share:
- Company use cases
- Architecture diagrams
- Tech stack details
- Security approaches
- Future plans

Slides often contain screenshots of internal systems.

---

## The Staff Enumeration Principles

### Principle 1: More than meets the eye
You see a job posting. What you DON'T see is the entire tech stack, the security measures, and the potential vulnerabilities.

### Principle 2: Visible vs Invisible
Visible: Employee skills and job titles
Invisible: The actual code, configurations, and infrastructure

### Principle 3: Always more information
One employee profile leads to:
- Their GitHub
- Their blog
- Their conference talks
- Their colleagues
- Their company's tech stack

---

## Key Takeaways

- Job postings are TECH SPECS - read them carefully
- LinkedIn profiles reveal employee skills and focus
- GitHub repos can contain leaked credentials
- Employee blogs show current tech interests
- Conference talks expose architecture
- Multiple employees = multiple sources of info
- Cross-reference findings between employees
- Document all technologies discovered
- Build a complete tech stack inventory
- This guides all later testing

---

## Quick Reference Checklist

Job Postings:
- Programming languages
- Frameworks
- Databases
- DevOps tools
- Cloud providers
- Security requirements

LinkedIn Profiles:
- Current role
- Past roles
- Skills
- Projects
- Recommendations

GitHub:
- Code snippets
- Configuration files
- Hardcoded secrets
- Personal info
- Work references

Blogs/Talks:
- Technologies used
- Architecture decisions
- Security measures
- Future plans
