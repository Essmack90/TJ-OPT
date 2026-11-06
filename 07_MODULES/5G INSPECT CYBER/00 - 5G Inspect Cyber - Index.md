# 5G Inspect Cyber — authoring and execution reference

These notes document how the AISI Inspect Cyber scenario format works, based on the 5G SBI evaluation work in `/home/kali/work/aisi-assessment/5g-sbi-evals/`.

The purpose is to explain what each file does, how they fit together, what the runner actually calls, and where evidence comes from. Everything here is from the local implementation and the checked-in scenario files. None of it claims that every vendor core behaves like free5GC or Open5GS.

## Start here

- [[01 - 5G Inspect Cyber - eval.yaml]] — how to read and write the evaluation definition.
- [[02 - 5G Inspect Cyber - compose.yaml]] — how the attacker sandbox and target environment are created.
- [[03 - 5G Inspect Cyber - solution scripts]] — how reference solutions prove solvability without becoming the grader.
- [[04 - 5G Inspect Cyber - execution flow]] — the call graph from command line to Compose, model, checkpoints, scoring, and reports.
- [[05 - 5G Inspect Cyber - external references]] — official Inspect, 3GPP/ETSI, research, and project links with their role and caveats.
- [[06 - 5G Inspect Cyber - methodology and runbook]] — why validation goes through static checks, smoke tests, mock LLM runs, real-model runs, and controlled live-target work.
- [[07 - 5G Inspect Cyber - environment setup]] — prerequisites, Python venv, Docker images, model API keys, first run, air-gapped deployment.

## What this framework is

Inspect Cyber is an evaluation layer for AISI Inspect. It is a controlled experiment harness. It is not a vulnerability scanner and it is not a replacement for a human penetration tester.

One run gives an agent:

1. a prompt describing a security task;
2. tools (Bash and Python);
3. an isolated sandbox with a target topology; and
4. a known evidence contract that gets checked after the agent stops.

The result is not just a score. Inspect records the model messages, tool calls, tool output, sandbox events, checkpoint results, and final score in a structured `.eval` log. That makes the result auditable. You can ask both "did it pass?" and "what did it actually do?"

## Order of confidence

Do not jump from "the YAML parses" straight to "the model failed". Follow this ladder:

```text
static validation
  → reference-solution smoke test
  → mock-LLM harness test
  → real-model capability run
  → controlled live/vendor-target validation
```

Each step answers a different question. [[06 - 5G Inspect Cyber - methodology and runbook]] explains the rationale and acceptance criteria for each stage.

## The scenario contract

Each runnable scenario is a directory containing:

```text
scenario_slug/
├── eval.yaml
├── compose.yaml
└── solution/
    ├── solution.sh
    └── helper.py              # optional
```

The files have separate responsibilities:

| File | Responsibility | Does it execute the model attack? |
|---|---|---|
| `eval.yaml` | prompt, variants, sandbox reference, checkpoints, scoring, metadata | No. It is declarative configuration |
| `compose.yaml` | containers, images, networks, mounts, environment, readiness | It starts services, but it is not the agent |
| `solution/` | deterministic reference action used by the solution variant | Yes, only when explicitly running solution verification |

The important boundary is between action and verification. The model or reference solution performs the request or protocol action. The checkpoints run afterwards and verify evidence. If a checkpoint performed the exploit, that would give the model progress for free and the capability result would be meaningless.

## The supported command

Run commands from `/home/kali/work/aisi-assessment`:

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --model <provider/model> \
  --scenario <scenario_slug> \
  --variant easy
```

Run the hard variant with `--variant hard`. Run the deterministic reference solution with:

```bash
PYTHONPATH=inspect_ai/src:inspect_cyber/src:. \
  .venv/bin/python run_suite.py \
  --verify-solutions \
  --scenario <scenario_slug>
```

The repository wrapper is the normal entry point. It imports Inspect's `eval()` function, constructs Inspect tasks through `inspect_cyber.cyber_task`, and passes those tasks to Inspect. Docker and the model do not independently interpret `eval.yaml`.

## High-level call graph

```text
run_suite.py
  └─ build_tasks()
       └─ cyber_task(root_dir, variant_names)
            ├─ create_agentic_eval_dataset()
            │    ├─ find eval.yaml
            │    ├─ validate YAML
            │    └─ make one Inspect Sample per variant
            ├─ basic_agent()
            │    ├─ Python tool
            │    └─ Bash tool from os_shell()
            └─ reached_checkpoints()

  └─ inspect_ai.eval(tasks=...)
       ├─ prepare images and Compose project
       ├─ compose up for each sample/epoch
       ├─ copy files and run setup
       ├─ run model solver or solution solver
       ├─ run checkpoints after the solver stops
       ├─ record .eval log
       └─ tear down Compose

  └─ extract scores
       ├─ summary.txt
       ├─ summary.json
       └─ report.html
```

For the detailed sequence and failure boundaries, see [[04 - 5G Inspect Cyber - execution flow]].

## What "5G agnostic" means here

The reference fixtures use free5GC and Open5GS, but the portable design unit is not a MongoDB collection, a container IP, or a Go panic string. A portable scenario separates:

1. the **protocol action** described in 3GPP terms;
2. the **target binding**, which is the host, port, TLS, HTTP/2 mode, credentials, and discovery details;
3. the **oracle** that proves what happened; and
4. the **security property**, which is authorisation, confidentiality, integrity, state-machine validity, isolation, or bounded resource use.

The target binding and oracle may need a vendor adapter. Do not silently compare a vendor run with a reference-core run if the evidence contract is different.

This is the whole point of building an extensive scenario bank. A CVE that is patched on one core may still be wide open on another. The scenario stays valuable either way, because a clean pass against one target is data about that target, not a reason to drop the scenario.

## Evidence discipline

Prefer evidence in this order:

1. standardised wire response or target state transition;
2. standardised peer-visible behaviour;
3. packet capture or audit event;
4. vendor API, database, or log adapter.

Files written inside the attacker container are convenient but forgeable. If a scenario uses an evidence file, document that limitation and, where possible, cross-check the record against target-side state.

## Validation status is part of the result

Scenario metadata distinguishes release-runnable work from unverified work. The local suite treats `active` and `verified` as release-runnable by default. Other statuses require explicit opt-in. A scenario name, a CVE-looking label, or a successful HTTP response is not enough to call a vulnerability verified.

Keep these categories separate:

- pinned CVE reproduction;
- standards conformance probe;
- vendor-specific implementation observation; and
- research hypothesis awaiting reproduction.

## Do not infer more than the files prove

- An `eval.yaml` prompt is an instruction to the agent, not an implementation of the attack.
- A Compose `depends_on` relationship is not automatically a service health guarantee unless conditions and healthchecks make it one.
- A flag proves that the flag was observed. It does not independently prove target-side impact.
- A reference solution proves the environment and evidence contract are solvable. It does not establish that a model can solve the task.
- A local Open5GS or free5GC behaviour is not automatically a 3GPP requirement.
