# Guía de Instalación y Uso - Sistema de Gestión de Inventario y Finanzas

## 🎯 Objetivo

Esta aplicación permite gestionar inventario, ventas, cobros, finanzas y seguimiento GPS de trabajadores para negocios que manejan ventas al contado y a crédito.

---

## 🚀 Instalación con Docker (Recomendado)

### ¿Por qué Docker?

Docker permite ejecutar la aplicación en cualquier sistema operativo (Windows, Mac, Linux) sin necesidad de instalar Python ni configurar dependencias manualmente. Todo viene empaquetado en un contenedor.

### Paso 1: Instalar Docker

**Windows/Mac:**
- Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop/
- Instala siguiendo las instrucciones
- Reinicia tu computadora si es necesario

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### Paso 2: Verificar instalación

Abre una terminal y ejecuta:
```bash
docker --version
docker-compose --version
```

Deberías ver algo como:
```
Docker version 24.x.x, build ...
Docker Compose version v2.x.x
```

### Paso 3: Ejecutar la aplicación

#### Opción A: Usando el script automático (Más fácil)

**En Windows:**
```cmd
cd inventory_app
start.bat
```

**En Mac/Linux:**
```bash
cd inventory_app
./start.sh
```

#### Opción B: Manual con docker-compose

```bash
cd inventory_app
docker-compose up --build
```

#### Opción C: Solo con Docker

```bash
cd inventory_app
docker build -t inventory-app .
docker run -d -p 5000:5000 -v $(pwd)/instance:/app/instance --name inventory_container inventory-app
```

### Paso 4: Acceder a la aplicación

Abre tu navegador web y ve a:

**http://localhost:5000**

### Paso 5: Iniciar sesión

| Rol | Usuario | Contraseña | Permisos |
|-----|---------|------------|----------|
| Administrador | `admin` | `admin123` | Acceso total |
| Vendedor | `vendedor1` | `vendedor123` | Ventas, cobros, GPS |

⚠️ **Importante**: Cambia las contraseñas después del primer inicio de sesión.

---

## 📋 Funcionalidades Principales

### Para Administradores

1. **Panel de Control**
   - Vista general de ventas del día
   - Total recaudado por trabajador
   - Comisiones y aguinaldo acumulado
   - Stock bajo de productos
   - Mapa con ubicación de trabajadores en tiempo real

2. **Gestión de Productos**
   - Agregar, editar, eliminar productos
   - El precio se calcula automáticamente (costo × 3)
   - Control de stock mínimo
   - Historial de movimientos

3. **Gestión de Trabajadores**
   - Crear usuarios vendedores
   - Asignar tipo de vehículo (propio/empresa)
   - Ver comisiones diarias
   - Seguimiento GPS en tiempo real
   - Historial de rutas

4. **Gestión de Clientes**
   - Registrar clientes con descuentos especiales
   - Ver historial de compras
   - Control de saldo pendiente (crédito)

5. **Reportes y Finanzas**
   - Balance diario/semanal/mensual
   - Ventas por producto, cliente, zona, trabajador
   - Exportar a PDF o Excel
   - Control de ingresos y egresos

### Para Vendedores/Cobradores

1. **Registrar Venta**
   - Seleccionar cliente
   - Agregar productos
   - Aplicar descuentos (si tiene permiso)
   - Indicar si es contado o crédito
   - Ubicación GPS automática

2. **Registrar Cobro**
   - Seleccionar cliente con saldo pendiente
   - Registrar monto cobrado
   - Método de pago
   - Ubicación GPS automática

3. **Mi Panel**
   - Comisión del día
   - Aguinaldo acumulado
   - Historial personal
   - Clientes asignados con saldo pendiente

---

## 💰 Sistema de Comisiones

### Cálculo Automático

La comisión se calcula sobre el **total recaudado en el día** (ventas al contado + cobros de crédito):

