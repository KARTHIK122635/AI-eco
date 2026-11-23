"""
Google Sheets OAuth 2.0 Client and Authentication Module.
Provides secure authentication, credential management, and harmless connectivity verification.
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any, List

# Ensure unbuffered stdout for interactive prompts and logging
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Minimum necessary scopes required for Phase IV
SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

DEFAULT_CLIENT_SECRETS_FILE = os.path.join("secrets", "google_oauth_client.json")
DEFAULT_TOKEN_FILE = os.path.join("secrets", "google_sheets_token.json")


def load_existing_credentials(token_path: str = DEFAULT_TOKEN_FILE) -> Optional[Credentials]:
    """
    Safely load existing OAuth2 credentials from token file if it exists.
    Refreshes expired credentials if refresh token is present.
    """
    if not os.path.exists(token_path):
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials
            save_credentials_safely(creds, token_path)
        if creds and creds.valid:
            return creds
    except Exception as e:
        logger.warning(f"Failed to load or refresh token from {token_path}: {type(e).__name__}")
    return None


def save_credentials_safely(creds: Credentials, token_path: str = DEFAULT_TOKEN_FILE) -> None:
    """
    Persist OAuth2 credentials to the specified token file in secrets directory.
    Never exposes credential values in logs.
    """
    os.makedirs(os.path.dirname(os.path.abspath(token_path)), exist_ok=True)
    with open(token_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    # On non-Windows platforms, set 0o600 permissions; on Windows, os.chmod is best-effort
    try:
        os.chmod(token_path, 0o600)
    except Exception:
        pass


def authenticate_desktop_oauth(
    client_secrets_path: str = DEFAULT_CLIENT_SECRETS_FILE,
    token_path: str = DEFAULT_TOKEN_FILE,
    port: int = 0,
) -> Credentials:
    """
    Executes the OAuth 2.0 Desktop local server authorization flow.
    Launches browser for user consent and writes tokens to token_path.
    """
    if not os.path.isfile(client_secrets_path):
        raise FileNotFoundError(f"OAuth client secret file not found at: {client_secrets_path}")

    # Check if valid existing credentials exist
    creds = load_existing_credentials(token_path)
    if creds and creds.valid:
        return creds

    # Initialize flow
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes=SCOPES)
    
    # Run local server to complete authorization
    # port=0 selects an available free port
    creds = flow.run_local_server(
        port=port,
        prompt="consent",
        authorization_prompt_message=(
            "\nOpening local web browser for Google Sheets OAuth 2.0 authorization...\n"
            "If your browser does not open automatically, visit this URL:\n{url}\n"
        ),
        success_message="Authentication successful! You may now close this browser window/tab."
    )

    if creds:
        save_credentials_safely(creds, token_path)

    return creds


def get_sheets_service(creds: Credentials) -> Resource:
    """
    Constructs and returns the Google Sheets API v4 Resource.
    """
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def check_connectivity(service: Resource) -> Dict[str, Any]:
    """
    Performs a harmless, read-only connectivity check against Google Sheets API.
    Does NOT create, modify, or delete any spreadsheet.
    
    Uses a dummy non-existent spreadsheet ID to verify:
    1. TLS and API endpoint connectivity
    2. OAuth token acceptance and validity
    3. Proper 404 response indicating valid authenticated access
    """
    dummy_id = "00000000000000000000000000000000000000000000"
    try:
        service.spreadsheets().get(spreadsheetId=dummy_id).execute()
        return {
            "success": True,
            "status": "CONNECTED_UNEXPECTED_200",
            "message": "Connected successfully to Google Sheets API."
        }
    except HttpError as err:
        status_code = err.resp.status
        if status_code == 404:
            # Expected behavior: authentication succeeded, API recognized caller, resource does not exist
            return {
                "success": True,
                "status": "AUTHENTICATED_AND_CONNECTED",
                "http_status": 404,
                "message": (
                    "Successfully authenticated and connected to Google Sheets API v4. "
                    "Endpoints responded with expected HTTP 404 for non-existent test resource. "
                    "Zero spreadsheets created, modified, or deleted."
                )
            }
        elif status_code in (401, 403):
            return {
                "success": False,
                "status": "AUTHENTICATION_FAILED",
                "http_status": status_code,
                "message": f"Authorization error: HTTP {status_code}. Details: {err.error_details}"
            }
        else:
            return {
                "success": False,
                "status": f"HTTP_ERROR_{status_code}",
                "http_status": status_code,
                "message": f"Unexpected HTTP status {status_code} during connectivity check."
            }
    except Exception as e:
        return {
            "success": False,
            "status": "CONNECTION_ERROR",
            "error_type": type(e).__name__,
            "message": str(e)
        }
