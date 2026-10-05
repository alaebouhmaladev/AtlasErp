#!/usr/bin/env bash
set -euo pipefail
printf 'frappe\nerpnext\natlas_erp\n' > sites/apps.txt
bench set-config -g db_host db
bench set-config -gp db_port 3306
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379
bench set-config -gp socketio_port 9000
if [[ ! -f "sites/${ATLAS_SITE}/site_config.json" ]]; then
    bench new-site "$ATLAS_SITE" --db-root-username root \
        --db-root-password "$DB_ROOT_PASSWORD" --mariadb-user-host-login-scope='%' \
        --admin-password "$ADMIN_PASSWORD"
fi
bench --site "$ATLAS_SITE" install-app erpnext
bench --site "$ATLAS_SITE" install-app atlas_erp
bench --site "$ATLAS_SITE" set-config developer_mode 0
bench --site "$ATLAS_SITE" set-config host_name "https://${ATLAS_SITE}"
bench --site "$ATLAS_SITE" migrate
bench --site "$ATLAS_SITE" enable-scheduler
bench use "$ATLAS_SITE"
