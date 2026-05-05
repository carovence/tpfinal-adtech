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

@app.get("/stats")
def stats():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT\n"
                "  COUNT(*) AS total_recomendaciones,\n"
                "  COUNT(DISTINCT advertiser_id) AS advertisers_unicos,\n"
                "  COUNT(DISTINCT date) AS fechas_con_datos,\n"
                "  MAX(date) AS ultima_fecha\n"
                "FROM recommendations"
            )
            generales = cursor.fetchone()

            cursor.execute(
                "SELECT model, COUNT(*) AS total\n"
                "FROM recommendations\n"
                "GROUP BY model\n"
                "ORDER BY model"
            )
            por_modelo = cursor.fetchall()

            return {
                "total_recomendaciones": generales["total_recomendaciones"],
                "advertisers_unicos": generales["advertisers_unicos"],
                "fechas_con_datos": generales["fechas_con_datos"],
                "ultima_fecha": generales["ultima_fecha"],
                "recomendaciones_por_modelo": por_modelo,
            }
    finally:
        connection.close()