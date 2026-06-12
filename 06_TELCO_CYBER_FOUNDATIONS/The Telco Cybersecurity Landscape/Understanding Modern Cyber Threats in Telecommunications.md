### 1. Evolving Threat Landscape

**The core reality:** Telecommunications companies are caught in an ongoing cycle of adaptation and defence, constantly updating measures to counter the latest threats.

#### Emerging Attack Vectors – Two Categories

| Category | Description | Detection Difficulty |
|----------|-------------|---------------------|
| **Passive Attack Vectors** | Hackers monitor systems for vulnerabilities (open ports, unpatched software) to gain access. Aim to access sensitive information without altering the environment. | Hard to detect |
| **Active Attack Vectors** | Involve altering systems or disrupting operations. Focus on causing chaos, disrupting operations, or damaging system resources. | Easier to detect (but more damaging) |

#### Most Common Attack Vectors

| Attack Vector | Description |
|---------------|-------------|
| **Phishing** | Tricking users into clicking malicious websites that appear genuine |
| **Malware** | Malicious software designed to harm systems, networks, or users |
| **Man-in-the-Middle (MitM)** | Attacker intercepts and modifies requests/responses between two parties |
| **Denial of Service (DoS)** | Disrupting operations by overwhelming target with excessive traffic |
| **Insider Threats** | Individuals within organization misusing access to confidential information |
| **Ransomware** | Malware that encrypts data, demanding payment for decryption |

#### Effective Security Strategies

| Strategy | Description |
|----------|-------------|
| **Network Segmentation** | Divides network into smaller, isolated segments separated by routers, switches, or firewalls |
| **Intrusion Detection and Prevention System (IDPS)** | Monitors malicious activity, reports incidents, attempts to block threats |
| **Antivirus Software** | Detects and eliminates viruses and malware |
| **Encryption** | Transforms data into ciphertext; accessible only to those with decryption key |
| **Regular Backups** | Creates copies of critical data; enables recovery and continuity |

---

### 2. Cyber Attacks – Detailed Descriptions

#### DoS and DDoS Attacks

**Goal:** Overwhelm systems, applications, or networks with excessive traffic, making them inaccessible to legitimate users.

**DoS Attack Categories:**

| Type | Description |
|------|-------------|
| **Buffer Overflow Attacks** | Cause memory buffer overflow, consuming disk space, memory, or CPU time → sluggish performance or crashes |
| **Flood Attacks** | Inundate server with huge packet volume; attacker needs more bandwidth than target |

**DDoS Attack Types:**

| Type | OSI Layer Targeted | Description |
|------|-------------------|-------------|
| **Volume-Based Attacks** | Bandwidth | Overwhelm bandwidth (e.g., DNS amplification with spoofed target address) |
| **Protocol Attacks** | Layers 3 & 4 | Exploit weaknesses (e.g., SYN flood with spoofed IP addresses, incomplete handshakes) |
| **Application-Layer Attacks** | Layer 7 (HTTP) | Force server to process excessive requests (e.g., HTTP flood, continuous browser refreshes) |

**DoS vs. DDoS – Key Differences (Table 1):**

| Difference | DoS | DDoS |
|------------|-----|------|
| **Detection & Tracing** | Easier (single location) | Harder (multiple remote locations) |
| **Attack Speed** | Slower (one source) | Faster (multiple sources simultaneously) |
| **Traffic Volume** | Lower (one machine) | Higher (multiple bots) |
| **Execution Method** | Scripts/tools from single machine | Coordinated bots via command-and-control server |

---

#### Malware

**Definition:** Malicious software aimed at harming systems and stealing data. Includes viruses, adware, spyware, ransomware.

**Types of Malware:**

| Type | Description |
|------|-------------|
| **Viruses** | Attach malicious code to clean files; corrupt systems; spread rapidly |
| **Worms** | Navigate through networks; infect connected machines swiftly |
| **Trojan Viruses** | Disguised as legitimate software; create backdoors for other malware |
| **Spyware** | Collects user data covertly; tracks activities invisibly |
| **Keyloggers** | Record user keystrokes; steal passwords and payment details |
| **Adware** | Floods screens with advertisements; hijacks web browsers |
| **Rootkits** | Hide on systems; grant attackers administrative access |
| **Cryptojacking** | Exploits computer resources to mine cryptocurrencies |
| **Ransomware** | Encrypts data; demands payment (usually cryptocurrency) |
| **Rogue Software** | Masquerades as security tools; tricks users into installing malware |
| **Scareware** | Uses fear tactics to deceive users into buying unnecessary harmful software |

