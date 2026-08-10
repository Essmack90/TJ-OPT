# Rustscan

Fast port scanner, written in Rust. Speeds up the *port discovery* step, not exploitation, still feeds straight into `nmap` for the actual service/version detection the OSCP methodology teaches.

---

## What it replaces, and why it's faster

The manual approach taught in [[Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3]] runs a full 65535-port `nmap -p- --min-rate 5000` sweep, which can still take several minutes on a slow link even with rate tuning. Rustscan scans all 65k ports in a few seconds by opening a huge number of async sockets at once, then hands the open-port list straight to `nmap` for the actual `-sC -sV` work nmap is good at. It's not a replacement for nmap, it's a fast pre-filter so nmap only has to look at ports that are actually open.

## Install

Not in Kali's official apt repos as of this writing, install via Cargo or the GitHub release `.deb`:
```bash
# Cargo (needs Rust installed)
cargo install rustscan

# or grab the .deb from the releases page directly
# https://github.com/bee-san/RustScan/releases
```

## Usage

```bash
# Scan every port, pipe straight into nmap for -sC -sV
rustscan -a <target> -- -sC -sV -oA nmap_full

# Specific port range
rustscan -a <target> --range 1-1024

# Quiet mode, just the open ports, useful for scripting
rustscan -a <target> -q
```
*Everything after `--` gets passed straight to nmap as its own arguments, so the workflow is genuinely "rustscan finds the open ports, nmap does everything else exactly like the module teaches," not a different tool replacing nmap's role.*

## Where this applies in the vault

- [[Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3, Port Scanning with Nmap]], the full-range `-p-` sweep specifically
- [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]]'s NSE script workflow, still needs the open-port list first
- [[Windows Methodology#Phase 1: Reconnaissance|Windows Methodology]] and [[Linux Methodology#Phase 1: Reconnaissance|Linux Methodology]]'s Step 1 port scanning

#### Tags: #ModernTooling #Rustscan #PortScanning #Nmap #Recon