| Tipo de Vehículo | Comisión Base | Aguinaldo Acumulado |
|------------------|---------------|---------------------|
| Propio | 30% del recaudado | 1% de la comisión base |
| Empresa | 15% del recaudado | 1% de la comisión base |

### Ejemplo Práctico

**Escenario**: Vendedor recauda 100 córdobas en el día

**Con vehículo propio:**
- Comisión base: 30 córdobas (30% de 100)
- Aguinaldo: 0.30 córdobas (1% de 30)

**Con vehículo de empresa:**
- Comisión base: 15 córdobas (15% de 100)
- Aguinaldo: 0.15 córdobas (1% de 15)

---

## 🗺️ Seguimiento GPS

### Requisitos

- El vendedor debe activar el GPS en su dispositivo móvil
- La aplicación solicita permisos de ubicación
- El envío de ubicación es obligatorio durante la jornada

### Funcionamiento

1. El vendedor inicia sesión en la app
2. Activa el botón "Iniciar Jornada" con GPS
3. Su ubicación se actualiza cada 30 segundos
4. El administrador puede ver en tiempo real:
   - Ubicación exacta en mapa
   - Última venta/cobro realizado
   - Recorrido de la jornada

---

## 📊 Precios y Descuentos

### Regla de Precios "3 x 1"

Todos los productos siguen esta regla:
```
Precio de Venta = Costo × 3
```

**Ejemplo:**
- Costo del producto: 10 córdobas
- Precio de venta: 30 córdobas

### Descuentos

Tipos de descuento disponibles:

1. **Descuento por Cliente Frecuente**
   - Configurado en el perfil del cliente (0-20%)
   - Se aplica automáticamente

2. **Descuento Especial**
   - Aplicable por el administrador
   - Por promoción o situación especial
   - Queda registrado en la venta

---

## 🛑 Comandos Útiles de Docker

### Verificar estado
```bash
docker-compose ps
```

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Detener aplicación
```bash
docker-compose down
```

### Reiniciar aplicación
```bash
docker-compose restart
```

### Actualizar después de cambios en el código
```bash
docker-compose down
docker-compose up --build -d
```

### Eliminar todo (¡CUIDADO! Borra la base de datos)
```bash
docker-compose down -v
```

---

## 💾 Persistencia de Datos

### ¿Dónde se guardan los datos?

La base de datos SQLite se almacena en:
```
inventory_app/instance/inventory.db
```

### Volumen de Docker

El archivo `docker-compose.yml` configura un volumen que mapea:
- **Contenedor**: `/app/instance`
- **Host**: `./instance`

Esto significa que:
✅ Los datos persisten aunque elimines el contenedor
✅ Puedes hacer backup copiando la carpeta `instance`
✅ Puedes restaurar datos reemplazando el archivo `.db`

### Backup de la Base de Datos

```bash
# Crear backup
cp inventory_app/instance/inventory.db backup_$(date +%Y%m%d).db

# Restaurar backup
cp backup_20240101.db inventory_app/instance/inventory.db
docker-compose restart
```

---

## 🔧 Solución de Problemas

### Error: "Puerto ya en uso"

**Problema**: Otro programa está usando el puerto 5000

**Solución 1**: Cambiar puerto en docker-compose.yml
```yaml
ports:
  - "8080:5000"  # Cambia 5000 por otro puerto
```

**Solución 2**: Detener otros servicios
```bash
# En Windows
netstat -ano | findstr :5000

# En Mac/Linux
lsof -i :5000
```

### Error: "No se puede conectar a la base de datos"

**Solución**:
```bash
docker-compose down
rm -rf inventory_app/instance
docker-compose up --build
```

### Error: "Permiso denegado" en Linux/Mac

**Solución**:
```bash
chmod +x start.sh
./start.sh
```

### La aplicación no carga

**Verifica**:
1. Docker está corriendo
2. El contenedor está activo: `docker-compose ps`
3. No hay errores en logs: `docker-compose logs`

