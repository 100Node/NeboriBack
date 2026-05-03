# -----------------------------
# CONFIGURATION
# -----------------------------
# За замовчуванням оточення "dev". 
# Щоб запустити для продакшену, додай ENV=prod (наприклад: make up ENV=prod)
ENV ?= dev

PROJECT_NAME = nebori_$(ENV)
COMPOSE_FILE = docker-compose.$(ENV).yml

# Базова команда, яка автоматично підставить правильний файл і назву проєкту
DC = docker compose --env-file .env.$(ENV).root -p $(PROJECT_NAME) -f $(COMPOSE_FILE)

# -----------------------------
# DOCKER COMMANDS
# -----------------------------
.PHONY: up build down clean logs fix-perms prune

# Запуск усіх сервісів у фоні
up:
	$(DC) up -d

# Перезбірка образів та запуск (використовуй після змін у Dockerfile)
build:
	$(DC) up -d --build

# Зупинка всіх сервісів
down:
	$(DC) down

# Повне очищення (зупинка + видалення volume'ів)
# Обережно: видалить усі дані БД і MinIO для поточного оточення!
clean:
	$(DC) down -v --remove-orphans

# Читання логів конкретного сервісу (make logs s=upload-service)
logs:
	$(DC) logs -f $(s)

# Швидкий фікс прав доступу для bash-скриптів (на хості)
fix-perms:
	chmod +x ./services/*/scripts/*.sh

# Глобальна чистка Docker від сміття
prune:
	docker system prune -a --volumes -f

# -----------------------------
# MIGRATIONS (Alembic)
# -----------------------------
# Використання: обов'язково вказуй сервіс через s=...
# Наприклад: make migrate s=upload-service

.PHONY: migrate revision current downgrade merge-heads

# Накотити останні міграції
migrate:
	$(DC) run --rm $(s) alembic upgrade head

# Створити нову міграцію (make revision s=upload-service m="init db")
revision:
	$(DC) run --rm -u root --entrypoint "" $(s) bash -c "alembic revision --autogenerate -m '$(m)' && chown -R $$(id -u):$$(id -g) ."

# Перевірити поточну міграцію
current:
	$(DC) run --rm $(s) alembic current

# Відкотити останню міграцію
downgrade:
	$(DC) run --rm $(s) alembic downgrade -1

# Злити кілька гілок міграцій (вирішення проблеми "multiple heads")
# (make merge-heads s=upload-service m="resolve conflict")
merge-heads:
	@if [ -z "$(m)" ]; then \
		$(DC) run --rm $(s) alembic merge heads; \
	else \
		$(DC) run --rm $(s) alembic merge heads -m "$(m)"; \
	fi

alembic-init:
	$(DC) run --rm -u root $(s) bash -c "alembic init alembic && chown -R $$(id -u):$$(id -g) alembic alembic.ini"