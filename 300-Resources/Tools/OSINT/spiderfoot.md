---
tags: [tool, osint, automation]
tool: "spiderfoot"
category: "OSINT"
installed: true
phase: [recon]
---

# SpiderFoot - Automated OSINT

## Tool Overview
Purpose: Automated OSINT collection and correlation
Location: http://localhost:5001 (Docker)

## When to Use
- Large-scale OSINT investigations
- Automated data correlation
- Finding relationships between data points

## How to Use It

Start SpiderFoot:
docker start spiderfoot

Access Web Interface:
http://localhost:5001

View Logs:
docker logs spiderfoot

Stop SpiderFoot:
docker stop spiderfoot

## Key Features
- 200+ modules
- Correlation engine
- Scan scheduling
- Report generation

## Related Tools
sn0int, recon-ng
