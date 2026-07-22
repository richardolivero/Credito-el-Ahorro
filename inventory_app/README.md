# Sistema de Gestión de Inventario y Finanzas

Aplicación web completa para la gestión de inventario, ventas, cobros, finanzas y seguimiento GPS de trabajadores.

## 🚀 Características Principales

### Roles de Usuario
- **Administrador/Propietario**: Acceso total al sistema
- **Cobrador/Vendedor**: Acceso limitado a sus propias operaciones

### Sistema de Comisiones
- **Vehículo Propio**: 30% sobre lo recaudado en el día
- **Vehículo de Empresa**: 15% sobre lo recaudado en el día
- **Aguinaldo**: 1% adicional de la comisión base se acumula automáticamente

### Regla de Precios 3x1
Si el costo del producto es 1, el precio de venta es 3 (aplicable a ventas al contado y crédito)

### Funcionalidades Clave
- ✅ Seguimiento GPS en tiempo real de vendedores
- ✅ Registro completo de ventas y cobros con ubicación
- ✅ Gestión de inventario con trazabilidad
- ✅ Control de finanzas y balances
- ✅ Gestión de clientes con descuentos especiales
- ✅ Reportes exportables (CSV)
- ✅ Interfaz responsive adaptable a móviles

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Navegar al directorio del proyecto

```bash
cd /workspace/inventory_app
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## 👤 Credenciales de Acceso

### Administrador
- **Usuario**: admin
- **Contraseña**: admin123

### Vendedor (ejemplo)
- **Usuario**: vendedor1
- **Contraseña**: vendedor123

## 📁 Estructura del Proyecto

```
inventory_app/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias
├── instance/
│   └── inventory.db      # Base de datos SQLite (se crea automáticamente)
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/               # JavaScript personalizado
└── templates/
    ├── base.html         # Plantilla base
    ├── login.html        # Página de login
    ├── admin/
    │   ├── dashboard.html
    │   ├── sellers.html
    │   ├── seller_form.html
    │   ├── products.html
    │   ├── product_form.html
    │   ├── customers.html
    │   ├── customer_form.html
    │   ├── finance.html
    │   ├── map.html
    │   └── reports.html
    └── seller/
        ├── dashboard.html
        ├── sale_form.html
        ├── collection_form.html
        └── commissions.html
```

## 📖 Uso de la Aplicación

### Panel del Administrador

1. **Dashboard**: Vista general con métricas del día
2. **Vendedores**: Gestionar vendedores y su tipo de vehículo
3. **Productos**: Administar inventario con regla 3x1 automática
4. **Clientes**: Gestionar clientes y descuentos especiales
5. **Finanzas**: Ver balance de ingresos y comisiones
6. **Mapa GPS**: Ver ubicación en tiempo real de vendedores
7. **Reportes**: Generar y exportar reportes

### Panel del Vendedor

1. **Dashboard**: Ver resumen diario y clientes con saldo pendiente
2. **Nueva Venta**: Registrar venta con productos, descuentos y ubicación GPS
3. **Nuevo Cobro**: Registrar cobro de crédito
4. **Mis Comisiones**: Ver comisiones y aguinaldo acumulado

## 🗺️ Uso del GPS

Los vendedores deben:
1. Permitir el acceso a la ubicación en su navegador
2. Mantener la pestaña abierta durante su jornada laboral
3. La ubicación se actualiza automáticamente cada 30 segundos

El administrador puede ver:
- Ubicación actual de cada vendedor
- Historial de ubicaciones
- Qué está vendiendo/cobrando cada vendedor

## 💰 Cálculo de Comisiones

**Ejemplo:**
- Recaudación diaria: 100 córdobas
- Vehículo propio: Comisión = 30 córdobas (30%), Aguinaldo = 0.30 córdobas (1% de 30)
- Vehículo empresa: Comisión = 15 córdobas (15%), Aguinaldo = 0.15 córdobas (1% de 15)

**Importante**: La comisión se calcula sobre lo RECAUDADO (cobrado) en el día, no sobre ventas a crédito pendientes.

## 📊 Exportación de Datos

Los reportes pueden exportarse en formato CSV para:
- Ventas
- Cobros
- Inventario
- Comisiones

## 🔐 Seguridad

- Las contraseñas están encriptadas usando Werkzeug
- Sesiones protegidas con Flask-Login
- Roles diferenciados con control de acceso

## 🛠️ Soporte Técnico

Para problemas o preguntas, revise los logs de la aplicación en la consola donde se ejecuta el servidor.

## 📝 Licencia

Este software es propiedad privada. Todos los derechos reservados.
