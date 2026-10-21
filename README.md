# docker-nginx-mysql-stack

A small three-tier web stack run with Docker Compose: **Nginx** as a reverse proxy, a **Python (Flask + Gunicorn)** app, and a **MySQL 8** database.

It mirrors the shape of a typical production deployment (proxy in front, app in the middle, database kept private) at a size you can run on a laptop.

## Architecture

```
            :8080
  Browser ────────► Nginx ──────► App (Gunicorn :5000) ──────► MySQL :3306
                  [frontend network]          [backend network, internal only]
```

- **Nginx** is the only container that publishes a port. It adds basic security headers and hides its version.
- **App** sits on both networks so it can reach Nginx and the database.
- **MySQL** is on an `internal` network with no published port, so it cannot be reached from outside Docker.
- Every service has a **health check**, and `depends_on` waits for the service below to be healthy before starting.

## Run it

```bash
git clone https://github.com/njjtlauji/docker-nginx-mysql-stack.git
cd docker-nginx-mysql-stack

cp .env.example .env      # then edit the passwords
docker compose up -d --build
docker compose ps         # all three should show "healthy"
```

Then open:

- http://localhost:8080/ : records a visit and returns the total count
- http://localhost:8080/health : app and database health
- http://localhost:8080/nginx-health : Nginx only

```bash
$ curl -s localhost:8080/
{"message":"Hello from Docker + Nginx + MySQL","visits":3}
```

## Useful commands

```bash
docker compose logs -f app          # follow app logs
docker compose exec db mysql -u root -p   # open a MySQL shell
docker compose down                 # stop (keeps the database volume)
docker compose down -v              # stop and delete the data
```

## Back up the database

```bash
docker compose exec db sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --single-transaction "$MYSQL_DATABASE"' \
  | gzip > backup-$(date +%F).sql.gz
```

## Security choices

- Secrets live in `.env`, which is git-ignored. Only `.env.example` is committed.
- The app container runs as a **non-root** user.
- The database has no published port and sits on an internal-only network.
- Image versions are pinned (`nginx:1.27-alpine`, `mysql:8.4`, `python:3.12-slim`) so builds are repeatable.

## What I'd add next

- HTTPS with Let's Encrypt (or Cloudflare in front)
- A CI pipeline (GitHub Actions) that builds the image and runs a smoke test on every push
- Centralised logs and metrics with Prometheus and Grafana
