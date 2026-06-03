# Changelog

## Unreleased

## [1.0.13] - 2026-06-03

### Added

- Added `ark-review-gate` for cross-agent external review gating, Codex/other-agent review packages, findings import, and focused recheck packages.
- Added `external-review-gate.md` to define immediate review, low-risk batch candidates, batch-ready limits, findings classification, and validation evidence requirements.
- Added a one-command release gate script with strict changelog release checks and optional Claude plugin validation.
- Added a FastAPI `/hello` endpoint skill smoke that verifies a minimal ARK Artifact loop with an isolated temporary uv cache.

### Changed

- Updated `ark-implement` reports with an external review gate recommendation so high-risk tasks stop for review and low-risk same-loop tasks can batch.
- Updated `ark-debug` to treat imported external findings as bounded repair input and recommend focused recheck after fixes.
- Updated `ark-validate` so tasks under external review gate cannot move to Done without external review or recheck evidence.
- Updated `ark-review`, `ark-next`, `ark-handoff`, README, MEMORY templates, and Artifact policies for the new cross-agent review workflow.
- Strengthened version, README badge, marketplace, changelog, CI, release checklist, uv smoke, and skill smoke checks.
- Improved `ark-skill-smoke.py` failure output with a focused failure summary, failed command, and inspection paths.

## [1.0.12] - 2026-06-03

### Fixed

- Aligned `validation-entry.snippet.md` with the validation coverage contract.
- Reduced decision record placeholder residue risk and added checks for snippet placeholder drift.

## [1.0.11] - 2026-06-03

### Changed

- Upgraded `ark-review` to default deep contract-driven code review with Findings, Craftsmanship, Verification, Open Questions, ARK Follow-up, and Verdict sections.
- Added review references for contract-driven Python review, craftsmanship review, and recheck workflows.
- Added repository checks and tests for the upgraded `ark-review` contract.

## [1.0.10] - 2026-06-02

### Changed

- Removed stale `ark-implement` report terminology and aligned all default output language around the `功能结果` report section.
- Split detailed `ark-implement` comment/docstring and batch/sub-agent guidance into references to reduce default Skill prompt density.
- Added contract fixtures and checks for planning granularity, implement reports, and validation coverage semantics.

## [1.0.9] - 2026-06-02

### Changed

- Aligned `ark-spec`, `ark-design`, and `ark-plan` with functional delivery-unit task sizing so upstream artifacts do not create file/function-level task fragmentation.
- Simplified the default `ark-implement` report around functional results, implementation summary, validation status, and risk/writeback while making process-heavy sections conditional.
- Added checks, smoke coverage, and tests for plan task-boundary guidance, design technical-loop guidance, spec acceptance granularity, and implement report structure.

## [1.0.8] - 2026-06-02

### Changed

- Refined task sizing so `ark-tasks` defaults to functional delivery units or verifiable technical loops instead of file/function-level implementation steps.
- Added explicit batch implementation and validation coverage rules so related tasks can share one evidence record without weakening Done semantics.
- Added a mandatory functional-view section to `ark-implement` reports so implementation output explains user-visible capability changes before file-level diffs.

## [1.0.7] - 2026-06-02

### Added

- Added `ark-stage` for multi-MVP stage governance, including stage status audit, stage close/open/transition modes, archive preview, carryover gates, and current Artifact rebuilding rules.
- Added stage templates for `docs/ark/stages.md` and `docs/ark/archive/<stage-id>/stage-summary.md`.
- Added repository checks and smoke coverage for the `ark-stage` contract and stage templates.

### Changed

- Updated README routing, Skill overview, and release metadata for ARK 1.0.7.
- Clarified that `decisions.md` is project-level long-term memory during stage transitions: long-lived decisions are retained, stage-only decisions are archived, uncertain decisions default to retained, and replaced decisions are marked as `superseded`.

## [1.0.6] - 2026-06-02

### Fixed

- Unified the Mode A `uv init` command so initialization stays in the current directory and does not create a nested project directory.
- Removed stale fallback guidance that allowed empty Artifact files when templates are unavailable.
- Updated plugin, marketplace, and README version metadata to `1.0.6` so Claude Code can detect the release.

### Added

- Added Artifact placeholder policy for distinguishing initial templates from substantive project state.
- Added stricter `ark-check.py` checks for fallback Artifact headers, placeholder drift, Skill frontmatter, update boundaries, CI assets, and release metadata.
- Added CI, smoke checks, and minimal unittest coverage for ARK repository assets.
- Added release checklist covering version bumps, plugin update behavior, and smoke validation.

### Changed

- Reduced high-risk placeholder rows in Artifact templates.
- Made `ark-next` a read-only recovery/c裁决入口 and delegated state correction to `ark-sync` or other dedicated Skills.
- Aligned validation snippet fields with the `ark-validate` fidelity and authenticity contract.

## [1.0.5] - 2026-06-02

### Added

- Initial reviewed release metadata for ARK 1.0.5.
