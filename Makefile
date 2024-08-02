# Variables
DOCKER_COMPOSE_FILE = ./airflow/docker-compose.yaml
DOCKER_IMAGE_NAME = airflow_image
DBT_COMPOSE_FILE = ./dbt/docker-compose.yml
DBT_IMAGE_NAME = dbt_image

.PHONY: help build up down logs

# Ayuda
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-15s - %s\n", $$1, $$2}'

airflow-build: ## Build Airflow image
	@echo "Build Airflow image..."
	docker build -t $(DOCKER_IMAGE_NAME) ./airflow

airflow-up: ## Start Airflow docker-compose
	@echo "Starting Airflow..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d

airflow-down: ## Stop Airflow docker-compose
	@echo "Stopping Airflow..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

airflow-logs: ## Show logs of Airflow
	@echo "Showing logs..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

dbt-build: ## Build dbt image
	@echo "Build dbt image..."
	docker build -t $(DBT_IMAGE_NAME) ./dbt

dbt-up: ## Start dbt docker-compose
	@echo "Starting dbt..."
	docker-compose -f $(DBT_COMPOSE_FILE) up -d

dbt-down: ## Stop dbt docker-compose
	@echo "Stopping dbt..."
	docker-compose -f $(DBT_COMPOSE_FILE) down

dbt-logs: ## Show logs of dbt
	@echo "Showing logs..."
	docker-compose -f $(DBT_COMPOSE_FILE) logs -f

%:
	@echo "Target '$@' not found."
	@$(MAKE) help
