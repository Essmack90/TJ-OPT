---
tags: [index, fuzzing]
---

# Fuzzing Tools Index

## Tools

- [[boofuzz]] - Network protocol fuzzing
- [[cats]] - REST API fuzzing
- [[afl++]] - Binary coverage-guided fuzzing
- [[radamsa]] - Input generation fuzzing

## Quick Commands

afl-fuzz -i seeds -o findings ./target
boofuzz my_script.py
cats --contract openapi.yaml --server https://api.target.com
radamsa input.txt
