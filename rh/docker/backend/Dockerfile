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
