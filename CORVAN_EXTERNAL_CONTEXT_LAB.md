# CORVAN · External-context cognitive hydration laboratory

**State:** noncanonical GitHub fixture; not installed in Casa, Nexus, Winston, ChatGPT runtime or an external app.

## Question under test
Can a host distinguish an internal conversation from an externally consumed artifact or action, retrieve only the functional capabilities that are needed, and adapt preparation criteria to the real audience without hard-coded app-name triggers or a fixed sequence?

Source specification (Drive, design candidate): `DESIGN_CANDIDATE_CORVAN_EXTERNAL_CONTEXT_HYDRATION_AND_AUDIENCE_ADAPTATION_v0_1` — document ID `1jZBUnNSEuANqb8ycUNF0dHjK1QGXQxv5pm5hze5EksI`.

## What the laboratory actually implements
- `src/corvan_external_context.py` receives a **typed mission signal** (purpose, consumption, operation, artifact kind, audience, destination, protected facts and action authorization).
- Classifies `INTERNAL`, `EXTERNAL_ARTIFACT`, `EXTERNAL_ACTION` or `MIXED` by purpose and context, **not** by Gmail, WhatsApp or GitHub in the input text.
- Selects the minimum set of available/current functional signatures from a synthetic catalog with preserved owners; rejects missing, stale, ownerless or ambiguous requirements.
- Produces differentiated output profiles for natural prose, academic, mathematics, code, and technical audiences.
- Uses a deterministic review of *protected factual strings* and a limited set of overly formulaic phrases; flags style concerns for human review rather than claiming authorship or linguistic quality.
- A publish/modify action is never performed in this module; only a permission state and a readback-contract requirement are produced.

## Function and owner discipline
These names describe **interfaces under test**, not new Casa owners:

- EXTERNAL_CONTEXT_BINDING: existing Context Hydration/Reanchor owners.
- FACT_CONSTRAINT_PRESERVATION: existing evidence/claim owners.
- AUDIENCE_FIT_REVIEW and LANGUAGE_CLARITY_REVIEW: existing output/intelligibility owners; Winston 56 and 68 retain phase boundaries when materially invoked.
- NUMERIC_CORRECTNESS_REVIEW / TECHNICAL_CORRECTNESS_REVIEW: domain verification capabilities, not an output prose template.
- EXTERNAL_EFFECT_PERMISSION_GATE and EXTERNAL_EFFECT_READBACK_CONTRACT: existing action permission and state-observation owners.

The fixture does **not** invoke primary Drive bodies or prove their runtime interfaces. It does **not** infer a person's identity, biography or emotional state.

## Adversarial tests
`tests/corvan_external_context_test.py` checks:

1. An internal question merely mentioning Gmail or WhatsApp does not trigger external hydration.
2. A third-party prose/academic artifact receives an audience-appropriate preparation profile.
3. Internal math retrieves numerical checking, not an unrelated language phase.
4. External mathematical reports, README/code, and technical materials have different function routes.
5. Mixed tasks preserve audience context.
6. Missing audience, destination, invalid intent, absent owner, stale functions and duplicate current owners are blocked.
7. Publish and modify require their **specific** authorizations; a prepared artifact cannot become a side effect by a status label.
8. Audience/domain perturbations change only relevant functions and keep facts invariant.
9. Lost protected facts require repair; boilerplate produces review advice, not automatic accusation.
10. PASS has a ceiling: deterministic fixture, not natural language generation or a Casa runtime.

## Evidence classification
- Target class: **M** (bounded selection mechanism) and **CTRL** (fail-closed boundaries).
- Evidence requested: observed PR test runs and source-file readback.
- No **CF**, **SYS**, **ADAPT** or cross-house runtime claim from these isolated tests.
- Genuine “no AI smell” cannot be proved by a small lexical list; it requires representative real drafts, blind reader judgments, preserved factual content and audience-specific review.
- Even a PR CI PASS does not permit automatic Casa admission.

## No side effects beyond laboratory commits
This laboratory writes only branch files and a pull request in `Fernando-corvan/skills-test-with-actions`. It must not send emails, publish to an outside platform, overwrite original Drive organs or merge automatically on an unsupported claim.

## Transfer after test
After recording the real SHA, PR number, checks, negative tests, failures and observed limitations, follow `corvan-agent-memory/protocols/lab_to_casa.md`: check the Casa 2.0 inventory, identify the functional owner, create a **proposal-only** receipt, and leave admission pending review. Unknown inventory function is a candidate for classification, not a new organ by default.
