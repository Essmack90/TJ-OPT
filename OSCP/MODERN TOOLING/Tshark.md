# Tshark

Tshark is Wireshark's command-line interface. It is useful for fast, reproducible protocol triage and field extraction when a packet capture is recovered during web or host enumeration.

## Use it after identifying the artifact

~~~bash
file "$BoxDir/loot/capture-$ObjectID.pcap"
capinfos "$BoxDir/loot/capture-$ObjectID.pcap"
tshark -r "$BoxDir/loot/capture-$ObjectID.pcap" -q -z io,phs
~~~

Use display filters that match the protocol tree:

~~~bash
tshark -r capture.pcap \
  -Y 'ftp.request.command == "USER" || ftp.request.command == "PASS"' \
  -T fields -e frame.number -e ftp.request.command -e ftp.request.arg

tshark -r capture.pcap \
  -Y 'http.authbasic || telnet || ftp' \
  -T fields -e frame.number -e tcp.stream -e ip.src -e ip.dst
~~~

## Privacy boundary

PCAPs may contain passwords, cookies, tokens, internal addresses, and session data. Save the original capture and authentication-bearing fields in mode-600 private loot. Do not send raw tshark output to shared transcripts, screenshots, or the Obsidian vault.

Tshark accelerates inspection; it does not decide whether a web object was accessible legitimately. Prove the IDOR with bounded adjacent-object comparison, then use the captured credential only against the evidence-backed service.

## Related knowledge

- [[OSCP/MODULES/06. Information Gathering|Module 6: Information Gathering]]
- [[OSCP/MODULES/16. Password Attacks#16.3.6.4. Network Traffic Credential Capture (Wireshark)|Module 16: Network Traffic Credential Capture]]
- [[OSCP/RUNBOOK V2/Linux - IDOR and PCAP Credential Recovery|Linux - IDOR and PCAP Credential Recovery]]
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]]

## Install

~~~bash
sudo apt install tshark
~~~

## Why this matters for OSCP

Tshark turns a potentially distracting binary capture into a repeatable evidence workflow: identify protocols, filter the relevant fields, preserve sensitive output privately, and validate one supported credential path.
