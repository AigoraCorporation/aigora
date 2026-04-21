# Contributing to AIGORA

Welcome to AIGORA.

AIGORA is a doc-first AI tutoring architecture project.
We value clarity, architectural reasoning, and pedagogical rigor.

This document explains how to contribute consistently and safely.

---

## Table of Contents

- [Project Scope](#project-scope)
- [Branching & Git Flow](#branching--git-flow)
- [Development Workflow](#development-workflow)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)

---

## Project Scope

→ [Goals & Non-Goals](docs/00-vision/goals-non-goals.md)

All contributions must align with the defined strategic scope.

---

## Branching & Git Flow

→ [Git Flow Guide](docs/05-engineering/workflow/git-flow.md)

- Work must be done in feature branches.
- `main` is protected.
- No direct push to `main` is allowed.
- All changes must go through a Pull Request.

---

## Task Creation

All work must begin with a GitHub Issue.

Use the official Issue template when creating new tasks.

Location:
→ .github/ISSUE_TEMPLATE/task.md

No feature or architectural change should start without an associated Issue.

---

## Development Workflow

All work must follow the official development lifecycle:

→ [Development Workflow](docs/05-engineering/workflow/development-workflow.md)

No change reaches `main` without:

- An associated Issue
- A dedicated branch
- Conventional commits
- A Pull Request
- Passing CI checks

This workflow is mandatory.

---

## Commit Convention

→ [Commit Convention](docs/05-engineering/conventions/commits.md)

Commits that do not follow the standard will fail CI checks.

---

## Pull Request Process

All Pull Requests must follow the official PR template.

→ [.github/pull_request_template.md](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)

Before merging:

- Ensure CI passes
- Ensure commit messages follow the standard
- Provide a clear PR description
- Keep changes focused and atomic