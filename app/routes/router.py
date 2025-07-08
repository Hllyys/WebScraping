from fastapi import APIRouter
from pydantic import BaseModel
from app.core.browser import scrape_with_browser

router = APIRouter()

class SearchRequest(BaseModel):
    date: str
    start: str
    end: str
    count: int

@router.post("/search/ravensnowshoe")
async def search_ravensnowshoe(payload: SearchRequest):
    return scrape_with_browser(
        date=payload.date,
        start=payload.start,
        end=payload.end,
        count=payload.count,
        subdomain="ravensnowshoe"
    )

@router.post("/search/verrado")
async def search_verrado(payload: SearchRequest):
    return scrape_with_browser(
        date=payload.date,
        start=payload.start,
        end=payload.end,
        count=payload.count,
        subdomain="verrado"
    )
