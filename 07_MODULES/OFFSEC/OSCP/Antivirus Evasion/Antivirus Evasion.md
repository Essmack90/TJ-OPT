---
tags: MOCs
---
In this Module, we will cover the following Learning Units:

- Antivirus Software Key Components and Operations
- Bypassing Antivirus Detections
- Antivirus Evasion in Practice

To compromise a target machine, attackers often disable or otherwise bypass antivirus software installed on these systems. As penetration testers, we must understand and be able to recreate these techniques to demonstrate this potential threat to our client.

In this Module, we will discuss the purpose of antivirus software, discover how it works, and outline how it is deployed in most companies. We will examine various methods used to detect malicious software and explore some of the available tools and techniques that will allow us to bypass AV software on target machines.

## 15.1. Antivirus software key components and operations

This Learning Unit covers the following Learning Objectives:

- Recognize Known vs Unknown Threats
- Understand AV Key Components
- Understand AV Detection Engines

[_Antivirus_](https://en.wikipedia.org/wiki/Antivirus_software) (AV), is a type of application designed to prevent, detect, and remove malicious software. It was originally designed to simply remove computer viruses. However, with the development of new types of malware, like bots and [_ransomware_](https://www.crowdstrike.com/cybersecurity-101/malware/types-of-malware/), antivirus software now typically includes additional protections such as [_IDS/IPS_](https://en.wikipedia.org/wiki/Intrusion_detection_system), firewall, website scanners, and more.

## 15.1.1. Known vs unknown threats

In its original design, an antivirus software bases its operation and decisions on signatures. The goal of a signature is to uniquely identify a specific piece of malware. Signatures can vary in terms of type and characteristics that can span from a very generic file hash summary to a more specific binary sequence match. As we'll discover in the following section, an AV comprises different engines responsible for detecting and analyzing specific components of the running system.

A signature language is often defined for each AV engine and thus, a signature can represent different aspects of a piece of malware, depending on the AV engine. For example, two signatures can be developed to contrast the exact same type of malware: one to target the malware file on disk and another to detect its network communication. The semantics of the two signatures can vary drastically as they are intended for two different AV engines. In 2014, a signature language named [_YARA_](https://en.wikipedia.org/wiki/YARA) was open-sourced to allow researchers to query the [_VirusTotal_](https://www.virustotal.com/#/home/upload) platform or even integrate their own malware signatures into AV products. VirusTotal is a malware search engine that allows users to search known malware or submit new samples and scan them against several AV products.

As signatures are written based on known threats, AV products could initially only detect and react based on malware that has already been vetted and documented. However, modern AV solutions, including [_Windows Defender_](https://docs.microsoft.com/en-us/microsoft-365/security/defender-endpoint/microsoft-defender-antivirus-windows?view=o365-worldwide), are shipped with a [_Machine Learning_](https://www.microsoft.com/security/blog/2017/08/03/windows-defender-atp-machine-learning-detecting-new-and-unusual-breach-activity/) (ML) engine that is queried whenever an unknown file is discovered on a system. These ML engines can detect unknown threats. Since ML engines operate on the cloud, they require an active connection to the internet, which is often not an option on internal enterprise servers. Moreover, the many engines that constitute an AV should not borrow too many computing resources from the rest of the system as it could impact the system's usability.

To overcome these AV limitations, [_Endpoint Detection and Response_](https://en.wikipedia.org/wiki/Endpoint_detection_and_response) (EDR) solutions have evolved during recent years. EDR software is responsible for generating security-event telemetry and forwarding it to a [_Security Information and Event Management_](https://en.wikipedia.org/wiki/Security_information_and_event_management) (SIEM) system, which collects data from every company host. These events are then rendered by the SIEM so that the security analyst team can gain a full overview of any past or ongoing attack affecting the organization.

Even though some EDR solutions include AV components, AVs and EDRs are not mutually exclusive as they complement each other with enhanced visibility and detection. Ultimately, their deployment should be evaluated based on an organization's internal network design and current security posture.

## 15.1.2. AV engines and components

At its core, a modern AV is fueled by signature updates fetched from the vendor's signature database that resides on the internet. Those signature definitions are stored in the local AV signature database, which in turn feeds the more specific engines.

A modern antivirus is typically designed around the following components:

- File Engine
- Memory Engine
- Network Engine
- Disassembler
- Emulator/Sandbox
- Browser Plugin
- Machine Learning Engine

Each of the engines above work simultaneously with the signature database to rank specific events as either benign, malicious, or unknown.

The _file engine_ is responsible for both scheduled and real-time file scans. When the engine performs a scheduled scan, it simply parses the entire file system and sends each file's metadata or data to the signature engine. On the contrary, real-time scans involve detecting and possibly reacting to any new file action, such as downloading new malware from a website. To detect such operations, the real-time scanners need to identify events at the kernel level via a specially crafted [_mini-filter driver_](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts). This is the reason why a modern AV needs to operate both in kernel and user land, in order to validate the entire operating system scope.

The _memory engine_ inspects each process's memory space at runtime for well-known binary signatures or suspicious API calls that might result in memory injection attacks, as we'll find shortly.

As the name suggests, the _network engine_ inspects the incoming and outgoing network traffic on the local network interface. Once a signature is matched, a network engine might attempt to block the malware from communicating with its [_Command and Control_](https://en.wikipedia.org/wiki/Botnet#Command_and_control) (C2) server.

To further hinder detection, malware often employs encryption and decryption through custom routines to conceal its true nature. AVs counterattack this strategy by _disassembling_ the malware packers or ciphers and loading the malware into a sandbox, or _emulator_.

The _disassembler_ engine is responsible for translating machine code into assembly language, reconstructing the original program code section, and identifying any encoding/decoding routine. A _sandbox_ is a special isolated environment in the AV software where malware can be safely loaded and executed without causing potential havoc to the system. Once the malware is unpacked/decoded and running in the emulator, it can be thoroughly analyzed against any known signature.

As browsers are protected by the sandbox, modern AVs often employ browser plugins to get better visibility and detect malicious content that might be executed inside the browser.

Additionally, the machine learning component is becoming a vital part of current AVs as it enables detection of unknown threats by relying on cloud-enhanced computing resources and algorithms.

## 15.1.3. Detection methods