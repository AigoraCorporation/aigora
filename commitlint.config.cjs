module.exports = {
  extends: ["@commitlint/config-conventional"],
  // Temporary ignores for two legacy commits in this PR that were made without
  // a scope. These patterns can be removed once those commits are no longer in
  // the checked range (i.e., after the PR merges into dev).
  ignores: [
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