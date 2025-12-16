import grpc
import index_pb2
import index_pb2_grpc

def main():
    gateway_ip = "0.0.0.0:8183"
    channel = grpc.insecure_channel(gateway_ip)
    stub = index_pb2_grpc.IndexStub(channel)
    
    print("Welcome to Googol!")
    
    while True:
        # Main menu
        print("\n1. Add URL")
        print("2. Search")
        print("3. Exit")
        choice = input("Choose: ")
        
        # Add new URL
        if choice == "1":
            url = input("Enter URL: ")
            p = 1
            stub.putNew(index_pb2.PutNewRequest(url=url, depth=0))
            print("URL added to queue!")
            
        elif choice == "2":
            query = input("Enter search terms (space separated): ")
            terms = query.lower().split()

            current_page = 1
            results_per_page = 10

            while True:
                response = stub.search(index_pb2.SearchRequest(
                    terms=terms, 
                    page=current_page, 
                    page_size=results_per_page
                ))
                total_results = response.total_results
                total_pages = (total_results + results_per_page - 1) // results_per_page
            
                if total_results == 0:
                    print("\nNo results found.")
                    break
                
                print(f"\nPage {current_page} of {total_pages} (Total: {total_results} results)")

                # Display current page results
                start_num = (current_page - 1) * results_per_page
                for idx, result in enumerate(response.results, start_num + 1):
                    print(f"\n[{idx}] Title: {result.title}")
                    print(f"URL: {result.url}")
                    print(f"Preview: {result.snippet}...")
                    print("  " + "-" * 60)

                # Navigation menu
                print("\nOptions:")
                print("- Enter a result number to check URLs linking to it")
                if current_page < total_pages:
                    print("- Type 'next' for next page")
                if current_page > 1:
                    print("- Type 'prev' for previous page")
                print("- Type 'exit' to return to main menu")

                user_input = input("\nYour choice: ").lower()

                if user_input == 'exit':
                    break
                elif user_input == 'next' and current_page < total_pages:
                    current_page += 1
                elif user_input == 'prev' and current_page > 1:
                    current_page -= 1
                # Get pages that link to the selected URL
                else:
                    try:
                        result_num = int(user_input)
                        # Calculate which page this result is on
                        result_page = (result_num - 1) // results_per_page + 1
                        result_index_in_page = (result_num - 1) % results_per_page
                        
                        # Check if it's a valid number overall
                        if 1 <= result_num <= total_results:
                            # If it's on current page, we already have it
                            if result_page == current_page:
                                selected_result = response.results[result_index_in_page]
                            else:
                                # Need to fetch that page
                                temp_response = stub.search(index_pb2.SearchRequest(
                                    terms=terms,
                                    page=result_page,
                                    page_size=results_per_page
                                ))
                                selected_result = temp_response.results[result_index_in_page]
                            
                            print(f"\nChecking pages linking to: {selected_result.url}")
                            links_response = stub.getIncomingLinks(
                                index_pb2.GetIncomingLinksRequest(url=selected_result.url)
                            )
                            
                            if len(links_response.links) == 0:
                                print("No pages linking to this URL were found.")
                            else:
                                print(f"Found {len(links_response.links)} pages linking to this URL:")
                                for link in links_response.links:
                                    print(f"- {link}")
                        else:
                            print(f"Invalid number. Please enter between 1 and {total_results}.")
                    except ValueError:
                        print("Invalid input. Please enter a valid option.")

        elif choice == "3":
            break
        else:
            print("\nInvalid input, try again:")
            
if __name__ == "__main__":
    main()