
### 1. Fixed Core Networks

Fixed core networks provide high-capacity, reliable connectivity for residential and enterprise users. They are mainly composed of edges and control functions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FIXED CORE NETWORK                                   │
├─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  Customer   │────│    BNG      │────│ IP/MPLS     │────│  Internet   │      │
│  Premises   │    │ (Broadband  │    │ Backbone    │    │  Gateway    │──────┼──► Internet
│  (CPE)      │    │  Gateway)   │    │             │    │             │      │
├─────────────┤    ├─────────────┤    ├─────────────┤    ├─────────────┤      │
│             │    │             │    │             │    │             │      │
│  DHCP ──────┼────│  AAA        │    │  OSS/BSS    │    │  IPX        │      │
│  Server     │    │ (RADIUS/    │    │             │    │  Peering    │      │
│             │    │  Diameter)  │    │             │    │             │      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Broadband Network Gateway (BNG)

**Function:** Entry point for subscriber traffic in fixed broadband networks (FTTH, xDSL, cable).

**Responsibilities:**
- Establishes and manages user sessions
- Authenticates subscribers
- Applies service policies (bandwidth profiles, QoS)
- Handles IP address assignments and accounting
- Forwards traffic to IP backbone

> **Modern trend:** BNGs are increasingly **virtualized and cloud-native** for scalability and automation.

#### IP/MPLS Backbone

**Function:** Core transport layer providing high-capacity connectivity between BNGs, data centers, and interconnection points.

| Technology | Role |
|------------|------|
| **IP** | Routing and interoperability |
| **MPLS** | Traffic engineering, fast rerouting, VPNs (L2/L3) |

**Benefits:** Low latency, high availability, scalability for millions of flows.

**Challenges:** Operational complexity, capacity planning, security (DDoS, BGP vulnerabilities).

#### Internet Gateway and Peering Points

```
                    ┌──────────────────┐
                    │   Operator Core  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────┴────┐    ┌─────┴─────┐   ┌────┴────┐
         │  IXP    │    │   IPX    │   │  Transit│
         │(Public  │    │(Private, │   │(ISP     │
         │Internet)│    │  QoS     │   │ Peer)   │
         └─────────┘    └──────────┘   └─────────┘
```

| Interconnection Type | Purpose | Characteristics |
|---------------------|---------|-----------------|
| **IXP** (Internet Exchange Point) | Public internet traffic | Best-effort |
| **IPX** (IP Exchange) | Operator-to-operator services (roaming, VoLTE) | Private, QoS-guaranteed, SLAs, isolated from public internet |

#### DHCP (Dynamic Host Configuration Protocol)

**Function:** Automatically assigns IP addresses and network parameters to customer devices.

**Integration:** Works with AAA systems to assign IPs based on subscriber profiles and service tiers.

#### AAA (RADIUS/Diameter)

**Function:** Authentication, Authorization, and Accounting for secure, controlled service access.

| Protocol | Era | Use Case |
|----------|-----|----------|
| **RADIUS** | Legacy | Traditional fixed broadband |
| **Diameter** | Modern | Advanced IP services, 4G/5G |

**Key features:** High availability, geo-redundancy, scalability to millions of sessions.

#### IP Service Management

**Function:** Lifecycle management of IP-based services (broadband internet, VoIP, IPTV, VPNs, CDNs).

**Objectives:**
- Meet SLAs (availability, latency, jitter, packet loss, throughput)
- Security (DDoS protection, lawful interception)
- Service continuity under network stress

---

