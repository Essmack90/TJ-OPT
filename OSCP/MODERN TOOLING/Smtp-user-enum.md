# smtp-user-enum

Purpose-built username enumeration over SMTP's `VRFY`/`EXPN`/`RCPT TO` commands. Ships in Kali by default.

---

## What it replaces, and why it's faster

[[Information Gathering#6.4.5. SMTP Enumeration|6.4.5]] teaches manually `telnet`-ing to port 25 and typing `VRFY <name>` one username at a time, reading the response code by eye each time. `smtp-user-enum` does the exact same protocol interaction, just against a whole wordlist in one command instead of one manual `telnet` session per guess.

## Install

Already present on Kali by default (`pentestmonkey/smtp-user-enum`, the classic Perl version). If missing:
```bash
sudo apt install smtp-user-enum
```

## Usage

```bash
# VRFY method against a wordlist
smtp-user-enum -M VRFY -U /usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt -t <target>

# EXPN method (mailing-list expansion, works even where VRFY is disabled)
smtp-user-enum -M EXPN -U users.txt -t <target>

# RCPT TO method (works even when both VRFY and EXPN are disabled, most SMTP servers still accept RCPT)
smtp-user-enum -M RCPT -U users.txt -t <target>
```
*Same three methods the module covers manually via `telnet`, `-M` just picks which one. Worth trying all three against a real target, some servers disable `VRFY` specifically but leave `RCPT TO` wide open.*

## Where this applies in the vault

- [[Information Gathering#6.4.5. SMTP Enumeration|6.4.5, SMTP Enumeration]], directly replaces the manual `telnet` + `VRFY` loop for anything beyond a one-off manual check

#### Tags: #ModernTooling #SmtpUserEnum #SMTP #UserEnumeration
