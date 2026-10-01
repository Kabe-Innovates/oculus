# Oculus AWS Architecture

Real-time payment fraud decision and review platform. Single region
`ap-south-1`, 2 Availability Zones, no cross-region components.

## Diagram

```mermaid
flowchart TB
    U["Internet / Analyst Browser"]

    U -->|HTTPS| CF["CloudFront Distribution"]
    CF -->|static assets| S3["S3 Bucket<br/>(private, OAC)<br/>React SPA"]
    CF -->|/api/*, /ws/*<br/>HTTPS + WebSocket| WAF["AWS WAFv2 WebACL"]

    subgraph VPC["VPC 10.20.0.0/16"]
        WAF --> ALB["Application Load Balancer<br/>sg: alb-sg"]

        subgraph AZ1["Availability Zone 1"]
            subgraph PubSub1["Public Subnet · sg: alb-sg"]
                ALBn1["ALB node"]
            end
            subgraph PrivSub1["Private Subnet"]
                ECS1["ECS Fargate task<br/>FastAPI · sg: ecs-sg"]
            end
        end

        subgraph AZ2["Availability Zone 2"]
            subgraph PubSub2["Public Subnet · sg: alb-sg"]
                ALBn2["ALB node"]
            end
            subgraph PrivSub2["Private Subnet"]
                ECS2["ECS Fargate task<br/>FastAPI · sg: ecs-sg"]
            end
        end

        ALB --> ALBn1 & ALBn2
        ALBn1 --> ECS1
        ALBn2 --> ECS2

        ECS1 & ECS2 --> RDS["RDS PostgreSQL<br/>(Multi-AZ) · sg: rds-sg"]
        ECS1 & ECS2 --> Redis["ElastiCache Redis<br/>sg: redis-sg"]
    end

    RDS --> Outbox["outbox table"]
    Outbox --> SQS["SQS outbox queue"]
    SQS -.on failure.-> DLQ["SQS DLQ"]
    SQS --> Lambda["Lambda outbox worker"]
    Lambda --> SNS["SNS Topic<br/>fraud-alerts"]
    Lambda --> SES["SES<br/>case-summary email"]
    SNS -->|email/SMS| U
    SES -->|email| U

    Cognito["Cognito User Pool<br/>analyst / admin groups"] -.auth (JWT).-> ALB
    Secrets["Secrets Manager<br/>RDS creds + app config"] -.GetSecretValue.-> ECS1
    Secrets -.GetSecretValue.-> ECS2
    ECS1 & ECS2 -.sns:Publish only.-> SNS

    CW["CloudWatch<br/>p50/p95 latency, per-rule<br/>hit rate, alarms"] -.metrics/logs.-> ALB
    CW -.metrics/logs.-> ECS1
    CW -.metrics/logs.-> ECS2
```

## Security boundaries

- **VPC**: single VPC `10.20.0.0/16`, 2 AZs (`ap-south-1a`, `ap-south-1b`).
- **Public subnets** (one per AZ): host the ALB only. `map_public_ip_on_launch
  = true`. Route to an Internet Gateway.
- **Private subnets** (one per AZ): host ECS Fargate tasks, RDS PostgreSQL,
  and ElastiCache Redis. No public IPs. Route to NAT Gateways (one per AZ)
  for outbound-only internet access (image pulls, AWS API calls).
- **Security groups** (trust boundaries shown in the diagram):
  - `alb-sg`: ingress 80/443 from `0.0.0.0/0` — the only internet-facing SG.
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
   SQS (failed messages route to the DLQ after 5 receives) and fans out
   alerts via SNS (email/SMS to analysts) and SES (rich case-summary
   email).
4. Cognito issues JWTs for `analyst`/`admin` roles, validated by the ALB
   or the FastAPI service.
5. CloudWatch collects ALB p50/p95 latency, ECS CPU/memory, SQS queue
   depth, and a custom per-rule hit-rate metric (from structured
   `rule_hit` log events), with alarms wired to the SNS topic.