**Telco impact:** Compromises routers, switches, servers, endpoints (mobile devices, IoT), software platforms, databases, customer management systems → privacy violations, data theft, degraded service quality, operational failures.

---

#### Phishing

**Definition:** Attackers use email, text, or direct messages to deceive users into revealing sensitive information. A form of **social engineering** exploiting human trust.

**Common Phishing Techniques:**

| Technique | Description |
|-----------|-------------|
| **Impersonation** | Hackers pose as trusted entities (CEO, finance department) |
| **Fake Login Pages** | Users redirected to lookalike websites to enter sensitive data |
| **Spoofed Email Addresses** | Slightly-altered addresses appear genuine; contain malicious links/attachments |
| **Urgency or Fear Tactics** | Messages create urgency to push users into disclosing information |
| **Social Engineering** | Personalized messages from info gathered via social media or data breaches |
| **QR Code Phishing** | QR codes lead to fake websites or trigger malware downloads |

**Example Scenario:** Email from "bank" with logo → urgent account issue → link to fake bank site → user enters credentials → credentials stolen.

---

#### Ransomware

**Definition:** Malware used to extort money by encrypting data and demanding ransom for decryption.

**Types of Ransomware:**

| Type | Description |
|------|-------------|
| **Scareware** | Social engineering to frighten victims into purchasing unnecessary software |
| **Screen Lockers** | Locks computer screen with payment demand (often impersonating law enforcement) – restore from backup instead of paying |
| **Encrypting (Crypto) Ransomware** | Encrypts data using complex algorithms; victims need backups or pay ransom |
| **Ransomware-as-a-Service (RaaS)** | Subscription model allowing inexperienced criminals to launch attacks without writing code |

**Growing threat:** Increased digitalization (COVID-19) led to more remote data storage, expanding ransomware targets.

---

#### Man-in-the-Middle (MitM)

**Definition:** Attackers intercept and manipulate communications between two parties to steal sensitive data. Parties remain unaware.

**Types of MitM Attacks:**

| Type | Description |
|------|-------------|
| **Email Hijacking** | Gain control of email accounts (banks, trusted institutions); spoof addresses to trick customers |
| **Wi-Fi Eavesdropping** | Set up fake Wi-Fi networks; monitor activity, scrape login details; verify network names, disable auto-connect |
| **DNS Spoofing** | Manipulated DNS records redirect traffic to fake websites; users tricked into logging in |
| **Session Hijacking** | Steal session cookie after login; access victim's account from attacker's device |
| **SSL Hijacking** | Exploit older SSL protocols to intercept data between user and server (modern sites use TLS) |
| **ARP Cache Poisoning** | Deceive victim's computer to send traffic to attacker instead of legitimate gateway |
| **IP Spoofing** | Modify IP addresses to redirect traffic from legitimate to fraudulent websites |
| **Stealing Browser Cookies** | Combine techniques to access browser cookies; retrieve stored passwords, credit card info |

---

#### Signaling Attacks

**Definition:** Exploit weaknesses in network signaling protocols (SS7, Diameter) to disrupt, intercept, or manipulate network operations – often without breaking user data encryption.

**Common Signaling Attack Scenarios:**

| Attack Type | Description |
|-------------|-------------|
| **Information Retrieval** | Extract sensitive subscriber and network data (personal info, billing details, network configurations) |
| **Location Tracking** | Manipulate signaling messages to determine user geographical location with high precision |
| **Traffic/Call Interception/Redirection** | Divert or eavesdrop on legitimate communications by altering signaling pathways |
| **Denial of Service (DoS)** | Overload signaling channels to disrupt service access |
| **Fraud** | Manipulate billing systems, make international calls without cost |
| **Phishing** | Use manipulated signaling messages to deceive users into revealing information |

