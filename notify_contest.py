from datetime import datetime, timedelta, timezone
from time import sleep
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

webhook_url = os.environ["NOTIFY_WEBHOOK_URL"]


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


def run(now):
    print("start")
    for event in get_events():
        start_time = iso8601.parse_date(event["start"]["dateTime"])
        minutes = (start_time - now).total_seconds() / 60
        if minutes >= 8 and minutes < 13:
            notify(start_time, event["summary"], f"あと10分")
        if minutes >= 58 and minutes < 63:
            notify(start_time, event["summary"], "あと1時間")
        if minutes >= 1438 and minutes < 1443:
            notify(start_time, event["summary"], "明日")
    print("finish")


def main():
    while True:
        if datetime.now().second == 0:
            break
    while True:
        now = datetime.now()
        if now.minute % 5 == 0 and now.second == 0:
            run(now)
            sleep(3*60)


if __name__ == "__main__":
    main()
