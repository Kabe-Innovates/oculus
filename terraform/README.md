# Oculus Terraform

Modular Terraform for the Oculus real-time fraud decision and review
platform on AWS, single region (`ap-south-1`), 2 Availability Zones.

## Modules

| Module | Purpose |
|---|---|
| `vpc` | VPC, 2 public subnets (ALB only), 2 private subnets (ECS/RDS/Redis), NAT per AZ |
| `security_groups` | ALB / ECS / RDS / Redis / Lambda security groups, boundary-enforced |
| `waf` | WAFv2 WebACL (managed rule groups + rate limiting) on the ALB |
| `alb` | Public ALB, HTTP/HTTPS listeners, target group (WebSocket-compatible) |
| `ecs_fargate` | FastAPI decision service cluster, task def, service, autoscaling, least-privilege task role |
| `rds_postgres` | PostgreSQL for transactions/fraud_flags/reviews/outbox |
| `elasticache_redis` | Redis for sliding-window velocity + baselines |
| `sqs` | Outbox queue + DLQ |
| `lambda_alerts` | SQS-triggered worker publishing to SNS/SES |
| `sns_ses` | Fraud alert topic (email/SMS) + SES sender identity |
| `cognito` | User pool, app client, `analyst`/`admin` groups |
| `cloudfront_spa` | Private S3 bucket + CloudFront serving the React SPA, proxies `/api/*` and `/ws/*` to the ALB |
| `secrets_manager` | RDS credentials + app config secrets |
| `cloudwatch` | Dashboard, p95 latency alarm, ECS CPU alarm, rule-hit-rate metric filter |

## Usage

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars: container_image, spa_bucket_suffix, alert_emails, etc.

terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Configure a remote backend (S3 + DynamoDB lock table) separately before
team use; this module set ships with local state for portability.

Diagram and security boundary notes: see `../docs/architecture.md`.
