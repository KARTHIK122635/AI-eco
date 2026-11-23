"""
CLI Script for Phase IV Google Sheets OAuth 2.0 Setup and Read-Only Verification.
"""

import sys
import os
import json

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.google_sheets_client import (
    SCOPES,
    DEFAULT_CLIENT_SECRETS_FILE,
    DEFAULT_TOKEN_FILE,
    load_existing_credentials,
    authenticate_desktop_oauth,
    get_sheets_service,
    check_connectivity,
)

def run_setup() -> bool:
    print("=" * 70)
    print("PHASE IV — GOOGLE SHEETS OAUTH 2.0 AUTHENTICATION & CONNECTIVITY SETUP")
    print("=" * 70)
    print(f"Client Secrets File : {DEFAULT_CLIENT_SECRETS_FILE}")
    print(f"Token Output File   : {DEFAULT_TOKEN_FILE}")
    print("\nIntended OAuth 2.0 Scopes:")
    for scope in SCOPES:
        print(f"  - {scope}")
    print("=" * 70)

    if not os.path.isfile(DEFAULT_CLIENT_SECRETS_FILE):
        print(f"ERROR: Client secret file not found: {DEFAULT_CLIENT_SECRETS_FILE}")
        return False

    # Check if already authenticated
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    if creds and creds.valid:
        print("\n[OK] Valid existing credentials discovered. Re-using cached token.")
    else:
        print("\n[INFO] Launching OAuth 2.0 Desktop local server flow...")
        print("[INFO] Your default web browser will open for Google consent.")
        print("[INFO] Please sign in with your authorized Google test account and approve scopes.")
        try:
            creds = authenticate_desktop_oauth(
                client_secrets_path=DEFAULT_CLIENT_SECRETS_FILE,
                token_path=DEFAULT_TOKEN_FILE
            )
            print("[OK] OAuth flow completed and tokens saved securely to secrets directory.")
        except Exception as e:
            print(f"\n[ERROR] OAuth authentication flow failed: {type(e).__name__}: {e}")
            return False

    print("\n[INFO] Performing harmless read-only Google Sheets API connectivity check...")
    try:
        service = get_sheets_service(creds)
        res = check_connectivity(service)
        print(f"Status        : {res.get('status')}")
        print(f"HTTP Code     : {res.get('http_status')}")
        print(f"Message       : {res.get('message')}")
        if res.get("success"):
            print("\n[SUCCESS] Google Sheets API connectivity verified successfully!")
            print("[SAFETY] Zero spreadsheets created, modified, or deleted.")
            return True
        else:
            print(f"\n[FAILURE] Connectivity check failed.")
            return False
    except Exception as e:
        print(f"\n[ERROR] Connectivity check failed with exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = run_setup()
    sys.exit(0 if success else 1)
