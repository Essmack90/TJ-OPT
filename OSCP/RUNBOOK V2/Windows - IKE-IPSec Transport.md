---
tags: [OSCP, RUNBOOKV2, Windows, IKE, IPSec, TransportMode, Enumeration]
status: Active
---

# Windows - IKE/IPSec Transport

**Step 2A of 50 · Windows**

*Fingerprint IKEv1 and establish a scoped IPSec transport policy when UDP 500 is exposed.*

## When to use this page

Use this page when UDP 500 is open or when a target description indicates IKE, IPSec, or a concealed TCP service surface. IKE, the Internet Key Exchange protocol, negotiates the cryptographic parameters; IPSec then applies the resulting policy to protected traffic. The page assumes that any required PSK has already been recovered through an authorized enumeration path such as [[Linux - SNMP Enum]].

## Run this

> **Why:** `ike-scan` identifies the peer's IKE version, authentication mode, encryption, integrity, and Diffie-Hellman group before a local IPSec configuration is attempted.
```bash
sudo ike-scan -M "$BoxIP" | tee "$BoxDir/loot/ike-scan.txt"
```

## Example output

```text
Main Mode Handshake returned
SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK)
```

## What did you get?

- [ ] Main Mode or Aggressive Mode handshake returned → record the proposal and continue to the scoped configuration below
- [ ] No response → confirm UDP 500 with Nmap, verify `$BoxIP`, and check the VPN route before changing proposals
- [ ] A proposal is returned but authentication is not PSK → route to the matching certificate or XAuth workflow instead of guessing a secret
- [ ] The IKE_SA establishes but the CHILD_SA fails → check the traffic selector and ESP proposal

## Build the scoped transport configuration

> **Why:** A transport-mode policy protects host-to-host traffic, while the TCP selector limits the policy to the service traffic that the target is hiding. Keeping the selector narrow avoids claiming a routed subnet that the peer did not negotiate.
```bash
cat > "$BoxDir/ipsec.conf" <<EOF
config setup
    uniqueids=no
    charondebug="ike 2, knl 2, cfg 2"

conn conceal
    keyexchange=ikev1
    authby=secret
    type=transport
    left=%defaultroute
    right=$BoxIP
    rightsubnet=$BoxIP[tcp]
    ike=3des-sha1-modp1024!
    esp=3des-sha1!
    auto=start
EOF

cat > "$BoxDir/ipsec.secrets" <<EOF
%any %any : PSK "$Password"
EOF

chmod 600 "$BoxDir/ipsec.secrets"
```

`$Password` must already contain the recovered PSK in private shell state. Do not replace it with a literal in a shared note. The `!` suffix forces the proposal rather than permitting a fallback that may not match the peer.

## Start strongSwan without changing the system secrets file

> **Why:** The local starter expects secrets at `/etc/ipsec.secrets`, so a private mount namespace lets the test use the box-specific file without overwriting the machine-wide configuration.
```bash
sudo ss -ulnp | grep ":$IKEPort" || true
sudo ipsec stop 2>/dev/null || true

sudo unshare --mount --propagation private bash -lc \
  "mount --bind '$BoxDir/ipsec.secrets' /etc/ipsec.secrets && \
   exec /usr/lib/ipsec/starter --nofork --conf '$BoxDir/ipsec.conf'" \
  2>&1 | tee "$BoxDir/loot/ipsec-start.txt" &
```

If another `charon` process owns UDP 500, the new starter can fail locally even though the target is reachable. Stop only the stale local IPSec service, then retry the private starter.

## Verify IKE, CHILD_SA, and XFRM state

> **Why:** An IKE handshake alone does not expose the protected TCP services. The IKE_SA and CHILD_SA establish the authenticated session and its traffic selectors; the XFRM policy shows that the Linux kernel installed those selectors.
```bash
sleep 5
sudo ip xfrm policy
sudo ip xfrm state
```

## What did you get?

- [ ] IKE_SA and CHILD_SA are established with a TCP selector → run the post-IPSec service scan
- [ ] IKE_SA is established but the selector is wrong → change only `rightsubnet=$BoxIP[tcp]` and retry
- [ ] `INVALID_ID_INFORMATION` appears → the peer rejected the traffic selector; do not broaden it blindly
- [ ] No local XFRM policy appears → inspect `$BoxDir/loot/ipsec-start.txt`, check for a port conflict, and verify the proposal

## Re-scan the now-reachable TCP surface

> **Why:** IPSec changes the effective attack surface, so the pre-policy TCP result must not be reused as the service list.
```bash
boxset OpenPorts "21,80,135,139,445,3389,5985,8080"
sudo nmap -Pn -n -sT -sV --version-light \
  -p "$OpenPorts" -oA "$BoxDir/nmap/post-ipsec" "$BoxIP"
```

Route the result to [[Windows - Service Scan]], then continue with the matching FTP, IIS, SMB, or other Windows service page. Conceal used [[Windows - FTP Enumeration]] and [[Windows - Web - FTP Upload]] after this stage.

## Gotchas

> [!warning] IKE is not access
> `ike-scan` can prove that the peer responds without proving that the PSK is correct or that a usable CHILD_SA can be negotiated.

> [!warning] Selector scope matters
> A transport-mode policy for the wrong protocol or host can establish partially and still leave the TCP services inaccessible.

> [!tip] Preserve the old and new scans
> Keep the pre-IPSec and post-IPSec Nmap outputs as separate files. The difference is the evidence that the network-layer gate was real.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- IKEv1 PSK fingerprinting, strongSwan transport mode, XFRM verification, and post-IPSec service discovery

## Related stages

- [[Port Triage]]
- [[Linux - SNMP Enum]]
- [[Windows - Service Scan]]
- [[Windows - FTP Enumeration]]
- [[Windows - Clean Down]]

## External Resources

- [ike-scan](https://github.com/royhills/ike-scan)
- [strongSwan documentation](https://docs.strongswan.org/)
- [HackTricks IPSec and IKE](https://book.hacktricks.wiki/en/network-services-pentesting/ipsec-ike-vpn.html)

## Why this matters for OSCP

This stage makes a hidden network boundary explicit. It teaches the difference between discovering an IKE peer, authenticating the peer, installing a kernel policy, and finally enumerating the service surface carried by that policy.
