# cloud_enum

**What it speeds up:** multi-cloud bucket and service enumeration by keyword. Instead of manually building naming-convention variants and testing each with `curl`, cloud_enum generates permutations automatically and checks all three major CSPs (AWS S3, Azure Blob/File/Web, GCP Storage) in one pass.

**What it doesn't replace:** the manual suffix-extraction step (you still need to find the known bucket name from the target's site first to get the random suffix). And the actual investigation of found buckets (listing contents, downloading files) still uses the AWS CLI.

**Module source:** [[25. Enumerating AWS Cloud Infrastructure#25.2.3 Service-specific Domains|Module 25. 25.2.3]]

---

## Installation

```bash
sudo apt install cloud-enum    # package name: cloud-enum, binary name: cloud_enum (underscore)
```

---

## Usage

```bash
# Single keyword — scan all permutations of this keyword across AWS/Azure/GCP
cloud_enum -k offseclab-assets-public-axevtewi

# Multiple keywords from file — useful for targeting naming conventions directly
cloud_enum -kf /tmp/keyfile.txt

# Quick scan — disable the built-in mutations wordlist (fuzz.txt)
# Use -qs when your keyfile already contains the exact names you want to test
cloud_enum -kf /tmp/keyfile.txt --quickscan       # or -qs

# Scope to one CSP (speeds up the scan significantly)
cloud_enum -kf /tmp/keyfile.txt -qs --disable-azure --disable-gcp    # AWS only
cloud_enum -kf /tmp/keyfile.txt -qs --disable-aws --disable-gcp      # Azure only
```

---

## Output Interpretation

| Output line | Meaning |
|------------|---------|
| `OPEN S3 BUCKET` | Bucket exists and is publicly readable — files listed automatically |
| `Protected S3 Bucket` | Bucket exists but access denied (private) |
| `[not listed]` | Bucket doesn't exist (NoSuchBucket) |

---

## Building the Keyword File

When the target uses a consistent random suffix across all their buckets (common poor practice), extract the suffix from the known public bucket and build a list of naming convention variants:

```bash
# Extract the suffix from a known bucket URL
# e.g. known bucket: offseclab-assets-public-ccchmcgu → suffix is ccchmcgu

# Build a keyfile targeting all gemstone-themed buckets
for gem in ruby amethyst sapphire emerald diamond topaz opal garnet; do
  echo "offseclab-${gem}-ccchmcgu"
done > /tmp/keyfile.txt

cloud_enum -kf /tmp/keyfile.txt -qs --disable-azure --disable-gcp
```

---

## Key Gotchas

- **Tool name vs package name:** the apt package is `cloud-enum` (with a hyphen), but the binary is `cloud_enum` (with an underscore). `cloud-enum` after install gives `command not found`.
- **`--quickscan` / `-qs` disables the built-in fuzz.txt mutations.** Without this flag, cloud_enum appends words from `/usr/lib/cloud-enum/enum_tools/fuzz.txt` to every keyword, useful for discovery but noisy and slow when you already know the exact bucket names.
- **Objects can be accessible even when bucket listing is blocked.** `cloud_enum` finding `Protected S3 Bucket` doesn't mean the objects inside are inaccessible, always try direct object-path access with `aws s3 cp s3://<bucket>/<object> -` after finding a protected bucket.
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

cloud_enum supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

cloud_enum is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
cloud_enum --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
