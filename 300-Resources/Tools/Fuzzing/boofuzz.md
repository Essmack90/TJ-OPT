---
tags: [tool, fuzzing]
tool: boofuzz
category: Fuzzing
installed: true
---

# boofuzz - Network Protocol Fuzzer

## Overview
Python-based network protocol fuzzing framework (successor to Sulley)

## Location
/usr/local/bin/boofuzz

## Basic Usage
boofuzz my_fuzzer.py

## Example Script
from boofuzz import *
session = Session(target=Target(connection=SocketConnection("127.0.0.1", 21)))
s_initialize("user")
s_static("USER")
s_delim(" ")
s_string("anonymous")
session.connect(s_get("user"))
session.fuzz()

## Web UI
http://localhost:26000
