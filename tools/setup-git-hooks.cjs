/* tools/setup-git-hooks.cjs */
const { execSync } = require("node:child_process");
const { existsSync } = require("node:fs");

function run(cmd) {
  return execSync(cmd, { stdio: "inherit" });
}

try {
  // Just execute if it is inside git repo 
  if (!existsSync(".git")) {
    process.exit(0);
  }

  run("git config core.hooksPath .husky");
  console.log("✅ Git hooks enabled: core.hooksPath = .husky");
} catch (err) {
  console.warn("⚠️ Could not enable git hooks automatically.");
  console.warn("Run manually: git config core.hooksPath .husky");
  process.exit(0); 
}