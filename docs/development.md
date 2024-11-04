# Getting Started

## Prerequisites

In order to start developing you need to satisfy the following prerequisites:

- Docker
- docker-compose
- user added to docker group

It is recommended you allocate at least 4GB of RAM to docker:

- [Instructions for Windows](https://docs.docker.com/docker-for-windows/#resources)
- [Instructions for macOS](https://docs.docker.com/desktop/settings/mac/#advanced)

Here is a screenshot showing the relevant setting in the Help Manual
![image](images/Docker%20Manual%20Screenshot%20-%20Resources%20section.png)
Here is a screenshot showing the settings in Docker Desktop on Mac
![images](images/Docker%20Desktop%20Screenshot%20-%20Resources%20section.png)

## Bootstrap Containers for development

Clone and change directory to saashq_docker directory

```shell
git clone https://github.com/saashqdev/saashq_docker.git
cd saashq_docker
```

Copy example devcontainer config from `devcontainer-example` to `.devcontainer`

```shell
cp -R devcontainer-example .devcontainer
```

Copy example vscode config for devcontainer from `development/vscode-example` to `development/.vscode`. This will setup basic configuration for debugging.

```shell
cp -R development/vscode-example development/.vscode
```

## Use VSCode Remote Containers extension

For most people getting started with Saashq development, the best solution is to use [VSCode Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

Before opening the folder in container, determine the database that you want to use. The default is MariaDB.
If you want to use PostgreSQL instead, edit `.devcontainer/docker-compose.yml` and uncomment the section for `postgresql` service, and you may also want to comment `mariadb` as well.

VSCode should automatically inquire you to install the required extensions, that can also be installed manually as follows:

- Install Dev Containers for VSCode
  - through command line `code --install-extension ms-vscode-remote.remote-containers`
  - clicking on the Install button in the Vistual Studio Marketplace: [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  - View: Extensions command in VSCode (Windows: Ctrl+Shift+X; macOS: Cmd+Shift+X) then search for extension `ms-vscode-remote.remote-containers`

After the extensions are installed, you can:

- Open saashq_docker folder in VS Code.
  - `code .`
- Launch the command, from Command Palette (Ctrl + Shift + P) `Dev Containers: Reopen in Container`. You can also click in the bottom left corner to access the remote container menu.

Notes:

- The `development` directory is ignored by git. It is mounted and available inside the container. Create all your wrenches (installations of wrench, the tool that manages saashq) inside this directory.
- Node v14 and v10 are installed. Check with `nvm ls`. Node v14 is used by default.

### Setup first wrench

> Jump to [scripts](#setup-wrench--new-site-using-script) section to setup a wrench automatically. Alternatively, you can setup a wrench manually using below guide.

Run the following commands in the terminal inside the container. You might need to create a new terminal in VSCode.

NOTE: Prior to doing the following, make sure the user is **saashq**.

```shell
wrench init --skip-redis-config-generation saashq-wrench
cd saashq-wrench
```

To setup saashq framework version 14 wrench set `PYENV_VERSION` environment variable to `3.10.5` (default) and use NodeJS version 16 (default),

```shell
# Use default environments
wrench init --skip-redis-config-generation --saashq-branch main saashq-wrench
# Or set environment versions explicitly
nvm use v16
PYENV_VERSION=3.10.13 wrench init --skip-redis-config-generation --saashq-branch main saashq-wrench
# Switch directory
cd saashq-wrench
```

To setup saashq framework version 13 wrench set `PYENV_VERSION` environment variable to `3.9.17` and use NodeJS version 14,

```shell
nvm use v14
PYENV_VERSION=3.9.17 wrench init --skip-redis-config-generation --saashq-branch main saashq-wrench
cd saashq-wrench
```

### Setup hosts

We need to tell wrench to use the right containers instead of localhost. Run the following commands inside the container:

```shell
wrench set-config -g db_host mariadb
wrench set-config -g redis_cache redis://redis-cache:6379
wrench set-config -g redis_queue redis://redis-queue:6379
wrench set-config -g redis_socketio redis://redis-queue:6379
```

For any reason the above commands fail, set the values in `common_site_config.json` manually.

```json
{
  "db_host": "mariadb",
  "redis_cache": "redis://redis-cache:6379",
  "redis_queue": "redis://redis-queue:6379",
  "redis_socketio": "redis://redis-queue:6379"
}
```

### Edit Honcho's Procfile

Note : With the option '--skip-redis-config-generation' during wrench init, these actions are no more needed. But at least, take a look to ProcFile to see what going on when wrench launch honcho on start command

Honcho is the tool used by Wrench to manage all the processes Saashq requires. Usually, these all run in localhost, but in this case, we have external containers for Redis. For this reason, we have to stop Honcho from trying to start Redis processes.

Honcho is installed in global python environment along with wrench. To make it available locally you've to install it in every `saashq-wrench/env` you create. Install it using command `./env/bin/pip install honcho`. It is required locally if you wish to use is as part of VSCode launch configuration.

Open the Procfile file and remove the three lines containing the configuration from Redis, either by editing manually the file:

```shell
code Procfile
```

Or running the following command:

```shell
sed -i '/redis/d' ./Procfile
```

### Create a new site with wrench

You can create a new site with the following command:

```shell
wrench new-site --no-mariadb-socket sitename
```

sitename MUST end with .localhost for trying deployments locally.

for example:

```shell
wrench new-site --no-mariadb-socket development.localhost
```

The same command can be run non-interactively as well:

```shell
wrench new-site --mariadb-root-password 123 --admin-password admin --no-mariadb-socket development.localhost
```

The command will ask the MariaDB root password. The default root password is `123`.
This will create a new site and a `development.localhost` directory under `saashq-wrench/sites`.
The option `--no-mariadb-socket` will configure site's database credentials to work with docker.
You may need to configure your system /etc/hosts if you're on Linux, Mac, or its Windows equivalent.

To setup site with PostgreSQL as database use option `--db-type postgres` and `--db-host postgresql`. (Available only v12 onwards, currently NOT available for ERPNexus).

Example:

```shell
wrench new-site --db-type postgres --db-host postgresql mypgsql.localhost
```

To avoid entering postgresql username and root password, set it in `common_site_config.json`,

```shell
wrench config set-common-config -c root_login postgres
wrench config set-common-config -c root_password '"123"'
```

Note: If PostgreSQL is not required, the postgresql service / container can be stopped.

### Set wrench developer mode on the new site

To develop a new app, the last step will be setting the site into developer mode. Documentation is available at [this link](https://saashq.io/docs/user/en/guides/app-development/how-enable-developer-mode-in-saashq).

```shell
wrench --site development.localhost set-config developer_mode 1
wrench --site development.localhost clear-cache
```

### Install an app

To install an app we need to fetch it from the appropriate git repo, then install in on the appropriate site:

You can check [VSCode container remote extension documentation](https://code.visualstudio.com/docs/remote/containers#_sharing-git-credentials-with-your-container) regarding git credential sharing.

To install custom app

```shell
# --branch is optional, use it to point to branch on custom app repository
wrench get-app --branch main https://github.com/myusername/myapp
wrench --site development.localhost install-app myapp
```

At the time of this writing, the Payments app has been factored out of the Version 14 ERPNexus app and is now a separate app. ERPNexus will not install it.

```shell
wrench get-app --branch main --resolve-deps erpnexus
wrench --site development.localhost install-app erpnexus
```

To install ERPNexus (from the version-13 branch):

```shell
wrench get-app --branch main erpnexus
wrench --site development.localhost install-app erpnexus
```

Note: Both saashq and erpnexus must be on branch with same name. e.g. version-14

### Start Saashq without debugging

Execute following command from the `saashq-wrench` directory.

```shell
wrench start
```

You can now login with user `Administrator` and the password you choose when creating the site.
Your website will now be accessible at location [development.localhost:8000](http://development.localhost:8000)
Note: To start wrench with debugger refer section for debugging.

### Setup wrench / new site using script

Most developers work with numerous clients and versions. Moreover, apps may be required to be installed by everyone on the team working for a client.

This is simplified using a script to automate the process of creating a new wrench / site and installing the required apps. `Administrator` password is for created sites is `admin`.

Sample `apps-example.json` is used by default, it installs erpnexus on current stable release. To install custom apps, copy the `apps-example.json` to custom json file and make changes to list of apps. Pass this file to the `installer.py` script.

> You may have apps in private repos which may require ssh access. You may use SSH from your home directory on linux (configurable in docker-compose.yml).

```shell
python installer.py  #pass --db-type postgres for postgresdb
```

For command help

```shell
python installer.py --help
usage: installer.py [-h] [-j APPS_JSON] [-b WRENCH_NAME] [-s SITE_NAME] [-r SAASHQ_REPO] [-t SAASHQ_BRANCH] [-p PY_VERSION] [-n NODE_VERSION] [-v] [-a ADMIN_PASSWORD] [-d DB_TYPE]

options:
  -h, --help            show this help message and exit
  -j APPS_JSON, --apps-json APPS_JSON
                        Path to apps.json, default: apps-example.json
  -b WRENCH_NAME, --wrench-name WRENCH_NAME
                        Wrench directory name, default: saashq-wrench
  -s SITE_NAME, --site-name SITE_NAME
                        Site name, should end with .localhost, default: development.localhost
  -r SAASHQ_REPO, --saashq-repo SAASHQ_REPO
                        saashq repo to use, default: https://github.com/saashqdev/saashq
  -t SAASHQ_BRANCH, --saashq-branch SAASHQ_BRANCH
                        saashq repo to use, default: main
  -p PY_VERSION, --py-version PY_VERSION
                        python version, default: Not Set
  -n NODE_VERSION, --node-version NODE_VERSION
                        node version, default: Not Set
  -v, --verbose         verbose output
  -a ADMIN_PASSWORD, --admin-password ADMIN_PASSWORD
                        admin password for site, default: admin
  -d DB_TYPE, --db-type DB_TYPE
                        Database type to use (e.g., mariadb or postgres)
```

A new wrench and / or site is created for the client with following defaults.

- MariaDB root password: `123`
- Admin password: `admin`

> To use Postegres DB, comment the mariabdb service and uncomment postegres service.

### Start Saashq with Visual Studio Code Python Debugging

To enable Python debugging inside Visual Studio Code, you must first install the `ms-python.python` extension inside the container. This should have already happened automatically, but depending on your VSCode config, you can force it by:

- Click on the extension icon inside VSCode
- Search `ms-python.python`
- Click on `Install on Dev Container: Saashq Wrench`
- Click on 'Reload'

We need to start wrench separately through the VSCode debugger. For this reason, **instead** of running `wrench start` you should run the following command inside the saashq-wrench directory:

```shell
honcho start \
    socketio \
    watch \
    schedule \
    worker_short \
    worker_long
```

Alternatively you can use the VSCode launch configuration "Honcho SocketIO Watch Schedule Worker" which launches the same command as above.

This command starts all processes with the exception of Redis (which is already running in separate container) and the `web` process. The latter can can finally be started from the debugger tab of VSCode by clicking on the "play" button.

You can now login with user `Administrator` and the password you choose when creating the site, if you followed this guide's unattended install that password is going to be `admin`.

To debug workers, skip starting worker with honcho and start it with VSCode debugger.

For advance vscode configuration in the devcontainer, change the config files in `development/.vscode`.

## Developing using the interactive console

You can launch a simple interactive shell console in the terminal with:

```shell
wrench --site development.localhost console
```

More likely, you may want to launch VSCode interactive console based on Jupyter kernel.

Launch VSCode command palette (cmd+shift+p or ctrl+shift+p), run the command `Python: Select interpreter to start Jupyter server` and select `/workspace/development/saashq-wrench/env/bin/python`.

The first step is installing and updating the required software. Usually the saashq framework may require an older version of Jupyter, while VSCode likes to move fast, this can [cause issues](https://github.com/jupyter/jupyter_console/issues/158). For this reason we need to run the following command.

```shell
/workspace/development/saashq-wrench/env/bin/python -m pip install --upgrade jupyter ipykernel ipython
```

Then, run the command `Python: Show Python interactive window` from the VSCode command palette.

Replace `development.localhost` with your site and run the following code in a Jupyter cell:

```python
import saashq

saashq.init(site='development.localhost', sites_path='/workspace/development/saashq-wrench/sites')
saashq.connect()
saashq.local.lang = saashq.db.get_default('lang')
saashq.db.connect()
```

The first command can take a few seconds to be executed, this is to be expected.

## Manually start containers

In case you don't use VSCode, you may start the containers manually with the following command:

### Running the containers

```shell
docker-compose -f .devcontainer/docker-compose.yml up -d
```

And enter the interactive shell for the development container with the following command:

```shell
docker exec -e "TERM=xterm-256color" -w /workspace/development -it devcontainer-saashq-1 bash
```

## Use additional services during development

Add any service that is needed for development in the `.devcontainer/docker-compose.yml` then rebuild and reopen in devcontainer.

e.g.

```yaml
...
services:
 ...
  postgresql:
    image: postgres:11.8
    environment:
      POSTGRES_PASSWORD: 123
    volumes:
      - postgresql-data:/var/lib/postgresql/data
    ports:
      - 5432:5432

volumes:
  ...
  postgresql-data:
```

Access the service by service name from the `saashq` development container. The above service will be accessible via hostname `postgresql`. If ports are published on to host, access it via `localhost:5432`.

## Using Cypress UI tests

To run cypress based UI tests in a docker environment, follow the below steps:

1. Install and setup X11 tooling on VM using the script `install_x11_deps.sh`

```shell
  sudo bash ./install_x11_deps.sh
```

This script will install required deps, enable X11Forwarding and restart SSH daemon and export `DISPLAY` variable.

2. Run X11 service `startx` or `xquartz`
3. Start docker compose services.
4. SSH into ui-tester service using `docker exec..` command
5. Export CYPRESS_baseUrl and other required env variables
6. Start Cypress UI console by issuing `cypress run command`

> More references : [Cypress Official Documentation](https://www.cypress.io/blog/2019/05/02/run-cypress-with-a-single-docker-command)

> Ensure DISPLAY environment is always exported.

## Using Mailpit to test mail services

To use Mailpit just uncomment the service in the docker-compose.yml file.
The Interface is then available under port 8025 and the smtp service can be used as mailpit:1025.
