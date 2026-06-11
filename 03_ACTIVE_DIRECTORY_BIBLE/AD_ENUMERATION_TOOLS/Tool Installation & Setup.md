## SECTION 1: AD ENUMERATION TOOLS
### Tool Installation & Setup

```bash
# Install all AD tools on Kali
sudo apt update && sudo apt install -y \
    bloodhound \
    neo4j \
    crackmapexec \
    impacket-scripts \
    evil-winrm \
    ldap-utils \
    rpcclient \
    smbclient \
    enum4linux \
    windapsearch \
    certipy-ad \
    python3-impacket \
    kerberos-user-enum \
    chisel
# Start Neo4j for BloodHound
sudo neo4j console
# Navigate to http://localhost:7474
# Default credentials: neo4j:neo4j
# Download SharpHound for Windows
git clone https://github.com/BloodHoundAD/BloodHound.git
# Compile or download pre-compiled SharpHound.exe