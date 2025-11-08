#!/usr/bin/env python3
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

print("Checking security groups...")
sgs = ec2.describe_security_groups()

violations = []
for sg in sgs['SecurityGroups']:
    for rule in sg.get('IpPermissions', []):
        for ip_range in rule.get('IpRanges', []):
            if ip_range['CidrIp'] == '0.0.0.0/0' and rule.get('ToPort') != 443:
                violations.append(f"SG {sg['GroupId']}: Port {rule.get('ToPort')} open to 0.0.0.0/0")

if violations:
    print("❌ VIOLATIONS FOUND:")
    for v in violations:
        print(f"  - {v}")
    exit(1)
else:
    print("✅ All security groups compliant")
