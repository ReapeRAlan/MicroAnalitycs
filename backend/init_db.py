import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.base import Base, engine
from backend.models import *

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos creada correctamente.")

if __name__ == "__main__":
    init_db()
