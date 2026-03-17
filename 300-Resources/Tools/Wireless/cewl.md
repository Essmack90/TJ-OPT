---
tags: [tool, wireless, wordlist]
tool: cewl
category: Wireless
installed: true
---

# CeWL - Custom Wordlist Generator

## Overview
Spiders websites to create tailored wordlists based on found words

## Location
/usr/bin/cewl

## Usage

### Basic Crawl
cewl -w wordlist.txt https://target.com

### Depth and Minimum Word Length
cewl -d 3 -m 6 -w wordlist.txt https://target.com

### With Authentication
cewl --auth user:pass -w wordlist.txt https://target.com

### Include Emails
cewl --email -w emails.txt https://target.com

### Options
-d : Crawl depth
-m : Minimum word length
-w : Output file
--email : Extract emails
--auth : Basic authentication
--with-numbers : Include words with numbers
--lowercase : Convert to lowercase
