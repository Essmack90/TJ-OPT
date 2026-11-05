# Execution flow — what calls what

This note traces one evaluation from the shell command to the final report.
The names below are the local implementation names, not pseudocode.

## Start command

From `/home/kali/work/aisi-assessment`:

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --model <provider/model> \
  --scenario udm_parameter_dos \
  --variant easy
```

For a reference solution:

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --verify-solutions --scenario udm_parameter_dos
```

The `PYTHONPATH` makes the local `inspect_ai`, `inspect_cyber`, and project code
importable. `run_suite.py` is the project wrapper; it is the command that
selects scenario directories and calls Inspect's evaluator.

## 1. `run_suite.py` parses the selection

`run_suite.py` imports:

```python
from inspect_ai import eval as inspect_eval
from inspect_cyber import cyber_task
from inspect_cyber import verify_solutions as verify_solution_solver
```

It discovers `*/eval.yaml` beneath `5g-sbi-evals/` and reads
`metadata.validation_status`. By default, only `active` and `verified`
scenarios are selected. `--include-unverified` expands the allowed inventory.

For each selected directory, `build_tasks()` calls:

```python
cyber_task(
    root_dir=str(scenario_dir),
    variant_names=variants,
)
```

Normal runs use `variants = ['easy', 'hard']` unless `--variant` is supplied.
Solution verification uses `variants = ['solution']`, `models = [None]`, and
the `verify_solutions()` solver.

## 2. `cyber_task()` builds an Inspect Task

`cyber_task()` lives in:

```text
inspect_cyber/src/inspect_cyber/task/_task.py
```

It calls `create_agentic_eval_dataset(root_dir)` and filters the resulting
samples by variant or metadata. It then returns an Inspect `Task` containing:

```text
dataset: Samples created from eval.yaml
solver: basic_agent(Python tool + os_shell)
scorer: reached_checkpoints()
```

The task factory does not start Docker at this point. It has only created the
description of what Inspect will later run.

## 3. The dataset factory reads `eval.yaml`

The dataset factory lives in:

```text
inspect_cyber/src/inspect_cyber/dataset/_factory.py
```

It:

1. recursively searches the supplied absolute root for `eval.yaml` or
   `eval.yml` (excluding hidden directories);
2. rejects multiple evaluation files in the same directory;
3. parses YAML with `yaml.safe_load()`;
4. validates the dictionary as the Inspect Cyber `Eval` Pydantic model;
5. resolves relative paths against the directory containing the YAML; and
6. creates one `inspect_ai.dataset.Sample` per variant.

Each `Sample` receives:

```text
id       = "<eval name> (<variant>)"
input    = variant.prompt or eval.prompt
target   = variant.flag or eval.flag or ""
sandbox  = variant.sandbox or eval.sandbox
files    = top-level files merged with variant files
setup    = variant.setup or eval.setup
metadata = eval/variant metadata + checkpoints + scoring strategy
```

The sample is data. It does not execute the prompt, solution, or checkpoint.

## 4. Inspect starts the evaluation

`run_suite.py` calls:

```python
inspect_eval(
    tasks=tasks,
    model=model,
    solver=verify_solution_solver() if verify_solutions else None,
    ...,
)
```

If no solver override is supplied, the solver already attached to the
`cyber_task()` Task is used. Inspect creates the model-generation and sandbox
contexts, then runs each sample/epoch.

## 5. Docker task initialisation

For `sandbox.type: docker`, Inspect selects
`DockerSandboxEnvironment` in Inspect AI.

The task-level initialisation:

- validates Docker prerequisites;
- creates an Inspect-scoped Compose project object;
- reads `docker compose config`;
- builds images when normal build mode is used;
- verifies local images in prebuilt mode; and
- pulls missing remote images where permitted.

This is preparation. The agent is not running yet.

## 6. Per-sample Compose startup

For each sample/epoch, the Docker provider:

1. resolves any Compose environment interpolation;
2. creates a unique project name using task/sample/epoch context;
3. reads the service list;
4. runs Compose `up --detach --wait`; and
5. checks that the expected services are running.

The effective command is equivalent to:

```text
docker compose --project-name <project> \
  -f <scenario>/compose.yaml \
  up --detach --wait --wait-timeout <timeout>
```

The `--wait` behaviour uses Docker healthchecks where present. `depends_on`
controls startup ordering and conditions; it is not a general-purpose
application readiness proof by itself.

The provider maps running Compose services to sandbox environments. It requires
a service named `default`, or one service marked `x-default: true`. That
environment is made the default for tool calls and checkpoints.

## 7. Files and setup are applied

After Compose is running, Inspect's sandbox context:

1. copies every file declared by an `eval.yaml` `files` mapping into its
   destination container;
2. copies the optional setup script into a temporary path in `default`;
3. executes setup in `default`; and
4. removes the temporary setup file.

Compose bind mounts and service environment variables are handled by Docker
when the containers start. The setup script is different: it is a sample-level
script injected and executed by Inspect after startup.

## 8. The solver runs

### Normal model sample

`cyber_task()` uses `basic_agent()` with:

- Inspect's Python tool; and
- `os_shell()` from Inspect Cyber, which adds a Bash tool for Linux samples.

The model receives `Sample.input`, calls Bash/Python tools, observes their
results, and decides whether to continue. A tool call executes inside the
default container through the sandbox provider, effectively using Compose
`exec` with a bounded timeout.

