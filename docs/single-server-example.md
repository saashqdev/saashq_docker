### Single Server Example

In this use case we have a single server with a static IP attached to it. It can be used in scenarios where one powerful VM has multiple wrenches and applications or one entry level VM with single site. For single wrench, single site setup follow only up to the point where first wrench and first site is added. If you choose this setup you can only scale vertically. If you need to scale horizontally you'll need to backup the sites and restore them on to cluster setup.

We will setup the following:

- Install docker and docker compose v2 on linux server.
- Install traefik service for internal load balancer and letsencrypt.
- Install MariaDB with containers.
- Setup project called `erpnexus-one` and create sites `one.example.com` and `two.example.com` in the project.
- Setup project called `erpnexus-two` and create sites `three.example.com` and `four.example.com` in the project.

Explanation:

Single instance of **Traefik** will be installed and act as internal loadbalancer for multiple wrenches and sites hosted on the server. It can also load balance other applications along with saashq wrenches, e.g. wordpress, metabase, etc. We only expose the ports `80` and `443` once with this instance of traefik. Traefik will also take care of letsencrypt automation for all sites installed on the server. _Why choose Traefik over Nginx Proxy Manager?_ Traefik doesn't need additional DB service and can store certificates in a json file in a volume.

Single instance of **MariaDB** will be installed and act as database service for all the wrenches/projects installed on the server.

Each instance of ERPNexus project (wrench) will have its own redis, socketio, gunicorn, nginx, workers and scheduler. It will connect to internal MariaDB by connecting to MariaDB network. It will expose sites to public through Traefik by connecting to Traefik network.

### Install Docker

Easiest way to install docker is to use the [convenience script](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script).

```shell
curl -fsSL https://get.docker.com | bash
```

Note: The documentation assumes Ubuntu LTS server is used. Use any distribution as long as the docker convenience script works. If the convenience script doesn't work, you'll need to install docker manually.

### Install Compose V2

