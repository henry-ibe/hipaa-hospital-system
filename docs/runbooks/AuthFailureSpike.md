# Runbook: AuthFailureSpike

## Summary
Failed authentication attempts exceed 0.5 per second — possible brute force attack.

## Impact
- Potential unauthorized access attempt
- HIPAA breach risk if successful

## Severity
Warning — P2

## Immediate Steps
1. Check which IPs are failing:
```bash
   sudo journalctl -u hospital-app | grep "Invalid credentials" | tail -30
```
2. Check if it is a broken integration or real attack
3. If attack — block IP at security group level:
```bash
   aws ec2 revoke-security-group-ingress \
     --group-id sg-0695e334fdacf2e70 \
     --protocol tcp --port 8000 --cidr <ATTACKER-IP>/32
```
4. Notify security team

## Escalation
If successful logins follow failed attempts — escalate to security team immediately. Potential breach in progress.
