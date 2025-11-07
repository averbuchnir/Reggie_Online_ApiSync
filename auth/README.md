# Auth Configuration

This folder contains authentication configuration for BigQuery using `.env` file.

## Setup

1. **Create `auth/.env` file** with your Google Cloud credentials:


```env
# Required - From your service account JSON file
GCP_PROJECT_ID=project_name
GCP_CLIENT_EMAIL=
GCP_PRIVATE_KEY=-

# Optional but recommended
GCP_AUTH_URI=
GCP_TOKEN_URI=
GCP_auth_provider_x509_cert_url=
GCP_CLIENT_ID=
GCP_PRIVATE_KEY_ID=
GCP_CLIENT_X509_CERT_URL=
```

2. **Copy values from your `read_BQ.json` file:**
   - `project_id` → `GCP_PROJECT_ID`
   - `client_email` → `GCP_CLIENT_EMAIL`
   - `private_key` → `GCP_PRIVATE_KEY` (replace `\n` with `\\n`)
   - Other optional fields as needed

## Environment Variables

### Required:
- `GCP_PROJECT_ID`: Your BigQuery project ID (e.g., "project_name")
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
GCP_PRIVATE_KEY=
```

The code automatically converts `\\n` back to actual newlines when loading credentials.

## Security Note

**Never commit your `.env` file or credentials to version control!**

Make sure these files are in `.gitignore`:
- `auth/.env`
- `auth/read_BQ.json`
- `auth/*.json`

The `.gitignore` file should already exclude these files.

