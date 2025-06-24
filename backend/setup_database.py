import sys
import os
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies for seeding"""
    print("Instalando dependencias necesarias...")
    try:
        # Install faker if not already installed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faker==19.12.0"])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    return True

def run_init_db():
    """Initialize the database"""
    print("\n Inicializando base de datos...")
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.append(str(project_root))
        
        from backend.init_db import init_db
        init_db()
        return True
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def run_seed_data():
    """Seed the database with sample data"""
    print("\n Inyectando datos ficticios...")
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.append(str(project_root))
        
        from backend.seed_data import main as seed_main
        seed_main()
        return True
    except Exception as e:
        print(f"❌ Error inyectando datos: {e}")
        return False

def main():
    """Main setup function"""
    print("CONFIGURACIÓN COMPLETA DE BASE DE DATOS")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Falló la instalación de dependencias")
        return 1
    
    # Step 2: Initialize database
    if not run_init_db():
        print("❌ Falló la inicialización de la base de datos")
        return 1
    
    # Step 3: Seed with sample data
    if not run_seed_data():
        print("❌ Falló la inyección de datos ficticios")
        return 1
    
    print("\n" + "=" * 50)
    print("CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("\n Resumen de lo que se ha configurado:")
    print("   ✅ Dependencias instaladas")
    print("   ✅ Base de datos inicializada")
    print("   ✅ Datos ficticios inyectados")
    print("\n Tu aplicación está lista para usar con datos realistas")

    return 0

if __name__ == "__main__":
    sys.exit(main())