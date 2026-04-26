# TP Final - Programación Avanzada 2026

Sistema de recomendación AdTech: pipeline de generación de recomendaciones y API de servicio.

## Integrantes

- Carolina Vence
- [Compañero 2]
- [Compañero 3]

## Arquitectura

El sistema consta de tres componentes principales:

1. **Pipeline de datos (Airflow sobre Compute Engine)**: genera recomendaciones diarias mediante dos modelos (TopCTR y TopProduct).
2. **Base de datos (Cloud SQL PostgreSQL)**: almacena las recomendaciones pre-computadas.
3. **API (FastAPI sobre Cloud Run)**: expone endpoints HTTP para consultar las recomendaciones.

## Estructura del repositorio

- `airflow/`: DAGs y tareas del pipeline de Airflow.
- `api/`: código de la API FastAPI y Dockerfile.
- `sql/`: scripts de creación de la base de datos.
- `scripts/`: script de generación de datos de prueba.
- `informe/`: informe final del TP.

## Recursos en GCP

- Proyecto: `tp-adtech`
- Cloud SQL: `sqp-tp-adtech` (con bases `airflow_db` y `recommendations_db`)
- VM: `vm-tp-adtech` (IP estática: `34.171.144.214`)
- Bucket: `tp-adtech-data`
- Service Account: `airflow-vm-sa@tp-adtech.iam.gserviceaccount.com`

## Endpoints de la API

- `GET /recommendations/{adv}/{model}`: recomendaciones del día para un advertiser y modelo.
- `GET /stats`: estadísticas generales sobre las recomendaciones.
- `GET /history/{adv}`: recomendaciones del advertiser en los últimos 7 días.
