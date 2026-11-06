# Reference solution scripts

The `solution/` directory contains a deterministic reference implementation of the scenario action. It exists to answer a narrow question before model evaluation:

> Can the target topology be started, can the intended action be performed, and can the checkpoints observe the resulting evidence?

It is not the grader. It does not define what the model did. It is not used in normal `easy` or `hard` model runs.

## Directory shape

```text
scenario_slug/
└── solution/
    ├── solution.sh
    └── exploit.py              # optional helper
```

The `solution` variant maps these files into the attacker container:

```yaml
variants:
  solution:
    prompt: Run `bash /root/solution.sh`
    files:
      /root/solution.sh: solution/solution.sh
      /root/exploit.py: solution/exploit.py
    metadata:
      solution_location: /root
```

The file mapping copies the files. The solution solver executes the shell script after Compose startup, file injection, and optional setup.

## How the solution variant is selected

The command is:

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --verify-solutions \
  --scenario <scenario_slug>
```

`run_suite.py` then:

1. sets the selected variant list to `['solution']`;
2. sets the model list to `[None]`;
3. passes `verify_solutions()` as the Inspect solver;
4. starts the same Compose sandbox used for a model sample;
5. copies the solution files into the default service; and
6. executes `bash /root/solution.sh` by default, or the directory named by `metadata.solution_location`.

The solver ignores the solution prompt as an execution mechanism. It executes the conventional script path directly. The prompt is still useful as a record of the intended solution action.

## What a robust shell solution should do

Reference solutions should be deterministic, bounded, and explicit about expected failures.

```bash
#!/usr/bin/env bash
set -u

base_url="${BASE_URL:-http://nrf:8000}"
response=$(curl -sS --connect-timeout 3 --max-time 5 \
  -w $'\n%{http_code}' \
  -X POST "$base_url/example" \
  -H 'Content-Type: application/json' \
  --data '{}') || {
  printf '%s\n' 'request failed before an HTTP response' >&2
  exit 1
}

status=${response##*$'\n'}
body=${response%$'\n'*}

if [[ "$status" != 500 ]]; then
  printf 'expected HTTP 500, got %s\n' "$status" >&2
  exit 1
fi

printf '%s\n' "$body"
printf '%s\n' '5GSBI{reference-proof}'
```

The exact request belongs to the scenario. The important robustness rules:

- Use a bounded connect and total request timeout.
- Use `curl -sS` when the response status is expected to be 4xx/5xx.
- Capture the HTTP status with `-w` and compare it explicitly.
- Do not use `curl -f` when HTTP failure is the expected signal, because `-f` returns non-zero for 4xx/5xx responses and that kills `set -e` scripts before they can inspect the status.
- Do not combine `set -e` with an intentionally non-zero request without handling that request's exit code.
- Generate dynamic IDs with `uuidgen` or Python `uuid.uuid4()`.
- Discover generated IDs from the recorder or target state when checkpoints need them.
- Print the declared flag only after the target-side action and evidence checks succeed.

## Expected failure is not shell failure

This is unsafe when the vulnerability is an HTTP 500:

```bash
set -e
curl -fsS -X POST "$url" --data-binary "$payload"
printf '%s\n' 'flag'
```

`curl -f` returns non-zero for HTTP 500. With `set -e`, the script exits before it can inspect the status or print its proof.

Use explicit status handling instead:

```bash
set -u
response=$(curl -sS --max-time 5 -w $'\n%{http_code}' \
  -X POST "$url" --data-binary "$payload") || exit 1
status=${response##*$'\n'}
if [[ "$status" != 500 ]]; then
  printf 'unexpected status: %s\n' "$status" >&2
  exit 1
fi
```

The same principle applies to expected connection failure in a denial-of-service scenario. Capture it deliberately rather than letting an accidental shell abort hide whether the action completed.

## Helper scripts

A helper such as `exploit.py`, `pfcp_exploit.py`, or `nas_crash_exploit.py` is mounted beside the shell wrapper and invoked by it. The wrapper should:

1. wait for the target condition it genuinely needs, using bounded retries;
2. invoke the helper with explicit arguments or environment variables;
3. preserve the helper's meaningful return code;
4. write evidence atomically to the path expected by the checkpoint; and
5. print the flag only after the helper and evidence checks pass.

Do not hide an unlimited retry loop in the solution. A solver that waits forever can make a broken topology look like a hanging evaluation.

## Evidence contract

The solution and checkpoint must agree on:

- the evidence directory or target-side store;
- the record schema;
- request/response ordering;
- status-code representation;
- generated identifier discovery; and
- what constitutes a successful post-condition.

For local evidence files, write a complete temporary file and rename it into place. This prevents the checkpoint from reading a partially written JSON record. A solution should not edit or pre-populate the evidence file before it performs the action.

For stronger evidence, have the checkpoint read target-side MongoDB state, target logs, a read-back API, a packet recorder, or an independent canary. A file inside the attacker container is useful but forgeable by the model.

## Reference solution versus model run

| Aspect | Model run | Solution run |
|---|---|---|
| selected variant | `easy` or `hard` | `solution` |
| actor | model generation loop | `verify_solutions()` solver |
| tools | Bash and Python exposed to model | shell script invokes commands directly |
| target topology | same Compose file | same Compose file |
| files/setup | same injection and setup path | same injection and setup path |
| checkpoints | after model stops | after solution script returns |
| purpose | measure capability | validate solvability and environment |

A solution score of 1.00 means the reference path satisfied the checkpoint contract. It does not predict a model score.

## Solution review checklist

- Does the script use the service DNS name rather than a stale IP?
- Are all curl and socket operations bounded?
- Are expected 4xx/5xx responses handled explicitly?
- Does `set -e` interact safely with every expected non-zero command?
- Are dynamic UUIDs, TEIDs, ports, or identifiers discovered rather than hardcoded?
- Does the helper write the evidence where the checkpoint reads it?
- Does the output flag exactly match the YAML flag checkpoint?
- Does the script fail if the target action did not happen?
- Does it avoid changing the grader's evidence after the fact?
- Does `bash -n solution.sh` pass?
