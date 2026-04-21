from fastapi import FastAPI
from app.database import engine, Base
from app.routes import shortener

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener",
    description="A fast and lightweight URL shortening service built with FastAPI",
    version="1.0.0"
)

app.include_router(shortener.router)


@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener API. Visit /docs for API documentation."}
