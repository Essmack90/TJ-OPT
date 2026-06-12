## Components of Access Networks

### Overview

Access networks are built from several key components that work together to connect end users to the service provider's transport and core network. Each component plays a specific role in enabling communication, managing traffic, ensuring service quality, and delivering reliable and secure connectivity.

**The main components covered in this section:**

| Component | Role |
|-----------|------|
| **CPE** (Customer Premises Equipment) | Hardware at user's site that establishes connection |
| **Last Mile Connectivity** | Final segment from provider to end user |
| **Radio Components** | Essential for wireless access (antennas, base stations, RRUs, BBUs) |
| **Aggregation** | Collects traffic from multiple users and forwards to core |
| **Interfaces** | Standardized connections between components |
| **Transmission Media** | Physical/wireless paths for data |

---

## 1. Customer Premises Equipment (CPE)

**Definition:** Any telecommunications or networking hardware located at the customer's site (home or business) that connects to the service provider's network.

### Common CPE Examples

| Device | Function |
|--------|----------|
| **Router / Residential Gateway** | Routing, NAT, Wi-Fi |
| **Modem** | Modulates/demodulates signals for DSL or cable |
| **ONT / ONU** (Optical Network Terminal/Unit) | Converts light signals to electrical signals in fiber networks |
| **Wi-Fi Access Point** | Local wireless coverage inside premises |
| **Set-top box** | Receives and decodes TV signals |
| **VoIP adapter** | Converts analog phone signals to digital IP packets |
| **IoT Gateway** | Bridges IoT devices (sensors, cameras) to network/cloud |

### Key Attributes of CPE

| Attribute | Description |
|-----------|-------------|
| **Network interface** | Connects customer to provider's network (internet, TV, voice) |
| **User-controlled** | Typically installed and managed by customer or with provider support |
| **Protocol support** | Handles Ethernet, Wi-Fi, DSL, fiber protocols |
| **Security functions** | Often includes firewalls, encryption, access control |
| **Remote management** | Many support remote diagnostics and firmware updates by provider |

> 🔐 **Security relevance:** CPE defines user experience (speed, Wi-Fi performance, service quality). It's a **critical control point** – misconfigurations or outdated firmware create vulnerabilities.

---

## 2. Last Mile Connectivity

**Definition:** The final segment of the telecommunications network that delivers service from the provider to the end user. Despite the name, it can be longer or shorter than a mile depending on geography.

**Why it matters:** Often the most complex and expensive part of the network to deploy, since it requires physical access to homes and businesses.

### Technologies Used in Last Mile

| Copper-based | Coaxial | Fiber | Wireless |
|--------------|---------|-------|----------|
| DSL | HFC (Hybrid Fiber-Coaxial) | FTTH (Fiber-To-The-Home) | Mobile networks (4G, 5G) |
| Ethernet over copper | | FTTB (Fiber-To-The-Building) | FWA |
| | | PON (GPON, XGS-PON, 10G-PON) | Wi-Fi |

### Key Features

| Feature | Description |
|---------|-------------|
| **Access point to end users** | Bridges main network backbone to individual users |
| **Multiple technologies** | Fiber, copper, coaxial, wireless, satellite |
| **Infrastructure dependent** | Varies by geography, population density, existing infrastructure |
| **Bandwidth sensitivity** | Performance depends heavily on bandwidth and congestion |
| **Scalability challenges** | Harder to upgrade than core network components |

---

## 3. Radio Components (Wireless Access)

Essential for wireless access networks where communication occurs through electromagnetic waves.

### Key Radio Components

| Component | Function |
|-----------|----------|
| **Base Station / Cell Tower** | Connects mobile devices to network (2G–5G) |
| **Antennas** | Transmit and receive radio signals (passive element) |
| **RRU / RRH** (Remote Radio Unit/Head) | Active device – amplifies signal, converts digital↔analog |
| **BBU** (Baseband Unit) | Digital processing of signal |

> 🔐 **Security note:** Access network is the most exposed part of mobile infrastructure – thousands of sites in public areas. Biggest threat: **false base stations (IMSI catchers)** that intercept user data.

