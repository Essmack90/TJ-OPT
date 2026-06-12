## Types of Access Networks 

### Three Main Categories

| Type | How It Works | Best For |
|------|--------------|----------|
| **Fixed (Wired)** | Physical cables (copper, coax, fiber) | Stable, high-speed connections where mobility isn't needed |
| **Wireless** | Radio waves | Mobile users, hard-to-wire areas |
| **Hybrid** | Combines fixed + wireless | Maximizing coverage, reliability, and performance |

> **All share the same goal:** Reliable communication between end users and the wider network.

---

## 1. Fixed Access Networks (Wired)

**Characteristics:** More stable, faster, less interference than wireless. Requires physical connection. Higher installation cost.

### Four Main Fixed Technologies

| Technology | Infrastructure | Speed | Best Use | Security |
|------------|---------------|-------|----------|----------|
| **DSL** | Copper telephone lines | Up to ~50 Mbps down | Residential (legacy) | Moderate (encrypted over copper) |
| **Cable Broadband** | Coaxial (HFC – fiber + coax) | 100 Mbps – 1 Gbps down | Residential broadband, TV | Moderate (shared medium risks) |
| **Ethernet** | Twisted-pair copper or fiber within LAN | 100 Mbps – 10 Gbps (up to 400 Gbps in data centers) | LANs, enterprise networks | Very secure (requires physical access) |
| **Fiber Optic** | Glass/plastic fibers, light pulses | Up to ~10 Gbps symmetric | Backbone, high-speed broadband | Highly secure (very difficult to tap) |

### DSL Deep Dive

- **DSL** = Digital Subscriber Loop (or Line)
- Transmits data over traditional copper telephone lines
- **Key property:** Voice and internet simultaneously (uses splitters/filters to separate frequencies)
- **Leverages existing infrastructure** → cost-effective where fiber isn't available

**xDSL Variants (Figure 2 summary):**

| Type | Description |
|------|-------------|
| ADSL | Asymmetric – faster down than up (residential) |
| SDSL | Symmetric – same speed both directions (business) |
| VDSL | Very high speed – shorter distances |
| VDSL2 | Enhanced VDSL, up to 100+ Mbps |

### Cable Broadband Deep Dive

- Uses **HFC architecture** (fiber for long distance, coaxial for last mile)
- Evolved from cable TV networks
- **Shared medium** – bandwidth distributed among multiple users in same area
- Uses **DOCSIS** standard for channel bonding and higher throughput

### Ethernet Deep Dive

- IEEE 802.3 standard – dominant for **wired LANs**
- Speeds from 10 Mbps to multi-hundred-gigabit
- Covered in more detail in Module 3

### Fiber Optic Deep Dive

- Data as **pulses of light** through glass/plastic
- Extremely high bandwidth, long distances without signal degradation
- Critical for modern telecom and internet infrastructure

### Wired Technologies Comparison Table (Condensed)

| Feature | DSL | Cable | Ethernet | Fiber |
|---------|-----|-------|----------|-------|
| Distance impact | Speed decreases with distance | Minimal (shared bandwidth) | Limited to <100m for copper | No impact |
| Reliability | Stable but limited | Drops during peak usage | Highly reliable | Extremely reliable |
| Cost | Affordable | Moderate | Low (internal network) | Higher initial cost |
| Latency | Moderate (10-70 ms) | Low-moderate (15-40 ms) | Very low (1-5 ms) | Extremely low (1-7 ms) |
| Scalability | Limited | High | Moderate (cabling limited) | Extremely scalable |

**Takeaway:** Fiber leads in speed, scalability, reliability. Ethernet dominates LANs. Cable is cost-effective residential. DSL is legacy but still used.

---

## 2. Wireless Access Networks

**Characteristics:** Data over radio waves. Ideal for mobility and difficult-to-wire areas. Trade-offs: interference, signal loss over distance/barriers (penetration loss), bandwidth limitations.

### Four Main Wireless Technologies

| Technology | Range | Speed | Best Use |
|------------|-------|-------|----------|
| **Wi-Fi** (IEEE 802.11) | 30-100 m | Up to 10 Gbps (Wi-Fi 6E) | Homes, offices, public spaces |
| **Bluetooth** (IEEE 802.15.1) | Up to 10 m (Class 2), 100 m (Class 1), 200+ m (Bluetooth 5) | Up to 3 Mbps (Bluetooth 5) | Peripherals, IoT, short-range |
| **Cellular Networks** (2G–5G) | Kilometers (cell coverage) | 2G: 64 Kbps → 5G: up to 10-20 Gbps | Mobile broadband, voice, IoT |
| **FWA** (Fixed Wireless Access) | Several km | 100 Mbps – 1 Gbps | Rural broadband, last-mile |

### Wi-Fi Deep Dive

- IEEE 802.11 standards (Wi-Fi 4, 5, 6, 6E, 7)
- Uses **unlicensed spectrum** (2.4 GHz, 5 GHz, now 6 GHz)
- Requires **AP (Access Point)** + client devices
- Security: **WPA2/WPA3** for authentication + encryption

### Bluetooth Deep Dive

