from concurrent import futures
import grpc
import index_pb2
import index_pb2_grpc
from google.protobuf import empty_pb2
import threading
import pickle
import os

class Barrel(index_pb2_grpc.IndexServicer):
    def __init__(self, name):
        self.name = name
        self.filename = f"{name}_index.pkl"
        self.link_file = f"{name}_links.pkl"
        self.meta_file = f"{name}_meta.pkl"
        self.index = {}
        self.incoming_links = {}
        self.page_meta = {}
        self.lock = threading.Lock()
        self._load_files()
        
    def _load_files(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    self.index = pickle.load(f)
                print(f"[{self.name}] Loaded file {self.filename}")
            except Exception as e:
                print(f"[{self.name}] Could not load index file: {e}")
                self.index = {}
        else:
            print(f"[{self.name}] No existing index file")
        
        if os.path.exists(self.link_file):
            try:
                with open(self.link_file, 'rb') as f:
                    self.incoming_links = pickle.load(f)
                print(f"[{self.name}] Loaded file {self.link_file}")
            except Exception as e:
                print(f"[{self.name}] Could not load links file: {e}")
                self.incoming_links = {}
        else:
            print(f"[{self.name}] No existing links file")
            
        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, 'rb') as f:
                    self.page_meta = pickle.load(f)
                print(f"[{self.name}] Loaded metadata from {self.meta_file}")
            except Exception as e:
                print(f"[{self.name}] Could not load metadata: {e}")
                self.page_meta = {}
        else:
            print(f"[{self.name}] No existing metadata file")
            
    def _save_data(self):
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.index, f)
        except Exception as e:
            print(f"[{self.name}] Failed to save index: {e}")
            
        try:
            with open(self.link_file, 'wb') as f:
                pickle.dump(self.incoming_links, f)
        except Exception as e:
            print(f"[{self.name}] Failed to save links: {e}")
            
        try:
            with open(self.meta_file, 'wb') as f:
                pickle.dump(self.page_meta, f)
        except Exception as e:
            print(f"[{self.name}] Failed to save metadata: {e}")
        
    # RPC: Downloader calls to add token and url to index
    def addToIndex(self, request, context):
        word, url = request.word, request.url
        with self.lock:
            if word not in self.index:
                self.index[word] = set()
            self.index[word].add(url)
            self._save_data()
            print(f"[{self.name}] Added ({word} -> {url})")
        return empty_pb2.Empty()
    
    # RPC: Donwloader calls to add pages that link to an url
    def addLinkTracking(self, request, context):
        with self.lock:
            prev_url = request.prev_url
            curr_url = request.curr_url
            
            if curr_url not in self.incoming_links:
                self.incoming_links[curr_url] = set()
            
            self.incoming_links[curr_url].add(prev_url)
    
        return empty_pb2.Empty()
    
    # RPC: Donwloader calls to add metadata (text and snippet)
    def addPageMeta(self, request, context):
        url = request.url
        title = request.title
        snippet = request.snippet

        with self.lock:
            self.page_meta[url] = {"title": title, "snippet": snippet}
            self._save_data()
            print(f"[{self.name}] Stored metadata for {url}")
        return empty_pb2.Empty()
    
    # RPC: Gateway calls this, returns pages that link to a specific URL
    def getIncomingLinks(self, request, context):
        url = request.url
        with self.lock:
            incoming = self.incoming_links.get(url, set())
            links = list(incoming)
        return index_pb2.GetIncomingLinksResponse(links=links)
    
    # RPC: Gateway calls this, returns search results order by relevance
    def search(self, request, context):
        terms = request.terms
        page = request.page if request.page > 0 else 1
        page_size = request.page_size if request.page_size > 0 else 10
        
        print(f"[{self.name}] Search request: terms={terms}, page={page}, page_size={page_size}")
        
        with self.lock:
            # Find URLs
            result_urls = None
            
            for term in terms:
                if term in self.index:
                    urls_with_term = self.index[term]
                    print(f"[{self.name}] Found {len(urls_with_term)} URLs for term '{term}'")
                    if result_urls is None:
                        result_urls = urls_with_term.copy()
                    else:
                        result_urls = result_urls.intersection(urls_with_term)
                else:
                    print(f"[{self.name}] Term '{term}' not found in index")
                    return index_pb2.SearchResponse(results=[], total_results=0)
            
            if result_urls is None:
                print(f"[{self.name}] No result URLs found")
                return index_pb2.SearchResponse(results=[], total_results=0)
            
            print(f"[{self.name}] Total matching URLs: {len(result_urls)}")
            
            # Sort by links
            url_scores = []
            for url in result_urls:
                num_incoming = len(self.incoming_links.get(url, set()))
                url_scores.append((url, num_incoming))
                
            url_scores.sort(key=lambda x: x[1], reverse=True)
            sorted_urls = [url for url, score in url_scores]
            
            results = []
            for url in sorted_urls:
                meta = self.page_meta.get(url, {"title": "(no title)", "snippet": ""})
                result = index_pb2.SearchResult(
                    url=url,
                    title=meta["title"],
                    snippet=meta["snippet"]
                )
                results.append(result)
            
            total_results = len(results)
            
            # Slice for pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_results = results[start_idx:end_idx]
            
            print(f"[{self.name}] Returning {len(paginated_results)} results (total: {total_results})")
        
        return index_pb2.SearchResponse(
            results=paginated_results,
            total_results=total_results
        )

def serve(name, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    barrel = Barrel(name)
    index_pb2_grpc.add_IndexServicer_to_server(barrel, server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    print(f"[{name}] Listening on port {port}")
    server.wait_for_termination()
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python storage_barrel.py <name> <port>")
        sys.exit(1)
    serve(sys.argv[1], int(sys.argv[2]))