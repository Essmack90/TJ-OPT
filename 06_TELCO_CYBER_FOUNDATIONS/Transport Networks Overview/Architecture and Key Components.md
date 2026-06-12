### 1. Wired Transmission Media (Deep Dive)

**Definition:** Physical mediums (cables) that direct and confine signals within a narrow pathway.

#### Advantages vs. Challenges

| Advantages | Challenges |
|------------|------------|
| High security (less eavesdropping/interference) | Difficult installation (walls, floors, ceilings) |
| Lower power consumption | Susceptibility to theft/vandalism |
| Higher transmission rates | Higher deployment costs (materials, installation, maintenance) |
| Point-to-point reliable connection | |

---

#### Twisted Pair Cables

**Structure:** Pairs of insulated copper wires twisted together, enclosed in protective outer jacket.

**Types (Figure 6):**

| Type | Full Name | Characteristics | Typical Use |
|------|-----------|----------------|-------------|
| **UTP** | Unshielded Twisted Pair | No shielding; most common, cheapest | Home/office Ethernet |
| **FTP** | Foil-Shielded Twisted Pair | Foil shield around pairs | Reduced interference environments |
| **STP** | Shielded Twisted Pair | Individual shielding per pair + overall shield | Industrial, high-interference areas |

**Applications:**
- Ethernet connections (local endpoints)
- Internet distribution (households/businesses)
- Telephone communications (minimizes electromagnetic interference)

---

#### Coaxial Cables

**Structure:** Inner copper conductor surrounded by outer conducting shield (copper mesh), separated by insulating material.

**Types (Figure 7):**

| Type | Characteristics | Applications |
|------|----------------|--------------|
| **Flexible** | Bendable, easy to route | Home cable TV, broadband |
| **Low Loss** | Reduced signal degradation over distance | Longer runs, professional installations |
| **Semi-Rigid & Conformable** | Maintains shape, minimal loss | Military, aerospace, high-precision |

---

#### Fiber Optic Cables

**Structure:** Glass or plastic core, surrounded by protective cladding. Transmits data as light pulses.

**Types (Figure 8):**

| Type | Characteristics | Distance | Typical Use |
|------|----------------|----------|--------------|
| **Single Mode Fiber (SMF)** | Very small core (8-10 microns); single light path | Long (up to 100+ km) | Submarine, backbone, long-haul |
| **Multimode Fiber (MMF)** | Larger core (50-62.5 microns); multiple light paths | Short (up to 2 km) | Data centers, campus networks, short-haul |

---

#### Submarine Cables – Critical Infrastructure

> **Scale:** Nearly 1.5 million kilometers of fiber optic cables under the ocean. **Facilitate over 95% of international data transfer.**

**Key Components:**

| Component | Function |
|-----------|----------|
| **Optical fiber** | Ultra-thin glass strands; data as light pulses |
| **Insulation** | Polyethylene layers; protects from water/environment |
| **Strength members** | Steel wires; withstand deep-sea pressure, seabed movement, marine life |
| **Conductor** | Copper/aluminum tube; supplies electrical power to repeaters |
| **Repeaters (optical amplifiers)** | Boost light signal; maintain data integrity over thousands of km |

**Advantages of fiber in submarine:** Higher bandwidth, lower latency, improved reliability/scalability, less maintenance than copper.

**Challenges:** High installation costs, geopolitical tensions over routes, physical damage risks (fishing, anchoring, natural disasters).

---

### 2. Wireless Transmission Media (Transport Network Context)

**For carrier-grade transport networks** (connecting major sites, exchanges, data centers) – focus on **high bandwidth, strong reliability, long range**.

| Technology | How It Works | Speed/Distance | Use Case |
|------------|--------------|----------------|----------|
| **High-capacity terrestrial microwave (point-to-point)** | Ultra-high frequency (E-band, 70-80 GHz); requires strict LOS; highly directional dish antennas | Multi-gigabit over several km | Fiber alternative; backhaul infrastructure; rapid deployment where fiber is cost-prohibitive |
| **Carrier-grade satellite communication** | GEO or LEO constellations (Starlink, Oneweb); C-band, Ku-band, Ka-band | LEO offers low latency | Redundancy; remote global regions; maritime; aircraft; out-of-band management for isolated equipment |
| **Free-space optical (FSO) (point-to-point)** | Modulated laser beams through atmosphere; immune to RF interference; requires LOS | Up to 10+ Gbps; <2 km | "Last mile" fiber extension; bridging buildings where fiber impossible or spectrum licenses difficult |

