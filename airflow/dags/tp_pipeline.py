"""
TP Final - Programación Avanzada.

Pipeline diario que:
1. FiltrarDatos: filtra logs por advertisers activos
2. TopCTR: top 20 productos con mejor CTR por advertiser
3. TopProduct: top 20 productos más vistos por advertiser
4. DBWriting: escribe las recomendaciones en Cloud SQL (PostgreSQL)

La fecha a procesar se toma del data_interval_start del DagRun (Jinja: {{ ds }}).
"""

import datetime
import os
from io import StringIO

import pandas as pd
import psycopg2
from google.cloud import storage

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


# Configuración
GCS_BUCKET = os.getenv("GCS_BUCKET", "tp-adtech-data")
TOP_N = 20

PG_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "database": os.getenv("PG_DATABASE", "recommendations_db"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD"),
}


# Helpers GCS
def _gcs_client():
    return storage.Client()


def _read_csv_from_gcs(blob_path):
    bucket = _gcs_client().bucket(GCS_BUCKET)
    content = bucket.blob(blob_path).download_as_text()
    return pd.read_csv(StringIO(content))


def _write_csv_to_gcs(df, blob_path):
    bucket = _gcs_client().bucket(GCS_BUCKET)
    bucket.blob(blob_path).upload_from_string(df.to_csv(index=False), content_type="text/csv")
    print(f"Wrote gs://{GCS_BUCKET}/{blob_path} ({len(df)} rows)")

def _next_day(date_str):
    return (datetime.datetime.strptime(date_str, "%Y-%m-%d")
            + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

# Tareas
def filtrar_datos(date_str):
    print(f"FiltrarDatos: input={date_str}, reco_date={_next_day(date_str)}")
    advertisers = _read_csv_from_gcs("raw/advertisers.csv")
    active_set = set(advertisers["advertiser_id"].astype(str))
    print(f"Active advertisers: {len(active_set)}")

    ads = _read_csv_from_gcs(f"raw/ads_views/date={date_str}/data.csv")
    ads_filt = ads[ads["advertiser_id"].astype(str).isin(active_set)].copy()
    print(f"Ads views: {len(ads)} -> {len(ads_filt)}")
    _write_csv_to_gcs(ads_filt, f"intermediate/date={date_str}/ads_views_filtered.csv")

    products = _read_csv_from_gcs(f"raw/product_views/date={date_str}/data.csv")
    products_filt = products[products["advertiser_id"].astype(str).isin(active_set)].copy()
    print(f"Product views: {len(products)} -> {len(products_filt)}")
    _write_csv_to_gcs(products_filt, f"intermediate/date={date_str}/product_views_filtered.csv")


def top_ctr(date_str):
    print(f"TopCTR: input={date_str}, reco_date={_next_day(date_str)}")
    df = _read_csv_from_gcs(f"intermediate/date={date_str}/ads_views_filtered.csv")
    counts = df.groupby(["advertiser_id", "product_id", "type"]).size().unstack(fill_value=0).reset_index()
    if "impression" not in counts.columns:
        counts["impression"] = 0
    if "click" not in counts.columns:
        counts["click"] = 0
    counts = counts[counts["impression"] > 0].copy()
    counts["ctr"] = counts["click"] / counts["impression"]
    top = (counts.sort_values(["advertiser_id", "ctr"], ascending=[True, False])
                 .groupby("advertiser_id").head(TOP_N).copy())
    top["rank"] = top.groupby("advertiser_id").cumcount() + 1
    top["model"] = "TopCTR"
    top["date"] = _next_day(date_str)
    out = top[["advertiser_id", "product_id", "model", "rank", "date"]]
    _write_csv_to_gcs(out, f"intermediate/date={date_str}/top_ctr.csv")


def top_product(date_str):
    print(f"TopProduct: input={date_str}, reco_date={_next_day(date_str)}")
    df = _read_csv_from_gcs(f"intermediate/date={date_str}/product_views_filtered.csv")
    counts = df.groupby(["advertiser_id", "product_id"]).size().reset_index(name="views")
    top = (counts.sort_values(["advertiser_id", "views"], ascending=[True, False])
                 .groupby("advertiser_id").head(TOP_N).copy())
    top["rank"] = top.groupby("advertiser_id").cumcount() + 1
    top["model"] = "TopProduct"
    top["date"] = _next_day(date_str)
    out = top[["advertiser_id", "product_id", "model", "rank", "date"]]
    _write_csv_to_gcs(out, f"intermediate/date={date_str}/top_product.csv")


def db_writing(date_str):
    print(f"DBWriting: input={date_str}, reco_date={_next_day(date_str)}")
    if not PG_CONFIG["password"]:
        raise ValueError("PG_PASSWORD no está seteada. Cargá las credenciales: source scripts/setup_env.sh")

    ctr = _read_csv_from_gcs(f"intermediate/date={date_str}/top_ctr.csv")
    prod = _read_csv_from_gcs(f"intermediate/date={date_str}/top_product.csv")
    all_recos = pd.concat([ctr, prod], ignore_index=True)
    print(f"Total recommendations to insert: {len(all_recos)}")

    rows = [
        (r["advertiser_id"], r["model"], r["product_id"], int(r["rank"]), r["date"])
        for _, r in all_recos.iterrows()
    ]

    conn = psycopg2.connect(**PG_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO recommendations (advertiser_id, model, product_id, rank, date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (advertiser_id, model, date, rank)
                DO UPDATE SET product_id = EXCLUDED.product_id
                """,
                rows,
            )
        conn.commit()
        print(f"Inserted/updated {len(rows)} rows")
    finally:
        conn.close()


# DAG
with DAG(
    dag_id="tp_pipeline",
    description="Pipeline de recomendaciones AdTech (TP Final)",
    schedule="0 3 * * *",  # Cada día a las 3 AM (procesa los datos del día anterior)
    start_date=datetime.datetime(2026, 4, 1),
    catchup=False,
    tags=["tp", "adtech"],
) as dag:

    # Pasamos {{ ds }} como string. Airflow lo resuelve al ejecutar la tarea.
    common_kwargs = {"date_str": "{{ ds }}"}

    t1 = PythonOperator(task_id="FiltrarDatos", python_callable=filtrar_datos, op_kwargs=common_kwargs)
    t2 = PythonOperator(task_id="TopCTR", python_callable=top_ctr, op_kwargs=common_kwargs)
    t3 = PythonOperator(task_id="TopProduct", python_callable=top_product, op_kwargs=common_kwargs)
    t4 = PythonOperator(task_id="DBWriting", python_callable=db_writing, op_kwargs=common_kwargs)

    t1 >> [t2, t3] >> t4
