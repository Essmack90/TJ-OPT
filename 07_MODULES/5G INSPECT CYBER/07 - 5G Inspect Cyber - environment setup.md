# Environment setup

This note covers everything needed to go from a clean machine to running your first evaluation. It assumes a Linux host with Docker installed. If you are setting up an air-gapped host, read the air-gap section at the end — and `5g-sbi-evals/AIRGAP.md`, which is the canonical build/transfer runbook — before starting.

> **Updated 2026-11-09.** The suite now ships a `requirements.txt`, an `eval.sh` convenience wrapper, digest-pinned images, Docker healthchecks on the free5GC SBI services, and graduated scoring dimensions. The commands below reflect that state.

## Prerequisites

You need:

- **Python 3.13** (the shipped `.venv` is built against the system `python3`, currently 3.13; 3.11 is the language floor if you rebuild from source).
- **Docker Engine 24+** with the Compose V2 plugin (`docker compose`, not the old `docker-compose`).
- **Git** to clone the repository.
- At least **8 GB free RAM** for running multiple 5G NF containers in parallel.
- At least **20 GB free disk** for Docker images (free5GC, Open5GS, MongoDB, Python, attacker image).

Check your versions:

```bash
python3 --version
docker --version
docker compose version
```

## Clone and set up the Python environment

```bash
git clone <repo-url> aisi-assessment
cd aisi-assessment
python3 -m venv .venv
source .venv/bin/activate
```

There is now a **`requirements.txt`** at the repository root. It installs the two local packages as editable source trees plus the two host-side runtime dependencies:

```text
-e ./inspect_ai
-e ./inspect_cyber
PyYAML==6.0.3
openai>=1.0
```

Install it:

```bash
pip install -r requirements.txt
```

`openai` is needed on the host only for OpenAI-compatible providers (OpenAI, DeepSeek, vLLM). `pymongo`, `pycrate`, `pysctp`, and `scapy` are **not** host dependencies — they live inside the attacker image, where checkpoint and solution commands run.

> **Kali/PEP-668 note:** on an externally-managed Python (Kali), a bare `pip install` into the system interpreter is blocked and can appear to no-op. Always install into the `.venv`. The repository `.venv` is the supported environment.

Verify the install:

```bash
python -c "from inspect_ai import eval; from inspect_cyber import cyber_task; print('ok')"
```

> **Import-shadowing gotcha:** the repo root contains a `./inspect_ai` source directory, which shadows the installed package if you run Python *from the repo root*. Run from a subdirectory (the `eval.sh` wrapper does this for you by `cd`-ing into `5g-sbi-evals/`), or rely on the editable install resolving `inspect_ai/src`.

## Build the attacker image

Every scenario's Compose file references the pinned tag `aisi-5g-attacker:2026-11-06`. Build it once:

```bash
docker build -t aisi-5g-attacker:2026-11-06 5g-sbi-evals/shared/attacker
```

This image contains curl (with HTTP/2 support), jq, iproute2, ping, net-tools, procps, SCTP headers/runtime, and pinned `pymongo`, `pycrate` (NAS message crafting), `pysctp` (SCTP sockets), and `scapy` (packet crafting). No scenario installs packages at runtime.

Verify the image has what you need:

```bash
docker run --rm aisi-5g-attacker:2026-11-06 bash -c \
  'curl --version | head -1; python3 -c "import pymongo, scapy, pycrate; print(\"deps ok\")"'
```

The WebUI scenario uses a second suite-owned image, `aisi-open5gs-webui-jwt:v2.7.2`, built offline from vendored source (see `AIRGAP.md`).

## Pull target images

The scenarios use specific pinned versions of free5GC and Open5GS images. The authoritative list with immutable digests is the image manifest in **`5g-sbi-evals/AIRGAP.md`**. Pull them before your first run so you are not waiting for downloads mid-evaluation:

```bash
# free5GC v3.4.3 (free5GC-SBI scenarios)
for nf in nrf udm udr nssf pcf ausf amf; do
  docker pull free5gc/${nf}:v3.4.3
done

# free5GC v4.2.3 (newer SBI + protocol scenarios)
for nf in nrf udr udm nef amf ausf nssf pcf; do
  docker pull free5gc/${nf}:v4.2.3
done

# free5GC point releases used by specific scenarios
docker pull free5gc/nef:v4.2.1
docker pull free5gc/nrf:v4.2.1
docker pull free5gc/udr:v4.2.1

# UERANSim (gNB/UE simulation), pinned by digest
docker pull free5gc/ueransim:latest

# Open5GS targets
docker pull ghcr.io/herlesupreeth/docker_open5gs:master   # Open5GS master (protocol scenarios)
docker pull gradiant/open5gs:2.7.5                         # pinned NRF fixture for sbi_enumeration

# Supporting
docker pull mongo:4.4
docker pull python:3.11-slim   # attacker base image
```

Check they are all present:

```bash
docker images | grep -E 'free5gc|herlesupreeth|open5gs|gradiant|mongo|python|aisi-5g'
```

> The old `openverso/open5gs:2.8.0/2.7.7/2.7.6` images and the `node:18-slim` WebUI base are **no longer used**. Open5GS targets are now the pinned `ghcr.io/herlesupreeth/docker_open5gs:master` and `gradiant/open5gs:2.7.5`; the WebUI image is prebuilt and vendored.

## Model API keys

Inspect supports many model providers. The model is selected with `--model provider/model-name`. Each provider reads its API key from an environment variable.

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Run with `--model anthropic/claude-sonnet-4-20250514` (or whichever model you want to test).

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

Run with `--model openai/gpt-4o` or similar.

### DeepSeek

DeepSeek is OpenAI-compatible and needs the `openai` package (installed by `requirements.txt`):

```bash
export DEEPSEEK_API_KEY="sk-..."
```

Run with `--model deepseek/deepseek-chat` (note the hyphen — `deepseek-chat`, not `deepseek.chat`).

### OpenAI-compatible endpoints (vLLM, OpenCode, custom)

For any OpenAI-compatible API, set the base URL and key:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://your-endpoint/v1"
```

Run with `--model openai/your-model-name`.

### Air-gapped / internal endpoint

For an internal deployment behind a proxy or on an air-gapped network:

```bash
export ANTHROPIC_BASE_URL="https://airgap:443"
export ANTHROPIC_API_KEY="internal-token"
```

The eval files do not change. Only the environment variables change between cloud and air-gapped deployments.

### No model (solution verification only)

For smoke testing reference solutions, no API key is needed:

```bash
./eval.sh --scenario udm_parameter_dos          # wrapper; verifies the reference solution
```

This runs the deterministic solution script, not a model.

## The `eval.sh` wrapper (preferred entry point)

`eval.sh` at the repository root is the supported way to run one scenario or the whole suite. It activates the `.venv`, `cd`s into `5g-sbi-evals/` so the `./inspect_ai` source cannot shadow the installed package, and defaults to deterministic solution verification when no `--model` is given.

```bash
./eval.sh                                  # from INSIDE a scenario dir -> that scenario (verify solution)
./eval.sh -s udm_parameter_dos             # one scenario by name, verify reference solution
./eval.sh -s udm_parameter_dos -m anthropic/claude-sonnet-4-20250514   # agentic run of one scenario
./eval.sh -m anthropic/claude-sonnet-4-20250514                        # whole release suite
./eval.sh --list                           # list available scenario names
```

Everything after the recognised flags is forwarded verbatim to `run_suite.py`.

### Running `run_suite.py` directly

If you bypass the wrapper, set the source trees on the path and run from a directory that is **not** the repo root:

```bash
cd 5g-sbi-evals
PYTHONPATH=../inspect_ai/src:../inspect_cyber/src \
  ../.venv/bin/python ../run_suite.py --verify-solutions --scenario udm_parameter_dos
```

## First run: verify a single scenario

Start with the reference solution for one scenario to confirm everything works:

```bash
./eval.sh --scenario udm_parameter_dos
```

A successful run prints a score of `1.00` and writes `summary.txt`, `summary.json`, and `report.html` to the output directory. If it fails, check:

1. Is the attacker image built? (`docker images | grep aisi-5g`)
2. Are the target images pulled? (`docker images | grep free5gc/udm`)
3. Is Docker running? (`docker info`)
4. Are you using `.venv`? (`eval.sh` enforces this.)

## First model run

Once the solution verification passes, run a real model:

```bash
./eval.sh --scenario udm_parameter_dos --model anthropic/claude-sonnet-4-20250514
```

This starts the Compose topology, gives the model the easy prompt, lets it use Bash/Python tools inside the attacker container, then scores its actions against the checkpoints.

## Running the full suite

Run all release-runnable scenarios against a model:

```bash
./eval.sh --model anthropic/claude-sonnet-4-20250514
```

Without `--scenario`, the runner selects all scenarios with `validation_status` of `active` or `verified`. Four scenarios are deferred and excluded from the default suite (`cross_service_token`, `nef_unprotected_api`, `nf_lateral_movement`, `udr_identifier_validation_bypass`); include them with `--include-unverified`.

### Filtering

```bash
./eval.sh --model ... --phase phase1
./eval.sh --model ... --target-filter free5gc
./eval.sh --model ... --target-filter open5gs
./eval.sh --model ... --include-unverified
```

## Comparing models

Run the same suite against multiple models and compare:

```bash
./eval.sh \
  --model anthropic/claude-sonnet-4-20250514 \
  --model deepseek/deepseek-chat \
  --variant easy \
  --epochs 3
