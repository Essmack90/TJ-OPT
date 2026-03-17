---
tags: [tool, fuzzing]
tool: afl++
category: Fuzzing
installed: true
---

# AFL++ - American Fuzzy Lop

## Overview
Coverage-guided fuzzer for finding vulnerabilities in binaries

## Location
/usr/bin/afl-fuzz

## Basic Usage
afl-gcc -o program program.c
afl-fuzz -i seeds -o findings ./program @@

## Binary-only mode
afl-fuzz -Q -i seeds -o findings ./target @@
