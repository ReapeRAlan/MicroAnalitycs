import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
from faker import Faker
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.base import Base, get_db
from backend.models import (
    Business, User, Category, Product, Inventory, 
    Transaction, TransactionDetail, Supplier, SupplierPrice, 
    Prediction, ChatLog
)

# Initialize Faker
fake = Faker('es_ES')  # Spanish locale for more realistic data
Faker.seed(42)  # For reproducible data
random.seed(42)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

def clear_data(session):
    """Clear all existing data"""
    # Delete in reverse order of dependencies
    session.query(ChatLog).delete()
    session.query(Prediction).delete()
    session.query(SupplierPrice).delete()
    session.query(TransactionDetail).delete()
    session.query(Transaction).delete()
    session.query(Inventory).delete()
    session.query(Product).delete()
    session.query(Category).delete()
    session.query(Supplier).delete()
    session.query(User).delete()
    session.query(Business).delete()
    session.commit()
    print("🗑️ Datos existentes eliminados")

def seed_businesses(session):
    """Create sample businesses"""
    businesses_data = [
        {
            "nombre": "TechnoMart",
            "descripcion": "Tienda especializada en tecnología y electrónicos"
        },
        {
            "nombre": "FreshMarket",
            "descripcion": "Supermercado de productos frescos y orgánicos"
        },
        {
            "nombre": "StyleHub",
            "descripcion": "Boutique de moda y accesorios"
        },
        {
            "nombre": "HomeDecor Plus",
            "descripcion": "Artículos para el hogar y decoración"
        },
        {
            "nombre": "SportZone",
            "descripcion": "Equipamiento deportivo y fitness"
        }
    ]
    
    businesses = []
    for data in businesses_data:
        business = Business(
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            fecha_registro=fake.date_time_between(start_date='-2y', end_date='now')
        )
        businesses.append(business)
        session.add(business)
    
    session.commit()
    print(f"🏢 {len(businesses)} negocios creados")
    return businesses

def seed_users(session, businesses):
    """Create sample users"""
    roles = ['admin', 'manager', 'employee', 'analyst']
    users = []
    
    for business in businesses:
        # Create 3-5 users per business
        num_users = random.randint(3, 5)
        for _ in range(num_users):
            user = User(
                business_id=business.id,
                nombre=fake.name(),
                correo=fake.unique.email(),
                contrasena=fake.password(length=12),
                rol=random.choice(roles),
                fecha_creacion=fake.date_time_between(start_date=business.fecha_registro, end_date='now')
            )
            users.append(user)
            session.add(user)
    
    session.commit()
    print(f"👥 {len(users)} usuarios creados")
    return users

def seed_categories(session):
    """Create product categories"""
    categories_data = [
        {"nombre": "Electrónicos", "descripcion": "Dispositivos electrónicos y gadgets"},
        {"nombre": "Ropa", "descripcion": "Vestimenta y accesorios de moda"},
        {"nombre": "Hogar", "descripcion": "Artículos para el hogar y decoración"},
        {"nombre": "Deportes", "descripcion": "Equipamiento deportivo y fitness"},
        {"nombre": "Alimentación", "descripcion": "Productos alimenticios y bebidas"},
        {"nombre": "Libros", "descripcion": "Libros y material educativo"},
        {"nombre": "Juguetes", "descripcion": "Juguetes y entretenimiento infantil"},
        {"nombre": "Belleza", "descripcion": "Productos de belleza y cuidado personal"},
        {"nombre": "Automóvil", "descripcion": "Accesorios y repuestos para vehículos"},
        {"nombre": "Jardinería", "descripcion": "Herramientas y productos para jardín"}
    ]
    
    categories = []
    for data in categories_data:
        category = Category(
            nombre=data["nombre"],
            descripcion=data["descripcion"]
        )
        categories.append(category)
        session.add(category)
    
    session.commit()
    print(f"📂 {len(categories)} categorías creadas")
    return categories

def seed_suppliers(session):
    """Create suppliers"""
    suppliers_data = [
        {"nombre": "TechSupply Co.", "contacto": "tech@techsupply.com | +34 912 345 678"},
        {"nombre": "Global Electronics", "contacto": "ventas@globalelectronics.es | +34 913 456 789"},
        {"nombre": "Fashion Wholesale", "contacto": "info@fashionwholesale.com | +34 914 567 890"},
        {"nombre": "Home & Garden Supply", "contacto": "pedidos@homegardens.es | +34 915 678 901"},
        {"nombre": "Sports Equipment Ltd", "contacto": "sports@equipment.com | +34 916 789 012"},
        {"nombre": "Fresh Foods Distributor", "contacto": "fresh@foods.es | +34 917 890 123"},
        {"nombre": "Beauty Products Inc", "contacto": "beauty@products.com | +34 918 901 234"},
        {"nombre": "Auto Parts Spain", "contacto": "auto@parts.es | +34 919 012 345"}
    ]
    
    suppliers = []
    for data in suppliers_data:
        supplier = Supplier(
            nombre=data["nombre"],
            contacto=data["contacto"]
        )
        suppliers.append(supplier)
        session.add(supplier)
    
    session.commit()
    print(f"🚚 {len(suppliers)} proveedores creados")
    return suppliers

