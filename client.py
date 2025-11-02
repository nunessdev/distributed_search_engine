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
            url = input("Enter URL: ")
            p = 1
            stub.putNew(index_pb2.PutNewRequest(url=url, depth=0))
            print("URL added to queue!")
            
        elif choice == "2":
            query = input("Enter search terms (space separated): ")
            terms = query.lower().split()
            response = stub.search(index_pb2.SearchRequest(terms=terms))
            print(f"\nFound {len(response.results)} results:")
            
            if len(response.results) == 0:
                print("\nNo results found.")
                
            else:
                results_per_page = 10
                current_page = 0
                total_pages = (len(response.results) + results_per_page - 1) // results_per_page
                
                while True:
                    
                    # Calculate which results to show
                    start = current_page * results_per_page + 1
                    end = min(start + results_per_page - 1, len(response.results))
                    page_results = response.results[start:end]
                    
                    print(f"Page {current_page + 1} of {total_pages} (Results {start}-{end} of {len(response.results)})")
                    
                    for idx, result in enumerate(page_results, start):
                        print(f"\n[{idx}] Title: {result.title}")
                        print(f"URL: {result.url}")
                        print(f"Preview: {result.snippet}...")
                        print("  " + "-" * 60)
                        
                    while True:
                        # Results manu
                        print("\nOptions:")
                        print("- Enter a result number to check URLs linking to it")
                        if current_page < total_pages - 1:
                            print("- Type 'next' for next page")
                        if current_page > 0:
                            print("- Type 'prev' for previous page")
                        print("- Type 'exit' to return to main menu")
                        
                        user_input = input("\nYour choice: ").lower()
                
                        if user_input == 'exit':
                            break
                        
                        elif user_input == 'next' and current_page < total_pages - 1:
                            current_page += 1
                            break
                            
                        elif user_input == 'prev' and current_page > 0:
                            current_page -= 1
                            break
                            
                        else:
                            try:
                                result_num = int(user_input)
                                if 1 <= result_num <= len(response.results):
                                    selected_result = response.results[result_num - 1]
                                    print(f"\nChecking pages linking to: {selected_result.url}")
                                    
                                    links_response = stub.getIncomingLinks(index_pb2.GetIncomingLinksRequest(url=selected_result.url))
                                    
                                    if len(links_response.links) == 0:
                                        print("No pages linking to this URL were found.")
                                    else:
                                        print(f"Found {len(links_response.links)} pages linking to this URL:")
                                        for link in links_response.links:
                                            print(f"- {link}")
                                else:
                                    print(f"Invalid number. Please enter a number between 1 and {len(response.results)}.")
                            # If convertion to int fails, retry input
                            except ValueError:
                                print("Invalid input. Please enter a valid option.")
                                
                    if user_input == 'exit':
                            break
        elif choice == "3":
            break
        
        else:
            print("\nInvalid input, try again:")
            
if __name__ == "__main__":
    main()