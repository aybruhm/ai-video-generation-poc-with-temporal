run:
	docker compose -f compose.yml up --build -d

stop:
	docker compose -f compose.yml down

add_migration:
	chmod 777 migrations/versions/
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a message. Usage: make add_migration MSG='your migration message'"; \
		exit 1; \
	fi
	docker compose -f compose.yml exec api python -m alembic revision --autogenerate -m "$(MSG)"
	chmod 777 migrations/versions/

run_migrations:
	docker compose -f compose.yml exec api python -m alembic upgrade head
