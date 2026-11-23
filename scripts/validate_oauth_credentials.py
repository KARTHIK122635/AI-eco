"""
Validation script for Google OAuth Desktop credentials.
Validates JSON structure without printing or exposing any credentials.
"""
import json
import os
import sys

def validate_oauth_client_json(file_path: str = "secrets/google_oauth_client.json") -> bool:
    if not os.path.isfile(file_path):
        print(f"ERROR: File not found at '{file_path}'")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse JSON: {type(e).__name__}")
        return False

    app_type = None
    if "installed" in data:
        app_type = "installed"
    elif "web" in data:
        app_type = "web"

    if app_type is None:
        print("ERROR: Neither 'installed' nor 'web' client application type found in JSON.")
        return False

    print(f"Top-level application type detected: '{app_type}' (Desktop/Installed app format verified: {app_type == 'installed'})")

    cfg = data[app_type]
    required_keys = ["client_id", "client_secret", "auth_uri", "token_uri"]
    all_ok = True

    for k in required_keys:
        present = k in cfg and isinstance(cfg[k], str) and len(cfg[k].strip()) > 0
        if present:
            print(f"  - Key '{k}': PRESENT and non-empty")
        else:
            print(f"  - Key '{k}': MISSING or EMPTY")
            all_ok = False

    redirect_uris = cfg.get("redirect_uris", [])
    if isinstance(redirect_uris, list) and len(redirect_uris) > 0:
        print(f"  - Key 'redirect_uris': PRESENT ({len(redirect_uris)} entries)")
    else:
        print("  - Key 'redirect_uris': WARNING (empty or not a list)")

    if all_ok:
        print("JSON structure validation: PASSED (Zero credential values exposed).")
        return True
    else:
        print("JSON structure validation: FAILED")
        return False

if __name__ == "__main__":
    success = validate_oauth_client_json()
    sys.exit(0 if success else 1)
