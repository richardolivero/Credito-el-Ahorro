@echo off
echo 🚀 Iniciando aplicacion de Inventario y Finanzas con Docker...
echo.

REM Verificar si Docker esta instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker no esta instalado.
    echo Por favor instala Docker Desktop desde: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

echo ✅ Docker detectado correctamente
echo.

REM Navegar al directorio del script
cd /d "%~dp0"

echo 📦 Construyendo imagen Docker...
docker-compose build

echo.
echo 🚀 Iniciando contenedores...
docker-compose up -d

echo.
echo ⏳ Esperando a que la aplicacion este lista...
timeout /t 10 /nobreak >nul

REM Verificar si el servicio esta corriendo
docker-compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: La aplicacion no pudo iniciarse correctamente.
    echo Revisa los logs con: docker-compose logs
    pause
    exit /b 1
)

echo.
echo ✅ ¡Aplicacion iniciada exitosamente!
echo.
echo 🌐 Accede en tu navegador a: http://localhost:5000
echo.
echo 📋 Credenciales por defecto:
echo    Administrador: admin / admin123
echo    Vendedor: vendedor1 / vendedor123
echo.
echo 🛑 Para detener la aplicacion ejecuta:
echo    docker-compose down
echo.
echo 📊 Para ver logs en tiempo real:
echo    docker-compose logs -f
echo.
pause
