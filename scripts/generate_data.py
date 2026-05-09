#!/usr/bin/env python
# coding: utf-8

# In[1]:


import io
import random
import string
import pandas as pd
from google.cloud import storage


# In[2]:


# ================================================================
# CONFIGURACIÓN — ajustar según el bucket del equipo
# ================================================================
BUCKET_NAME = "tp-adtech-data-cnaa"
RAW_PREFIX = "raw"
 
# Cantidad de eventos por día (la notebook original tenía 100.000 totales)
PRODUCT_VIEWS_PER_DAY = 2400
ADS_VIEWS_PER_DAY = 2400
 
# Catálogo
N_ACTIVE_ADVERTISERS = 20
N_INACTIVE_ADVERTISERS = 5
PRODUCTS_PER_ADVERTISER = 100
 
# CTR objetivo (probabilidad de click vs impression)
CLICK_WEIGHT = 1
IMPRESSION_WEIGHT = 99
 
# Fechas a generar (mismo rango que la notebook de la cátedra)
DATES = (
    [f"2026-04-{day:02d}" for day in range(18, 31)]
    + [f"2026-05-{day:02d}" for day in range(1, 30)]
)
 
# Semilla para reproducibilidad
RANDOM_SEED = 4


# In[3]:


# ================================================================
# FUNCIONES
# ================================================================
 
def generate_advertisers():
    """Genera 20 advertisers activos y 5 inactivos."""
    active = [
        "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        for _ in range(N_ACTIVE_ADVERTISERS)
    ]
    inactive = [
        "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        for _ in range(N_INACTIVE_ADVERTISERS)
    ]
    return active, inactive
 
 
def generate_catalogs(all_advertisers):
    """Para cada advertiser, genera un catálogo de 100 productos."""
    return {
        adv: [
            "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            for _ in range(PRODUCTS_PER_ADVERTISER)
        ]
        for adv in all_advertisers
    }
 
 
def generate_product_views_for_date(date, all_advertisers, catalogs, n_rows):
    """Genera n_rows de vistas de productos para una fecha específica."""
    rows = []
    for _ in range(n_rows):
        adv = random.choice(all_advertisers)
        product = random.choice(catalogs[adv])
        rows.append([adv, product, date])
    return pd.DataFrame(rows, columns=["advertiser_id", "product_id", "date"])
 
 
def generate_ads_views_for_date(date, all_advertisers, catalogs, n_rows):
    """Genera n_rows de vistas de ads (impressions y clicks) para una fecha."""
    rows = []
    for _ in range(n_rows):
        adv = random.choice(all_advertisers)
        product = random.choice(catalogs[adv])
        event_type = random.choices(
            ["impression", "click"],
            weights=[IMPRESSION_WEIGHT, CLICK_WEIGHT],
        )[0]
        rows.append([adv, product, event_type, date])
    return pd.DataFrame(
        rows, columns=["advertiser_id", "product_id", "type", "date"]
    )
 
 
def upload_dataframe_to_gcs(df, bucket, blob_path):
    """Sube un DataFrame como CSV al bucket de GCS."""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
    print(f"  ✓ Subido: gs://{BUCKET_NAME}/{blob_path} ({len(df):,} filas)")
 


# In[4]:


def main():
    random.seed(RANDOM_SEED)
 
    # Cliente de Storage (usa las credenciales de gcloud auth application-default login)
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
 
    print(f"🪣 Bucket destino: gs://{BUCKET_NAME}/{RAW_PREFIX}/")
    print()
 
    # 1. Generar advertisers y catálogos
    print("📋 Generando advertisers y catálogos...")
    active_advertisers, inactive_advertisers = generate_advertisers()
    all_advertisers = active_advertisers + inactive_advertisers
    catalogs = generate_catalogs(all_advertisers)
    print(f"   Activos: {len(active_advertisers)}, inactivos: {len(inactive_advertisers)}")
 
    # 2. Subir lista de advertisers activos
    print("\n📤 Subiendo lista de advertisers activos...")
    df_advertisers = pd.DataFrame(active_advertisers, columns=["advertiser_id"])
    upload_dataframe_to_gcs(
        df_advertisers, bucket, f"{RAW_PREFIX}/advertisers.csv"
    )
 
    # 3. Generar y subir un archivo por día
    print(f"\n📅 Generando datos para {len(DATES)} días...")
    for date in DATES:
        print(f"\n  📆 {date}")
 
        # Product views
        df_pv = generate_product_views_for_date(
            date, all_advertisers, catalogs, PRODUCT_VIEWS_PER_DAY
        )
        upload_dataframe_to_gcs(
            df_pv,
            bucket,
            f"{RAW_PREFIX}/product_views/date={date}/data.csv",
        )
 
        # Ads views
        df_av = generate_ads_views_for_date(
            date, all_advertisers, catalogs, ADS_VIEWS_PER_DAY
        )
        upload_dataframe_to_gcs(
            df_av,
            bucket,
            f"{RAW_PREFIX}/ads_views/date={date}/data.csv",
        )
 
    print("\n✅ Listo! Datos cargados en el bucket.")
    print(
        f"   Total: {len(DATES)} días × 2 archivos = {len(DATES) * 2} archivos + 1 advertisers.csv"
    )
 
 
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:


