# Project 2 — CI/CD Pipeline with GitHub Actions

A fully automated CI/CD pipeline that tests, builds a Docker image, pushes it to Docker Hub, and deploys to a Kubernetes cluster on every `git push` — zero manual steps.

## Architecture

```
git push to main
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                  GitHub Actions                      │
│                                                     │
│  Job 1: Test          Job 2: Build & Push           │
│  ──────────           ──────────────────            │
│  pip install    ───►  docker buildx                 │
│  pytest               push to Docker Hub            │
│  (fail = stop)        :latest + :sha                │
│                              │                      │
│                       Job 3: Deploy                 │
│                       ────────────                  │
│                       kubectl set image             │
│                       kubectl rollout wait          │
└─────────────────────────────────────────────────────┘
                              │
                              ▼
                   k3s Kubernetes Cluster
                   http://<ip>:30200
```

## Stack

| Tool | Role |
|------|------|
| GitHub Actions | CI/CD orchestration |
| Docker + Docker Hub | Image build and registry |
| Flask + pytest | Application and tests |
| kubectl | Kubernetes deployment |
| k3s | Target Kubernetes cluster |

## Project Structure

```
02-cicd-pipeline/
├── .github/
│   └── workflows/
│       └── cicd.yaml          # 3-job pipeline definition
├── app/
│   ├── app.py                 # Flask API (/ and /health endpoints)
│   ├── test_app.py            # pytest test suite
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Multi-stage build
└── k8s/
    └── deployment.yaml        # K8s Deployment + NodePort service
```

## Pipeline Jobs

### Job 1 — Run Tests
```yaml
- pip install -r requirements.txt
- pytest app/test_app.py -v
```
Tests must pass before any image is built or deployed.

### Job 2 — Build & Push Image
```yaml
- docker login to Docker Hub
- docker buildx build --platform linux/amd64
- push with :latest and :<commit-sha> tags
```
Two tags enable traceability — you can roll back to any previous commit.

### Job 3 — Deploy to k3s
```yaml
- decode KUBECONFIG secret and configure kubectl
- kubectl set image deployment/... image=...:sha
- kubectl rollout status (waits for healthy pods)
```

## GitHub Secrets Required

| Secret | Value |
|--------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token (not password) |
| `KUBECONFIG` | `base64 -w 0 ~/.kube/config` output |

### Encode your kubeconfig
```bash
# Replace 127.0.0.1 with your master node public IP first
sed -i 's/127.0.0.1/<MASTER_PUBLIC_IP>/g' ~/.kube/config
base64 -w 0 ~/.kube/config
```
Paste the output as the `KUBECONFIG` secret value.

## Setup

### 1. Fork / clone this repo and push to GitHub

### 2. Add the three GitHub secrets
Settings → Secrets and variables → Actions → New repository secret

### 3. Push any change to trigger the pipeline
```bash
git add .
git commit -m "trigger pipeline"
git push origin main
```

### 4. Watch it run
GitHub → Actions tab → see all three jobs turn green

### 5. Verify the deployment
```bash
# On the k3s master node
kubectl get pods
kubectl get svc
curl http://<MASTER_IP>:30200
```

Expected response:
```json
{"message": "Hello from DevOps Portfolio!", "status": "running"}
```

## What This Demonstrates

- **CI/CD principles** — tests gate deployments; nothing broken ships
- **GitHub Actions** — YAML-defined workflows with jobs, steps, secrets, conditionals
- **Docker multi-stage builds** — lean production images
- **Image tagging strategy** — `:latest` + `:commit-sha` for traceability and rollback
- **Secrets management** — credentials never in source code
- **Kubernetes rolling updates** — zero-downtime deployments with rollout status checks
- **Multi-platform builds** — `buildx` for `linux/amd64` images built on any machine
