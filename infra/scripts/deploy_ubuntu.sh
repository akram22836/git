#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy_ubuntu.sh <DOMAIN_OR_IP>
# This script installs Docker, pulls/builds containers, runs migrations, and starts services.

DOMAIN_OR_IP=${1:-localhost}

if ! command -v docker &>/dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
fi

if ! command -v docker-compose &>/dev/null; then
  echo "Installing docker-compose plugin..."
  mkdir -p ~/.docker/cli-plugins
  curl -SL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
  chmod +x ~/.docker/cli-plugins/docker-compose
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

pushd "$REPO_ROOT/infra" >/dev/null

# Copy example env for backend if missing
if [ ! -f "$REPO_ROOT/backend/.env" ]; then
  cp "$REPO_ROOT/backend/.env.example" "$REPO_ROOT/backend/.env"
fi

docker compose pull || true

docker compose build

docker compose up -d db

# Wait for Postgres to be ready
echo "Waiting for Postgres..."
RETRIES=30
until docker compose exec -T db pg_isready -U acct_user -d accounting || [ $RETRIES -eq 0 ]; do
  sleep 2
  RETRIES=$((RETRIES-1))
  echo "..."
done

# Run Alembic migrations
docker compose run --rm backend bash -lc "alembic upgrade head"

# Start backend
docker compose up -d backend

popd >/dev/null

echo "Deployment completed. Backend at http://$DOMAIN_OR_IP:8000/docs"
