# How to install ERPNexus on linux/mac using Saashq_docker ?

step1: clone the repo

```
git clone https://github.com/saashqdev/saashq_docker
```

step2: add platform: linux/amd64 to all services in the /pwd.yaml

here is the update pwd.yml file

```yml
version: "3"

services:
  backend:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs

  configurator:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: none
    entrypoint:
      - bash
      - -c
    # add redis_socketio for backward compatibility
    command:
      - >
        ls -1 apps > sites/apps.txt;
        wrench set-config -g db_host $$DB_HOST;
        wrench set-config -gp db_port $$DB_PORT;
        wrench set-config -g redis_cache "redis://$$REDIS_CACHE";
        wrench set-config -g redis_queue "redis://$$REDIS_QUEUE";
        wrench set-config -g redis_socketio "redis://$$REDIS_QUEUE";
        wrench set-config -gp socketio_port $$SOCKETIO_PORT;
    environment:
      DB_HOST: db
      DB_PORT: "3306"
      REDIS_CACHE: redis-cache:6379
      REDIS_QUEUE: redis-queue:6379
      SOCKETIO_PORT: "9000"
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs

  create-site:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: none
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs
    entrypoint:
      - bash
      - -c
    command:
      - >
        wait-for-it -t 120 db:3306;
        wait-for-it -t 120 redis-cache:6379;
        wait-for-it -t 120 redis-queue:6379;
        export start=`date +%s`;
        until [[ -n `grep -hs ^ sites/common_site_config.json | jq -r ".db_host // empty"` ]] && \
          [[ -n `grep -hs ^ sites/common_site_config.json | jq -r ".redis_cache // empty"` ]] && \
          [[ -n `grep -hs ^ sites/common_site_config.json | jq -r ".redis_queue // empty"` ]];
        do
          echo "Waiting for sites/common_site_config.json to be created";
          sleep 5;
          if (( `date +%s`-start > 120 )); then
            echo "could not find sites/common_site_config.json with required keys";
            exit 1
          fi
        done;
        echo "sites/common_site_config.json found";
        wrench new-site --no-mariadb-socket --admin-password=admin --db-root-password=admin --install-app erpnexus --set-default frontend;

  db:
    image: mariadb:10.6
    platform: linux/amd64
    healthcheck:
      test: mysqladmin ping -h localhost --password=admin
      interval: 1s
      retries: 20
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --skip-character-set-client-handshake
      - --skip-innodb-read-only-compressed # Temporary fix for MariaDB 10.6
    environment:
      MYSQL_ROOT_PASSWORD: admin
    volumes:
      - db-data:/var/lib/mysql

  frontend:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    depends_on:
      - websocket
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - nginx-entrypoint.sh
    environment:
      BACKEND: backend:8000
      SAASHQ_SITE_NAME_HEADER: frontend
      SOCKETIO: websocket:9000
      UPSTREAM_REAL_IP_ADDRESS: 127.0.0.1
      UPSTREAM_REAL_IP_HEADER: X-Forwarded-For
      UPSTREAM_REAL_IP_RECURSIVE: "off"
      PROXY_READ_TIMEOUT: 120
      CLIENT_MAX_BODY_SIZE: 50m
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs
    ports:
      - "8080:8080"

  queue-long:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - wrench
      - worker
      - --queue
      - long,default,short
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs

  queue-short:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - wrench
      - worker
      - --queue
      - short,default
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs

  redis-queue:
    image: redis:6.2-alpine
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    volumes:
      - redis-queue-data:/data

  redis-cache:
    image: redis:6.2-alpine
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    volumes:
      - redis-cache-data:/data

  scheduler:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - wrench
      - schedule
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs

  websocket:
    image: saashqdev/erpnexus:v15
    platform: linux/amd64
    deploy:
      restart_policy:
        condition: on-failure
    command:
      - node
      - /home/saashq/saashq-wrench/apps/saashq/socketio.js
    volumes:
      - sites:/home/saashq/saashq-wrench/sites
      - logs:/home/saashq/saashq-wrench/logs

volumes:
  db-data:
  redis-queue-data:
  redis-cache-data:
  sites:
  logs:
```

step3: run the docker

```
cd saashq_docker
```

```
docker-compose -f ./pwd.yml up
```

---

Wait for couple of minutes.

Open localhost:8080
