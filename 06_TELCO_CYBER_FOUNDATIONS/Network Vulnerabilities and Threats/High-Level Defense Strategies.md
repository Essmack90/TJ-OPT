### 1. Proactive Vulnerability Management

Vulnerability management is an ongoing effort to pinpoint and fix security flaws in an organisation's infrastructure. It minimises risks like unauthorised access and data breaches by preemptively dealing with vulnerabilities.

#### The 7 Steps of the Vulnerability Management Process

| Step | Description |
|------|-------------|
| **1. Asset discovery and inventory** | Identify all hardware and software components to map potential entry points. Maintain updated records to prioritize securing sensitive assets. |
| **2. Vulnerability scanning and identification** | Conduct regular automated scans to detect weaknesses. Analyze results to identify high-risk vulnerabilities and prioritize remediation. |
| **3. Vulnerability assessment and analysis** | Evaluate impact, exploitability, and severity of identified vulnerabilities. Prioritize issues based on risk to allocate resources effectively. |
| **4. Prioritization and risk assessment** | Rank vulnerabilities by potential impact and exploitation likelihood. Assess risks considering asset importance and business implications. |
| **5. Remediation and mitigation strategies** | Fix vulnerabilities with patches and configurations. Implement mitigation measures to reduce impact of unresolved issues. |
| **6. Verification and continuous monitoring** | Re-scan systems to ensure vulnerabilities are resolved. Monitor for new threats and adapt strategies to respond promptly. |
| **7. Reporting and documentation** | Provide stakeholders with updates on vulnerability status and remediation progress. Maintain records to support compliance and future assessments. |

#### Vulnerability Management Best Practices

| Best Practice | Description |
|---------------|-------------|
| **Establish clear policies and procedures** | Create detailed guidelines for roles and responsibilities. Ensure consistent application across the organization. |
| **Automate vulnerability scanning and analysis** | Use automated tools for regular scanning. Automate analysis to prioritize critical vulnerabilities quickly. |
| **Integrate vulnerability management into DevOps** | Embed security checks within DevOps practices. Foster a culture of continuous security awareness among developers. |
| **Use threat intelligence for prioritization** | Utilize threat intelligence to provide context about potential threats. Optimize resource allocation for remediation. |
| **Conduct regular penetration testing** | Simulate real-world attacks to uncover vulnerabilities. Gain insights beyond automated scans. |
| **Employee training and awareness** | Conduct regular training sessions on security best practices. Promote a security-conscious culture to reduce human error. |

---

### 2. Security Testing and Penetration Testing

Penetration testing is a security practice where experts (ethical hackers/pentesters) simulate cyber attacks to uncover vulnerabilities in computer systems.

#### Types of Penetration Tests

| Test Type | Description |
|-----------|-------------|
| **Open-box test** | Pentester receives some pre-disclosed information about the target company's security |
| **Closed-box test** | "Single-blind" test – pentester has no prior information except the company name |
| **Covert test** | "Double-blind" test – almost everyone (including IT and security teams) is unaware of the test |
| **External test** | Assesses external-facing technologies (websites, network servers) |
| **Internal test** | Conducted within internal network – evaluates potential damage from compromised or disgruntled employees |

#### Network Penetration Testing Process

| Phase | Description |
|-------|-------------|
| **Information gathering and planning** | Define testing goals, identify known vulnerabilities, select test types. Three common perspectives: |
| └ *Black box testing* | Simulates external attacks with no prior knowledge of the network |
| └ *Gray box testing* | Represents an insider threat with some internal system knowledge |
| └ *White box testing* | Uses comprehensive internal information (IT specialist perspective) |
| **Reconnaissance and discovery** | Leverage data for live tests; use port scanners, vulnerability scanners, social engineering |
| **Conducting the test** | Execute scripts and attempts to access data; assess potential damage and duration of unauthorized access |
| **Analysis and reporting** | Document tests performed, analyze results, provide evidence, vulnerabilities, and remediation recommendations |

---

### 3. Software Patch Management

Patch management involves deploying updates (patches) to software and systems to address security vulnerabilities and ensure they remain secure and up to date.

#### Benefits of Patch Management

| Benefit | Description |
|---------|-------------|
| **Enhanced security** | Timely patching closes security gaps to prevent malware, ransomware, and unauthorized access (e.g., Equifax breach) |
| **Improved stability** | Patches fix bugs that cause crashes and performance issues |
| **Regulatory compliance** | Meeting standards like GDPR and HIPAA requires consistent patching |
| **Reduced downtime and cost savings** | Automated patching reduces human error, minimizes outages, saves costs |

