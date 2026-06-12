## Transport Network Frameworks 

### 1. Main Frameworks – Overview

**Why frameworks matter:** As telecom networks evolve with new technologies and equipment, we need standardized models that enable diverse devices to interconnect.

**The two fundamental models:**

| Model | Type | Purpose |
|-------|------|---------|
| **OSI** (Open Systems Interconnection) | Comprehensive, 7-layer framework | Standardize networking protocols, enable interoperability |
| **TCP/IP** (Transmission Control Protocol/Internet Protocol) | Conceptual, 4-layer framework | Define how data is transmitted over the internet |

> **Key distinction:** OSI is more comprehensive and theoretical; TCP/IP is simpler and powers the actual internet.

See Figure 4 for layer structures of both models.

---

### 2. OSI Model – Deep Dive

**Definition:** A conceptual framework that standardizes telecommunication or computing system functions into **seven distinct layers**.

**How data moves:** In the form of **Protocol Data Units (PDUs)** – each containing data + layer-specific control information. As a PDU moves through layers, each layer adds or removes its control information.

#### Core Concept: Encapsulation

> **Encapsulation** = when a PDU from an upper layer is wrapped inside the data field of a lower layer's PDU.

As data moves **downward** through layers, each layer encapsulates the PDU with its own control information. This ensures data is properly formatted with necessary control information for effective communication at each layer.

#### OSI Layers (Bottom to Top) – Memorize "Please Do Not Throw Sausage Pizza Away"

| Layer | Name | Function | PDU (at this layer) |
|-------|------|----------|---------------------|
| 7 | **Application** | User-facing apps (email, web, file transfer) | Data |
| 6 | **Presentation** | Encryption, compression, formatting (e.g., JPEG, ASCII) | Data |
| 5 | **Session** | Manages sessions, checkpoints, authentication | Data |
| 4 | **Transport** | End-to-end error recovery, flow control (TCP/UDP) | Segment/Datagram |
| 3 | **Network** | Routing, logical addressing (IP) | Packet |
| 2 | **Data Link** | MAC addressing, switching, error detection (Ethernet) | Frame |
| 1 | **Physical** | Cables, radio, voltage, bits | Bits |

#### OSI Advantages and Disadvantages (Table 2)

| Advantages | Disadvantages |
|------------|---------------|
| Clear separation of functions across seven layers | Highly theoretical; rarely implemented fully in practice |
| Each layer has a clearly defined role | Partial functional overlaps between layers |
| Errors can be isolated and analyzed precisely | Strict layer separation is difficult in real networks |
| Modular structure simplifies maintenance and development | Streamlined TCP/IP model is often preferred in practice |
| Ideal for training, documentation, and network planning | Ambiguity in assigning functions (e.g., encryption or compression) |

> **Bottom line:** OSI is excellent for **learning, documentation, and planning** – but TCP/IP is what actually runs the internet.

---

### 3. TCP/IP Model – Deep Dive

**Definition:** A 4-layer framework that organizes protocols governing network communication. The foundation of the internet.

**Core goal:** Ensure data sent by the sender arrives safely and correctly at the receiver.

**How it works:** Data is broken into smaller parts called **packets**. Packets travel independently and are reassembled in correct order at the destination.

#### TCP/IP Layers (Figure 4 comparison)

| TCP/IP Layer | Function | Corresponding OSI Layers | Key Protocols |
|--------------|----------|--------------------------|---------------|
| **Application** | User-facing services | OSI 5, 6, 7 | HTTP, HTTPS, FTP, SMTP, DNS, SSH |
| **Transport** | End-to-end communication, reliability | OSI 4 | TCP (reliable), UDP (fast) |
| **Internet** | Routing, logical addressing | OSI 3 | IP (IPv4, IPv6), ICMP, ARP |
| **Network Access** | Physical transmission, MAC addressing | OSI 1, 2 | Ethernet, Wi-Fi, DSL, fiber |

> **Note:** TCP/IP combines OSI's top three layers (Application, Presentation, Session) into a single **Application layer**, and OSI's bottom two (Data Link, Physical) into **Network Access**.

#### Advantages of TCP/IP

| Advantage | What It Means |
|-----------|---------------|
| **Interoperability** | Different types of computers and networks can communicate |
| **Scalability** | Suitable for small LANs to the global internet |
| **Standardization** | Open standards ensure devices and software work together |
| **Flexibility** | Supports various routing protocols, data types, communication methods |
| **Reliability** | Error-checking and retransmission features ensure reliable data transfer |

#### Disadvantages of TCP/IP

| Disadvantage | What It Means |
|--------------|---------------|
| **Security concerns** | Original design prioritized interoperability, not security ("trust-by-default"). SSL/TLS are "add-ons," not built-in → creates gaps and new risks |
| **Inefficiency for small networks** | Overhead and complexity unnecessary for very small networks |
| **Limited by address space** | IPv4 has address exhaustion (mitigated by IPv6) |
| **Data overhead** | TCP includes significant overhead for reliability |

#### Why TCP/IP is Preferred Over OSI (Figure 5)

| Reason | Explanation |
|--------|-------------|
| **Simplicity** | 4 layers instead of 7 |
| **Practicality** | Designed for real-world use, not theory |
| **Widespread adoption** | Powers the actual internet |
| **Protocol alignment** | Closely matches real-world protocols used today |

---

### 4. OSI vs. TCP/IP – Key Differences (Consolidated)

| Aspect | OSI Model | TCP/IP Model |
|--------|-----------|---------------|
| **Number of layers** | 7 layers | 4 layers |
| **Origin** | Theoretical (ISO) | Practical (ARPANET) |
| **Usage** | Teaching, documentation, planning | Actual internet and real-world networks |
| **Approach** | Vertical (layer-by-layer) | Horizontal (protocol suite) |
| **Protocol dependency** | Protocols defined after model | Model defined after existing protocols |
| **Session/Presentation** | Separate layers | Combined into Application layer |
| **Physical/Data Link** | Separate layers | Combined into Network Access layer |

---

## 📌 One-Paragraph Takeaway (for memory)

> Transport networks rely on two main frameworks: **OSI** (7 layers) and **TCP/IP** (4 layers). **OSI** is theoretical – excellent for learning, documentation, and planning – with clear separation of functions (Physical, Data Link, Network, Transport, Session, Presentation, Application). Data moves via **PDUs** and **encapsulation** (each layer wraps the upper layer's data with its own control info). However, OSI is rarely fully implemented. **TCP/IP** is practical – it powers the internet – with four layers (Network Access, Internet, Transport, Application). It breaks data into packets that travel independently and reassemble at the destination. TCP/IP's advantages: interoperability, scalability, standardization, flexibility, reliability. Disadvantages: security was an afterthought (SSL/TLS are add-ons, not built-in), IPv4 address exhaustion, overhead for small networks. **Key difference:** OSI is theoretical and comprehensive; TCP/IP is simpler, widely adopted, and practical.

---

