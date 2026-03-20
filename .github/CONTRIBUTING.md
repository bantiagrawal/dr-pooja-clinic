# Contributing

Thanks for contributing to `dr-pooja-clinic`.

## Workflow

1. Create an issue first (bug/feature/task).
2. Create a branch from `main`.
3. Keep PRs small and focused.
4. Link PR to issue.
5. Include validation steps in PR description.

## Local Setup

- Backend: `docker compose up -d` then `docker compose exec api alembic upgrade head`
- Mobile: `cd mobile && pip install -r requirements.txt && python main.py`

## Coding Expectations

- Follow existing folder structure and naming.
- Avoid unrelated refactors in feature PRs.
- Keep security-sensitive defaults safe.
