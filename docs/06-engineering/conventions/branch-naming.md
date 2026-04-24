# Branch Naming Convention

This document defines the official branch naming convention for AIGORA.

## Branch Name Pattern

`<type>/<topic>`

Where:

- **type** — category of the change
- **topic** — short description of the change

## Allowed Types

| Prefix | Purpose | Example |
|-------|---------|--------|
| `feature/` | New functionality | `feature/student-model` |
| `fix/` | Bug fixes | `fix/login-validation` |
| `docs/` | Documentation updates | `docs/interaction-model` |
| `refactor/` | Code restructuring without behavior change | `refactor/retrieval-layer` |
| `test/` | Tests | `test/student-model-tests` |
| `chore/` | Maintenance tasks | `chore/update-ci` |

## Recommendations

- Use lowercase letters
- Use hyphens to separate words
- Keep branch names concise and descriptive