---

### 3. Topology

**Definition:** Physical and logical configuration of nodes and links in a network. Affects performance, security, and scalability.

#### Topology Types (Figure 9) – Detailed Comparison (Table 3)

| Topology | How It Works | Advantages | Disadvantages | Security Advantages | Security Disadvantages |
|----------|--------------|------------|---------------|---------------------|------------------------|
| **Bus** | Single flat network; all devices on same cable; data broadcast to all stations | Simple, inexpensive, less cable, good for small networks | Single point of failure (backbone break); performance degrades under heavy traffic; difficult troubleshooting | Failure of one station doesn't affect others | Entire network traffic easily sniffed/tapped; minimal data privacy |
| **Ring** | Continuous circular structure; data passes device-to-device | Orderly data flow; prevents collisions; consistent performance | Single link failure breaks entire ring; adding/removing nodes disrupts network | Data passes through every node; potential token-based security checks | Break stops all communication; compromised node can disrupt/intercept all data |
| **Star** | Central node (router/switch); all devices connect to center | Easy to install/manage; device failure isolation; simple troubleshooting | Central hub = single point of failure; requires more cable | Cable break affects only one node; central point enables excellent monitoring/control (firewalls, ACLs) | Central hub compromise = entire network down; critical vulnerability point |
| **Mesh** | Every node connects directly to all others | Extremely robust/fault-tolerant; multiple data paths; high bandwidth | Very expensive (cabling); complex installation/management; costly redundancy | Highly resilient to physical attacks/failures; data reroutes instantly around compromised paths | Many connection points increase attack surface; many physical access points |
| **Tree** | Hierarchical (core, distribution, access layers); leaf-spine variant in data centers | Scalable; easy to add segments; centralized management within each star segment | Backbone failure cripples entire network; complex configuration | Hierarchical structure enables localized security policies and segmentation | Backbone compromise impacts large swaths of network |
| **Hybrid** | Combines multiple topologies | Highly flexible; customized to needs; balances cost and performance | Complex design/management; difficult troubleshooting | Best security aspects from constituent topologies | Complexity can create unforeseen security gaps |

> **Enterprise preference:** **Star and hybrid topologies** are generally preferred because centralization enables robust security controls and monitoring points difficult to implement in distributed bus/ring networks.

---

### 4. Main Components of Transport Networks (Figure 10)

| Component | Function | Security Relevance |
|-----------|----------|---------------------|
| **Switches** | Connect multiple devices; forward data within local network based on simple forwarding rules | Layer 2 forwarding; MAC address tables; VLAN segmentation for isolation |
| **Routers** | Direct data between different networks; choose best path | Layer 3 forwarding; ACLs; routing security (BGP, OSPF authentication) |
| **Multiplexers** | Combine multiple low-rate signals into single high-capacity signal for sharing transmission link | Traffic aggregation point; potential interception risk |
| **Demultiplexers** | Separate combined high-capacity signal back into individual original signals | Signal separation point |
| **Line terminal equipment** | Equipment at each end of transmission system; sends, receives, manages signals over long-distance links | Endpoint security; authentication |
| **Amplifiers** (optical) | Boost light signal strength for longer travel without degradation | Physical infrastructure; tamper protection |

---


## 📌 One-Paragraph Takeaway (for memory)

> Transport networks use **wired transmission media** (twisted pair – UTP/FTP/STP for Ethernet/telephone; coaxial – flexible/low-loss/semi-rigid for TV/broadband; fiber optic – single-mode for long-haul, multimode for short-haul). **Submarine cables** (95%+ of international data) use fiber with repeaters, insulation, strength members. **Wireless** transport uses terrestrial microwave (E-band, multi-gigabit, LOS), carrier-grade satellite (GEO/LEO for redundancy/remote areas), and FSO (laser, short-range, RF-immune). **Topologies** include bus (simple, insecure), ring (orderly but single break kills all), star (centralized control, critical hub vulnerability), mesh (robust but expensive), tree (hierarchical, scalable), hybrid (flexible but complex). **Star and hybrid** are preferred for enterprise security. **Main components:** switches (intra-network), routers (inter-network), multiplexers (combine signals), demultiplexers (separate), line terminal equipment (endpoints), amplifiers (boost optical signals). Redundancy is critical for resilience.

---
