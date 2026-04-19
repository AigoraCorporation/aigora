# Changelog Generator

AI-powered automated changelog generation with fallback to deterministic generation based on Conventional Commits.

## Architecture

**Modular design** with separation of concerns:
- `models.py` - Pydantic models for type-safe data (Commit, ChangelogSection, ChangelogContent)
- `parser.py` - Conventional Commits parser + Git integration  
- `agent.py` - pydantic-ai based agent for LLM-powered generation with fallback

## Quick Start

### 1. Deterministic Preview (No API Key Required)
```bash
python3 demo_dryrun.py
```
Shows raw structured changelog from commits (no AI summarization).

### 2. AI-Powered Generation (Requires API Key)
```bash
# Option A: Environment variables
export OPENAI_API_KEY=sk-proj-...
python3 demo_ai.py

# Option B: .env file
cp .env.example .env
# Edit .env and add your API key
python3 demo_ai.py

# Option C: Alternative provider
export CHANGELOG_PROVIDER=anthropic
export CHANGELOG_MODEL=claude-3-5-sonnet
export ANTHROPIC_API_KEY=sk-ant-...
python3 demo_ai.py
```

## Configuration

### Environment Variables
```bash
# Required
CHANGELOG_PROVIDER=openai              # openai, anthropic, etc.
CHANGELOG_MODEL=gpt-4o-mini           # Model name
CHANGELOG_API_KEY=sk-proj-...          # API key (or use provider-specific keys)

# Optional
CHANGELOG_DATE=2026-04-20              # Release date (YYYY-MM-DD)
CHANGELOG_REV_RANGE=v0.1.1..HEAD       # Commit range (default: since last tag)
CHANGELOG_DOCS_SCOPE=curriculum,arch   # Documentation scope filter
```

### .env File
Copy `.env.example` and fill in your values:
```bash
cp .env.example .env
# Edit .env with your provider details
```

The `.env` file is automatically loaded and takes precedence over environment variables.

## How It Works

**Deterministic Mode (Fallback):**
Parses git commits following Conventional Commits format and groups into sections:
- `feat` → **Added**
- `fix` → **Fixed**
- `refactor`, `perf`, `ci`, `build`, `docs`, `test`, `chore` → **Changed**
- `revert` → **Removed**
- Breaking changes (marked with `!`) → **Breaking** section

**AI-Powered Mode:**
When API key is available, uses LLM to intelligently:
- Consolidate duplicate commits from merged branches
- Create human-readable descriptions
- Group related changes logically
- Summarize at component level

## Command Line Options (via demo_ai.py)

| Option | Description | Example |
|--------|-------------|---------|
| version | Version for changelog | `v0.2.0` |
| rev-range | Git revision range | `v0.1.1..HEAD` |
| date | Release date (YYYY-MM-DD) | `2026-04-20` |
| docs-scope | Documentation scope filter | `curriculum,architecture` |

## Testing

Run full test suite:
```bash
python3 -m pytest tests/ -v
```

**Coverage:**
- 53 tests covering models, parser, and agent
- ~78% code coverage
- All core functionality tested

## Examples

### Preview changelog (no API key needed)
```bash
python3 demo_dryrun.py
```

### Generate with AI (requires OPENAI_API_KEY)
```bash
export OPENAI_API_KEY=sk-proj-...
python3 demo_ai.py
```

### Specify alternative provider
```bash
CHANGELOG_PROVIDER=anthropic \
CHANGELOG_MODEL=claude-3-5-sonnet \
ANTHROPIC_API_KEY=sk-ant-... \
python3 demo_ai.py
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

