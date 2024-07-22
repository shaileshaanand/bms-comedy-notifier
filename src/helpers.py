from telegram import send_notification


def sanitize(st: str):
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for special_char in special_chars:
        st = st.replace(special_char, f"\{special_char}")
    return st


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
