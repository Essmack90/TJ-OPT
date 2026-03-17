---
tags: [module, nmap, output, documentation, beginner]
module: "Saving Nmap Results"
level: beginner
---

# Saving Nmap Results - Beginner's Guide #nmap #output #documentation #beginner

## Why Save Your Scan Results? #core #documentation

While we run various scans, we should always save the results. This is a critical habit for several reasons:

- **Comparison:** Later we can examine differences between different scanning methods
- **Documentation:** Results are needed for reports and proof of work
- **Evidence:** Saved scans show exactly what was found and when
- **Reuse:** No need to re-scan the same targets later

Think of it like taking photos during an investigation - you never know what detail might become important later.

---

## The Three Output Formats #formats

Nmap can save results in three different formats. Each serves a different purpose.

| Format | Option | File Extension | Best For |
|--------|--------|----------------|----------|
| Normal output | -oN | .nmap | Reading by humans |
| Grepable output | -oG | .gnmap | Parsing with grep and scripts |
| XML output | -oX | .xml | Generating reports, tools integration |

### Save All Formats at Once #tip

Instead of running three separate commands, use -oA to save in all formats at once:

sudo nmap 10.129.2.28 -p- -oA target

This creates three files:
target.nmap
target.gnmap
target.xml

---

## Example: Full Port Scan with All Outputs #example

sudo nmap 10.129.2.28 -p- -oA target

Starting Nmap 7.80 at 2020-06-16 12:14 CEST
Nmap scan report for 10.129.2.28
Host is up (0.0091s latency).
Not shown: 65525 closed ports
PORT      STATE SERVICE
22/tcp    open  ssh
25/tcp    open  smtp
80/tcp    open  http
MAC Address: DE:AD:00:00:BE:EF

Nmap done: 1 IP address (1 host up) scanned in 10.22 seconds

After the scan completes, check the files created:

ls
target.gnmap  target.xml  target.nmap

---

## Understanding Each Format #formats-explained

### 1. Normal Output (-oN) #normal-output

This is the same output you see on screen, saved to a file.

cat target.nmap

# Nmap 7.80 scan initiated Tue Jun 16 12:14:53 2020 as: nmap -p- -oA target 10.129.2.28
Nmap scan report for 10.129.2.28
Host is up (0.053s latency).
Not shown: 4 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
25/tcp open  smtp
80/tcp open  http
MAC Address: DE:AD:00:00:BE:EF

# Nmap done at Tue Jun 16 12:15:03 2020 -- 1 IP address (1 host up) scanned in 10.22 seconds

**Use this for:** Reading later, including in reports for technical people.

### 2. Grepable Output (-oG) #grepable-output

This format puts all information about a host on a single line, making it easy to search with grep.

cat target.gnmap

# Nmap 7.80 scan initiated Tue Jun 16 12:14:53 2020 as: nmap -p- -oA target 10.129.2.28
Host: 10.129.2.28 () Status: Up
Host: 10.129.2.28 () Ports: 22/open/tcp//ssh///, 25/open/tcp//smtp///, 80/open/tcp//http/// Ignored State: closed (4)
# Nmap done at Tue Jun 16 12:14:53 2020 -- 1 IP address (1 host up) scanned in 10.22 seconds

**Use this for:** Quick searches with grep to extract specific information.

Example: Extract all hosts with port 80 open:
grep "80/open" target.gnmap

### 3. XML Output (-oX) #xml-output

This is a structured format that can be parsed by other tools and transformed into reports.

cat target.xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<?xml-stylesheet href="file:///usr/local/bin/../share/nmap/nmap.xsl" type="text/xsl"?>
<nmaprun scanner="nmap" args="nmap -p- -oA target 10.129.2.28" version="7.80">
<scaninfo type="syn" protocol="tcp" numservices="65535" services="1-65535"/>
<host>
<status state="up" reason="arp-response"/>
<address addr="10.129.2.28" addrtype="ipv4"/>
<address addr="DE:AD:00:00:BE:EF" addrtype="mac"/>
<ports>
<port protocol="tcp" portid="22"><state state="open"/><service name="ssh"/></port>
<port protocol="tcp" portid="25"><state state="open"/><service name="smtp"/></port>
<port protocol="tcp" portid="80"><state state="open"/><service name="http"/></port>
</ports>
</host>
</nmaprun>

**Use this for:** Importing into other tools, generating HTML reports, automation.

---

## Converting XML to HTML Reports #reporting

The XML format can be transformed into beautiful, easy-to-read HTML reports using xsltproc.

### Basic Conversion

xsltproc target.xml -o target.html

This creates target.html which you can open in any browser.

### How It Works

The XML file references an XSL stylesheet (nmap.xsl) that tells the browser or xsltproc how to format the data as HTML.

### Why This Matters #documentation

HTML reports are:
- Easy to read for non-technical people (managers, clients)
- Professional-looking for documentation
- Searchable and printable
- Can be included in final penetration test reports

---

## Best Practices #best-practices

### 1. Always Save Your Scans

Make it a habit to add -oA to every significant scan. You'll thank yourself later when writing reports.

### 2. Use Meaningful Names

-oA target-name-date
-oA internal-network-full-scan-20260317

### 3. Store Scans Organized

Create a directory structure:
mkdir -p ~/scans/client-name/$(date +%Y-%m-%d)

### 4. Document the Command

The saved files include the exact command used, so you always know what was run.

### 5. Convert XML to HTML for Reports

Before submitting reports, generate HTML versions for a professional presentation.

---

## Key Takeaways #keypoints

- Always save scan results using -oA to get all three formats
- Normal output (.nmap) is for human reading
- Grepable output (.gnmap) is for quick searches with grep
- XML output (.xml) is for tools and HTML reports
- Use xsltproc to convert XML to professional HTML reports
- Saved scans are essential for documentation, comparison, and evidence
- Without saving, you'll have to re-scan (wasting time) or guess what you found
- The official documentation at https://nmap.org/book/output.html has more details
