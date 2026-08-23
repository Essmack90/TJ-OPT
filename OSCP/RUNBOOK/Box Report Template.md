# Penetration Test Report — {{BoxName}}

**Date:** {{Date}}
**Platform:** HTB / PG / OffSec Lab
**Difficulty:** Easy / Medium / Hard
**OS:** Linux / Windows
**IP:** {{BoxIP}}

---

## 1. Executive Summary

**{{BoxName}}** is a {{difficulty}} {{OS}} machine. The attack path involved:

1. {{Brief step 1, e.g. "Web enumeration revealing an exposed admin panel"}}
2. {{Brief step 2, e.g. "Default credentials granting initial foothold"}}
3. {{Brief step 3, e.g. "Writable cron script exploited for root"}}

**Initial access:** {{How shell was obtained}}
**Privilege escalation:** {{How root/SYSTEM was obtained}}

---

## 2. Vulnerability Summary

| # | Vulnerability | Severity | Location |
|---|--------------|----------|----------|
| 1 | {{e.g. Anonymous FTP with sensitive files}} | High | FTP port 21 |
| 2 | {{e.g. Weak credentials on admin panel}} | High | HTTP port 80 |
| 3 | {{e.g. Writable cron script running as root}} | Critical | /etc/cron.d/ |

---

## 3. Attack Narrative

### 3.1 Reconnaissance

**Full port scan:**

```
nmap -p- --min-rate 10000 {{BoxIP}}
```

> 📸 ![[nmap-allports.png]]

**Key open ports:**

| Port | Service | Version |
|------|---------|---------|
| {{port}} | {{service}} | {{version}} |

**Targeted scan:**

```
nmap -sC -sV -p {{ports}} {{BoxIP}}
```

> 📸 ![[nmap-services.png]]

---

### 3.2 Enumeration

*(Document what you found on each service, just the meaningful findings, not every command run.)*

**{{Service/port heading, e.g. "HTTP — Port 80"}}**

{{What you found. E.g.: "Directory brute-force with feroxbuster revealed /admin/ returning 200. Navigating to the page presented a login form."}}

> 📸 ![[{{relevant screenshot}}.png]]

---

### 3.3 Initial Foothold

**Vulnerability:** {{e.g. Default credentials on admin panel}}

**Steps:**

1. {{Step 1}}
2. {{Step 2}}
3. {{Step 3, e.g. "Uploaded PHP reverse shell via file upload form"}}

**Listener:**

```bash
nc -lvnp $Port
```

**Shell obtained as:** `{{username}}` on `{{hostname}}`

> 📸 ![[foothold-whoami.png]]

---

### 3.4 Privilege Escalation

**Vulnerability:** {{e.g. Cron job running user-writable script as root}}

**Discovery:**

{{How you found it, e.g. "linpeas.sh highlighted a cron entry in /etc/cron.d/cleanup running /opt/cleanup.sh as root every minute. The script was world-writable."}}

> 📸 ![[privesc-finding.png]]

**Exploitation:**

```bash
{{The winning command(s)}}
```

> 📸 ![[privesc-exploit.png]]

---

## 4. Proof of Exploitation

### User Flag

> 📸 ![[user-flag.png]]

```
{{flag value}}
```

### Root / SYSTEM Flag

> 📸 ![[PROOF-{{BoxName}}.png]]

*(Screenshot must show: `whoami` → root/SYSTEM, `hostname`, and flag content, all in one frame)*

```
{{flag value}}
```

---

## 5. Tools Used

| Tool | Purpose |
|------|---------|
| nmap | Port scanning |
| {{feroxbuster / gobuster}} | Directory brute-force |
| {{linpeas / winpeas}} | PrivEsc enumeration |
| {{others}} | {{purpose}} |

---

## 6. Credentials Found

| Username | Password / Hash | Service | Notes |
|----------|----------------|---------|-------|
| {{user}} | {{pass/hash}} | {{SSH/HTTP/etc}} | {{where found}} |

---

## 7. Remediation Recommendations

| Vulnerability | Recommendation |
|--------------|----------------|
| {{Vuln 1}} | {{e.g. Change default credentials immediately}} |
| {{Vuln 2}} | {{e.g. Restrict file upload to non-executable types}} |
| {{Vuln 3}} | {{e.g. Remove world-write permissions from /opt/cleanup.sh}} |

---

## 8. Lessons Learned / Module Links

*What did this box teach or reinforce?*

- {{e.g. "FTP anonymous login → checked [[06. Information Gathering#FTP|Information Gathering#FTP]]"}}
- {{e.g. "Cron abuse → reinforced [[18. Linux Privilege Escalation#Cron|Linux Privilege Escalation#Cron]]"}}
- {{Note anything the box covered that ISN'T yet in a module note, flag it for addition}}
