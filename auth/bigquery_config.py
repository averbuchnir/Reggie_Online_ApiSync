"""
BigQuery configuration and client setup.
Loads credentials from environment variables or .env file.
"""
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from pathlib import Path
from dotenv import load_dotenv


def load_credentials():
    """
    Load BigQuery credentials from .env file.
    Constructs credentials from individual environment variables.
    
    Required .env variables:
    - PROJECT_ID or BIGQUERY_PROJECT
    - CLIENT_EMAIL
    - PRIVATE_KEY (can be with \n for newlines or use PRIVATE_KEY_ID)
    
    Optional .env variables:
    - PRIVATE_KEY_ID
    - CLIENT_ID
    - AUTH_URI (default: https://accounts.google.com/o/oauth2/auth)
    - TOKEN_URI (default: https://oauth2.googleapis.com/token)
    - AUTH_PROVIDER_X509_CERT_URL (default: https://www.googleapis.com/oauth2/v1/certs)
    - CLIENT_X509_CERT_URL
    - UNIVERSE_DOMAIN (default: googleapis.com)
    
    Alternative: CREDENTIALS_JSON (full JSON as string) or CREDENTIALS_PATH (path to JSON file)
    
    Returns:
        service_account.Credentials: Authenticated credentials
    """
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        raise FileNotFoundError(
            f".env file not found at {env_path}. Please create .env file with required credentials."
        )
    
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")
    
    # Check if full JSON is provided as string
    if os.getenv("CREDENTIALS_JSON"):
        import json
        print("Loading credentials from CREDENTIALS_JSON environment variable")
        credentials_json = json.loads(os.getenv("CREDENTIALS_JSON"))
        credentials = service_account.Credentials.from_service_account_info(credentials_json)
        print(f"Credentials loaded successfully from CREDENTIALS_JSON")
        return credentials
    
    # Check if path to JSON file is provided
    credentials_path = os.getenv("CREDENTIALS_PATH")
    if credentials_path:
        if not os.path.isabs(credentials_path):
            credentials_path = str(Path(__file__).parent / credentials_path)
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
        
        print(f"Loading credentials from file: {credentials_path}")
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        print(f"Credentials loaded successfully from file")
        return credentials
    
    # Build credentials from individual .env variables (with GCP_ prefix)
    print("Constructing credentials from .env variables")
    
    # Required variables - check GCP_ prefix first, then fallback to old names
    project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("PROJECT_ID") or os.getenv("BIGQUERY_PROJECT")
    client_email = os.getenv("GCP_CLIENT_EMAIL") or os.getenv("CLIENT_EMAIL")
    private_key = os.getenv("GCP_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID must be set in .env file")
    if not client_email:
        raise ValueError("GCP_CLIENT_EMAIL must be set in .env file")
    if not private_key:
        raise ValueError("GCP_PRIVATE_KEY must be set in .env file")
    
    # Replace \\n with actual newlines in private key (for .env file format)
    private_key = private_key.replace('\\n', '\n')
    
    # Build credentials dictionary
    credentials_info = {
        "type": "service_account",
        "project_id": project_id,
        "private_key": private_key,
        "client_email": client_email,
    }
    
    # Optional variables - check GCP_ prefix first, then fallback
    private_key_id = os.getenv("GCP_PRIVATE_KEY_ID") or os.getenv("PRIVATE_KEY_ID")
    if private_key_id:
        credentials_info["private_key_id"] = private_key_id
    
    client_id = os.getenv("GCP_CLIENT_ID") or os.getenv("CLIENT_ID")
    if client_id:
        credentials_info["client_id"] = client_id
    
    credentials_info["auth_uri"] = os.getenv("GCP_AUTH_URI") or os.getenv("AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    credentials_info["token_uri"] = os.getenv("GCP_TOKEN_URI") or os.getenv("TOKEN_URI", "https://oauth2.googleapis.com/token")
    credentials_info["auth_provider_x509_cert_url"] = os.getenv(
        "GCP_AUTH_PROVIDER_X509_CERT_URL") or os.getenv("GCP_auth_provider_x509_cert_url") or os.getenv(
        "AUTH_PROVIDER_X509_CERT_URL", 
        "https://www.googleapis.com/oauth2/v1/certs"
    )
    
    client_x509_cert_url = os.getenv("GCP_CLIENT_X509_CERT_URL") or os.getenv("CLIENT_X509_CERT_URL")
    if client_x509_cert_url:
        credentials_info["client_x509_cert_url"] = client_x509_cert_url
    
    credentials_info["universe_domain"] = os.getenv("GCP_UNIVERSE_DOMAIN") or os.getenv("UNIVERSE_DOMAIN", "googleapis.com")
    
    # Create credentials from the dictionary
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    print(f"Credentials loaded successfully from .env variables")
    return credentials


def get_bigquery_client():
    """
    Initialize and return a BigQuery client.
    Uses credentials from .env file and project from .env.
    
    Returns:
        bigquery.Client: Authenticated BigQuery client
    """
    credentials = load_credentials()
    
    # Get project ID from .env (already loaded in load_credentials)
    # Priority: GCP_PROJECT_ID > PROJECT_ID > BIGQUERY_PROJECT > default
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("PROJECT_ID") or os.getenv("BIGQUERY_PROJECT") or "iucc-f4d"
    
    print(f"Initializing BigQuery client with project: {project_id}")
    if hasattr(credentials, 'service_account_email'):
        print(f"Using credentials from service account: {credentials.service_account_email}")
    
    # Initialize BigQuery client with credentials and project
    client = bigquery.Client(credentials=credentials, project=project_id)
    return client


# Global client instance (lazy loaded)
_bq_client = None


def get_client():
    """
    Get or create the global BigQuery client instance.
    
    Returns:
        bigquery.Client: BigQuery client
    """
    global _bq_client
    if _bq_client is None:
        _bq_client = get_bigquery_client()
    return _bq_client

