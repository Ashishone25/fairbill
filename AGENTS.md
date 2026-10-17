# AGENTS.md - rules for AI agents and humans

## Hard rules
- Never push to main. Work on a branch and open a pull request. Never merge your own PR.
- Do not create or edit dependabot configuration. We do not use Dependabot.
- Never commit secrets, API keys, real bills, or personal data. Use .env.example placeholders.
- Never store or log uploaded bill files or raw bill text. Only structured results are persisted.
- Keep PRs small and focused. Conventional Commit titles (feat:, fix:, test:, docs:, chore:).

## Stack
- web/: Next.js 16, React 19, TypeScript, Tailwind CSS 4, Clerk, Prisma 7 on NeonDB.
- api/: FastAPI on Python 3.14, Pydantic v2, scikit-learn, pandas, Gemini API (google-genai SDK).
- Pin dependency versions. Add a dependency only if the task needs it.

## Definition of done
- `make check` passes (web lint, tsc, build; api ruff, ruff format --check, pytest).
- New logic has tests. Public behaviour is documented in the PR description.
- User-facing wording says "possible overcharge". Never accuse a hospital or give legal advice.