---

### Base Station (Cell Tower) Deep Dive

**Function:** Bridge between mobile users and telecom network infrastructure. Sends/receives wireless communication to/from mobile devices, then forwards data to core network via transport/backhaul.

**Naming by Generation:**

| Generation | Base Station Name | Controller |
|------------|-------------------|------------|
| **2G** | BTS (Base Transceiver Station) | BSC (Base Station Controller) |
| **3G** | NodeB | RNC (Radio Network Controller) |
| **4G** | eNodeB (evolved NodeB) | Integrated – connects directly to EPC |
| **5G** | gNodeB (next-generation NodeB) | Split: CU (Central Unit) + DU (Distributed Unit) |

**Base Station Components:**
- Antennas
- RRUs
- BBUs
- Interconnected by fiber optic or coaxial cables (feeders, jumpers)
- Cabinet contains BBUs + batteries + climate control

**Evolution (Figure 4):** Traditional: BBU connected to RRU via feeders (with TMA amplifier to compensate loss). Modern: Fiber optic connection (much less loss), no TMA needed.

**5G Active Antenna Systems (AAS):** Integrates antenna and RF components in single unit – eliminates need for separate RRU.

> 🔐 **False base station mitigation:** Vendors provide software-only automated solutions with security manager platform + RAN-specific detection logic (real-time event logging, detection logic, measurement reporting, automated alerts).

---

### Antenna Deep Dive

**Function:** Passive element that transmits and receives radio signals.
- **Downlink:** Converts electrical signals from RRU → electromagnetic waves
- **Uplink:** Receives signals from user devices (smartphones, IoT, modems)

**Types of Antennas (Figure 5):**

| Type | Characteristics | Use Cases |
|------|----------------|-----------|
| **Omnidirectional** | Radiates in all directions | Indoor scenarios, small cells |
| **Directional** | Focuses energy in specific directions | Sites divided into 3+ sectors for better coverage/capacity |
| **Panel** | Directional, flat | Outdoor mobile networks |
| **Parabolic dish** | Highly directional | Satellite connections (TV reception in rural areas) |

**Indoor cells:** Offices, shopping malls, stadiums, airports, factories.

**Small cells:** Low-power base stations covering small areas (tens to hundreds of meters). Types:
- **Femtocells** – very small, often for homes
- **Picocells** – small offices or enterprises
- **Microcells** – larger outdoor or campus coverage

**DAS (Distributed Antenna System):** Network of spatially-separated antennas connected to common source for coverage over large area or inside buildings.

---

### Radio Remote Unit (RRU) Deep Dive

**Function:** Handles radio signal processing close to the antenna.
- Converts digital signals from BBU → RF signals for transmission
- Converts RF signals from antenna → digital for BBU
- Amplifies signal power for transmission over air
- Contains typically at least 2 power amplifiers (one per RF branch)

**Location:** Mounted near antenna on tower/mast to reduce signal loss.

**Connection to BBU:** High-speed optical link using **CPRI** or **eCPRI** protocols.

> 🔐 **Security concern:** CPRI/eCPRI interfaces can introduce vulnerabilities – interception of optical signals or protocol-based attacks if not properly secured.

---

### Baseband Unit (BBU) Deep Dive

**Function:** Central processing unit of a base station. Handles all digital baseband signal processing, control, and management functions.

**What it does:**
- Modulates/demodulates data
- Coding, decoding, error correction
- Manages scheduling, handovers, radio configuration
- Separates control plane (signaling) and user plane (data)
- Ensures precise synchronization for radio interface and transport network

---

### 5G Radio Components Evolution (Critical Section)

**Traditional (pre-5G):** BBU (digital processing) + RRU (radio transmission/reception). Flexible, reduced signal loss.

**5G Change:** BBU functions split into two logical units (defined by 3GPP):

