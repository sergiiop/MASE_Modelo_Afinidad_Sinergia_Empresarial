#!/bin/bash
set -e

# Script para iniciar la aplicación MASE

# Mostrar variables de entorno (sin mostrar contraseñas)
echo "Iniciando MASE en entorno: $MASE_ENVIRONMENT"
echo "Host: $MASE_HOST, Puerto: $MASE_PORT"
echo "Servidor PostgreSQL: $MASE_POSTGRES_SERVER:$MASE_POSTGRES_PORT"

# Esperar a que PostgreSQL esté disponible
echo "Esperando a que PostgreSQL esté disponible..."

# Contador para timeout
count=0
max_tries=30

until PGPASSWORD=$MASE_POSTGRES_PASSWORD psql -h $MASE_POSTGRES_SERVER -U $MASE_POSTGRES_USER -d $MASE_POSTGRES_DB -c '\q' 2>/dev/null; do
  echo "PostgreSQL no está disponible aún - esperando..."
  sleep 2
  count=$((count+1))
  
  if [ $count -ge $max_tries ]; then
    echo "Error: Tiempo de espera agotado para PostgreSQL. Verifique la configuración."
    exit 1
  fi
done

echo "PostgreSQL está disponible."

# Inicializar la base de datos
echo "Inicializando la base de datos..."
python -m app.db.init_db

# Verificar si la inicialización fue exitosa
if [ $? -ne 0 ]; then
  echo "Error: Falló la inicialización de la base de datos. Revise los logs para más detalles."
  exit 1
fi

echo "Base de datos inicializada correctamente."

# Iniciar la aplicación
echo "Iniciando la aplicación MASE..."
if [ "$MASE_ENVIRONMENT" = "development" ]; then
  echo "Modo de desarrollo con recarga automática"
  exec uvicorn app.main:app --host $MASE_HOST --port $MASE_PORT --reload
else
  echo "Modo de producción con $MASE_WORKERS workers"
  exec uvicorn app.main:app --host $MASE_HOST --port $MASE_PORT --workers $MASE_WORKERS --proxy-headers
fi
