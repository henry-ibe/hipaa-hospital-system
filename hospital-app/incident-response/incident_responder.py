#!/usr/bin/env python3
"""
Automated Incident Response System
Monitors Prometheus metrics and takes automated actions
"""

import requests
import time
import json
import yaml
from datetime import datetime, timedelta
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText

class IncidentResponder:
    def __init__(self, prometheus_url="http://localhost:9090", config_file="alert_rules.yml"):
        self.prometheus_url = prometheus_url
        self.blocked_ips = set()
        self.locked_accounts = {}
        self.incident_log = []
        
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print(f"[{datetime.now()}] Incident Responder Started")
        print(f"Monitoring: {prometheus_url}")
    
    def query_prometheus(self, query):
        """Query Prometheus metrics"""
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': query}
            )
            return response.json()
        except Exception as e:
            print(f"Error querying Prometheus: {e}")
            return None
    
    def check_failed_logins(self):
        """Check for excessive failed login attempts"""
        threshold = self.config['alerts']['failed_login_threshold']['threshold']
        window = self.config['alerts']['failed_login_threshold']['window_minutes']
        
        # Query failed logins in last N minutes
        query = f'increase(hospital_login_attempts_total{{status="failed"}}[{window}m])'
        result = self.query_prometheus(query)
        
        if result and result['status'] == 'success':
            data = result['data']['result']
            if data and len(data) > 0:
                failed_count = float(data[0]['value'][1])
                
                if failed_count >= threshold:
                    self.handle_failed_login_incident(failed_count, threshold)
                    return True
        return False
    
    def check_mfa_brute_force(self):
        """Check for MFA brute force attempts"""
        threshold = self.config['alerts']['mfa_brute_force']['threshold']
        window = self.config['alerts']['mfa_brute_force']['window_minutes']
        
        query = f'increase(hospital_mfa_attempts_total{{status="failed"}}[{window}m])'
        result = self.query_prometheus(query)
        
        if result and result['status'] == 'success':
            data = result['data']['result']
            if data and len(data) > 0:
                failed_count = float(data[0]['value'][1])
                
                if failed_count >= threshold:
                    self.handle_mfa_brute_force(failed_count, threshold)
                    return True
        return False
    
    def handle_failed_login_incident(self, failed_count, threshold):
        """Handle excessive failed login attempts"""
        incident = {
            'timestamp': datetime.now().isoformat(),
            'type': 'EXCESSIVE_FAILED_LOGINS',
            'severity': 'CRITICAL',
            'failed_attempts': int(failed_count),
            'threshold': threshold,
            'action_taken': []
        }
        
        print(f"\n{'='*60}")
        print(f"🚨 SECURITY INCIDENT DETECTED 🚨")
        print(f"Type: Excessive Failed Login Attempts")
        print(f"Count: {int(failed_count)} (Threshold: {threshold})")
        print(f"Time: {incident['timestamp']}")
        print(f"{'='*60}")
        
        # Action 1: Lock the account (simulated)
        if self.config['actions']['lock_account']['enabled']:
            duration = self.config['actions']['lock_account']['duration_minutes']
            self.lock_account("suspicious_user", duration)
            incident['action_taken'].append(f"Account locked for {duration} minutes")
            print(f"✅ Action: Account locked for {duration} minutes")
        
        # Action 2: Log to incident file
        self.log_incident(incident)
        
        # Action 3: Send alert (simulated)
        if self.config['actions']['lock_account']['notify_admin']:
            self.send_alert(incident)
            incident['action_taken'].append("Admin notified")
            print(f"✅ Action: Admin notification sent")
        
        print(f"{'='*60}\n")
        self.incident_log.append(incident)
    
    def handle_mfa_brute_force(self, failed_count, threshold):
        """Handle MFA brute force attempts"""
        incident = {
            'timestamp': datetime.now().isoformat(),
            'type': 'MFA_BRUTE_FORCE',
            'severity': 'CRITICAL',
            'failed_attempts': int(failed_count),
            'threshold': threshold,
            'action_taken': []
        }
        
        print(f"\n{'='*60}")
        print(f"🚨 SECURITY INCIDENT DETECTED 🚨")
        print(f"Type: MFA Brute Force Attack")
        print(f"Count: {int(failed_count)} (Threshold: {threshold})")
        print(f"Time: {incident['timestamp']}")
        print(f"{'='*60}")
        
        # Action: Block source IP (simulated)
        if self.config['actions']['block_ip']['enabled']:
            duration = self.config['actions']['block_ip']['duration_minutes']
            fake_ip = "203.0.113.42"  # Simulated attacker IP
            self.block_ip(fake_ip, duration)
            incident['action_taken'].append(f"IP {fake_ip} blocked for {duration} minutes")
            print(f"✅ Action: IP {fake_ip} blocked for {duration} minutes")
        
        self.log_incident(incident)
        
        if self.config['actions']['block_ip']['notify_admin']:
            self.send_alert(incident)
            incident['action_taken'].append("Admin notified")
            print(f"✅ Action: Admin notification sent")
        
        print(f"{'='*60}\n")
        self.incident_log.append(incident)
    
    def lock_account(self, username, duration_minutes):
        """Lock a user account (simulated - in production, update database)"""
        unlock_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.locked_accounts[username] = unlock_time
        
        # In production, this would:
        # - Update database: UPDATE users SET locked=true WHERE username=?
        # - Set unlock time in cache/DB
        print(f"   → Account '{username}' locked until {unlock_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def block_ip(self, ip_address, duration_minutes):
        """Block an IP address (simulated - in production, update WAF)"""
        unblock_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.blocked_ips.add((ip_address, unblock_time))
        
        # In production, this would:
        # - Add IP to WAF IP set: boto3.client('wafv2').update_ip_set()
        # - Add iptables rule: subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        print(f"   → IP {ip_address} blocked until {unblock_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Simulated WAF update
        with open('blocked_ips.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()}|{ip_address}|{unblock_time.isoformat()}\n")
    
    def log_incident(self, incident):
        """Log incident to file"""
        with open('incidents.log', 'a') as f:
            f.write(json.dumps(incident) + '\n')
    
    def send_alert(self, incident):
        """Send alert notification (simulated)"""
        alert_file = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(alert_file, 'w') as f:
            f.write(f"SECURITY ALERT - {incident['type']}\n")
            f.write(f"="*60 + "\n")
            f.write(f"Timestamp: {incident['timestamp']}\n")
            f.write(f"Severity: {incident['severity']}\n")
            f.write(f"Details: {json.dumps(incident, indent=2)}\n")
            f.write(f"\nActions Taken:\n")
            for action in incident['action_taken']:
                f.write(f"  - {action}\n")
        
        print(f"   → Alert written to {alert_file}")
        
        # In production, this would:
        # - Send SNS notification: sns.publish(TopicArn=..., Message=...)
        # - Send email via SES
        # - Post to Slack webhook
    
    def cleanup_expired_blocks(self):
        """Remove expired IP blocks and account locks"""
        now = datetime.now()
        
        # Cleanup expired IP blocks
        expired_ips = [ip for ip, unblock_time in self.blocked_ips if now >= unblock_time]
        for ip_data in expired_ips:
            self.blocked_ips.remove(ip_data)
            print(f"✅ IP {ip_data[0]} unblocked (timer expired)")
        
        # Cleanup expired account locks
        expired_accounts = [user for user, unlock_time in self.locked_accounts.items() if now >= unlock_time]
        for user in expired_accounts:
            del self.locked_accounts[user]
            print(f"✅ Account '{user}' unlocked (timer expired)")
    
    def get_status(self):
        """Get current incident response status"""
        return {
            'blocked_ips': len(self.blocked_ips),
            'locked_accounts': len(self.locked_accounts),
            'total_incidents': len(self.incident_log),
            'last_check': datetime.now().isoformat()
        }
    
    def run(self, interval_seconds=30):
        """Main monitoring loop"""
        print(f"\n🛡️  Starting Incident Response Monitor (checking every {interval_seconds}s)\n")
        
        while True:
            try:
                # Check for incidents
                self.check_failed_logins()
                self.check_mfa_brute_force()
                
                # Cleanup expired blocks
                self.cleanup_expired_blocks()
                
                # Status update
                status = self.get_status()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: "
                      f"{status['total_incidents']} incidents | "
                      f"{status['blocked_ips']} IPs blocked | "
                      f"{status['locked_accounts']} accounts locked")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Incident Responder Stopped")
                print(f"Total incidents handled: {len(self.incident_log)}")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    # Install required package if needed
    try:
        import yaml
    except ImportError:
        print("Installing PyYAML...")
        import subprocess
        subprocess.run(['pip3', 'install', 'pyyaml', '--break-system-packages'])
        import yaml
    
    responder = IncidentResponder()
    responder.run(interval_seconds=30)
