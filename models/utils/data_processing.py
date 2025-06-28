from typing import Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.base import SessionLocal
from backend.models.transaction import Transaction
from backend.models.transaction_detail import TransactionDetail
from backend.models.product import Product
from backend.models.inventory import Inventory
from backend.models.category import Category
from backend.models.supplier_price import SupplierPrice

from .logger import model_logger
from .error_handling import handle_errors, DatabaseError, DataValidationError
from .data_validation import DataValidator, DataCleaner

def get_temporada(fecha: datetime) -> str:
    """Determina la temporada basada en el mes"""
    mes = fecha.month
    if mes in [12, 1, 2]:
        return 'verano'
    elif mes in [3, 4, 5]:
        return 'otoño'
    elif mes in [6, 7, 8]:
        return 'invierno'
    else:
        return 'primavera'

def get_dias_desde_ingreso(inventario, fecha_transaccion: datetime) -> int:
    """Calcula días desde el ingreso del inventario"""
    if inventario and hasattr(inventario, 'fecha_ingreso') and inventario.fecha_ingreso:
        return (fecha_transaccion - inventario.fecha_ingreso).days
    return 0

def get_rotacion_inventario(inventario, cantidad_vendida: int) -> float:
    """Calcula rotación de inventario"""
    if inventario and inventario.stock_actual > 0:
        return cantidad_vendida / inventario.stock_actual
    return 0.0

def get_precio_proveedor_promedio(precios_proveedor, fecha_transaccion: datetime) -> float:
    """Obtiene precio promedio del proveedor vigente"""
    if not precios_proveedor:
        return 0.0
    
    # Buscar precio más reciente antes o igual a la fecha de transacción
    precios_validos = [p for p in precios_proveedor if p.fecha <= fecha_transaccion]
    if precios_validos:
        return float(precios_validos[0].precio)  # Ya está ordenado desc
    return 0.0

def get_variacion_precio_proveedor(precios_proveedor, fecha_transaccion: datetime) -> float:
    """Calcula variación del precio del proveedor"""
    if len(precios_proveedor) < 2:
        return 0.0
    
    precios_validos = [p for p in precios_proveedor if p.fecha <= fecha_transaccion]
    if len(precios_validos) >= 2:
        precio_actual = float(precios_validos[0].precio)
        precio_anterior = float(precios_validos[1].precio)
        if precio_anterior > 0:
            return (precio_actual - precio_anterior) / precio_anterior
    return 0.0

