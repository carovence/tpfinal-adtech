# TP Final - Programación Avanzada

Sistema de recomendación AdTech sobre Google Cloud Platform.
Maestría en Ciencia de Datos — Universidad de San Andrés, 2026.

## Descripción

Pipeline diario que procesa logs de actividad de usuarios y calcula recomendaciones de productos con dos modelos (TopCTR y TopProduct), expuestas mediante una API REST.

## Links

- **API en producción:** https://api-recommendations-402172564462.us-central1.run.app
- **Documentación interactiva (Swagger):** https://api-recommendations-402172564462.us-central1.run.app/docs

## Estructura del repositorio

    tpfinal-adtech/
    ├── airflow/dags/tp_pipeline.py    # Pipeline ETL diario
    ├── api/                           # API REST en FastAPI + Dockerfile
    ├── scripts/generate_data.py       # Generador de datos sintéticos
    ├── requirements.txt               # Dependencias del pipeline
    └── README.md

## Stack tecnológico

- **Apache Airflow** sobre Compute Engine (orquestación del pipeline)
- **PostgreSQL** en Cloud SQL (almacenamiento de recomendaciones)
- **FastAPI** desplegada en Cloud Run (serving online)
- **Google Cloud Storage** (datos crudos e intermedios)

## Endpoints de la API

| Endpoint | Descripción |
|---|---|
| `/health` | Health check |
| `/db-check` | Verifica conexión a Cloud SQL |
| `/recommendations/{adv}/{model}` | Top 20 productos del día |
| `/history/{adv}` | Histórico de últimos 7 días |
| `/stats` | Estadísticas globales |

Documentación completa en el informe entregado por campus.