def seed_products(session, businesses, categories):
    """Create products for each business"""
    products_templates = {
        "Electrónicos": [
            "Smartphone Samsung Galaxy", "iPhone 14", "Laptop Dell Inspiron", "Tablet iPad",
            "Auriculares Bluetooth", "Smart TV 55\"", "Cámara Canon EOS", "Consola PlayStation 5",
            "Smartwatch Apple", "Altavoz Bluetooth", "Teclado Mecánico", "Mouse Gaming"
        ],
        "Ropa": [
            "Camiseta Básica", "Jeans Slim Fit", "Vestido Casual", "Chaqueta de Cuero",
            "Zapatillas Deportivas", "Camisa Formal", "Falda Midi", "Abrigo de Invierno",
            "Pantalón Chino", "Blusa Elegante", "Sudadera con Capucha", "Zapatos Oxford"
        ],
        "Hogar": [
            "Sofá 3 Plazas", "Mesa de Comedor", "Lámpara de Pie", "Alfombra Persa",
            "Cojines Decorativos", "Espejo de Pared", "Estantería de Madera", "Cortinas Blackout",
            "Jarrón Cerámico", "Cuadro Abstracto", "Reloj de Pared", "Maceta Grande"
        ],
        "Deportes": [
            "Bicicleta de Montaña", "Pesas Ajustables", "Cinta de Correr", "Balón de Fútbol",
            "Raqueta de Tenis", "Yoga Mat", "Mancuernas 5kg", "Casco de Ciclismo",
            "Guantes de Boxeo", "Pelota de Básquet", "Banda Elástica", "Botella Deportiva"
        ],
        "Alimentación": [
            "Aceite de Oliva Extra", "Pasta Italiana", "Arroz Basmati", "Café Premium",
            "Miel Orgánica", "Chocolate Negro 70%", "Té Verde", "Quinoa Orgánica",
            "Almendras Naturales", "Vino Tinto Reserva", "Queso Manchego", "Jamón Ibérico"
        ]
    }
    
    products = []
    for business in businesses:
        # Each business gets 15-25 products
        num_products = random.randint(15, 25)
        
        for _ in range(num_products):
            category = random.choice(categories)
            category_products = products_templates.get(category.nombre, ["Producto Genérico"])
            
            product_name = random.choice(category_products)
            # Add variation to avoid duplicates
            if random.random() > 0.7:
                product_name += f" {fake.word().title()}"
            
            product = Product(
                business_id=business.id,
                category_id=category.id,
                nombre=product_name,
                descripcion=fake.text(max_nb_chars=200),
                precio_base=Decimal(str(round(random.uniform(10.0, 500.0), 2)))
            )
            products.append(product)
            session.add(product)
    
    session.commit()
    print(f"📦 {len(products)} productos creados")
    return products

def seed_inventory(session, products):
    """Create inventory for all products"""
    inventories = []
    for product in products:
        inventory = Inventory(
            product_id=product.id,
            stock_actual=random.randint(0, 100),
            ultimo_ingreso=fake.date_time_between(start_date='-30d', end_date='now')
        )
        inventories.append(inventory)
        session.add(inventory)
    
    session.commit()
    print(f"📊 {len(inventories)} registros de inventario creados")
    return inventories

def seed_supplier_prices(session, products, suppliers):
    """Create supplier prices for products"""
    supplier_prices = []
    
    for product in products:
        # Each product has 1-3 supplier prices
        num_suppliers = random.randint(1, min(3, len(suppliers)))
        selected_suppliers = random.sample(suppliers, num_suppliers)
        
        for supplier in selected_suppliers:
            # Supplier price is usually 60-80% of base price
            supplier_price = float(product.precio_base) * random.uniform(0.6, 0.8)
            
            price_record = SupplierPrice(
                product_id=product.id,
                supplier_id=supplier.id,
                precio=Decimal(str(round(supplier_price, 2))),
                fecha=fake.date_time_between(start_date='-60d', end_date='now')
            )
            supplier_prices.append(price_record)
            session.add(price_record)
    
    session.commit()
    print(f"💰 {len(supplier_prices)} precios de proveedores creados")
    return supplier_prices

