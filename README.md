[![Build Stable](https://github.com/saashqdev/saashq_docker/actions/workflows/build_stable.yml/badge.svg)](https://github.com/saashqdev/saashq_docker/actions/workflows/build_stable.yml)
[![Build Develop](https://github.com/saashqdev/saashq_docker/actions/workflows/build_develop.yml/badge.svg)](https://github.com/saashqdev/saashq_docker/actions/workflows/build_develop.yml)

Everything about [Saashq](https://github.com/saashqdev/saashq) and [ERPNexus](https://github.com/saashqdev/erpnexus) in containers.

# Getting Started

To get started you need [Docker](https://docs.docker.com/get-docker/), [docker-compose](https://docs.docker.com/compose/), and [git](https://docs.github.com/en/get-started/getting-started-with-git/set-up-git) setup on your machine. For Docker basics and best practices refer to Docker's [documentation](http://docs.docker.com).

Once completed, chose one of the following two sections for next steps.

### Try on your Dev environment

First clone the repo:

```sh
git clone https://github.com/saashqdev/saashq_docker
cd saashq_docker
```

Then run: `docker compose -f pwd.yml up -d`

## Final steps

Wait for 5 minutes for ERPNexus site to be created or check `create-site` container logs before opening browser on port 8080. (username: `Administrator`, password: `admin`)

If you ran in a Dev Docker environment, to view container logs: `docker compose -f pwd.yml -d`. Don't worry about some of the initial error messages, some services take a while to become ready, and then they go away.

# Documentation

### [Frequently Asked Questions](https://github.com/saashqdev/saashq_docker/wiki/Frequently-Asked-Questions)

### [Production](#production)

- [List of containers](docs/list-of-containers.md)
- [Single Compose Setup](docs/single-compose-setup.md)
- [Environment Variables](docs/environment-variables.md)
- [Single Server Example](docs/single-server-example.md)
- [Setup Options](docs/setup-options.md)
- [Site Operations](docs/site-operations.md)
- [Backup and Push Cron Job](docs/backup-and-push-cronjob.md)
- [Port Based Multi Tenancy](docs/port-based-multi-tenancy.md)
- [Migrate from multi-image setup](docs/migrate-from-multi-image-setup.md)
- [running on linux/mac](docs/setup_for_linux_mac.md)

### [Custom Images](#custom-images)

- [Custom Apps](docs/custom-apps.md)
- [Build Version 10 Images](docs/build-version-10-images.md)

### [Development](#development)

- [Development using containers](docs/development.md)
- [Wrench Console and VSCode Debugger](docs/wrench-console-and-vscode-debugger.md)
- [Connect to localhost services](docs/connect-to-localhost-services-from-containers-for-local-app-development.md)

