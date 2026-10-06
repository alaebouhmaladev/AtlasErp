#!/usr/bin/env bash
set -euo pipefail
printf 'frappe\nerpnext\natlas_erp\n' > sites/apps.txt
for atlas_optional_app in hrms whatsapp crm; do
    if [[ -d "apps/${atlas_optional_app}" ]]; then
        printf '%s\n' "$atlas_optional_app" >> sites/apps.txt
    fi
done
bench set-config -g db_host db
bench set-config -gp db_port 3306
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379
bench set-config -gp socketio_port 9000
bench set-config -g webserver_host backend
bench set-config -gp webserver_port 8000
if [[ ! -f "sites/${ATLAS_SITE}/site_config.json" ]]; then
    bench new-site "$ATLAS_SITE" --db-root-username root \
        --db-root-password "$DB_ROOT_PASSWORD" --mariadb-user-host-login-scope='%' \
        --admin-password "$ADMIN_PASSWORD"
fi
bench --site "$ATLAS_SITE" install-app erpnext
bench --site "$ATLAS_SITE" install-app atlas_erp
for atlas_optional_app in ${ATLAS_EXTRA_APPS:-}; do
    case "$atlas_optional_app" in
        hrms|whatsapp|crm) bench --site "$ATLAS_SITE" install-app "$atlas_optional_app" ;;
        *) printf 'Unsupported extra app: %s\n' "$atlas_optional_app" >&2; exit 1 ;;
    esac
done
bench --site "$ATLAS_SITE" set-config developer_mode 0
bench --site "$ATLAS_SITE" set-config host_name "https://${ATLAS_SITE}"
bench --site "$ATLAS_SITE" migrate
bench --site "$ATLAS_SITE" enable-scheduler
bench use "$ATLAS_SITE"
