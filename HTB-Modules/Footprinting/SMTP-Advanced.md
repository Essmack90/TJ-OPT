---
tags: [module/footprinting, smtp, email, mail-server, level/advanced, practical]
---

# SMTP Enumeration - Practical Application

## Complete SMTP Enumeration Workflow

Phase 1: Service Discovery
Phase 2: Banner Grabbing
Phase 3: Supported Commands Enumeration
Phase 4: User Enumeration (VRFY/EXPN/RCPT)
Phase 5: Open Relay Testing
Phase 6: Manual Email Sending/Spoofing
Phase 7: Header Analysis

---

## Phase 1: Service Discovery

### Nmap Basic Scan

nmap -p25,465,587 -sV -sC 10.129.14.128

### Nmap SMTP Scripts

ls /usr/share/nmap/scripts/smtp-*

Key scripts:
- smtp-commands.nse - List supported commands
- smtp-open-relay.nse - Test for open relay
- smtp-enum-users.nse - Enumerate users
- smtp-vuln-*.nse - Check for vulnerabilities
- smtp-brute.nse - Brute force authentication

### SMTP Command Enumeration

nmap --script smtp-commands -p25 10.129.14.128

Output:
|_smtp-commands: mail1.inlanefreight.htb, PIPELINING, SIZE 10240000, VRFY, ETRN, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING

---

## Phase 2: Banner Grabbing

### Using Netcat

nc -nv 10.129.14.128 25

### Using Telnet

telnet 10.129.14.128 25

### Using OpenSSL (for SSL/TLS ports)

openssl s_client -connect 10.129.14.128:465 -quiet
openssl s_client -connect 10.129.14.128:587 -starttls smtp -quiet

### What to Look For

- Server software (Postfix, Sendmail, Exim, Microsoft Exchange)
- Version numbers
- Domain names
- Supported extensions

---

## Phase 3: Supported Commands Enumeration

### Manual EHLO

EHLO test
250-mail1.inlanefreight.htb
250-PIPELINING
250-SIZE 10240000
250-ETRN
250-ENHANCEDSTATUSCODES
250-8BITMIME
250-DSN
250-SMTPUTF8
250 CHUNKING

### Key Extensions to Note

| Extension | What It Means |
|-----------|---------------|
| PIPELINING | Can send multiple commands at once |
| SIZE 10240000 | Max message size 10MB |
| VRFY | Can verify users |
| ETRN | Remote queue processing |
| 8BITMIME | Supports 8-bit characters |
| DSN | Delivery Status Notifications |
| SMTPUTF8 | Supports UTF-8 in addresses |
| CHUNKING | Supports large messages |
| STARTTLS | Can upgrade to encrypted |
| AUTH | Supports authentication |

---

## Phase 4: User Enumeration

### VRFY Method

VRFY root
VRFY admin
VRFY postmaster
VRFY user

### EXPN Method

EXPN list
EXPN users
EXPN staff

### RCPT TO Method

MAIL FROM: test@test.com
RCPT TO: existinguser@domain.com
RCPT TO: nonexistent@domain.com

### Automated User Enumeration

nmap --script smtp-enum-users -p25 10.129.14.128 --script-args smtp-enum-users.methods={VRFY,EXPN,RCPT}

### SMTP User Enumeration with Metasploit

use auxiliary/scanner/smtp/smtp_enum
set RHOSTS 10.129.14.128
set USER_FILE /usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt
run

### smtp-user-enum Tool

smtp-user-enum -M VRFY -U users.txt -t 10.129.14.128
smtp-user-enum -M EXPN -U users.txt -t 10.129.14.128
smtp-user-enum -M RCPT -U users.txt -t 10.129.14.128

---

## Phase 5: Open Relay Testing

### What is an Open Relay?

An SMTP server configured to forward email from ANY sender to ANY recipient without authentication. Spammers LOVE these.

### Manual Open Relay Test

HELO test
MAIL FROM: <anyone@anywhere.com>
RCPT TO: <test@example.com>
DATA
Subject: Test
This is a test.
.
QUIT

If the server accepts and queues the message, it's an open relay.

### Nmap Open Relay Test

nmap --script smtp-open-relay -p25 10.129.14.128 -v

Output:
| smtp-open-relay: Server is an open relay (16/16 tests)
|  MAIL FROM:<> -> RCPT TO:<relaytest@nmap.scanme.org>
|  MAIL FROM:<antispam@nmap.scanme.org> -> RCPT TO:<relaytest@nmap.scanme.org>
|_ ... (16 tests passed)

### Check Configuration for Open Relay

Look for:
mynetworks = 0.0.0.0/0
smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated

---

## Phase 6: Manual Email Sending/Spoofing

### Send Email with Spoofed Sender

telnet 10.129.14.128 25

