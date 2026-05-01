from fastapi import FastAPI

from app.db import get_connection

app = FastAPI(title="AdTech Recommendations API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM recommendations;")
            result = cur.fetchone()
        return result
    finally:
        conn.close()