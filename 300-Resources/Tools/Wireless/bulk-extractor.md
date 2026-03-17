---
tags: [tool, forensics, extraction]
tool: bulk-extractor
category: Wireless
installed: true
---

# Bulk Extractor - Digital Forensics

## Overview
High-speed extraction of email addresses, URLs, credit cards from disk images

## Location
/usr/bin/bulk_extractor

## Usage

### Basic Extraction
bulk_extractor -o output_dir image.dd

### Extract Specific Features
bulk_extractor -e email -e http -o output_dir image.dd

### With Custom Wordlist
bulk_extractor -F wordlist.txt -o output_dir image.dd

### Output Directories
output_dir/email.txt : Email addresses
output_dir/url.txt : URLs
output_dir/telephone.txt : Phone numbers
output_dir/ccn.txt : Credit card numbers
output_dir/domain.txt : Domain names
output_dir/ether.txt : MAC addresses

### Features
- Email extraction
- URL extraction
- Credit card numbers
- Phone numbers
- Domain names
- MAC addresses
