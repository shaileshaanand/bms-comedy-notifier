import requests
import os
import logging
import redis
import json

from helpers import sanitize
from telegram import send_notification

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

base_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
    "x-app-code": "WEB",
    "x-platform-code": "DESKTOP-WEB",
}


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


def get_cookies():
    logger.info(
        f"getting cookies using Flaresolverr URL: {os.environ['FLARESOLVERR_URL']}/v1",
    )
    resp = requests.post(
        f"{os.environ['FLARESOLVERR_URL']}/v1",
        headers={"Content-Type": "application/json"},
        json={
            "cmd": "request.get",
            "url": "https://in.bookmyshow.com/",
            "maxTimeout": 60000,
            "returnOnlyCookies": True,
        },
    ).json()

    logger.info(f"Response: {resp}")
    if resp["status"] == "ok":
        return resp["solution"]["cookies"], resp["solution"]["userAgent"]

    logger.error(f"Failed to get cookies: {resp.text}")
    raise Exception("Failed to get cookies")


def get_shows():

    pageId = None
    scrollId = None

    cookies, user_agent = get_cookies()

    cookie_jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        cookie_jar.set(
            cookie["name"],
            cookie["value"],
            domain=cookie["domain"],
            path=cookie["path"],
        )

    headers = {
        **base_headers,
        "User-Agent": user_agent,
        "x-bms-id": list(filter(lambda c: c.name == "bmsId", cookie_jar))[0].value,
    }

    cards = []

    while True:
        params = (
            {
                "region": "BANG",
                "categories": "comedy-shows",
                "scrollId": scrollId,
                "pageId": pageId,
            }
            if pageId
            else {
                "region": "BANG",
                "categories": "comedy-shows",
            }
        )

        response = requests.get(
            "https://in.bookmyshow.com/api/explore/v1/discover/events-bengaluru",
            params=params,
            headers=headers,
        )
        response = response.json()

        logger.info(f"Response for pageId: {pageId} = {response}")

        cards.extend(
            [card for listing in response["listings"] for card in listing["cards"]]
        )
        if response.get("pageId"):
            pageId = response["pageId"]
            scrollId = response["scrollId"]
        else:
            break
    return cards


def update_redis_and_notify():
    redis_client = redis.Redis(
        host=os.environ["VALKEY_HOST"],
        port=os.environ["VALKEY_PORT"],
    )
    existing_show_ids_bytes = redis_client.get("shows")
    if existing_show_ids_bytes is not None:
        existing_show_ids_list = json.loads(existing_show_ids_bytes.decode("utf-8"))
        existing_show_ids = set(existing_show_ids_list)
    else:
        existing_show_ids = set()
    current_shows_list = get_shows()
    current_shows = {show["id"]: show for show in current_shows_list}
    current_show_ids = {show["id"] for show in current_shows_list}
    redis_client.set("shows", json.dumps(list(current_show_ids)))
    new_show_ids = current_show_ids - existing_show_ids
    for show_id in new_show_ids:
        logger.info(f"New show found: {show_id}")
        notify(current_shows[show_id])
    else:
        logger.info("No new shows found")


if __name__ == "__main__":
    update_redis_and_notify()
