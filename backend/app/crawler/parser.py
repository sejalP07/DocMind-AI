from bs4 import BeautifulSoup


class HTMLParser:

    @staticmethod
    def parse(html: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else "Untitled"
        )

        text = soup.get_text(" ", strip=True)

        return {
            "title": title,
            "content": text,
        }