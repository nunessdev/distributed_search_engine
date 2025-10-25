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
        return None


# Extrat title, text and links from HTML
def extract_content(soup):
    text = soup.get_text(" ", strip=True)
    links = soup.find_all("a", href=True)
    links = [link for link in links if link["href"].startswith("http")]
    return text, links


# Main function and downloader logic
def main():
    visited = set()
    for url in start_urls:
        print(f"[Downloader] Visiting {url}")
        soup = download_html(url)
        if soup is None:
            print(f"[Downloader] Failed to download {url}")
            continue
        else:
            print(f"[Downloader] Downloaded {url}")
            text, links = extract_content(soup)
            visited.add(url)
            # TODO: Send links to gateway
            # TODO: Send text to storage barrels

    # TODO: Same as above, but take links from inversed index at the gateway


if __name__ == "__main__":
    main()
