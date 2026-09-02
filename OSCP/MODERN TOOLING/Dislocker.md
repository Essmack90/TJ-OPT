# dislocker

A FUSE-based tool that decrypts BitLocker-encrypted volumes on Linux, presenting the decrypted content as a virtual block device for mounting. Used in combination with `losetup` to mount `.vhd`/physical partitions containing BitLocker volumes.

---

## What it replaces, and why it's faster

BitLocker-encrypted volumes from Windows (`.vhd` files, physical disks, forensic images) are opaque blobs on Linux without dislocker. The alternative is booting into Windows to unlock and extract, which is slow and sometimes not possible in an OSCP lab context. dislocker + losetup + mount is a three-step chain entirely on Kali.

## Install

```bash
sudo apt install dislocker
```

## Usage

**The full mount chain for a `.vhd` file:**
```bash
# Step 1: expose the VHD as a loop device with partition scanning
sudo losetup -f -P bitlocker.vhd
sudo losetup -a      # note which device was assigned, e.g. /dev/loop0
                     # partition will appear as /dev/loop0p1

# Step 2: create mountpoints
sudo mkdir -p /mnt/bitlocker_raw /mnt/bitlocker_cleartext

# Step 3: decrypt with dislocker
sudo dislocker -u<PASSWORD> /dev/loop0p1 /mnt/bitlocker_raw/
# -u<PASSWORD>: user passphrase (no space between -u and the password)
# Alternatively: -r for recovery key, -p for PIN

# Step 4: mount the decrypted virtual disk
sudo mount -o loop /mnt/bitlocker_raw/dislocker-file /mnt/bitlocker_cleartext/

# Browse the decrypted NTFS filesystem
ls /mnt/bitlocker_cleartext/
```

**Teardown (in reverse order):**
```bash
sudo umount /mnt/bitlocker_cleartext
sudo umount /mnt/bitlocker_raw
sudo losetup -d /dev/loop0
```

**Recovery key instead of password:**
```bash
sudo dislocker -r <48-digit-recovery-key> /dev/loop0p1 /mnt/bitlocker_raw/
```

**BitLocker hash for offline cracking:**
```bash
bitlocker2john -i bitlocker.vhd > bitlocker_hash.txt
hashcat -m 22100 bitlocker_hash.txt /usr/share/wordlists/rockyou.txt
```

> 🔍 **Worth remembering:** the `-u` flag takes the password immediately after the flag with no space (`-uMyPassword`), not `-u MyPassword`. Older versions differ; check `dislocker --help` on your Kali version if you get a parse error.

> ⚠️ `losetup -P` (partition scan) is required when the VHD has a partition table. Without it you get `/dev/loop0` but no `/dev/loop0p1`, and dislocker has nothing to point at.

## Where this applies in the vault

- [[16. Password Attacks|PA.4]]
- [[Password Attacks (Breakdowns)#BitLocker VHD mount chain: why losetup + dislocker + mount are all needed|Command Breakdowns]]

🔁 [[16. Password Attacks|PA.4]]

#### Tags: #ModernTooling #dislocker #BitLocker #FUSE #losetup #VHD #Forensics #OfflineCracking
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Dislocker supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Dislocker is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
dislocker --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