Refer [original documentation](https://docs.docker.com/compose/cli-command/#install-on-linux) for updated version.

```shell
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

### Prepare

Clone `saashq_docker` repo for the needed YAMLs and change the current working directory of your shell to the cloned repo.

```shell
git clone https://github.com/saashqdev/saashq_docker
cd saashq_docker
```

Create configuration and resources directory

```shell
mkdir ~/gitops
```

The `~/gitops` directory will store all the resources that we use for setup. We will also keep the environment files in this directory as there will be multiple projects with different environment variables. You can create a private repo for this directory and track the changes there.

### Install Traefik

Basic Traefik setup using docker compose.

Create a file called `traefik.env` in `~/gitops`

```shell
echo 'TRAEFIK_DOMAIN=traefik.example.com' > ~/gitops/traefik.env
echo 'EMAIL=admin@example.com' >> ~/gitops/traefik.env
echo 'HASHED_PASSWORD='$(openssl passwd -apr1 changeit | sed -e s/\\$/\\$\\$/g) >> ~/gitops/traefik.env
```

Note:

- Change the domain from `traefik.example.com` to the one used in production. DNS entry needs to point to the Server IP.
- Change the letsencrypt notification email from `admin@example.com` to correct email.
- Change the password from `changeit` to more secure.

env file generated at location `~/gitops/traefik.env` will look like following:

```env
TRAEFIK_DOMAIN=traefik.example.com
EMAIL=admin@example.com
HASHED_PASSWORD=$apr1$K.4gp7RT$tj9R2jHh0D4Gb5o5fIAzm/
```

If Container does not deploy put the HASHED_PASSWORD in ''.

Deploy the traefik container with letsencrypt SSL

```shell
docker compose --project-name traefik \
  --env-file ~/gitops/traefik.env \
  -f overrides/compose.traefik.yaml \
  -f overrides/compose.traefik-ssl.yaml up -d
```

This will make the traefik dashboard available on `traefik.example.com` and all certificates will reside in the Docker volume `cert-data`.

For LAN setup deploy the traefik container without overriding `overrides/compose.traefik-ssl.yaml`.

### Install MariaDB

Basic MariaDB setup using docker compose.

Create a file called `mariadb.env` in `~/gitops`

```shell
echo "DB_PASSWORD=changeit" > ~/gitops/mariadb.env
```

Note:

- Change the password from `changeit` to more secure.

env file generated at location `~/gitops/mariadb.env` will look like following:

```env
DB_PASSWORD=changeit
```

Note: Change the password from `changeit` to more secure one.

Deploy the mariadb container

```shell
docker compose --project-name mariadb --env-file ~/gitops/mariadb.env -f overrides/compose.mariadb-shared.yaml up -d
```

This will make `mariadb-database` service available under `mariadb-network`. Data will reside in `/data/mariadb`.

### Install ERPNexus

#### Create first wrench

Create first wrench called `erpnexus-one` with `one.example.com` and `two.example.com`

Create a file called `erpnexus-one.env` in `~/gitops`

```shell
cp example.env ~/gitops/erpnexus-one.env
sed -i 's/DB_PASSWORD=123/DB_PASSWORD=changeit/g' ~/gitops/erpnexus-one.env
sed -i 's/DB_HOST=/DB_HOST=mariadb-database/g' ~/gitops/erpnexus-one.env
sed -i 's/DB_PORT=/DB_PORT=3306/g' ~/gitops/erpnexus-one.env
sed -i 's/SITES=`erp.example.com`/SITES=\`one.example.com\`,\`two.example.com\`/g' ~/gitops/erpnexus-one.env
echo 'ROUTER=erpnexus-one' >> ~/gitops/erpnexus-one.env
echo "WRENCH_NETWORK=erpnexus-one" >> ~/gitops/erpnexus-one.env
```

Note:

- Change the password from `changeit` to the one set for MariaDB compose in the previous step.

env file is generated at location `~/gitops/erpnexus-one.env`.

Create a yaml file called `erpnexus-one.yaml` in `~/gitops` directory:

```shell
docker compose --project-name erpnexus-one \
  --env-file ~/gitops/erpnexus-one.env \
  -f compose.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.multi-wrench.yaml \
  -f overrides/compose.multi-wrench-ssl.yaml config > ~/gitops/erpnexus-one.yaml
```

For LAN setup do not override `compose.multi-wrench-ssl.yaml`.

Use the above command after any changes are made to `erpnexus-one.env` file to regenerate `~/gitops/erpnexus-one.yaml`. e.g. after changing version to migrate the wrench.

Deploy `erpnexus-one` containers:

```shell
docker compose --project-name erpnexus-one -f ~/gitops/erpnexus-one.yaml up -d
```

Create sites `one.example.com` and `two.example.com`:

```shell
# one.example.com
docker compose --project-name erpnexus-one exec backend \
  wrench new-site --no-mariadb-socket --mariadb-root-password changeit --install-app erpnexus --admin-password changeit one.example.com
```

You can stop here and have a single wrench single site setup complete. Continue to add one more site to the current wrench.

```shell
# two.example.com
docker compose --project-name erpnexus-one exec backend \
  wrench new-site --no-mariadb-socket --mariadb-root-password changeit --install-app erpnexus --admin-password changeit two.example.com
```

#### Create second wrench

Setting up additional wrench is optional. Continue only if you need multi wrench setup.

Create second wrench called `erpnexus-two` with `three.example.com` and `four.example.com`

Create a file called `erpnexus-two.env` in `~/gitops`

```shell
curl -sL https://raw.githubusercontent.com/saashq/saashq_docker/main/example.env -o ~/gitops/erpnexus-two.env
sed -i 's/DB_PASSWORD=123/DB_PASSWORD=changeit/g' ~/gitops/erpnexus-two.env
sed -i 's/DB_HOST=/DB_HOST=mariadb-database/g' ~/gitops/erpnexus-two.env
sed -i 's/DB_PORT=/DB_PORT=3306/g' ~/gitops/erpnexus-two.env
echo "ROUTER=erpnexus-two" >> ~/gitops/erpnexus-two.env
echo "SITES=\`three.example.com\`,\`four.example.com\`" >> ~/gitops/erpnexus-two.env
echo "WRENCH_NETWORK=erpnexus-two" >> ~/gitops/erpnexus-two.env
```

Note:

- Change the password from `changeit` to the one set for MariaDB compose in the previous step.

env file is generated at location `~/gitops/erpnexus-two.env`.

Create a yaml file called `erpnexus-two.yaml` in `~/gitops` directory:

```shell
docker compose --project-name erpnexus-two \
  --env-file ~/gitops/erpnexus-two.env \
  -f compose.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.multi-wrench.yaml \
  -f overrides/compose.multi-wrench-ssl.yaml config > ~/gitops/erpnexus-two.yaml
```

Use the above command after any changes are made to `erpnexus-two.env` file to regenerate `~/gitops/erpnexus-two.yaml`. e.g. after changing version to migrate the wrench.

Deploy `erpnexus-two` containers:

```shell
docker compose --project-name erpnexus-two -f ~/gitops/erpnexus-two.yaml up -d
```

Create sites `three.example.com` and `four.example.com`:

```shell
# three.example.com
docker compose --project-name erpnexus-two exec backend \
  wrench new-site --no-mariadb-socket --mariadb-root-password changeit --install-app erpnexus --admin-password changeit three.example.com
# four.example.com
docker compose --project-name erpnexus-two exec backend \
  wrench new-site --no-mariadb-socket --mariadb-root-password changeit --install-app erpnexus --admin-password changeit four.example.com
```

#### Create custom domain to existing site

In case you need to point custom domain to existing site follow these steps.
Also useful if custom domain is required for LAN based access.

Create environment file

```shell
echo "ROUTER=custom-one-example" > ~/gitops/custom-one-example.env
echo "SITES=\`custom-one.example.com\`" >> ~/gitops/custom-one-example.env
echo "BASE_SITE=one.example.com" >> ~/gitops/custom-one-example.env
echo "WRENCH_NETWORK=erpnexus-one" >> ~/gitops/custom-one-example.env
```

Note:

- Change the file name from `custom-one-example.env` to a logical one.
- Change `ROUTER` variable from `custom-one.example.com` to the one being added.
- Change `SITES` variable from `custom-one.example.com` to the one being added. You can add multiple sites quoted in backtick (`) and separated by commas.
- Change `BASE_SITE` variable from `one.example.com` to the one which is being pointed to.
- Change `WRENCH_NETWORK` variable from `erpnexus-one` to the one which was created with the wrench.

env file is generated at location mentioned in command.

Generate yaml to reverse proxy:

```shell
docker compose --project-name custom-one-example \
  --env-file ~/gitops/custom-one-example.env \
  -f overrides/compose.custom-domain.yaml \
  -f overrides/compose.custom-domain-ssl.yaml config > ~/gitops/custom-one-example.yaml
```

For LAN setup do not override `compose.custom-domain-ssl.yaml`.

Deploy `erpnexus-two` containers:

```shell
docker compose --project-name custom-one-example -f ~/gitops/custom-one-example.yaml up -d
```

### Site operations

Refer: [site operations](./site-operations.md)
