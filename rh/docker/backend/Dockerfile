# syntax=docker/dockerfile:1
FROM python:3.11.5
WORKDIR /app

# Install system dependencies for python-ldap
RUN apt-get update && apt-get install -y \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install gunicorn
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

ADD . /app/backend
ADD ./docker /app/docker

RUN sed -i 's/\r$//' /app/docker/backend/server-entrypoint.sh /app/docker/backend/worker-entrypoint.sh
RUN chmod +x /app/docker/backend/server-entrypoint.sh
RUN chmod +x /app/docker/backend/worker-entrypoint.sh

# Pré-collecte des assets dans l'image (secours si entrypoint échoue).
WORKDIR /app/backend
ENV DJANGO_SETTINGS_MODULE=payday.settings
ENV SECRET_KEY=build-collectstatic-only
ENV DATABASE_URL=sqlite:////tmp/onip-build.sqlite3
ENV DEBUG=0
ENV WHITENOISE_USE_FINDERS=1
RUN python manage.py collectstatic --noinput || \
    (mkdir -p staticfiles && cp -a static/. staticfiles/)
