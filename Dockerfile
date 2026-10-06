# syntax=docker/dockerfile:1

FROM node:24-bookworm-slim AS node

FROM python:3.14-slim-bookworm

ARG FRAPPE_BRANCH=develop
ARG FRAPPE_REF
ARG BENCH_PATH=/home/frappe/frappe-bench

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/home/frappe/.local/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Frappe runtime libraries plus the compilers needed by its Python packages.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        cron \
        curl \
        git \
        libffi-dev \
        libjpeg62-turbo-dev \
        libldap2-dev \
        libmariadb-dev \
        libmariadb-dev-compat \
        libpq-dev \
        libsasl2-dev \
        libssl-dev \
        mariadb-client \
        pkg-config \
        redis-server \
        wkhtmltopdf \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Keep Node aligned with this repository's CI configuration.
COPY --from=node /usr/local/ /usr/local/

RUN rm -f /usr/local/bin/yarn /usr/local/bin/yarnpkg \
    && npm install --global yarn@1.22.22 \
    && pip install --no-cache-dir frappe-bench \
    && useradd --create-home --shell /bin/bash frappe

USER frappe
WORKDIR /home/frappe

# ERPNext 17-develop requires the matching Frappe development branch.
RUN bench init \
        --frappe-branch "${FRAPPE_BRANCH}" \
        --python python3 \
        --skip-assets \
        "${BENCH_PATH}"

WORKDIR ${BENCH_PATH}

# VPS releases pass a tested commit instead of following a moving branch.
RUN if [ -n "${FRAPPE_REF}" ]; then \
        git -C apps/frappe fetch --depth 1 https://github.com/frappe/frappe.git "${FRAPPE_REF}" \
        && git -C apps/frappe checkout "${FRAPPE_REF}" \
        && ./env/bin/pip install --no-cache-dir --editable ./apps/frappe \
        && yarn --cwd apps/frappe install --frozen-lockfile; \
    fi

# Use the application source from this repository instead of fetching ERPNext.
COPY --chown=frappe:frappe . apps/erpnext
COPY --chown=frappe:frappe apps/atlas_erp apps/atlas_erp

RUN printf 'frappe\nerpnext\natlas_erp\n' > sites/apps.txt \
    && ./env/bin/pip install --no-cache-dir --editable ./apps/erpnext --editable ./apps/atlas_erp \
    && yarn --cwd apps/erpnext install --frozen-lockfile \
    && bench build --apps frappe,erpnext,atlas_erp \
    && find apps -type d -name node_modules -prune -o \
        -type d -name __pycache__ -prune -exec rm -rf '{}' +

EXPOSE 8000 9000

CMD ["bench", "start"]
