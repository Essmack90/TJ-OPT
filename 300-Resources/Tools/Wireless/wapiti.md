---
tags: [tool, web, scanner]
tool: wapiti
category: Wireless
installed: true
---

# Wapiti - Web Vulnerability Scanner

## Overview
Black-box web app scanner that injects payloads to find SQLi, XSS, file disclosure

## Location
/usr/bin/wapiti

## Usage

### Basic Scan
wapiti -u https://target.com

### Specific Attack Modules
wapiti -u https://target.com -m sql,xss,file

### Authentication
wapiti -u https://target.com --auth-type basic --auth-cred "admin:pass"

### Crawl and Scan
wapiti -u https://target.com --scope page --depth 3

### Output Report
wapiti -u https://target.com -f html -o report.html

### Modules
sql : SQL injection
xss : Cross-site scripting
file : File inclusion
exec : Command execution
crlf : CRLF injection
backup : Backup files
htaccess : htaccess misconfiguration
