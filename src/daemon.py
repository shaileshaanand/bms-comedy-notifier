from scraper import get_shows, get_bms_id
from telegram import send_notification
from helpers import sanitize
import time
import cloudscraper


def notify(show):
    NEW_SHOW_MESSAGE_TEMPLATE = """New Show Found
*{title}*

At _{location}_

Price: *{price}*
"""
    send_notification(
        NEW_SHOW_MESSAGE_TEMPLATE.format(
            title=sanitize(show["text"][0]["components"][0]["text"]),
            location=sanitize(show["text"][1]["components"][0]["text"]),
            price=sanitize(show["text"][3]["components"][0]["text"].strip()),
        ),
        show["ctaUrl"],
        show["image"]["url"],
    )


scraper = cloudscraper.create_scraper()
bmsId = get_bms_id(scraper)

current_show_ids = {show["id"] for show in get_shows(scraper, bmsId)}


while True:
    shows = get_shows(scraper, bmsId)
    shows_dict = {show["id"]: show for show in shows}
    show_ids = {show["id"] for show in shows}
    new_show_ids = show_ids - current_show_ids
    current_show_ids = show_ids
    if new_show_ids:
        print("new shows found")
        for show_id in new_show_ids:
            print(shows_dict[show_id]["text"][0]["components"][0]["text"])
        notify(shows_dict[show_id])

    if not new_show_ids:
        print("No changes")
    time.sleep(300)
