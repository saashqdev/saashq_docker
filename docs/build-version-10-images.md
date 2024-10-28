Clone the version-10 branch of this repo

```shell
git clone https://github.com/saashqdev/saashq_docker.git -b version-10 && cd saashq_docker
```

Build the images

```shell
export DOCKER_REGISTRY_PREFIX=saashq
docker build -t ${DOCKER_REGISTRY_PREFIX}/saashq-socketio:v10 -f build/saashq-socketio/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/saashq-nginx:v10 -f build/saashq-nginx/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/erpnexus-nginx:v10 -f build/erpnexus-nginx/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/saashq-worker:v10 -f build/saashq-worker/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/erpnexus-worker:v10 -f build/erpnexus-worker/Dockerfile .
```
