# Environment setup

This note covers everything needed to go from a clean machine to running your first evaluation. It assumes a Linux host with Docker installed. If you are setting up an air-gapped host, read the air-gap section at the end before starting.

## Prerequisites

You need:

- **Python 3.11+** (the venv currently runs 3.13, but 3.11 is the minimum)
- **Docker Engine 24+** with the Compose V2 plugin (`docker compose`, not the old `docker-compose`)
- **Git** to clone the repository
- At least **8 GB free RAM** for running multiple 5G NF containers in parallel
- At least **20 GB free disk** for Docker images (free5GC, Open5GS, MongoDB, Python, attacker image)

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

Install the local packages in development mode. There is no `requirements.txt`. The two local packages (`inspect_ai` and `inspect_cyber`) are installed from their source trees:

```bash
pip install -e inspect_ai
pip install -e inspect_cyber
pip install pyyaml pymongo
```

Verify the install:

```bash
python -c "from inspect_ai import eval; from inspect_cyber import cyber_task; print('ok')"
```

## Build the attacker image

Every scenario's Compose file references `aisi-5g-attacker:latest`. Build it once:

```bash
docker build -t aisi-5g-attacker:latest 5g-sbi-evals/shared/attacker
```

This image contains curl (with HTTP/2 support), jq, iproute2, pymongo, pycrate (NAS message crafting), pysctp (SCTP sockets), and scapy (packet crafting). No scenario should need to install packages at runtime.

Verify the image has what you need:

```bash
docker run --rm aisi-5g-attacker:latest bash -c \
  'curl --version | head -1; python3 -c "import pymongo, scapy, pycrate; print(\"deps ok\")"'
```

## Pull target images

The scenarios use specific pinned versions of free5GC and Open5GS images. Pull them before your first run so you are not waiting for downloads mid-evaluation:

```bash
# free5GC v3.4.3 (Phase 1/2 scenarios)
for nf in nrf udm udr nssf pcf ausf; do
  docker pull free5gc/${nf}:v3.4.3
done

# free5GC v4.2.3 (Phase 2/3 scenarios)
for nf in nrf udr udm nef amf; do
  docker pull free5gc/${nf}:v4.2.3
done

# free5GC v4.2.1 (NEF notification crash)
docker pull free5gc/nef:v4.2.1

# Open5GS (Phase 3/5 scenarios)
docker pull openverso/open5gs:2.8.0
docker pull openverso/open5gs:2.7.7
docker pull openverso/open5gs:2.7.6

# Supporting
docker pull mongo:4.4
docker pull node:18-slim   # WebUI scenario only
```

Check they are all present:

```bash
docker images | grep -E 'free5gc|open5gs|openverso|mongo|aisi-5g'
```

## Model API keys

Inspect supports many model providers. The model is selected with `--model provider/model-name`. Each provider reads its API key from an environment variable.

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Run with `--model anthropic/claude-sonnet-4-20250514` or whichever model you want to test.

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

Run with `--model openai/gpt-4o` or similar.

### DeepSeek

```bash
export DEEPSEEK_API_KEY="sk-..."
```

Run with `--model deepseek/deepseek-chat`.

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
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --verify-solutions \
  --scenario udm_parameter_dos
```

This runs the deterministic solution script, not a model.

## The PYTHONPATH

Every `run_suite.py` command needs the local source trees on the Python path:

```bash
export PYTHONPATH=inspect_ai/src:inspect_cyber/src:.
```

Set this once in your shell session, or add it to your `.bashrc`/`.zshrc` for convenience. All the commands below assume it is set.

## First run: verify a single scenario

Start with the reference solution for one scenario to confirm everything works:

```bash
.venv/bin/python run_suite.py \
  --verify-solutions \
  --scenario udm_parameter_dos
```

A successful run prints a score of `1.00` and writes `summary.txt`, `summary.json`, and `report.html` to the output directory. If it fails, check:

1. Is the attacker image built? (`docker images | grep aisi-5g`)
2. Are the target images pulled? (`docker images | grep free5gc/udm`)
3. Is Docker running? (`docker info`)
4. Is the PYTHONPATH set?

## First model run

Once the solution verification passes, run a real model:

```bash
.venv/bin/python run_suite.py \
  --model anthropic/claude-sonnet-4-20250514 \
  --scenario udm_parameter_dos \
  --variant easy
```

This starts the Compose topology, gives the model the easy prompt, lets it use Bash/Python tools inside the attacker container, then scores its actions against the checkpoints.

## Running the full suite

Run all release-runnable scenarios:

```bash
.venv/bin/python run_suite.py \
  --model anthropic/claude-sonnet-4-20250514 \
  --variant easy
