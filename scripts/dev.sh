#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

case "${1:-help}" in
  init)
    if [[ -f .env ]]; then
      echo '.env already exists; preserving its settings.'
      exit 0
    fi
    umask 077
    db_password=$(openssl rand -hex 24)
    admin_password=$(openssl rand -hex 16)
    cat > .env <<EOF
ATLAS_HTTP_PORT=8000
ATLAS_SOCKETIO_PORT=9000
ATLAS_SITE=atlas.localhost
FRAPPE_BRANCH=develop
DB_ROOT_PASSWORD=$db_password
ADMIN_PASSWORD=$admin_password
EOF
    echo 'Created private .env. Administrator password is stored there.'
    ;;
  up) docker compose up -d --build ;;
  stop) docker compose stop ;;
  logs) docker compose logs --tail=80 -f app ;;
  status) docker compose ps ;;
  bench) shift; docker compose exec app bench "$@" ;;
  *) echo 'Usage: bash scripts/dev.sh {init|up|stop|logs|status|bench <arguments>}' ;;
esac
