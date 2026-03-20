# Runbook

## Local Start
1. docker compose up -d`r
2. docker compose exec api alembic upgrade head`r
3. docker compose exec api python seed_demo.py`r
4. cd mobile && pip install -r requirements.txt && python main.py`r

## Operational Checks
- API health: /health`r
- Swagger: /docs`r
- Flower: http://localhost:5555`r

