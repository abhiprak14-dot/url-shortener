from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import URL
from app.schemas import URLCreate, URLResponse
from app.utils.generator import generate_short_code

router = APIRouter()
BASE_URL = "https://parvatai.com"

@router.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    for _ in range(5):
        code = generate_short_code()
        if not db.query(URL).filter(URL.short_code == code).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique code")
    url_entry = URL(original_url=str(payload.original_url), short_code=code)
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)
    return URLResponse(original_url=url_entry.original_url, short_code=url_entry.short_code,
                       short_url=f"{BASE_URL}/{url_entry.short_code}", clicks=url_entry.clicks,
                       created_at=url_entry.created_at)

@router.get("/stats/{short_code}", response_model=URLResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return URLResponse(original_url=url_entry.original_url, short_code=url_entry.short_code,
                       short_url=f"{BASE_URL}/{url_entry.short_code}", clicks=url_entry.clicks,
                       created_at=url_entry.created_at)

@router.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    url_entry.clicks += 1
    db.commit()
    return RedirectResponse(url=url_entry.original_url)
