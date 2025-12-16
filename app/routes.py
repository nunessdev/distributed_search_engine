from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.rpc_client import put_new_url, search_terms, get_incoming_links

import requests

# Used local tinyllama model
def generate_ai_summary(search_terms):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": f"Provide a brief summary about: {', '.join(search_terms)}",
            "stream": False
        },
    )
    return response.json()['response']

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Homepage
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Index a new URL page
@router.get("/index", response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse("add_url.html", {"request": request})

# Search Page
@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

# Get URLs that link to a specific page
@router.post("/links", response_class=HTMLResponse)
def links_page(request: Request, url: str = Form(...)):
    response = get_incoming_links(url)
    links = response.links
    
    return templates.TemplateResponse("links.html", {
        "request": request,
        "target_url": url,
        "links": links,
        "total_links": len(links)
    })

# Index a URL
@router.post("/index")
async def api_index_url(request: Request, url: str = Form(...)):
    put_new_url(url)
    return templates.TemplateResponse("add_url.html", {
        "request": request, 
        "message": "URL added to queue!"
    })

# Search
@router.post("/search")
async def search_results(request: Request, query: str = Form(...), page: int = Form(1)):
    # Split query
    terms = query.lower().split()
    
    # Call RPC
    response = search_terms(terms, page=page, page_size=10)
    
    total_results = response.total_results
    total_pages = (total_results + 9) // 10 

    ai_summary = generate_ai_summary(terms) if page == 1 else ""
    
    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "query": query,
        "results": response.results,
        "current_page": page,
        "total_pages": total_pages,
        "total_results": total_results,
        "ai_summary": ai_summary
    })