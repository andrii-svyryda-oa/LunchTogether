# Deployment Implementation Plan

## Overview
This plan outlines the implementation of deployment infrastructure using Docker Compose for local development, Terraform for Azure infrastructure, and GitHub Actions for CI/CD.

## Technology Stack
- Docker & Docker Compose
- Terraform (Azure provider)
- GitHub Actions
- Azure Services (App Service, PostgreSQL, Blob Storage, Container Registry)

## Project Structure

```
lunchtogether/
├── .github/
│   └── workflows/
│       ├── backend-ci.yml          # Backend CI pipeline
│       ├── frontend-ci.yml         # Frontend CI pipeline
│       ├── deploy-staging.yml      # Deploy to staging
│       └── deploy-production.yml   # Deploy to production
├── docker/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── frontend/
│   │   ├── Dockerfile
│   │   ├── nginx.conf
│   │   └── .dockerignore
│   └── postgres/
│       └── init.sql                # Initial database setup
├── docker-compose.yml              # Local development setup
├── docker-compose.prod.yml         # Production-like local setup
├── terraform/
│   ├── main.tf                     # Main Terraform configuration
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values
│   ├── terraform.tfvars.example    # Example variables
│   ├── modules/
│   │   ├── networking/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── database/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── storage/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── app-services/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── container-registry/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   └── environments/
│       ├── staging/
│       │   ├── main.tf
│       │   └── terraform.tfvars
│       └── production/
│           ├── main.tf
│           └── terraform.tfvars
└── scripts/
    ├── build.sh                    # Build script for all services
    ├── deploy-local.sh             # Local deployment script
    └── backup-db.sh                # Database backup script
```

## Implementation Steps

### Part 1: Docker Setup

#### 1. Backend Dockerfile
**Task**: Create production-ready Dockerfile for FastAPI backend

**File to create**: `docker/backend/Dockerfile`

**Implementation details**:
- Multi-stage build (builder + runtime)
- Use Python 3.12 slim base image
- Install uv in builder stage
- Copy and install dependencies using uv
- Copy application code
- Use non-root user for security
- Expose port 8000
- Health check endpoint
- CMD to run uvicorn with proper workers

**File to create**: `docker/backend/.dockerignore`
- Exclude __pycache__, .env, .venv, .git, tests

#### 2. Frontend Dockerfile
**Task**: Create production-ready Dockerfile for React frontend

**File to create**: `docker/frontend/Dockerfile`

**Implementation details**:
- Multi-stage build (builder + runtime)
- Builder stage: Node.js for building React app
- Runtime stage: Nginx alpine for serving static files
- Install dependencies and build app
- Copy build artifacts to nginx
- Custom nginx configuration

**File to create**: `docker/frontend/nginx.conf`
- Serve React app
- Handle client-side routing (SPA)
- Proxy /api requests to backend
- Gzip compression
- Security headers

**File to create**: `docker/frontend/.dockerignore`
- Exclude node_modules, .env, .git, dist

#### 3. PostgreSQL Initialization
**Task**: Create database initialization scripts

**File to create**: `docker/postgres/init.sql`
- Create database
- Create extensions (uuid-ossp)
- Set up initial users/permissions

#### 4. Docker Compose - Development
**Task**: Create docker-compose.yml for local development

**File to create**: `docker-compose.yml`

**Services to define**:

