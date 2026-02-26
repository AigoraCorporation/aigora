module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [2, "always", ["feat","fix","docs","refactor","test","perf","build","ci","chore","revert"]],
    "scope-enum": [2, "always", ["core","tutor","assessment","content","curriculum","evals","api","infra","docs","ci","repo"]],
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case"]],
    "subject-full-stop": [2, "never", "."],
    "scope-empty": [2, "never"],
    "type-empty": [2, "never"]
  }
};