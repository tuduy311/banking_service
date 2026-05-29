import uvicorn

if __name__ == "__main__":
    # Run the backend FastAPI app located under backend/app/main.py
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
