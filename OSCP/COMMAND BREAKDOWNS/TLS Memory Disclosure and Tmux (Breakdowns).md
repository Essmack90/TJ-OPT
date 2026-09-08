# TLS Memory Disclosure and Tmux, Command Breakdowns

## Heartbleed capture

**Full command:**

```bash
python2 $BoxDir/exploits/heartbleed-32764.py $BoxIP -p $SSLPort > $BoxDir/loot/heartbleed-output.txt
```

**Piece by piece:**

- `python2` -> runs the legacy Exploit-DB client in the interpreter it expects.
- `$BoxDir/exploits/heartbleed-32764.py` -> the reviewed CVE-2014-0160 client; inspect it before changing any request fields.
- `$BoxIP -p $SSLPort` -> selects the target and HTTPS service identified during recon.
- `>` -> saves the raw hex dump because useful memory may be buried in a large response.

**Where this comes from:** [Exploit-DB 32764](https://www.exploit-db.com/exploits/32764), with the vulnerability independently confirmed by the Nmap `ssl-heartbleed` NSE script.

**Where to look in the response:** `type = 24`, an oversized response length, and `WARNING: server returned more data than it should`.

## Hex representation versus encrypted key

**Full command:**

```bash
xxd -r -p $BoxDir/loot/hype_key $BoxDir/loot/hype_key.decoded
```

**Piece by piece:**

- `xxd` -> converts between byte representations and hexadecimal text.
- `-r` -> reverses a hex dump back into bytes.
- `-p` -> treats the input as plain hexadecimal without offsets or ASCII columns.
- The two paths -> keep the downloaded representation intact while creating a separate decoded artifact for validation.

**Where this comes from:** the standard `xxd` utility and the key format recorded in the supplied `/dev/` capture.

**Where to look in the response:** `file` should identify the output as an encrypted RSA private key. The encryption metadata means the passphrase is still required.

## Legacy SSH options

**Full command:**

```bash
ssh -i $BoxDir/loot/hype_key.decoded $Username@$BoxIP -o 'HostKeyAlgorithms=+ssh-rsa' -o 'PubkeyAcceptedAlgorithms=+ssh-rsa' -o 'KexAlgorithms=+diffie-hellman-group1-sha1'
```

**Piece by piece:**

- `-i` -> selects the recovered private key rather than password authentication.
- `HostKeyAlgorithms=+ssh-rsa` -> re-enables the legacy RSA host-key algorithm required by the old server.
- `PubkeyAcceptedAlgorithms=+ssh-rsa` -> permits the RSA public-key authentication method used by the key.
- `KexAlgorithms=+diffie-hellman-group1-sha1` -> re-enables the old key-exchange method requested by the daemon.

**Where this comes from:** the OpenSSH error messages and the legacy SSH negotiation documented in the Linux credential runbook.

**Where to look in the response:** distinguish a local key passphrase prompt from a negotiation error and from a remote login failure. A successful login banner followed by `id` confirms the route.

## Tmux socket selection

**Full command:**

```bash
tmux -S $TmuxSocket ls
tmux -S $TmuxSocket attach-session -t 0
```

**Piece by piece:**

- `-S $TmuxSocket` -> tells tmux to use the non-default Unix socket discovered during local enumeration.
- `ls` -> lists sessions without attaching or changing pane state.
- `attach-session -t 0` -> attaches to the exact session target returned by the listing.

**Where this comes from:** the [tmux manual](https://man7.org/linux/man-pages/man1/tmux.1.html) and the socket permissions recorded on Valentine.

**Where to look in the response:** verify the server and session owner with `id`. The socket name alone does not prove that the attached shell is root.

🔁 **Seen in:** [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]]

