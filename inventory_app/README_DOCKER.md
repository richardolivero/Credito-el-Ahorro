# Aplicación de Gestión de Inventario y Finanzas

Aplicación web completa para gestión de inventario, ventas, cobros, finanzas y seguimiento GPS de trabajadores.

## 🚀 Instalación con Docker (Recomendado)

### Requisitos previos
- Docker instalado ([Instrucciones](https://docs.docker.com/get-docker/))
- Docker Compose instalado (viene incluido con Docker Desktop)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <repositorio>
   cd inventory_app
   ```

2. **Construir y ejecutar con Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Acceder a la aplicación**
   
   Abre tu navegador y ve a: **http://localhost:5000**

### Credenciales por defecto

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Vendedor/Cobrador:**
- Usuario: `vendedor1`
- Contraseña: `vendedor123`

### Detener la aplicación
```bash
docker-compose down
```

### Reiniciar la aplicación
```bash
docker-compose restart
```

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

---

## 📦 Instalación Manual (Sin Docker)

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

3. **Acceder a la aplicación**
   
   Abre tu navegador y ve a: **http://localhost:5000**

---

## 📋 Características Principales

### Roles de Usuario
- **Administrador**: Acceso total al sistema, reportes, configuración
- **Cobrador/Vendedor**: Acceso limitado a sus operaciones y ubicación

### Sistema de Comisiones
- **Vehículo propio**: 30% del total recaudado en el día
- **Vehículo de empresa**: 15% del total recaudado en el día
- **Aguinaldo**: Acumulación automática del 1% sobre la comisión base

### Funcionalidades
- ✅ Seguimiento GPS en tiempo real de trabajadores
- ✅ Registro de ventas (contado/crédito) con descuentos
- ✅ Registro de cobros de crédito
- ✅ Gestión de inventario con precios 3x1
- ✅ Control financiero completo
- ✅ Gestión de clientes y historial
- ✅ Reportes exportables (PDF/Excel)
- ✅ Panel de administrador con métricas en tiempo real
- ✅ Interfaz responsive adaptada para móviles

### Precios de Productos
Regla "3 x 1": Si el costo es 1, el precio de venta es 3

---

## 🗺️ Uso del Mapa GPS

El administrador puede ver en tiempo real:
- Ubicación actual de cada trabajador
- Ventas y cobros realizados en la jornada
- Recorrido y rutas tomadas

Los vendedores deben activar el envío de ubicación GPS durante su jornada laboral.

---

## 💾 Persistencia de Datos

La base de datos se almacena en `instance/inventory.db`. Con Docker, este directorio está montado como volumen para preservar los datos incluso si el contenedor se elimina.

**Importante**: No elimines el directorio `instance` si quieres conservar tus datos.

---

## 🔧 Configuración Avanzada

### Cambiar el puerto
Edita `docker-compose.yml` y modifica:
```yaml
ports:
  - "8080:5000"  # Cambia 5000 por el puerto deseado
```

### Resetear la base de datos
```bash
rm instance/inventory.db
docker-compose restart
```

---

## 📞 Soporte

Para problemas o preguntas, revisa los logs:
```bash
docker-compose logs app
```

---

## 🛡️ Seguridad

**Importante**: Cambia las contraseñas por defecto después de la primera instalación desde el panel de administración.
