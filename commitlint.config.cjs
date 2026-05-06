module.exports = {
  extends: ["@commitlint/config-conventional"],
  plugins: [
    {
      rules: {
        "body-max-line-length": (parsed, _when, value) => {
          const { body } = parsed;
          if (!body) return [true];
          const metadataPattern = /^(Agent-Logs-Url:|Co-authored-by:)/;
          const valid = body
            .split("\n")
            .every((line) => line.length <= value || metadataPattern.test(line));
          return [
            valid,
            `body's lines must not be longer than ${value} characters`,
          ];
        },
      },
    },
  ],
  rules: {
    "type-enum": [2, "always", ["feat","fix","docs","refactor","test","perf","build","ci","chore","revert"]],
    "scope-enum": [2, "always", ["core","tutor","assessment","content","curriculum","evals","api","infra","docs","ci","repo", "architecture"]],
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case"]],
    "subject-full-stop": [2, "never", "."],
    "scope-empty": [2, "never"],
    "type-empty": [2, "never"],
    "body-max-line-length": [2, "always", 100]
  }
};