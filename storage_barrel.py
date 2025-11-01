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
        self.index = {}
        self.lock = threading.Lock()
        self._load_index()
        
    def _load_index(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    self.index = pickle.load(f)
                print(f"[{self.name}] Loaded file {self.filename}")
            except Exception as e:
                print(f"[{self.name}] Could not load file: {e}")
                self.index = {}
        else:
            print(f"[{self.name}] No existing file")
            
    def _save_index(self):
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.index, f)
        except Exception as e:
            print(f"[{self.name}] Failed to save: {e}")
        
    def addToIndex(self, request, context):
        word, url = request.word, request.url
        with self.lock:
            if word not in self.index:
                self.index[word] = set()
            self.index[word].add(url)
            self._save_index()
            print(f"[{self.name}] Added ({word} -> {url})")
        return empty_pb2.Empty()
    
    def search(self, request, context):
        terms = request.terms  # list of words to search for
        
        with self.lock:
            # Find URLs that have ALL the terms
            result_urls = None
            
            for term in terms:
                if term in self.index:
                    urls_with_term = self.index[term]
                    if result_urls is None:
                        result_urls = urls_with_term.copy()
                    else:
                        # Intersection: only URLs that have ALL terms
                        result_urls = result_urls.intersection(urls_with_term)
                else:
                    # Term not found, no results
                    return index_pb2.SearchResponse(urls=[])
            
            if result_urls is None:
                return index_pb2.SearchResponse(urls=[])
        
        return index_pb2.SearchResponse(urls=list(result_urls))

def serve(name, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    barrel = Barrel(name)
    index_pb2_grpc.add_IndexServicer_to_server(barrel, server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[{name}] Listening on port {port}")
    server.wait_for_termination()
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python storage_barrel.py <name> <port>")
        sys.exit(1)
    serve(sys.argv[1], int(sys.argv[2]))