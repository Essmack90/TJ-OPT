---
tags: [Offsec, Skylark, Mixed, Partial, Evidence-backed, Archived]
platform: Offsec
os: Mixed
hostname: Skylark
difficulty: Unrated
status: Archived — stopped at 23/35
aliases: [Skylark]
---

# OffSec: Skylark — stopped at 23/35

## The gist

This is the closure record for the Skylark 35-flag challenge. The run was stopped after the session recorded 23 flags. This page imports only saved evidence, separates historical and fresh target allocations, and labels later genuine evidence as excluded. It does not claim the remaining 12 flags, and a flag value is not treated as proof of a complete boot-to-root chain unless the saved evidence supports that claim.

## Scope and cutoff

- Challenge scope: 35 flags.
- User-approved stopping point: 23/35.
- Canonical cutoff evidence: the saved session status at `2026-10-20T16:07:24Z` says that 23 flags were recorded and names the PREPROD local flag and PBX `.32` proof flag.
- No further challenge execution is part of this import.
- The saved material spans more than one allocation (`192.168.132.x`, `192.168.105.x`, `10.10.105.x`, `10.20.105.x`, and `172.16.105.x`). Values are therefore not silently deduplicated by the final octet.

The webapp record should be read as an evidence archive, not as a newly reconstructed scoreboard. Where the preserved notes disagree about allocation, portal credit, or revalidation, the disagreement is retained below.

## Exact values in the saved Run 1 checkpoint

These 15 values are transcribed from `Platforms/Offsec/Skylark/CHECKPOINT_RUN1.md`. They belong to the earlier `192.168.132.x` allocation and are kept as a historical checkpoint rather than merged with fresh Run 2 values.

| Host | Type | Value |
|---|---|---|
| `.223` | local | `c2ac370808097e19004d9243b93b8599` |
| `.223` | proof | `bfeaecebcd6572c92d866cb87716271a` |
| `.225` | local | `50e4821e966f78f7d342388bacdf25f6` |
| `.225` | proof | `fdcec9db7d3f4ca537f1122b4157f835` |
| `.221` | local | `5e75aeb024db35bf695a3f7b0c82391e` |
| `.221` | proof | `143490126335cad88150797f76f6424f` |
| `.222` | local | `500a7512257496dc02e1b2e63d79222b` |
| `.226` | local | `27823826964ed172d3d66e278a1de0ba` |
| `.226` | proof | `92522d06764a46e1568e8c0c45dfeadd` |
| `.227` | proof | `bf90218d005859a078baa982d44c3f3b` |
| `.14` | local | `abec03a6c1bbc5545c8940c05fb09e4a` |
| `.220` | local | `741d7f4ce6a7582350aede1a2c199fa9` |
| `.220` | proof | `93824e933ec42d3cb615beed4b89de34` |
| `.10` | local | `509dfff1b2e78844a32bc14e92e3ad2c` |
| `.10` | proof | `d5bdbebfb8369ad1e2555ff34fae06c5` |

## Exact values in saved Run 2 evidence

These are direct values present in the current Run 2 evidence directory unless marked `transcript-only`. The `.225` pair is explicitly a fresh revalidation on `192.168.105.225`; it is not silently counted as two new logical slots on top of the historical `.225` pair.

| Host / allocation | Type | Value | Evidence and status |
|---|---|---|---|
| `192.168.105.225` | local | `2221d8f3261e473260eb2999beae323c` | `225-reestablishment-checkpoint.md`, `225-root-flags.txt`; fresh revalidation |
| `192.168.105.225` | proof | `ed3382031d2fed6ab0806c04508fac59` | `225-reestablishment-checkpoint.md`, `225-root-flags.txt`; fresh revalidation |
| `10.10.105.11` / LAB | proof | `8f98eba0aa67fcef3fb0a2b52fe34fa1` | `lab11-full-flag-search-current.txt`; direct WinRM evidence |
| `10.10.105.13` / MAIL | proof | `023bb720ced599c522124fa42f0eabeb` | `mail13-full-flag-search-current2.txt`; direct WinRM evidence |
| `10.20.105.15` / PREPROD | local | `b6868b111a7ca88e1961c5bbc4ffbea5` | `preprod-local-flag-current.txt`; exposed repository path recorded in `preprod-local-targeted-current.txt` |
| `10.20.105.15` / PREPROD | proof | `b6d945bea40daf787debe3db7b2dd8d1` | `preprod-Users_Administrator_Desktop_proof.txt` (UTF-16LE); `preprod-ps-whoami.txt` records SYSTEM context |
| `10.20.105.110` / CLIENT01 | local | `7969ed2e0d90e4cb3265277cde7816b3` | `client01-flags-current.txt`; direct WinRM evidence |
| `10.20.105.110` / CLIENT01 | proof | `eff3c11e615e496d828cfc9290a46b78` | `client01-flags-current.txt`; direct WinRM evidence |
| `172.16.105.32` / PBX | proof | `4d8b8d954b78cd1b1638eee7d77c6fdd` | `pbx-stop-top-current.txt` and `pbx-flag-review-top-current.txt`; callback is `uid=0(root)` and reads `/root/proof.txt` |
| `.223` / current transcript status | local | `fdd8bda2cc9c2d694039b70c64798679` | Claude session transcript at `2026-10-20T13:55:26Z`; no matching raw Run 2 file was found |
| `.223` / current transcript status | proof | `d4e13a33bce5d79173bd8f677b1d5be2` | Claude session transcript at `2026-10-20T14:05:22Z`; no matching raw Run 2 file was found |

