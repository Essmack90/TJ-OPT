# UpDown

- **OS:** Linux (Ubuntu 20.04.5)
- **Entry vector:** Exposed `/dev/.git` → recovered source → `dev.siteisup.htb` with `Special-Dev: only4dev` → `.phar` upload plus a timestamp race → `phar://` include. Common PHP execution functions were disabled, so `proc_open` provided the command boundary.
- **Foothold:** Reverse shell as `www-data`.
- **Privilege escalation:** SUID `/home/developer/dev/siteisup` launches Python; a preserved `PYTHONPATH` allowed a controlled `requests` import and a shell as `developer`. The developer account had passwordless sudo for `/usr/local/bin/easy_install`; a temporary setup module provided the final root shell.
- **Flags:** User and root flags were submitted on HTB; values intentionally omitted.
- **Cleanup:** Removed target-side temporary artifacts and uploaded PHAR files, stopped local listeners, and ingested the engagement log.
