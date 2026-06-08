---
tags: [module/footprinting, smtp, email, mail-server, level/beginner]
---

# SMTP Enumeration - Beginner's Guide

## What is SMTP?

SMTP (Simple Mail Transfer Protocol) is the standard protocol for sending emails across the Internet. Think of it as the digital postal service - it handles getting your email from your computer to the recipient's mail server.

---

## How Email Delivery Works

1. **You write an email** in your email client (Outlook, Gmail, Thunderbird)
2. **Your client sends it** to an SMTP server (usually your provider's mail server)
3. **SMTP server finds** the recipient's mail server using DNS
4. **SMTP servers talk** to each other to transfer the email
5. **Recipient picks it up** using POP3 or IMAP

---

## Key Components

| Component | Full Name | Role |
|-----------|-----------|------|
| MUA | Mail User Agent | Your email client (Outlook, Thunderbird) |
| MSA | Mail Submission Agent | First server that accepts your email |
| MTA | Mail Transfer Agent | Relays email between servers |
| MDA | Mail Delivery Agent | Delivers email to recipient's mailbox |
| Relay | Open Relay | Server that forwards email for others |

---

## SMTP Ports

| Port | Protocol | Use |
|------|----------|-----|
| 25 | SMTP | Standard SMTP (often blocked for spam prevention) |
| 465 | SMTPS | SMTP over SSL (encrypted from start) |
| 587 | SMTP | SMTP with STARTTLS (upgrades to encryption) |

**Important:** Port 25 is often used for server-to-server communication. Port 587 is for authenticated clients.

---

## SMTP Commands

| Command | Description | Example |
|---------|-------------|---------|
| HELO | Identify yourself to the server | HELO mail.example.com |
| EHLO | Extended HELO (ESMTP) | EHLO client |
| MAIL FROM | Specify sender | MAIL FROM: <user@domain.com> |
| RCPT TO | Specify recipient | RCPT TO: <recipient@domain.com> |
| DATA | Begin email content | DATA (then type message, end with . on its own line) |
| VRFY | Verify if user exists | VRFY root |
| EXPN | Expand mailing list | EXPN listname |
| RSET | Reset the connection | RSET |
| NOOP | No operation (keep alive) | NOOP |
| QUIT | End session | QUIT |

---

## SMTP Response Codes

| Code | Meaning |
|------|---------|
| 220 | Service ready |
| 221 | Service closing transmission channel |
| 250 | Requested action OK (success) |
| 251 | User not local, will forward |
| 252 | Cannot VRFY user, but will accept message |
| 354 | Start mail input (after DATA command) |
| 421 | Service not available |
| 450 | Mailbox unavailable (temporary) |
| 550 | Mailbox unavailable (permanent) |
| 551 | User not local |
| 552 | Exceeded storage allocation |
| 553 | Mailbox name not allowed |

---

## Connecting to SMTP

### Using Telnet

telnet 10.129.14.128 25

Connected to 10.129.14.128.
220 ESMTP Server

### Say Hello

HELO mail1.inlanefreight.htb
250 mail1.inlanefreight.htb

### Extended Hello (ESMTP)

EHLO mail1
250-mail1.inlanefreight.htb
250-PIPELINING
250-SIZE 10240000
250-ETRN
250-ENHANCEDSTATUSCODES
250-8BITMIME
250-DSN
250-SMTPUTF8
250 CHUNKING

---

## Checking for Users (VRFY)

telnet 10.129.14.128 25

VRFY root
252 2.0.0 root

VRFY cry0l1t3
252 2.0.0 cry0l1t3

VRFY testuser
252 2.0.0 testuser

VRFY aaaaaaaaaaaaaaaaaaaaaaaaaaaa
252 2.0.0 aaaaaaaaaaaaaaaaaaaaaaaaaaaa

**Warning:** If the server responds with 252 for every request, it's lying! This is configured to prevent user enumeration. Don't trust false positives.

---

## Sending an Email Manually

telnet 10.129.14.128 25

HELO inlanefreight.htb
MAIL FROM: <cry0l1t3@inlanefreight.htb>
RCPT TO: <mrb3n@inlanefreight.htb>
DATA
From: <cry0l1t3@inlanefreight.htb>
To: <mrb3n@inlanefreight.htb>
Subject: Test
Date: Tue, 28 Sept 2021 16:32:51 +0200

This is a test message.
.
QUIT

The single dot on a line ends the DATA command.

---

## Default SMTP Configuration (Postfix)

Configuration file: `/etc/postfix/main.cf`

Important settings:

smtpd_banner = ESMTP Server
myhostname = mail1.inlanefreight.htb
mydestination = $myhostname, localhost
mynetworks = 127.0.0.0/8 10.129.0.0/16
smtpd_helo_restrictions = reject_invalid_hostname

---

## Dangerous SMTP Settings

| Setting | Description | Risk |
|---------|-------------|------|
| mynetworks = 0.0.0.0/0 | Allow any network to relay | OPEN RELAY - anyone can send spam |
| smtpd_helo_restrictions = | No restrictions on HELO | Can fake identity |
| disable_vrfy_command = no | VRFY enabled | User enumeration |
| allow_untrusted_routing = yes | Allows relaying | Open relay risk |

### The Open Relay Danger

mynetworks = 0.0.0.0/0

This means ANYONE can use this server to send email. Spammers LOVE this. If you find an open relay, you can send emails from any address to any address.

---

## Key Takeaways

- SMTP sends emails, POP3/IMAP receive them
- Port 25 for server-to-server, 587 for authenticated clients
- VRFY command can enumerate users (if enabled)
- EHLO shows supported ESMTP extensions
- DATA command followed by a single dot ends the message
- Open relays allow anyone to send email through the server
- False positives (252 responses) may be configured
- Always verify manually - automated tools can be wrong
- Email headers contain valuable information
- SPF, DKIM, DMARC help prevent spoofing
