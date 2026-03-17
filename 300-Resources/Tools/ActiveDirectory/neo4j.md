---
tags: [tool, database, bloodhound]
tool: "neo4j"
category: "Active Directory"
installed: true
phase: [analysis]
---

# Neo4j - Graph Database for BloodHound

## Tool Overview
Purpose: Graph database backend for BloodHound
Location: /usr/bin/neo4j

## How to Use It

Start Neo4j:
sudo systemctl start neo4j
sudo neo4j console

Default Credentials:
Username: neo4j
Password: neo4j

Change Password:
curl -H "Content-Type: application/json" -X POST -d '{"password":"newpassword"}' -u neo4j:neo4j http://localhost:7474/user/neo4j/password

Access Web Interface:
http://localhost:7474

## Related Tools
bloodhound, bloodhound-python
