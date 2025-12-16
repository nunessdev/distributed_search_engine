import grpc
import index_pb2
import index_pb2_grpc

# Connect to gateway at startup
GATEWAY = "localhost:8183"
channel = grpc.insecure_channel(GATEWAY)
stub = index_pb2_grpc.IndexStub(channel)

def put_new_url(url: str, depth: int = 0):
    return stub.putNew(index_pb2.PutNewRequest(url=url, depth=depth))

def search_terms(terms: list[str], page: int = 1, page_size: int = 10):
    return stub.search(index_pb2.SearchRequest(terms=terms, page=page, page_size=page_size))

def get_incoming_links(url: str):
    return stub.getIncomingLinks(index_pb2.GetIncomingLinksRequest(url=url))