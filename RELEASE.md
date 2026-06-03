# ARK Release Checklist

Use this checklist before publishing a new ARK plugin version.

## Versioning

- Bump `.claude-plugin/plugin.json` `version`
- Bump `.claude-plugin/marketplace.json` `metadata.version`
- Bump `.claude-plugin/marketplace.json` plugin entry `version`
- Update README version badge
- Add a `CHANGELOG.md` entry for the new version

ARK uses explicit plugin versions. If `plugin.json` keeps the same version string, Claude Code may treat the installed plugin as current and skip `/plugin update`, even when new commits exist.

## Local Checks

For release checks, uv must be installed. After moving `CHANGELOG.md` `Unreleased`
content into the target version entry, run the one-command release gate:

```bash
python scripts/ark-release-check.py
```

To inspect the gate without running it:

```bash
python scripts/ark-release-check.py --list
```

The release gate runs:

```bash
python -m json.tool .claude-plugin/plugin.json
python -m json.tool .claude-plugin/marketplace.json
python scripts/ark-check.py --release
python scripts/ark-smoke.py
python scripts/ark-smoke.py --require-uv
python scripts/ark-skill-smoke.py
python -m unittest discover -s tests
uv run python scripts/ark-check.py --release
uv run python scripts/ark-smoke.py --require-uv
uv run python scripts/ark-skill-smoke.py
uv run python -m unittest discover -s tests
```

If Claude Code CLI is available on `PATH`, the release gate also runs:

```bash
claude plugin validate .
```

Use `python scripts/ark-release-check.py --require-claude` when the release
machine must have Claude Code CLI, or `--skip-claude` when plugin validation is
handled manually.

Then inspect tracked/untracked changes:

```bash
git status --short
```

Before publishing, confirm any new release assets are intentionally added to the commit, especially `.github/workflows/`, `tests/`, `scripts/`, `rules/`, `CHANGELOG.md`, and `RELEASE.md`.

## Plugin Smoke

When Claude Code CLI is available, validate the plugin manifest:

```bash
claude plugin validate .
```

Then validate and install from a local marketplace inside Claude Code:

```text
/plugin validate .
/plugin marketplace add ./path/to/ark
/plugin install ark@ark
/reload-plugins
```

Then verify a versioned update:

```text
/plugin marketplace update ark
/plugin update ark@ark
/reload-plugins
```

## Init Smoke

In a temporary empty directory, run `/ark:ark-init` Mode A. The uv path must use:

```bash
uv init --bare --name <distribution_name> --python <version> --build-backend hatch --no-workspace --vcs none --no-readme --no-pin-python
```

Verify:

- No nested project directory is created
- `pyproject.toml` does not contain `[project.scripts]`
- No uv-generated sample Python file, `main()`, `hello()`, or `Hello from ...` remains
- ARK manually creates `src/<package_name>/__init__.py`
- `docs/ark/` contains 7 non-empty Artifact files
- Each Artifact has `ark-artifact`, `schema-version`, and `last-updated`
- `pyproject.toml` uses `build-backend = "hatchling.build"`
- No generated Python file exists except package/test `__init__.py` and explicitly allowed test scaffolding

In an existing sample project, run `/ark:ark-init` Mode B and verify:

- Existing source files are not modified
- Existing project configs are not modified
- `CLAUDE.md`, `MEMORY.md`, and missing `docs/ark/*` are created or skipped according to user choice
- Local `.claude/` helper files are created only after user confirmation

## Do Not Run In Release Automation

- `rm -rf`
- `git reset --hard`
- Automatic commits
- Automatic plugin publishing without the checks above
