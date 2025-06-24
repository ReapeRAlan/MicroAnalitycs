"""
Módulo para validación de calidad de datos y manejo de datos faltantes
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
from .logger import model_logger

class DataValidator:
    """Validador de calidad de datos"""
    
    def __init__(self):
        self.required_columns = [
            'fecha', 'producto_id', 'cantidad_vendida', 
            'precio_base', 'stock_actual'
        ]
        
    def validate_data_quality(self, data: pd.DataFrame, producto_id: int) -> Dict[str, Any]:
        """
        Valida la calidad de los datos y reporta problemas
        
        Returns:
            Dict con problemas encontrados y data limpia
        """
        issues = {
            'missing_values': {},
            'outliers': {},
            'data_gaps': [],
            'invalid_values': {},
            'warnings': []
        }
        
        # 1. Verificar columnas requeridas
        missing_cols = [col for col in self.required_columns if col not in data.columns]
        if missing_cols:
            issues['missing_columns'] = missing_cols
            model_logger.log_error(
                Exception(f"Columnas faltantes: {missing_cols}"),
                f"Validación producto {producto_id}"
            )
        
        # 2. Verificar valores faltantes
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(data)) * 100
                issues['missing_values'][col] = {
                    'count': missing_count,
                    'percentage': missing_pct
                }
                
                if missing_pct > 20:  # Más del 20% faltante
                    issues['warnings'].append(
                        f"Columna {col} tiene {missing_pct:.1f}% de valores faltantes"
                    )
        
        # 3. Detectar outliers en ventas
        if 'cantidad_vendida' in data.columns:
            outliers = self._detect_outliers(data['cantidad_vendida'])
            if len(outliers) > 0:
                issues['outliers']['cantidad_vendida'] = {
                    'indices': outliers.tolist(),
                    'count': len(outliers)
                }
        
        # 4. Verificar gaps temporales
        if 'fecha' in data.columns:
            gaps = self._detect_date_gaps(data['fecha'])
            issues['data_gaps'] = gaps
        
        # 5. Validar valores lógicos
        issues['invalid_values'] = self._validate_logical_values(data)
        
        # Log de problemas
        if any(issues.values()):
            model_logger.log_data_quality(producto_id, issues)
        
        return issues
    
    def _detect_outliers(self, series: pd.Series) -> np.ndarray:
        """Detecta outliers usando IQR"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return series[(series < lower_bound) | (series > upper_bound)].index.values
    
    def _detect_date_gaps(self, dates: pd.Series) -> List[Dict[str, Any]]:
        """Detecta gaps en fechas"""
        dates_sorted = pd.to_datetime(dates).sort_values()
        gaps = []
        
        for i in range(1, len(dates_sorted)):
            diff = (dates_sorted.iloc[i] - dates_sorted.iloc[i-1]).days
            if diff > 7:  # Gap mayor a una semana
                gaps.append({
                    'start_date': dates_sorted.iloc[i-1].strftime('%Y-%m-%d'),
                    'end_date': dates_sorted.iloc[i].strftime('%Y-%m-%d'),
                    'days_gap': diff
                })
        
        return gaps
    
    def _validate_logical_values(self, data: pd.DataFrame) -> Dict[str, List[int]]:
        """Valida que los valores sean lógicamente correctos"""
        invalid = {}
        
        # Cantidades negativas
        if 'cantidad_vendida' in data.columns:
            negative_sales = data[data['cantidad_vendida'] < 0].index.tolist()
            if negative_sales:
                invalid['negative_sales'] = negative_sales
        
        # Precios negativos
        if 'precio_base' in data.columns:
            negative_prices = data[data['precio_base'] <= 0].index.tolist()
            if negative_prices:
                invalid['negative_prices'] = negative_prices
        
        # Stock negativo
        if 'stock_actual' in data.columns:
            negative_stock = data[data['stock_actual'] < 0].index.tolist()
            if negative_stock:
                invalid['negative_stock'] = negative_stock
        
        return invalid


class DataCleaner:
    """Limpieza y imputación de datos faltantes"""
    
    def __init__(self):
        self.imputation_strategies = {
            'cantidad_vendida': 'median',
            'precio_base': 'forward_fill',
            'stock_actual': 'median',
            'margen': 'mean',
            'ventas_7_dias': 'rolling_mean',
            'ventas_30_dias': 'rolling_mean'
        }
    
    def clean_data(self, data: pd.DataFrame, producto_id: int) -> pd.DataFrame:
        """
        Limpia y procesa los datos faltantes
        """
        cleaned_data = data.copy()
        
        # Ordenar por fecha
        if 'fecha' in cleaned_data.columns:
            cleaned_data = cleaned_data.sort_values('fecha')
        
        # Aplicar estrategias de imputación
        for column, strategy in self.imputation_strategies.items():
            if column in cleaned_data.columns:
                cleaned_data[column] = self._impute_missing_values(
                    cleaned_data[column], strategy
                )
        
        # Remover outliers extremos
        cleaned_data = self._handle_outliers(cleaned_data)
        
        # Validar resultado final
        validator = DataValidator()
        final_issues = validator.validate_data_quality(cleaned_data, producto_id)
        
        if final_issues['warnings']:
            model_logger.logger.warning(
                f"Producto {producto_id} - Advertencias post-limpieza: {final_issues['warnings']}"
            )
        
        return cleaned_data
    
    def _impute_missing_values(self, series: pd.Series, strategy: str) -> pd.Series:
        """Imputa valores faltantes según la estrategia"""
        if strategy == 'median':
            return series.fillna(series.median())
        elif strategy == 'mean':
            return series.fillna(series.mean())
        elif strategy == 'forward_fill':
            return series.fillna(method='ffill').fillna(method='bfill')
        elif strategy == 'rolling_mean':
            return series.fillna(series.rolling(window=7, min_periods=1).mean())
        else:
            return series.fillna(0)
    
    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Maneja outliers extremos"""
        if 'cantidad_vendida' in data.columns:
            # Limitar outliers al percentil 95
            upper_limit = data['cantidad_vendida'].quantile(0.95)
            data.loc[data['cantidad_vendida'] > upper_limit, 'cantidad_vendida'] = upper_limit
        
        return data
