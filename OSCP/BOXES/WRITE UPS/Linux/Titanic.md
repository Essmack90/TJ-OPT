# Titanic

- **OS:** Linux (Ubuntu; Apache/Werkzeug and Gitea)
- **Entry vector:** HTTP virtual-host discovery exposed `dev.titanic.htb`, a public Gitea instance, and public repositories. The Docker configuration disclosed `/home/developer/gitea/data`; the booking app's `/download?ticket=` path allowed arbitrary file reads, including the Gitea SQLite database.
- **Credential transition:** Extracted the developer PBKDF2-SHA256 record from SQLite, converted it to Hashcat mode 10900, and validated the recovered SSH access.
- **Privilege escalation:** A root-scheduled ImageMagick 7.1.1-35 job processed writable JPGs from `/opt/app/static/assets/images`. CVE-2024-41817 empty-path shared-library loading allowed a temporary `libxcb.so.1` callback and a root shell.
- **Flags:** User and root flags were submitted on HTB; values intentionally omitted.
- **Cleanup:** Removed the temporary shared library and stopped local listeners and cracking processes.
