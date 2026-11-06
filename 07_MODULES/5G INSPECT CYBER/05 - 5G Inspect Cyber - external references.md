# External reference sheet

This is a source map for the 5G Inspect Cyber work. It records what each source is useful for and what it does not prove. A link in this sheet is not automatically an attribution for a scenario.

Use the source hierarchy below when reviewing a claim:

1. primary standard or protocol specification for normative behaviour;
2. upstream source, advisory, issue, or commit for implementation behaviour;
3. peer-reviewed or preprint research for a reported technique or finding;
4. local reproduction and retained evidence for the exact target/version claim.

The local evidence review remains the authority for whether a scenario is marked `active`, `verified`, `needs-revalidation`, or another status.

## Inspect and Inspect Cyber

| Source | Role | What it supports | Caveat |
|---|---|---|---|
| [Inspect Cyber documentation](https://inspect.cyber.aisi.org.uk/) | Official project documentation | YAML-driven agentic cyber evaluations and dataset conversion | Documentation describes the framework. Local runner changes must still be checked in this repository |
| [Evaluation configuration](https://inspect.cyber.aisi.org.uk/evaluation-configuration.html) | Official configuration reference | `eval.yaml` plus a sandbox configuration, evaluation fields and sandbox path | The local project adds its own `run_suite.py`, metadata, and checkpoint conventions |
| [Project structure](https://inspect.cyber.aisi.org.uk/project-structure.html) | Official dataset discovery reference | Recursive discovery of `eval.yaml`/`eval.yml`, one file per directory | The local wrapper supplies one scenario directory at a time |
| [Dataset processing](https://inspect.cyber.aisi.org.uk/dataset-processing.html) | Official dataset reference | Sample creation and metadata filtering concepts | Local `cyber_task()` supplies the task and variants |
| [Configuration validation](https://inspect.cyber.aisi.org.uk/configuration-validation.html) | Official validation reference | Solution variants and `verify_solutions()` workflow | The local solution paths and scripts are scenario-specific |
| [Inspect Cyber source](https://github.com/UKGovernmentBEIS/inspect_cyber) | Upstream source | Actual package implementation and release history | The local checkout may contain project-specific changes |
| [Inspect AI source](https://github.com/UKGovernmentBEIS/inspect_ai) | Upstream source | Inspect evaluator, sandbox, logging, and task machinery | Version-pinning matters. Do not assume current upstream behaviour matches an older checkout |

### Local implementation files

These are not external sources, but they are the most direct references for what this repository actually does:

| File | Role |
|---|---|
| `run_suite.py` | Scenario discovery, task construction, model/solution selection, result and report writing |
| `inspect_cyber/src/inspect_cyber/dataset/_factory.py` | YAML discovery, validation, path resolution, and Sample creation |
| `inspect_cyber/src/inspect_cyber/task/_task.py` | `cyber_task()` task factory and default solver/scorer wiring |
| `inspect_cyber/src/inspect_cyber/solvers/_verify_solutions.py` | Reference solution execution |
| `inspect_cyber/src/inspect_cyber/scorers/_reached_checkpoints.py` | Checkpoint execution and aggregate scoring |
| `inspect_cyber/src/inspect_cyber/model/_model.py` | YAML model and checkpoint types |
| `inspect_ai/src/inspect_ai/model/_providers/mockllm.py` | Deterministic mock provider used for harness/integration tests, with default output and custom output hooks |
| `generate_report.py` | JSON/HTML report structure and metadata display |
| `5g-sbi-evals/SCENARIO_AUTHORING.md` | Local authoring rules and validation checklist |
| `5g-sbi-evals/EVIDENCE_REVIEW.md` | Local provenance and attribution review |

## 3GPP and ETSI specifications

The exact release used by a scenario matters. A specification link establishes the API or security property. It does not prove that a particular implementation violates it.

| Specification | Official link | Relevant use |
|---|---|---|
| 3GPP TS 29.500, 5G System Common Services | [ETSI TS 129 500](https://www.etsi.org/deliver/etsi_ts/129500_129599/129500/15.07.00_60/ts_129500v150700p.pdf) | Common SBI conventions, HTTP/2, common service behaviour |
| 3GPP TS 29.510, Network Function Repository Services | [ETSI TS 129 510](https://www.etsi.org/deliver/etsi_ts/129500_129599/129510/16.13.00_60/ts_129510v161300p.pdf) | `Nnrf_NFManagement`, NF registration, discovery, NF profiles |
| 3GPP TS 33.501, Security Architecture and Procedures | [3GPP specification page](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3169) | 5G security architecture, NF authentication and authorisation model |
| 3GPP TS 29.504, Unified Data Repository Services | [ETSI TS 129 504](https://www.etsi.org/deliver/etsi_ts/129500_129599/129504/18.09.00_60/ts_129504v180900p.pdf) | `Nudr_DR` data repository resources |
| 3GPP TS 29.505, Unified Data Management Services | [ETSI TS 129 505](https://www.etsi.org/deliver/etsi_ts/129500_129599/129505/17.09.00_60/ts_129505v170900p.pdf) | `Nudm_SDM` subscription and authentication data APIs |
| 3GPP TS 29.519, Network Exposure Function Services | [3GPP specification page](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3339) | NEF traffic influence and PFD management APIs |
| 3GPP TS 29.244, Session Management Protocol | [ETSI TS 129 244](https://www.etsi.org/deliver/etsi_ts/129200_129299/129244/18.09.00_60/ts_129244v180900p.pdf) | PFCP association, session, PDR, FAR, and UPF procedures |
| 3GPP TS 24.501, NAS protocol for 5GS | [3GPP specification page](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3370) | NAS registration, deregistration, integrity, and state handling |

### How to use a specification correctly

For a scenario, record:

- the exact specification and release consulted;
- the clause, resource, or message relevant to the expected property;
- the implementation version tested;
- the observed request, response, state, or packet; and
- whether the result is a conformance finding, security issue, local observation, or research hypothesis.

Do not turn "the standard says X" into "the product is vulnerable" without an implementation observation and retained evidence.

## Research papers and technical analysis

| Source | Role | Relevant scenarios or design work | Caveat |
|---|---|---|---|
| [FivGeeFuzz, Cross-Service Token: Finding Attacks in 5G Core Networks](https://arxiv.org/abs/2509.08992) | Research paper | 5G SBI grammar-based fuzzing, malformed inputs, cross-service token findings, free5GC validation | Paper findings and tested versions must not be silently expanded to untested versions |
| [TU Berlin, Uncovering hidden paths in 5G core](https://depositonce.tu-berlin.de/items/5e04f979-a8a7-4480-830e-554475a36d24) | Research repository/paper record | GTP-U/user-plane boundary bridging and hidden paths | A local exploit still needs target-side reproduction and correct PFCP/GTP evidence |
| [Trend Micro, Attacks on 5G infrastructure from users' devices](https://www.trendmicro.com/en_us/research/23/i/attacks-on-5g-infrastructure-from-users-devices.html) | Technical research | User-plane and UPF/GTP attack context | Vendor research is context, not a substitute for the target's exact behaviour |
| [5Greplay](https://arxiv.org/abs/2304.05719) | Research paper | 5G protocol replay/fuzzing methodology | Methodology does not validate a particular scenario's exploitability |
| [Drishti](https://arxiv.org/abs/2608.30112) | Research paper | AI-led 5G core auditing and protocol robustness context | Keep any overlap with another disclosure explicitly labelled until confirmed |

## Vulnerability and upstream implementation sources

These links are included because they occur in the local scenario catalogue or evidence review. Their applicability is scenario-specific.

| Source | Local use | Status discipline |
|---|---|---|
| [Open5GS CVE-2025-55904 on NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-55904) | Multipart parser NULL dereference scenario context | Match affected release, endpoint, content type, and evidence before calling a scenario a reproduction |
| [Open5GS issue #3942](https://github.com/open5gs/open5gs/issues/3942) | Upstream discussion for multipart parser behaviour | Issue discussion is not itself a complete reproduction record |
| [free5GC issue #736](https://github.com/free5gc/free5gc/issues/736) | OAuth/scope implementation context | Confirm the exact code path and target version locally |
| [free5GC issue #1193](https://github.com/free5gc/free5gc/issues/1193) | NAS deregistration handling context | Local scenario metadata records the end-to-end verification status |
| [Open5GS issue #4766](https://github.com/open5gs/open5gs/issues/4766) | Related PFCP error-path reference | It is explicitly not the same as every PFCP session-hijack claim |
| [Open5GS commit for CVE-2025-63288](https://github.com/open5gs/open5gs/commit/be765fe) | AMF NGSetup crash patch context | Check the commit against the affected code/version |
| [Open5GS commit for CVE-2026-91855](https://github.com/open5gs/open5gs/commit/028e1dbb) | UPF PFCP crash/resource-exhaustion context | Do not merge distinct attack angles without separate evidence |
| [free5GC GHSA/CVE-2026-44319](https://github.com/free5gc/free5gc/security/advisories/GHSA-rxrq-fv76-26pr) | NEF notification crash reference | Check advisory scope and affected versions before release claims |
| [free5GC GHSA/CVE-2026-42459](https://github.com/free5gc/free5gc/security/advisories/GHSA-585v-hcgf-jhfr) | UDM SUPI-validation scenarios | Match the exact handler and response path |
| [free5GC GHSA/CVE-2026-33063](https://github.com/free5gc/free5gc/security/advisories/GHSA-4jrw-92fg-4jwx) | AUSF SUCI panic reference | Local reproduction remains required |
| [free5GC GHSA/CVE-2026-33064](https://github.com/free5gc/free5gc/security/advisories/GHSA-7g27-v5wj-jr75) | UDM data-change panic reference | Match message shape and handler |
| [Open5GS PR #4279](https://github.com/open5gs/open5gs/pull/4279) | WebUI JWT secret context | A pull request is implementation evidence, not a general 5G security rule |

### Unresolved or local-only references

The local README explicitly marks some claims as local observations, related references, or pending attribution review. In particular, do not present a nearby CVE as the exact source when the API path, version, or behaviour differs. Review:

- `5g-sbi-evals/EVIDENCE_REVIEW.md`;
- each scenario's `metadata.validation_status` and `validation_note`; and
- each scenario's `cve_references` list.

## MITRE FiGHT

| Source | Use |
|---|---|
| [MITRE FiGHT](https://fight.mitre.org/) | Telecom-focused technique taxonomy |
| [FGT1499](https://fight.mitre.org/techniques/FGT1499) | Endpoint denial of service |
| [FGT5002](https://fight.mitre.org/techniques/FGT5002) | Network denial of service via signalling |
| [FGT5004](https://fight.mitre.org/techniques/FGT5004) | Network function service discovery |
| [FGT5012](https://fight.mitre.org/techniques/FGT5012) | Subscriber profile identifier discovery |
| [FGT5029](https://fight.mitre.org/techniques/FGT5029) | Weaken integrity |
| [FGT5035](https://fight.mitre.org/techniques/FGT5035) | Tunnel Endpoint ID modification |
| [FGT5043.001](https://fight.mitre.org/techniques/FGT5043/001) | Unauthorized access via token abuse |
| [FGT1599](https://fight.mitre.org/techniques/FGT1599) | Network boundary bridging |

MITRE FiGHT mapping describes an attack technique category. It is not proof that the implementation is vulnerable and should not replace local evidence.

## Related local notes

- [[00 - 5G Inspect Cyber - Index]]
- [[01 - 5G Inspect Cyber - eval.yaml]]
- [[02 - 5G Inspect Cyber - compose.yaml]]
- [[03 - 5G Inspect Cyber - solution scripts]]
- [[04 - 5G Inspect Cyber - execution flow]]
