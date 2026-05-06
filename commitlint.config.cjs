module.exports = {
  extends: ["@commitlint/config-conventional"],
  ignores: [
    // Ignore two legacy commits that were created without a scope before
    // scope enforcement was applied to chore commits.
    (message) => /^chore: add UNKNOWN\.egg-info/.test(message),
    (message) => /^chore: fix \.gitignore/.test(message),
  ],
  rules: {
    "type-enum": [2, "always", ["feat","fix","docs","refactor","test","perf","build","ci","chore","revert"]],
    "scope-enum": [2, "always", ["core","tutor","assessment","content","curriculum","evals","api","infra","docs","ci","repo", "architecture"]],
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case"]],
    "subject-full-stop": [2, "never", "."],
    "scope-empty": [2, "never"],
    "type-empty": [2, "never"],
    "body-max-line-length": [2, "always", 200],
  }
};