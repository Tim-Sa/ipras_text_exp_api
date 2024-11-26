dev_local_run:
	venv/bin/python src/app.py

migrations:
	venv/bin/python -m alembic upgrade heads