### 1. Overview – Protocols and Standards in Transport Networks

**Why they matter:** Carrier-grade transport networks rely on layered architectures with different protocols and standards to provide immense capacity, reliability, and service flexibility.

| Category | OSI Layer | Technologies/Protocols |
|----------|-----------|------------------------|
| **Physical & Optical** | Layer 1 | DWDM, OTN, SONET/SDH |
| **Packet/Switching** | Layer 2/2.5 | MPLS, MPLS-TP, Carrier Ethernet |
| **Network Layer** | Layer 3 | IP, BGP |
| **Transport & Above** | Layer 4+ | TCP, UDP, SCTP |

---

### 2. Physical and Optical Layer (Layer 1)

These technologies focus on physically moving massive amounts of data over fiber optic cables.

| Technology | Function | Key Characteristics |
|------------|----------|---------------------|
| **DWDM** (Dense Wavelength Division Multiplexing) | Increases fiber capacity by sending multiple data streams using different wavelengths (colors) of light | Core technology, not a protocol; dramatically boosts capacity |
| **OTN** (Optical Transport Network) – ITU-T G.709 | "Digital wrapper" for client signals (Ethernet, SDH, IP) | Standardized framing, monitoring, Forward Error Correction (FEC); carrier-grade reliability |
| **SONET/SDH** (Synchronous Optical Network / Synchronous Digital Hierarchy) | Time-division multiplexing (TDM) standards originally for voice traffic | 50ms protection switching; legacy but still deployed |

---

### 3. Packet/Switching Layer (Layer 2 / 2.5)

These protocols manage how data packets are routed efficiently across physical infrastructure.

| Protocol | Function | Key Characteristics |
|----------|----------|---------------------|
| **MPLS** (Multi-Protocol Label Switching) | High-performance forwarding; directs data using short, fixed-length labels instead of complex IP lookups | Enables VPNs, QoS, fast rerouting (protection switching) |
| **MPLS-TP** (MPLS-Transport Profile) | Designed specifically for transport network operational requirements | Simplified, connection-oriented OAM; bidirectional paths (vs. MPLS unidirectional); performance monitoring; enhanced protection |
| **Carrier Ethernet (CE)** – MEF specs, IEEE 802.1 | Reliable, scalable, manageable Ethernet services over wide areas | Governed by Metro Ethernet Forum (MEF) |

---

### 4. Network Layer (Layer 3)

These protocols manage logical addressing and routing of data packets.

| Protocol | Function | Key Characteristics |
|----------|----------|---------------------|
| **IP** (Internet Protocol – IPv4/IPv6) | Universal standard for logical addressing and routing | Transport network's job is to carry IP packets efficiently |
| **BGP** (Border Gateway Protocol) | Exchanges routing information between autonomous systems (AS) on the internet | Enables peering; selects best route via RIB; runs over TCP; supports CIDR; **originally minimal built-in security** (vulnerable to prefix hijacking, DoS, MitM) |

---

### 5. Transport Layer and Above (Layer 4+)

These protocols ensure reliable data transmission between host computers.

| Protocol | Connection Type | Reliability | Speed | Key Features | Typical Uses |
|----------|----------------|------------|-------|--------------|---------------|
| **TCP** (Transmission Control Protocol) | Connection-oriented | Reliable, ordered delivery | Slower | Flow control, congestion control, error checking, retransmission | Web browsing, email, FTP |
| **UDP** (User Datagram Protocol) | Connectionless | "Best effort" (no guarantee) | Faster | Minimal header, low overhead, broadcast/multicast support | Streaming, online gaming, VoIP, DNS |
| **SCTP** (Stream Control Transmission Protocol) | Connection-oriented | Reliable | Moderate (comparable to TCP) | Message-oriented delivery, multi-streaming, multi-homing | Telecommunications, voice/video over IP, signaling transport |

#### TCP/UDP/SCTP Comparison 

| Feature | TCP | UDP | SCTP |
|---------|-----|-----|------|
| Reliability | ✅ Reliable | ❌ Unreliable | ✅ Reliable |
| Connection type | Connection-oriented | Connectionless | Connection-oriented |
| Ordered delivery | ✅ Yes | ❌ No | ✅ Yes |
| Speed | Slower | Faster | Moderate |
| Overhead | Higher | Lower | Moderate |
| Congestion control | ✅ Yes | ❌ No | ✅ Yes |
| Message-oriented | ❌ No | ❌ No | ✅ Yes |
| Multi-streaming | ❌ No | ❌ No | ✅ Yes |
| Multi-homing | ❌ No | ❌ No | ✅ Yes |

---

### 6. Data Link Layer (Layer 2) – Deep Dive

#### Ethernet (IEEE 802.3)

**Function:** Predominant wired LAN standard for high-speed data communication within limited scope (offices, campuses).

**Ethernet Types Comparison (Table 4):**

| Ethernet Type | Speed | Media | Typical Use |
|---------------|-------|-------|--------------|
| **Fast Ethernet** | 100 Mbps | Twisted pair (CAT5), fiber | Data centers, surveillance |
| **Gigabit Ethernet** | 1 Gbps | CAT5e, CAT6, fiber | Modern office/home networks |
| **10-Gigabit Ethernet** | 10 Gbps | CAT6a, CAT7, fiber | Data centers, enterprise backbones |

