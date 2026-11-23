"""
Stage 1 Verification Script for Phase IV Google Sheets OAuth & Connectivity.
Checks token validity, scopes, Google Sheets API connectivity without exposing secret values.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.google_sheets_client import (
    SCOPES,
    DEFAULT_CLIENT_SECRETS_FILE,
    DEFAULT_TOKEN_FILE,
    load_existing_credentials,
    get_sheets_service,
    check_connectivity,
)

def verify_stage1():
    print("=" * 70)
    print("STAGE 1 — GOOGLE SHEETS OAUTH & CONNECTIVITY VERIFICATION")
    print("=" * 70)

    # 1. Check dependencies
    deps = ["google.auth", "google_auth_oauthlib", "googleapiclient"]
    deps_ok = True
    for d in deps:
        try:
            __import__(d)
            print(f"[DEP] {d}: OK")
        except ImportError as e:
            print(f"[DEP] {d}: MISSING ({e})")
            deps_ok = False

    # 2. Check files
    print(f"\n[FILE] Client Secret File ({DEFAULT_CLIENT_SECRETS_FILE}): {os.path.isfile(DEFAULT_CLIENT_SECRETS_FILE)}")
    token_exists = os.path.isfile(DEFAULT_TOKEN_FILE)
    print(f"[FILE] Token File ({DEFAULT_TOKEN_FILE}): {token_exists}")

    if not token_exists:
        print("[ERROR] Token file does not exist!")
        return False

    # 3. Inspect token structure safely (no secrets printed)
    with open(DEFAULT_TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    token_keys = list(token_data.keys())
    print(f"\n[TOKEN] Token keys present: {token_keys}")
    has_token = bool(token_data.get("token"))
    has_refresh = bool(token_data.get("refresh_token"))
    has_client_id = bool(token_data.get("client_id"))
    has_client_secret = bool(token_data.get("client_secret"))
    token_scopes = token_data.get("scopes", [])

    print(f"[TOKEN] Access Token Present: {has_token}")
    print(f"[TOKEN] Refresh Token Present: {has_refresh}")
    print(f"[TOKEN] Client ID Present: {has_client_id}")
    print(f"[TOKEN] Client Secret Present: {has_client_secret}")
    print(f"[TOKEN] Granted Scopes: {token_scopes}")

    required_scopes_ok = all(s in token_scopes for s in SCOPES)
    print(f"[TOKEN] All Required Scopes Present: {required_scopes_ok}")

    # 4. Load credentials and check validity
    creds = load_existing_credentials(DEFAULT_TOKEN_FILE)
    if not creds:
        print("[ERROR] Failed to load credentials from token file.")
        return False

    print(f"\n[AUTH] Credentials loaded successfully.")
    print(f"[AUTH] Credentials Valid: {creds.valid}")
    print(f"[AUTH] Credentials Expired: {creds.expired}")

    # 5. Verify live Google Sheets API connectivity (harmless read-only check)
    print("\n[API] Testing live Google Sheets API v4 connectivity...")
    service = get_sheets_service(creds)
    conn_result = check_connectivity(service)

    print(f"[API] Connectivity Status: {conn_result.get('status')}")
    print(f"[API] HTTP Status Code  : {conn_result.get('http_status')}")
    print(f"[API] Message           : {conn_result.get('message')}")
    print(f"[API] Success           : {conn_result.get('success')}")

    # 6. Check Drive API identity / user info if accessible under scopes
    try:
        from googleapiclient.discovery import build
        drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)
        about = drive_service.about().get(fields="user(displayName,emailAddress)").execute()
        user_info = about.get("user", {})
        email = user_info.get("emailAddress", "Unknown")
        name = user_info.get("displayName", "Unknown")
        print(f"\n[ACCOUNT] Authenticated User: {name} ({email})")
    except Exception as e:
        print(f"\n[ACCOUNT] Drive about check skipped or restricted under scopes ({type(e).__name__})")

    overall_success = deps_ok and token_exists and required_scopes_ok and creds.valid and conn_result.get("success", False)
    print("\n" + "=" * 70)
    print(f"STAGE 1 OVERALL STATUS: {'PASSED' if overall_success else 'FAILED'}")
    print("=" * 70)
    return overall_success

if __name__ == "__main__":
    ok = verify_stage1()
    sys.exit(0 if ok else 1)
