# Docker Buildx Bake build definition file
# Reference: https://github.com/docker/buildx/blob/master/docs/reference/buildx_bake.md

variable "REGISTRY_USER" {
    default = "saashqdev"
}

variable PYTHON_VERSION {
    default = "3.11.6"
}
variable NODE_VERSION {
    default = "18.18.2"
}

variable "SAASHQ_VERSION" {
    default = "develop"
}

variable "ERPNEXUS_VERSION" {
    default = "develop"
}

variable "SAASHQ_REPO" {
    default = "https://github.com/saashqdev/saashq"
}

variable "ERPNEXUS_REPO" {
    default = "https://github.com/saashqdev/erpnexus"
}

variable "WRENCH_REPO" {
    default = "https://github.com/saashqdev/wrench"
}

variable "LATEST_WRENCH_RELEASE" {
    default = "latest"
}

# Wrench image

target "wrench" {
    args = {
        GIT_REPO = "${WRENCH_REPO}"
    }
    context = "images/wrench"
    target = "wrench"
    tags = [
        "saashqdev/wrench:${LATEST_WRENCH_RELEASE}",
        "saashqdev/wrench:latest",
    ]
}

target "wrench-test" {
    inherits = ["wrench"]
    target = "wrench-test"
}

# Main images
# Base for all other targets

group "default" {
    targets = ["erpnexus", "base", "build"]
}

function "tag" {
    params = [repo, version]
    result = [
      # If `version` param is develop (development build) then use tag `latest`
      "${version}" == "develop" ? "${REGISTRY_USER}/${repo}:latest" : "${REGISTRY_USER}/${repo}:${version}",
      # Make short tag for major version if possible. For example, from v13.16.0 make v13.
      can(regex("(v[0-9]+)[.]", "${version}")) ? "${REGISTRY_USER}/${repo}:${regex("(v[0-9]+)[.]", "${version}")[0]}" : "",
      # Make short tag for major version if possible. For example, from v13.16.0 make version-13.
      can(regex("(v[0-9]+)[.]", "${version}")) ? "${REGISTRY_USER}/${repo}:version-${regex("([0-9]+)[.]", "${version}")[0]}" : "",
    ]
}

target "default-args" {
    args = {
        SAASHQ_PATH = "${SAASHQ_REPO}"
        ERPNEXUS_PATH = "${ERPNEXUS_REPO}"
        WRENCH_REPO = "${WRENCH_REPO}"
        SAASHQ_BRANCH = "${SAASHQ_VERSION}"
        ERPNEXUS_BRANCH = "${ERPNEXUS_VERSION}"
        PYTHON_VERSION = "${PYTHON_VERSION}"
        NODE_VERSION = "${NODE_VERSION}"
    }
}

target "erpnexus" {
    inherits = ["default-args"]
    context = "."
    dockerfile = "images/production/Containerfile"
    target = "erpnexus"
    tags = tag("erpnexus", "${ERPNEXUS_VERSION}")
}

target "base" {
    inherits = ["default-args"]
    context = "."
    dockerfile = "images/production/Containerfile"
    target = "base"
    tags = tag("base", "${SAASHQ_VERSION}")
}

target "build" {
    inherits = ["default-args"]
    context = "."
    dockerfile = "images/production/Containerfile"
    target = "build"
    tags = tag("build", "${SAASHQ_VERSION}")
}
