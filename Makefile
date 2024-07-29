current_dir = $(shell pwd)

start_service:
	docker compose -f docker-compose.yml up;

stop_service:
	docker compose -f docker-compose.yml stop;

build_service:
	docker compose -f docker-compose.yml build;

down_service:
	docker compose -f docker-compose.yml down;