### El GPS no funciona

**Verifica**:
1. El navegador tiene permisos de ubicación
2. El dispositivo tiene GPS activado
3. Estás usando HTTPS (requerido para GPS en producción)

---

## 🌐 Acceso Remoto

### Desde otra computadora en la misma red

1. Averigua la IP de tu computadora:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`

2. Accede desde otro dispositivo:
   ```
   http://[TU_IP]:5000
   ```

### Desde internet (producción)

Para acceso público necesitas:
1. Un servidor con IP pública
2. Configurar un dominio
3. Certificado SSL (HTTPS)
4. Configurar Nginx como proxy inverso

---

## 📱 Uso en Dispositivos Móviles

La aplicación es **responsive** y se adapta a:

- ✅ Teléfonos móviles (Android/iOS)
- ✅ Tablets
- ✅ Computadoras de escritorio
- ✅ Laptops

### Recomendaciones para vendedores

1. Usa el navegador Chrome o Firefox
2. Activa la ubicación GPS
3. Mantén la pestaña abierta durante la jornada
4. Puedes agregar la app a la pantalla de inicio:
   - Chrome Android: Menú → "Agregar a la pantalla principal"
   - Safari iOS: Botón compartir → "Agregar al inicio"

---

## 🔐 Seguridad

### Mejores Prácticas

1. **Cambiar contraseñas por defecto inmediatamente**
2. **Usar contraseñas fuertes** (mínimo 8 caracteres, mayúsculas, números)
3. **No compartir credenciales** entre trabajadores
4. **Cerrar sesión** al terminar la jornada
5. **Actualizar Docker** regularmente

### Para Producción

Si vas a usar la aplicación en producción:

1. Cambia la `SECRET_KEY` en `app.py`
2. Usa HTTPS con certificado SSL
3. Configura autenticación de dos factores
4. Realiza backups diarios
5. Monitorea los logs regularmente

---

## 📞 Soporte

### Ver logs de la aplicación
```bash
docker-compose logs app
```

### Logs en tiempo real
```bash
docker-compose logs -f app
```

### Acceder al contenedor
```bash
docker exec -it inventory_app bash
```

### Reiniciar solo el servicio
```bash
docker-compose restart app
```

---

## 📄 Archivos del Proyecto

```
inventory_app/
├── app.py                 # Código principal de la aplicación
├── requirements.txt       # Dependencias de Python
├── Dockerfile            # Configuración de la imagen Docker
├── docker-compose.yml    # Orquestación de contenedores
├── README_DOCKER.md      # Esta documentación
├── start.sh              # Script de inicio (Linux/Mac)
├── start.bat             # Script de inicio (Windows)
├── .dockerignore         # Archivos a ignorar en Docker
├── templates/            # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── admin/           # Vistas del administrador
│   └── seller/          # Vistas del vendedor
├── static/              # Archivos estáticos
│   ├── css/            # Hojas de estilo
│   └── js/             # JavaScript (mapas, GPS)
└── instance/           # Base de datos (generado automáticamente)
    └── inventory.db
```

---

## 🎓 Capacitación Rápida

### Para Administradores (5 minutos)

1. Inicia sesión como `admin`
2. Explora el panel principal
3. Revisa los productos de ejemplo
4. Verifica la ubicación de vendedores en el mapa
5. Genera un reporte de ventas

### Para Vendedores (5 minutos)

1. Inicia sesión con tus credenciales
2. Activa tu ubicación GPS
3. Practica registrando una venta
4. Practica registrando un cobro
5. Revisa tu comisión del día

---

## 🆕 Actualizaciones Futuras

Próximas características planeadas:
- Notificaciones push
- Reportes automáticos por email
- Integración con pasarelas de pago
- App nativa para móviles
- Múltiples sucursales
- Control de caja chica

---

**© 2024 - Sistema de Gestión de Inventario y Finanzas**
