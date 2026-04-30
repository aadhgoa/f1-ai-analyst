"""Main entry point for the F1 AI Analyst API."""

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="F1 AI Analyst", version="1.0.0")

app.include_router(router)


@app.get("/")
def root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the F1 AI Analyst API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", port=8000, reload=True)
