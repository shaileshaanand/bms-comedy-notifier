from scraper import get_shows
from telegram import send_notification
from helpers import sanitize
import time
import random

current_show_ids = {show["id"] for show in get_shows()}

MESSAGE_TEMPLATE = """New Show Found
*{title}*

At _{location}_

Price: *{price}*
"""

while True:
    shows = get_shows()
    show_ids = {show["id"] for show in shows}
    new_shows = show_ids - current_show_ids
    deleted_shows = current_show_ids - show_ids
    if new_shows:
        print("new shows found")
        for show in new_shows:
            print(show["text"][0]["components"][0]["text"])

    if deleted_shows:
        print("deleted shows found")
        for show in new_shows:
            print(show["text"][0]["components"][0]["text"])
            send_notification(
                f"""New Show Found
            {show["text"][0]["components"][0]["text"]}
            """,
                show["ctaUrl"],
                show["image"]["url"],
            )
    notification_show = random.choice(shows)
    send_notification(
        MESSAGE_TEMPLATE.format(
            title=sanitize(notification_show["text"][0]["components"][0]["text"]),
            location=sanitize(notification_show["text"][1]["components"][0]["text"]),
            price=sanitize(
                notification_show["text"][3]["components"][0]["text"].strip()
            ),
        ),
        notification_show["ctaUrl"],
        notification_show["image"]["url"],
    )
    if not (deleted_shows and new_shows):
        print("No changes")
    time.sleep(600)
