v**Docker / Docker Compose**

This project includes basic containerization for the Flask app.

Files added:
- `Dockerfile` — builds a Docker image for the app and stores the SQLite DB at `/data/db.sqlite`.
- `docker-compose.yml` — starts the `web` service and mounts a named volume `db_data` to `/data`.
- `.dockerignore` — excludes venv and cache files.
- `requirements.txt` — runtime Python dependencies used by the Docker image.

Quick start (Docker Compose):

1. Build and start the service:

```powershell
docker-compose up --build -d
```

2. Open the app in your browser:

```
http://localhost:5000/
```

3. The SQLite DB file is stored in the Docker named volume `db_data` at container path `/data/db.sqlite`. To inspect it you can run a temporary container mounting the volume:

```powershell
# Replace with an interactive shell image if needed
docker run --rm -v laba-5_db_data:/data -it --entrypoint sh alpine
# then inside the container: ls -la /data
```

Stopping and removing containers and volumes:

```powershell
# stop and remove containers
docker-compose down

# remove volumes (this deletes the DB)
docker-compose down -v
```

Notes:
- The app reads the DB file path from the `DB_PATH` environment variable (defaults to `db.sqlite`). In the Compose setup `DB_PATH` is set to `/data/db.sqlite` so the DB persists in the `db_data` volume.
- If you want to run with the DB file on the host filesystem instead of a named volume, change the `volumes` entry in `docker-compose.yml` to a host path, e.g. `- ./data:/data`.

The Docker setup in this repo now includes the following quality improvements:

- multi-stage build in `Dockerfile` to reduce final image size
- healthcheck configured in `docker-compose.yml` (checks HTTP `/`)
- named volume `db_data` mounted at `/data` to persist SQLite DB
- `.env` support (copy `.env.example` to `.env`) via `env_file` in `docker-compose.yml`
- data directory is created and ownership set for a non-root `app` user

Configuration and environment variables
- Copy `.env.example` to `.env` and adjust variables as needed. The following variables are supported:
	- `HOST` (default `0.0.0.0`)
	- `PORT` (default `5000`)
	- `DB_PATH` (default `/data/db.sqlite` in the container)

Usage reminders
- Build and start the service:

```powershell
docker-compose up --build -d
```

- To stop and remove containers and the volume (deletes DB):

```powershell
docker-compose down -v
```

Advanced notes
- If you prefer mounting the DB on the host filesystem, edit `docker-compose.yml` and replace the `db_data` volume with a host path such as `- ./data:/data`.
- The image runs as a non-root `app` user and the `/data` directory is chown'd appropriately during build.

If you want, I can add:
- pinned dependency versions in `requirements.txt` and a lock-step workflow for deterministic builds,
- an entrypoint script that runs DB initialization/seed on first start,
- or a `Makefile` / PowerShell helper for common Docker commands.

Мови проєкту
------------

Короткі деталі про основні мови та технології, що застосовуються в цьому репозиторії:

- **Python (Flask)**
	- Роль: серверна логіка, маршрути, API, робота з БД.
	- Ключові файли/папки: `app.py`, `models.py`, `init_db.py`, `seed_data.py`, `routes/`, `tests/`.
	- Рекомендації: використовувати Python 3.10–3.12, фіксувати залежності у `requirements.txt`/`requirements-dev.txt`, запускати тести через `pytest`.

- **HTML / Jinja2 (шаблони)**
	- Роль: генерація сторінок на сервері, шаблони знаходяться в `templates/`.
	- Порада: великі або повторювані скрипти винести у `static/`.

- **Tailwind CSS / CSS**
	- Роль: стилі інтерфейсу (утилітарні класи у шаблонах). Може підключатися через CDN або локальну збірку.
	- Порада: для кастомізації і оптимізації у продакшн розгляньте локальну збірку Tailwind з purge/optimize кроком.

- **JavaScript**
	- Роль: клієнтська логіка (пошук, динаміка карток, AJAX). Часто скрипти розміщені прямо в шаблонах (`templates/home.html`, `templates/shop.html`).
	- Порада: для підтримки та продуктивності винесіть в `static/js/` і мінімізуйте файли у продакшн.

- **SQL / SQLite**
	- Роль: зберігання даних у локальному файлі БД (шлях визначається `DB_PATH`).
	- Примітка: SQLite чудово підходить для локального розвитку та невеликих проєктів; для масштабування розгляньте PostgreSQL або MySQL.

- **Shell / PowerShell / Batch**
	- Роль: скрипти запуску та бекапу (e.g., `run-dev.ps1`, `run-dev.bat`, `scripts/backup_db.sh`).

- **Docker / YAML**
	- Роль: контейнеризація та оркестрація (`Dockerfile`, `docker-compose.yml`, `docker-compose.prod.yml`).
	- Порада: використовуємо multi-stage збірку, healthcheck та non-root `app` user.

- **Nginx**
	- Роль: конфігурація реверс-проксі у продакшн (`nginx/nginx.conf`).

- **JSON / Інші формати**
	- Роль: `Postman_Collection.json` для тестування API, Markdown для документації (`DOCKER.md`, `TESTING.md`).

Архітектура
----------

- `web` service: the Flask application container. Runs as non-root `app` user, serves HTTP on port 5000 inside the bridge network.
- `nginx` (production): reverse-proxy in front of `web`, terminates connections and forwards requests. Useful for TLS termination and static file caching.
- `db_data` volume: named docker volume that persists SQLite DB file across container restarts and recreations.

Logging
-------

Docker Compose configures `json-file` logging with rotation in both dev and prod compose files. You can view logs with:

```powershell
docker-compose logs -f web
docker-compose logs -f nginx
```

For centralized logging in production, configure the `logging.driver` to `syslog`, `fluentd` or another supported driver and provide driver options in `docker-compose.prod.yml`.

Backup strategy
---------------

The repository includes `scripts/backup_db.sh` which copies the `db.sqlite` file from the named volume `laba-5_db_data` to a `backups/` directory on the host with a timestamp. Use a host cron job or CI job to run this script periodically. Example:

```bash
# run once
./scripts/backup_db.sh

# add to crontab (daily at 2AM)
0 2 * * * cd /path/to/project && /path/to/project/scripts/backup_db.sh
```

Alternatively, you can mount `./backups:/backup` in a scheduled container and use the `docker run` approach shown in the script.

Troubleshooting
---------------

- Container fails to start: check `docker-compose logs web` and `docker-compose ps` for exit codes. If the app fails due to missing dependencies, ensure you rebuilt the image after changing `requirements.txt`.
- Healthcheck failing: `docker inspect --format='{{json .State.Health}}' <container>` shows recent checks. If healthcheck times out, ensure the app starts and listens on `0.0.0.0:5000`.
- Unable to access from host: check port mapping (`docker-compose ps`), host firewall, and that `HOST`/`PORT` env vars are correctly set.
- File permission issues writing DB: ensure the volume is owned by the `app` user inside the container. If using host bind mount (`./data:/data`), set appropriate permissions on the host: `chown -R 1000:1000 ./data` (1000 is typical UID for the app user in container). If necessary, adjust `Dockerfile` to match host UID.

Commands summary
----------------

- Development (mounts source, live reload if you use a watcher):

```powershell
docker-compose up --build
```

- Production (build image + run with nginx):

```powershell
docker-compose -f docker-compose.prod.yml up --build -d
```

If you'd like, I can:
- add a small `entrypoint.sh` to initialize or seed the DB on first start,
- make the backup service run as a scheduled container (using `crond` image) inside compose,
- or configure a logging driver for remote log collection (e.g., `fluentd`) and show example setup.
