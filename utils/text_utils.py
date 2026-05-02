def spongebob_case(text: str) -> str:
    """Alternate upper/lower case on each character (mocking text)."""
    result = []
    upper = False
    for char in text:
        result.append(char.upper() if upper else char.lower())
        upper = not upper
    return "".join(result)


def convert_binary(text: str) -> str:
    """Convert each character in text to its 8-bit binary representation."""
    return " ".join(format(ord(char), "08b") for char in text)
