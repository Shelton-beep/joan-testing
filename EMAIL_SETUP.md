# Email Notification Setup Guide

## Overview
The Zero-Trust Anomaly Detection system sends email alerts to `zerotrustalliance@gmail.com` when anomalies are detected.

## Configuration

### Option 1: Gmail SMTP (Recommended)

**⚠️ IMPORTANT: You MUST use a Gmail App Password, NOT your regular Gmail password!**

1. **Enable 2-Step Verification (Required First):**
   - Go to https://myaccount.google.com/security
   - Under "Signing in to Google", click "2-Step Verification"
   - Follow the prompts to enable it (you'll need your phone)

2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as the device, enter "Zero-Trust System"
   - Click "Generate"
   - **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
   - Remove spaces when using it: `abcdefghijklmnop`

3. **Create .env file in project root:**
   ```bash
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```
   
   **Note:** Do NOT use `export` in the .env file. Just use `KEY=value` format.

### Option 2: Other Email Providers

**Outlook/Hotmail:**
```bash
export EMAIL_USER="your-email@outlook.com"
export EMAIL_PASSWORD="your-password"
export SMTP_SERVER="smtp-mail.outlook.com"
export SMTP_PORT="587"
```

**Custom SMTP:**
```bash
export EMAIL_USER="your-email@domain.com"
export EMAIL_PASSWORD="your-password"
export SMTP_SERVER="smtp.yourdomain.com"
export SMTP_PORT="587"
```

## Testing

To test email functionality, trigger an anomaly in the Login UI:
1. Set bytes_transferred > 5GB, OR
2. Use parameters that trigger model-based anomaly detection

You should receive an email at `zerotrustalliance@gmail.com` with full anomaly details.

## Email Content

Each alert includes:
- Event timestamp and details
- User, device, IP, and location information
- Anomaly classification and reason
- Top contributing factors (SHAP values)
- Recommended security actions

## Troubleshooting

**Email not sending:**
1. Verify environment variables are set: `echo $EMAIL_USER`
2. Check Gmail app password is correct
3. Ensure 2FA is enabled on Gmail account
4. Check firewall/network allows SMTP connections

**Security Note:**
Never commit email credentials to version control. Use environment variables or a secure secrets manager.

