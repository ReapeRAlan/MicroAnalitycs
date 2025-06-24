# 🗄️ Configuración de Base de Datos - MicroAnalytics

## 📋 Archivos Incluidos

- **`init_db.py`** - Inicialización y gestión de tablas de la base de datos
- **`seed_data.py`** - Script de inyección de datos ficticios
- **`setup_database.py`** - Script automatizado de configuración completa
- **`seed_requirements.txt`** - Dependencias adicionales para el seeding

## 🚀 Configuración Rápida

### Opción 1: Configuración Automática
```bash
cd backend
python setup_database.py
```

Esto:
1.  Instala las dependencias necesarias
2.  Inicializa la base de datos
3.  Inyecta datos ficticios realistas

### Opción 2: Configuración Manual

#### Paso 1: Instalar dependencias
```bash
pip install faker==19.12.0
```

#### Paso 2: Inicializar base de datos
```bash
python init_db.py
```

#### Paso 3: Inyectar datos ficticios
```bash
python seed_data.py
```
## Relaciones de la base de datos:
## 1. Negocio
   - Entidad principal que posee otros recursos
   - Tiene múltiples Usuarios (relación 1:N)
   - Tiene múltiples Productos (relación 1:N)
   - Tiene múltiples Transacciones (relación 1:N)
   - Ejemplo: Un negocio 'Tienda ABC' tiene 4 empleados (usuarios), 50 productos y procesa 100 transacciones mensuales

## 2. Usuario
   - Pertenece a un Negocio (relación N:1)
   - Puede crear múltiples RegistrosChat (relación 1:N)
   - Ejemplo: El usuario 'Juan Pérez' trabaja en 'Tienda ABC' y ha iniciado 5 sesiones de chat

## 3. Producto
   - Pertenece a un Negocio (relación N:1)
   - Pertenece a una Categoría (relación N:1)
   - Tiene un registro de Inventario (relación 1:1)
   - Tiene múltiples PreciosProveedor (relación 1:N)
   - Tiene múltiples Predicciones (relación 1:N)
   - Aparece en múltiples DetallesTransacción (relación 1:N)
   - Ejemplo: El producto 'Leche Entera' pertenece a 'Tienda ABC', está en la categoría 'Lácteos', tiene stock de 50 unidades y se ha vendido 30 veces

## 4. Categoría
   - Contiene múltiples Productos (relación 1:N)
   - Ejemplo: La categoría 'Lácteos' contiene 15 productos diferentes de leche y queso

## 5. Inventario
   - Registra el stock de un Producto (relación 1:1)
   - Ejemplo: 'Leche Entera' tiene 50 unidades en inventario con último reabastecimiento el 15/05/2023

## 6. Transacción
   - Pertenece a un Negocio (relación N:1)
   - Contiene múltiples DetallesTransacción (relación 1:N)
   - Ejemplo: La transacción #1001 en 'Tienda ABC' contiene 5 artículos por un total de $45.99

## 7. DetalleTransacción
   - Pertenece a una Transacción (relación N:1)
   - Referencia un Producto (relación N:1)
   - Ejemplo: La transacción #1001 incluye 2 unidades de 'Leche Entera' a $1.99 cada una

## 8. Proveedor
   - Provee múltiples PreciosProveedor (relación 1:N)
   - Ejemplo: El proveedor 'Lácteos SA' suministra productos lácteos a múltiples negocios

## 9. PrecioProveedor
   - Pertenece a un Proveedor (relación N:1)
   - Referencia un Producto (relación N:1)
   - Ejemplo: 'Lácteos SA' vende 'Leche Entera' a los negocios a $1.50 por unidad

## 10. Predicción
    - Pronósticos para un Producto (relación N:1)
    - Ejemplo: Se predicen ventas de 65 unidades para 'Leche Entera' el próximo mes

## 11. RegistroChat
    - Creado por un Usuario (relación N:1)
    - Ejemplo: La sesión de chat #1234 fue iniciada por 'Juan Pérez' sobre disponibilidad de productos


## 📊 Datos Generados

El script `seed_data.py` genera datos realistas para todas las tablas:

### 🏢 Negocios (5 empresas)
- TechnoMart (Tecnología)
- FreshMarket (Supermercado)
- StyleHub (Moda)
- HomeDecor Plus (Hogar)
- SportZone (Deportes)

### 👥 Usuarios (15-25 por empresa)
- Roles: admin, manager, employee, analyst
- Datos realistas con Faker (nombres, emails, etc.)

### 📂 Categorías (10 categorías)
- Electrónicos, Ropa, Hogar, Deportes, Alimentación
- Libros, Juguetes, Belleza, Automóvil, Jardinería

### 📦 Productos (15-25 por empresa)
- Nombres realistas según categoría
- Precios entre €10-€500
- Descripciones generadas automáticamente

### 🚚 Proveedores (8 proveedores)
- Información de contacto realista
- Especializados por categoría

### 📊 Inventario
- Stock actual (0-100 unidades)
- Fechas de último ingreso

### 💰 Precios de Proveedores
- 1-3 proveedores por producto
- Precios 60-80% del precio base

### 🛒 Transacciones (20-40 por empresa)
- Últimos 90 días
- 1-5 productos por transacción
- Totales calculados automáticamente

### 🔮 Predicciones ML
- 2-4 predicciones por producto
- Modelos: linear_regression, random_forest, neural_network, arima
- Resultados ±20% del precio base

### 💬 Chat Logs (5-15 por usuario)
- Conversaciones realistas sobre análisis de datos
- Preguntas y respuestas típicas del sistema

##  Errores Comunes

### Error: "Database is locked" (SQLite Studio)
**⚠️ IMPORTANTE**: Si tienes SQLite Studio abierto, ciérralo antes de ejecutar los scripts.

1. **Cierra SQLite Studio completamente**
2. Asegúrate de que no hay conexiones activas a la base de datos
3. Ejecuta el script:
```bash
python setup_database.py
```

### Conflictos con SQLite Studio
SQLite Studio puede mantener conexiones activas que impiden la escritura. Para evitar problemas:

1. **Antes de ejecutar scripts**:
   - Cierra SQLite Studio
   - Verifica que no hay procesos de SQLite activos

2. **Después de ejecutar scripts**:
   - Puedes abrir SQLite Studio para ver los datos
   - Usa "Refresh" en SQLite Studio para ver los nuevos datos

### Error: "Table already exists"
```bash
python init_db.py --reset
```

## 📈 Verificación

Después de ejecutar los scripts, deberías tener:
- ✅ 5 empresas con datos realistas
- ✅ 15-125 usuarios distribuidos por empresa
- ✅ 75-125 productos con inventario
- ✅ 100-200 transacciones con detalles
- ✅ 150-500 predicciones ML
- ✅ 75-1875 logs de chat

## 🔄 Regenerar Datos

Para generar nuevos datos ficticios:
```bash
python seed_data.py
```

El script automáticamente:
1. Limpia los datos existentes
2. Genera nuevos datos con diferentes valores aleatorios
3. Mantiene la consistencia entre tablas relacionadas

---

💡 **Tip**: Usa `python setup_database.py` para una configuración completa y sin complicaciones.