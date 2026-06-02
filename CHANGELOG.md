# Changelog

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
