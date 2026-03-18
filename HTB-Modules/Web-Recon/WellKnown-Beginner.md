---
tags: [module/web-recon, well-known, uris, metadata, configuration, level/beginner]
---

# .well-known URIs - Beginner's Guide

## What is .well-known?

The .well-known directory is a standardized location on web servers (at `/.well-known/`) that stores a website's metadata, configuration files, and information about its services, protocols, and security mechanisms.

Think of it as a "bulletin board" on a website where important notices and configuration details are posted in predictable locations.

---

## Why .well-known Matters for Pentesters

| Why | What You Find |
|-----|---------------|
| Security policies | How to report vulnerabilities |
| Authentication configs | OAuth, OpenID Connect endpoints |
| App associations | Verified app ownership |
| Email security | MTA-STS policies |
| Crypto keys | Public keys for verification |

**The Value:** Standardized locations mean you know exactly where to look.

---

## The .well-known Standard (RFC 8615)

RFC 8615 defines a standard location for metadata:
- Always at `https://domain.com/.well-known/`
- Followed by a specific URI (e.g., `security.txt`)
- IANA maintains a registry of all registered URIs

This consistency is gold for recon - you don't have to guess where things are.

---

## Common .well-known URIs

| URI | Purpose | What It Reveals |
|-----|---------|-----------------|
| `security.txt` | Vulnerability disclosure contact | Who to contact for security issues |
| `openid-configuration` | OpenID Connect metadata | Auth endpoints, keys, supported features |
| `change-password` | Standard password change URL | Where users reset passwords |
| `assetlinks.json` | Digital asset verification | App ownership verification |
| `mta-sts.txt` | Email security policy | MTA Strict Transport Security config |
| `keybase.txt` | Keybase identity verification | Keybase proof |
| `acme-challenge/` | Let's Encrypt verification | Domain validation for SSL |

---

## security.txt - The Most Important One

### What is security.txt?

`security.txt` is a standard for publishing security contact information. It tells researchers how to report vulnerabilities.

### Example security.txt

Contact: mailto:security@example.com
Contact: https://example.com/hackerone
Encryption: https://example.com/pgp-key.txt
Acknowledgements: https://example.com/hall-of-fame
Policy: https://example.com/security-policy
Hiring: https://example.com/jobs

### What It Reveals

| Field | What It Tells You |
|-------|-------------------|
| Contact | Who to report bugs to (email, URL) |
| Encryption | PGP key for encrypted reports |
| Acknowledgements | Hall of fame - past researchers |
| Policy | Security disclosure policy |
| Hiring | They're hiring security people |

### How to Check

curl -s https://target.com/.well-known/security.txt
curl -s https://target.com/security.txt

---

## openid-configuration - Authentication Goldmine

### What is openid-configuration?

This endpoint returns metadata about an OpenID Connect provider (authentication system).

### Example Response

{
  "issuer": "https://example.com",
  "authorization_endpoint": "https://example.com/oauth2/authorize",
  "token_endpoint": "https://example.com/oauth2/token",
  "userinfo_endpoint": "https://example.com/oauth2/userinfo",
  "jwks_uri": "https://example.com/oauth2/jwks",
  "response_types_supported": ["code", "token", "id_token"],
  "subject_types_supported": ["public"],
  "id_token_signing_alg_values_supported": ["RS256"],
  "scopes_supported": ["openid", "profile", "email"]
}

### What It Reveals

| Field | What It Tells You |
|-------|-------------------|
| authorization_endpoint | Where users log in |
| token_endpoint | Where tokens are issued |
| userinfo_endpoint | Where user data is accessed |
| jwks_uri | Public keys (crypto analysis) |
| response_types_supported | What OAuth flows are supported |
| scopes_supported | What data can be requested |

### How to Check

curl -s https://target.com/.well-known/openid-configuration | jq .

---

## Other Useful .well-known Endpoints

### change-password

curl -s https://target.com/.well-known/change-password
Often redirects to the actual password change page.

### assetlinks.json

curl -s https://target.com/.well-known/assetlinks.json
Shows which Android/iOS apps are associated with the domain.

### mta-sts.txt

curl -s https://target.com/.well-known/mta-sts.txt
Shows email security policy (MTA-STS).

### keybase.txt

curl -s https://target.com/.well-known/keybase.txt
Verifies Keybase identity.

---

## How to Brute Force .well-known URIs

### Simple Bash Loop

for uri in security.txt openid-configuration change-password assetlinks.json mta-sts.txt keybase.txt; do
    echo "[*] Checking .well-known/$uri"
    curl -s -o /dev/null -w "%{http_code}" https://target.com/.well-known/$uri
    echo ""
done

### Using ffuf

ffuf -w /usr/share/seclists/Discovery/Web-Content/well-known.txt -u https://target.com/.well-known/FUZZ -fc 404

---

## Key Takeaways

- .well-known is a standardized location for metadata
- Always check security.txt for disclosure policies
- openid-configuration reveals authentication endpoints
- IANA maintains the full registry of URIs
- Many endpoints return JSON - use jq to parse
- Brute force common URIs to find hidden configs
- This is passive recon - no detection risk
- Document all discovered endpoints
- Combine with other recon techniques
- The standardized nature makes it predictable and valuable
