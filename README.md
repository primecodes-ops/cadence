# Cadence 🎧

A Spotify-connected backend that analyzes your top tracks and surfaces a simple
listening-history profile — built primarily as a hands-on vehicle for learning
backend development, containerization, CI/CD, and AWS cloud deployment.

Infrastructure is also fully defined as Terraform/IaC — see [cadence-terraform](../cadence-terraform).

## What it does

- Authenticates with Spotify via OAuth 2.0 (Authorization Code flow)
- Fetches your top tracks and top artists from the Spotify Web API
- Computes a "decade breakdown" — which decade your most-listened tracks come from
- Returns the result as a simple JSON response

## Why this project

This started as a music-themed learning project with a specific goal: build
something real enough to genuinely exercise cloud/devops skills — authentication,
a working backend, containerization, automated builds, and real cloud deployment —
rather than a toy example.

Along the way, Spotify deprecated or restricted several API fields for
Development Mode apps (audio features, artist genres, and track/artist
popularity), which forced the project's analytical scope to narrow from an
original "mood analyzer" concept down to the decade-breakdown feature it has now.
That pivot is intentional and documented — see [Known Limitations](#known-limitations).

## Tech stack

- **Backend:** Python, FastAPI, Uvicorn
- **Auth:** Spotify OAuth 2.0 (Authorization Code flow)
- **HTTP client:** httpx
- **Containerization:** Docker
- **CI:** GitHub Actions
- **Cloud:** AWS (ECR, ECS/Fargate, IAM, Secrets Manager, CloudWatch Logs, VPC/Security Groups)

## Architecture

Deployed as a Docker container running on AWS ECS Fargate, pulling its image
from ECR, reading Spotify credentials from AWS Secrets Manager, and logging to
CloudWatch.

## Local setup

1. Clone the repo and create a virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
2. Create a Spotify app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard),
   and add `http://127.0.0.1:8000/callback` as a Redirect URI.
3. Create a `.env` file in the project root:
4. Run the app:
```bash
   uvicorn main:app --reload
```
5. Visit `http://127.0.0.1:8000/login` to start the OAuth flow.

## Running with Docker

```bash
docker build -t cadence .
docker run -p 8000:8000 --env-file .env cadence
```

## Status

Fully deployed on AWS (ECR, ECS/Fargate, IAM, Secrets Manager, CloudWatch,
VPC/Security Groups). Backend confirmed reachable publicly (`/docs`).

## Known limitations

- **OAuth doesn't work on the live AWS deployment yet.** Spotify requires HTTPS
  for any non-localhost redirect URI. The current deployment exposes the ECS
  task on a plain HTTP public IP, so `/login` → `/callback` works locally and in
  a local Docker container, but not on the public AWS deployment yet. Fixing
  this requires an Application Load Balancer + AWS Certificate Manager (TLS
  cert) + a registered domain — a deliberate follow-up, not yet implemented.
- **No genre or mood/energy analysis.** Spotify deprecated the `/audio-features`
  endpoint (Nov 2024) and removed `genres`/`popularity` fields for Development
  Mode apps, which removed the data this project originally intended to analyze.
  The current decade-breakdown feature uses only the fields still reliably
  available (`release_date`).
- **No persistence layer.** Tokens and results aren't stored — each request
  re-runs the full OAuth + fetch + analysis flow. PostgreSQL integration was
  deferred in favor of finishing the deployment pipeline, and is planned as
  part of a separate, larger future project instead.
- **Public IP is not static.** Fargate assigns a new IP on every task restart,
  so the deployed address changes over time without a load balancer in front.

## Progress

- [x] FastAPI backend, OAuth 2.0 (Spotify)
- [x] Decade-breakdown analysis from top tracks
- [x] Dockerized, cross-platform build (`linux/amd64`)
- [x] CI pipeline (GitHub Actions) — build verification on every push
- [x] Deployed to AWS: ECR, ECS/Fargate, IAM roles, Secrets Manager, CloudWatch Logs, VPC/Security Groups
- [ ] HTTPS via ALB + ACM + custom domain (needed for OAuth to work publicly)
- [ ] Full CD — automatic build/push/deploy on every push
- [ ] PostgreSQL persistence (deferred to a future, larger project)

## What this project demonstrates

- OAuth 2.0 implementation from scratch (not a library wrapper)
- REST API design and consumption (FastAPI + external API integration)
- Secrets management, both locally (`.env`) and in the cloud (AWS Secrets Manager)
- Docker containerization, including cross-architecture build issues
- CI automation with GitHub Actions
- Real AWS deployment: ECR, ECS/Fargate, IAM roles and trust policies, VPC
  networking, security groups, and CloudWatch logging — including debugging
  actual deployment failures (IAM trust policy errors, missing log groups,
  image architecture mismatches) rather than a guided tutorial path