# Changelog Generation Workflows

This project uses a **dual changelog workflow** to manage changes across multiple branches with manual review at each stage.

## Workflow Overview

```
develop (dev features)
    ↓ [Generate Staging Changelog]
release (staged for production)
    ↓ [Generate Changelog]
main (production)
```

### Branch Hierarchy

- **main** - Production releases (stable, customer-facing)
- **release** - Staging branch (pre-release, ready for production)
- **develop** - Development (integration of features and fixes)

---

## Workflow 1: Generate Staging Changelog

**When to use:** Before merging `develop` → `release`

**Compares:** `release...develop` (commits in develop not yet in release)

**Steps:**

1. Go to **Actions** → **Generate Staging Changelog**
2. Click **Run workflow**
3. Enter:
   - **Version**: e.g., `staging-v0.2.0` or `v0.2.0-rc.1`
   - **Rev-range** (optional): Leave blank for default `release..develop`
4. Review the **dry-run preview** in workflow output
5. If satisfied, commit to `release` branch:
   ```bash
   git checkout release
   python3 tools/changelog_generator/cli.py \
     --version "v0.2.0" \
     --rev-range "release..develop" \
     --mode deterministic
   git add CHANGELOG-STAGING.md
   git commit -m "chore(changelog): prepare staging release v0.2.0"
   git push
   ```
6. Then merge or fast-forward `release` with latest commits

**Output:** `CHANGELOG-STAGING.md` (or annotated in CHANGELOG.md)

---

## Workflow 2: Generate Changelog

**When to use:** Before merging `release` → `main` for production

**Compares:** `main...release` (commits in release not yet in main)

**Steps:**

1. Go to **Actions** → **Generate Changelog**
2. Click **Run workflow**
3. Enter:
   - **Version**: e.g., `v0.2.0`
   - **Rev-range** (optional): Leave blank for default `main..release`
4. Review the **dry-run preview** in workflow output
5. If satisfied, commit to `release` branch:
   ```bash
   git checkout release
   python3 tools/changelog_generator/cli.py \
     --version "v0.2.0" \
     --rev-range "main..release" \
     --mode deterministic
   git add CHANGELOG.md
   git commit -m "chore(changelog): generate changelog for v0.2.0"
   git push
   ```
6. Then open a PR from `release` → `main`

**Output:** `CHANGELOG.md`

---

## Typical Release Flow

### Phase 1: Feature Development
```
# On develop branch
# ... create features, fixes, PRs ...
```

### Phase 2: Stage for Release
```bash
# 1. Ensure develop is up-to-date
git checkout develop
git pull

# 2. Generate staging changelog preview
# → Go to Actions → Generate Staging Changelog
# → Review commits in develop (relative to release)

# 3. Merge into release
git checkout release
git merge develop
git push

# 4. Update changelog for staging
python3 tools/changelog_generator/cli.py \
  --version "v0.2.0" \
  --rev-range "release..develop" \
  --mode deterministic
```

### Phase 3: Release to Production
```bash
# 1. Generate production changelog preview
# → Go to Actions → Generate Changelog
# → Review commits in release (relative to main)

# 2. Update CHANGELOG.md
python3 tools/changelog_generator/cli.py \
  --version "v0.2.0" \
  --rev-range "main..release" \
  --mode deterministic

# 3. Open PR from release → main
git push
# → Open PR on GitHub
```

### Phase 4: Merge to Production
```bash
# On GitHub: Review and merge PR release → main
# This triggers validate-release-pr.yml checks
# Then merge to production
```

---

## Manual Changelog Commands

If you prefer to generate changelogs locally without the workflow:

### Staging (develop → release)
```bash
cd tools/changelog_generator
python3 cli.py \
  --version "v0.2.0" \
  --rev-range "release..develop" \
  --mode deterministic \
  --dry-run  # Remove to commit
```

### Production (release → main)
```bash
cd tools/changelog_generator
python3 cli.py \
  --version "v0.2.0" \
  --rev-range "main..release" \
  --mode deterministic \
  --dry-run  # Remove to commit
```

### With AI Enhancement
```bash
python3 cli.py \
  --version "v0.2.0" \
  --rev-range "main..release" \
  --mode ai \
  --provider openai \
  --model gpt-4o-mini \
  --dry-run
```

---

## Validation

### Release PR to Main
When you open a PR from `release` → `main`:
- **validate-release-pr.yml** checks:
  - ✅ PR source is `release` branch
  - ✅ CHANGELOG.md was modified
  - ℹ️ Shows if late-arriving PRs might need changelog regeneration

---

## Configuration

Both workflows use credentials from:
- `.env` file (local) or GitHub secrets for API keys
- `CHANGELOG_PROVIDER` - LLM provider (openai, anthropic)
- `CHANGELOG_MODEL` - Model name (gpt-4o-mini, claude-3-5-sonnet, etc.)
- `CHANGELOG_API_KEY` - Provider API key

---

## Best Practices

1. **Always review dry-run preview** before committing
2. **Use meaningful version numbers** (v0.2.0, not staging-1.0)
3. **One changelog commit per release** (don't split across PRs)
4. **Run staging before release** to avoid surprises
5. **Keep develop → release → main flowing** in one direction
6. **Test changelog generation locally** before GitHub Actions

---

## Troubleshooting

**Q: "main..release not found"**  
A: Ensure both branches exist locally. Run: `git fetch origin`

**Q: "No commits in range"**  
A: Correct! No changes to release since last production release.

**Q: "Want to regenerate?"**  
A: Re-run the workflow with the same version - previous changelog will be updated.

**Q: "Custom commits selection?"**  
A: Use `--rev-range` parameter to specify exact commit range (e.g., `commit1..commit2`)

