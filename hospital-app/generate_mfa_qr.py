#!/usr/bin/env python3
import pyotp
import qrcode

# MFA secret for all test users
SECRET = "JBSWY3DPEHPK3PXP"

users = {
    "dr.smith": "Dr. Sarah Smith",
    "nurse.johnson": "Nurse Emily Johnson", 
    "admin": "Admin Michael Chen",
    "billing.davis": "Billing Jessica Davis",
    "lab.wilson": "Lab Robert Wilson",
    "reception.brown": "Reception Lisa Brown"
}

print("=" * 60)
print("Mount Sinai Hospital - MFA Setup")
print("=" * 60)
print()

for username, name in users.items():
    # Generate provisioning URI
    totp = pyotp.TOTP(SECRET)
    uri = totp.provisioning_uri(
        name=username,
        issuer_name="Mount Sinai Hospital"
    )
    
    print(f"User: {name} ({username})")
    print(f"Secret: {SECRET}")
    print(f"URI: {uri}")
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    # Save QR code
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"mfa_qr_{username}.png"
    img.save(filename)
    print(f"QR Code saved: {filename}")
    print()

print("=" * 60)
print("Setup Instructions:")
print("1. Download the QR code images to your computer")
print("2. Open Google Authenticator app on your phone")
print("3. Tap '+' to add account")
print("4. Choose 'Scan QR code'")
print("5. Scan any of the QR codes (they all use same secret)")
print("6. Use the 6-digit code from the app to login")
print("=" * 60)