EHLO attacker.com
MAIL FROM: <ceo@company.com>
RCPT TO: <employee@company.com>
DATA
From: CEO <ceo@company.com>
To: Employee <employee@company.com>
Subject: Urgent Transfer

Please transfer $50,000 to account 123456 immediately.
.

QUIT

### Send Email with Custom Headers

HELO test
MAIL FROM: <fake@attacker.com>
RCPT TO: <victim@company.com>
DATA
From: "IT Support" <support@company.com>
To: victim@company.com
Subject: Password Reset
Date: Tue, 28 Sept 2021 16:32:51 +0200
Message-ID: <unique-id@company.com>
X-Priority: 1 (Highest)
Importance: High

Your password has expired. Click here to reset: http://attacker.com/reset
.

### Send Email with Attachment (Base64 Encoded)

HELO test
MAIL FROM: <attacker@test.com>
RCPT TO: <victim@company.com>
DATA
From: attacker@test.com
To: victim@company.com
Subject: Invoice
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary"

--boundary
Content-Type: text/plain

Please see attached invoice.

--boundary
Content-Type: application/octet-stream; name="invoice.pdf"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="invoice.pdf"

JVBERi0xLjQKJcOkw7zD...
(base64 encoded content here)

--boundary--
.
QUIT

---

## Phase 7: Header Analysis

### Full Email Headers Example

Return-Path: <cry0l1t3@inlanefreight.htb>
Received: from mail1.inlanefreight.htb (localhost [127.0.0.1])
    by mail1.inlanefreight.htb (Postfix) with ESMTP id 6E1CF1681AB
    for <mrb3n@inlanefreight.htb>; Tue, 28 Sep 2021 16:32:51 +0200 (CEST)
Received: from [10.10.14.4] (unknown [10.10.14.4])
    by mail1.inlanefreight.htb (Postfix) with ESMTP id 3D4F516819A
    for <mrb3n@inlanefreight.htb>; Tue, 28 Sep 2021 16:32:48 +0200 (CEST)
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=inlanefreight.htb;
    s=selector; h=from:to:subject:date;
    bh=base64hash; b=signature
From: <cry0l1t3@inlanefreight.htb>
To: <mrb3n@inlanefreight.htb>
Subject: DB
Date: Tue, 28 Sept 2021 16:32:51 +0200
Message-ID: <20210928143251.12345@mail1.inlanefreight.htb>
Authentication-Results: mail1.inlanefreight.htb;
    spf=pass smtp.mailfrom=cry0l1t3@inlanefreight.htb
    dkim=pass header.d=inlanefreight.htb
X-Spam-Status: No, score=-2.3

### What Headers Reveal

| Header | Information Leaked |
|--------|-------------------|
| Received | Mail server IPs, internal hostnames |
| DKIM-Signature | DomainKeys configuration |
| Authentication-Results | SPF/DKIM/DMARC results |
| X-Spam-Status | Spam filtering rules |
| Message-ID | Server naming convention |
| Received from | Client IP address (if logged) |

---

## Open Relay Testing Script

Save as smtp-open-relay-test.sh:

#!/bin/bash
SERVER=$1
PORT=$2
TEST_DOMAIN="example.com"
TEST_RCPT="test@$TEST_DOMAIN"

echo "[*] Testing SMTP server $SERVER:$PORT for open relay"

{
    sleep 1
    echo "HELO test"
    sleep 1
    echo "MAIL FROM: <anyone@anywhere.com>"
    sleep 1
    echo "RCPT TO: <$TEST_RCPT>"
    sleep 1
    echo "DATA"
    sleep 1
    echo "Subject: Open Relay Test"
    echo "This is a test from an open relay scanner."
    echo "."
    sleep 1
    echo "QUIT"
} | nc -nv $SERVER $PORT

---

## SMTP User Enumeration Script

Save as smtp-user-enum.sh:

#!/bin/bash
SERVER=$1
USERLIST=$2

while read user; do
    {
        sleep 1
        echo "HELO test"
        sleep 1
        echo "VRFY $user"
        sleep 1
        echo "QUIT"
    } | nc -nv $SERVER 25 | grep -E "^250|^251|^252" && echo "[+] User found: $user"
done < $USERLIST

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| telnet | Manual interaction | Quick testing |
| nc | Scripting | Automated tests |
| Nmap scripts | Comprehensive scans | Initial enumeration |
| smtp-user-enum | User enumeration | Targeted user discovery |
| Metasploit aux modules | Exploitation | Password attacks |
| swaks | Email sending | Spoofing tests |

---

## Key Takeaways

- SMTP uses ports 25, 465, and 587
- EHLO reveals supported extensions
- VRFY/EXPN can enumerate users (if enabled)
- 252 responses may be false positives
- Open relays allow anyone to send email
- Spoofed emails can bypass SPF if relay is misconfigured
- Email headers reveal server IPs and hostnames
- Always test manually after automated scans
- Check for STARTTLS support for encrypted connections
- Document all discovered users and addresses