### 2. Wireless Core Networks – 2G/3G

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         2G/3G CORE ARCHITECTURE                                 │
├─────────────────────────────┬───────────────────────────────────────────────────┤
│    CIRCUIT-SWITCHED (CS)    │              PACKET-SWITCHED (PS)                 │
│                             │                                                   │
│  ┌─────┐    ┌─────┐         │    ┌─────┐         ┌─────┐                        │
│  │BTS  │────│ BSC │         │    │SGSN│─────────│GGSN │────────► Internet      │
│  └─────┘    └──┬──┘         │    └──┬──┘         └─────┘                        │
│                │            │       │                                           │
│                ▼            │       ▼                                           │
│  ┌─────┐    ┌─────┐         │    ┌─────┐                                        │
│  │NodeB│────│ RNC │         │    │HLR/ │                                        │
│  └─────┘    └──┬──┘         │    │AuC  │                                        │
│                │            │    └─────┘                                        │
│                ▼            │                                                   │
│  ┌─────────────────────┐    │    ┌─────┐                                        │
│  │        MSC          │────────│VLR  │                                        │
│  │ (Mobile Switching   │    │    └─────┘                                        │
│  │  Center)            │    │                                                   │
│  └─────────┬───────────┘    │    ┌─────┐                                        │
│            │                │    │EIR  │                                        │
│            ▼                │    └─────┘                                        │
│  ┌─────────────────────┐    │                                                   │
│  │        GMSC         │────┼────────────────────────► PSTN                    │
│  │(Gateway MSC)        │    │                                                   │
│  └─────────────────────┘    │                                                   │
└─────────────────────────────┴───────────────────────────────────────────────────┘
```

#### CS Core Network (Circuit-Switched)

**Purpose:** Voice calls and circuit-based data sessions.

| Component | Function |
|-----------|----------|
| **MSC** (Mobile Switching Center) | Sets up, manages, terminates voice calls and SMS; handles mobility |
| **GMSC** (Gateway MSC) | Routes incoming calls from external networks (PSTN); protocol conversion (ISUP ↔ MAP) |
| **HLR** (Home Location Register) | Central database of subscriber info (mobile number, services, authentication keys, location) |
| **VLR** (Visitor Location Register) | Stores location records of subscribers currently in MSC service area (including roamers) |
| **AuC** (Authentication Center) | Stores encryption/authentication keys; generates authentication triplets |
| **EIR** (Equipment Identity Register) | Database of IMEIs; tracks authorized/barred devices |

##### Authentication Triplet (2G/3G)

```
        Network (AuC)                              Mobile Device (SIM)
             │                                           │
             │  1. RAND (Random Number) ─────────────────►│
             │                                           │
             │                                           │ Uses Ki + RAND
             │                                           │ to compute SRES
             │                                           │
             │  2. SRES (Signed Response) ◄──────────────│
             │                                           │
             ▼                                           ▼
        Compare SRES                                 Kc (Ciphering Key)
        If match → authenticated                     for encryption
