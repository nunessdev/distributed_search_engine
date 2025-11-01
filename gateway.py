from concurrent import futures
from collections import deque
import grpc
import index_pb2
import index_pb2_grpc
from google.protobuf import empty_pb2
import threading


class Gateway(index_pb2_grpc.IndexServicer):
    # Initialize queues and variables
    def __init__(self):
        self.queue = deque()
        self.visited = set()
        self.lock = threading.Lock()

        self.start_urls = ["https://www.python.org/"]

        for url in self.start_urls:
            self._add_to_queue(url, 0)

        print("[Gateway] Started with start URLs.")

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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    index_pb2_grpc.add_IndexServicer_to_server(Gateway(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("[Gateway] Server started, listening on port 50051.")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
