# Distributed Search Engine (Googol)
Googol is a distributed search engine where components communicate through RPC calls. It works through a simple web frontend or CLI that lets the user index new URLs and perform searches.

## How it's built
There are five main components in the system's backend:

![Arquitecture](./arquitetura.png)
### URL Queue
The URL Queue is a data structure that tracks URLs waiting to be indexed. It's implemented inside the Gateway, so both Clients and Downloaders can add URLs through the same RPC endpoint. Clients use it when submitting a URL manually, and Downloaders when they discover new links while crawling the web pages.


### Gateway
The Gateway exposes the URL Queue via two RPC methods: `putNew()`, used by both Clients and Downloaders to add a URL to be indexed, and `takeNext()`, used by the Downloaders to pull the next URL to crawl. It also serves as the entry point for the clients, `search()` returns ranked results for a set of search terms, and `getIncomingLinks()` returns pages linking to a given URL.

### Client
The Client is the program a user interacts with directly and it invokes RPC calls on the Gateway. Users can index new URLs, perform searches, look through the results with pagination and look up which pages link to a given result.

### Downloaders
Downloaders handle web crawling. Each Downloader takes a new URL from the Queue using `takeNext()`, downloads, parses and tokenizes its text, keeping only words with 3 or more characters. Each word is sent to every Storage Barrel via `addToIndex()` adding it to the inverted index alongside the URL. Title and text snippet are then sent separately via `addPageMeta()`. New URLs found are sent back to the Gateway to be queued for crawling, up to a maximum depth. Each link is also sent to the Storage Barrels with `addLinkTracking()` which saves it to a link dictionary that keeps track of incoming links between pages.

### Storage Barrels
Barrels act as the system's storage and handle search requests from the Gateway. They receive data from the Downloaders and index it into their data structures. Each Barrel saves its data to disk using `pickle`, avoiding data loss if it goes down. When a restart occurs, each Barrel tries to reload its own files.
Barrels expose three RPC methods used by the Downloaders and two for the Gateway, as mentioned in each of these components descriptions.
When the Gateway calls `search()`, the Barrel returns results ranked by number of incoming links, and metadata (title and text preview) for each result. Search results are paginated server-side, the caller specifies a page and page size, and the Barrel returns only that slice along with the total result count.
