import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Garante que a raiz do projeto esteja no PYTHONPATH para importar os serviços
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.database.session import engine, SessionLocal
from src.services.esg_engine import ESGEngine
from src.schemas.esg import VehicleFactorsEnum
from src.models import Base, User, Vehicle, Event, Product, Redemption

# --- Seeding for individual tables ---

def _seed_users(db: Session, faker: Faker) -> list[User]:
    """Generates and saves user records."""
    print("👤 Gerando 20 Usuários B2C...")
    users = []
    for _ in range(20):
        # Giving users some initial points to allow for redemptions
        user = User(name=faker.name(), email=faker.unique.email(), user_type='b2c', points=random.randint(500, 5000))
        users.append(user)
    db.add_all(users)
    db.commit()
    return users

def _seed_vehicles(db: Session, faker: Faker, users: list[User]) -> list[Vehicle]:
    """Generates and saves vehicle records."""
    print("🚗 Gerando 500 Veículos...")
    vehicles = []
    vehicle_types = ["car", "truck"]
    for _ in range(500):
        vehicle = Vehicle(
            license_plate=faker.license_plate(),
            vehicle_type=random.choice(vehicle_types),
            user_id=random.choice(users).id
        )
        vehicles.append(vehicle)
    db.add_all(vehicles)
    db.commit()
    return vehicles

def _seed_products(db: Session) -> list[Product]:
    """Generates and saves product records for the marketplace."""
    print("🛍️ Gerando Produtos no Marketplace...")
    products = [
        Product(name="Voucher iFood R$25", cost_points=2500),
        Product(name="Crédito Uber R$10", cost_points=1200),
        Product(name="Ingresso Cinemark", cost_points=1800),
        Product(name="Doação para Projeto de Reflorestamento", cost_points=1000),
        Product(name="1 Mês de Spotify Premium", cost_points=2200),
        Product(name="Desconto de 10% em Postos Shell", cost_points=800),
        Product(name="Lavagem Ecológica de Veículo", cost_points=3500),
        Product(name="Crédito de Celular R$15", cost_points=1500),
        Product(name="Assinatura de E-book sobre Sustentabilidade", cost_points=500),
        Product(name="Kit de Canudos de Inox", cost_points=750),
    ]
    db.add_all(products)
    db.commit()
    return products

def _seed_events(db: Session, esg_engine: ESGEngine, vehicles: list[Vehicle], total_events: int, batch_size: int):
    """Generates and saves event records in batches."""
    print(f"🛣️ Gerando {total_events} Eventos no histórico...")
    
    events_batch = []
    for i in range(1, total_events + 1):
        vehicle = random.choice(vehicles)
        event_type = random.choice(['toll', 'parking'])
        
        v_factors = VehicleFactorsEnum[vehicle.vehicle_type.upper()].value
        
        resultado = esg_engine.calculate_savings(
            vehicle_factors=v_factors,
            vehicles_count=1,
            event_type=event_type,
            occurrences=1
        )
        
        events_batch.append(Event(
            vehicle_id=vehicle.id,
            event_type=event_type,
            co2_saved=resultado.co2_saved_kg,
            time_saved=resultado.time_saved_min,
            fuel_saved=resultado.fuel_saved_l
        ))

        if i % batch_size == 0 or i == total_events:
            db.bulk_save_objects(events_batch)
            db.commit()
            print(f"   -> Lote salvo: {i}/{total_events} eventos...")
            events_batch.clear()

def _seed_redemptions(db: Session, users: list[User], products: list[Product]):
    """Generates and saves product redemption records."""
    print("🔄 Gerando 50 Resgates de Produtos...")
    redemptions = []
    for _ in range(50):
        user = random.choice(users)
        product = random.choice(products)
        
        # Simple logic: assume user has enough points for this simulation
        if user.points >= product.cost_points:
            redemption = Redemption(
                user_id=user.id,
                product_id=product.id
            )
            redemptions.append(redemption)
            user.points -= product.cost_points # Update user points
    
    db.add_all(redemptions)
    db.commit()

# --- Main Seeder Runner ---

def run_seeder(total_events: int = 10000, batch_size: int = 2000):
    """Main function to coordinate the database seeding process."""
    print(f"🌱 Iniciando Seeding TaggyGreen...")
    
    # Corrected DB connection
    print("🔥 Apagando e recriando o banco de dados...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    faker = Faker('pt_BR')
    esg_engine = ESGEngine()

    try:
        users = _seed_users(db, faker)
        vehicles = _seed_vehicles(db, faker, users)
        products = _seed_products(db)
        _seed_events(db, esg_engine, vehicles, total_events, batch_size)
        _seed_redemptions(db, users, products)

        print("\n✅ Seeding finalizado com Sucesso!")
    except Exception as e:
        print(f"❌ Erro durante o seeding: {e}")
        db.rollback()
    finally:
        print("🔒 Fechando conexão com o banco.")
        db.close()

if __name__ == "__main__":
    run_seeder()
