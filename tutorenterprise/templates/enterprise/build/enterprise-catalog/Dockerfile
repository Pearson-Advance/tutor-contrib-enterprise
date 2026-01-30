###### Minimal image with base system requirements for most stages.
FROM docker.io/ubuntu:24.04 as minimal
RUN apt update && \
    apt install -y curl git-core language-pack-en

###### Install python and virtual environment.
FROM minimal as python
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv python3-dev \
        build-essential \
        pkg-config libmysqlclient-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*
ENV LC_ALL en_US.UTF-8

# From then on, run as unprivileged "app" user
# Note that this must always be different from root (APP_USER_ID=0)
ARG APP_USER_ID=1000
RUN if [ "$APP_USER_ID" = 0 ]; then echo "app user may not be root" && false; fi
RUN useradd --no-log-init --home-dir /openedx --create-home --shell /bin/bash --uid ${APP_USER_ID} app
USER ${APP_USER_ID}

###### Checkout code.
ARG ENTERPRISE_CATALOG_REPOSITORY={{ ENTERPRISE_CATALOG_REPOSITORY }}
ARG ENTERPRISE_CATALOG_VERSION={{ ENTERPRISE_CATALOG_GIT_VERSION }}
RUN mkdir -p /openedx/enterprise_catalog && \
    git clone $ENTERPRISE_CATALOG_REPOSITORY --branch $ENTERPRISE_CATALOG_VERSION --depth 1 /openedx/enterprise-catalog

# Install python venv.
FROM python as python-virtualenv
RUN python3 -m venv /openedx/venv/
ENV PATH "/openedx/venv/bin:$PATH"
RUN pip install \
    # https://pypi.org/project/setuptools/
    # https://pypi.org/project/pip/
    # https://pypi.org/project/wheel/
    setuptools==80.9.0 pip==25.3 wheel==0.45.1
WORKDIR /openedx/enterprise-catalog

# Install base requirements.
RUN pip install -r ./requirements/production.txt
# Install django-redis for using redis as a django cache.
# https://pypi.org/project/django-redis/
RUN pip install django-redis==5.4.0
# Install uwsgi.
# https://pypi.org/project/uWSGI/
RUN pip install uwsgi==2.0.31

# Collect static assets.
COPY --chown=app:app assets.py ./enterprise_catalog/settings/assets.py
RUN DJANGO_SETTINGS_MODULE=enterprise_catalog.settings.assets make static

# Setup minimal yml config file, which is required by production settings.
RUN echo "{}" > /openedx/config.yml
ENV ENTERPRISE_CATALOG_CFG /openedx/config.yml

# Run production server.
ENV DJANGO_SETTINGS_MODULE enterprise_catalog.settings.tutor.production
EXPOSE 8000
CMD uwsgi \
    --static-map /static=/openedx/enterprise-catalog/enterprise_catalog/assets \
    --static-map /media=/openedx/enterprise-catalog/enterprise_catalog/media \
    --http 0.0.0.0:8000 \
    --thunder-lock \
    --single-interpreter \
    --enable-threads \
    --processes=2 \
    --buffer-size=8192 \
    --wsgi-file enterprise_catalog/wsgi.py
