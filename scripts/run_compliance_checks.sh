#!/bin/bash
echo "================================"
echo "HIPAA Compliance Checks"
echo "================================"
echo ""

echo "1. Security Group Check"
python3 scripts/compliance/check_security_groups.py
SG_RESULT=$?
echo ""

echo "2. EBS Encryption Check"
python3 scripts/compliance/check_ebs_encryption.py
EBS_RESULT=$?
echo ""

if [ $SG_RESULT -eq 0 ] && [ $EBS_RESULT -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    exit 0
else
    echo "❌ SOME CHECKS FAILED"
    exit 1
fi
