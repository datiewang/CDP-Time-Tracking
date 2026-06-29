import os
import json
import csv
import re
import urllib.parse
from datetime import datetime
from collections import defaultdict
import requests
import msal

# MSAL Configuration
TOKEN_CACHE_FILE = "token_cache.bin"
SCOPES = ["Calendars.Read", "Calendars.Read.Shared", "User.Read"]
KEYWORDS = ["CDP", "IRU", "AZDS", "SHIJI", "QUALTRICS", "LOYALTY", "INTEGRATION", "TABLECHECK"]

def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, "r") as f:
                cache.deserialize(f.read())
        except Exception as e:
            print(f"Warning: Failed to load token cache: {e}")
    return cache

def save_cache(cache):
    if cache.has_state_changed:
        try:
            with open(TOKEN_CACHE_FILE, "w") as f:
                f.write(cache.serialize())
        except Exception as e:
            print(f"Warning: Failed to save token cache: {e}")

def get_access_token(config):
    client_id = config.get("client_id")
    tenant_id = config.get("tenant_id", "common")
    client_secret = config.get("client_secret")
    auth_flow = config.get("auth_flow", "interactive").lower()
    
    if not client_id or "ENTER_YOUR_CLIENT_ID" in client_id:
        raise ValueError(
            "Error: Please configure a valid 'client_id' in 'graph_config.json'.\n"
            "Follow the guide in 'azure_registration_guide.md' to create one."
        )

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    
    # 1. Option B: Client Credentials flow (Application permissions)
    if auth_flow == "client_credentials":
        if not client_secret or "ENTER_YOUR_CLIENT_SECRET" in client_secret:
            raise ValueError(
                "Error: 'client_secret' is required for client_credentials flow.\n"
                "Please configure a valid 'client_secret' in 'graph_config.json'."
            )
        print("Using Client Credentials authentication (Option B)...")
        app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority
        )
        # Use .default scope for client credentials flow
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if result and "access_token" in result:
            print("Client Credentials authentication successful.")
            return result["access_token"]
        else:
            error_msg = result.get("error_description") if result else "Unknown authentication error"
            raise RuntimeError(f"Client Credentials authentication failed: {error_msg}")

    # 2. Option A: Public Client flows (Delegated permissions - interactive / device_code)
    cache = load_cache()
    
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=authority,
        token_cache=cache
    )
    
    # Try silent token acquisition from cache first
    accounts = app.get_accounts()
    if accounts:
        print(f"Found cached account: {accounts[0]['username']}. Attempting silent login...")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            save_cache(cache)
            return result["access_token"]
            
    # If cache lookup fails, log in interactively or via device code
    print("No valid cached token found. Starting authentication flow...")
    result = None
    if auth_flow == "device_code":
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "message" in flow:
            print("\n" + "=" * 60)
            print(flow["message"])
            print("=" * 60 + "\n")
        else:
            print("Failed to initiate device code flow.")
        result = app.acquire_token_by_device_flow(flow)
    else:  # Default to interactive
        try:
            result = app.acquire_token_interactive(scopes=SCOPES)
        except Exception as e:
            print(f"Interactive login failed: {e}. Falling back to device code flow...")
            flow = app.initiate_device_flow(scopes=SCOPES)
            if "message" in flow:
                print("\n" + "=" * 60)
                print(flow["message"])
                print("=" * 60 + "\n")
            result = app.acquire_token_by_device_flow(flow)
            
    if result and "access_token" in result:
        save_cache(cache)
        print("Login successful.")
        return result["access_token"]
    else:
        error_msg = result.get("error_description") if result else "Unknown authentication error"
        raise RuntimeError(f"Authentication failed: {error_msg}")

