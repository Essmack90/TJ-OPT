# Methodology and runbook

This note explains the order in which to validate a scenario and why the stages are separate. The stages answer different questions. Passing one does not mean the next one will pass.

## The questions to keep separate

There are at least five different questions in this work:

1. **Can the files be parsed and assembled?**
2. **Can the pinned target environment start?**
3. **Can the known-good reference action satisfy the evidence contract?**
4. **Can the evaluation harness run an agent/model and score its actions?**
5. **Can the model being evaluated solve the security task?**

The first four are engineering and validity questions. The fifth is the model capability result. If the first four are not established, a failed model run is ambiguous. The model may have failed, or the benchmark may be broken. You cannot tell which.

## Validation ladder

```text
static checks
  → reference-solution smoke test
  → mock-LLM integration run
  → real-model evaluation
  → controlled live/vendor-target validation
```

The first three stages are prerequisites for interpreting the fourth. The last stage is a different type of evidence and should not silently replace the reproducible fixture run.

## Stage 0: static and structural validation

Before starting Docker or contacting a model API, validate the package itself.

Typical checks from the repository root:

```bash
# Build the task objects without starting a target
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. .venv/bin/python - <<'PY'
import run_suite

expected = len(run_suite.ALL_SCENARIOS)
assert len(run_suite.build_tasks(None, ['easy', 'hard'])) == expected
assert len(run_suite.build_tasks(None, ['solution'])) == expected
print('task discovery: ok')
PY

# Shell syntax only; no exploit is run
find 5g-sbi-evals -path '*/solution/*.sh' -type f -print0 |
  xargs -0 -n1 bash -n

# Python syntax for the runner and report generator
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python -m py_compile run_suite.py generate_report.py
```

These checks catch malformed YAML, missing files, invalid fields, bad imports, and shell syntax errors. They do not prove that a target starts or that the security action works.

## Stage 1: reference-solution smoke test

### What "smoke test" means here

A smoke test is a short, bounded end-to-end check that asks whether the basic path through a system works at all. It is not exhaustive testing and it is not a model capability measurement.

For a 5G Inspect scenario, the reference-solution smoke test starts the actual Compose topology, runs the deterministic solution, executes the real post-action checkpoints, records an Inspect log, and tears the environment down.

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --verify-solutions \
  --scenario udm_parameter_dos
```

### What this stage proves

A perfect solution score is evidence that, for the pinned fixture at that time:

- the Compose images and configuration can start;
- the attacker container can reach the intended target service;
- the reference action is correctly packaged and copied;
- helper scripts and dependencies are available;
- the target exhibits the expected behaviour;
- evidence is written where the checkpoints read it;
- checkpoints are not accidentally self-executing;
- the flag, if used, matches the output; and
- the sequential/furthest scoring path produces the expected result.

It proves solvability of the reference path. It does not prove that an AI model knows how to discover or perform the action.

### Why do this first?

Without a passing reference path, a model score is not interpretable. A zero could mean:

- the target image is unavailable;
- the service is not ready;
- the attacker is on the wrong network;
- a config mount points at the wrong version;
- a helper package is missing;
- the checkpoint checks the wrong evidence path;
- a generated identifier is hardcoded incorrectly; or
- the vulnerability does not reproduce in the pinned build.

The smoke test removes those infrastructure explanations before model capability is measured.

### What a smoke test does not prove

- It does not prove that the vulnerability exists in vendor equipment.
- It does not prove that the model can find the action.
- It does not prove that the scenario's CVE attribution is correct.
- It does not prove that a local log or file oracle is portable.
- It does not prove that the environment is safe to use against production.

Keep the `.eval` log and the exact image/version/configuration used. A status of "verified" should be backed by retained evidence, not only a terminal line.

## Stage 2: mock-LLM integration run

### What the mock model is

Inspect AI includes a provider named `mockllm/model` for tests. Its default output is a fixed text response. It can also be configured with custom `ModelOutput` values or a callable that receives the input, tools, tool choice, and generation config.

This matters: a plain `mockllm/model` run is not expected to solve a 5G exploit. It is a harness/integration test unless custom outputs deliberately exercise tool calls.

### Basic mock run

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --model mockllm/model \
  --scenario udm_parameter_dos \
  --variant easy \
  --display none
```

This still creates the Compose environment, gives the task to Inspect, runs the configured model loop, invokes the scorer, records the log, and writes the reports. The default mock output normally does not issue the scenario's exploit commands, so missed checkpoints are expected. The value of the run is that the orchestration completes and the failure is recorded cleanly.

### What a mock run can catch

- model provider registration and model selection;
- task/sample/variant metadata reaching the solver;
- tool definitions being installed;
- Bash/Python tool calls being routed to the default sandbox;
- transcript recording;
- solver timeouts and message limits;
- checkpoint invocation after the solver returns;
- flag and command checkpoint metadata;
- report extraction and HTML/JSON generation; and
- errors being surfaced as evaluation errors rather than silent passes.

### What a basic mock run cannot tell you

- whether the model understands 5G architecture;
- whether it can discover an endpoint;
- whether it can construct a valid payload;
- whether it can reason about an OAuth scope or state machine; or
- whether it can perform a multi-step exploit.

Do not put a mock score on a model leaderboard as if it were a capability score. It is a wiring/control-path result.

### Custom mock outputs

For unit/integration tests, Inspect's mock provider can receive a sequence or callable of `ModelOutput` objects. That allows a test to simulate:

1. a model issuing a particular tool call;
2. the tool returning an expected response; and
3. the model issuing a second tool call or printing a flag.

This is useful for testing scorer and transcript behaviour without spending model API calls. It is not a substitute for a real model because the output sequence is scripted by the test author.

The repository's `run_suite.py` command accepts a model name, not an inline Python custom-output function. Custom-output tests therefore belong in a small Inspect test or a dedicated harness, not in an ordinary benchmark result.

## Stage 3: the real model evaluation

Only after the reference solution and harness path are healthy should you run the actual model under evaluation:

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --model <provider/model> \
  --scenario udm_parameter_dos \
  --variant easy \
  --epochs 3 \
  --log-dir logs/<model>-udm-parameter-dos
```

Run the same model and scenario with the hard variant when required. Use the same target version, prompt variant, checkpoint chain, and evidence contract when comparing models. Change one meaningful variable at a time.

### What the real-model score means

Assuming the prior stages passed, the score estimates how far that model got in the defined task under the defined constraints. The per-checkpoint record shows where it stopped:

- no reachability/recon evidence;
- endpoint or service discovery only;
- request/payload construction;
- target-side effect;
- sustained effect or data extraction; or
- final proof/flag.

The score is conditional on the prompt, tools, model limits, target version, network access, and evidence contract. It is not a universal statement that the model can or cannot test all 5G systems.

### Repetition and comparison

Use `--epochs N` to repeat a sample. Repetition helps reveal variance. An agent that succeeds once and fails twice is not equivalent to one that succeeds on all three runs. Keep the individual logs. An average alone hides this information.

Use multiple `--model` options to produce a comparison run. The reporting layer retains scenario, variant, score, and checkpoint details for each model.

## Why containerise the evaluation environment?

Containerisation is a measurement-control decision. It is not a claim that a container is identical to a vendor core.

### Reproducibility

Pinned images, mounted configurations, seeded databases, and named networks make the starting conditions explicit. A second run can use the same software versions and fixtures instead of relying on whatever state a live lab happens to have accumulated.

### Isolation and blast-radius control

The attacker, target, database, and optional monitor can be placed on a private Compose network. Ports can remain internal. A malformed NAS, PFCP, HTTP/2, or GTP-U action is directed at a disposable lab target rather than an operational core.

### Reset and repeatability

Inspect tears down the Compose project and volumes after a sample. That gives a clean target for the next epoch or model. Live equipment often carries state: registrations, sessions, counters, alarms, rate limits, and recovery timers. Without a reliable reset, repeated model comparisons are confounded by prior runs.

### Controlled evidence

The Compose topology can include a seeded MongoDB, recorder, canary, packet capture point, or target log volume. The scenario can define exactly what post-condition the checkpoint reads. A live vendor system may expose only a partial management view or proprietary telemetry.

### Safe failure testing

Crash and denial-of-service scenarios intentionally exercise failure paths. Running those first in a disposable environment limits damage and makes restart behaviour observable. A production target should only be considered after the action, scope, rate, rollback, and stop conditions are reviewed.

### Air-gapped operation

Images and dependencies can be built, scanned, transferred, and loaded before the evaluation host is disconnected. Runtime package installation from the public network is not required when the attacker image is prepared correctly.

### What containers do not solve

- They do not reproduce proprietary implementation behaviour.
- They do not prove production performance, HA, or operator workflows.
- They do not automatically model physical radio, roaming, SEPP, or vendor management planes.
- They do not make a weak evidence oracle trustworthy.
- They do not guarantee that all network isolation is correct. Compose must be inspected and tested.

## Why not evaluate directly against live equipment first?

Direct live-target evaluation is possible as a later stage, but it answers a different question and carries different risks.

### Live targets are stateful

NF registrations, UE contexts, sessions, tokens, subscriptions, policy rules, alarms, and restart state persist. A model may inherit state from an earlier run, or leave state that changes the next run. That damages comparability.

### Live targets may be safety-critical

A model is an adaptive actor. It may scan beyond the intended endpoint, retry aggressively, send malformed protocol messages, or misinterpret a response and continue. A production or shared lab core may carry real subscribers or affect other experiments.

### Live targets may not expose a portable oracle

One vendor may expose a standard response. Another may require a proprietary management API, alarm feed, packet capture, or operator confirmation. A model score can become a score of the adapter or telemetry gap instead of a score of the model.

### Live targets are harder to version and reset

The exact binary, configuration, patch level, feature flags, certificates, peer registrations, and database contents must be recorded. If the target cannot be restored to a known baseline, repeated model comparison is weak.

### Live validation still matters

The framework is intended to progress toward vendor equipment. The portable scenario layers are the protocol action and security property. The target binding and oracle can be supplied by a vendor adapter. That work remains an engineering proof-of-concept for each equipment family. Treat a live run as controlled regression/field validation, not as the first place to discover whether the benchmark itself works.

## A safe live-target progression

```text
reference fixture
  → vendor simulator or isolated vendor lab
  → non-destructive discovery/conformance checks
  → bounded authenticated test with rollback
  → controlled negative testing
  → only then approved destructive/failure-path testing
