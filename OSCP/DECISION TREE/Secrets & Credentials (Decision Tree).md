# Secrets & Credentials, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for private keys and other secrets. Will likely absorb more content once a dedicated Password Attacks module is covered.

---

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
