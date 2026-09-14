# Linux - Clean Down

**Step 21 of 50 · Linux**

*Remove payloads and restore any modified target files after the box is complete.*

## Run this

> **Why:** This command gathers the linux clean down evidence needed to decide which documented route applies next.
```bash
rm -f /tmp/linpeas.sh
rm -f $PayloadFile
rm -f $ModifiedFile
cp $BackupFile $ModifiedFile
```

## Example output

 > *Example shape only: cleanup paths must be confirmed for the box.*
```
$ test ! -e /tmp/linpeas.sh && echo removed
removed
$ test ! -e $PayloadFile && echo removed
removed
```
## What did you get?

- [ ] Uploaded files are removed → **Run `find $BoxDir/loot -type f -maxdepth 1 -print` and confirm each recorded remote path is absent, then continue**
- [ ] A file was modified → **Run `cp $BackupFile $TargetFile`, then run `sha256sum $TargetFile $BackupFile` and confirm the hashes match**
- [ ] A listener or server is still running → **Run `pkill -f 'python3 -m http.server|nc -lvnp'`, then run `ss -ltnp` and confirm the port is closed**
- [ ] Verification is clean → **The Linux run is complete**

## Notes

The exact cleanup target must be recorded during the run.

If `/etc/sudoers` was modified (e.g. via DOSBox), restore it from the package cache:

> **Why:** This filter extracts readable evidence from the saved output so likely credentials or configuration clues can be validated.
```bash
# Find the original sudoers in the cached package
dpkg -L sudo | grep sudoers
bsdtar -xOf /var/cache/apt/archives/sudo_*.deb ./etc/sudoers > /etc/sudoers
visudo -c   # verify syntax
```

## Gotcha

> [!warning] 💡
> The commands containing `$PayloadFile`, `$ModifiedFile`, and `$BackupFile` are templates. Replace them only with paths you recorded during the box.

> [!warning] 💡
> If you modified `/etc/sudoers`, always verify the file is syntactically valid after restoring it. A broken sudoers file locks out all sudo access. Run `visudo -c` to check.

> [!warning] 💡
> Cleanup paths are placeholders. Replace them only with payloads, users, files, tunnels, or configuration lines that you recorded creating during this box. Verify each removal from the target before closing the session.

Networked verified the cleanup workflow for a PHP upload, cron marker, and temporary network configuration.

For a Networked-style run, remove only the recorded webshell path, controlled marker filenames, and generated interface configuration. Verify the webshell returns `404`, close the listener and shell sessions, then run `boxdone`.

```bash
rm -f "/var/www/html/$Path"
rm -f /var/www/html/uploads/x*
rm -f /home/guly/networked_pwned
rm -f /etc/sysconfig/network-scripts/ifcfg-guly
curl -sS -o /dev/null -w '%{http_code}\n' "http://$BoxIP/$Path"
boxdone
```

For a Poison-style run, no target-side payload files were created. Close the VNC client, terminate the SSH local-forward process, verify the Kali-side tunnel port is closed, and keep the credential-bearing archive in private loot.

```bash
pkill -f "ssh -N -L $TunnelPort:127.0.0.1:$RemotePort"
ss -ltnp | grep "$TunnelPort" || true
boxdone
```

For a Traceback-style login-hook run, restore the original MOTD script and remove the SUID copy and backup created during testing:

```bash
cp /home/sysadmin/00-header.bak /etc/update-motd.d/00-header
rm -f /tmp/rootbash /home/sysadmin/00-header.bak
tail -n 5 /etc/update-motd.d/00-header
stat -c '%U:%G %A %n' /etc/update-motd.d/00-header
boxdone
```

> [!warning] 💡
> Only remove an `authorized_keys` entry if this run added it and you recorded the original file. A successful SSH reconnect is evidence of access, not proof that every key in the file was created during the run.

For a CronOS-style writable root cron target, restore the original application file before removing the temporary backup. Compare the restored file with the backup while it still exists, then remove only the backup created by this run:

~~~bash
cp -p /tmp/artisan.CronOS.backup /var/www/laravel/artisan
cmp -s /var/www/laravel/artisan /tmp/artisan.CronOS.backup && echo "artisan restored"
rm -f /tmp/artisan.CronOS.backup
php -l /var/www/laravel/artisan
ss -ltnp | grep -E ":$Port|:$Port2" || true
boxdone
~~~

Do not delete or overwrite an application file unless its original content and exact path were recorded during the current run.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- no target-side payloads were created; the local hosts mapping was the only recorded configuration change and was restored before closeout
- [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]] -- restored the writable Laravel scheduler, removed its temporary backup, closed listeners, and recorded boxdone
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- removed webshell, SUID helper, and created script tree
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- restored the modified internal PHP page and removed staged key material
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- documented the reset boundary for two fragile custom services
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- restored `/scripts/test.py` and removed the temporary SUID helper
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- removed web shell, callback scripts, SUID helper, and systemd override
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- closed the local box session and recorded target cleanup requirements
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- removed the uploaded webshell, cron marker, temporary config, and closed with `boxdone`
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- closed VNC and SSH forwarding sessions; no target-side payload files were created
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- no target-side persistence was required; closed SSH and recorded `boxdone`
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- removed the RFI server, crafted archive, extracted helper, and closed with `boxdone`; reset is preferred for timer-created artifacts
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- no target-side payloads were created; sessions were closed and `boxdone` was recorded
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- no persistent target-side payloads were required; private evidence was retained and `boxdone` was recorded
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- restored `/etc/update-motd.d/00-header`, removed the temporary SUID Bash and backup, and recorded `boxdone`
- [[OSCP/BOXES/WRITE UPS/Linux/SolidState|SolidState]] -- callback listeners, possible completion-file artifacts, reset-sensitive `/opt/tmp.py`, and the `boxdone` evidence boundary were documented
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- removed the recorded temporary proof path, closed the callback listener, and verified the local port was closed
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- removed recorded XML upload artifacts and verified the application source tree had no leftovers
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- no target-side payloads or configuration changes were required; private completion data was kept out of shared evidence

For a DevOops-style XML upload run, remove only the filenames created during this run. Keep local evidence private and leave the application source and repository unchanged:

```bash
ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP" \
  "rm -f '$RemoteSrcDir/feed.xml' '$RemoteSrcDir/app.xml' '$RemoteSrcDir/feed-source.xml' '$RemoteSrcDir/key.xml' '$RemoteSrcDir/roosa-key.xml'"
ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP" \
  "find '$RemoteSrcDir' -maxdepth 1 -type f \\
   \( -name 'feed.xml' -o -name 'app.xml' -o -name 'feed-source.xml' \\
   -o -name 'key.xml' -o -name 'roosa-key.xml' \) -print"
boxdone
```

An empty `find` result means the recorded XML filenames are absent. Do not remove files merely because they are XML, and do not delete the source repository as cleanup.

For a Knife-style PHP backdoor run, remove only temporary files created during the current session, close the callback listener, and verify the listener port is no longer bound:

```bash
rm -f /tmp/knife-root-proof.txt 2>/dev/null || true
pkill -f "nc -lvnp $Lport" 2>/dev/null || true
ss -ltnp | grep ":$Lport" || true
boxdone
```

Do not remove application files or interpret a private flag record as a cleanup target. The temporary proof path above is valid only when the current run created it and its exact path was recorded.

## Shocker example

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- no target-side payload file was recorded; the callback listener and cleanup evidence boundary were documented

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - XXE]]
- [[Linux - Python Pickle]]
- [[Linux - Credential Search]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