```

| Element | Size | Description |
|---------|------|-------------|
| **RAND** | 128-bit | Random challenge from network |
| **SRES** | 32-bit | Response computed by SIM using A3 algorithm + Ki |
| **Ki** | 128-bit | Secret key on SIM and AuC (never transmitted) |
| **Kc** | 64-bit | Ciphering key derived via A8 algorithm; used with A5 for encryption |

#### PS Core Network (Packet-Switched)

**Purpose:** Data services (web browsing, email, streaming). Introduced in 2.5G (GPRS) and 3G (UMTS).

| Component | Function |
|-----------|----------|
| **SGSN** (Serving GPRS Support Node) | Packet routing within network; subscriber authentication; session management; QoS enforcement; charging (CDRs); lawful interception |
| **GGSN** (Gateway GPRS Support Node) | Gateway between mobile network and external packet networks (internet, intranet); IP address allocation; screening/firewalling; GTP tunnel endpoint |

---

### 3. Wireless Core Networks – 4G (EPC)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    4G LTE EVOLVED PACKET CORE (EPC)                         │
│                                                                             │
│                      ┌─────────────────────────────────────┐                │
│                      │            CONTROL PLANE            │                │
│                      │                                     │                │
│  eNodeB ────S1-MME───►  MME ────────────► HSS              │                │
│             │        │  (Mobility        (Home             │                │
│             │        │   Management      Subscriber        │                │
│             │        │   Entity)         Server)           │                │
│             │        │                                     │                │
│             │        │  │                                 │                │
│             │        │  ▼                                 │                │
│             │        │  PCRF ◄─────────────────────────────┤                │
│             │        │  (Policy & Charging                 │                │
│             │        │   Rules Function)                   │                │
│             │        └─────────────────────────────────────┘                │
│             │                         │                                      │
│             │                         │ (Control)                            │
│             ▼                         ▼                                      │
│  eNodeB ────S1-U────► S-GW ────S5/S8────► P-GW ────► Internet              │
│                      (Serving          (Packet Data                         │
│                       Gateway)          Network Gateway)                    │
│                                                                             │
│                      ◄──────── USER PLANE ──────────►                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### EPC Components

| Component | Function | Plane |
|-----------|----------|-------|
| **MME** (Mobility Management Entity) | Control-plane signaling; paging; idle mode management; authentication; security; S-GW selection | Control |
| **HSS** (Home Subscriber Server) | Central database (combines HLR + AuC functions); user profiles, authentication credentials | Control |
| **S-GW** (Serving Gateway) | Data path anchor; downlink data buffering; bearer state maintenance; inter-system handovers (2G/3G via S4) | User |
| **P-GW** (Packet Data Network Gateway) | Interface to external networks; IP address allocation; DPI; packet filtering; QoS enforcement; policy enforcement; roaming gateway | User |
| **PCRF** (Policy and Charging Rules Function) | Policy Decision Function (PDF) + Charging Rules Function (CRF); real-time policy decisions; bandwidth allocation; billing rules | Control |

**Advantages over 2G/3G:**
- All-IP architecture (no CS domain)
- Higher efficiency for data services
- Seamless mobility across LTE and Wi-Fi
- Foundation for IoT and 5G

---

### 4. Wireless Core Networks – 5G (SBA)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        5G CORE – SERVICE-BASED ARCHITECTURE (SBA)                    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                           CONTROL PLANE (NFS)                                │   │
│  │                                                                             │   │
│  │  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐             │   │
│  │  │AMF  │    │SMF  │    │PCF  │    │UDM  │    │AUSF │    │NSSF │             │   │
│  │  │     │    │     │    │     │    │     │    │     │    │     │             │   │
│  │  │Access│    │Session│   │Policy│   │User  │   │Auth  │   │Slice │             │   │
│  │  │& Mob │    │Mgmt  │    │Control│   │Data  │   │Server│   │Select│             │   │
│  │  └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘             │   │
│  │     │          │          │          │          │          │                 │   │
│  │     └──────────┼──────────┼──────────┼──────────┼──────────┘                 │   │
│  │                │          │          │                                        │   │
│  │            ┌───┴───┐  ┌───┴───┐  ┌───┴───┐                                    │   │
│  │            │ NRF   │  │ NEF   │  │ SEPP  │                                    │   │
│  │            │Repo   │  │Expose │  │Sec    │                                    │   │
│  │            │       │  │       │  │Edge   │                                    │   │
│  │            └───────┘  └───────┘  └───────┘                                    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                          │
│                                          │ (N4 Interface)                           │
│                                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                           USER PLANE                                        │   │
│  │                                                                             │   │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │   │
│  │  │                         UPF (User Plane Function)                    │   │   │
│  │  │  • Packet routing & forwarding    • QoS management                   │   │   │
│  │  │  • Packet inspection              • Mobility anchor                  │   │   │
│  │  │  • Traffic reporting              • Downlink buffering               │   │   │
│  │  └─────────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  gNB (5G Base Station) ◄─────────────────────────────────────────────────────────► │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Key 5G Core Functions

**User Plane Function (UPF)**

| Responsibility | Description |
|----------------|-------------|
| PDU session integration | External data network connectivity |
| Mobility anchor | Intra-RAT and inter-RAT mobility |
| Packet routing/forwarding | Efficient data transfer |
| QoS management | User plane quality enforcement |
| Traffic reporting | Usage analytics |
| Downlink buffering | Data notifications for idle devices |

> UPF uses **Vector Packet Processing (VPP)** for high-performance packet forwarding at the network edge.

**Control Plane Functions**

| Function | Role | Key Responsibilities |
|----------|------|---------------------|
| **AMF** (Access & Mobility Management Function) | Central controller | NAS signaling, registration, authentication, security context, mobility across technologies |
| **SMF** (Session Management Function) | Session manager | PDU session lifecycle, IP allocation, UPF selection, QoS enforcement |
| **PCF** (Policy Control Function) | Policy enforcer | Service/mobility/charging rules; network slice policy; AF interaction |
| **UDM** (Unified Data Management) | Subscriber database | 4G HSS evolution; authentication, authorization, subscriber profiles |
| **CHF** (Charging Function) | Billing | Offline/online/converged charging; quota management |
| **AUSF** (Authentication Server Function) | Authentication | 5G authentication methods; interacts with UDM/ARPF |
| **NSSF** (Network Slice Selection Function) | Slice selection | Determines allowed slices for UE; AMF selection |
| **NRF** (Network Repository Function) | Service discovery | NF profile management; discovery and selection |
| **NEF** (Network Exposure Function) | API exposure | Securely exposes network capabilities to external AFs |
| **SEPP** (Security Edge Protection Proxy) | Inter-network security | Protects inter-PLMN signaling; topology hiding; confidentiality/integrity |
| **BSF** (Binding Support Function) | Binding | UE to serving NF binding information |
| **SCP** (Service Communication Proxy) | Message routing | Indirect communication; load balancing; resiliency |
| **AF** (Application Function) | App interaction | Influences traffic handling; communicates app requirements |

**Charging Types:**

| Type | Description |
|------|-------------|
| **Offline Charging** | After resource usage, sent to billing domain |
| **Online Charging** | Before resource usage, OCS verifies account |
| **Converged Charging** | Combines online + offline (CHF in 5G) |

> **5G Security Foundation:** Stronger than 4G (SUCI encrypted subscriber identity, SEPP for roaming, network slicing isolation). But effectiveness depends on implementation.

---

### 5. Network Management Systems

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NETWORK MANAGEMENT LAYER                               │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │      OMC        │  │      OAM        │  │      OSS        │             │
│  │ (Operations &   │  │ (Operations,    │  │ (Operations     │             │
│  │  Maintenance    │  │  Administration,│  │  Support        │             │
│  │  Center)        │  │  Maintenance)   │  │  System)        │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                      │
│           └────────────────────┼────────────────────┘                      │
│                                │                                           │
│                                ▼                                           │
│                    ┌─────────────────────┐                                 │
│                    │   NETWORK ELEMENTS  │                                 │
│                    │ (BNG, MME, UPF, etc)│                                 │
│                    └─────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### OMC (Operations and Maintenance Center)

Centralized hub for mobile network management.

| Function | Description |
|----------|-------------|
| Network monitoring | Signal strength, traffic load, call quality |
| Fault detection | Alarm management, diagnosis |
| Performance optimization | Parameter adjustment, cell optimization |
| Configuration/provisioning | Base station and switch parameters |
| Traffic management | Load balancing, congestion prevention |
| Security monitoring | Breach detection, abnormal activity |
| Capacity planning | Growth forecasting |
| Backup/disaster recovery | Service restoration |

#### OSS (Operations Support Subsystem)

Software applications for managing network infrastructure, services, and operations.

| Function | Description |
|----------|-------------|
| Network monitoring & fault management | Proactive detection; AI-driven predictive failure |
| Service provisioning & activation | Automated broadband/VoIP/mobile data activation |
| Network inventory & resource management | Asset tracking (fiber, switches, routers, data centers) |
| Performance management | Bandwidth, signal strength, latency monitoring |
| Security & compliance | Cyber protection, regulatory adherence |

**OSS Benefits:** Operational efficiency, faster service delivery, proactive fault management, cost reduction, regulatory compliance.

#### OAM (Operations, Administration, Maintenance)

| Aspect | Description |
|--------|-------------|
| **Operations** | Day-to-day management, resource management, performance optimization |
| **Administration** | Network policies, user accounts, security protocols |
| **Maintenance** | Routine checks, repairs, preventive measures |

---

### 6. Business Support Subsystem (BSS)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BSS FUNCTIONS                                      │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Customer &  │  │ Product &   │  │ Order       │  │ Billing &   │        │
│  │ Account     │  │ Offer       │  │ Management  │  │ Charging    │        │
│  │ Management  │  │ Management  │  │             │  │ Management  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐                                          │
│  │ Revenue     │  │ Payment &   │                                          │
│  │ Assurance   │  │ Collection  │                                          │
│  │ & Financial │  │ Management  │                                          │
│  │ Management  │  │             │                                          │
│  └─────────────┘  └─────────────┘                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**BSS Functions:**

| Function | Description |
|----------|-------------|
| **Customer & Account Management** | Centralized profiles; CRM; customer lifecycle |
| **Product & Offer Management** | Pricing models, promotions, bundles |
| **Order Management** | Validation, orchestration, fulfillment |
| **Billing & Charging Management** | Prepaid/postpaid; real-time charging; invoicing |
| **Revenue Assurance** | Validates billable usage; reduces leakage |
| **Payment & Collection Management** | Multi-channel payments; credit control; dunning |

**Common Attack Vectors on BSS:**

| Vector | Description |
|--------|-------------|
| Social engineering | Manipulating staff |
| Malware/ransomware | Locking or encrypting BSS data |
| Phishing/weak passwords | Initial access |
| Unpatched software | Known vulnerabilities |

---
## 📌 One-Paragraph Takeaway (for memory)

> **Fixed core networks** use BNG (subscriber entry, authentication, QoS), IP/MPLS backbone (high-capacity transport), DHCP (IP assignment), AAA (RADIUS/Diameter), and interconnect via IXP (public internet) or IPX (private, QoS-guaranteed). **2G/3G** has CS domain (MSC, GMSC, HLR, VLR, AuC with authentication triplets RAND/SRES/Ki/Kc) and PS domain (SGSN, GGSN). **4G EPC** is all-IP with MME (control), HSS (subscriber database), S-GW (user plane anchor), P-GW (external gateway), PCRF (policy/charging). **5G SBA** is cloud-native with UPF (user plane) and control functions: AMF (mobility), SMF (sessions), PCF (policy), UDM (subscriber data), AUSF (authentication), NSSF (slice selection), NRF (service discovery), NEF (API exposure), SEPP (inter-network security). **Management:** OMC (monitoring/faults), OAM (operations/administration/maintenance), OSS (automation/provisioning). **BSS** handles customer lifecycle, billing, revenue assurance – and faces social engineering, malware, phishing, and unpatched software risks.

---
