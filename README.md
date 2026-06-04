# Example Voting App

A simple distributed application running across multiple Docker containers.

## Getting started

Download [Docker Desktop](https://www.docker.com/products/docker-desktop) for Mac or Windows. [Docker Compose](https://docs.docker.com/compose) will be automatically installed. On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/).

This solution uses Python, Node.js, .NET, with Redis for messaging and Postgres for storage.

Run in this directory to build and run the app:

```shell
docker compose up
```

The `vote` app will be running at [http://localhost:8080](http://localhost:8080), and the `results` will be at [http://localhost:8081](http://localhost:8081).

Alternately, if you want to run it on a [Docker Swarm](https://docs.docker.com/engine/swarm/), first make sure you have a swarm. If you don't, run:

```shell
docker swarm init
```

Once you have your swarm, in this directory run:

```shell
docker stack deploy --compose-file docker-stack.yml vote
```

## Run the app in Kubernetes

The folder k8s-specifications contains the YAML specifications of the Voting App's services.

Run the following command to create the deployments and services. Note it will create these resources in your current namespace (`default` if you haven't changed it.)

```shell
kubectl create -f k8s-specifications/
```

The `vote` web app is then available on port 31000 on each host of the cluster, the `result` web app is available on port 31001.

To remove them, run:

```shell
kubectl delete -f k8s-specifications/
```

## Architecture

![Architecture diagram](architecture.excalidraw.png)

- A front-end web app in [Python](/vote) which lets you vote between two options
- A [Redis](https://hub.docker.com/_/redis/) which collects new votes
- A [.NET](/worker/) worker which consumes votes and stores them in…
- A [Postgres](https://hub.docker.com/_/postgres/) database backed by a Docker volume
- A [Node.js](/result) web app which shows the results of the voting in real time

## Notes

The voting application only accepts one vote per client browser. It does not register additional votes if a vote has already been submitted from a client.

This isn't an example of a properly architected perfectly designed distributed app... it's just a simple
example of the various types of pieces and languages you might see (queues, persistent data, etc), and how to
deal with them in Docker at a basic level.

## Epic 2: Jenkins Pipeline Setup

Epic 2 focuses on provisioning Jenkins and creating the first CI/CD pipeline skeleton.

Completed work:

- Provisioned Jenkins server on AWS EC2
- Installed Java 21, Jenkins, Docker, and Docker Compose
- Created Jenkins Pipeline job connected to GitHub
- Added Jenkinsfile with basic stages:
  - Checkout
  - Validate Docker Compose
  - Build
  - Basic Tests
  - Create Build Artifact
- Verified successful Jenkins pipeline run
- Archived basic build artifacts in Jenkins
- Configured GitHub webhook
- Confirmed that push events automatically trigger Jenkins builds

Validation:

- Jenkins Build #3 completed successfully manually
- Jenkins Build #4 was triggered automatically by GitHub webhook and completed successfully

Security note:

No passwords, tokens, private keys, or Jenkins admin credentials are stored in this repository.

## Epic 4: Security Gates with Trivy

Epic 4 adds container image security scanning to the Jenkins pipeline using Trivy.

Security policy:

- Jenkins builds Docker images for `vote`, `result`, and `worker`
- Trivy scans each image for vulnerabilities
- Reports are saved as Jenkins build artifacts
- Pipeline fails if Trivy finds HIGH or CRITICAL vulnerabilities

Archived reports:

- `vote-trivy-report.txt`
- `result-trivy-report.txt`
- `worker-trivy-report.txt`

No security scan reports are committed to the repository. Reports are generated during Jenkins pipeline execution and archived in Jenkins.
