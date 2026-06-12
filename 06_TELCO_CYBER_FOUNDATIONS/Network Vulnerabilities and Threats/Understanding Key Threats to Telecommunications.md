Network vulnerabilities are weaknesses in software, hardware, or organisational processes that can be exploited to cause security breaches.

#### Protocol Weaknesses

| Vulnerability | Description | At-Risk Protocols |
|---------------|-------------|-------------------|
| **Man-in-the-Middle (MitM)** | Attackers intercept communications between two parties | HTTP, FTP (unencrypted) |
| **DNS Spoofing** | Poisoning DNS cache to redirect users to malicious websites | DNS (when DNSSEC not deployed) |
| **TCP/IP Spoofing & SYN Flood** | Exploiting TCP handshake vulnerabilities | TCP |
| **HTTP Response Splitting & XSS** | Manipulating server responses and injecting malicious scripts | HTTP |

#### Misconfigurations

Security misconfiguration occurs when software, systems, servers, or network devices are not securely set up.

**Common misconfiguration vulnerabilities:**

| Vulnerability | Impact |
|---------------|--------|
| Administrative accounts with default/weak passwords | Easily exploited by attackers |
| Delayed security patch installation | Exposure to known vulnerabilities |
| Excessive user privileges | Data breaches or privilege escalation |
| Open network ports | Potential access points for attackers |
| Incorrect file permissions | Unauthorized exposure of sensitive information |

#### Outdated Software/Hardware

As new advancements emerge, older systems become increasingly vulnerable.

**Impacts of using outdated software:**

| Impact | Description |
|--------|-------------|
| **Frequent downtime** | Older systems fail more often, causing productivity losses |
| **Data loss and security vulnerabilities** | Unsupported systems no longer receive security updates |
| **Compliance failures** | Struggle to meet HIPAA, PCI, SEC audit requirements |
| **Hidden costs** | Replacement parts become scarce; emergency fixes cost more than modernization |

---

### 2. Threat Taxonomy

Organisations encounter three main categories of threats.

```
THREAT TAXONOMY
├── Insider Threats (malicious/careless actions by employees, contractors, partners)
├── External Attackers (opportunistic hackers, hacktivists, state-sponsored entities)
└── Supply Chain Risks (vulnerabilities in third-party vendors and suppliers)
```

#### Insider Threats

Insider threats originate from individuals within the organization who have legitimate access.

| Category | Description |
|----------|-------------|
| **Intentional threats** | "Malicious insider" – deliberately seeks to harm (grievances, revenge) |
| **Unintentional threats** | Employee errors or negligence |
| └ **Accidental** | Human error (wrong email recipient, malicious links) |
| └ **Negligent** | Carelessness (weak passwords, lost devices, no updates) |
| **Third-party threats** | Business partners or contractors compromising security |
| **Collusive threats** | Insiders collaborating with external actors |

#### External Attackers

External threats originate outside an organization's network. Since attackers lack internal access, they use technical exploits, social engineering, or brute force.

**Social engineering attack phases:**

| Phase | Description |
|-------|-------------|
| **Preparation** | Identify target, gather background, select attack method |
| **Initial deception** | Engage victim with convincing narrative |
| **Information extraction** | Deepen influence, execute main attack |
| **Conclusion** | Remove traces, cover tracks |

**Common external threat types:**

| Threat | Description |
|--------|-------------|
| **Phishing** | Emails, messages, fake websites deceiving users into revealing information |
| **Malware & ransomware** | Malicious software installed without consent; ransomware encrypts files |
| **DDoS attacks** | Overwhelming servers with traffic from multiple sources |
| **State-sponsored groups** | Advanced, persistent tactics targeting sensitive data or critical infrastructure |

> **Info Box:** After receiving a malicious email, **84% of employees are deceived within 10 minutes**. Only **3% of passwords** meet NIST complexity standards.

#### Supply Chain Risks

A supply chain attack targets an organization's software or service providers within its digital supply chain.

**Impacts of supply chain attacks:**

| Impact | Description |
|--------|-------------|
| **Financial losses** | System downtime, lost revenue, remediation costs, reputational damage |
| **Data breaches** | Customer records, intellectual property, trade secrets, classified documents |
| **Erosion of trust** | Deterioration among customers, suppliers, investors |
| **National security risks** | Attacks on power grids, water supplies, transportation systems |
| **Regulatory penalties** | Fines for non-compliance with GDPR and other data protection laws |

---

### 3. Attack Methods

#### Eavesdropping

Unauthorized interception and listening to private communications (also known as snooping or sniffing). Predominantly **passive** – attacker does not alter data.

**Methods:**

| Method | Description |
|--------|-------------|
| **Packet sniffers** | Software capturing data packets traveling across network |
| **Wiretapping** | Physically accessing transmission lines |
| **Compromised Wi-Fi** | Exploiting unsecured wireless networks |

**Mitigation strategies:**

| Strategy | Description |
|----------|-------------|
| **Encryption** | HTTPS, WPA3, end-to-end encryption |
| **VPN usage** | Encrypts all traffic, especially on public Wi-Fi |
| **Secure networks** | Properly secured and regularly updated routers/switches |
| **Access controls** | Restrict network access, monitor unauthorized entries |
| **Awareness training** | Educate employees on risks of unsecured communications |

#### Spoofing

Cybercriminals disguise themselves as trusted sources. By impersonating a legitimate entity, attackers can steal information, extort money, or install malware.

