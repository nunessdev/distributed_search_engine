from bs4 import BeautifulSoup
import requests

# Test URL
start_urls = ["https://www.python.org/"]
MAX_DEPTH = 2


# Download HTML with BeautifulSoup and return None if fails
def download_html(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[Error] Failed to fetch {url}: {e}")
        return None


# Extrat title, text and links from HTML
def extract_content(soup):
    text = soup.get_text(" ", strip=True)
    links = soup.find_all("a", href=True)
    links = [link for link in links if link["href"].startswith("http")]
    return text, links


# Turn text into a list of only words, lowercased, no punctuation
def parse_text(text):
    text = text.lower()
    text = text.replace(".", "")
    text = text.replace(",", "")
    text = text.replace("!", "")
    text = text.replace("?", "")
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = text.split()

    return text


# Main function
def main():
    soup = download_html(start_urls[0])
    text, links = extract_content(soup)
    print(text)
    for link in links:
        print(link["href"])

    print(parse_text(text))
    visited = set()

    # while url_queue:


if __name__ == "__main__":
    main()
