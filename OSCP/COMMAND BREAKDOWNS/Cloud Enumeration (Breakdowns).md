# Cloud Enumeration — Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Line-by-line teardowns for cloud enumeration commands that aren't self-explanatory. For full syntax see [[Cloud Enumeration]] (Command Appendix). For phase-ordered workflow see [[Cloud Methodology]].

#AWS #Cloud #IAM #CommandBreakdowns

---

## `aws ec2 describe-snapshots` with JMESPath size filter

```bash
aws ec2 describe-snapshots \
  --owner-ids 621533607853 \
  --no-cli-pager \
  --query "Snapshots[?VolumeSize==\`1\`]"
```

| Part | What it does |
|------|-------------|
| `aws ec2 describe-snapshots` | List EBS snapshots |
| `--owner-ids 621533607853` | Filter to snapshots owned by this account — without this you'd get all public AWS snapshots (thousands). `--owner-ids` narrows by account ownership |
| `--no-cli-pager` | Print directly to stdout instead of piping through `less` — avoids having to press `q` to exit the pager on large outputs |
| `--query "Snapshots[?VolumeSize==\`1\`]"` | JMESPath client-side filter: `Snapshots` = the array returned, `[?VolumeSize==\`1\`]` = keep only items where `VolumeSize` equals `1` (the backtick syntax is required to compare against a number literal rather than a string) |

**Why the backtick?** JMESPath uses backtick literals for non-string comparisons. `[?VolumeSize=='1']` would compare to the string `"1"` and never match. `[?VolumeSize==\`1\`]` compares to the integer `1`. The backslash escapes the backtick from the shell before JMESPath receives it.

---

## `jq` IAM dump analysis

```bash
jq '.UserDetailList[] | {user: .UserName, groups: .GroupList, attached: [.AttachedManagedPolicies[].PolicyName], inline: [(.UserPolicyList // [])[].PolicyName]}' /tmp/iam-dump.json
```

| Part | What it does |
|------|-------------|
| `.UserDetailList[]` | Select the `UserDetailList` array and iterate over each element |
| `\| {user: ..., groups: ..., attached: ..., inline: ...}` | Construct a new JSON object for each user with renamed/reshaped fields |
| `.UserName` | Extract the username string |
| `.GroupList` | The group list in this dump is already an array of plain strings (not objects) — reference directly |
| `[.AttachedManagedPolicies[].PolicyName]` | Iterate all attached managed policy objects, extract just their `PolicyName` field, wrap in an array |
| `(.UserPolicyList // [])` | `UserPolicyList` may be absent for some users (jq throws an error if you index a null). The `// []` fallback substitutes an empty array when the key is null or missing |
| `[...][].PolicyName` | Iterate the (possibly empty) UserPolicyList array, extract policy names, wrap in output array |

**What this reveals:** most users will show empty `attached` and `inline` arrays, they only inherit permissions via group. A user with a non-empty `attached` or `inline` has **direct** permissions on top of their group inheritance. That's the thing to investigate for misconfigs or privesc paths.

---

## `aws s3 cp` with stdout destination

```bash
aws s3 cp s3://offseclab-emerald-ccchmcgu/proof.txt - 2>/dev/null || echo "not found"
```

| Part | What it does |
|------|-------------|
| `aws s3 cp` | Copy an S3 object — can copy to/from local filesystem or between buckets |
| `s3://offseclab-emerald-ccchmcgu/proof.txt` | Source: the S3 URI identifying bucket and object key |
| `-` | Destination: a single dash tells the AWS CLI to write to stdout instead of a file — useful for reading short text files inline without creating a temp file |
| `2>/dev/null` | Redirect stderr to /dev/null — hides the `AccessDenied` / `NoSuchKey` error messages that appear for buckets where the object doesn't exist or isn't accessible |
| `\|\| echo "not found"` | If the `aws s3 cp` command exits non-zero (access denied, not found, network error), print `not found` — keeps the loop output clean when scanning many buckets |

---

## `curl -H "Host:"` virtual host bypass

```bash
curl -s http://32.198.34.252 -H "Host: www.offseclab.io" | grep -o 'offseclab-[^/"]*'
```

| Part | What it does |
|------|-------------|
| `curl -s` | Silent mode — suppresses progress meter and error messages (clean output) |
| `http://32.198.34.252` | Target the EC2 IP directly — bypasses DNS (useful when you haven't added the lab DNS to `/etc/resolv.conf`) |
| `-H "Host: www.offseclab.io"` | Inject a `Host` header — the EC2 instance hosts multiple virtual sites; without this header, the server doesn't know which site to serve and may return a blank/default page |
| `\| grep -o 'offseclab-[^/"]*'` | `-o` = print only the matching portion (not the whole line); the pattern `offseclab-[^/"]*` matches any string starting with `offseclab-` and ending before a `/` or `"` — extracts bucket names from S3 URLs embedded in the HTML |

**Why this matters:** when the lab DNS IP changes between sessions, you can still access the site by hitting the EC2 IP directly with a `Host` header instead of adding the nameserver to `/etc/resolv.conf`. Useful for quick one-off requests without changing system DNS config.

---

## `aws configure set aws_session_token`

```bash
aws configure set aws_session_token "<long-token-string>" --profile amethyst
```

| Part | What it does |
|------|-------------|
| `aws configure set` | Directly write a single config value to `~/.aws/credentials` without going through the interactive prompts |
| `aws_session_token` | The credential file key name for temporary session tokens (STS-issued credentials always include a token alongside the key ID and secret) |
| `"<long-token-string>"` | The token itself — must be quoted because it contains `+`, `/`, and `=` characters that the shell would otherwise interpret |
| `--profile amethyst` | Write to the `[amethyst]` section of `~/.aws/credentials` |

**When you need this:** `aws configure` interactive mode now prompts for the session token directly (newer CLI versions). But if you're adding a token to an existing profile, or if the interactive flow confused the order, `set` lets you write the value directly without re-entering everything.
