# Contributing to AIGORA

Welcome to AIGORA.

AIGORA is a doc-first AI tutoring architecture project.
We value clarity, architectural reasoning, and pedagogical rigor.

This document explains how to contribute consistently and safely.

---

## Table of Contents

- [Branching & Git Flow](#branching--git-flow)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)

---

## Branching & Git Flow

All contributions must follow the official workflow:

→ [Git Flow Guide](docs/06-operations/git-flow.md)

### Important

- Work must be done in feature branches.
- `main` is protected.
- No direct push to `main` is allowed.
- All changes must go through a Pull Request.

---

## Commit Convention

All commits must follow the Conventional Commits standard:

→ [Commit Convention](docs/conventions/commits.md)

Commits that do not follow the standard will fail CI checks.

---

## Pull Request Process

Before merging:

- Ensure CI passes
- Ensure commit messages follow the standard
- Provide a clear PR description (what and why)
- Keep changes focused and atomic

Only approved Pull Requests can be merged into `main`.