**Frequency and Severity (Table 2):**

| Attack Scenario | Frequency | Severity |
|----------------|-----------|----------|
| Information Retrieval | High (monthly) | Medium-High |
| Location Tracking | High (monthly) | High |
| Interception/Redirection | Low-High (varies) | High-Critical |
| DoS | Low | High |
| Fraud | Low | High |

> **Note:** While predominantly on SS7 networks, these attacks are increasingly migrating to Diameter and other protocols.

---

#### Supply Chain Attacks

**Definition:** Leverages third-party tools or services to infiltrate a target's system by exploiting dependencies in the supply chain (also known as value-chain or third-party attacks).

**Types of Supply Chain Attacks:**

| Type | Description |
|------|-------------|
| **Browser-Based Attacks** | Malicious code targets end-user browsers via JavaScript libraries or extensions |
| **Software Attacks** | Malware disguised in software updates (e.g., SolarWinds) |
| **Open-Source Attacks** | Vulnerabilities in open-source code exploited to introduce malware |
| **JavaScript Attacks** | Exploit existing JavaScript vulnerabilities or embed malicious scripts |
| **Magecart Attacks** | Malicious JavaScript skims credit card data from checkout forms (formjacking) |
| **Watering Hole Attacks** | Identify and exploit vulnerabilities in popular websites to deliver malware |
| **Cryptojacking** | Malicious code/ads hijack computational resources for cryptocurrency mining |

**Telco relevance:** Ensuring security of third-party suppliers and vendors is critical to maintain network integrity and reliability.

---

#### Advanced Persistent Threats (APTs)

**Definition:** Covert cyberattacks aimed at stealing sensitive data, conducting espionage, or sabotaging crucial systems over extended periods. Unlike ransomware, APTs strive to remain undetected while infiltrating and expanding presence.

**Common APT Techniques:**

| Technique | Description |
|-----------|-------------|
| **Social Engineering** | Phishing, spear phishing to trick users into clicking malicious links or revealing access information |
| **Zero-Day Attacks** | Deploy malicious code to scan for unpatched vulnerabilities before administrators can respond |
| **Supply Chain Attacks** | Target trusted business, technology, or vendor partners for unauthorized access |
| **Rootkits** | Provide hidden, backdoor access; conceal presence and manage remote operations |

**Telco vulnerability:** APTs can compromise critical infrastructure and data exchanges. Detection requires highly-specialized monitoring and threat intelligence.

---

#### Deepfake Attacks

**Definition:** Uses artificial intelligence (AI) to produce convincing fake images, sounds, and videos. Merges "deep learning" with "fake."

**Malicious Uses:**

| Use | Description |
|-----|-------------|
| **Scams and Hoaxes** | False videos of executives admitting crimes or making damaging claims |
| **Election Manipulation** | Fake videos of political leaders to sway public opinion |
| **Social Engineering** | Audio deepfakes trick individuals into believing trusted figures made statements (e.g., unauthorized fund transfers) |
| **Automated Disinformation** | Propagate false information and conspiracy theories |
| **Identity Theft and Financial Fraud** | Create fake documents or impersonate voices |

**Telco impact:** Can manipulate voice communications and video calls, potentially leading to unauthorized access and data breaches.

---

### 3. Case Studies (Real-World Incidents)

| Case | Incident | Key Lesson |
|------|----------|------------|
| **1 – AT&T (2024)** | Cloud workspace breach (Snowflake) exposed call metadata of 109 million customers (phone numbers, cell-tower identifiers for geolocation) | Cloud-hosted telecom data requires same oversight as on-premises systems |
| **2 – Salt Typhoon (2024-2025)** | Exploited Cisco IOS XE vulnerabilities (CVE-2023-20198, CVE-2023-20273) compromising 5+ telecom providers; gained root access on edge routers | Unpatched network-edge devices remain prime targets |
| **3 – France (2024)** | Coordinated physical attacks on long-distance fiber cables disrupted fixed/mobile services for multiple operators | Physical infrastructure (long-haul fiber) remains vulnerable |
| **4 – Orange & NTT (2025)** | Orange: 600,000 customer records breached via Atlassian Jira vulnerabilities. NTT: 18,000 corporate customer files exposed | Enterprise IT systems are critical assets; compromise provides lateral access |
| **5 – Salt Typhoon (2024-2025)** | Breached multiple U.S. operators (AT&T, Verizon, T-Mobile, Lumen, Charter, Windstream, Consolidated) | Single vulnerability in widely-deployed hardware can cascade across operators |

