# Distributed Search Engine (Googol)
Googol is a distributed search engine where components communicate through RPC calls. It works through a simple web frontend or CLI that lets the user index new URLs and perform searches.

## How it's built
There are five main components in the system:

![Arquitecture](./arquitetura.png)
### URL Queue
The URL Queue is a data structure that tracks URLs waiting to be indexed. It lives inside the Gateway rather than as a separate component, so both Clients and Downloaders can add URLs through the same RPC enpoint. Clients do this when submitting a URL manually while Downloaders do this when they discover new links while crawling a page.


### Gateway
