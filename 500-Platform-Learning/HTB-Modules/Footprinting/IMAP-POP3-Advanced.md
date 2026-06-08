---
tags: [module/footprinting, imap, pop3, email, mail-client, level/advanced, practical]
---

# IMAP/POP3 Enumeration - Practical Application

## Complete Mail Server Enumeration Workflow

Phase 1: Service Discovery
Phase 2: Banner Grabbing
Phase 3: Capabilities Enumeration
Phase 4: Authentication Testing
Phase 5: Mailbox Enumeration
Phase 6: Email Downloading/Analysis
Phase 7: SSL Certificate Analysis

---

## Phase 1: Service Discovery

### Nmap Port Scan

nmap -p110,143,993,995 -sV -sC 10.129.14.128

### Nmap Scripts

ls /usr/share/nmap/scripts/imap-*
ls /usr/share/nmap/scripts/pop3-*

Key scripts:
- imap-capabilities.nse
- pop3-capabilities.nse
- imap-ntlm-info.nse
- pop3-ntlm-info.nse
- imap-brute.nse
- pop3-brute.nse

### Service Scan with Scripts

nmap --script imap-capabilities,pop3-capabilities -p110,143,993,995 10.129.14.128

---

## Phase 2: Banner Grabbing

### POP3 Banner

nc -nv 10.129.14.128 110
telnet 10.129.14.128 110
openssl s_client -connect 10.129.14.128:995 -quiet

### IMAP Banner

nc -nv 10.129.14.128 143
telnet 10.129.14.128 143
openssl s_client -connect 10.129.14.128:993 -quiet

### What Banners Reveal

- Server software (Dovecot, Courier, Microsoft Exchange)
- Version numbers
- Capabilities
- Hostnames

Example:
* OK [CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE LITERAL+ AUTH=PLAIN] HTB-Academy IMAP4 v.0.21.4

---

## Phase 3: Capabilities Enumeration

### POP3 Capabilities

openssl s_client -connect 10.129.14.128:995 -quiet
CAPA

Response:
+OK Capability list follows
TOP
UIDL
RESP-CODES
PIPELINING
USER
SASL PLAIN
. 

### IMAP Capabilities

openssl s_client -connect 10.129.14.128:993 -quiet
1 CAPABILITY

Response:
* CAPABILITY IMAP4rev1 SASL-IR LOGIN-REFERRALS ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE SNIPPET=FUZZY PREVIEW=FUZZY LITERAL+ NOTIFY SPECIAL-USE AUTH=PLAIN
1 OK Pre-login capabilities listed

### Important Capabilities

| Capability | What It Means |
|------------|---------------|
| AUTH=PLAIN | Plain text authentication |
| AUTH=LOGIN | Login authentication |
| STARTTLS | Can upgrade to encryption |
| SASL-IR | SASL initial response |
| ID | Server identification |
| IDLE | Push notifications |
| LITERAL+ | Large message support |
| CHILDREN | Child folders |
| NAMESPACE | Folder hierarchy |
| UIDPLUS | UID operations |

---

## Phase 4: Authentication Testing

### Test Default/Weak Credentials

Try common combinations:
- username:username
- username:password
- admin:admin
- root:root
- user:pass
- test:test
- backup:backup
- robin:robin

### Manual Authentication (POP3)

openssl s_client -connect 10.129.14.128:995 -quiet
USER robin
PASS robin
STAT
LIST

### Manual Authentication (IMAP)

openssl s_client -connect 10.129.14.128:993 -quiet
1 LOGIN robin robin
2 LIST "" *
3 SELECT INBOX
4 FETCH 1 body[]
5 LOGOUT

### Using curl

curl -k 'imaps://10.129.14.128/INBOX' --user robin:robin
curl -k 'pop3s://10.129.14.128' --user robin:robin

---

## Phase 5: Mailbox Enumeration

### List All Folders (IMAP)

openssl s_client -connect 10.129.14.128:993 -quiet
1 LOGIN robin robin
2 LIST "" *
3 LSUB "" *
4 LOGOUT

### Check Mailbox Status

openssl s_client -connect 10.129.14.128:993 -quiet
1 LOGIN robin robin
2 SELECT INBOX
3 STATUS INBOX (MESSAGES UNSEEN RECENT)
4 LOGOUT

### POP3 Mailbox Status

openssl s_client -connect 10.129.14.128:995 -quiet
USER robin
PASS robin
STAT
LIST
QUIT

### Automated Mailbox Enumeration Script

Save as imap-enum.sh:

#!/bin/bash
SERVER=$1
USER=$2
PASS=$3

{
    sleep 1
    echo "1 LOGIN $USER $PASS"
    sleep 1
    echo "2 LIST "" *"
    sleep 1
    echo "3 LOGOUT"
} | openssl s_client -connect $SERVER:993 -quiet 2>/dev/null

---

## Phase 6: Email Downloading and Analysis

### Download All Emails (POP3)

Save as pop3-download.sh:

#!/bin/bash
SERVER=$1
USER=$2
PASS=$3
OUTPUT_DIR="pop3-emails-$USER"
mkdir -p $OUTPUT_DIR

{
    echo "USER $USER"
    echo "PASS $PASS"
    echo "STAT"
    echo "LIST"
} | openssl s_client -connect $SERVER:995 -quiet 2>/dev/null > $OUTPUT_DIR/headers.txt

# Parse message count from STAT response
COUNT=$(grep -o '^+OK [0-9]*' $OUTPUT_DIR/headers.txt | cut -d' ' -f2)