---

### 4. Threat Actors

| Actor Type | Motivation | Characteristics | Key Techniques |
|------------|------------|----------------|----------------|
| **Nation-State Actors** | Geopolitical interests, intelligence gathering, positioning for disruption | Extensive resources, advanced tooling, long-term patience | Targeted reconnaissance, exploitation of legacy systems, signaling network access, supply-chain infiltration |
| **Organized Cybercrime Groups** | Financial incentives | Professional structure, specialized tooling, collaboration with criminal ecosystem | Credential theft, social engineering, misconfiguration exploitation, automated scanning |
| **Ideologically-Motivated Groups** | Visibility, advancing a cause | Varying sophistication | Widely-available offensive tools, poorly-secured devices |
| **Insider Threats** | Malicious or error-based | Employees, contractors, third-party partners with legitimate access | Misconfiguration, data exposure, weakened security controls |
| **Opportunistic Actors** | Visibility, experimentation | Amateur hackers, small groups | Known vulnerabilities exploitation |

---

### 5. Impact of Network Modernization (Digital Transformation)

#### Cloud Adoption

| Challenge | Required Controls |
|-----------|-------------------|
| Increased privileged identities | Controlled provisioning of access |
| External interfaces and API dependencies | Continuous configuration validation |
| Dynamic workloads (deployed, relocated, scaled) | Real-time visibility across workloads |

> **Shift:** Traditional perimeter replaced by identity, policy enforcement, and telemetry as primary control anchors.

#### Internet of Things (IoT)

| Challenge | Required Controls |
|-----------|-------------------|
| High device volumes | Network-level segmentation |
| Fragmented vendor ecosystems | Device attestation |
| Uneven security baselines (weak authentication, limited updates) | Continuous behavior monitoring |

**Risk:** Compromised IoT endpoints can influence signaling load, generate abnormal traffic patterns, or serve as entry points for broader intrusion campaigns.

#### 5G

| Challenge | Required Controls |
|-----------|-------------------|
| Extensive virtualization | Granular trust controls across containers, service-based interfaces, micro-segmented workloads |
| Distributed edge computing | Robust north-south and east-west inspection |
| Network slicing | Secure lifecycle management of VNFs |
| Mission-critical use cases | Automated enforcement capable of milliseconds response |

> **Key risk:** Even minor configuration errors or delays in security updates can expose entire systems to serious vulnerabilities.

**Collective bottom line:** Prevention, detection, and response must operate across fluid boundaries. Operators need **adaptive security architectures, automation-driven assurance, and continuous validation**.

---

## 📌 One-Paragraph Takeaway (for memory)

> The telco threat landscape is defined by **passive vectors** (monitoring for vulnerabilities) and **active vectors** (altering systems/disrupting operations). Common attacks include **phishing, malware, MitM, DoS/DDoS, insider threats, ransomware, signaling attacks** (SS7/Diameter – information retrieval, location tracking, interception), **supply chain attacks, APTs** (stealthy, long-term espionage), and **deepfakes** (AI-generated fraud). **Case studies** show cloud misconfigurations (AT&T, 109M records), unpatched edge devices (Salt Typhoon, Cisco vulns), physical fiber sabotage (France), enterprise software breaches (Orange, NTT), and cascading operator compromises. **Threat actors** include nation-states (geopolitical, advanced), organized cybercrime (financial, professional), ideologically-motivated groups, insiders, and opportunistic actors. **Network modernization** (cloud, IoT, 5G) expands attack surfaces – requiring identity-based perimeters, device attestation, behavior monitoring, and millisecond-response enforcement. Defense requires **network segmentation, IDPS, encryption, backups**, and adaptive security architectures.

---
