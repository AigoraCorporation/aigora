# Development Workflow

This document defines the official development lifecycle of AIGORA.

All contributions must follow this workflow.

The goal is to ensure:

- Architectural discipline
- Scope alignment
- Clean history
- CI enforcement
- Predictable delivery

---

# Overview

All work in AIGORA follows this lifecycle:

Issue → Branch → Commit → Pull Request → CI → Merge → Close Issue

No work reaches `main` without passing through these stages.

---

# 1. Task Creation (Issue)

All work must start with a GitHub Issue.

An Issue defines:

- Context
- Objective
- Scope
- Acceptance Criteria

No feature or structural change should begin without an associated Issue.

Issues must be labeled appropriately (e.g., architecture, tutor, infra, docs, curriculum, evals, research).

---

# 2. Branch Creation

Branches must originate from `dev` (or the designated integration branch).

Naming convention:

feature/<issue-number>-short-description  
fix/<issue-number>-short-description  
docs/<issue-number>-short-description  

Example:

feature/12-student-model-schema

Branches must be linked to their Issue.

---

# 3. Commits

All commits must follow the Conventional Commits standard.

Reference:
docs/conventions/commits.md

Commits are validated via commitlint locally and in CI.

Example:

feat(tutor): implement adaptive hint strategy

---

# 4. Pull Request

All changes must be submitted through a Pull Request.

The PR must:

- Follow the official PR template
- Include Changes, Motivation, and Impact sections
- Align with Goals & Non-Goals
- Pass all CI checks

Direct pushes to `main` are not allowed.

---

# 5. Continuous Integration

All Pull Requests trigger automated checks:

- Commit message validation
- PR description validation
- Additional checks (future: tests, linting, coverage)

A PR cannot be merged if required checks fail.

---

# 6. Merge Policy

Only Pull Requests can update `main`.

Rules:

- No direct push to `main`
- No force push
- No merge without PR
- All required checks must pass

Recommended merge strategy:

Squash and merge

This keeps the `main` branch clean and readable.

---

# 7. Issue Closure

When a PR is merged:

- The related Issue must be closed
- The Project board item must move to "Done"

Use:

Closes #`<issue-number>`

inside the PR description for automatic closure.

---

# Governance Principles

AIGORA follows a doc-first philosophy.

This workflow ensures:

- Decisions are intentional
- Scope creep is minimized
- Architectural clarity is preserved
- Contributions remain structured and reviewable

Clean process is part of the system design.