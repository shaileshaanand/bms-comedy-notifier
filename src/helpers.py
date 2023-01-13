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
