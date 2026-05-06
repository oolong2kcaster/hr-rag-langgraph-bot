SHELL := /bin/bash
COMPOSE := docker compose
APP := app
DOCS ?= data/raw
Q ?=
AGENT ?=

.PHONY: help dev prod build rebuild start stop restart logs app-logs shell ingest validate ask agents test clean clean-index

help:
	@echo "HR RAG LangGraph Bot - commands"
	@echo ""
	@echo "  make dev                Copy .env if missing, build, start qdrant + app container"
	@echo "  make prod               Start services in detached mode for production-like use"
	@echo "  make build              Build app image"
	@echo "  make rebuild            Rebuild app image without cache"
	@echo "  make start              Start existing services"
	@echo "  make stop               Stop services"
	@echo "  make restart            Restart services"
	@echo "  make logs               Follow docker-compose logs"
	@echo "  make app-logs           Tail application log file"
	@echo "  make shell              Open shell in app container"
	@echo "  make ingest DOCS=data/raw"
	@echo "  make validate"
	@echo "  make ask Q='Nội quy nghỉ hằng năm như thế nào?'"
	@echo "  make agents             List document-agents loaded into vector store"
	@echo "  make test               Run tests"
	@echo "  make clean-index        Delete local processed reports and Qdrant collection"
	@echo "  make clean              Stop and remove docker volumes"

.env:
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example. Please set OPENAI_API_KEY."; fi

dev: .env build
	$(COMPOSE) up -d qdrant app
	@echo "Dev services are running. Next: make ingest DOCS=$(DOCS)"

prod: .env build
	$(COMPOSE) up -d
	@echo "Production-like services are running."

build: .env
	$(COMPOSE) build app

rebuild: .env
	$(COMPOSE) build --no-cache app

start:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) stop

restart: stop start

logs:
	$(COMPOSE) logs -f --tail=200

app-logs:
	@mkdir -p logs
	@touch logs/app.log
	tail -f logs/app.log

shell: .env
	$(COMPOSE) run --rm $(APP) bash

ingest: .env
	$(COMPOSE) run --rm $(APP) python -m app.main ingest --path "$(DOCS)"

validate: .env
	$(COMPOSE) run --rm $(APP) python -m app.main validate

ask: .env
	@if [ -z "$(Q)" ]; then echo "Usage: make ask Q='your question'"; exit 1; fi
	$(COMPOSE) run --rm $(APP) python -m app.main ask "$(Q)" $(if $(AGENT),--agent "$(AGENT)",)

agents: .env
	$(COMPOSE) run --rm $(APP) python -m app.main agents

test: .env
	$(COMPOSE) run --rm $(APP) pytest -q

clean-index: .env
	$(COMPOSE) run --rm $(APP) python -m app.main reset-index --yes
	rm -rf data/processed/*
	touch data/processed/.gitkeep

clean:
	$(COMPOSE) down -v --remove-orphans