| Unit | Function | Location |
|------|----------|----------|
| **CU (Central Unit)** | Higher-layer functions: RRC, session management, signaling. Can be virtualized in cloud. Connects to 5G core via NG interface | Can be centralized or virtualized in data center |
| **DU (Distributed Unit)** | Real-time, lower-layer processing: MAC, RLC, parts of PHY. Connects to CU via F1 interface, to RRU via fronthaul (e.g., eCPRI) | Located closer to antennas for low latency |

**Why this split matters (Figure 6):**

| Benefit | Explanation |
|---------|-------------|
| **Flexibility** | CU and DU can be deployed in different locations to optimize latency and capacity |
| **Virtualization** | Both can run on cloud-native infrastructure → faster scaling, automation, easier upgrades |
| **Efficiency** | Centralized control of multiple DUs reduces hardware costs, simplifies management |
| **Low latency** | Keeping DU close to radio enables URLLC for real-time applications, autonomous systems, industrial IoT |

---

## 4. Access Network Aggregation

**Definition:** The process of collecting traffic from multiple end users, cell sites, or access nodes and forwarding it into the transport or core network.

**Why needed:** Once individual users connect through the last mile, their traffic must be consolidated and forwarded deeper into the network.

### Typical Aggregation Components

| Component | Function |
|-----------|----------|
| **Cell Site Router (CSR)** | Connects mobile sites to transport network |
| **Access Switches** | Aggregate Ethernet or fiber connections from multiple users |
| **OLT (Optical Line Terminal)** | Controls PON networks, aggregates optical signals from ONTs/ONUs |
| **Layer 2/3 Aggregation Switches** | Forward traffic toward core, often support MPLS, VLANs, QoS |

> Aggregation devices help **scale** the access network and support high-density deployments.

---

## 5. Interfaces

**Definition:** Well-defined interfaces that allow different components (customer devices, base stations, aggregation nodes) to communicate seamlessly. They define how data, signaling, and control information move between elements, ensuring **compatibility across vendors and technologies**.

### Common Interfaces (Figure 7)

| Interface | Connects | Used In |
|-----------|----------|---------|
| **CPRI / eCPRI** | BBU ↔ RRU | Fronthaul links |
| **S1** | eNodeB ↔ EPC | LTE |
| **F1** | CU ↔ DU | 5G |
| **NG** | gNodeB ↔ 5G Core | 5G |
| **X2 / Xn** | Between radio nodes (e.g., for handovers) | LTE / 5G |
| **Uu** | User device ↔ 3G/4G base station | 3G, 4G |
| **Um** | User device ↔ 2G base station | 2G |

> **Why interfaces matter:** They enable multi-vendor interoperability, simplify integration, and support flexible network evolution.

---

## 6. Transmission Media (Refresher)

As covered in Module 1, transmission media are the physical or wireless paths used to transmit data.

| Category | Types | Characteristics |
|----------|-------|-----------------|
| **Wired** | Copper (twisted pair, coaxial) | Limited bandwidth/distance, legacy |
| | Fiber optic | Very high capacity, low latency, minimal loss |
| | In-building cabling | Ethernet, coaxial, fiber inside offices/buildings |
| **Wireless** | Radio waves | Wi-Fi, cellular, FWA |
| | Microwave, satellite | Long-distance or remote connectivity |

---

## 📌 One-Paragraph Takeaway (for memory)

> Access network components work together to connect users to the core. **CPE** (routers, modems, ONTs) is the user-side hardware – a critical security control point. The **last mile** (fiber, copper, coax, wireless) is the most complex and expensive deployment segment. **Radio components** include base stations (BTS/NodeB/eNodeB/gNodeB), antennas (omnidirectional/directional), **RRUs** (signal processing near antenna), and **BBUs** (digital processing). In 5G, the BBU splits into **CU** (higher-layer, can be cloud-based) and **DU** (lower-layer, closer to antenna for low latency). **Aggregation** (CSRs, OLTs, switches) collects traffic from many users. **Standardized interfaces** (CPRI/eCPRI, S1, F1, NG, Xn) ensure multi-vendor interoperability. The access network is the most exposed part of telecom infrastructure – false base stations are a major threat, requiring continuous monitoring and detection.

---
