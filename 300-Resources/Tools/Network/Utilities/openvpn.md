---
tags: [tool, vpn, network]
tool: "openvpn"
category: "Network Utilities"
installed: true
phase: [pivoting]
---

# OpenVPN - VPN Client/Server

## Overview
Virtual Private Network solution

## Location
/usr/sbin/openvpn

## Basic Usage
sudo openvpn --config config.ovpn
sudo openvpn --remote server --dev tun

## Common Options
--config : Config file
--remote : Remote server
--dev : Device type

## Related Tools
wireguard
