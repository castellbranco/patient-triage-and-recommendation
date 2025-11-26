# Deployment

Production deployment configurations and scripts for the Patient Triage & Management System.

## Structure

```
deploy/
├── docker/              # Production-optimized Dockerfiles
├── k8s/                 # Kubernetes manifests
│   ├── base/           # Base configurations
│   └── overlays/       # Environment-specific overlays
├── terraform/           # Infrastructure as Code
│   ├── aws/            # AWS deployment
│   └── gcp/            # GCP deployment
└── scripts/            # Deployment automation scripts
```

## Deployment Options

### 1. Docker Compose (Development/Staging)

**Use Case**: Local development, staging environments

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**See**: [docker/README.md](../docker-compose.yml)

### 2. Google Cloud Platform (GCP)

**Services Used**:
- Cloud Run (containerized backend/frontend)
- Cloud SQL (PostgreSQL)
- Cloud Storage (file uploads)
- Cloud Load Balancing

**Deploy**:
```bash
cd terraform/gcp
terraform init
terraform plan
terraform apply
```

**See**: [../docs/deployment/gcp.md](../docs/deployment/gcp.md)

### 3. Amazon Web Services (AWS)

**Services Used**:
- ECS/Fargate (containers)
- RDS PostgreSQL
- S3 (file storage)
- Application Load Balancer

**Deploy**:
```bash
cd terraform/aws
terraform init
terraform plan
terraform apply
```

**See**: [../docs/deployment/aws.md](../docs/deployment/aws.md)

### 4. Kubernetes (Future)

**Use Case**: Large-scale production, multi-cloud

**Deploy**:
```bash
kubectl apply -k k8s/overlays/production
```

**See**: [k8s/README.md](k8s/README.md)

## Production Dockerfiles

Production images are optimized separately from development:

- **Multi-stage builds**: Minimal runtime images
- **Security**: Non-root users, minimal attack surface
- **Size**: Optimized layer caching
- **Health checks**: Built-in health endpoints

See [docker/](docker/) for production Dockerfiles.

## Deployment Scripts

Automation scripts for common deployment tasks:

- `deploy-local.sh`: Local Docker Compose deployment
- `deploy-gcp.sh`: Deploy to Google Cloud Run
- `deploy-aws.sh`: Deploy to AWS ECS

## Environment Configuration

### Required Secrets

Must be configured in deployment environment:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://...

# JWT
SECRET_KEY=<generated-secret>

# Cloud Storage (if applicable)
GCP_PROJECT_ID=...
AWS_ACCESS_KEY_ID=...
```

### Environment-Specific Configs

- **Development**: `.env` file
- **Docker Compose**: `.env.docker`
- **GCP**: Cloud Secret Manager
- **AWS**: Systems Manager Parameter Store
- **Kubernetes**: Sealed Secrets or External Secrets

## CI/CD Integration

GitHub Actions automatically:
1. Build Docker images on tag creation
2. Push to container registry (GitHub Container Registry)
3. Deploy to selected environment based on tag pattern

**See**: [../.github/workflows/deploy.yml](../.github/workflows/deploy.yml)

## Monitoring & Observability

### Health Checks

All deployments must expose:
- `/api/public/v1/health`: Liveness probe
- `/api/public/v1/ready`: Readiness probe

### Logging

- **Development**: Console logs
- **Production**: Structured JSON logs to cloud logging
- **Retention**: 30 days minimum

### Metrics (Phase 6)

- Application metrics (request rate, latency)
- Infrastructure metrics (CPU, memory, disk)
- Business metrics (patients, appointments, triage results)

## Backup Strategy

### Database Backups

- **Frequency**: Daily automated backups
- **Retention**: 30 days
- **Point-in-time recovery**: Enabled
- **Testing**: Monthly restore tests

### File Storage Backups

- **Frequency**: Real-time replication (cloud storage)
- **Retention**: 90 days
- **Versioning**: Enabled

## Disaster Recovery

### Recovery Time Objective (RTO)

- **Critical**: < 1 hour
- **High**: < 4 hours
- **Medium**: < 24 hours

### Recovery Point Objective (RPO)

- **Database**: < 5 minutes
- **Files**: Near real-time

### Runbooks

- Database failure: [docs/runbooks/database-failure.md]
- Application failure: [docs/runbooks/app-failure.md]
- Complete outage: [docs/runbooks/disaster-recovery.md]

## Security Considerations

### Network Security

- **TLS/SSL**: All traffic encrypted
- **Firewall**: Restrict to necessary ports
- **VPC**: Private networking for databases

### Access Control

- **IAM**: Least privilege principle
- **Secrets**: Never in code or plain text
- **Rotation**: Regular secret rotation

### Compliance

- **HIPAA**: Healthcare data compliance (Phase 6)
- **Audit Logging**: All data access logged
- **Encryption**: At rest and in transit

## Cost Optimization

### GCP Recommendations

- Use Cloud Run for auto-scaling
- Cloud SQL automatic backups (free)
- Cloud Storage lifecycle policies

### AWS Recommendations

- Use Fargate Spot for non-critical workloads
- RDS Reserved Instances for cost savings
- S3 Intelligent-Tiering

## Scaling Strategy

### Vertical Scaling (Phase 1-4)

- Increase instance size as needed
- Monitor resource utilization
- Scale when CPU > 70% or Memory > 80%

### Horizontal Scaling (Phase 5-6)

- Auto-scaling based on metrics
- Load balancing across instances
- Database read replicas

## References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
