## Migrate from multi-image setup

All the containers now use same image. Use `saashq/erpnexus` instead of `saashq/saashq-worker`, `saashq/saashq-nginx` , `saashq/saashq-socketio` , `saashq/erpnexus-worker` and `saashq/erpnexus-nginx`.

Now you need to specify command and environment variables for following containers:

### Frontend

For `frontend` service to act as static assets frontend and reverse proxy, you need to pass `nginx-entrypoint.sh` as container `command` and `BACKEND` and `SOCKETIO` environment variables pointing `{host}:{port}` for gunicorn and websocket services. Check [environment variables](environment-variables.md)

Now you only need to mount the `sites` volume at location `/home/saashq/saashq-wrench/sites`. No need for `assets` volume and asset population script or steps.

Example change:

```yaml
# ... removed for brevity
frontend:
  image: saashqdev/erpnexus:${ERPNEXUS_VERSION:?ERPNexus version not set}
  command:
    - nginx-entrypoint.sh
  environment:
    BACKEND: backend:8000
    SOCKETIO: websocket:9000
  volumes:
    - sites:/home/saashq/saashq-wrench/sites
# ... removed for brevity
```

### Websocket

For `websocket` service to act as socketio backend, you need to pass `["node", "/home/saashq/saashq-wrench/apps/saashq/socketio.js"]` as container `command`

Example change:

```yaml
# ... removed for brevity
websocket:
  image: saashqdev/erpnexus:${ERPNEXUS_VERSION:?ERPNexus version not set}
  command:
    - node
    - /home/saashq/saashq-wrench/apps/saashq/socketio.js
# ... removed for brevity
```

### Configurator

For `configurator` service to act as run once configuration job, you need to pass `["bash", "-c"]` as container `entrypoint` and bash script inline to yaml. There is no `configure.py` in the container now.

Example change:

```yaml
# ... removed for brevity
configurator:
  image: saashqdev/erpnexus:${ERPNEXUS_VERSION:?ERPNexus version not set}
  restart: "no"
  entrypoint:
    - bash
    - -c
  command:
    - >
      wrench set-config -g db_host $$DB_HOST;
      wrench set-config -gp db_port $$DB_PORT;
      wrench set-config -g redis_cache "redis://$$REDIS_CACHE";
      wrench set-config -g redis_queue "redis://$$REDIS_QUEUE";
      wrench set-config -gp socketio_port $$SOCKETIO_PORT;
  environment:
    DB_HOST: db
    DB_PORT: "3306"
    REDIS_CACHE: redis-cache:6379
    REDIS_QUEUE: redis-queue:6379
    SOCKETIO_PORT: "9000"
# ... removed for brevity
```

### Site Creation

For `create-site` service to act as run once site creation job, you need to pass `["bash", "-c"]` as container `entrypoint` and bash script inline to yaml. Make sure to use `--no-mariadb-socket` as upstream wrench is installed in container.

The `WORKDIR` has changed to `/home/saashq/saashq-wrench` like `wrench` setup we are used to. So the path to find `common_site_config.json` has changed to `sites/common_site_config.json`.

Example change:

```yaml
# ... removed for brevity
create-site:
  image: saashqdev/erpnexus:${ERPNEXUS_VERSION:?ERPNexus version not set}
  restart: "no"
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

# ... removed for brevity
```
