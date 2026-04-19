# Changelog Generator

AI-powered automated changelog generation with fallback to deterministic generation based on Conventional Commits.

## Architecture

**Modular design** with separation of concerns:
- `models.py` - Pydantic models for type-safe data (Commit, ChangelogSection, ChangelogContent)
- `parser.py` - Conventional Commits parser + Git integration  
- `agent.py` - pydantic-ai based agent for LLM-powered generation with fallback

## Quick Start

### Unified CLI Interface

Use `cli.py` for all changelog generation with `--mode` parameter:

**Deterministic mode** (no API key needed):
```bash
python3 cli.py --mode deterministic --version v0.2.0
```

**AI-powered mode** (intelligent summarization):
```bash
export OPENAI_API_KEY=sk-proj-...
python3 cli.py --mode ai --version v0.2.0
```

**Compare branches:**
```bash
python3 cli.py --mode ai --version v0.2.0 --rev-range main..dev
```

**Alternative provider:**
```bash
python3 cli.py --mode ai --version v0.2.0 \
  --provider anthropic \
  --model claude-3-5-sonnet \
  --api-key sk-ant-...
```

### Legacy Demo Scripts

For quick testing without CLI arguments:
- `demo_dryrun.py` - Deterministic preview (no API key needed)
- `demo_ai.py` - AI-powered generation (requires API key)

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

## CLI Reference

### Basic Usage
```bash
python3 cli.py --version VERSION [--mode {deterministic,ai}] [options]
```

### Arguments

| Argument | Required | Default | Example |
|----------|----------|---------|---------|
| `--version` | Yes | - | `v0.2.0` |
| `--mode` | No | deterministic | `ai` or `deterministic` |
| `--repo` | No | Repository root | `/path/to/repo` |
| `--rev-range` | No | Commits since last tag | `main..dev` or `v0.1.1..HEAD` |
| `--date` | No | Today | `2026-04-20` |
| `--docs-scope` | No | - | `curriculum,architecture` |
| `--provider` | No | openai | `anthropic` |
| `--model` | No | gpt-4o-mini | `claude-3-5-sonnet` |
| `--api-key` | No | From .env or env vars | `sk-proj-...` |

### Full Examples
```bash
# Show help
python3 cli.py --help

# Deterministic mode - fast preview
python3 cli.py --mode deterministic --version v0.2.0

# AI mode with default OpenAI
python3 cli.py --mode ai --version v0.2.0

# Compare dev against main
python3 cli.py --mode ai --version v0.2.0 --rev-range main..dev

# Anthropic Claude model
python3 cli.py --mode ai --version v0.2.0 \
  --provider anthropic \
  --model claude-3-5-sonnet

# Custom date and scope filter
python3 cli.py --mode ai --version v0.2.0 \
  --date 2026-04-20 \
  --docs-scope curriculum,architecture
```

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

### Using the Unified CLI

**Preview with deterministic mode:**
```bash
python3 cli.py --mode deterministic --version v0.2.0
```

**Generate with AI (requires API key):**
```bash
export OPENAI_API_KEY=sk-proj-...
python3 cli.py --mode ai --version v0.2.0
```

**Compare branches (e.g., dev vs main):**
```bash
python3 cli.py --mode ai --version v0.2.0 --rev-range main..dev
```

**Use Anthropic Claude:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 cli.py --mode ai --version v0.2.0 \
  --provider anthropic \
  --model claude-3-5-sonnet
```

### Using Legacy Demo Scripts

**Quick preview without CLI:**
```bash
python3 demo_dryrun.py
```

**AI generation with environment setup:**
```bash
export OPENAI_API_KEY=sk-proj-...
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