```

Without `--scenario`, the runner selects all scenarios with `validation_status` of `active` or `verified`. Each scenario gets its own Compose environment, started and torn down independently.

### Filtering

Filter by phase:

```bash
.venv/bin/python run_suite.py --model ... --phase phase1
```

Filter by target core:

```bash
.venv/bin/python run_suite.py --model ... --target-filter free5gc
.venv/bin/python run_suite.py --model ... --target-filter open5gs
```

Include draft/unverified scenarios:

```bash
.venv/bin/python run_suite.py --model ... --include-unverified
```

## Comparing models

Run the same suite against multiple models and compare:

```bash
.venv/bin/python run_suite.py \
  --model anthropic/claude-sonnet-4-20250514 \
  --model deepseek/deepseek-chat \
  --variant easy \
  --epochs 3
```

The report output includes per-scenario, per-model scores and checkpoint progress.

## Inspect trace directory

Inspect writes trace logs to `~/.local/share/inspect_ai/traces/` by default. If that directory is read-only (common in isolated lab sessions), redirect it:

```bash
export XDG_DATA_HOME=/path/to/writable/directory
```

The runner handles this automatically in recent versions, but set it explicitly if you get permission errors on first run.

## Useful environment variables summary

| Variable | Purpose | Required? |
|---|---|---|
| `PYTHONPATH` | Local source trees for inspect_ai and inspect_cyber | Always |
| `ANTHROPIC_API_KEY` | Anthropic/Claude model access | For Anthropic models |
| `OPENAI_API_KEY` | OpenAI model access (or OpenAI-compatible) | For OpenAI models |
| `DEEPSEEK_API_KEY` | DeepSeek model access | For DeepSeek models |
| `OPENAI_BASE_URL` | Custom OpenAI-compatible endpoint | For custom endpoints |
| `ANTHROPIC_BASE_URL` | Air-gapped Anthropic endpoint | For internal deployments |
| `XDG_DATA_HOME` | Override Inspect trace directory | If default is read-only |
| `DOCKER_HOST` | Remote Docker daemon | If not using local Docker |

## Air-gapped setup

On a disconnected host, there is no internet access for pulling images or contacting model APIs. Prepare everything on a connected machine first.

### On the connected machine

1. Build the attacker image and pull all target images (see sections above).
2. Save them to a tar archive:

```bash
docker save \
  aisi-5g-attacker:latest \
  free5gc/nrf:v3.4.3 free5gc/udm:v3.4.3 free5gc/udr:v3.4.3 \
  free5gc/nssf:v3.4.3 free5gc/pcf:v3.4.3 free5gc/ausf:v3.4.3 \
  free5gc/nrf:v4.2.3 free5gc/udr:v4.2.3 free5gc/udm:v4.2.3 \
  free5gc/nef:v4.2.3 free5gc/amf:v4.2.3 \
  free5gc/nef:v4.2.1 \
  openverso/open5gs:2.8.0 openverso/open5gs:2.7.7 openverso/open5gs:2.7.6 \
  mongo:4.4 \
  | gzip > aisi-5g-images.tar.gz
```

3. Record image digests:

```bash
docker images --digests --format '{{.Repository}}:{{.Tag}} {{.Digest}}' \
  | grep -E 'free5gc|open5gs|openverso|mongo|aisi-5g' > image-digests.txt
```

4. Package the repository (including the `.venv`):

```bash
tar czf aisi-assessment.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  aisi-assessment/
```

### Transfer

Move `aisi-5g-images.tar.gz`, `image-digests.txt`, and `aisi-assessment.tar.gz` to the disconnected host via approved media.

### On the air-gapped host

1. Load the images:

```bash
gunzip -c aisi-5g-images.tar.gz | docker load
```

2. Verify digests match:

```bash
docker images --digests --format '{{.Repository}}:{{.Tag}} {{.Digest}}' \
  | grep -E 'free5gc|open5gs|openverso|mongo|aisi-5g'
# Compare with image-digests.txt
```

3. Extract and activate the repository:

```bash
tar xzf aisi-assessment.tar.gz
cd aisi-assessment
source .venv/bin/activate
export PYTHONPATH=inspect_ai/src:inspect_cyber/src:.
```

4. Set up the model endpoint (internal/air-gapped):

```bash
export ANTHROPIC_BASE_URL="https://airgap:443"
export ANTHROPIC_API_KEY="internal-token"
```

5. Run the solution verification first to confirm the environment is healthy:

```bash
.venv/bin/python run_suite.py --verify-solutions
```

6. Then run model evaluations as normal.

### What must not happen on an air-gapped host

- No `apt-get install`, `pip install`, or `npm install` at runtime.
- No `docker pull` at runtime.
- No outbound network connections from evaluation containers.
- All Compose networks should be marked `internal: true` (28 of 29 already are; `sbi_enumeration` uses an external adapter and has an explicit exception documented).

## Related notes

- [[00 - 5G Inspect Cyber - Index]]
- [[04 - 5G Inspect Cyber - execution flow]]
- [[06 - 5G Inspect Cyber - methodology and runbook]]
