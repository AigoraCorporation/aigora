# Git Flow --- How code reaches `main`

This document describes the official branching strategy for AIGORA.

The goal is to ensure:

-   Clean history
-   Predictable releases
-   Stable `main` branch
-   Controlled integration of features

------------------------------------------------------------------------

# Branch Model

AIGORA follows a multi-stage integration model:

main ↑ release ↑ dev ↑ feature branches

Flow:

feature → dev → release  → main

Each stage has a specific responsibility in the delivery pipeline.

------------------------------------------------------------------------

## `main`

The `main` branch represents the **stable state of the system**.

Rules:

-   Always stable
-   Protected
-   Updated **only via Pull Request**
-   No direct pushes allowed
-   All required checks must pass

`main` should always reflect a deployable state.

------------------------------------------------------------------------

## `release`

The `release` branch is used to prepare production-ready versions.

Responsibilities:

-   Stabilization before release
-   Final validation
-   Release documentation

Only the `dev` branch can be merged into `release`.

Hotfixes may also be applied here if necessary.

------------------------------------------------------------------------

## `dev`

The `dev` branch is the **integration branch**.

All feature work must merge here first.

Responsibilities:

-   Integration of features
-   Continuous validation
-   Early detection of conflicts

`dev` acts as the development baseline for the system.

------------------------------------------------------------------------

## Feature Branches

All development work must be performed in branches created from `dev`.

Feature branches must be short-lived and merged into `dev` via Pull Request.

For branch naming rules, see:

`docs/06-engineering/conventions/branch-naming.md`

**Recommendations**

- Use lowercase letters
- Use hyphens to separate words
- Keep names concise and descriptive

------------------------------------------------------------------------

# Enforced Rules

Protected branches:

-   `main`
-   `release`
-   `dev`

Rules:

-   🔒 No direct push
-   🔒 No force push
-   🔒 Pull Request required
-   🔒 CI checks must pass

------------------------------------------------------------------------

# Merge Strategy

Preferred merge strategy:

**Merge commit**

Benefits:

-   Preserves complete commit history
-   Maintains development context
-   Improves debugging and investigation
-   Improves debugging and investigatio
-   Preserves commit authorship
-   Improves architectural traceability
-   Retains granular review history
-   Avoids loss of information caused by squashing commits
-   Provides a transparent evolution of the codebase

------------------------------------------------------------------------

# Rebase Policy

Rebase is allowed **only on feature branches**.

Example:

git checkout dev git pull origin dev git checkout feature/my-feature git
rebase dev git push --force-with-lease

Never rebase:

-   `dev`
-   `release`
-   `main`

------------------------------------------------------------------------

# Summary

Development flow:

feature → dev → release → main

This ensures:

-   Safe integration
-   Controlled releases
-   Stable production branch
