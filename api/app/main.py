from fastapi import FastAPI

app = FastAPI(title="AdTech Recommendations API")


@app.get("/health")
def health():
    return {"status": "ok"}