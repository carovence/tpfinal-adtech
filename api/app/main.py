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

@app.get("/recommendations/{adv}/{model}")
def recommendations(adv: str, model: str):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT product_id, rank FROM recommendations\n"
                "WHERE advertiser_id = %s AND model = %s AND date = CURRENT_DATE\n"
                "ORDER BY rank ASC",
                (adv, model)
            )
            return cursor.fetchall()
    finally:
        connection.close()      

@app.get("/history/{adv}")
def history(adv: str):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT date, model, product_id, rank FROM recommendations\n"
                "WHERE advertiser_id = %s\n"
                "  AND date >= CURRENT_DATE - INTERVAL '7 days'\n"
                "ORDER BY date DESC, rank ASC",
                (adv,),
            )
            return cursor.fetchall()
    finally:
        connection.close()          