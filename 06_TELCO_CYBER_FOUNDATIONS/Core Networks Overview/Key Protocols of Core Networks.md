
### 1. Session Initiation Protocol (SIP)

**Definition:** A set of rules enabling devices (phones, computers) to make voice and video calls over the internet. SIP acts as a **communication facilitator** – locating devices, initiating/ending calls, and managing conversations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIP CALL FLOW                                       │
│                                                                             │
│   ┌──────────┐                    ┌──────────┐                             │
│   │  Device  │                    │  Device  │                             │
│   │   (A)    │                    │   (B)    │                             │
│   └────┬─────┘                    └────┬─────┘                             │
│        │                               │                                    │
│        │  1. INVITE (SIP) ────────────►│                                    │
│        │                               │                                    │
│        │  2. 180 Ringing ◄────────────│                                    │
│        │                               │                                    │
│        │  3. 200 OK ◄─────────────────│                                    │
│        │                               │                                    │
│        │  4. ACK ────────────────────►│                                    │
│        │                               │                                    │
│        │  ◄────── RTP (Audio/Video) ──►│                                    │
│        │                               │                                    │
│        │  5. BYE ─────────────────────►│                                    │
│        │                               │                                    │
│        │  6. 200 OK ◄─────────────────│                                    │
│        │                               │                                    │
│   ┌────┴─────┐                    ┌────┴─────┐                             │
│   │  Device  │                    │  Device  │                             │
│   │   (A)    │                    │   (B)    │                             │
│   └──────────┘                    └──────────┘                             │
│                                                                             │
│   SIP = Call setup, control, teardown (SIP server coordinates)              │
│   RTP = Actual audio/video transport                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Protocol | Role |
|----------|------|
| **SIP** | Initiates, controls, terminates calls (signaling) |
| **RTP** (Real-time Transport Protocol) | Transmits audio/video data |

**Standardisation:** IETF RFCs.

**Key impact:** Revolutionised online communication – versatile, efficient, cost-effective voice/video calls.

---

### 2. RADIUS (Remote Authentication Dial-In User Service)

**Definition:** Networking protocol for authenticating and authorizing users accessing a remote network, plus accounting for usage.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RADIUS ARCHITECTURE                                 │
│                                                                             │
│   ┌──────────────┐      RADIUS      ┌──────────────┐                       │
│   │    User      │◄────────────────►│   RADIUS     │                       │
│   │  (Supplicant)│                   │   Server     │                       │
│   └──────┬───────┘                   └──────┬───────┘                       │
│          │                                  │                               │
│          │ (Access Request)                 │ (User credentials DB)        │
│          ▼                                  ▼                               │
│   ┌──────────────┐                   ┌──────────────┐                       │
│   │    NAS       │                   │   LDAP /     │                       │
│   │ (RADIUS      │                   │   SQL /      │                       │
│   │  Client)     │                   │   Active Dir │                       │
│   └──────────────┘                   └──────────────┘                       │
│                                                                             │
│   Ports: 1812 (Authentication/Authorization), 1813 (Accounting)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Core Functions (AAA):**

| Function | Description |
|----------|-------------|
| **Authentication** | Verifies users/devices before granting network access |
| **Authorization** | Allocates permissions for specific services |
| **Accounting** | Tracks resource usage (packets, bytes, session duration) |

**Key ports:** 1812 (Auth/Authz), 1813 (Accounting)

**Comparison to TCP:** Robust security comparable to TCP.

---

### 3. DIAMETER

**Definition:** A comprehensive improvement over RADIUS for AAA operations. Essential for mobile networks, IMS (IP Multimedia Subsystem), and IoT.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RADIUS vs. DIAMETER                                      │
│                                                                             │
│   ┌─────────────────────────┐      ┌─────────────────────────┐             │
│   │        RADIUS           │      │        DIAMETER         │             │
│   ├─────────────────────────┤      ├─────────────────────────┤             │
│   │ UDP (unreliable)        │      │ TCP/SCTP (reliable)     │             │
│   │ No peer-to-peer         │      │ Peer-to-peer            │             │
│   │ Limited AVPs            │      │ Extensible AVPs         │             │
│   │ No failover (basic)     │      │ Application failover    │             │
│   │ No session management   │      │ Explicit session mgmt   │             │
│   │ No capability negotiat. │      │ Capability negotiation  │             │
│   │ Legacy                  │      │ Modern (4G/5G/IMS/IoT)  │             │
│   └─────────────────────────┘      └─────────────────────────┘             │
│                                                                             │
│   AVP = Attribute-Value Pair (encapsulates username, password, session     │
│         details, configuration parameters)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Components:**