```

The report output includes per-scenario, per-model scores and checkpoint progress, including the graduated scoring dimensions (quality / impact / efficiency / persistence) described in [[01 - 5G Inspect Cyber - eval.yaml]].

## Readiness (healthchecks)

The free5GC SBI services (and the `udm_parameter_dos` topology) now carry Docker healthchecks (`nc -z 127.0.0.1 8000`) with `depends_on: condition: service_healthy`, so the attacker container does not start until the targets are listening. Protocol-level scenarios (AMF/UPF/MME/GTP/PFCP, `sbi_enumeration`, `rogue_nf_registration`) keep readiness-waits inside their solution scripts instead. See [[02 - 5G Inspect Cyber - compose.yaml]].

## Inspect trace directory

Inspect writes trace logs to `~/.local/share/inspect_ai/traces/` by default. If that directory is read-only (common in isolated lab sessions), redirect it:

```bash
export XDG_DATA_HOME=/path/to/writable/directory
```

## Useful environment variables summary

| Variable | Purpose | Required? |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic/Claude model access | For Anthropic models |
| `OPENAI_API_KEY` | OpenAI model access (or OpenAI-compatible) | For OpenAI models |
| `DEEPSEEK_API_KEY` | DeepSeek model access | For DeepSeek models |
| `OPENAI_BASE_URL` | Custom OpenAI-compatible endpoint | For custom endpoints |
| `ANTHROPIC_BASE_URL` | Air-gapped Anthropic endpoint | For internal deployments |
| `XDG_DATA_HOME` | Override Inspect trace directory | If default is read-only |
| `DOCKER_HOST` | Remote Docker daemon | If not using local Docker |

`PYTHONPATH` is handled by `eval.sh`; set it manually only when invoking `run_suite.py` directly.

## Air-gapped setup

On a disconnected host there is no internet access for pulling images or contacting model APIs. **`5g-sbi-evals/AIRGAP.md` is the canonical build/pin/scan/transfer/load runbook** — follow it. The summary below is the shape of that process.

### On the connected machine

1. Build the two suite-owned images (`aisi-5g-attacker:2026-11-06`, `aisi-open5gs-webui-jwt:v2.7.2`) and pull every registry image by digest from the `AIRGAP.md` manifest.
2. Save them to tar archives and record SHA-256 sums:

```bash
docker save \
  aisi-5g-attacker:2026-11-06 aisi-open5gs-webui-jwt:v2.7.2 \
  free5gc/nrf:v3.4.3 free5gc/udm:v3.4.3 free5gc/udr:v3.4.3 \
  free5gc/nssf:v3.4.3 free5gc/pcf:v3.4.3 free5gc/ausf:v3.4.3 free5gc/amf:v3.4.3 \
  free5gc/nrf:v4.2.3 free5gc/udr:v4.2.3 free5gc/udm:v4.2.3 \
  free5gc/nef:v4.2.3 free5gc/amf:v4.2.3 free5gc/ausf:v4.2.3 \
  free5gc/nssf:v4.2.3 free5gc/pcf:v4.2.3 \
  free5gc/nef:v4.2.1 free5gc/nrf:v4.2.1 free5gc/udr:v4.2.1 \
  free5gc/ueransim:latest \
  ghcr.io/herlesupreeth/docker_open5gs:master gradiant/open5gs:2.7.5 \
  mongo:4.4 python:3.11-slim \
  | gzip > aisi-5g-images.tar.gz
sha256sum aisi-5g-images.tar.gz > aisi-5g-images.tar.gz.sha256
```

3. Package the repository (including the `.venv` and `requirements.txt`):

```bash
tar czf aisi-assessment.tar.gz --exclude='.git' --exclude='__pycache__' aisi-assessment/
```

### Transfer

Move the image tar, its SHA-256 manifest, the scan reports, and the repository checkout to the disconnected host via approved media.

### On the air-gapped host

```bash
sha256sum -c aisi-5g-images.tar.gz.sha256
gunzip -c aisi-5g-images.tar.gz | docker load
docker images | grep -E 'free5gc|herlesupreeth|open5gs|gradiant|mongo|python|aisi-5g'

tar xzf aisi-assessment.tar.gz
cd aisi-assessment
source .venv/bin/activate     # prebuilt venv; or: pip install -r requirements.txt

export ANTHROPIC_BASE_URL="https://airgap:443"
export ANTHROPIC_API_KEY="internal-token"

./eval.sh --verify-solutions   # confirm the environment is healthy first
```

### What must not happen on an air-gapped host

- No `apt-get install`, `pip install` from PyPI, or `npm install` at runtime.
- No `docker pull` at runtime.
- No outbound network connections from evaluation containers.
- All Compose networks are `internal: true` (all 36/36 network declarations across the 30 Compose files; `sbi_enumeration` is now self-contained with its own NRF and flag-server fixtures).

## Related notes

- [[00 - 5G Inspect Cyber - Index]]
- [[01 - 5G Inspect Cyber - eval.yaml]]
- [[02 - 5G Inspect Cyber - compose.yaml]]
- [[04 - 5G Inspect Cyber - execution flow]]
- [[06 - 5G Inspect Cyber - methodology and runbook]]
