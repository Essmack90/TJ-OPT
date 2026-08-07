# theHarvester

Passive OSINT aggregator, pulls emails, subdomains, IPs, and employee names from a whole batch of public sources (search engines, certificate transparency logs, Shodan, and more) in one run, instead of checking each source by hand.

---

## What it replaces, and why it's faster

[[Information Gathering#6.2. Passive Information Gathering|6.2]] teaches WHOIS, Google dorking, Netcraft, GitHub searching, and Shodan as separate manual techniques, each genuinely worth understanding on its own, since knowing *why* a source leaks what it leaks is what lets you adapt when one source dries up (Netcraft's own service discontinuation partway through this module is a good example of exactly that). theHarvester doesn't replace understanding those sources, it queries most of them in a single pass and de-duplicates the results, useful once the manual technique is understood and the goal shifts to covering ground fast on a real engagement.

## Install

Ships with Kali by default:
```bash
theHarvester -d <domain> -b all
```

## Usage

```bash
# Query every supported source at once
theHarvester -d megacorpone.com -b all

# Restrict to specific sources (faster, useful if some sources need API keys you don't have)
theHarvester -d megacorpone.com -b google,bing,crtsh

# Save results
theHarvester -d megacorpone.com -b all -f results.html
```
*Some sources (Shodan, Hunter.io, etc) need an API key configured in theHarvester's own config file to actually return results, worth checking `theharvester --help` / its config for which sources are active without one before assuming a source came back empty.*

## Where this applies in the vault

- [[Information Gathering#6.2. Passive Information Gathering|6.2]], the whole passive-OSINT section this tool aggregates: WHOIS-adjacent info, subdomains, emails
- Complements [[Information Gathering#6.2.5. Shodan|6.2.5]] (theHarvester can pull from Shodan as one of its sources) without replacing the manual understanding of what Shodan itself indexes

#### Tags: #ModernTooling #TheHarvester #PassiveRecon #OSINT
