# Oculus AWS Architecture

Real-time payment fraud decision and review platform. Single region
`ap-south-1`, 2 Availability Zones, no cross-region components.

## Diagram

```mermaid
flowchart TB
    Analyst["Analyst Browser"]

    subgraph AWS["AWS Account - ap-south-1"]
        CF["CloudFront Distribution"]
        S3["S3 Bucket (private, OAC)<br/>React SPA static assets"]

        subgraph VPC["VPC 10.20.0.0/16"]
            subgraph PubAZ1["Public Subnet AZ-1 (10.20.0.0/24)<br/>SG: alb-sg"]
                ALB1["ALB node"]
            end
            subgraph PubAZ2["Public Subnet AZ-2 (10.20.1.0/24)<br/>SG: alb-sg"]
                ALB2["ALB node"]
            end

            WAF["AWS WAFv2 WebACL<br/>(managed rules + rate limit)"]

            subgraph PrivAZ1["Private Subnet AZ-1 (10.20.10.0/24)<br/>SG: ecs-sg / rds-sg / redis-sg"]
                ECS1["ECS Fargate task<br/>FastAPI decision service"]
                RDS1["RDS PostgreSQL<br/>(primary)"]
                Redis1["ElastiCache Redis<br/>(primary)"]
            end

            subgraph PrivAZ2["Private Subnet AZ-2 (10.20.11.0/24)<br/>SG: ecs-sg / rds-sg / redis-sg"]
                ECS2["ECS Fargate task<br/>FastAPI decision service"]
                RDS2["RDS PostgreSQL<br/>(standby, Multi-AZ)"]
                Redis2["ElastiCache Redis<br/>(replica)"]
            end

            NAT1["NAT Gateway AZ-1"]
            NAT2["NAT Gateway AZ-2"]
        end

        SQS["SQS outbox queue + DLQ"]
        Lambda["Lambda outbox worker<br/>(SG: lambda-sg, egress-only)"]
        SNS["SNS Topic<br/>fraud-alerts"]
        SES["SES<br/>case-summary email"]
        Cognito["Cognito User Pool<br/>groups: analyst, admin"]
        Secrets["Secrets Manager<br/>RDS creds + app config"]
        CW["CloudWatch<br/>dashboards + alarms<br/>p50/p95, rule hit rate"]
    end

    Analyst -->|HTTPS| CF
    CF -->|/ default path| S3
    CF -->|/api/*, /ws/* HTTPS + WebSocket| WAF
    WAF --> ALB1
    WAF --> ALB2
    ALB1 --> ECS1
    ALB2 --> ECS2
    Cognito -.auth/roles.-> ALB1

    ECS1 --> RDS1
    ECS2 --> RDS2
    ECS1 --> Redis1
    ECS2 --> Redis2
    ECS1 -. NAT egress .-> NAT1
    ECS2 -. NAT egress .-> NAT2

    RDS1 -->|outbox rows| SQS
    SQS --> Lambda
    Lambda --> SNS
    Lambda --> SES
    SNS -->|email/SMS| Analyst
    SES -->|email| Analyst

    ECS1 -.sns:Publish only.-> SNS
    ECS1 -.reads.-> Secrets
    ECS2 -.reads.-> Secrets

    ECS1 -.metrics/logs.-> CW
    ALB1 -.metrics.-> CW
```

## Security boundaries

- **VPC**: single VPC `10.20.0.0/16`, 2 AZs (`ap-south-1a`, `ap-south-1b`).
- **Public subnets** (`10.20.0.0/24`, `10.20.1.0/24`): host the ALB only.
  `map_public_ip_on_launch = true`. Route to Internet Gateway.
- **Private subnets** (`10.20.10.0/24`, `10.20.11.0/24`): host ECS Fargate
  tasks, RDS PostgreSQL, and ElastiCache Redis. No public IPs. Route to
  NAT Gateways (one per AZ) for outbound-only internet access (image
  pulls, AWS API calls).
- **Security groups**:
  - `alb-sg`: ingress 80/443 from `0.0.0.0/0` (the only internet-facing SG).
  - `ecs-sg`: ingress on the app port from `alb-sg` only.
  - `rds-sg`: ingress 5432 from `ecs-sg` only.
  - `redis-sg`: ingress 6379 from `ecs-sg` only.
  - `lambda-sg`: egress-only, no inbound (outbox worker talks to AWS APIs,
    not VPC resources).
- **WAF**: WAFv2 WebACL (AWS managed Common + KnownBadInputs rule groups,
  plus per-IP rate limiting) attached to the ALB in front of both REST and
  WebSocket paths.
- **IAM least privilege**: the ECS task role is scoped to `sns:Publish` on
  the fraud-alerts topic ARN only, plus `secretsmanager:GetSecretValue` on
  its own two secrets (via the execution role). The Lambda outbox worker
  role is scoped to `sqs:ReceiveMessage`/`DeleteMessage` on its queue,
  `sns:Publish` on the alerts topic, and `ses:SendEmail`.

## Flow summary

1. Analyst browser loads the React SPA from CloudFront/S3, and calls the
   API / opens a WebSocket through CloudFront -> WAF -> ALB -> ECS Fargate.
2. The stateless FastAPI decision service evaluates each transaction
   through pluggable rules (velocity, amount anomaly, geo-impossibility,
   etc.), using Redis for sliding-window counters and baselines, and
   persists transactions/fraud_flags/reviews plus an outbox row to RDS
   PostgreSQL in the same transaction.
3. A relay drains the `outbox` table into SQS. A Lambda worker consumes
   SQS and fans out alerts via SNS (email/SMS to analysts) and SES (rich
   case-summary email).
4. Cognito issues JWTs for `analyst`/`admin` roles, validated by the ALB
   or the FastAPI service.
5. CloudWatch collects ALB p50/p95 latency, ECS CPU/memory, SQS queue
   depth, and a custom per-rule hit-rate metric (from structured
   `rule_hit` log events), with alarms wired to the SNS topic.