#### Types of Patches

| Type | Description |
|------|-------------|
| **Security patches** | Address known vulnerabilities to protect systems from potential exploits |
| **Bug fixes** | Resolve software issues to ensure reliable operation |
| **Feature updates** | Introduce new functionalities and improve performance |
| **Hotfixes** | Emergency patches for critical vulnerabilities, issued outside regular schedule |
| **Cumulative updates** | Bundled updates that include multiple patches, simplifying maintenance |

> **Bottom line:** Effective patch management is essential for reducing the attack surface, enhancing system stability, ensuring compliance, and saving costs.

---

### 4. Bluetooth Security

Bluetooth enables wireless communication between devices within short-range radio frequency. Devices calculate Received Signal Strength Indication (RSSI) and adjust transmission power for power efficiency.

#### NIST Bluetooth Security Levels (Table 2)

| Level | FIPS Approved Algorithms | MitM Protection | User Interaction | Encryption Required |
|-------|--------------------------|-----------------|------------------|---------------------|
| 0 | No | No | None | No |
| 1 | No | No | Minimal | Yes |
| 2 | No | No | Minimal | Yes |
| 3 | No | Yes | Acceptable | Yes |
| 4 | Yes | Yes | Acceptable | Yes |

*Note: Level 0 is for Service Discovery Protocol only*

#### Mitigation Strategies

| Strategy | Description |
|----------|-------------|
| **Link keys** | Secret symmetric keys used for authentication. Should never be stored or transmitted. |
| **PIN** | Randomly generated link keys shared between devices; never sent or stored elsewhere. |
| **Authentication** | Challenge-response system where one device proves identity to another. |
| **Encryption** | NIST recommends AES-CMAC with p-256 elliptic curve algorithm for high-security requirements (112-bit security). |

#### Critical Bluetooth Vulnerabilities

| Vulnerability | Description |
|---------------|-------------|
| Weak encryption | Poor implementation of security protocols |
| Eavesdropping on link keys | Intercepting keys during transmission |
| Insecure storage and reuse of keys | Keys stored improperly or reused across sessions |
| Spoofing devices to obtain keys | Impersonating legitimate devices |
| Short PINs without random number generation | Weak authentication material |
| Sharing keys across multiple networks (piconets) | Key reuse across different security contexts |
| Weak encryption algorithms | Using deprecated or broken algorithms |

---

### 6.5. Module 6 Wrap-Up (Condensed)

| What We Covered | Key Takeaway |
|----------------|---------------|
| **Threat landscape** | Mobile/fixed networks, 5G, IoT have expanded attack surface. Threats include insider risks, supply chain vulnerabilities, AI-driven attacks, protocol weaknesses, social engineering. |
| **Key threats** | Protocol weaknesses (MitM, DNS spoofing), misconfigurations, outdated software, signaling storms, spoofing, malware propagation, BGP hijacking, SS7 attacks. |
| **Attack surfaces** | Access (SIM exploits, rogue base stations), transport (unencrypted backhaul, BGP hijacking), core (control plane attacks, GTP exploits), end-user/IoT (unpatched devices, botnets), interconnection (SS7/Diameter/5G SBA exploits). |
| **Defense strategies** | Proactive vulnerability management (7 steps), penetration testing (black/gray/white box), patch management, configuration hardening, Bluetooth security (NIST levels 0-4). |

## 📌 One-Paragraph Takeaway (for memory)

> **Proactive vulnerability management** follows 7 steps: asset discovery, scanning, assessment, prioritization, remediation, verification, and reporting. Best practices include automation, DevOps integration, threat intelligence, regular penetration testing, and employee training. **Penetration testing** uses black box (no prior knowledge), gray box (some internal knowledge), and white box (comprehensive internal information) perspectives across open-box, closed-box, covert, external, and internal tests. **Patch management** delivers security patches, bug fixes, feature updates, hotfixes, and cumulative updates – providing enhanced security, stability, compliance, and cost savings. **Bluetooth security** (NIST levels 0-4) uses link keys, PINs, authentication, and encryption (AES-CMAC with p-256). Critical vulnerabilities include weak encryption, key eavesdropping, insecure key storage, spoofing, short PINs, key reuse across piconets, and weak algorithms. Defense requires continuous vigilance, security-by-design, industry cooperation, and regulatory compliance.

---