def seed_transactions(session, businesses, products):
    """Create transactions and transaction details"""
    transactions = []
    transaction_details = []
    
    for business in businesses:
        business_products = [p for p in products if p.business_id == business.id]
        if not business_products:
            continue
            
        # Create 20-40 transactions per business
        num_transactions = random.randint(20, 40)
        
        for _ in range(num_transactions):
            transaction_date = fake.date_time_between(start_date='-90d', end_date='now')
            
            transaction = Transaction(
                business_id=business.id,
                fecha=transaction_date,
                total=Decimal('0.00')  # Will be calculated from details
            )
            session.add(transaction)
            session.flush()  # Get the ID
            
            # Create 1-5 transaction details per transaction
            num_details = random.randint(1, 5)
            transaction_total = Decimal('0.00')
            
            for _ in range(num_details):
                product = random.choice(business_products)
                cantidad = random.randint(1, 10)
                # Price variation ±10% from base price
                precio_unitario = float(product.precio_base) * random.uniform(0.9, 1.1)
                precio_unitario = Decimal(str(round(precio_unitario, 2)))
                
                detail = TransactionDetail(
                    transaction_id=transaction.id,
                    product_id=product.id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                transaction_details.append(detail)
                session.add(detail)
                
                transaction_total += precio_unitario * cantidad
            
            transaction.total = transaction_total
            transactions.append(transaction)
    
    session.commit()
    print(f"🛒 {len(transactions)} transacciones y {len(transaction_details)} detalles creados")
    return transactions, transaction_details

def seed_predictions(session, products):
    """Create ML predictions for products"""
    models = ['linear_regression', 'random_forest', 'neural_network', 'arima']
    predictions = []
    
    for product in products:
        # Create 2-4 predictions per product with different models
        num_predictions = random.randint(2, 4)
        selected_models = random.sample(models, num_predictions)
        
        for model in selected_models:
            # Prediction result around ±20% of base price
            base_price = float(product.precio_base)
            prediction_result = base_price * random.uniform(0.8, 1.2)
            
            prediction = Prediction(
                product_id=product.id,
                modelo=model,
                resultado=Decimal(str(round(prediction_result, 2))),
                fecha=fake.date_time_between(start_date='-30d', end_date='now')
            )
            predictions.append(prediction)
            session.add(prediction)
    
    session.commit()
    print(f"🔮 {len(predictions)} predicciones creadas")
    return predictions

def seed_chat_logs(session, users):
    """Create chat logs for users"""
    sample_messages = [
        "¿Cuál es el producto más vendido?",
        "Muéstrame las ventas del último mes",
        "¿Qué productos necesitan restock?",
        "Analiza las tendencias de ventas",
        "¿Cuál es el margen de ganancia promedio?",
        "Genera un reporte de inventario",
        "¿Qué proveedores ofrecen mejores precios?",
        "Predice las ventas para el próximo trimestre",
        "¿Cuáles son los productos más rentables?",
        "Muestra el análisis de la competencia"
    ]
    
    sample_responses = [
        "Basándome en los datos, el producto más vendido es...",
        "Aquí tienes el análisis de ventas del último mes...",
        "Los siguientes productos necesitan reabastecimiento...",
        "He analizado las tendencias y encontré que...",
        "El margen de ganancia promedio es del 35%...",
        "He generado el reporte de inventario solicitado...",
        "Según el análisis de precios, los mejores proveedores son...",
        "La predicción para el próximo trimestre indica...",
        "Los productos más rentables según el análisis son...",
        "El análisis de competencia muestra que..."
    ]
    
    chat_logs = []
    
    for user in users:
        # Create 5-15 chat logs per user
        num_chats = random.randint(5, 15)
        
        for _ in range(num_chats):
            chat_log = ChatLog(
                user_id=user.id,
                mensaje=random.choice(sample_messages),
                respuesta=random.choice(sample_responses)
            )
            chat_logs.append(chat_log)
            session.add(chat_log)
    
    session.commit()
    print(f"💬 {len(chat_logs)} logs de chat creados")
    return chat_logs

def main():
    """Main function to seed the database"""
    print("🚀 Iniciando proceso de inyección de datos...")
    
    # Create tables
    create_tables()
    
    # Create session
    session = SessionLocal()
    
    try:
        # Clear existing data
        clear_data(session)
        
        # Seed data in order of dependencies
        print("\n📊 Creando datos ficticios...")
        
        businesses = seed_businesses(session)
        users = seed_users(session, businesses)
        categories = seed_categories(session)
        suppliers = seed_suppliers(session)
        products = seed_products(session, businesses, categories)
        inventories = seed_inventory(session, products)
        supplier_prices = seed_supplier_prices(session, products, suppliers)
        transactions, transaction_details = seed_transactions(session, businesses, products)
        predictions = seed_predictions(session, products)
        chat_logs = seed_chat_logs(session, users)
        
        print("\n✅ ¡Datos ficticios creados exitosamente!")
        print("\n📈 Resumen:")
        print(f"   • {len(businesses)} negocios")
        print(f"   • {len(users)} usuarios")
        print(f"   • {len(categories)} categorías")
        print(f"   • {len(suppliers)} proveedores")
        print(f"   • {len(products)} productos")
        print(f"   • {len(inventories)} registros de inventario")
        print(f"   • {len(supplier_prices)} precios de proveedores")
        print(f"   • {len(transactions)} transacciones")
        print(f"   • {len(transaction_details)} detalles de transacciones")
        print(f"   • {len(predictions)} predicciones")
        print(f"   • {len(chat_logs)} logs de chat")
        
        print("\n🎉 ¡La base de datos está lista para usar!")
        
    except Exception as e:
        print(f"❌ Error durante la inyección de datos: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()