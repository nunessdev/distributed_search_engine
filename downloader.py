from bs4 import BeautifulSoup
import requests
import grpc
import index_pb2
import index_pb2_grpc
from google.protobuf import empty_pb2
import time
import re

# Depth serves as a stopping point for the web crawler
MAX_DEPTH = 2

# Download HTML with BeautifulSoup and return None if fails
def download_html(url):
    try:
        print(f"[Downloader] Downloading: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[Downloader] Failed to download {url}: {e}")
        return None


# Extrat title, text and links from HTML
def extract_content(soup):
    title = soup.title.string if soup.title else "(no title)"
    text = soup.get_text(" ", strip=True)
    links = soup.find_all("a", href=True)
    links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("http")]
    return title, text, links


# Main function and downloader logic
def main():
    gateway_ip = "localhost:8183"
    barrel1_ip = "localhost:8184"
    barrel2_ip = "localhost:8185"
    
    channel = grpc.insecure_channel(gateway_ip)
    stub = index_pb2_grpc.IndexStub(channel)
    print(f"[Downloader] Connected to Gateway at {gateway_ip}")
    
    barrel1_channel = grpc.insecure_channel(barrel1_ip)
    barrel1_stub = index_pb2_grpc.IndexStub(barrel1_channel)
    
    barrel2_channel = grpc.insecure_channel(barrel2_ip)
    barrel2_stub = index_pb2_grpc.IndexStub(barrel2_channel)
    
    print(f"[Downloader] Connected to 2 Barrels")
    
    try:
        try:
            while True:
                response = stub.takeNext(empty_pb2.Empty())
                url = response.url
                depth = response.depth
                
                if url == "":
                    print("[Downloader] Queue empty, waiting 5s...")
                    time.sleep(5)
                else:
                    print(f"[Downloader] URL recieved: {url}")
                    soup = download_html(url)
                    
                    if soup is None:
                        print(f"[Downloader] Skipping {url} (download failed)")
                    else:
                        title, text, links = extract_content(soup)
                        print(f"[Downloader] Parsed: '{title}' with {len(links)} links")
                        snippet = text[:200]
                        
                        # Tokenize text and send to barrel
                        text = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                        for word in text:
                            try:
                                barrel1_stub.addToIndex(index_pb2.AddToIndexRequest(word=word, url=url))
                            except grpc.RpcError as e:
                                print(f"[Downloader] Barrel1 failed: {e}")
                                
                            try:
                                barrel2_stub.addToIndex(index_pb2.AddToIndexRequest(word=word, url=url))
                            except grpc.RpcError as e:
                                print(f"[Downloader] Barrel2 failed: {e}")
                        
                        # Only add links if there are links and max depth hasn't been reached
                        if len(links) > 0 and depth < MAX_DEPTH:
                            for link in links:
                                stub.putNew(index_pb2.PutNewRequest(url=link, depth = depth + 1))
                                # Also add link tracking
                                barrel1_stub.addLinkTracking(index_pb2.addLinkTrackingRequest(prev_url=url, curr_url=link))
                                barrel2_stub.addLinkTracking(index_pb2.addLinkTrackingRequest(prev_url=url, curr_url=link))
                            print(f"[Downloaders] Added links with depth {depth + 1}")
                            
                        # Also send metadata
                        title = str(title)
                        snippet = str(snippet)
                        url = str(url)
                        
                        barrel1_stub.addPageMeta(index_pb2.AddPageMetaRequest(url=url, title=title, snippet=snippet))
                        barrel2_stub.addPageMeta(index_pb2.AddPageMetaRequest(url=url, title=title, snippet=snippet))
            
        except grpc.RpcError as e:
            print(f"[Downloader] RPC failed: {e.code()}")
            print(f"[Downloader] RPC error details: {e.details()}")
            raise
        
    except KeyboardInterrupt:
        print("\n[Downloader] Shutting down...")
    
    return


if __name__ == "__main__":
    main()