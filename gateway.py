from concurrent import futures
from collections import deque
import grpc
import index_pb2
import index_pb2_grpc
from google.protobuf import empty_pb2
import threading
import random

barrel1_ip = "0.0.0.0:8184"
barrel2_ip = "0.0.0.0:8185"
gateway_ip = "0.0.0.0:8183"

class Gateway(index_pb2_grpc.IndexServicer):
    # Initialize queues and variables
    def __init__(self):
        self.queue = deque()
        self.visited = set()
        self.lock = threading.Lock()

        self.start_urls = []

        for url in self.start_urls:
            self._add_to_queue(url, 0)

        print("[Gateway] Started with start URLs.")
        
        self.barrel_stubs = []
        self.barrel_stubs.append(index_pb2_grpc.IndexStub(grpc.insecure_channel(barrel1_ip)))
        self.barrel_stubs.append(index_pb2_grpc.IndexStub(grpc.insecure_channel(barrel2_ip)))
        
        print("[Gateway] Connected to Barrels.")

    # Add URL to queue
    def _add_to_queue(self, url, depth):
        if url not in self.visited:
            self.queue.append((url, depth))
            print(f"[Gateway] Added {url} to queue.")

    # RPC: Downloaders call this to get new URL
    def takeNext(self, request, context):
        with self.lock:
            if len(self.queue) == 0:
                print("[Gateway] Queue is empty.")
                return index_pb2.TakeNextResponse(url="")
            else:
                url, depth = self.queue.popleft()
                self.visited.add(url)
                print(f"[Gateway] Sending url {url}.")
                return index_pb2.TakeNextResponse(url=url, depth=depth)

    # RPC: Downloaders amd Clients call this to add URLs to queue
    def putNew(self, request, context):
        with self.lock:
            url = request.url
            depth = request.depth
            self._add_to_queue(url, depth)
        return empty_pb2.Empty()

    # RPC: Client calls this to make a search
    def search(self, request, context):
        barrel = random.choice(self.barrel_stubs)
        try:
            return barrel.search(request)
        except grpc.RpcError as e:
            print(f"[Gateway] Barrel failed, trying another...")
            # Try the other barrel 
            for other_barrel in self.barrel_stubs:
                if other_barrel != barrel:
                    try:
                        return other_barrel.search(request)
                    except:
                        pass
            # All barrels failed
            return index_pb2.SearchResponse(results=[])
    
    # RPC: Client calls to get pages that link to a search result (basically the same as above)
    def getIncomingLinks(self, request, context):
        barrel = random.choice(self.barrel_stubs)
        try:
            return barrel.getIncomingLinks(request)
        except grpc.RpcError as e:
            print(f"[Gateway] Barrel failed, trying another...")
            # Try the other barrel
            for other_barrel in self.barrel_stubs:
                if other_barrel != barrel:
                    try:
                        return other_barrel.getIncomingLinks(request)
                    except:
                        pass
            # All barrels failed
            return index_pb2.GetIncomingLinksResponse(links=[])
    
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    index_pb2_grpc.add_IndexServicer_to_server(Gateway(), server)
    server.add_insecure_port("{}".format(gateway_ip))
    server.start()
    print("[Gateway] Server started, listening on port 8183.")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
