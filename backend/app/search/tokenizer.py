import re


def tokenize(text: str) -> list[str]:
    """
    Convert text into lowercase word tokens.

    Example:
    Input:
        "Python is Amazing!!"

    Output:
        ["python", "is", "amazing"]
    """

    if not text:
        return []

    text = text.lower()

    return re.findall(r"[a-z0-9]+", text)