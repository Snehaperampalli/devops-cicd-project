# DevOps CI/CD + GitOps Project

A small Flask API that is tested, containerized, scanned and published automatically
on every push. Later phases add Kubernetes (k3s), Argo CD (GitOps) and
Prometheus + Grafana monitoring.

```
git push -> GitHub Actions (lint, test, build, Trivy scan) -> GHCR
         -> Argo CD -> k3s on Ubuntu -> Prometheus + Grafana
```

## Repo layout

```
app/                      Flask app, tests, Dockerfile
.github/workflows/ci.yml  CI pipeline
```

Planned next: `ansible/`, `helm/`, `monitoring/`.

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Name and version |
| `/health` | GET | Liveness / readiness probe |
| `/api/tasks` | GET, POST | Simple in-memory task list |
| `/api/error` | GET | Returns 500 on purpose (to test error-rate alerts) |
| `/metrics` | GET | Prometheus metrics |

## Run locally on Ubuntu

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

flake8 .          # lint
pytest -v         # tests
python app.py     # http://localhost:8080
```

Try it:

```bash
curl localhost:8080/health
curl -X POST localhost:8080/api/tasks -H 'Content-Type: application/json' -d '{"title":"learn devops"}'
curl localhost:8080/api/tasks
curl localhost:8080/metrics | head
```

## Run with Docker

```bash
sudo apt install -y docker.io
sudo usermod -aG docker $USER     # log out and back in once
cd app
docker build -t devops-demo:local .
docker run --rm -p 8080:8080 -e APP_VERSION=1.0.0 devops-demo:local
```

The image is multi-stage, runs as a non-root user, and has a built-in healthcheck.

## CI pipeline (`.github/workflows/ci.yml`)

1. **test**: flake8 lint and pytest on every push and pull request.
2. **build-scan-push**: builds the image, scans it with Trivy (fails on fixable
   CRITICAL or HIGH issues), then pushes to GHCR tagged with the commit SHA.
   Pushing happens only from `main`, never from pull requests.

### One-time GitHub setup

1. Create a repo and push this code to `main`.
2. Settings > Actions > General > Workflow permissions: **Read and write**.
3. After the first run, GHCR > your package > Package settings > make it
   **public** (so the cluster can pull it without credentials).
4. Settings > Branches: add a protection rule on `main` that requires the
   **test** check to pass before merging.

## Roadmap

- [x] Phase 1: app, tests, Dockerfile
- [x] Phase 2: CI pipeline
- [ ] Phase 3: Ansible playbook (Docker + k3s on Ubuntu)
- [ ] Phase 4: Kubernetes manifests / Helm chart
- [ ] Phase 5: Argo CD GitOps deployment
- [ ] Phase 6: Prometheus + Grafana dashboard and alert
- [ ] Phase 7: bonus (rollback demo, HPA, or backup script)
