# Troubleshooting

Acá vamos anotando los problemas que se nos van presentando durante el desarrollo del TP y cómo los resolvimos. Esta documentación nos sirve para el informe final y para el coloquio.

## Problema: Service Account sin acceso al bucket por API faltante

**Síntoma:** desde la VM `vm-tp-adtech`, los comandos `gcloud storage ls` y `gcloud storage cp` fallaban con error `storage.objects.list denied`, a pesar de tener los roles "Administrador de objetos de Storage" y "Cliente de Cloud SQL" correctamente asignados.

**Causa raíz:** la API **Cloud Resource Manager** no estaba habilitada en el proyecto, lo cual impide que los permisos IAM se evalúen correctamente para Service Accounts sobre recursos específicos.

**Solución:** desde Cloud Shell (con la cuenta de propietario del proyecto), habilitar las APIs necesarias:

\`\`\`bash
gcloud services enable \\
  cloudresourcemanager.googleapis.com \\
  compute.googleapis.com \\
  sqladmin.googleapis.com \\
  storage.googleapis.com \\
  iam.googleapis.com \\
  iamcredentials.googleapis.com \\
  run.googleapis.com \\
  artifactregistry.googleapis.com \\
  cloudbuild.googleapis.com
\`\`\`

Y reforzar los permisos de la SA a nivel bucket:

\`\`\`bash
gcloud storage buckets add-iam-policy-binding gs://tp-adtech-data \\
  --member="serviceAccount:airflow-vm-sa@tp-adtech.iam.gserviceaccount.com" \\
  --role="roles/storage.objectAdmin"
\`\`\`

**Aprendizaje:** en GCP, asignar roles IAM no es suficiente por sí solo: las APIs correspondientes deben estar habilitadas para que esos permisos sean evaluados.
