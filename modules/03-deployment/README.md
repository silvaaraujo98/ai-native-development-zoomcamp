# Module 03 — Deployment TODO

Use this checklist to track the deployment work for the project.

## Deployment milestones

- [ ] Put the frontend and backend inside one container so the backend serves the frontend
- [ ] Replace SQLite with PostgreSQL for production
- [ ] Simplify local development with Docker Compose
- [ ] Create an end-to-end test for the Docker Compose application
- [ ] Deploy the application to the cloud using CloudFormation
- [ ] Create a CI/CD pipeline to deploy every change automatically

## Project setup

- [ ] Review the product specification in `docs/spec.md`
- [ ] Review the API definition in `openapi.yaml`
- [ ] Confirm the required environment variables and secrets
- [ ] Document the local setup and deployment prerequisites

## Backend

- [ ] Install backend dependencies with `uv sync`
- [ ] Run the backend locally with `make backend`
- [ ] Run the backend test suite with `make test`
- [ ] Add a production server configuration
- [ ] Configure the production database
- [ ] Configure authentication and secret management
- [ ] Add health and readiness endpoints
- [ ] Add structured logging and error handling

## Frontend

- [ ] Install frontend dependencies with `npm install`
- [ ] Run the frontend locally with `make frontend`
- [ ] Configure the production API URL
- [ ] Build the frontend for production
- [ ] Verify the frontend can connect to the deployed backend

## Containerization and deployment

- [ ] Create a `Dockerfile` for the backend
- [ ] Create a `Dockerfile` or static hosting configuration for the frontend
- [ ] Add a `.dockerignore` file
- [ ] Build the production images locally
- [ ] Run the containers locally and test the complete application
- [ ] Configure HTTPS and a domain name
- [ ] Deploy the backend
- [ ] Deploy the frontend
- [ ] Configure CORS for the production frontend domain

## Verification

- [ ] Verify authentication and session creation
- [ ] Verify candidate links and permissions
- [ ] Verify canvas changes are saved and restored
- [ ] Verify multiple participants can collaborate
- [ ] Verify reconnect behavior after a temporary network failure
- [ ] Verify API and frontend error states
- [ ] Run the production smoke tests
- [ ] Check logs, metrics, and alerts

## Documentation and handoff

- [ ] Document the deployment steps
- [ ] Document rollback and recovery procedures
- [ ] Document required environment variables
- [ ] Record the deployed URLs
- [ ] Commit the completed work to Git