@handle_errors(DatabaseError, default_return=pd.DataFrame())
def obtener_datos_enriquecidos(producto_id: int) -> pd.DataFrame:
    """
    Obtiene features enriquecidos para entrenamiento con validación y limpieza automática
    """
    if not isinstance(producto_id, int) or producto_id <= 0:
        raise DataValidationError(f"ID de producto inválido: {producto_id}")
    
    db = SessionLocal()
    try:
        # Consultas a la base de datos con manejo de errores
        transacciones = db.query(TransactionDetail).join(Transaction)\
            .filter(TransactionDetail.product_id == producto_id)\
            .order_by(Transaction.fecha)\
            .all()
        
        if not transacciones:
            model_logger.logger.warning(f"No se encontraron transacciones para producto {producto_id}")
            # Generar datos sintéticos para demo
            return _generar_datos_sinteticos(producto_id)
        
        producto = db.query(Product).filter(Product.id == producto_id).first()
        if not producto:
            raise DataValidationError(f"Producto {producto_id} no encontrado")
        
        inventario = db.query(Inventory).filter(Inventory.product_id == producto_id).first()
        precios_proveedor = db.query(SupplierPrice)\
            .filter(SupplierPrice.product_id == producto_id)\
            .order_by(SupplierPrice.fecha.desc())\
            .all()
        
        # Crear DataFrame base con estructura completa
        data_records = []
        
        for i, t in enumerate(transacciones):
            fecha_transaccion = t.transaccion.fecha
            
            # Features básicos
            record = {
                # Identificadores
                'producto_id': producto_id,
                'transaccion_id': t.transaccion.id,
                
                # Features temporales
                'fecha': fecha_transaccion,
                'dia_semana': fecha_transaccion.weekday(),
                'mes': fecha_transaccion.month,
                'dia_mes': fecha_transaccion.day,
                'trimestre': (fecha_transaccion.month - 1) // 3 + 1,
                'temporada': get_temporada(fecha_transaccion),
                'es_fin_semana': fecha_transaccion.weekday() >= 5,
                'es_inicio_mes': fecha_transaccion.day <= 7,
                'es_fin_mes': fecha_transaccion.day >= 25,
                
                # Features de producto
                'categoria_id': producto.category_id,
                'precio_base': float(producto.precio_base) if producto.precio_base else 0.0,
                'precio_venta': float(t.precio_unitario),
                
                # Features de ventas (variable objetivo)
                'cantidad_vendida': t.cantidad,
                'monto_total': float(t.cantidad * t.precio_unitario),
                
                # Features de inventario
                'stock_actual': inventario.stock_actual if inventario else 0,
                'dias_desde_ingreso': get_dias_desde_ingreso(inventario, fecha_transaccion),
                'rotacion_inventario': get_rotacion_inventario(inventario, t.cantidad),
                
                # Features de proveedor
                'precio_proveedor_promedio': get_precio_proveedor_promedio(precios_proveedor, fecha_transaccion),
                'margen': 0.0,  # Se calculará después
                'variacion_precio_proveedor': get_variacion_precio_proveedor(precios_proveedor, fecha_transaccion),
                
                # Features históricos (se calcularán después)
                'ventas_7_dias': 0,
                'ventas_30_dias': 0,
                'ventas_90_dias': 0,
                'promedio_ventas_7_dias': 0.0,
                'promedio_ventas_30_dias': 0.0,
                'tendencia_ventas': 0.0,
                'volatilidad_ventas': 0.0,
                
                # Features de precio
                'variacion_precio': 0.0,
                'precio_relativo_categoria': 0.0,
                'elasticidad_precio': 0.0,
                
                # Features de comportamiento
                'frecuencia_compra': 0.0,
                'estacionalidad': 0.0,
                'dias_desde_ultima_venta': 0,
                
                # Features externos
                'mes_alta_demanda': fecha_transaccion.month in [11, 12, 1],  # Navidad y Año Nuevo
                'dia_pago': fecha_transaccion.day in [15, 30, 31],  # Días típicos de pago
            }
            
            data_records.append(record)
        
        # Crear DataFrame
        data = pd.DataFrame(data_records)
        
        if data.empty:
            return data
        
        # Calcular features históricos y derivados
        data = calcular_features_historicos(data)
        data = calcular_features_precio(data)
        data = calcular_features_comportamiento(data)
        
        # Validar y limpiar datos
        validator = DataValidator()
        cleaner = DataCleaner()
        
        # Validar calidad
        validation_issues = validator.validate_data_quality(data, producto_id)
        
        # Limpiar datos si hay problemas
        if any(validation_issues.values()):
            model_logger.logger.info(f"Aplicando limpieza de datos para producto {producto_id}")
            data = cleaner.clean_data(data, producto_id)
        
        model_logger.logger.info(
            f"Datos procesados para producto {producto_id}: {len(data)} registros, {len(data.columns)} features"
        )
        
        return data
        
    except Exception as e:
        model_logger.log_error(e, f"Obtención datos producto {producto_id}")
        raise DatabaseError(f"Error obteniendo datos para producto {producto_id}: {str(e)}")
    
    finally:
        db.close()

