build-app:
	sudo docker compose -f docker-compose.yaml --env-file .env build

stop-app:
	sudo docker compose -f docker-compose.yaml --env-file .env down

run-app:
	sudo docker compose -f docker-compose.yaml --env-file .env up -d

remove-app:
	sudo docker compose -f docker-compose.yaml --env-file .env down --rmi local

logs:
	sudo docker compose -f docker-compose.yaml --env-file .env logs -f

migration:
	sudo docker compose -f docker-compose.yaml --env-file .env run app uv run alembic revision --autogenerate -m "$(message)"

migrate:
	sudo docker compose -f docker-compose.yaml --env-file .env run app uv run alembic upgrade head