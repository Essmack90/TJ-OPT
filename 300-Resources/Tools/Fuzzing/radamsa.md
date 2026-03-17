---
tags: [tool, fuzzing]
tool: radamsa
category: Fuzzing
installed: true
---

# Radamsa - Protocol Fuzzer

## Overview
General-purpose protocol fuzzer for generating test cases

## Location
/usr/local/bin/radamsa

## Basic Usage
echo "normal input" | radamsa
echo "test" | radamsa -n 100
radamsa input.txt > fuzzed.txt
radamsa -s 12345 input.txt
