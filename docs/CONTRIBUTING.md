## Git and GitHub workflow

Branching:
- main: always releasable, protected.
- feature/<scope>-<short-desc>: branch from main; short-lived.
- hotfix/<desc>: branch from main for urgent fixes.

Commits and PRs:
- Use Conventional Commits: feat(scope):, fix(scope):, chore:, refactor:, docs:, test:, ci:.
- Keep PRs small and focused; draft early, squash-merge when green.
- PR title uses Conventional Commit style; PR body explains what/why and links issues.

Reviews and protections:
- Require 1 review on main; status checks must pass; no force-push to main.
- Auto-delete branches on merge; prefer linear history via squash.

Releases:
- Tag `vX.Y.Z` from main.
- Release Drafter aggregates notes; publish on tag.

CI gates:
- Ruff + Black (check-only) for Python; ESLint for `expo/`.
- Optional tests: run non-network/unit tests; skip `archive/**` and `dev/tests/**` by default.

Secrets:
- Never commit credentials or dumps; use environment variables.
- Gitleaks runs in CI to detect secrets.

Local hygiene:
- `pre-commit install` to enable ruff/black/prettier hooks.


