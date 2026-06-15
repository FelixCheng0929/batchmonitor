# -*- coding: utf-8 -*-
"""
create_sharepoint_list.py
=========================
One-click script to create the IFMonitorLog SharePoint List
with all 14 required fields for BatchMonitor.

Usage:
  python create_sharepoint_list.py

  Edit the config section below first, then run.

Zero dependencies - stdlib only (urllib).
"""

import json, urllib.request, urllib.parse, urllib.error, sys, os

# ============================================================
#  CONFIG - Edit these values before running
# ============================================================

# Option A: Client Credentials (App-only, recommended)
AUTH_MODE = "client_credentials"
TENANT_ID = "9e0bc7b5-fef7-40a8-9534-cd9423f74118"   # Hitachi
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
AUTHORITY = "https://login.microsoftonline.com/" + TENANT_ID + "/oauth2/v2.0/token"
SCOPE = "https://graph.microsoft.com/.default"

# Option B: ROPC (username + password)
# AUTH_MODE = "ropc"
# TENANT_ID = "9e0bc7b5-fef7-40a8-9534-cd9423f74118"
# USERNAME = "j.chen@itg.hitachi.cn"
# PASSWORD = "YOUR_PASSWORD"
# CLIENT_ID = "14d82adc-01f2-4e59-b69e-1d0a3c0b3a4c"
# AUTHORITY = "https://login.microsoftonline.com/organizations/oauth2/v2.0/token"
# SCOPE = "Sites.ReadWrite.All offline_access"

# SharePoint site URL
SITE_URL = "https://hitachigroup.sharepoint.com/sites/bsbu-it-fs/hand"

# List name to create
LIST_NAME = "IFMonitorLog"

# ============================================================
#  AUTH
# ============================================================

def get_token_ropc():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "scope": SCOPE,
    }).encode()
    req = urllib.request.Request(AUTHORITY, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        tok = json.loads(resp.read().decode())
    if "access_token" not in tok:
        raise RuntimeError("ROPC failed: " + json.dumps(tok, indent=2)[:500])
    return tok["access_token"]

def get_token_cc():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": SCOPE,
    }).encode()
    req = urllib.request.Request(AUTHORITY, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        tok = json.loads(resp.read().decode())
    if "access_token" not in tok:
        raise RuntimeError("Client Credentials failed: " + json.dumps(tok, indent=2)[:500])
    return tok["access_token"]

# ============================================================
#  GRAPH API HELPERS
# ============================================================

def graph_get(token, url):
    req = urllib.request.Request(url,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def graph_post(token, url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

# ============================================================
#  LIST COLUMN DEFINITIONS
# ============================================================

COLUMNS = [
    {"name": "DbId",          "number": {}},
    {"name": "BatchName",     "text": {}},
    {"name": "StartTime",     "dateTime": {"format": "dateTime"}},
    {"name": "EndTime",       "dateTime": {"format": "dateTime"}},
    {"name": "Duration",      "number": {}},
    {"name": "TotalCount",    "number": {}},
    {"name": "SuccessCount",  "number": {}},
    {"name": "ErrorCount",    "number": {}},
    {"name": "WarningCount",  "number": {}},
    {"name": "Result",        "choice": {"choices": ["異常", "警告", "正常"], "allowTextEntry": False}},
    {"name": "ErrorMsg",      "text": {"allowMultipleLines": True, "maxLength": 0}},
    {"name": "LogFile",       "text": {}},
    {"name": "ExecDayNo",     "number": {}},
    {"name": "SyncTime",      "dateTime": {"format": "dateTime"}},
]

# ============================================================
#  MAIN
# ============================================================

def main():
    print("=== Create SharePoint List ===")
    print("Site: " + SITE_URL)
    print("List: " + LIST_NAME)
    print("Auth: " + AUTH_MODE)
    print()

    # 1. Auth
    print("[1/4] Authenticating...")
    try:
        if AUTH_MODE == "client_credentials":
            token = get_token_cc()
        else:
            token = get_token_ropc()
        print("  OK - Token acquired")
    except Exception as e:
        print("  FAIL - " + str(e)[:300])
        print()
        print("Hint: For Client Credentials, make sure:")
        print("  1. App is registered in Azure Portal")
        print("  2. API permission Sites.ReadWrite.All is GRANTED (admin consent)")
        print("  3. client_id and client_secret are correct")
        return

    # 2. Get site
    print("[2/4] Resolving site...")
    try:
        uri = urllib.parse.urlparse(SITE_URL)
        path = uri.path.strip("/")
        site = graph_get(token,
            "https://graph.microsoft.com/v1.0/sites/" + uri.hostname + ":/" + path)
        site_id = site["id"]
        print("  Site: " + site.get("displayName", site.get("name", "N/A")))
        print("  ID: " + site_id[:40] + "...")
    except Exception as e:
        print("  FAIL - " + str(e)[:300])
        return

    # 3. Check if list exists
    print("[3/4] Checking list...")
    try:
        lst = graph_get(token,
            "https://graph.microsoft.com/v1.0/sites/" + site_id + "/lists/" + LIST_NAME)
        print("  List ALREADY EXISTS!")
        print("  URL: " + lst.get("webUrl", ""))
        print()
        print("No action needed. List is ready for BatchMonitor.")
        return
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("  List not found. Creating...")
        else:
            body = e.read().decode()
            print("  Error " + str(e.code) + ": " + body[:300])
            return

    # 4. Create list
    print("[4/4] Creating list with 14 columns...")
    try:
        body = {
            "displayName": LIST_NAME,
            "columns": COLUMNS,
            "list": {"template": "genericList"},
        }
        created = graph_post(token,
            "https://graph.microsoft.com/v1.0/sites/" + site_id + "/lists", body)
        print("  CREATED!")
        print("  URL: " + created.get("webUrl", ""))
        print("  ID: " + created.get("id", ""))
    except Exception as e:
        print("  FAIL - " + str(e)[:500])
        print()
        print("If Sites.ReadWrite.All is missing, go to Azure Portal -> App -> API Permissions")
        return

    print()
    print("=== DONE ===")
    print("List is ready. Update config_monitor.json with:")
    print('  "siteUrl": "' + SITE_URL + '"')
    print('  "listName": "' + LIST_NAME + '"')

if __name__ == "__main__":
    main()
    print()
    input("Press Enter to exit...")