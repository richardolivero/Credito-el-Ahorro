# Script de inicio rápido para Docker

#!/bin/bash

echo "🚀 Iniciando aplicación de Inventario y Finanzas con Docker..."
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado."
    echo "Por favor instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar si docker-compose está disponible (versión antigua o nueva)
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Error: Docker Compose no está disponible."
    echo "Por favor instala Docker Desktop o docker-compose."
    exit 1
fi

echo "✅ Docker detectado correctamente"
echo ""

# Navegar al directorio del proyecto
cd "$(dirname "$0")"

echo "📦 Construyendo imagen Docker..."
$COMPOSE_CMD build

echo ""
echo "🚀 Iniciando contenedores..."
$COMPOSE_CMD up -d

echo ""
echo "⏳ Esperando a que la aplicación esté lista..."
sleep 10

# Verificar si el servicio está corriendo
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo ""
    echo "✅ ¡Aplicación iniciada exitosamente!"
    echo ""
    echo "🌐 Accede en tu navegador a: http://localhost:5000"
    echo ""
    echo "📋 Credenciales por defecto:"
    echo "   Administrador: admin / admin123"
    echo "   Vendedor: vendedor1 / vendedor123"
    echo ""
    echo "🛑 Para detener la aplicación ejecuta:"
    echo "   $COMPOSE_CMD down"
    echo ""
    echo "📊 Para ver logs en tiempo real:"
    echo "   $COMPOSE_CMD logs -f"
    echo ""
else
    echo "❌ Error: La aplicación no pudo iniciarse correctamente."
    echo "Revisa los logs con: $COMPOSE_CMD logs"
    exit 1
fi
