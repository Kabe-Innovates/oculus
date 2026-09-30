#!/usr/bin/env python3
"""
Oculus Fraud Detection Platform — Automated AWS EC2 Deployment Script

Provisions a cloud instance on AWS EC2 in ap-south-1 with:
- Security Group allowing HTTP (port 80) and SSH (port 22)
- Docker & Docker Compose automated installation via cloud-init
- Auto-cloning of https://github.com/Kabe-Innovates/oculus.git
- Ingestion of environment configuration & AWS SNS alerting credentials
- Single command deployment with public URL output
"""

import os
import sys
import time
import base64
import argparse
import boto3
from botocore.exceptions import ClientError


def get_aws_credentials():
    """Retrieve active AWS credentials from session or environment."""
    session = boto3.Session()
    creds = session.get_credentials()
    if not creds:
        return "", "", ""
    frozen = creds.get_frozen_credentials()
    return frozen.access_key, frozen.secret_key, frozen.token or ""


def deploy(region="ap-south-1", instance_type="t3.small"):
    print(f"[*] Initializing AWS EC2 deployment in region: {region}...")
    ec2_client = boto3.client("ec2", region_name=region)
    ec2_resource = boto3.resource("ec2", region_name=region)

    # 1. Get Default VPC
    print("[*] Resolving default VPC...")
    vpcs = ec2_client.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])
    if not vpcs["Vpcs"]:
        print("[!] No default VPC found. Looking for any available VPC...")
        vpcs = ec2_client.describe_vpcs()
        if not vpcs["Vpcs"]:
            print("[X] Error: No VPC available in this region.")
            sys.exit(1)
    vpc_id = vpcs["Vpcs"][0]["VpcId"]
    print(f"[+] Using VPC: {vpc_id}")

    # 2. Configure Security Group
    sg_name = "oculus-security-group"
    sg_id = None
    try:
        sgs = ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [sg_name]}, {"Name": "vpc-id", "Values": [vpc_id]}]
        )
        if sgs["SecurityGroups"]:
            sg_id = sgs["SecurityGroups"][0]["GroupId"]
            print(f"[+] Found existing Security Group: {sg_id}")
    except ClientError as e:
        print(f"[!] Error checking security groups: {e}")

    if not sg_id:
        print(f"[*] Creating Security Group '{sg_name}'...")
        res = ec2_client.create_security_group(
            GroupName=sg_name,
            Description="Security group for Oculus Fraud Platform (HTTP, WebSocket, SSH)",
            VpcId=vpc_id,
        )
        sg_id = res["GroupId"]
        print(f"[+] Created Security Group: {sg_id}")

        # Authorize ingress rules: HTTP (80) and SSH (22)
        print("[*] Configuring firewall ingress rules (ports 80 and 22)...")
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTP Web and Console access"}],
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "SSH administrative access"}],
                },
            ],
        )

    # 3. Configure Key Pair
    key_name = "oculus-keypair"
    key_path = os.path.expanduser(f"~/.ssh/{key_name}.pem")
    try:
        ec2_client.describe_key_pairs(KeyNames=[key_name])
        print(f"[+] Using existing EC2 Key Pair: {key_name}")
    except ClientError:
        print(f"[*] Creating new EC2 Key Pair: {key_name}...")
        key_pair = ec2_client.create_key_pair(KeyName=key_name)
        os.makedirs(os.path.expanduser("~/.ssh"), exist_ok=True)
        with open(key_path, "w") as f:
            f.write(key_pair["KeyMaterial"])
        os.chmod(key_path, 0o400)
        print(f"[+] Key pair saved locally to {key_path}")

    # 4. Resolve Ubuntu 22.04 LTS AMI
    print("[*] Resolving latest Ubuntu 22.04 LTS AMI...")
    images = ec2_client.describe_images(
        Filters=[
            {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]},
            {"Name": "state", "Values": ["available"]},
            {"Name": "virtualization-type", "Values": ["hvm"]},
        ],
        Owners=["099720109477"],  # Canonical
    )
    sorted_images = sorted(images["Images"], key=lambda x: x["CreationDate"], reverse=True)
    if not sorted_images:
        print("[X] Error: Could not locate Ubuntu 22.04 AMI in this region.")
        sys.exit(1)
    ami_id = sorted_images[0]["ImageId"]
    print(f"[+] Selected AMI: {ami_id} ({sorted_images[0]['Name']})")

    # 5. Read local environment secrets to propagate to cloud instance
    env_file = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
    sns_topic_arn = ""
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("SNS_TOPIC_ARN="):
                    sns_topic_arn = line.strip().split("=", 1)[1]

    aws_access_key, aws_secret_key, aws_token = get_aws_credentials()

    # 6. Generate Cloud-Init User Data Script
    user_data_script = f"""#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "[*] Initializing system update and Docker setup..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release git

# Install Docker official repository
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

systemctl enable docker
systemctl start docker

# Clone repository
echo "[*] Cloning Oculus repository..."
rm -rf /opt/oculus
git clone https://github.com/Kabe-Innovates/oculus.git /opt/oculus
cd /opt/oculus

# Configure production environment variables
cat << 'EOF' > /opt/oculus/.env
SNS_TOPIC_ARN={sns_topic_arn}
AWS_REGION={region}
AWS_ACCESS_KEY_ID={aws_access_key}
AWS_SECRET_ACCESS_KEY={aws_secret_key}
EOF

cat << 'EOF' > /opt/oculus/backend/.env
SNS_TOPIC_ARN={sns_topic_arn}
AWS_REGION={region}
AWS_ACCESS_KEY_ID={aws_access_key}
AWS_SECRET_ACCESS_KEY={aws_secret_key}
EOF

# Launch Docker Compose Stack
echo "[*] Starting Oculus Docker Compose Stack..."
docker compose up -d --build

echo "[+] Oculus Fraud Platform deployed and active on port 80!"
"""

    encoded_user_data = base64.b64encode(user_data_script.encode("utf-8")).decode("utf-8")

    # 7. Launch Instance
    print(f"[*] Launching EC2 instance ({instance_type})...")
    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        UserData=user_data_script,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "Oculus-Fraud-Platform"},
                    {"Key": "Project", "Value": "Oculus"},
                ],
            }
        ],
    )
    instance = instances[0]
    print(f"[+] Instance initiated: {instance.id}")
    print("[*] Waiting for instance to transition to RUNNING state...")
    instance.wait_until_running()
    instance.reload()

    public_ip = instance.public_ip_address
    public_dns = instance.public_dns_name

    print("\n" + "=" * 70)
    print("  OCULUS FRAUD DETECTION PLATFORM — AWS DEPLOYMENT COMPLETE")
    print("=" * 70)
    print(f"  Instance ID:   {instance.id}")
    print(f"  Public IPv4:   {public_ip}")
    print(f"  Public DNS:    {public_dns}")
    print(f"  Live Console:  http://{public_ip}/")
    print(f"  REST API Docs: http://{public_ip}/docs")
    print(f"  WebSocket:     ws://{public_ip}/ws/transactions")
    print("=" * 70)
    print("\nNote: The instance is currently building the containers via cloud-init.")
    print("It will be fully live and accepting traffic in approximately 2 to 3 minutes.")
    print(f"SSH access (if needed): ssh -i {key_path} ubuntu@{public_ip}")
    print("=" * 70 + "\n")

    return public_ip, public_dns


def main():
    parser = argparse.ArgumentParser(description="Deploy Oculus to AWS EC2")
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1)")
    parser.add_argument("--instance-type", default="t3.small", help="EC2 instance type (default: t3.small)")
    args = parser.parse_args()

    deploy(region=args.region, instance_type=args.instance_type)


if __name__ == "__main__":
    main()
