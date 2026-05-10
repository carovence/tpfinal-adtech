# TP Final - Programación Avanzada

Sistema de recomendación AdTech sobre Google Cloud Platform.
Maestría en Ciencia de Datos — Universidad de San Andrés, 2026.

## Descripción

Pipeline diario que procesa logs de actividad de usuarios y calcula recomendaciones de productos con dos modelos (TopCTR y TopProduct), expuestas mediante una API REST.

## Links

- **API en producción:** https://api-recommendations-402172564462.us-central1.run.app
- **Documentación interactiva (Swagger):** https://api-recommendations-402172564462.us-central1.run.app/docs
  
## Lista de anuncios activos

2WPF1NXECF3G6NUMWDO7
 5E325T5HYL61QSABVR5V
 62FIK8F2YT8JSFDBLEC9
 6X20RDH567MX2X3TXYJ7
 8C88YB6E8YCGWU07HA7A
 AK81O7W3KGPEN8LABG2N
 EN1SA43DTN2LIR8DEW5S
 GXLKAA83238FVRU718EX
 IDOFCO721HTJGDH7332G
 IOBPI63RBJIHI5FB7U9O
 K6Z0X85ZUY0TSF4RCG5J
 KD9PHCBGYFBRI9ET1O9R
 LTRZRCI4M19WYVL6Q6L5
 LW045DVYSGRD75TK6U54
 M0LU6DCI1WILGQBZ6808
 OAGTYWN8WFC997VLDJH7
 OY5LNPB5A8FF43ITRZG3
 P41C5HK4P2G5GFRMT6ZA
 SOVPFK3BBWKTQM9HOHWJ
 Y0W3K7OV6ZLILW96OO3K
 
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