The model can reach target services only through the networks and ports that
Compose grants. Compose service names such as `nrf`, `udm`, `udr`, and `db` are
resolved by Docker's internal DNS.

### Reference solution sample

`--verify-solutions` swaps in `verify_solutions()` from:

```text
inspect_cyber/src/inspect_cyber/solvers/_verify_solutions.py
```

It selects `metadata.solution_location` or `/root`, then executes:

```text
bash /root/solution.sh
```

The solution script's stdout becomes sample output. A non-zero exit records a
solution failure and does not become a successful score.

## 9. Solver stops, then checkpoints start

The checkpoint scorer is not running as a second model loop. It runs after the
solver returns.

`reached_checkpoints()` lives in:

```text
inspect_cyber/src/inspect_cyber/scorers/_reached_checkpoints.py
```

It obtains checkpoints from sample metadata, converts dictionaries into
checkpoint objects, and calls each object's `reached(state)` method.

### Command checkpoint call path

```text
eval.yaml command
  → CommandCheckpoint.reached(state)
  → get_sandbox("default")
  → sandbox.exec(["bash", "-c", command], timeout=...)
  → return code/stdout/stderr
  → CheckpointResult(reached=True/False)
```

The command reaches the default container, not the host. It should be a
read-only verifier of evidence left by the agent or target.

### Sustained checkpoint call path

```text
eval.yaml sustained command
  → SustainedCommandCheckpoint.reached(state)
  → run observer command
  → sleep interval
  → repeat until duration
  → calculate met_ratio
  → compare with threshold
  → CheckpointResult(reached=True/False)
```

This is the continuous/time-series path. The command observes the target; it
must not be the exploit request.

### Flag checkpoint call path

```text
eval.yaml flag
  → FlagCheckpoint.reached(state)
  → inspect model/tool transcript events
  → ignore user prompt content
  → CheckpointResult(reached=True/False)
```

## 10. Checkpoint booleans become a score

With `strategy: sequential`, the scorer counts the contiguous prefix of passed
checkpoints:

```text
[pass, pass, fail, pass] with 4 checkpoints → 2 / 4 = 0.50
```

With `strategy: furthest`, a later pass can show progress even if an earlier
checkpoint failed. The scorer records both the aggregate value and the detailed
per-checkpoint results.

## 11. Monitor services are not hidden callbacks

Two mechanisms are possible:

### Compose monitor service

If `compose.yaml` declares `monitor`, Docker starts it like any other service.
Its own Python loop may poll the target and expose `/status` or `/flag`. It is
only part of the score if a checkpoint queries that endpoint or reads evidence
that it wrote.

### Sustained checkpoint monitor

If `eval.yaml` declares `type: sustained`, the scorer itself performs the
repeated observer calls after the solver stops. In the current `nrf_parser_dos`
definition, the checkpoint directly probes the NRF and there is no separate
monitor service.

The older `cve-2025-55904` demo has a separate `monitor/monitor.py` service. It
uses HTTP/2 prior-knowledge curl, tracks continuous downtime, and releases its
own flag after the configured interval. Compose starts it; `eval.yaml` does not
call it automatically.

## 12. Logs, teardown, and reports

Inspect records a `.eval` log containing the interaction and result data. After
scoring, the Docker provider normally runs:

```text
docker compose --project-name <project> \
  -f <scenario>/compose.yaml down --volumes
```

The wrapper then extracts each sample's score and checkpoint metadata and writes:

- `summary.txt` — compact text result;
- `summary.json` — machine-readable result rows; and
- `report.html` — comparison matrix and per-scenario checkpoint chain.

`generate_report.py` reads scenario metadata for labels and provenance. It does
not execute the target and does not re-run the exploit.

## Full call graph in one view

```text
shell command
  → run_suite.main()
  → build_tasks()
  → cyber_task()
  → create_agentic_eval_dataset()
  → Sample(id, prompt, sandbox, files, checkpoints, metadata)
  → inspect_ai.eval()
  → DockerSandboxEnvironment.task_init()
  → DockerSandboxEnvironment.sample_init()
  → docker compose up --detach --wait
  → copy files / run setup
  → basic_agent() OR verify_solutions()
  → model/tool actions OR bash /root/solution.sh
  → reached_checkpoints()
  → command / sustained / flag checkpoint methods
  → sequential/furthest score
  → .eval log
  → compose down --volumes
  → summary.txt / summary.json / report.html
```

## Failure-layer map

| Failure | Meaning to investigate |
|---|---|
| Scenario not listed | status filtering or directory/YAML discovery |
| YAML validation error | invalid field, missing prompt/sandbox, or malformed checkpoint |
| Compose/image error | Docker, image, path, or target topology problem |
| No default sandbox | missing `default` service or `x-default: true` |
| Agent cannot reach target | network, service DNS, exposed port, or target bind address |
| Setup fails | setup script, copied file, image tool, or timeout problem |
| Solution exits non-zero | reference action failed; inspect script output |
| Command checkpoint fails | evidence missing, malformed, stale, or command non-zero |
| Sustained checkpoint fails | wrong protocol probe, target recovered, or threshold/timing mismatch |
| Flag checkpoint fails | flag not printed in assistant/tool output or spelling differs |
| Partial score | first missed checkpoint under sequential strategy |

