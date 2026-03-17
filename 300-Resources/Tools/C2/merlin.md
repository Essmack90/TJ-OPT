---
tags: [tool, c2]
tool: merlin
category: C2
installed: true
---

# Merlin - Go C2 Framework

## Overview
Cross-platform C2 framework written in Go

## Location
/usr/local/bin/merlin-server
~/tools/pivoting/windows/merlin-agent.exe

## Usage

### Start Server
merlin-server

### Agent Commands (in server)
help
list agents
use agent [id]
shell whoami
upload local remote
download remote local
socks start 9050

### Web UI
https://localhost:8443