**Key Components:**
- **Frame:** PDU that encapsulates and transmits data
- **Access control mechanism:** CSMA/CD (Carrier Sense Multiple Access with Collision Detection) for collision management on shared media
- **Encoding:** Manchester Encoding

**Key Features:** Speed (10 Mbps to 400 Gbps), reliability (error detection), cost-effectiveness, interoperability (IEEE 802.3), security (encryption/authentication support), scalability, broad compatibility.

#### GPON (Gigabit Passive Optical Network)

**Function:** High-speed fiber-optic broadband standard using point-to-multipoint architecture.

| Component | Location | Function |
|-----------|----------|----------|
| **OLT** (Optical Line Terminal) | Service provider central office | Transmits data to multiple users; collects data from them |
| **ONT/ONU** (Optical Network Terminal/Unit) | User premises | Receives data from OLT |

**Key Characteristics:**
- **Speed:** Asymmetric – downstream up to 2.5 Gbps, upstream up to 1.25 Gbps
- **Wavelengths:** Uses WDM (different wavelengths for downstream/upstream)
- **Layer 2 protocols:** Ethernet (data) + TDM (voice)
- **Distance:** Up to 20 km
- **Security:** Data encryption ensures tapped fiber cannot be interpreted
- **Applications:** High-speed internet, IPTV, VoIP

---

### 7. Session Layer (Layer 5) – Deep Dive

#### Diameter

**Function:** AAA protocol (Authentication, Authorization, Accounting) – comprehensive improvement over legacy RADIUS.

**Key Characteristics:**
- Ensures secure user identification, resource authorization, usage tracking
- Essential for: **Mobile networks, IMS (IP Multimedia Subsystem), IoT**

#### SIP (Session Initiation Protocol)

**Function:** IETF standard enabling voice and video calls over the internet.

**Role:** Communication facilitator – devices locate each other, initiate/end calls, manage conversations.

---

### 8. Security Protocols – IPsec vs. TLS

| Aspect | IPsec | TLS |
|--------|-------|-----|
| **OSI Layer** | Network Layer (3) | Application Layer (7) / Transport Layer (4) |
| **What it protects** | All IP traffic between two IP addresses (any protocol – TCP, UDP, etc.) | Specific application-layer communications (e.g., web browser to server) |
| **Key mechanisms** | ESP (Encapsulating Security Payload), AH (Authentication Header), SAs (Security Associations) | Cryptographic handshake, certificates, encryption |
| **Complexity** | Higher – complex to configure/maintain | Moderate – widely tested, trusted |
| **Best for** | Building large secure networks, secure tunnels between networks | Securing individual applications, public internet communications |

**Both provide:** Encryption, integrity checking, mutual authentication, replay protection, key exchange.

---

### 9. Standards and Standards Organizations

**What standards provide:**

| Benefit | Description |
|---------|-------------|
| **Interoperability** | Different networks/devices work together seamlessly |
| **Innovation** | Global collaboration accelerates technological advancement |
| **Enhanced security** | Consistent protocols for encryption and authentication |
| **Global communication** | Widespread, efficient communication across diverse systems |

**Key Standards Organizations:**

| Organization | Focus |
|--------------|-------|
| **3GPP** (3rd Generation Partnership Project) | Mobile telecommunications standards |
| **5G-PPP** (5G Infrastructure Public Private Partnership) | 5G technology and infrastructure |
| **IEEE** (Institute of Electrical and Electronics Engineers) | Broad range – networking, communications (e.g., 802.3 Ethernet) |
| **ITU** (International Telecommunication Union) | Global telecommunications and IT standards |

---

### 10. Signaling System 7 (SS7)

**Function:** International telecommunication standard defining how network elements in the **Public Switched Telephone Network (PSTN)** exchange information and control signals.

**What it manages:** Routing and billing of telephone calls, advanced calling features, SMS.

> ⚠️ **Security note:** SS7 was designed in an era of trusted networks – it has well-known security vulnerabilities (location tracking, call interception, SMS interception) that are still exploitable where SS7 remains in use.

---
## 📌 One-Paragraph Takeaway (for memory)

> Transport network protocols and standards are organized by OSI layer. **Physical/Optical (Layer 1):** DWDM (multiple wavelengths on one fiber), OTN (digital wrapper with FEC), SONET/SDH (legacy TDM with 50ms protection). **Packet/Switching (Layer 2/2.5):** MPLS (label switching for VPNs/QoS), MPLS-TP (transport-optimized with bidirectional paths), Carrier Ethernet (wide-area Ethernet services). **Network Layer (Layer 3):** IP (universal addressing), BGP (inter-AS routing – but lacks built-in security). **Transport Layer (Layer 4+):** TCP (reliable, ordered, slower), UDP (fast, unreliable), SCTP (reliable + multi-streaming + multi-homing – used in telecom). **Data Link specifics:** Ethernet (IEEE 802.3 – CSMA/CD, Manchester encoding), GPON (point-to-multipoint fiber with OLT/ONT, asymmetric speeds, encryption). **Session Layer:** Diameter (AAA for mobile/IMS/IoT), SIP (voice/video call setup). **Security:** IPsec (network layer, protects all traffic between two IPs) vs. TLS (application layer, secures specific apps). Standards from 3GPP, IEEE, ITU ensure interoperability, innovation, and security.

---