for i in $(seq 1 $COUNT); do
    {
        echo "USER $USER"
        echo "PASS $PASS"
        echo "RETR $i"
        echo "QUIT"
    } | openssl s_client -connect $SERVER:995 -quiet 2>/dev/null > "$OUTPUT_DIR/email-$i.txt"
    echo "Downloaded email $i"
done

echo "All emails saved to $OUTPUT_DIR/"

### Download All Emails (IMAP)

Save as imap-download.sh:

#!/bin/bash
SERVER=$1
USER=$2
PASS=$3
OUTPUT_DIR="imap-emails-$USER"
mkdir -p $OUTPUT_DIR

# Get list of message IDs
MSGS=$(echo -e "1 LOGIN $USER $PASS\n2 SELECT INBOX\n3 SEARCH ALL\n4 LOGOUT" | openssl s_client -connect $SERVER:993 -quiet 2>/dev/null | grep -E '^\* SEARCH' | cut -d' ' -f3-)

for msg in $MSGS; do
    {
        echo "1 LOGIN $USER $PASS"
        echo "2 SELECT INBOX"
        echo "3 FETCH $msg body[]"
        echo "4 LOGOUT"
    } | openssl s_client -connect $SERVER:993 -quiet 2>/dev/null > "$OUTPUT_DIR/email-$msg.txt"
    echo "Downloaded email $msg"
done

echo "All emails saved to $OUTPUT_DIR/"

### Extract Information from Emails

grep -i "password" email-*.txt
grep -i "confidential" email-*.txt
grep -i "secret" email-*.txt
grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" email-*.txt
grep -E "(http|https)://[a-zA-Z0-9./?=_-]*" email-*.txt

---

## Phase 7: SSL Certificate Analysis

### Extract Certificate Details

openssl s_client -connect 10.129.14.128:993 2>/dev/null | openssl x509 -text -noout

### Certificate Information

| Field | What It Reveals |
|-------|-----------------|
| Subject CN | Server hostname |
| Subject O | Organization name |
| Subject L | Location (city) |
| Subject ST | State/Province |
| Subject C | Country |
| Issuer | Certificate authority |
| Validity | Certificate age |
| SAN | Alternative hostnames |
| Email | Admin contact |

### Example Certificate

Subject: C=US, ST=California, L=Sacramento, O=Inlanefreight, OU=Customer Support, CN=mail1.inlanefreight.htb, emailAddress=cry0l1t3@inlanefreight.htb

This reveals:
- Company: Inlanefreight
- Location: Sacramento, California
- Server: mail1.inlanefreight.htb
- Admin email: cry0l1t3@inlanefreight.htb

---

## Complete Mail Server Enumeration Script

Save as mail-enum.sh:

#!/bin/bash
TARGET=$1
USERLIST=$2
PASSLIST=$3
OUTPUT_DIR="mail-enum-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting mail server enumeration on $TARGET"

echo "[*] Nmap scan..."
nmap -p110,143,993,995 --script imap-capabilities,pop3-capabilities -oN $OUTPUT_DIR/nmap.txt $TARGET

echo "[*] SSL certificate analysis..."
{
    echo "POP3S certificate:"
    openssl s_client -connect $TARGET:995 2>/dev/null | openssl x509 -text -noout
    echo ""
    echo "IMAPS certificate:"
    openssl s_client -connect $TARGET:993 2>/dev/null | openssl x509 -text -noout
} > $OUTPUT_DIR/certificates.txt

echo "[*] Banner grabbing..."
nc -nv $TARGET 110 2>&1 | head -5 > $OUTPUT_DIR/pop3-banner.txt
nc -nv $TARGET 143 2>&1 | head -5 > $OUTPUT_DIR/imap-banner.txt

echo "[*] Checking capabilities..."
{
    echo "CAPA" | openssl s_client -connect $TARGET:995 -quiet 2>/dev/null
} > $OUTPUT_DIR/pop3-capabilities.txt

{
    echo "1 CAPABILITY" | openssl s_client -connect $TARGET:993 -quiet 2>/dev/null
} > $OUTPUT_DIR/imap-capabilities.txt

echo "[*] Testing default credentials..."
for user in admin root postmaster robin cry0l1t3 mrb3n; do
    for pass in $user password $user$user Password123; do
        echo "Testing $user:$pass"
        {
            echo "USER $user"
            echo "PASS $pass"
            echo "STAT"
            echo "QUIT"
        } | openssl s_client -connect $TARGET:995 -quiet 2>/dev/null | grep -q "+OK" && echo "[+] Valid POP3 credentials: $user:$pass" >> $OUTPUT_DIR/credentials.txt
    done
done

echo "[*] Mail server enumeration complete. Check $OUTPUT_DIR/"

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| telnet | Manual interaction | Quick testing |
| openssl s_client | Encrypted connections | SSL/TLS services |
| curl | Automated access | Scripting |
| Nmap scripts | Discovery | Initial enumeration |
| Custom scripts | Downloading emails | Data extraction |

---

## Key Takeaways

- POP3 on 110 (plain), 995 (SSL)
- IMAP on 143 (plain), 993 (SSL)
- CAPA command reveals server capabilities
- LOGIN command authenticates users
- LIST shows all mail folders
- SELECT chooses which folder to access
- FETCH retrieves email content
- RETR (POP3) downloads emails
- SSL certificates reveal hostnames and organization
- Emails contain sensitive information
- Weak credentials (robin:robin) are common
- Document all discovered mailboxes