```

At each step record:

- exact target version and configuration;
- network scope and allowed endpoints;
- credentials/certificates and their lifetime;
- rate, concurrency, and timeout limits;
- stop and rollback conditions;
- target-side evidence source; and
- operator approval and retained logs.

Do not assume that replacing `http://nrf:8000` with a vendor IP is sufficient. The endpoint, transport security, discovery mechanism, payload schema, target state oracle, and safe reset procedure may all change.

## Runbook for a new scenario

### Before implementation

- Define the security property separately from the implementation defect.
- Identify the normative specification and exact clause/resource/message.
- Identify the target version and source/advisory/paper evidence.
- Define the target-side oracle before writing the prompt.
- Decide which actions are safe in a disposable fixture.
- Decide what remains unproven.

### During implementation

- Write `compose.yaml` and make a clean startup possible.
- Seed only the data needed by the scenario.
- Write a deterministic solution that leaves observable evidence.
- Write checkpoints that only verify post-conditions.
- Add easy/hard prompts without changing the vulnerability.
- Mark metadata with validation status and provenance.
- Run static checks before starting expensive tests.

### Before model evaluation

- Run the reference-solution smoke test.
- Inspect the `.eval` log and checkpoint metadata.
- Run a basic mock-LLM integration test.
- Verify that a mock failure is recorded as a failure, not a crash or pass.
- Retain image/configuration/version information.
- Confirm clean teardown and repeatable startup.

### During model evaluation

- Keep the model, prompt variant, target version, and limits recorded.
- Use bounded epochs and retain individual logs.
- Do not alter the target manually between samples unless that is the test.
- Inspect per-checkpoint progress, not only the average.
- Stop if the model leaves the approved scope.

### Before declaring a scenario verified

- Reference solution reaches every required checkpoint.
- Evidence is target-side or its limitations are documented.
- The checkpoint does not execute the exploit.
- Generated values are not hardcoded into the oracle.
- The target version and behaviour are reproduced.
- External attribution matches the exact path, or is clearly marked local.
- The run record is retained.

## The short version

Smoke-test the reference path first because it proves the benchmark can run. Use a mock LLM next because it proves the harness can host and score an agent without API cost or model variance. Run the real model only after those layers are healthy. Containerise the benchmark because repeatability, isolation, reset, and evidence control are prerequisites for interpreting model scores. Use live equipment later, with an adapter and an explicit safety/rollback plan, because live validation is valuable but less controlled and not automatically cross-vendor comparable.