**postgres service**:
- Image: postgres:16-alpine
- Environment variables (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
- Volume for data persistence
- Volume for init scripts
- Port mapping: 5432:5432
- Health check

**backend service**:
- Build from docker/backend/Dockerfile
- Depends on postgres
- Environment variables (DATABASE_URL, JWT_SECRET, etc.)
- Volume mount source code (for hot reload)
- Port mapping: 8000:8000
- Command: uvicorn with --reload

**frontend service**:
- Build from docker/frontend/Dockerfile (dev target)
- Depends on backend
- Environment variables (VITE_API_BASE_URL)
- Volume mount source code (for hot reload)
- Port mapping: 3000:3000
- Command: npm run dev

**azurite service** (local Azure Blob Storage emulator):
- Image: mcr.microsoft.com/azure-storage/azurite
- Port mappings for blob, queue, table
- Volume for data persistence

**volumes**:
- postgres-data
- azurite-data

**networks**:
- lunchtogether-network

#### 5. Docker Compose - Production-like
**Task**: Create docker-compose.prod.yml for production testing

**File to create**: `docker-compose.prod.yml`

**Differences from development**:
- No volume mounts for source code
- Build production images
- No hot reload
- Proper health checks
- Resource limits
- Logging configuration

### Part 2: Terraform Infrastructure

#### 6. Terraform Base Configuration
**Task**: Set up Terraform project structure

**File to create**: `terraform/main.tf`
- Configure Azure provider
- Configure backend (Azure Storage for state)
- Call modules for each resource type

**File to create**: `terraform/variables.tf`
- Project name
- Environment (staging/production)
- Azure region
- Resource tags
- Database configuration
- App service SKU
- Enable/disable features

**File to create**: `terraform/outputs.tf`
- Resource group name
- App service URLs
- Database connection string
- Container registry URL
- Storage account details

**File to create**: `terraform/terraform.tfvars.example`
- Example values for all variables

#### 7. Terraform Module - Networking
**Task**: Create networking infrastructure module

**Directory**: `terraform/modules/networking/`

**Resources to create**:
- Virtual Network
- Subnets (app, database, storage)
- Network Security Groups
- Private endpoints for services
- DNS zones

**Outputs**:
- VNet ID
- Subnet IDs
- NSG IDs

#### 8. Terraform Module - Container Registry
**Task**: Create Azure Container Registry module

**Directory**: `terraform/modules/container-registry/`

**Resources to create**:
- Azure Container Registry
- Admin user enabled (for CI/CD)
- SKU configuration (Basic, Standard, Premium)
- Geo-replication (for production)

**Outputs**:
- Registry name
- Registry URL
- Admin credentials (sensitive)

#### 9. Terraform Module - Database
**Task**: Create Azure Database for PostgreSQL module

**Directory**: `terraform/modules/database/`

**Resources to create**:
- Azure Database for PostgreSQL Flexible Server
- Database instance
- Firewall rules (allow Azure services)
- Private endpoint (optional)
- Backup configuration
- High availability configuration (production)

**Outputs**:
- Database server FQDN
- Database name
- Connection string (sensitive)

#### 10. Terraform Module - Storage
**Task**: Create Azure Blob Storage module

**Directory**: `terraform/modules/storage/`

**Resources to create**:
- Storage account
- Blob containers
- Private endpoint (optional)
- Access policies
- Lifecycle management rules

**Outputs**:
- Storage account name
- Connection string (sensitive)
- Container names

#### 11. Terraform Module - App Services
**Task**: Create App Service module for backend and frontend

**Directory**: `terraform/modules/app-services/`

**Resources to create**:

**App Service Plan**:
- Linux plan
- SKU based on environment
- Auto-scaling rules (production)

**Backend App Service**:
- Linux App Service
- Docker container configuration
- Environment variables (from Key Vault)
- Application settings
- Health check path
- Always on (production)
- HTTPS only

**Frontend App Service**:
- Linux App Service
- Docker container configuration
- Environment variables
- Custom domain (optional)
- CDN integration (optional)

**Outputs**:
- App service URLs
- App service IDs

#### 12. Terraform Module - Key Vault (Optional but Recommended)
**Task**: Create Key Vault for secrets management

**Directory**: `terraform/modules/key-vault/`

**Resources to create**:
- Azure Key Vault
- Access policies
- Secrets (database password, JWT secret, etc.)

**Outputs**:
- Key Vault name
- Key Vault URI

#### 13. Terraform Environments - Staging
**Task**: Create staging environment configuration

**Directory**: `terraform/environments/staging/`

**File**: `main.tf`
- Use root module
- Set backend configuration
- Override variables for staging

**File**: `terraform.tfvars`
- Staging-specific values
- Lower SKUs for cost optimization
- Staging resource naming

#### 14. Terraform Environments - Production
**Task**: Create production environment configuration

**Directory**: `terraform/environments/production/`

**File**: `main.tf`
- Use root module
- Set backend configuration
- Override variables for production

**File**: `terraform.tfvars`
- Production-specific values
- Higher SKUs for performance
- High availability enabled
- Geo-replication enabled
- Production resource naming

### Part 3: GitHub Actions CI/CD

#### 15. Backend CI Pipeline
**Task**: Create CI pipeline for backend

**File to create**: `.github/workflows/backend-ci.yml`

**Triggers**:
- Push to main/develop branches
- Pull requests affecting backend/

**Jobs**:

**lint-and-test job**:
- Checkout code
- Set up Python 3.12
- Install uv
- Install dependencies
- Run ruff linting
- Run ruff formatting check
- Run typer checks
- Run tests with pytest
- Upload coverage report

**build-docker job**:
- Depends on lint-and-test
- Checkout code
- Set up Docker Buildx
- Login to Azure Container Registry
- Build Docker image
- Tag with git SHA and branch
- Push to registry (only on main/develop)

#### 16. Frontend CI Pipeline
**Task**: Create CI pipeline for frontend

**File to create**: `.github/workflows/frontend-ci.yml`

**Triggers**:
- Push to main/develop branches
- Pull requests affecting frontend/

**Jobs**:

**lint-and-test job**:
- Checkout code
- Set up Node.js
- Install dependencies
- Run ESLint
- Run TypeScript type checking
- Run tests with Vitest
- Build production bundle (verify)

**build-docker job**:
- Depends on lint-and-test
- Checkout code
- Set up Docker Buildx
- Login to Azure Container Registry
- Build Docker image
- Tag with git SHA and branch
- Push to registry (only on main/develop)

#### 17. Deploy to Staging Pipeline
**Task**: Create deployment pipeline for staging

**File to create**: `.github/workflows/deploy-staging.yml`

**Triggers**:
- Push to develop branch
- Manual workflow dispatch

**Jobs**:

**deploy-infrastructure job**:
- Checkout code
- Set up Terraform
- Azure login
- Terraform init (staging)
- Terraform plan
- Terraform apply (auto-approve)
- Save outputs as artifacts

**deploy-backend job**:
- Depends on deploy-infrastructure
- Download infrastructure outputs
- Azure login
- Update App Service with new container image
- Run database migrations
- Restart app service
- Wait for health check

**deploy-frontend job**:
- Depends on deploy-infrastructure
- Azure login
- Update App Service with new container image
- Restart app service

**smoke-tests job** (optional):
- Depends on deploy-backend and deploy-frontend
- Run basic API tests against staging
- Verify frontend is accessible

#### 18. Deploy to Production Pipeline
**Task**: Create deployment pipeline for production

**File to create**: `.github/workflows/deploy-production.yml`

**Triggers**:
- Push to main branch (with protection rules)
- Manual workflow dispatch (with approval)

**Jobs**: Similar to staging but with:
- Manual approval step (using environments)
- Backup database before deployment
- Blue-green or canary deployment strategy
- More comprehensive smoke tests
- Rollback capability
- Notifications (Slack, email)

**Additional steps**:

**backup job**:
- Create database backup
- Upload to blob storage
- Tag backup with deployment ID

**deploy with safety**:
- Deploy to subset of instances first
- Monitor errors
- Gradually roll out
- Automatic rollback on high error rate

**post-deployment**:
- Run integration tests
- Monitor application insights
- Send notifications

#### 19. GitHub Secrets Configuration
**Task**: Document required GitHub secrets

**Secrets to configure** (in GitHub repository settings):

**Azure Credentials**:
- `AZURE_CREDENTIALS`: Service principal JSON
- `ACR_USERNAME`: Container registry username
- `ACR_PASSWORD`: Container registry password
- `ACR_LOGIN_SERVER`: Container registry URL

**Application Secrets**:
- `JWT_SECRET_KEY`: JWT signing key
- `SENTRY_DSN`: Sentry error tracking DSN
- `DATABASE_PASSWORD_STAGING`: Staging DB password
- `DATABASE_PASSWORD_PRODUCTION`: Production DB password

**Terraform**:
- `TF_STATE_STORAGE_ACCOUNT`: Storage account for Terraform state
- `TF_STATE_CONTAINER`: Container for Terraform state
- `TF_STATE_KEY`: State file key

#### 20. Helper Scripts
**Task**: Create helper scripts for common operations

**File to create**: `scripts/build.sh`
- Build all Docker images locally
- Tag images appropriately
- Optional: push to registry

**File to create**: `scripts/deploy-local.sh`
- Start Docker Compose
- Wait for services to be healthy
- Run database migrations
- Display access URLs

**File to create**: `scripts/backup-db.sh`
- Create database backup
- Upload to Azure Blob Storage
- Clean old backups

### Part 4: Configuration and Documentation

#### 21. Environment Variables Documentation
**Task**: Create comprehensive environment variables guide

**File to create**: `docs/environment-variables.md`

**Document for each environment**:
- Development (local Docker Compose)
- Staging (Azure)
- Production (Azure)

**For each variable**:
- Name
- Description
- Example value
- Required/optional
- Where to set it

#### 22. Deployment Documentation
**Task**: Create deployment runbook

**File to create**: `docs/deployment-guide.md`

**Sections**:
- Prerequisites
- Initial setup (Terraform state, Azure login)
- Local development deployment
- Staging deployment
- Production deployment
- Rollback procedures
- Monitoring and logging
- Troubleshooting

#### 23. Infrastructure Documentation
**Task**: Document Azure infrastructure

**File to create**: `docs/infrastructure.md`

**Sections**:
- Architecture diagram (description)
- Resource naming conventions
- Network topology
- Security configuration
- Backup and disaster recovery
- Cost optimization
- Scaling considerations

#### 24. CI/CD Documentation
**Task**: Document CI/CD pipelines

**File to create**: `docs/ci-cd.md`

**Sections**:
- Pipeline overview
- Branch strategy
- Build process
- Testing strategy
- Deployment process
- Manual approval process
- Rollback procedures
- Monitoring deployments

### Part 5: Initial Setup Tasks

#### 25. Azure Setup Checklist
**Task**: Initial Azure configuration steps

**Manual steps required**:
1. Create Azure subscription
2. Create service principal for Terraform
3. Create service principal for GitHub Actions
4. Create storage account for Terraform state
5. Configure GitHub secrets
6. Set up Azure Key Vault (optional)
7. Configure custom domains (if needed)
8. Set up Application Insights
9. Configure Azure Monitor alerts

#### 26. Terraform Initialization
**Task**: Initialize Terraform for first time

**Steps**:
1. Create backend storage account
2. Run `terraform init` in staging environment
3. Run `terraform plan` and review
4. Run `terraform apply` to create staging infrastructure
5. Repeat for production environment
6. Verify all resources created correctly

#### 27. GitHub Actions Setup
**Task**: Configure GitHub repository

**Steps**:
1. Create environments (staging, production)
2. Configure protection rules
3. Add required reviewers for production
4. Configure secrets
5. Enable workflows
6. Run manual trigger to test pipelines

## Validation Checklist

### Docker
- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully
- [ ] Docker Compose starts all services
- [ ] Services can communicate with each other
- [ ] Volumes persist data correctly
- [ ] Health checks work properly

### Terraform
- [ ] Terraform init succeeds
- [ ] Terraform plan shows expected resources
- [ ] All modules have proper variables and outputs
- [ ] State is stored in Azure Storage
- [ ] Resources are properly tagged
- [ ] Staging and production environments are separate

### CI/CD
- [ ] Backend CI pipeline passes
- [ ] Frontend CI pipeline passes
- [ ] Docker images are pushed to registry
- [ ] Deployment pipelines succeed
- [ ] Database migrations run automatically
- [ ] Rollback procedures work
- [ ] Notifications are sent on failure

### Security
- [ ] Secrets are stored in Key Vault or GitHub Secrets
- [ ] No secrets in code or Terraform files
- [ ] HTTPS enforced on all services
- [ ] Database is not publicly accessible
- [ ] Network security groups are properly configured
- [ ] Service principals have minimal required permissions

## Cost Optimization Tips

1. **Development**: Use Docker Compose locally instead of Azure resources
2. **Staging**: Use lower-tier SKUs (B1 for App Service, Basic for PostgreSQL)
3. **Staging**: Single instance, no geo-replication
4. **Production**: Right-size based on actual usage
5. **Auto-scaling**: Configure based on metrics, not over-provision
6. **Shutdown**: Consider shutting down staging environment overnight
7. **Reserved Instances**: Consider for production if usage is predictable

## Next Steps After Implementation

1. Deploy to staging and verify all services work
2. Run load tests to validate performance
3. Test rollback procedures
4. Configure monitoring and alerts
5. Set up log aggregation
6. Document operational procedures
7. Train team on deployment process
8. Plan production deployment
9. Set up backup verification
10. Create disaster recovery plan