def calcular_features_historicos(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula features basados en histórico de ventas usando métodos vectorizados"""
    if data.empty:
        return data
    
    data = data.sort_values('fecha').copy()
    data = data.reset_index(drop=True)
    
    # Asegurar que fecha sea datetime
    data['fecha'] = pd.to_datetime(data['fecha'])
    
    # Calcular features usando rolling windows
    # Esto es más eficiente que loops manuales
    data['ventas_7_dias'] = data['cantidad_vendida'].rolling(window=7, min_periods=1).sum().shift(1).fillna(0)
    data['ventas_30_dias'] = data['cantidad_vendida'].rolling(window=30, min_periods=1).sum().shift(1).fillna(0)
    data['ventas_90_dias'] = data['cantidad_vendida'].rolling(window=90, min_periods=1).sum().shift(1).fillna(0)
    
    # Promedios
    data['promedio_ventas_7_dias'] = data['cantidad_vendida'].rolling(window=7, min_periods=1).mean().shift(1).fillna(0)
    data['promedio_ventas_30_dias'] = data['cantidad_vendida'].rolling(window=30, min_periods=1).mean().shift(1).fillna(0)
    
    # Tendencia (diferencia entre promedios de períodos)
    promedio_15_reciente = data['cantidad_vendida'].rolling(window=15, min_periods=1).mean().shift(1)
    promedio_15_anterior = data['cantidad_vendida'].rolling(window=15, min_periods=1).mean().shift(16)
    
    data['tendencia_ventas'] = ((promedio_15_reciente - promedio_15_anterior) / promedio_15_anterior.where(promedio_15_anterior > 0, 1)).fillna(0)
    
    # Volatilidad
    data['volatilidad_ventas'] = data['cantidad_vendida'].rolling(window=30, min_periods=1).std().shift(1).fillna(0)
    
    # Días desde última venta (simplificado)
    data['dias_desde_ultima_venta'] = data.index.to_series().diff().fillna(1)
    
    return data

def calcular_features_precio(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula features relacionados con precios"""
    if data.empty:
        return data
        
    data = data.copy()
    
    # Calcular margen
    data['margen'] = np.where(
        data['precio_proveedor_promedio'] > 0,
        (data['precio_venta'] - data['precio_proveedor_promedio']) / data['precio_proveedor_promedio'],
        0.0
    )
    
    # Variación de precio respecto al precio base
    data['variacion_precio'] = np.where(
        data['precio_base'] > 0,
        (data['precio_venta'] - data['precio_base']) / data['precio_base'],
        0.0
    )
    
    # Elasticidad precio usando diferencias y shifts
    precio_change = data['precio_venta'].pct_change().fillna(0)
    cantidad_change = data['cantidad_vendida'].pct_change().fillna(0)
    
    data['elasticidad_precio'] = np.where(
        precio_change != 0,
        cantidad_change / precio_change,
        0.0
    )
    
    # Limpiar infinitos y NaN
    data['elasticidad_precio'] = data['elasticidad_precio'].replace([np.inf, -np.inf], 0).fillna(0)
    
    return data

def calcular_features_comportamiento(data: pd.DataFrame) -> pd.DataFrame:
    """Calcula features de comportamiento de compra"""
    if data.empty:
        return data
        
    data = data.copy()
    data['fecha'] = pd.to_datetime(data['fecha'])
    
    # Frecuencia de compra (aproximación usando rolling mean)
    data['frecuencia_compra'] = data['cantidad_vendida'].rolling(window=30, min_periods=1).mean().shift(1).fillna(0)
    
    # Estacionalidad (promedio del mes vs promedio general)
    promedio_general = data['cantidad_vendida'].mean()
    
    if promedio_general > 0:
        estacionalidad_por_mes = data.groupby('mes')['cantidad_vendida'].mean() / promedio_general
        data['estacionalidad'] = data['mes'].map(estacionalidad_por_mes).fillna(1.0)
    else:
        data['estacionalidad'] = 1.0
    
    return data

def _generar_datos_sinteticos(producto_id: int) -> pd.DataFrame:
    """
    Genera datos sintéticos para demo cuando no hay datos reales disponibles.
    """
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generar fechas para los últimos 90 días
    fechas = [datetime.now() - timedelta(days=i) for i in range(90, 0, -1)]
    
    # Generar datos sintéticos con tendencia y ruido
    np.random.seed(producto_id)  # Para consistencia por producto
    
    base_demand = 50 + (producto_id % 10) * 10  # Demanda base variable por producto
    trend = 0.1  # Tendencia ligera al alza
    
    data_records = []
    for i, fecha in enumerate(fechas):
        # Demanda con tendencia + estacionalidad + ruido
        tendencia_valor = base_demand + trend * i
        estacionalidad = 10 * np.sin(2 * np.pi * i / 7)  # Ciclo semanal
        ruido = np.random.normal(0, 5)
        demanda = max(1, int(tendencia_valor + estacionalidad + ruido))
        
        precio_base = 10.0 + np.random.uniform(-1, 1)
        
        # Crear registro sintético con todas las columnas requeridas
        record = {
            'fecha': fecha,
            'demanda': demanda,
            'precio': precio_base,
            'precio_base': precio_base,  # Columna requerida por el modelo
            'stock': max(0, 100 - demanda + np.random.randint(-10, 10)),
            'stock_actual': max(0, 100 - demanda + np.random.randint(-10, 10)),  # Columna requerida
            'categoria_id': 1,
            'proveedor_id': 1,
            'estacionalidad': estacionalidad,
            'dia_semana': fecha.weekday(),
            'mes': fecha.month,
            'demanda_acumulada': demanda * (i + 1) / len(fechas),  # Simulación de acumulada
            'precio_promedio': precio_base,  # Columna adicional que puede ser requerida
            'volumen_ventas': demanda * precio_base,
            'margen': 0.2,  # Margen del 20%
            'costo_unitario': precio_base * 0.8,
            'temporada': 'alta' if fecha.month in [11, 12, 1] else 'baja',  # Estacionalidad
            'promocion': False,  # Sin promociones por defecto
            'competencia': 1.0,  # Factor de competencia neutro
        }
        data_records.append(record)
    
    df = pd.DataFrame(data_records)
    model_logger.logger.info(f"Datos sintéticos generados para producto {producto_id}: {len(df)} registros")
    return df