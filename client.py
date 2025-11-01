import grpc
import index_pb2
import index_pb2_grpc

def main():
    gateway_ip = "localhost:8183"
    channel = grpc.insecure_channel(gateway_ip)
    stub = index_pb2_grpc.IndexStub(channel)
    
    print("Welcome to Googol!")
    
    while True:
        print("\n1. Add URL")
        print("2. Search")
        print("3. Exit")
        choice = input("Choose: ")
        
        if choice == "1":
            url = input("Enter URL: ")# TODO: Implement search
            p = 1
            stub.putNew(index_pb2.PutNewRequest(url=url, depth=0))
            print("URL added to queue!")
            
        elif choice == "2":
            query = input("Enter search terms (space separated): ")
            terms = query.lower().split()
            response = stub.search(index_pb2.SearchRequest(terms=terms))
            print(f"\nFound {len(response.urls)} results:")
            for url in response.urls:
                print(f"  - {url}")
            
        elif choice == "3":
            break
        
        else:
            print("\nInvalid input, try again:")
            
if __name__ == "__main__":
    main()