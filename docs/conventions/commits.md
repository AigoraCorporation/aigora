# Commit Convention

This project follows **Conventional Commits** to maintain a clean
history, facilitate changelog generation, and simplify code reviews.

## Format

`<type>(<scope>): <subject>`

Examples:

-   feat(tutor): add tutoring loop skeleton
-   fix(assessment): handle empty answer input
-   docs(architecture): add C4 container diagram
-   refactor(core): split student model into profiles
-   test(tutor): add policy decision unit tests
-   chore(ci): add commitlint workflow

------------------------------------------------------------------------

## Allowed Types

-   **feat**: new feature
-   **fix**: bug fix
-   **docs**: documentation only
-   **refactor**: internal change without altering behavior
-   **test**: adding or updating tests
-   **perf**: performance improvement
-   **build**: build system or dependency changes
-   **ci**: CI/CD pipelines or automation
-   **chore**: general maintenance tasks (no functional impact)
-   **revert**: revert a previous commit

------------------------------------------------------------------------

## Scope (Required)

The scope indicates the affected module or area. Use one of the
following:

-   core
-   tutor
-   assessment
-   content
-   curriculum
-   evals
-   api
-   infra
-   docs
-   ci
-   repo

If unsure, use `repo`.

------------------------------------------------------------------------

## Subject Rules

-   Must be written in **English**
-   Use the **imperative mood** ("add", "fix", "update")
-   **No trailing period**
-   Maximum \~72 characters
-   Describe *what* changed (the *why* can go in the body)

### ✅ Good

-   feat(tutor): add adaptive hint policy

### ❌ Bad

-   feat: Added stuff.
-   update things

------------------------------------------------------------------------

## Body (Optional, Recommended for Larger Changes)

Use the body to explain motivation, context, and trade-offs.

------------------------------------------------------------------------

## Breaking Changes

If the change introduces a breaking change, indicate it:

-   Add `!` in the header:
    -   feat(api)!: change session schema

And/or include in the body:

BREAKING CHANGE: describe what changed and provide migration notes.
