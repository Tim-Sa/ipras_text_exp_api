dev_local_run:
	venv/bin/python src/app.py

migrations:
	venv/bin/python -m alembic upgrade heads

run:
	docker-compose up --force-recreate -d

stop:
	docker-compose down