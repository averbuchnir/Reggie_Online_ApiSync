# Auth Configuration

This folder contains authentication configuration for BigQuery using `.env` file.

## Setup

1. **Create `auth/.env` file** with your Google Cloud credentials:

```env
# Required - From your service account JSON file
GCP_PROJECT_ID=iucc-f4d
GCP_CLIENT_EMAIL=query-from-bq@iucc-f4d.iam.gserviceaccount.com
GCP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDV/0qYhdMbBGIO\\n... (replace \\n with actual newlines)\\n-----END PRIVATE KEY-----

# Optional but recommended
GCP_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GCP_TOKEN_URI=https://oauth2.googleapis.com/token
GCP_auth_provider_x509_cert_url=https://www.googleapis.com/oauth2/v1/certs
GCP_CLIENT_ID=114940523003685681884
GCP_PRIVATE_KEY_ID=70720cec56d8c90319dcd4cbffbe7f8861300fe1
GCP_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/query-from-bq%40iucc-f4d.iam.gserviceaccount.com
```

2. **Copy values from your `read_BQ.json` file:**
   - `project_id` → `GCP_PROJECT_ID`
   - `client_email` → `GCP_CLIENT_EMAIL`
   - `private_key` → `GCP_PRIVATE_KEY` (replace `\n` with `\\n`)
   - Other optional fields as needed

## Environment Variables

### Required:
- `GCP_PROJECT_ID`: Your BigQuery project ID (e.g., "iucc-f4d")
- `GCP_CLIENT_EMAIL`: Service account email from JSON credentials
- `GCP_PRIVATE_KEY`: Private key from JSON (use `\\n` for newlines in .env file)

### Optional:
- `GCP_PRIVATE_KEY_ID`: Private key ID
- `GCP_CLIENT_ID`: Client ID
- `GCP_AUTH_URI`: Auth URI (default provided if not set)
- `GCP_TOKEN_URI`: Token URI (default provided if not set)
- `GCP_auth_provider_x509_cert_url`: Auth provider cert URL
- `GCP_CLIENT_X509_CERT_URL`: Client X509 cert URL

### Alternative Options:
- `CREDENTIALS_JSON`: Full JSON credentials as a string (alternative to individual variables)
- `CREDENTIALS_PATH`: Path to JSON credentials file (alternative to individual variables)

## Priority Order

The code loads credentials in this priority:
1. Individual `.env` variables with `GCP_` prefix (recommended)
2. `CREDENTIALS_JSON` in `.env` (full JSON as string)
3. `CREDENTIALS_PATH` in `.env` (path to JSON file)

## Private Key Format

In your `.env` file, the private key should use `\\n` for newlines:

```
GCP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDV/0qYhdMbBGIO\\nnmH5cKZxIITb5egzqmaIOCU3U2Xq6SvFQ8z9/bfpNO0lX2TA5mgWzjIGKtTjrTdk\\n...\\n-----END PRIVATE KEY-----
```

The code automatically converts `\\n` back to actual newlines when loading credentials.

## Security Note

**Never commit your `.env` file or credentials to version control!**

Make sure these files are in `.gitignore`:
- `auth/.env`
- `auth/read_BQ.json`
- `auth/*.json`

The `.gitignore` file should already exclude these files.