| Component | Description |
|-----------|-------------|
| **AVP** (Attribute-Value Pair) | Encapsulates usernames, passwords, session details, config parameters – makes DIAMETER extensible |
| **Peer-to-peer communication** | Dynamic peer discovery for scalability |
| **Session management** | Tracks ongoing transactions for efficient resource utilization |

**Advantages over RADIUS:** Reliability (TCP/SCTP), scalability, extensibility (AVPs), failover support, explicit session management.

**Disadvantages:** Complexity, higher CPU/memory/bandwidth usage.

---

### 4. Signaling System 7 (SS7)

**Definition:** International telecommunication standard defining how network elements in the **Public Switched Telephone Network (PSTN)** exchange information and control signals.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SS7 NETWORK                                        │
│                                                                             │
│   ┌─────────────┐                    ┌─────────────┐                       │
│   │    SSP      │◄──────────────────►│    STP      │                       │
│   │ (Service    │                    │ (Signal     │                       │
│   │  Switching  │                    │  Transfer   │                       │
│   │  Point)     │                    │  Point)     │                       │
│   └──────┬──────┘                    └──────┬──────┘                       │
│          │                                  │                               │
│          ▼                                  ▼                               │
│   ┌─────────────┐                    ┌─────────────┐                       │
│   │    SCP      │                    │    SCP      │                       │
│   │ (Service    │                    │ (Service    │                       │
│   │  Control    │                    │  Control    │                       │
│   │  Point)     │                    │  Point)     │                       │
│   └─────────────┘                    └─────────────┘                       │
│                                                                             │
│   Functions: Call routing, billing, SMS, advanced calling features         │
│   Nodes known as "signaling points"                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What it manages:**
- Routing and billing of telephone calls
- Advanced calling features
- SMS

**⚠️ CRITICAL SECURITY VULNERABILITIES:**

| Vulnerability | Description |
|---------------|-------------|
| **No encryption** | SMS messages are unencrypted and easily readable |
| **No mutual authentication** | SS7 was designed before digital encryption/authentication era |
| **Location tracking** | Governments/attackers can track mobile users worldwide without GPS |
| **Call/SMS interception** | Attackers can redirect calls and SMS 2FA codes |
| **Decryption key access** | GSM call decryption keys accessible via SS7 network |

**Known attack types:**
- **SS7 probe / IMSI catcher** – intercepts SMS and call data
- **2FA bypass** – redirect SMS multifactor codes to attacker-controlled numbers
- **Passive exploitation** – often goes undetected

> **Why still in use:** SS7 remains essential for call routing, SMS delivery, inter-operator signaling, roaming, and billing. Modern networks (4G/5G) use SS7 primarily for fallback and interworking with legacy systems.

---

### 5. GPRS Tunnelling Protocol (GTP)

**Definition:** IP-based protocol suite for transmitting GPRS within GSM, UMTS, LTE, and 5G NR networks.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GTP PROTOCOL SUITE                                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         GTP-C (Control)                              │   │
│   │  • Session activation/deactivation                                  │   │
│   │  • QoS adjustments                                                  │   │
│   │  • Roaming updates                                                  │   │
│   │  • Mobility management (eGTP-C/GTPv2-C)                             │   │
│   │  • Inter-LTE handovers                                              │   │
│   │  • UDP port 2123                                                    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         GTP-U (User Data)                            │   │
│   │  • Tunneling protocol for user data                                  │   │
│   │  • Multiple tunnels per subscriber                                   │   │
│   │  • TEID (Tunnel Endpoint Identifier) for security                    │   │
│   │  • Encapsulates IP packets                                           │   │
│   │  • UDP port 2152 (GTPv1-U)                                           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         GTP' (Charging)                              │   │
│   │  • Transfers charging data to CGF (Charging Gateway Function)       │   │
│   │  • TCP/UDP port 3386                                                │   │
│   │  • Same message structure as GTP-C/GTP-U                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Component | Function | Port |
|-----------|----------|------|
| **GTP-C** | Control plane – session activation, QoS, roaming, mobility | UDP 2123 |
| **GTP-U** | User plane – tunnels user data, TEID for security | UDP 2152 |
| **GTP'** | Charging – transfers CDRs to billing systems | TCP/UDP 3386 |

