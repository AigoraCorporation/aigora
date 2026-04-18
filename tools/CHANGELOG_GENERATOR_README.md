# Changelog Generator

Automated changelog generation based on Conventional Commits for the AIGORA project.

## Overview

The changelog generator parses git commits following the Conventional Commits format
and generates structured changelog entries organized by type (Added, Changed, Fixed, Removed).

## Features

- **Conventional Commits parsing**: Extracts type, scope, and subject from commit messages
- **Semantic grouping**: Automatically categorizes commits by type
- **Breaking change detection**: Identifies commits with breaking changes (marked with `!`)
- **Flexible version ranges**: Generate entries for specific commit ranges or since last tag
- **Dry-run mode**: Preview changes without modifying files
- **GitHub Actions integration**: Automated changelog generation in release workflows

## Usage

### Command Line

Generate changelog entries and preview them:

```bash
python3 tools/changelog_generator.py --version v0.2.0 --dry-run
```

Update CHANGELOG.md with generated entries:

```bash
python3 tools/changelog_generator.py --version v0.2.0
```

Generate entries for specific commit range:

```bash
python3 tools/changelog_generator.py \
  --version v0.2.0 \
  --rev-range v0.1.0..HEAD
```

### Options

- `--version VERSION` (required): Version for the changelog entry (e.g., v0.2.0)
- `--date DATE`: Release date in YYYY-MM-DD format (defaults to today)
- `--changelog PATH`: Path to CHANGELOG.md file (default: CHANGELOG.md)
- `--rev-range RANGE`: Git revision range (e.g., v0.1.0..HEAD). Defaults to commits since last tag
- `--repo PATH`: Path to git repository (default: current directory)
- `--dry-run`: Print changelog entry without updating file

### Examples

#### Generate entries since last tag

```bash
python3 tools/changelog_generator.py --version v0.2.0 --dry-run
```

#### Generate entries for a specific date

```bash
python3 tools/changelog_generator.py \
  --version v0.2.0 \
  --date 2026-04-20
```

#### Generate entries for commits between two tags

```bash
python3 tools/changelog_generator.py \
  --version v0.2.0 \
  --rev-range v0.1.0..v0.2.0-rc1
```

## Conventional Commits Format

Commits must follow the format:

```
<type>(<scope>): <subject>
```

### Supported Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Test additions/updates
- `perf`: Performance improvement
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Maintenance (no functional impact)
- `revert`: Revert previous commit

### Breaking Changes

Mark breaking changes with `!`:

```
feat(api)!: change session schema
```

## Changelog Sections

Commits are automatically categorized into changelog sections:

| Commit Type | Changelog Section |
|-------------|-------------------|
| feat | Added |
| fix | Fixed |
| refactor, perf, ci, build, docs, test, chore | Changed |
| revert | Removed |

## GitHub Actions Integration

The changelog generator is integrated into the release workflow via the
`generate-changelog.yml` GitHub Action.

### Automatic Generation on Release PR

When a Pull Request is opened from `release` to `main`, the action:

1. Parses commits since the last version tag
2. Generates changelog entries
3. Updates CHANGELOG.md
4. Automatically commits the changes
5. Posts a comment confirming the update

### Manual Trigger

Manually trigger the workflow in GitHub Actions:

1. Go to **Actions** → **Generate Changelog**
2. Click **Run workflow**
3. Enter version and optional revision range
4. Click **Run workflow**

## Implementation Details

### Code Structure

- `tools/changelog_generator.py`: Main script with classes:
  - `ConventionalCommit`: Parses individual commits
  - `ChangelogGenerator`: Generates changelog entries and updates files

### Testing

Run tests to verify functionality:

```bash
python3 -m pytest tests/unit/changelog_generator_test.py -v
```

Test coverage includes:
- Conventional commit parsing
- Type to section mapping
- Changelog formatting
- File updates
- Integration tests

## Validation

The CI pipeline validates release PRs:

- Checks that CHANGELOG.md was modified
- Validates changelog format
- Ensures at least one section has entries

Manual validation before merging:

1. Review generated changelog entries
2. Verify sections are properly formatted
3. Check that entries are readable and consistent
4. Ensure version matches intended release

## Limitations

- Only processes commits following Conventional Commits format
- Non-conventional commits are automatically excluded
- Does not support historical changelog reconstruction
- Changelog entries are text-based (no commit hashes in entries)

## Future Enhancements

Potential improvements:

- Support for commit bodies in changelog entries
- Custom mapping of types to sections
- Markdown link generation for commit references
- Support for pull request summaries
- Interactive changelog review before commit
- Automatic version bumping

## See Also

- [Release Workflow](./release-workflow.md)
- [Commit Convention](./conventions/commits.md)
- [Git Flow](./git-flow.md)
