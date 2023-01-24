import cloudscraper

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


def get_bms_id(scraper: cloudscraper.CloudScraper):
    resp = scraper.get("https://in.bookmyshow.com/", headers=base_headers)
    return resp.cookies.get_dict()["bmsId"]


def get_shows(scraper: cloudscraper.CloudScraper, bmsId: str):
    headers = {**base_headers, "x-bms-id": bmsId}

    pageId = None
    scrollId = None

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

        response = scraper.get(
            "https://in.bookmyshow.com/api/explore/v1/discover/events-bengaluru",
            params=params,
            headers=headers,
        )
        response = response.json()

        cards.extend(
            [card for listing in response["listings"] for card in listing["cards"]]
        )
        if response.get("pageId"):
            pageId = response["pageId"]
            scrollId = response["scrollId"]
        else:
            break
    return cards