**Key concept:** **TEID (Tunnel Endpoint Identifier)** – identifies individual tunnels for enhanced security.

---

### 6. HTTP/2

**Definition:** 2015 protocol addressing HTTP/1.x shortcomings (security, reliability, mobile device suitability, point-to-point limitations).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HTTP/2 FEATURES                                          │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         MULTIPLEXING                                │   │
│   │  Multiple requests/responses over a single connection               │   │
│   │  Reduces overhead, optimizes network resource utilization           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         BINARY PROTOCOL                              │   │
│   │  Text → Binary (reduces data size, increases efficiency)            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         SERVER PUSH                                  │   │
│   │  Server preemptively pushes responses to client caches              │   │
│   │  Eliminates need for multiple requests                              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Additional benefits: Decreased RTT, increased throughput, enhanced       │
│   security (TLS support), backward compatible with HTTP/1.x                │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Features:**

| Feature | Description |
|----------|-------------|
| **Multiplexing** | Multiple requests/responses over single connection |
| **Binary protocol** | Reduced data size, increased efficiency |
| **Server push** | Preemptive response pushing to client caches |
| **Backward compatibility** | Seamless integration with existing HTTP systems |
| **Reduced RTT** | Faster website loading |
| **TLS support** | Enhanced security |

---

### 7. HTTP/3

**Definition:** Latest HTTP version (RFC 9114, 2022). Operates over **QUIC** (UDP-based) instead of TCP – "HTTP over QUIC."

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HTTP/2 vs HTTP/3                                         │
│                                                                             │
│   HTTP/2                                HTTP/3                              │
│   ┌─────────────────┐                   ┌─────────────────┐                 │
│   │   Application   │                   │   Application   │                 │
│   ├─────────────────┤                   ├─────────────────┤                 │
│   │      HTTP/2     │                   │      HTTP/3     │                 │
│   ├─────────────────┤                   ├─────────────────┤                 │
│   │    TLS (opt)    │                   │   QUIC (TLS     │                 │
│   ├─────────────────┤                   │   embedded)     │                 │
│   │      TCP        │                   ├─────────────────┤                 │
│   └─────────────────┘                   │      UDP        │                 │
│                                          └─────────────────┘                 │
│                                                                             │
│   Problems with HTTP/2 over TCP:          HTTP/3 over QUIC fixes:          │
│   • Head-of-line blocking                • No head-of-line blocking        │
│   • No connection migration              • Seamless network switching      │
│   • TLS optional (may be missing)        • TLS mandatory by default        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Comparison Table (HTTP/2 vs. HTTP/3):**

| Feature | HTTP/2 | HTTP/3 |
|---------|--------|--------|
| **Transport protocol** | TCP | QUIC (over UDP) |
| **Head-of-line blocking** | Yes (for multiplexed streams) | No (UDP out-of-order delivery) |
| **TLS encryption** | Optional | Embedded in QUIC (mandatory) |
| **Connection migration** | No | Yes (via connection IDs) |
| **Error handling** | Limited | Enhanced (via QUIC) |

**Why HTTP/3 matters for mobile:** Users frequently switch networks (WiFi ↔ cellular). QUIC's connection migration allows seamless handoff without interrupting ongoing connections – critical for modern mobile-heavy internet usage.

## 📌 One-Paragraph Takeaway (for memory)

> **SIP** handles call signaling (setup, control, teardown) while RTP transports audio/video. **RADIUS** provides AAA (Authentication, Authorization, Accounting) on UDP ports 1812/1813. **DIAMETER** improves on RADIUS with TCP/SCTP, peer-to-peer, extensible AVPs, session management, and failover – essential for 4G/5G/IMS/IoT. **SS7** (PSTN signaling) manages call routing, SMS, and billing but has critical vulnerabilities: no encryption, no mutual authentication → location tracking, SMS interception, 2FA bypass. **GTP** has three components: GTP-C (control, UDP 2123), GTP-U (user data, UDP 2152, TEID for security), and GTP' (charging, TCP/UDP 3386). **HTTP/2** improved with multiplexing, binary protocol, server push, reduced RTT, and TLS support. **HTTP/3** runs over QUIC (UDP) instead of TCP – eliminates head-of-line blocking, supports connection migration (critical for mobile), and embeds TLS by default.
