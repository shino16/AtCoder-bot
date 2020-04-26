from datetime import datetime, timedelta, timezone
import pickle
import os
import json
import iso8601
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from discord_webhook import DiscordWebhook


credentials = json.loads(os.environ["CALENDAR_CREDENTIALS"])

calendar_id = os.environ["CALENDAR_ID"]

JST = timezone(timedelta(hours=+9), 'JST')

webhook_url = os.environ["CALENDAR_WEBHOOK_URL"]


def get_events():
    creds = Credentials.from_service_account_info(credentials)
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + "Z"  # RFC 3339 timestamp
    until = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, timeMax=until, singleEvents=True
        ).execute()
    return events_result.get("items", [])


def notify(time, title, msg):
    encoded_time = time.astimezone(JST).strftime("%Y-%m-%d %H:%M%z")[:-2]
    content = f"【{msg}】{encoded_time} {title}"
    DiscordWebhook(url=webhook_url, content=content).execute()


def main():
    now = datetime.now(JST)
    for event in get_events():
        start_time = iso8601.parse_date(event["start"]["dateTime"])
        minutes = (start_time - now).total_seconds() / 60
        if minutes >= 7 and minutes < 17:
            notify(start_time, event["summary"], f"あと{round(minutes)}分")
        if minutes >= 52 and minutes < 62:
            notify(start_time, event["summary"], "あと1時間")
        if minutes >= 1440 and minutes < 1450:
            notify(start_time, event["summary"], "明日")


if __name__ == "__main__":
    main()
