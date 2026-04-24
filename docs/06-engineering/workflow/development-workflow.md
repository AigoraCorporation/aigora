# Development Workflow

This document defines the official development lifecycle of AIGORA.

All contributions must follow this workflow.

The goal is to ensure:

-   Architectural discipline
-   Scope alignment
-   Clean history
-   CI enforcement
-   Predictable delivery

------------------------------------------------------------------------

# Overview

All work in AIGORA follows this lifecycle:

Issue → Branch → Commit → Pull Request → CI → Merge → Close Issue

No work reaches protected branches without passing through these stages.

------------------------------------------------------------------------

# 1. Task Creation (Issue)

All work must start with a GitHub Issue.

An Issue defines:

-   Context
-   Objective
-   Scope
-   Acceptance Criteria

No feature or structural change should begin without an associated
Issue.

Issues must be labeled appropriately.

------------------------------------------------------------------------

# 2. Branch Creation

Branches must follow the branching strategy defined in:

`docs/06-engineering/workflow/git-flow.md`

Branch naming conventions are defined in:

`docs/06-engineering/conventions/branch-naming.md`

Feature branches originate from the **`dev` branch`.

Branches should be linked to their corresponding Issue.

------------------------------------------------------------------------

# 3. Commits

All commits must follow the **Conventional Commits** standard.

Reference:

docs/06-engineering/conventions/commits.md

Commits are validated via **commitlint** locally and in CI.

Example:

feat(tutor): implement adaptive hint strategy

------------------------------------------------------------------------

# 4. Pull Request

All changes must be submitted through a Pull Request.

The PR must:

-   Follow the official PR template
-   Include Changes, Motivation, and Impact sections
-   Align with Goals & Non-Goals
-   Pass all CI checks

Feature branches must target:

dev

------------------------------------------------------------------------

# 5. Continuous Integration

All Pull Requests trigger automated checks.

Examples:

-   Commit message validation
-   PR description validation
-   Future checks (tests, linting, coverage)

A PR cannot be merged if required checks fail.

------------------------------------------------------------------------

# 6. Promotion Between Branches

Code promotion follows the Git Flow model:

feature → dev → release → main

Meaning:

-   Features integrate into `dev`
-   Stabilized versions move to `release`
-   Production-ready versions move to `main`

------------------------------------------------------------------------

# 7. Issue Closure

When a PR is merged:

-   The related Issue must be closed
-   The Project board item must move to "Done"

Use:

Closes \#`<issue-number>`

inside the PR description for automatic closure.

------------------------------------------------------------------------

# Governance Principles

AIGORA follows a **doc-first philosophy**.

This workflow ensures:

-   Decisions are intentional
-   Scope creep is minimized
-   Architectural clarity is preserved
-   Contributions remain structured and reviewable

Clean process is part of the system design.