def get_current_user_upn(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("userPrincipalName", "").lower()
    return None

def fetch_calendar_events(access_token, email, current_user_upn, start_date, end_date, timezone):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": f'outlook.timezone="{timezone}"'
    }
    
    # Use /me endpoint for the logged-in user, and /users/{email} for others
    if email.lower() == current_user_upn:
        endpoint = "https://graph.microsoft.com/v1.0/me/calendarView"
    else:
        encoded_email = urllib.parse.quote(email)
        endpoint = f"https://graph.microsoft.com/v1.0/users/{encoded_email}/calendarView"
        
    params = {
        "startDateTime": start_date,
        "endDateTime": end_date,
        "$select": "subject,start,end,isAllDay,organizer,attendees,body",
        "$top": 1000
    }
    
    print(f"Fetching calendar for: {email}...")
    events = []
    url = endpoint
    
    while url:
        # For the first call, pass parameters. For subsequent pages, query parameter is in nextLink URL
        response = requests.get(url, headers=headers, params=params if url == endpoint else None)
        if response.status_code == 403 or response.status_code == 404:
            print(f"  -> Access denied or calendar not found for {email} (skipped).")
            break
        elif response.status_code != 200:
            print(f"  -> Error {response.status_code} fetching {email}: {response.text}")
            break
            
        data = response.json()
        page_events = data.get("value", [])
        events.extend(page_events)
        url = data.get("@odata.nextLink")  # Pagination URL
        
    print(f"  -> Retrieved {len(events)} events.")
    return events

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "graph_config.json")
    
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    try:
        access_token = get_access_token(config)
    except Exception as e:
        print(e)
        return
        
    current_user_upn = get_current_user_upn(access_token)
    if current_user_upn:
        print(f"Logged in as: {current_user_upn}")
        
    start_date = config.get("start_date", "2025-04-01T00:00:00Z")
    end_date = config.get("end_date", "2025-10-01T00:00:00Z")
    timezone = config.get("timezone", "Tokyo Standard Time")
    target_emails = config.get("target_emails", [])
    config_keywords = config.get("keywords", KEYWORDS)
    keywords_upper = [kw.upper() for kw in config_keywords]
    name_suffix = config.get("name_suffix", "/ONHM").upper()
    
    # We define the window filter parameters
    window_start = datetime.fromisoformat(start_date.replace("Z", "+00:00")).replace(tzinfo=None)
    window_end = datetime.fromisoformat(end_date.replace("Z", "+00:00")).replace(tzinfo=None)
    
    all_events = []
    for email in target_emails:
        try:
            events = fetch_calendar_events(access_token, email, current_user_upn, start_date, end_date, timezone)
            all_events.extend(events)
        except Exception as e:
            print(f"  -> Unexpected error fetching {email}: {e}")
            
    # Process and filter events
    seen_events_people = set()
    stats = {}
    event_details = []
    people = set()
    
    for event in all_events:
        subject = (event.get("subject") or "").strip()
        is_all_day = event.get("isAllDay", False)
        
        start_obj = event.get("start")
        start_raw = start_obj.get("dateTime") if start_obj is not None else None
        
        end_obj = event.get("end")
        end_raw = end_obj.get("dateTime") if end_obj is not None else None
        
        body_obj = event.get("body")
        body = body_obj.get("content", "") or "" if body_obj is not None else ""
        
        if is_all_day or not start_raw or not end_raw:
            continue
            
        # Parse ISO datetime strings (ignoring ms/tz details if any, since we prefer JST)
        try:
            start_dt = datetime.fromisoformat(start_raw[:19])
            end_dt = datetime.fromisoformat(end_raw[:19])
        except Exception:
            continue
            
        if end_dt <= start_dt:
            continue
            
        # Only single-day events
        if start_dt.date() != end_dt.date():
            continue
            
        # Time window check
        if end_dt < window_start or start_dt > window_end:
            continue
            
        # Cancelled check (subject + body)
        full_text = subject + " " + body
        if "キャンセル" in full_text or "CANCELL" in full_text.upper():
            continue
            
        # Keyword filter (CDP-related)
        full_text_upper = full_text.upper()
        if not any(kw in full_text_upper for kw in keywords_upper):
            continue
            
        # Names extraction (Organizer + Attendees)
        names = []
        organizer_obj = event.get("organizer")
        org_email_addr = organizer_obj.get("emailAddress") if organizer_obj is not None else None
        org_name = org_email_addr.get("name", "") if org_email_addr is not None else ""
        if org_name:
            names.append(org_name)
            
        attendees = event.get("attendees")
        if attendees is None:
            attendees = []
        for attendee in attendees:
            att_email_addr = attendee.get("emailAddress") if attendee is not None else None
            att_name = att_email_addr.get("name", "") if att_email_addr is not None else ""
            if att_name:
                names.append(att_name)
                
        # Deduplicate names and add to all people set
        for n in names:
            people.add(n)
            
        participants = set()
        for n in names:
            n_str = str(n).strip()
            if n_str.upper().endswith(name_suffix):
                participants.add(n_str)
                
        if not participants:
            continue
            
        duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
        if duration_hours <= 0:
            continue
            
        month_key = f"{start_dt.year}/{start_dt.month}"
        day_str = start_dt.date().isoformat()
        start_time_str = start_dt.time().replace(second=0, microsecond=0).isoformat()
        end_time_str = end_dt.time().replace(second=0, microsecond=0).isoformat()
        subject_norm = subject.strip().upper()
        
        for person in participants:
            key = (day_str, start_time_str, end_time_str, subject_norm, person)
            if key in seen_events_people:
                continue
            seen_events_people.add(key)
            stats_key = (person, month_key)
            stats[stats_key] = stats.get(stats_key, 0.0) + duration_hours
            event_details.append({
                "Person": person,
                "Date": day_str,
                "Start": start_time_str,
                "End": end_time_str,
                "Month": month_key,
                "Subject": subject,
                "DurationHours": f"{duration_hours:.2f}"
            })
            
    # Output results
    if not stats and not people:
        print("No data collected matching the filters.")
        return
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, "output", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1) Save People list
    people_path = os.path.join(output_dir, "calendar_people_graph.txt")
    with open(people_path, "w", encoding="utf-8") as f:
        for p in sorted(people):
            f.write(str(p) + "\n")
    print(f"Total unique people: {len(people)}. List saved to: {people_path}")
    
    # 2) Save monthly summary CSV
    summary_path = os.path.join(output_dir, "cdp_time_by_person_month_graph.csv")
    with open(summary_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Month", "TotalHours"])
        for (person, month) in sorted(stats.keys(), key=lambda k: (k[0].lower(), k[1])):
            total_hours = stats[(person, month)]
            writer.writerow([person, month, f"{total_hours:.2f}"])
    print(f"Summary CSV written to: {summary_path}")
    
    # 3) Save detailed events CSV
    detail_path = os.path.join(output_dir, "cdp_events_detail_graph.csv")
    with open(detail_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Person", "Date", "Start", "End", "Month", "Subject", "DurationHours"])
        writer.writeheader()
        for row in event_details:
            writer.writerow(row)
    print(f"Event details written to: {detail_path}")
    
    # 4) Export per-person Markdown report
    try:
        from export_all_person_md import main as export_person_md
        person_md_dir = os.path.join(output_dir, "person_md")
        export_person_md(detail_path, person_md_dir)
        print(f"Individual Markdown reports generated under: {person_md_dir}")
    except Exception as e:
        print(f"Failed to generate Markdown reports: {e}")
        
    # Excel output removed by user request

if __name__ == "__main__":
    main()