- Short-range, low power
- **Bluetooth 5** extended range (up to 200+ meters in open environments)
- **BLE (Bluetooth Low Energy)** for IoT and wearables
- Security: AES encryption, frequency hopping, secure simple pairing

### Cellular Networks Deep Dive

**Core concept:** Geographic area divided into **cells**, each served by a base station.

#### Generations Comparison

| Generation | Key Features | Speed | Security Notes |
|------------|--------------|-------|----------------|
| **2G** (GSM) | Digital voice, SMS, circuit-switched data | Up to 64 Kbps | A5/1, A5/2 encryption (weak), SIM authentication, **no mutual authentication** → vulnerable to fake base stations (IMSI catchers) |
| **3G** (UMTS) | Mobile internet, multimedia | 384 Kbps – several Mbps | **Mutual authentication** introduced, KASUMI/SNOW 3G encryption, integrity protection → but downgrade attacks possible |
| **4G** (LTE) | All-IP, high-speed broadband | 10-100 Mbps (up to 300 Mbps with LTE-A) | AES encryption, control/user plane separation, frequent key refreshes, **much stronger security** |
| **5G** (NR) | Ultra-low latency, massive IoT, eMBB, URLLC, mMTC | 50 Mbps – 2 Gbps (up to 10-20 Gbps theoretical) | **Secure by design** – encrypted permanent identifiers (SUCI), stronger encryption, SEPP for roaming security, network slicing isolation, anti-fallback measures |

**5G spectrum bands:**
- **Low-band (sub-1 GHz):** Wide coverage, lower speeds
- **Mid-band (1-6 GHz):** Balance of speed and coverage
- **High-band (mmWave, 24-100 GHz):** Extremely high speeds, limited range/penetration

> ⚠️ **Legacy networks note (2025 GSA report):** 2G and 3G are being phased out but still operational in many regions. 131 operators in 65 markets have 2G shutdown plans; 147 operators in 62 markets are phasing out 3G. Many are upgrading to 4G and 5G.

### Fixed Wireless Access (FWA) Deep Dive

- Delivers broadband using **wireless links** (cellular or microwave) instead of cables
- Ideal for **underserved/rural areas** where laying fiber is expensive
- Uses **licensed spectrum** for reliability
- Requires outdoor antenna + CPE at customer location

### Wireless Technologies Comparison (Condensed)

| Feature | Wi-Fi | Bluetooth | Cellular | FWA |
|---------|-------|-----------|----------|-----|
| Range | 30-100 m | Up to 100 m (Class 1) | Kilometers | Several km |
| Mobility | Limited | High | Excellent | None (fixed location) |
| Cost | Low-moderate | Very low | High | Moderate |
| Latency | Very low (1-10 ms) | Sub-ms | 5G: 1-10 ms | Low-moderate |
| Power | Moderate | Very low | Moderate-high | Moderate |

---

## 3. Hybrid Access Networks

**Definition:** Combines fixed + wireless technologies to maximize performance, coverage, and reliability.

### Key Attributes

| Attribute | What It Means |
|-----------|----------------|
| **Enhanced coverage** | Reaches remote/rural areas |
| **Improved reliability** | Multiple paths reduce outage risk |
| **Bandwidth aggregation** | Combines links (e.g., DSL + LTE) for higher throughput |
| **Optimized performance** | Wired for heavy loads, wireless for flexibility |
| **Flexible deployment** | Ideal where high-speed fixed access is limited but mobile coverage exists |

### Benefits vs. Drawbacks

| Benefits | Drawbacks |
|----------|-----------|
| Reliability (multiple technologies) | Complex management |
| Cost efficiency (uses existing infrastructure) | Higher equipment costs |
| Business continuity (backup options) | Latency variability |
| Built-in redundancy (automatic failover) | Security concerns (multiple integration points) |

### Hybrid Configurations Examples

| Hybrid Type | How It Works | Best For |
|-------------|--------------|----------|
| **DSL + LTE** | Wired broadband with cellular failover | Rural broadband, backup links |
| **Fiber + Wi-Fi** | Fiber backbone + wireless distribution | High-speed home/enterprise networks |
| **Cable + Cellular** | Cable broadband with LTE redundancy | Urban broadband with resilience |

**Security angle:** Multiple access methods create layered defenses – harder to fully disrupt.

---

## 📌 One-Paragraph Takeaway (for memory)

> Access networks fall into three categories. **Fixed (wired)** networks use DSL, cable, Ethernet, or fiber – fiber is fastest and most reliable, DSL is legacy but widely available. **Wireless** networks use Wi-Fi (short-range, unlicensed), Bluetooth (very short-range, low power), cellular (2G–5G, wide-area), and FWA (rural broadband). Cellular security evolved dramatically: 2G had weak encryption and no mutual authentication (vulnerable to IMSI catchers); 3G added mutual authentication; 4G introduced AES and all-IP security; 5G is "secure by design" with encrypted subscriber IDs, network slicing isolation, and SEPP for roaming. **Hybrid** networks combine fixed + wireless for redundancy, bandwidth aggregation, and improved coverage – but add management complexity and security integration challenges. The choice depends on balancing speed, reliability, cost, mobility, and coverage needs.

---
