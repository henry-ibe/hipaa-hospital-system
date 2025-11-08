#!/usr/bin/env python3
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

print("Checking EBS volumes...")
volumes = ec2.describe_volumes()

violations = []
for vol in volumes['Volumes']:
    if not vol['Encrypted']:
        violations.append(f"Volume {vol['VolumeId']}: Not encrypted")

if violations:
    print("❌ VIOLATIONS FOUND:")
    for v in violations:
        print(f"  - {v}")
    exit(1)
else:
    print("✅ All EBS volumes encrypted")
