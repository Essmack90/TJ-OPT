---
tags: [tool, fuzzing]
tool: cats
category: Fuzzing
installed: true
---

# CATS - REST API Fuzzer

## Overview
Automated REST API fuzzing using OpenAPI specifications

## Location
/usr/local/bin/cats

## Basic Usage
cats --contract openapi.yaml --server https://api.target.com
cats --contract openapi.yaml --server https://api.target.com --mode positive
cats --contract openapi.yaml --server https://api.target.com --mode negative

## Options
--healthCheck : Check service health first
--list --profiles : Show available profiles
