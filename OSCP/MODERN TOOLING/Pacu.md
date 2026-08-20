# Pacu

**What it speeds up:** cross-account IAM role/user enumeration, IAM permission brute-forcing, and AWS session management when juggling multiple credential sets. The manual alternative (IAM trust policy oracle via `put-bucket-policy`) requires creating a bucket and editing JSON policy documents per-attempt. Pacu automates the probe-and-check loop.

**What it doesn't replace:** actual exploitation decisions stay manual. Pacu finds that a role exists and can be assumed; you decide whether to assume it and what to do next.

**Module source:** [[Enumerating AWS Cloud Infrastructure#25.3.4 Enumerating IAM Users in Other Accounts|Module 25. 25.3.4]]

---

## Installation

```bash
pip3 install pacu
# or
sudo apt install pacu
```

---

## Session Setup

```bash
pacu
# → prompted for session name

# Import credentials from AWS CLI profile
import_keys <profile-name>      # from ~/.aws/credentials [<profile-name>]
import_keys --all               # import all profiles at once

# Or enter manually
set_keys

# Verify active keys
whoami

# Switch between loaded key sets
swap_keys
```

---

## IAM Enumeration Modules

### `iam__enum_roles` — Cross-Account Role Existence Oracle

```bash
run iam__enum_roles --account-id <target-account-id> --word-list /tmp/roles.txt
```

**How it works:** for each name in the wordlist, Pacu creates a temporary role in your attacker account and tries to set its trust policy to include `arn:aws:iam::<target>:role/<name>` as a Principal. AWS validates the Principal ARN:
- `MalformedPolicy: Invalid principal` = role does **not** exist in the target account
- No error = role **exists**

If a found role can also be assumed (`sts:AssumeRole`), Pacu dumps the temporary credentials immediately.

**Wordlist tip:** combine known naming patterns (gemstone names, department names, org conventions) × role suffixes (admin, viewer, developer, readonly):
```bash
for prefix in ruby amethyst sapphire; do
  for suffix in lab_admin security_auditor content_creator; do
    echo "${prefix}-${suffix}"
  done
done > /tmp/roles.txt
```

**Cleanup note:** Pacu tries to delete the temp `PacuIamEnumRoles-XXXXX` role it creates. If the attacker account lacks `iam:DeleteRole`, you'll see an `AccessDenied` error at the end, harmless, the role just stays in your attacker account. The enumeration result is still valid.

### `iam__enum_users` — Cross-Account User Existence Oracle

```bash
run iam__enum_users --account-id <target-account-id> --word-list /tmp/users.txt
```

Same oracle mechanism as `iam__enum_roles` but for IAM users.

### `iam__enum_users_roles_policies_groups` — Full IAM Dump (with Creds)

```bash
run iam__enum_users_roles_policies_groups
```

Equivalent to `aws iam get-account-authorization-details`. Requires the active credentials to have IAM read permissions. Stores results in Pacu's SQLite database, query with:

```bash
data IAM       # dump all collected IAM data
services       # list which services have data collected this session
```

### `iam__bruteforce_permissions` — Permission Discovery

```bash
run iam__bruteforce_permissions
```

Tries every available IAM/EC2/S3/etc. action and records which succeed vs. return `AccessDenied`. Very noisy (hundreds of API calls), avoid on stealth engagements. Use `aws iam get-account-authorization-details` instead when the credentials have IAM read access.

---

## Role Assumption

```bash
# Inside Pacu
assume_role arn:aws:iam::<account>:role/<role-name>
# Adds resulting temp credentials to the session database and makes them active

# Or from CLI (after Pacu found the ARN)
aws sts assume-role --role-arn arn:aws:iam::<acct>:role/<name> \
  --role-session-name mysession --profile <attacker>
# Then configure the returned AccessKeyId/SecretAccessKey/SessionToken as a new profile
```

---

## Session Management

```bash
sessions           # list all sessions in the database
swap_session <name>   # switch active session
export_keys        # write active keys to ~/.aws/credentials for use with regular AWS CLI
history            # list previously typed commands
data               # dump all data collected for the current session
```

---

## Key Gotchas

- **Pacu's `aws` shell command uses ~/.aws/credentials** — not the active Pacu keys. Be careful which credentials are in effect when running `aws` commands inside Pacu. Use `export_keys` first, or just exit Pacu and use the CLI normally.
- **Cleanup `AccessDenied` on `DeleteRole`** — expected and harmless if the attacker account lacks `iam:DeleteRole`. The enumeration result is still valid.
- **Session database persists** — `~/.local/share/pacu/sqlite.db` stores all sessions and collected data. Resume an existing session with `swap_session <name>`.
