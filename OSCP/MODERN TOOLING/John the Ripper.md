# John the Ripper

John the Ripper is an offline password-cracking tool. In Covfefe it was used with `ssh2john` to turn an encrypted OpenSSH private key into a crackable hash, then tested a local wordlist against the key passphrase.

## When to use it

Use John when a recovered credential artifact can be processed offline, such as an encrypted SSH key, password database, archive, document, or shadow file. Offline cracking avoids repeated authentication attempts and therefore avoids network noise and account lockout for this stage.

## Encrypted OpenSSH key workflow

```bash
KeyFile=$BoxDir/loot/id_rsa
HashFile=$BoxDir/loot/id_rsa.john
Wordlist=/usr/share/wordlists/rockyou.txt

ssh2john $KeyFile > $HashFile
john --wordlist=$Wordlist $HashFile
john --show $HashFile
ssh -i $KeyFile $Username@$BoxIP
```

`ssh2john` is the format-conversion step, not the cracker. John reads the generated hash and tests candidate passphrases locally. Keep the private key, hash, and recovered passphrase in private loot, not in a shared write-up.

## Efficiency and alternatives

- Run `john --wordlist=...` before trying broad rules or masks. A leaked key passphrase often appears in a standard wordlist.
- Use `john --show` to confirm the result without repeating the attack.
- Hashcat is a useful alternative when GPU acceleration or custom masks and rules are needed, but John is a compact default for SSH keys because the conversion utility is already available alongside it.
- If the key is not encrypted, skip cracking and test it with the correct account and restrictive permissions: `chmod 600 $KeyFile`.

## Troubleshooting

- `ssh2john: command not found`: locate the helper with `command -v ssh2john` or `find /usr -name ssh2john 2>/dev/null`.
- SSH rejects the key before authentication: check the file type with `file $KeyFile`, set `chmod 600`, and confirm the key was downloaded without an HTML error page.
- John finds nothing: verify the wordlist path, inspect the key header, and only then move to rules or a targeted custom list.

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] - encrypted SSH key conversion and offline passphrase recovery
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] - Kerberos TGS and PKCS#12/PFX password cracking

## Related runbooks

- [[OSCP/RUNBOOK V2/Linux - Credential Search]]
- [[16. Password Attacks|Password Attacks]]

## External resources

- [Openwall John the Ripper](https://www.openwall.com/john/)
- [Openwall jumbo documentation](https://www.openwall.com/john/doc/)

#### Tags: #JohnTheRipper #ssh2john #PasswordCracking #CredentialSearch #Covfefe