The two `.223` rows above are retained as transcript-only evidence, not upgraded to a stronger artifact class. The raw transcript itself is preserved at `/home/kali/.claude/projects/-home-kali-Platforms-Offsec-Skylark/97fa1a01-3f93-46da-96d2-3b0ff04e28f0.jsonl`.

## Chains that are actually documented

### `.223` / MILAN04 — documented Linux chain

The saved Run 1 notes document osCommerce 2.3.4.1 installer abuse associated with CVE-2018-25114, a `www-data` webshell, a statically transferred CVE-2023-0386 overlayfs/FUSE path, and the SUID `/tmp/ds_bash -p` root transition. The historical `.223` local/proof values above are from the exact checkpoint file. The later `.223` values are kept transcript-only because the corresponding raw value files were not found in the current evidence directory.

### `.225` — documented Linux chain and fresh revalidation

The saved notes document `admin:admin` access to the backend on port 8090, a PDF/PHP polyglot upload, a `www-data` shell, the CVE-2023-0386 overlayfs/FUSE path, and SUID `/tmp/ds_bash -p`. The fresh checkpoint confirms the same shape on `192.168.105.225` and records the fresh local/proof pair. The fresh pair is revalidation evidence, not an invented extra challenge slot.

### PREPROD `.15`

The evidence proves Administrator WinRM access, a `local.txt` in the exposed application repository, a proof file, and SYSTEM context in the captured PowerShell output. The complete initial-access and escalation chain is not normalized in the saved material here, so this page does not invent one.

### LAB `.11`, MAIL `.13`, CLIENT01 `.110`, and PBX `.32`

The saved files prove the stated flag paths/values and the captured access context. They are recorded as flag evidence. A full reproducible boot-to-root chain is not asserted for these hosts where the preserved notes do not provide one end to end.

## Excluded later evidence

The later VAX `.31` result is genuine saved evidence but occurred after the 23-flag stopping checkpoint. It is deliberately excluded from the stopped score:

- local: `9cd8dfc4a41a61c9b19ae601711e1647`
- proof: `8a5d32b1b3036c6929b3e593aa4636e9`
- source: `vax-local-flag-4499.txt`, `vax-root-services-4499.txt`, and `vax-finger-multi-4497.txt`
- the session later reported 25 flags at approximately `2026-10-20T20:59Z`

This exclusion is a cutoff decision, not a claim that the values are false.

## Remaining scope

Twelve of the 35 challenge flags are intentionally not represented as found. There are no placeholders, guessed values, or fabricated chains for them. Negative results and unresolved blockers remain in the original Skylark logs and evidence directory for historical reference; this import does not reopen the challenge.

## Evidence index

- Historical checkpoint: `/home/kali/Platforms/Offsec/Skylark/CHECKPOINT_RUN1.md`
- Run 1 worklog: `/home/kali/Platforms/Offsec/Skylark/WORKLOG.md`
- Run 2 evidence root: `/home/kali/Platforms/Offsec/Skylark/evidence/agent-output/20261020T072717Z-codex-skylark-run2-07f7582d/`
- Combined session log: `/home/kali/Platforms/Offsec/Skylark/Skylark.log`
- Transcript used for the 23-flag cutoff and transcript-only `.223` rows: `/home/kali/.claude/projects/-home-kali-Platforms-Offsec-Skylark/97fa1a01-3f93-46da-96d2-3b0ff04e28f0.jsonl`

