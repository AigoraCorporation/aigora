# Changelog Generator

AI-powered changelog generation with Conventional Commits support.

## Quick Start

**Preview (dry-run):**
```bash
python3 cli.py --mode deterministic --version v0.2.0 --dry-run
```

**Update CHANGELOG.md:**
```bash
python3 cli.py --mode deterministic --version v0.2.0
```

**AI-powered (requires API key):**
```bash
export OPENAI_API_KEY=sk-proj-...
python3 cli.py --mode ai --version v0.2.0
```

**Compare branches:**
```bash
python3 cli.py --mode ai --version v0.2.0 --rev-range main..dev
```

## Usage

```bash
python3 cli.py --version VERSION [--mode {deterministic,ai}] [options]
```

### Options

| Option | Default | Example |
|--------|---------|---------|
| `--version` | required | `v0.2.0` |
| `--mode` | deterministic | `ai` |
| `--dry-run` | false | (preview only, don't update) |
| `--rev-range` | since last tag | `main..dev` |
| `--date` | today | `2026-04-20` |
| `--repo` | repo root | `/path/to/repo` |
| `--provider` | openai | `anthropic` |
| `--model` | gpt-4o-mini | `claude-3-5-sonnet` |
| `--api-key` | from .env | `sk-proj-...` |

## Configuration

Set environment variables or create `.env`:
```bash
cp .env.example .env
```

```env
CHANGELOG_PROVIDER=openai
CHANGELOG_MODEL=gpt-4o-mini
CHANGELOG_API_KEY=sk-proj-...
```

## Architecture

- `models.py` - Data structures
- `parser.py` - Git + Conventional Commits
- `agent.py` - LLM integration with fallback
- `cli.py` - CLI interface

## Testing

```bash
python3 -m pytest tests/ -v
```

53 tests, ~78% coverage