**Common spoofing attacks:**

| Type | Description |
|------|-------------|
| **Email spoofing** | Alter "From" field or mimic known contact; homograph attacks (0 for O, l for I) |
| **Caller ID spoofing** | Disguise phone numbers; pose as customer support |
| **Website/domain spoofing** | Create lookalike sites with slightly altered domain names |
| **IP spoofing** | Change IP addresses to hide identity or impersonate users (common in DoS) |
| **ARP spoofing** | Link MAC address to legitimate IP to intercept data |
| **GPS spoofing** | Alter GPS signal to mislead location (navigation systems in vehicles, planes, ships) |

**Detecting spoofing – key questions:**

| Question | Red Flag |
|----------|----------|
| Was the request solicited? | Unsolicited password reset emails |
| Does the message ask for sensitive information? | Legitimate orgs don't ask for full passwords via email |
| Is the domain different? | Hover over links to see actual URL |
| Is the URL secure (HTTPS)? | Be cautious with HTTP links |
| Are there unsolicited attachments? | Avoid unexpected attachments |
| Is the message personalized? | Generic greetings like "Dear customer" |
| Are there grammar/spelling errors? | Common in spoofing attempts |

#### Signaling Storms

Occur when the volume of control signals from devices overwhelms the network's processing capacity, causing service disruptions. Can snowball as devices repeatedly attempt connections.

**Factors contributing to signaling storms:**

| Factor | Description |
|--------|-------------|
| **Faulty devices** | Repeated registration attempts due to firmware bugs |
| **Misconfigured timers** | Inconsistent settings causing repeated signaling |
| **Software bugs** | Aggressive retries by network functions |
| **Roaming issues** | Continuous registration retries due to incorrect PLMN IDs |

**Mitigation strategies:**

| Strategy | Description |
|----------|-------------|
| **Redundancy** | Enable switching between multiple networks (eSIMs, eUICCs) |
| **Device security** | Strong encryption, regular firmware updates |
| **Dedicated network access** | Private APNs to reduce exposure |

#### Malware Propagation

Malware spreads through various tactics rather than direct entry.

**Common propagation methods:**

| Method | Description |
|--------|-------------|
| Phishing emails | Malicious links or attachments |
| Drive-by downloads | From compromised websites |
| Outdated software | Vulnerabilities in unpatched systems |
| Removable media | Infected USB drives |
| Supply chain attacks | Trusted vendors or updates |

**Malware detection methods:**

| Method | Description |
|--------|-------------|
| **Signature-based detection** | Database of known malware signatures |
| **Heuristic analysis** | Examines code for suspicious behaviors |
| **Behavioral analysis** | Monitors system activities and network communications |
| **AI-powered & ML** | Analyzes threat intelligence, identifies complex patterns |
| **Sandboxing** | Runs suspicious files in isolated environment |
| **Endpoint Detection & Response (EDR)** | Continuous endpoint activity tracking |

**Lock or Encrypt BSS Data:** Attackers target BSS databases (billing, charging, customer management) to disrupt billing cycles, service activation, partner settlements, and customer-care functions. Defenses include network segmentation between BSS and IT domains, hardened access control, continuous monitoring, and immutable offline backups.

---

### 4. Real-World Examples

#### SS7 Signalization Bank Account Attack (Germany's O2 Telefonica)

Attackers combined credential harvesting, signaling-layer manipulation, and real-time SMS interception to defeat banking two-factor authentication.

```
Attack Flow:
1. Attacker harvests banking credentials (phishing/malware)
2. Uses SS7 signaling to intercept SMS with 2FA code
3. Intercepted code allows attacker to complete fraudulent transaction
4. Victim's bank account compromised despite 2FA

Key takeaway: SS7 control-plane weaknesses can bypass modern authentication
```

#### BGP Hijacking – Pakistan Telecom / YouTube (2008)

Pakistan Telecom attempted to block YouTube domestically by announcing a more specific BGP route to blackhole YouTube traffic within Pakistan. The errant BGP announcement leaked upstream to its provider and propagated globally, causing large portions of the internet to misroute YouTube traffic to Pakistan Telecom – effectively blackholing YouTube internationally for several hours.

**Key takeaway:** A single incorrect BGP advertisement can unintentionally hijack traffic on a global scale.

---

## 📌 One-Paragraph Takeaway (for memory)

> Network vulnerabilities include **protocol weaknesses** (MitM, DNS spoofing, TCP/IP attacks), **misconfigurations** (weak passwords, delayed patches, excessive privileges, open ports, incorrect permissions), and **outdated software/hardware** (frequent downtime, data loss, compliance failures, hidden costs). **Threat taxonomy** divides into insider threats (intentional, unintentional/accidental/negligent, third-party, collusive), external attackers (phishing, malware/ransomware, DDoS, state-sponsored), and supply chain risks (financial loss, data breaches, trust erosion, national security risks, regulatory penalties). **Attack methods** include eavesdropping (packet sniffers, wiretapping, compromised Wi-Fi), spoofing (email, caller ID, website, IP, ARP, GPS), signaling storms (faulty devices, misconfigured timers, software bugs, roaming issues), and malware propagation (phishing, drive-by downloads, outdated software, removable media, supply chain). **Real-world examples:** SS7 signalization attack against O2 Telefonica (bypassing 2FA via signaling manipulation) and Pakistan Telecom BGP hijack of YouTube (single incorrect route blackholing global traffic).

---
