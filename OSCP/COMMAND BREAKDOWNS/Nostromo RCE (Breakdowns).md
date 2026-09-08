# Nostromo RCE (Breakdowns)

## Exploit-DB 47837 identity proof

**Full command:**

```bash
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort "id"
```

**Piece by piece:**

- `python2` -> the supplied proof of concept uses Python 2 syntax.
- `$BoxDir/exploits/nostromo-47837.py` -> the reviewed local copy of Exploit-DB 47837.
- `$BoxIP` -> the authorized target address.
- `$WebPort` -> the Nostromo HTTP port discovered by Nmap.
- `"id"` -> a harmless command used to prove execution and identify the service account before attempting a callback.

**Where this comes from:** [Exploit-DB 47837](https://www.exploit-db.com/exploits/47837) and [[OSCP/RUNBOOK V2/Linux - Nostromo RCE|Linux - Nostromo RCE]].

**Where to look in the response:** Look for `uid=`, `gid=`, and `groups=`. A result such as `uid=33(www-data)` proves RCE but is not a root shell.

🔁 **Seen in:** [[OSCP/BOXES/WRITE UPS/Linux/Traverxec#6. Confirm command execution|Traverxec command-execution proof]]

## The exact `journalctl` sudo rule

**Full command:**

```bash
sudo -n /usr/bin/journalctl -n5 -unostromo.service
```

**Piece by piece:**

- `sudo -n` -> use sudo non-interactively and fail instead of prompting for a password.
- `/usr/bin/journalctl` -> the exact permitted binary.
- `-n5` -> request the last five log lines.
- `-u nostromo.service` -> restrict the journal view to the Nostromo service. The original command uses the compact form `-unostromo.service`.
- The pager -> the output viewer may be `less`; its `!` command runs a shell command in the pager's privilege context.
- `!/bin/bash` -> entered inside the pager, not at the shell prompt.

**Where this comes from:** the user-owned `/home/david/bin/server-stats.sh` helper and [GTFOBins journalctl](https://gtfobins.github.io/gtfobins/journalctl/).

**Where to look in the response:** `sudo -l` may not make the rule obvious, and a generic `sudo journalctl` may fail. The decisive evidence is the script's exact invocation succeeding, followed by a pager and `id` reporting UID 0.

🔁 **Seen in:** [[OSCP/BOXES/WRITE UPS/Linux/Traverxec#15. Execute the exact sudo command|Traverxec pager escape]]

## Encrypted SSH key workflow

**Full command:**

```bash
ssh2john $KeyFile > $HashFile
john --wordlist=/usr/share/wordlists/rockyou.txt $HashFile
ssh -i $KeyFile $Username@$BoxIP
```

**Piece by piece:**

- `ssh2john` -> extracts the key's encryption metadata into a John-compatible hash representation.
- `$KeyFile` -> the original encrypted private key; preserve it as evidence.
- `$HashFile` -> private crack output, separate from the original key.
- `john --wordlist=...` -> tests the standard wordlist offline.
- `ssh -i` -> uses the validated private key for the target account.

**Where this comes from:** [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] and the SSH-key section of the John the Ripper documentation.

**Where to look in the response:** A successful crack is shown by John's completion output. Validate the key with `ssh-keygen -y` or an SSH login, but keep the passphrase and key out of shared notes.

🔁 **Seen in:** [[OSCP/BOXES/WRITE UPS/Linux/Traverxec#12. Crack and validate the encrypted SSH key|Traverxec encrypted-key workflow]]
