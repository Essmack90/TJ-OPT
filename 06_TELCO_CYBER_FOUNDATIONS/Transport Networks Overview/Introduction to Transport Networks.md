
## Transport Networks – Introduction

### 1. The Role of Transport Networks

**Definition:** Transport networks are the **backbone** of modern communication systems – they enable the seamless exchange and efficient movement of large volumes of data across different segments of a telecommunications network.

**What they do:** Connect core elements and data centers, and bridge access networks to provide the essential infrastructure for all communication services (see Figure 1).

### Key Characteristics & Benefits

| Characteristic | What It Means | Why It Matters |
|----------------|---------------|----------------|
| **High reliability** | Redundant paths, advanced fault detection and correction mechanisms | Continuous operation, minimal downtime |
| **Large capacity** | Optical fiber supports up to **48 terabits per second** | Handles massive data volumes |
| **Long distance** | Low fiber loss + coherent light = thousands of km without electrical relay | Enables global connectivity |
| **Multi-service access** | Supports PDH, SDH, Ethernet, video; robust protection mechanisms | Quick recovery, minimal service disruption |
| **Interoperability** | Standards-based protocols and interfaces | Compatible across diverse network elements |

> **Bottom line:** Transport networks ensure reliable, rapid transfer of information – they are the backbone that makes everything else work.

---

## 2. Transport Networks Evolution

### Categorization by Transmission Method

| Category | Technology | Core Principle |
|----------|------------|----------------|
| **Time-based** | PDH, SDH, SONET | Time Division Multiplexing (TDM) – each user gets a unique timeslot |
| **IP-based** | PTN (Packet Transport Network) | Packet-based transmission – data broken into packets, sent independently |
| **Hybrid** | MSTP, WDM (CWDM/DWDM), OTN | Combines TDM and packet methods for flexibility and scalability |

---

### Time-based Transmission Technologies

#### PDH (Plesiochronous Digital Hierarchy)
| Aspect | Details |
|--------|---------|
| **Era** | 1960s–1980s |
| **Meaning** | "Almost synchronous" – clocks very close but not exactly aligned |
| **Medium** | Copper or fiber optic cables |
| **Role** | Early digital telecom networks; reliable long-distance voice/data |
| **Status** | Largely replaced by SDH/SONET, but its multiplexing principles influenced future technologies |

#### SDH (Synchronous Digital Hierarchy)
| Aspect | Details |
|--------|---------|
| **Era** | Late 1980s |
| **Meaning** | "Synchronous" = network clocks aligned; "Digital hierarchy" = structured multiplexing of different data rates |
| **How it works** | Multiplexes multiple digital signals into a single optical signal, all synchronized to a common clock |
| **Status** | Replaced PDH; global standard |

#### SONET (Synchronous Optical Network)
| Aspect | Details |
|--------|---------|
| **Developer** | Bellcore (1980s), standardized by ANSI |
| **Role** | Backbone for internet, carrier networks, large enterprise WANs |
| **Key features** | Fault tolerance, self-healing capabilities |
| **Region** | Primarily United States |

### SDH vs. SONET Comparison (Table 1)

| Feature | SDH | SONET |
|---------|-----|-------|
| **Interfaces** | Network node, user-network, U reference-point | Digital hierarchy for optical transmission |
| **Overhead bytes** | 81 transport overhead bytes | 27 transport overhead bytes |
| **Transmission modes** | Synchronous and asynchronous | Synchronous only |
| **Basic unit** | STM-1 | OC-1 |
| **Base rate** | 155.52 Mbps | 51.84 Mbps |
| **Region** | Global | United States |

> **Key insight:** SDH built on SONET's foundation but offers a more flexible hierarchy for multiplexing, making it better suited for integration with diverse global networks. They are interoperable at certain levels.

---

### IP-based Transmission Technologies

#### PTN (Packet Transport Network)
| Aspect | Details |
|--------|---------|
| **Era** | Early 2000s |
| **Problem solved** | Traditional networks struggled with bursty packet traffic from IP-based services |
| **What it does** | Adds a layer between IP service and optical transmission medium |
| **Benefits** | Multi-service provisioning, lower TCO, high availability, reliability, bandwidth management, traffic engineering, scalability, high security |

