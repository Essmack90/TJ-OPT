### 1. TCP/IP vs. OSI Models

Both models exist to solve the same problem: **different devices and networks need to talk to each other** in a standardized way.

| Feature | TCP/IP | OSI |
|---------|--------|-----|
| Layers | 4 layers | 7 layers |
| Origin | Practical (ARPANET) | Theoretical (ISO) |
| Usage | Actual internet | Teaching, troubleshooting, reference |
| Focus | Getting data from A to B reliably | Detailed separation of functions |

**TCP/IP Layers (simplified):**
1. **Network Access** – physical cables, Wi-Fi, Ethernet
2. **Internet** – IP addresses, routing
3. **Transport** – TCP/UDP (reliable vs. fast)
4. **Application** – HTTP, DNS, email, etc.

**OSI Layers (memorize: Please Do Not Throw Sausage Pizza Away):**
7. Application – user-facing apps
8. Presentation – encryption, formatting
9. Session – managing conversations
10. Transport – error recovery, flow control
11. Network – routing, addressing
12. Data Link – MAC addresses, switching
13. Physical – cables, radio, voltage

> **Key insight:** The three essential components (transmission media, switching, protocols) map across both models. Media sits at the bottom, switching in the middle, protocols everywhere.

---

### 2. Transmission Media – Wired vs. Wireless

#### Wired Media (Confined path, high security)

| Cable Type | Throughput | Max Length | Main Use |
|------------|------------|------------|-----------|
| **Coaxial** | 0.1–10 Gb/s | 100–500 m | Home, residential distribution |
| **Twisted Pair** | 1–10 Gb/s | 100–300 m | Ethernet, LAN, ADSL |
| **Fiber Optic** | 1–400 Gb/s | 10–5,000 km | Backbone, submarine, FTTx |

**Fiber advantages:** Almost zero noise/loss, very high fidelity, huge throughput.  
**Fiber downside:** More expensive to install, fragile compared to copper.

#### Wireless Media (No cables, mobility)

| Type | Best for | Limitations |
|------|----------|-------------|
| **Radio waves** | Broadcasting, mobile, long distance | Congestion, interference |
| **Microwaves** | Satellite, WLAN, military | Line of sight, weather |
| **Infrared** | Short-range (remotes, keyboards) | Cannot penetrate walls |

> **Trade-off:** Wired = secure, fast, but fixed. Wireless = flexible, cheaper to deploy, but vulnerable to noise and interference.

---

### 3. Switching Technologies – How Data Moves

| Type | How it works | Delay | Efficiency | Reliability | Used In |
|------|--------------|-------|------------|-------------|---------|
| **Message switching** | Store entire message, forward to next hop | High | Very low | Low | Telegraph, old email |
| **Circuit switching** | Dedicated physical path for entire session | Low after setup | Low | High | Landlines, 2G/3G voice |
| **Packet switching** | Split into packets, each takes its own route | Variable | High | High | Internet, 4G, 5G |

**Why packet switching won:**  
- No wasted capacity (circuit switching keeps line open even when silent)
- Can retransmit lost packets
- Scales better

**Benefits of switching in general:**  
- Improves network performance  
- Reduces delays  
- Scales with organization growth  
- Used in data centers, enterprise LANs, ISP infrastructure

---

### 4. Protocols and Standards – The Rules of the Road

- **Protocol** = a set of rules (e.g., HTTP, IP, TCP, SIP, Diameter)
- **Standard** = a formal, published specification (e.g., IEEE 802.11 for Wi-Fi, 3GPP for 5G)

**Why they matter:**  
- Interoperability (Cisco phone talks to Ericsson switch)
- Security is built in, not bolted on
- Scalability without constant redesign
- Global collaboration (open standards)

**Security goal – CIA Triad:**  
- **Confidentiality** → encryption (IPSec, MACsec, TLS)  
- **Integrity** → hashing, checksums (no tampering)  
- **Availability** → DDoS protection, redundancy  

> Telecom is critical infrastructure. Security is **not optional** – it's a design requirement.

---

### 5. Four Basic Components of a Telecom Network

```
[End-User Devices] → [Access Network] → [Transport Network] → [Core Network]
```

| Component | Function | Examples | Security relevance |
|-----------|----------|----------|--------------------|
| **End-user devices** | User entry point | Smartphone, laptop, CPE, sensors | Biggest attack surface (malware, phishing) |
| **Access network** | First link from user to network | DSL, fiber, 5G, Wi-Fi, base stations | Needs authentication + encryption (e.g., WPA3, 5G-AKA) |
| **Transport network** | Long-distance data movement | Fiber, microwave, satellite, MPLS, DWDM | Needs encryption (IPSec, MACsec), segmentation (VLAN, VPN) |
| **Core network** | Routing, management, control | 5GC, EPC, IMS, OSS/BSS, routers | Signaling security (SS7, Diameter, SIP), DDoS mitigation, geo-redundancy |

#### Deeper on each:

**End-user devices**  
- Run OS + apps (SMS, VoIP, browsers)  
- Critical for user experience  
- Often the weakest link (BYOD risks, unpatched software)

**Access networks**  
- Wired (DSL, fiber, Ethernet) or wireless (5G, Wi-Fi)  
- Uses modems, routers, switches, base stations  
- **Primary entry point** → needs strong security (authentication, encryption)

**Transport networks**  
- The "highway" between regions  
- Technologies: SDH, OTN, DWDM, PTN, MPLS  
- **Backbone of communications** → needs high availability + encryption

**Core networks**  
- The "brain" – manages sessions, mobility, billing, policies  
- Contains mobile core (EPC, 5GC), datacenters, OSS/BSS  
- Handles signaling, QoS, interconnection with other operators  
- **Most critical to protect** → firewalls, geo-redundancy, signaling firewalls

---
## 📌 One-paragraph takeaway (for memory)

> Telecom networks rely on **TCP/IP and OSI models** to standardize communication. Data travels over **wired or wireless media** (fiber is fastest, most reliable). **Switching** – mainly **packet switching** – moves data efficiently. **Protocols and standards** ensure interoperability, with **security (CIA triad)** built into all layers. The network is made of four parts: **end-user devices** (entry point), **access network** (first link), **transport network** (long-distance highway), and **core network** (brain that routes, manages, and secures traffic). Each layer has specific security needs – authentication, encryption (IPSec, MACsec), segmentation, and DDoS protection.

---
