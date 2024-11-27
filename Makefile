dev_local_run:
	venv/bin/python src/app.py

migrations:
	venv/bin/python -m alembic upgrade heads

run:
	docker-compose up --force-recreate -d -V

stop:
	docker-compose down --rmi all

restart:
	make stop
	make run