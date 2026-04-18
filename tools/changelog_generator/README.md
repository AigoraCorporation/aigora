# Changelog Generator

Automated changelog generation based on Conventional Commits.

## Quick Start

```bash
# Preview changelog for v0.2.0
python3 tools/changelog_generator.py --version v0.2.0 --dry-run

# Update CHANGELOG.md
python3 tools/changelog_generator.py --version v0.2.0
```

## How It Works

Parses git commits following Conventional Commits format and generates structured changelog entries:
- `feat` → **Added**
- `fix` → **Fixed**
- `refactor`, `perf`, `ci`, `build`, `docs`, `test`, `chore` → **Changed**
- `revert` → **Removed**
- Breaking changes (marked with `!`) → **Breaking** section

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--version` | Version for changelog (required) | `v0.2.0` |
| `--date` | Release date (YYYY-MM-DD) | `2026-04-20` |
| `--changelog` | Path to CHANGELOG.md | `CHANGELOG.md` |
| `--rev-range` | Git revision range | `v0.1.0..HEAD` |
| `--repo` | Repository path | `.` |
| `--dry-run` | Preview only | (flag) |

## Examples

### Generate since last tag
```bash
python3 tools/changelog_generator.py --version v0.2.0 --dry-run
```

### Generate for specific date
```bash
python3 tools/changelog_generator.py --version v0.2.0 --date 2026-04-20
```

### Generate for commit range
```bash
python3 tools/changelog_generator.py --version v0.2.0 --rev-range v0.1.0..v0.2.0
```

## Conventional Commits Format

Commits must follow: `<type>(<scope>): <subject>`

**Valid types:** feat, fix, docs, refactor, test, perf, build, ci, chore, revert

**Examples:**
```
feat(tutor): add adaptive hint policy
fix(assessment): handle empty answer input
docs(architecture): add C4 diagram
feat(api)!: change session schema
```

## GitHub Actions Integration

The workflow `generate-changelog.yml` automatically:
- Generates changelog when PR is opened from `release` to `main`
- Accepts manual triggers via GitHub Actions UI
- Commits and pushes changes automatically
- Posts confirmation comment

**Manual trigger:** Actions → Generate Changelog → Run workflow

## Testing

```bash
python3 -m pytest tests/unit/changelog_generator_test.py -v
```

## Validation

Release PR checks:
- CHANGELOG.md must be modified
- At least one changelog section must have entries
- Format validation (headers and structure)

## Key Points

- ✅ Only conventional commits are included (non-standard commits excluded)
- ✅ Follows existing CHANGELOG.md structure
- ✅ Supports semantic versioning (v0.1.0, v1.0.0, etc.)
- ✅ Detects breaking changes automatically
- ⚠️ Non-conventional commits are skipped (not an error)

## Implementation

- `tools/changelog_generator.py`: Main script
- `tests/unit/changelog_generator_test.py`: Test suite (15 tests)
- `.github/workflows/generate-changelog.yml`: GitHub Action

See [Release Workflow](../docs/06-engineering/workflow/release-workflow.md) for integration details.

