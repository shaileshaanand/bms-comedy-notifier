import requests

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
}


def get_shows():

    headers = {
        **base_headers,
        "x-app-code": "WEB",
        "x-platform-code": "DESKTOP-WEB",
    }
    resp = requests.get("https://in.bookmyshow.com/", headers=headers)
    bmsCookie = list(
        filter(
            lambda cookie: cookie.name == "bmsId",
            resp.cookies,
        )
    )

    # headers["x-bms-id"] = "1.169359087.1670230427247"
    headers["x-bms-id"] = bmsCookie[0].value

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

        response = requests.get(
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
    # for card in cards:
    #     print(card["text"][0]['components'][0]['text'])
    return cards
