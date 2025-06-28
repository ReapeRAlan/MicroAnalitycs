#!/bin/bash

# Script de configuración y ejecución del sistema MicroAnalytics
# ================================================================

set -e  # Salir si hay algún error

echo "🚀 Iniciando MicroAnalytics - Sistema de Predicción de Demanda"
echo "=============================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar dependencias
check_dependencies() {
    print_info "Verificando dependencias..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 no está instalado"
        exit 1
    fi
    print_success "Python3 encontrado"
    
    # Pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 no está instalado"
        exit 1
    fi
    print_success "pip3 encontrado"
    
    # Node.js (opcional para ngrok)
    if command -v node &> /dev/null; then
        print_success "Node.js encontrado"
    else
        print_warning "Node.js no encontrado (opcional para ngrok)"
    fi
}

# Configurar entorno Python
setup_python_env() {
    print_info "Configurando entorno Python..."
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        print_info "Creando entorno virtual..."
        python3 -m venv venv
        print_success "Entorno virtual creado"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    print_success "Entorno virtual activado"
    
    # Instalar dependencias
    print_info "Instalando dependencias..."
    pip install -r requirements.txt
    
    # Instalar dependencias adicionales para el frontend
    pip install streamlit plotly
    
    print_success "Dependencias instaladas"
}

# Configurar base de datos
setup_database() {
    print_info "Configurando base de datos..."
    
    # Ejecutar script de configuración de DB
    cd backend
    python setup_database.py
    
    # Inicializar con datos de ejemplo
    python seed_data.py
    
    cd ..
    print_success "Base de datos configurada"
}

# Función para iniciar el backend
start_backend() {
    print_info "Iniciando backend FastAPI..."
    
    cd backend
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    cd ..
    
    # Esperar a que el backend esté listo
    print_info "Esperando a que el backend esté listo..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/predict/health > /dev/null 2>&1; then
            print_success "Backend iniciado en http://localhost:8000"
            return 0
        fi
        sleep 1
    done
    
    print_error "El backend no pudo iniciarse correctamente"
    return 1
}

# Función para iniciar el frontend
start_frontend() {
    print_info "Iniciando frontend Streamlit..."
    
    cd frontend
    streamlit run chatbot_app.py --server.port 8501 --server.address 0.0.0.0 &
    FRONTEND_PID=$!
    
    cd ..
    
    # Esperar un poco para que Streamlit inicie
    sleep 3
    print_success "Frontend iniciado en http://localhost:8501"
}

# Función para mostrar instrucciones de Ollama
show_ollama_instructions() {
    echo ""
    print_info "Configuración de Ollama"
    echo "======================="
    echo ""
    echo "Para usar la funcionalidad de IA, necesitas configurar Ollama:"
    echo ""
    echo "📋 OPCIÓN 1: Ejecución Local"
    echo "   1. Instala Ollama: https://ollama.ai/"
    echo "   2. Ejecuta: ollama run llama2"
    echo "   3. El servicio estará en http://localhost:11434"
    echo ""
    echo "📋 OPCIÓN 2: Google Colab + ngrok (Recomendado)"
    echo "   1. Abre el notebook de Colab:"
    echo "      https://colab.research.google.com/github/ollama/ollama/blob/main/examples/jupyter/ollama.ipynb"
    echo "   2. Ejecuta las celdas para instalar Ollama"
    echo "   3. Instala ngrok en Colab:"
    echo "      !pip install pyngrok"
    echo "      from pyngrok import ngrok"
    echo "      ngrok.set_auth_token('TU_TOKEN_NGROK')"
    echo "      public_url = ngrok.connect(11434)"
    echo "      print(public_url)"
    echo "   4. Copia la URL pública y úsala en la configuración del frontend"
    echo ""
    echo "🔧 Configuración en el Frontend:"
    echo "   - Abre http://localhost:8501"
    echo "   - En la barra lateral, pega la URL de Ollama"
    echo "   - Selecciona el modelo (llama2 recomendado)"
    echo "   - Haz clic en 'Probar Conexión'"
    echo ""
}

# Función para mostrar estadísticas del sistema
show_system_status() {
    echo ""
    print_info "Estado del Sistema"
    echo "=================="
    echo ""
    
    # Backend
    if curl -s http://localhost:8000/api/predict/health > /dev/null 2>&1; then
        print_success "Backend: Funcionando ✓"
        echo "   📍 URL: http://localhost:8000"
        echo "   📊 API Docs: http://localhost:8000/docs"
    else
        print_error "Backend: No disponible ✗"
    fi
    
    # Frontend
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_success "Frontend: Funcionando ✓"
        echo "   📍 URL: http://localhost:8501"
    else
        print_error "Frontend: No disponible ✗"
    fi
    
    # Base de datos
    if [ -f "backend/microanalytics.db" ]; then
        print_success "Base de datos: Configurada ✓"
        DB_SIZE=$(du -h backend/microanalytics.db | cut -f1)
        echo "   📦 Tamaño: $DB_SIZE"
    else
        print_error "Base de datos: No encontrada ✗"
    fi
    
    echo ""
}

# Función para limpiar procesos
cleanup() {
    print_info "Cerrando servicios..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "Backend cerrado"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend cerrado"
    fi
    
    # Matar cualquier proceso de uvicorn o streamlit que pueda estar corriendo
    pkill -f "uvicorn app:app" 2>/dev/null || true
    pkill -f "streamlit run" 2>/dev/null || true
    
    print_success "Limpieza completada"
}

# Manejar señales de interrupción
trap cleanup EXIT INT TERM

# Función principal
main() {
    case "${1:-start}" in
        "start")
            check_dependencies
            setup_python_env
            
            # Configurar DB solo si no existe
            if [ ! -f "backend/microanalytics.db" ]; then
                setup_database
            else
                print_success "Base de datos ya existe"
            fi
            
            start_backend
            start_frontend
            show_ollama_instructions
            show_system_status
            
            print_success "Sistema iniciado completamente"
            echo ""
            print_info "Presiona Ctrl+C para detener todos los servicios"
            
            # Mantener el script corriendo
            wait
            ;;
            
        "stop")
            cleanup
            ;;
            
        "status")
            show_system_status
            ;;
            
        "setup")
            check_dependencies
            setup_python_env
            setup_database
            print_success "Configuración completada"
            ;;
            
        "reset-db")
            print_warning "Recreando base de datos..."
            rm -f backend/microanalytics.db
            setup_database
            print_success "Base de datos recreada"
            ;;
            
        "test")
            print_info "Ejecutando tests..."
            source venv/bin/activate
            python -m pytest tests/ -v
            ;;
            
        "help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  start     - Iniciar todos los servicios (por defecto)"
            echo "  stop      - Detener todos los servicios"
            echo "  status    - Mostrar estado del sistema"
            echo "  setup     - Solo configurar el entorno"
            echo "  reset-db  - Recrear la base de datos"
            echo "  test      - Ejecutar tests"
            echo "  help      - Mostrar esta ayuda"
            echo ""
            echo "Ejemplos:"
            echo "  $0                # Iniciar todo"
            echo "  $0 start          # Iniciar todo"
            echo "  $0 stop           # Detener servicios"
            echo "  $0 status         # Ver estado"
            ;;
            
        *)
            print_error "Comando desconocido: $1"
            print_info "Usa '$0 help' para ver comandos disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
