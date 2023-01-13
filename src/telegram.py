import requests
import os
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]


def send_notification(content, url, image_url):
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "caption": content,
            "photo": image_url,
            "chat_id": CHANNEL_ID,
            "parse_mode": "MarkdownV2",
            "reply_markup": json.dumps(
                {"inline_keyboard": [[{"text": "Book Now", "url": url}]]}
            ),
        },
    )
    print(resp.status_code, resp.text)


# send_notification("hii", "https://google.com")
