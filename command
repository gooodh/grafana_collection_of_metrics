uvicorn app.main:app --host 0.0.0.0 --port 8080
docker compose up -d --build
docker compose -f docker-compose-prod.yml up -d --build

docker compose down
docker compose down -v

http://localhost:15432/
http://localhost:3000/  #  grafana
http://localhost:8080/  #  app

python -m pytest tests/ -v

docker exec app_postgres_container hostname -I или -i

alembic init -t async app/migration

; Измененный код migration/env.py
; import asyncio
; from logging.config import fileConfig
; from sqlalchemy import pool
; from sqlalchemy.ext.asyncio import async_engine_from_config
; from alembic import context
; from bot.database import Base, DATABASE_PG_URL
; from bot.users.models import User  # Импортируйте ваши модели

; config = context.config
; config.set_main_option("sqlalchemy.url", DATABASE_PG_URL)

; if config.config_file_name is not None:
;     fileConfig(config.config_file_name)

; target_metadata = Base.metadata

; def run_migrations_offline() -> None:
;     url = config.get_main_option("sqlalchemy.url")
;     context.configure(
;         url=url,
;         target_metadata=target_metadata,
;         literal_binds=True,
;         dialect_opts={"paramstyle": "named"},
;     )

;     with context.begin_transaction():
;         context.run_migrations()

; def do_run_migrations(connection) -> None:
;     context.configure(connection=connection, target_metadata=target_metadata)

;     with context.begin_transaction():
;         context.run_migrations()

; async def run_async_migrations() -> None:
;     connectable = async_engine_from_config(
;         config.get_section(config.config_ini_section, {}),
;         prefix="sqlalchemy.",
;         poolclass=pool.NullPool,
;     )

;     async with connectable.connect() as connection:
;         await connection.run_sync(do_run_migrations)

;     await connectable.dispose()

; def run_migrations_online() -> None:
;     asyncio.run(run_async_migrations())

; if context.is_offline_mode():
;     run_migrations_offline()
; else:
;     run_migrations_online()


alembic.ini -> sqlalchemy.url = sqlite+aiosqlite:///data/db.sqlite3
alembic.ini -> sqlalchemy.url = postgresql://postgres_container:postgres_container@172.18.0.2:5432/postgres


alembic revision --autogenerate -m "Initial revision"



alembic upgrade head #Обновление базы данных до последней версии миграции
docker compose exec bot alembic upgrade head

alembic downgrade -1  # Чтобы откатить миграцию на одну версию назад или alembic downgrade d97a9824423b



alembic current

docker exec -it bot psql -h 127.0.0.1 -U postgres -d db_mailing_bot


nginx

sudo nano /etc/nginx/sites-enabled/bot_mailing
sudo nginx -t
sudo systemctl stop nginx
sudo certbot certonly --standalone --preferred-challenges http -d sender-mailing-bot.duckdns.org
sudo nginx -t
sudo systemctl start nginx


sudo cp mailingbot.service /etc/systemd/system
sudo systemctl enable mailingbot.service
sudo systemctl restart mailingbot.service
