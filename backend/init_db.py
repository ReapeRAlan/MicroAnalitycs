import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.base import Base, engine
from backend.models import *

def init_db():
    """Initialize the database by creating all tables"""
    try:
        print("Inicializando base de datos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos creada correctamente.")
        print("Tablas creadas:")
        for table_name in Base.metadata.tables.keys():
            print(f"   • {table_name}")
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        raise

def drop_all_tables():
    """Drop all tables (useful for development)"""
    try:
        print("Eliminando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        print("✅ Todas las tablas eliminadas.")
    except Exception as e:
        print(f"❌ Error al eliminar las tablas: {e}")
        raise

def reset_db():
    """Reset the database by dropping and recreating all tables"""
    print("Reiniciando base de datos...")
    drop_all_tables()
    init_db()
    print("✅ Base de datos reiniciada correctamente.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestión de base de datos')
    parser.add_argument('--reset', action='store_true', help='Reiniciar la base de datos (eliminar y recrear todas las tablas)')
    parser.add_argument('--drop', action='store_true', help='Eliminar todas las tablas')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_db()
    elif args.drop:
        drop_all_tables()
    else:
        init_db()
