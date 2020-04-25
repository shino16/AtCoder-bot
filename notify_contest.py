from datetime import datetime, timedelta, timezone
import pickle
import os
import iso8601
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from discord_webhook import DiscordWebhook


scope = "https://www.googleapis.com/auth/calendar.readonly"

credential = {"installed": {
    "client_id": os.environ["CALENDAR_ID"],
    "project_id": os.environ["CALENDAR_PROJECT_ID"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": os.environ["CALENDAR_CLIENT_SECRET"],
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
}}

calendar_id = os.environ["CALENDAR_ID"]

JST = timezone(timedelta(hours=+9), 'JST')

webhook_url = os.environ["CALENDAR_WEBHOOK_URL"]


def get_api_events_proxy():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(credential, scope)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service.events()


def get_events():
    proxy = get_api_events_proxy()
    now = datetime.utcnow().isoformat() + "Z"  # RFC 3339 timestamp
    until = (now + timedelta(hours=24)).isoformat() + "Z"
    events_result = proxy.list(calendarId=calendar_id, timeMin=now, timeMax=until,
                               singleEvents=True, orderBy="startTime").execute()
    return events_result.get("items", [])


def notify(time, title, msg):
    encoded_time = time.astimezone(JST).strftime("%Y-%m-%d %H:%M%z")[:-2]
    content = f"【{msg}】{encoded_time} {title}"
    DiscordWebhook(url=webhook_url, content=content).execute()


def main():
    now = datetime.now(JST)
    for event in get_events():
        start_time = iso8601.parse_date(event["start"]["datetime"])
        minutes = (start_time - now).total_seconds() // 60
        if minutes >= 7 and minutes < 17:
            notify(start_time, event["summary"], f"あと{minutes}分")
        if minutes >= 52 and minutes < 62:
            notify(start_time, event["summary"], "あと1時間")
        if minutes >= 1440 and minutes < 1450:
            notify(start_time, event["summary"], "明日")


if __name__ == "__main__":
    main()
