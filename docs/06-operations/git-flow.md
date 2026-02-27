# Git Flow --- How code reaches `main`

This document describes the official branching and contribution workflow
for AIGORA.

The goal is to ensure:

-   Clean history
-   Predictable merges
-   Enforced standards
-   Stable `main` branch

------------------------------------------------------------------------

## Branch Model

### `main`

-   Always stable
-   Protected
-   Updated **only via Pull Request**
-   All required checks must pass

### Feature branches

All work must be done in branches created from `main`.

Naming convention:

    feature/<short-description>
    docs/<short-description>
    chore/<short-description>
    refactor/<short-description>
    test/<short-description>

Examples:

    feature/adaptive-hint-policy
    docs/curriculum-topic-map
    chore/update-commitlint-rules

------------------------------------------------------------------------

## Enforced Rules (Protected `main`)

The following rules are enforced at the repository level:

-   🔒 No direct push to `main`
-   🔒 No merge without Pull Request
-   🔒 No merge if Commitlint fails
-   🔒 No force push
-   🔒 Required status checks must pass
-   🔒 At least one PR approval (if enabled)

These restrictions cannot be bypassed.

------------------------------------------------------------------------

## Step-by-step Contribution Flow

### 1. Clone the repository

``` bash
git clone <repo-url>
cd aigora
npm install
```

> `npm install` enables local commit validation via Husky.

------------------------------------------------------------------------

### 2. Sync `main`

``` bash
git checkout main
git pull origin main
```

------------------------------------------------------------------------

### 3. Create a feature branch

``` bash
git checkout -b feature/your-feature-name
```

------------------------------------------------------------------------

### 4. Make commits (Conventional Commits required)

Commit messages must follow:

    <type>(<scope>): <subject>

Example:

``` bash
git commit -m "docs(curriculum): add topic dependency map"
```

Commit rules are defined in:

    docs/conventions/commits.md

------------------------------------------------------------------------

### 5. Push the branch

``` bash
git push -u origin feature/your-feature-name
```

------------------------------------------------------------------------

### 6. Open a Pull Request → `main`

-   Provide a clear description
-   Explain what changed and why

------------------------------------------------------------------------

### 7. CI (Commitlint) runs automatically

If the check **fails**:

``` bash
git commit --amend
git push
```

CI will run again.

If the check **passes**:

The PR can be merged.

------------------------------------------------------------------------

### 8. Merge into `main`

After all requirements pass:

-   Status checks
-   Required approvals

The branch can be merged.

`main` remains protected.

------------------------------------------------------------------------

## Rebase Policy

Before merging, contributors may rebase their feature branch onto the
latest `main`:

``` bash
git checkout main
git pull origin main
git checkout feature/your-feature-name
git rebase main
git push --force-with-lease
```

### Important:

-   Rebase is allowed **only on your own feature branch**
-   Never rebase `main`
-   Never force push to `main`
-   Force push is blocked on protected branches

------------------------------------------------------------------------

## Recommended Merge Strategy

Preferred:

-   **Squash and merge**

Benefits:

-   Clean linear history
-   One commit per PR
-   Easy to read blame and changelog

------------------------------------------------------------------------

## Summary Flow

    Clone → Feature Branch → Commit → Push → PR → CI → Merge → main

If CI fails:

    Fix → Push → CI again

------------------------------------------------------------------------

## Philosophy

AIGORA prioritizes:

-   Clarity over speed
-   Structure over chaos
-   Governance over convenience

A clean Git history is part of the system architecture.
