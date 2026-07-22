# Sistema de Gestión de Inventario y Finanzas

Aplicación web completa para gestión de inventario, ventas, cobros, finanzas y seguimiento GPS de trabajadores.

## 🚀 Inicio Rápido con Docker

### Opción 1: Usando docker-compose (Recomendado)

```bash
cd inventory_app
docker-compose up --build
```

### Opción 2: Usando docker directamente

```bash
cd inventory_app
docker build -t inventory-app .
docker run -d -p 5000:5000 -v $(pwd)/instance:/app/instance --name inventory_container inventory-app
```

## 📋 Acceder a la Aplicación

Una vez iniciado el contenedor, abre tu navegador en:

**http://localhost:5000**

### Credenciales por defecto

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `admin123` |
| Vendedor | `vendedor1` | `vendedor123` |

## 🛑 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener la aplicación
docker-compose down

# Reiniciar
docker-compose restart

# Eliminar contenedor y volumenes (¡cuidado! borra la BD)
docker-compose down -v
```

## 📖 Documentación Completa

Consulta [README_DOCKER.md](inventory_app/README_DOCKER.md) para instrucciones detalladas.

## 📦 Estructura del Proyecto

```
inventory_app/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Orquestación Docker
├── README_DOCKER.md      # Documentación completa
├── templates/            # Plantillas HTML
├── static/               # Archivos estáticos (CSS, JS)
└── instance/             # Base de datos SQLite (persistente)
```

## 🔧 Características Principales

- ✅ **Roles de usuario**: Administrador y Vendedor/Cobrador
- ✅ **Comisiones automáticas**: 30% (vehículo propio) o 15% (empresa)
- ✅ **Aguinaldo**: 1% acumulado sobre comisión base
- ✅ **GPS en tiempo real**: Seguimiento de trabajadores en mapa
- ✅ **Precios 3x1**: Costo x3 = Precio de venta
- ✅ **Descuentos**: Para clientes frecuentes y especiales
- ✅ **Inventario completo**: Entradas, salidas, stock
- ✅ **Finanzas**: Ingresos, egresos, balances
- ✅ **Reportes exportables**: PDF y Excel
- ✅ **Responsive**: Adaptable a móviles

## 💾 Persistencia de Datos

La base de datos se guarda en `inventory_app/instance/inventory.db`. 
El volumen de Docker preserva los datos incluso si eliminas el contenedor.

## ⚠️ Seguridad

**Importante**: Cambia las contraseñas por defecto después de la primera instalación.