---

### Hybrid Transmission Technologies

#### MSTP (Multi-Service Transmission Platform)
| Aspect | Details |
|--------|---------|
| **Problem solved** | Traditional SDH devices only offered E1, E3, E4 ports – couldn't handle diverse access services |
| **What it does** | Enhances SDH with a service board; operates on TDM plane |
| **Capability** | Carries voice, video, and internet data over single infrastructure |
| **Users** | Telecom operators, cable providers, enterprise networks |
| **Security concern** | Aggregates multiple services on shared infrastructure → needs **traffic isolation, encryption, access control** |

#### WDM (Wavelength Division Multiplexing)
| Aspect | Details |
|--------|---------|
| **Concept** | Multiple data streams at different frequencies (wavelengths/colors) over a single optical fiber |
| **How it works** | Multiplexer combines signals from different transponders; demultiplexer separates them at receiving end |
| **Benefit** | Optimizes fiber utilization, maximizes network investment efficiency |

**Two WDM Categories:**

| Feature | CWDM (Coarse WDM) | DWDM (Dense WDM) |
|---------|-------------------|-------------------|
| **Channels** | 8 channels | 40–80 channels (40 with 100GHz spacing, 80 with 50GHz spacing) |
| **Wavelength spacing** | 20 nanometers | Much tighter (100GHz or 50GHz) |
| **Energy consumption** | Lower | Higher |
| **Cost** | Less expensive | More expensive |
| **Capacity** | Lower | Much higher |
| **Distance** | Shorter | Longer (core networks) |
| **Typical use** | Enhancing existing optical networks | Core telecom, cable networks, cloud data centers (IaaS) |

> **Today's dominant technology:** **DWDM** is the most widely-used WDM technology in modern optical networks – essential for 5G, video streaming, cloud computing.

> 🔐 **Security note:** WDM aggregates multiple channels on the same physical medium → needs encryption at higher network layers, strict access control for optical nodes, monitoring for anomalous wavelength activity.

#### OTN (Optical Transport Network)
| Aspect | Details |
|--------|---------|
| **Definition** | Network of optical elements interconnected through fiber links |
| **What it does** | Transmits, multiplexes, routes, manages, monitors, and protects customer signals using optical channels |
| **Key feature** | **Customer independence** – transmission settings are irrelevant to customer signal characteristics |
| **How it works** | Provides a **digital wrapper** around client signals; encapsulates them into OTN containers (OTU); adds Forward Error Correction (FEC); integrates OAM (fault management, monitoring, provisioning) |
| **Drivers of growth** | Cloud adoption, data centers, 5G, video streaming, AI workloads |
| **Industries** | Finance, healthcare, manufacturing, government |

> **Why OTN matters:** Networks need to be scalable, transparent, and efficient without complexity or high costs. OTN delivers this.

---

### Throughput Summary (Figure 3)

The evolution from legacy to modern interfaces:

| Legacy Interfaces | Modern Interfaces |
|------------------|-------------------|
| E1/E4 | OTU-1 to OTU-4 |
| STM-1 to STM-64 | 100G Ethernet and beyond |

**Most widely adopted today:** OTU-4 and 100G Ethernet – essential for cloud computing, 5G, video streaming, AI workloads.

---

## 📌 One-Paragraph Takeaway (for memory)

> **Transport networks** are the backbone of telecom – they connect core elements, data centers, and access networks, enabling high-capacity, long-distance, reliable communication. Key characteristics: **high reliability** (redundant paths, fault detection), **large capacity** (up to 48 Tbps via optical fiber), **long distance** (thousands of km without electrical relay), **multi-service access**, and **interoperability**. Evolution: **Time-based** (PDH → SDH/SONET) used TDM; **IP-based** (PTN) handles bursty packet traffic; **Hybrid** (MSTP, WDM, OTN) combines both. **WDM** (CWDM/DWDM) sends multiple wavelengths over one fiber – DWDM dominates core networks. **OTN** wraps client signals with digital wrapper (FEC, OAM) for scalable, transparent transport. Security concerns: MSTP needs traffic isolation; WDM needs encryption and access control. Most widely adopted today: **OTU-4 and 100G Ethernet**.

---

