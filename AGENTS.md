# Repository Guidelines

## Project Structure & Module Organization

This repository currently contains product and implementation documentation plus seed data. Key paths:

- `data/`: source materials used for import and knowledge management, including `.docx` scenic data and `.xlsx` behavior data.
- `docs/superpowers/specs/`: approved design specs.
- `docs/superpowers/plans/`: execution plans for the first implementation slice.
- Root `*.md`: product requirements and development planning documents in Chinese.

Planned source layout for implementation:

- `backend/`: FastAPI service, import pipeline, models, tests.
- `admin-web/`: Vue 3 + Element Plus admin UI.
- `uploads/`: local uploaded files; keep only `.gitkeep` in version control.

## Build, Test, and Development Commands

**Python interpreter**: Use `D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe` for all backend commands (not the .venv one).

- Backend run: `"D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m uvicorn app.main:app --reload`
- Backend tests: `"D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m pytest tests -q`
- Backend install deps: `"D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m pip install -r requirements.txt`
- Frontend install: `cd admin-web && npm install`
- Frontend dev server: `npm run dev`
- Frontend tests: `npm run test`
- Frontend build: `npm run build`
- Miniprogram dev (H5): `cd miniprogram && npm run dev:h5`
- Miniprogram dev (WeChat): `cd miniprogram && npm run dev:mp-weixin`

Use `npm.cmd` on Windows PowerShell to avoid execution policy issues.

## Coding Style & Naming Conventions

- Python: 4-space indentation, type hints required, snake_case for modules/functions, PascalCase for models/schemas.
- Vue/TypeScript: PascalCase for components, camelCase for variables/functions, route/view files named by feature, e.g. `ScenicSpotListView.vue`.
- Keep modules focused by domain: `auth`, `scenic`, `knowledge`, `imports`, `dashboard`, `settings`.
- Prefer ASCII in code and filenames unless the file is user-facing content already using Chinese.

## Testing Guidelines

- Backend: `pytest` with test files named `test_<feature>.py`.
- Frontend: `Vitest` with `*.test.ts`.
- Follow TDD: write the failing test first, run it, then implement the minimum code to pass.
- Cover import flows, CRUD endpoints, dashboard aggregation, and login/auth boundaries.

## Commit & Pull Request Guidelines

This repository does not yet include Git history. Use Conventional Commits from the start:

- `feat: add scenic spot import`
- `fix: handle empty docx rows`
- `docs: update backend run instructions`

PRs should include: purpose, scope, verification steps, affected paths, and screenshots for UI changes. Link the relevant spec or plan file when implementing planned work.

## Security & Configuration Tips

- Never commit real API keys, passwords, or filled `.env` files.
- Keep MySQL credentials in local environment variables.
- Treat files in `data/` as source data; do not overwrite them during import.
