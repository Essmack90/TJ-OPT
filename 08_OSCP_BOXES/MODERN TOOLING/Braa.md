# Braa

Ultra-fast mass SNMP scanner, its own SNMPv1/v2 stack, no dependency on `net-snmp`'s tools. Ships in Kali.

---

## What it replaces, and why it's faster

[[Information Gathering#6.4.6. SNMP Enumeration|6.4.6]] teaches `snmpwalk` to enumerate the entire MIB tree of one host at a time. Braa can query dozens or hundreds of hosts simultaneously in a single process, useful the moment SNMP enumeration needs to happen across more than one device (a whole subnet of routers/printers/switches, for instance) rather than one box at a time.

## Install

```bash
sudo apt install braa
```

## Usage

```bash
# Single host, single OID (numerical OIDs only, braa doesn't resolve MIB names like snmpwalk does)
braa <community>@<target>:.1.3.6.1.2.1.1.1.0

# Walk a subtree (append 'x' to the OID prefix)
braa <community>@<target>:.1.3.6.1.2.1.1.1.0x

# Many hosts at once, from a file of community@host:oid lines
braa -c braa_targets.txt
```
*The trade-off for the speed: braa wants numerical OIDs, not the friendly `system.sysName.0` style names `snmpwalk` accepts. Look up the OID first (or just use `snmpwalk` for a quick one-host exploratory pass, then switch to `braa` once scanning many hosts at once actually matters).*

## Where this applies in the vault

- [[Information Gathering#6.4.6. SNMP Enumeration|6.4.6, SNMP Enumeration]], as the multi-host complement to the module's own `onesixtyone` (community string brute force) + `snmpwalk` (single-host MIB walk) combination

#### Tags: #ModernTooling #Braa #SNMP #MassScanning
