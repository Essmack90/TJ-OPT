---
tags: [module, nmap, output, documentation, advanced, practical]
module: "Saving Nmap Results"
level: advanced
---

# Saving Nmap Results - Complete Reference #nmap #output #documentation #advanced

## Why Output Formats Matter #importance

A common problem with security tools is confusing and disorganized output. Many tools spew out irrelevant debugging information, forcing users to dig through pages to find important results. Nmap was designed with readable, well-organized, and flexible output in mind.

Since different people and software use Nmap in different ways, no single format can please everyone. That's why Nmap offers several formats:

- Interactive mode for humans to read directly
- Normal files for later reference
- XML for easy parsing by software
- Grepable for quick command-line searches

---

## Complete Output Options Reference #options

| Option | Format | Extension | Use Case |
|--------|--------|-----------|----------|
| -oN | Normal | .nmap | Human-readable reports |
| -oG | Grepable | .gnmap | grep-based parsing |
| -oX | XML | .xml | Automation, reporting tools |
| -oA | All formats | .nmap/.gnmap/.xml | Comprehensive documentation |
| -oS | Script kiddie | .nmap | l33t 5p34k output (joke option) |

**Note:** If no full path is given, results are stored in the current directory.

---

## Parsing Grepable Output #grepable

The grepable format puts all information about a host on a single line, making it ideal for quick searches and scripting.

### Format Structure

Host: <ip> () Status: <Up/Down>
Host: <ip> () Ports: <port>/<state>/<protocol>//<service>///

### Useful grep Commands

Find all live hosts:
grep "Status: Up" *.gnmap

Extract IPs of live hosts:
grep "Status: Up" *.gnmap | cut -d " " -f 2

Find all hosts with port 80 open:
grep "80/open" *.gnmap

Extract all open ports with services:
grep -o "[0-9]\+/open/tcp//[^/]*" *.gnmap

Generate a target list for further scanning:
grep "Status: Up" *.gnmap | cut -d " " -f 2 > live-hosts.txt

---

## XML Output Deep Dive #xml

The XML format is the most powerful for automation and integration.

### Key XML Elements

| Element | Contains |
|---------|----------|
| <nmaprun> | Scan metadata (version, command, time) |
| <scaninfo> | Scan type, protocol, ports scanned |
| <host> | All data about a single host |
| <status> | Host up/down state |
| <address> | IP and MAC addresses |
| <ports> | All port scan results |
| <port> | Individual port details |
| <state> | Port state (open/closed/filtered) |
| <service> | Service name and version |
| <os> | OS detection results |
| <times> | Timing information |
| <runstats> | Scan summary statistics |

### Parsing XML with Command Line

Using xmllint:
xmllint --xpath "//port[@portid='80']/state/@state" target.xml

Using xmlstarlet:
xmlstarlet sel -t -v "//port[@portid='22']/service/@name" target.xml

### Sample XML Extraction Script

#!/bin/bash
# Extract all open ports from XML to CSV

echo "IP,Port,Protocol,Service" > open-ports.csv
for ip in $(xmlstarlet sel -t -v "//address[@addrtype='ipv4']/@addr" target.xml); do
    xmlstarlet sel -t -v "//address[@addrtype='ipv4'][@addr='$ip']/../ports/port[@protocol='tcp'][state/@state='open']/concat('$ip,',@portid,',tcp,',service/@name,'\n')" target.xml >> open-ports.csv
done

---

## Generating Professional HTML Reports #reporting

### Basic HTML Report

xsltproc target.xml -o target.html

This uses the default XSL stylesheet located at /usr/share/nmap/nmap.xsl

### Custom Styling

You can create custom XSL stylesheets for branded reports:

xsltproc --output custom-report.html custom-style.xsl target.xml

### Adding to Reports

HTML reports are ideal for:
- Client deliverables
- Management summaries
- Compliance documentation
- Evidence preservation

### Batch Processing Multiple Scans

for scan in *.xml; do
    xsltproc "$scan" -o "${scan%.xml}.html"
done

---

## Scripting with Nmap Output #automation

### Example 1: Automated Scanning and Reporting

#!/bin/bash
TARGET="10.129.2.28"
DATE=$(date +%Y%m%d-%H%M%S)
OUTPUT="scan-$TARGET-$DATE"

# Run scan and save all formats
sudo nmap -sS -sV -p- $TARGET -oA $OUTPUT

# Generate HTML report
xsltproc $OUTPUT.xml -o $OUTPUT.html

# Extract live hosts (if multiple targets)
grep "Status: Up" $OUTPUT.gnmap | cut -d " " -f 2 > live-$DATE.txt

# Email report
mail -a $OUTPUT.html -s "Scan Report for $TARGET" client@example.com < /dev/null

### Example 2: Diff Two Scans

#!/bin/bash
# Compare two scans to find new open ports

SCAN1="previous-scan.xml"
SCAN2="current-scan.xml"

echo "New ports in current scan:"
diff <(xmlstarlet sel -t -v "//port/@portid" $SCAN1 | sort) \
     <(xmlstarlet sel -t -v "//port/@portid" $SCAN2 | sort) | grep "^>" | cut -d " " -f2

---

## Integration with Other Tools #integration

| Tool | Input Format | Purpose |
|------|--------------|---------|
| Metasploit | XML | Import targets |
| Dradis | XML | Collaboration |
| Faraday | XML | Pentest management |
| Elasticsearch | XML | Log analysis |
| Custom scripts | Grepable | Quick parsing |

### Importing to Metasploit

msfconsole
db_import target.xml
hosts
services

---

## Output Format Comparison #comparison

| Feature | Normal | Grepable | XML |
|---------|--------|----------|-----|
| Human readable | Excellent | Poor | Fair |
| Machine parsable | Poor | Good | Excellent |
| Size | Medium | Small | Large |
| Includes all data | Yes | Yes | Yes |
| Easy to grep | No | Yes | No |
| Hierarchical data | No | No | Yes |
| Stylesheet support | No | No | Yes |
| Multi-host summary | Yes | Yes | Yes |

---

## Best Practices for Professional Engagements #best-practices

### 1. Standardized Naming Convention

sudo nmap -sV -sC -p- $TARGET -oA "engagement-$(date +%Y%m%d)-$TARGET"

### 2. Directory Structure

mkdir -p ~/engagements/client-name/{scans,reports,evidence}
cd ~/engagements/client-name/scans

### 3. Document Everything

- Save raw scans (-oA)
- Generate HTML reports for clients
- Keep notes on why specific scans were run
- Version control your scan files

### 4. Verify File Integrity

sha256sum *.nmap *.gnmap *.xml > checksums.txt

### 5. Include in Final Report

- Reference scan files in appendices
- Include key findings tables
- Provide HTML reports as separate deliverables

---

## Key Takeaways #keypoints

- Nmap offers three complementary output formats: normal, grepable, XML
- Use -oA to save all formats in one command
- Grepable output is perfect for quick searches and shell scripting
- XML output enables automation, reporting, and tool integration
- xsltproc converts XML to professional HTML reports
- Saved scans are essential for documentation, evidence, and comparison
- Scripting with output files can automate large portions of your workflow
- Different formats serve different audiences (technical vs. management)
- Always organize and preserve your scan data
- The official documentation at https://nmap.org/book/output.html has extensive details on all output formats
