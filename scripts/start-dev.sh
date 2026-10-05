#!/usr/bin/env bash
set -euo pipefail

# Configure external services; bench start must not spawn additional Redis servers.
printf 'frappe\nerpnext\natlas_erp\n' > sites/apps.txt
bench set-config -g db_host db
bench set-config -g db_port 3306
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379
bench set-config -gp socketio_port 9000

# The ERPNext package is mounted from the host. Its generated assets therefore
# need building once into that mount, using dependencies installed in the image.
if [[ ! -d apps/erpnext/erpnext/public/dist ]]; then
  bench build --apps frappe,erpnext,atlas_erp
fi

if [[ ! -f "sites/${ATLAS_SITE}/site_config.json" ]]; then
  bench new-site "$ATLAS_SITE" \
    --db-root-username root \
    --db-root-password "$DB_ROOT_PASSWORD" \
    --mariadb-user-host-login-scope='%' \
    --admin-password "$ADMIN_PASSWORD"
fi

# Re-running these commands is safe for already installed apps and also lets a
# partially completed installation resume without deleting a site or database.
bench --site "$ATLAS_SITE" install-app erpnext
bench --site "$ATLAS_SITE" install-app atlas_erp
bench --site "$ATLAS_SITE" set-config developer_mode 1
bench use "$ATLAS_SITE"

cat > Procfile <<'EOF'
web: bench serve --host 0.0.0.0 --port 8000
socketio: bench socketio
schedule: bench schedule
worker: bench worker --queue short,default,long
EOF

exec bench start
