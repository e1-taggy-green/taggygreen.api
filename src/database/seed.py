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
from src.core.enums import VehicleFactorsEnum
from src.models import Base, User, Vehicle, Event, Product, Redemption

# --- Seeding for individual tables ---

def _seed_users(db: Session, faker: Faker) -> list[User]:
    """Generates and saves user records."""
    print("👤 Gerando Usuários (Fixos e Aleatórios)...")
    users = []
    
    # --- Usuários Fixos para Demonstração ---
    demo_b2c = User(name="Carlos Teste", email="teste.b2c@taggy.com", user_type='b2c', points=50000)
    demo_b2b = User(name="Frota Teste S/A (B2B)", email="teste.b2b@taggy.com", user_type='b2b', points=0)
    users.extend([demo_b2c, demo_b2b])
    
    for _ in range(20):
        # Giving users some initial points to allow for redemptions
        user = User(name=faker.name(), email=faker.unique.email(), user_type='b2c', points=random.randint(500, 5000))
        users.append(user)
    db.add_all(users)
    db.commit()
    return users

def _seed_vehicles(db: Session, faker: Faker, users: list[User]) -> list[Vehicle]:
    """Generates and saves vehicle records."""
    print("🚗 Gerando Veículos (Fixos e Aleatórios)...")
    vehicles = []
    vehicle_types = ["car", "truck"]
    
    # --- Veículos Fixos para Demonstração ---
    demo_b2c = next((u for u in users if u.email == "teste.b2c@taggy.com"), None)
    demo_b2b = next((u for u in users if u.email == "teste.b2b@taggy.com"), None)
    
    if demo_b2c:
        vehicles.append(Vehicle(license_plate="B2C-0001", vehicle_type="car", user_id=demo_b2c.id))
    if demo_b2b:
        for i in range(1, 56):
            v_type = "truck" if i % 2 == 0 else "car"
            vehicles.append(Vehicle(license_plate=f"B2B-{1000+i}", vehicle_type=v_type, user_id=demo_b2b.id))

    for _ in range(30):
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

def _seed_events(db: Session, esg_engine: ESGEngine, vehicles: list[Vehicle], faker: Faker):
    """Generates and saves event records in batches."""
    print("🛣️ Gerando Eventos (distribuídos em 6 meses)...")
    
    events_batch = []
    
    def generate_event(vehicle: Vehicle, past_date, occurrences: int = 1) -> Event:
        event_type = random.choice(['toll', 'parking'])
        v_factors = VehicleFactorsEnum[vehicle.vehicle_type.upper()].value
        resultado = esg_engine.calculate_savings(
            vehicle_factors=v_factors,
            vehicles_count=1,
            event_type=event_type,
            occurrences=occurrences
        )
        return Event(
            vehicle_id=vehicle.id,
            event_type=event_type,
            co2_saved=resultado.co2_saved_kg,
            time_saved=resultado.time_saved_min,
            fuel_saved=resultado.fuel_saved_l,
            created_at=past_date
        )

    # 1. 100 Eventos para Demo B2C
    b2c_vehicle = next((v for v in vehicles if v.license_plate == "B2C-0001"), None)
    if b2c_vehicle:
        for _ in range(250):
            date_obj = faker.date_time_between(start_date='-180d', end_date='now')
            events_batch.append(generate_event(b2c_vehicle, date_obj))

    # 2. 30 Eventos para cada veículo da frota Demo B2B
    b2b_vehicles = [v for v in vehicles if v.license_plate.startswith("B2B-")]
    for b2b_v in b2b_vehicles:
        for _ in range(30):
            date_obj = faker.date_time_between(start_date='-180d', end_date='now')
            events_batch.append(generate_event(b2b_v, date_obj))

    # 3. 500 Eventos aleatórios para a massa restante
    other_vehicles = [v for v in vehicles if not v.license_plate.startswith("B2C-") and not v.license_plate.startswith("B2B-")]
    if other_vehicles:
        for _ in range(500):
            # Massa restante gerada com range de 4 meses
            date_obj = faker.date_time_between(start_date='-120d', end_date='now')
            events_batch.append(generate_event(random.choice(other_vehicles), date_obj))

    db.add_all(events_batch)
    db.commit()
    print(f"   -> {len(events_batch)} eventos salvos com sucesso!")

def _seed_redemptions(db: Session, users: list[User], products: list[Product]):
    """Generates and saves product redemption records."""
    print("🔄 Gerando 50 Resgates de Produtos...")
    redemptions = []
    # 1. Resgates para Demo B2C
    demo_b2c = next((u for u in users if u.email == "teste.b2c@taggy.com"), None)
    if demo_b2c:
        # Busca o total de CO2 economizado que gerou saldo real de pontos
        from src.repositories.event_repository import EventRepository
        event_repo = EventRepository(db)
        real_points = event_repo.get_total_co2_saved_by_user(demo_b2c.id)
        
        # Queremos deixar o usuário demo com saldo real livre para testar resgates adicionais
        saldo_restante = real_points
        for _ in range(10):
            product = random.choice(products)
            # Garante que resta saldo suficiente para novos resgates manuais (ex: pelo menos 5.000 pontos)
            if saldo_restante - product.cost_points >= 5000:
                redemptions.append(Redemption(user_id=demo_b2c.id, product_id=product.id))
                saldo_restante -= product.cost_points
                demo_b2c.points -= product.cost_points

    # 2. Resgates aleatórios
    for _ in range(40):
        user = random.choice(users)
        product = random.choice(products)
        
        # Simple logic: assume user has enough points for this simulation
        if user.points >= product.cost_points:
            redemptions.append(Redemption(
                user_id=user.id,
                product_id=product.id
            ))
            user.points -= product.cost_points # Update user points
    
    db.add_all(redemptions)
    db.commit()

# --- Main Seeder Runner ---

def run_seeder():
    """Main function to coordinate the database seeding process."""
    print(f"🌱 Iniciando Seeding TaggyGreen (Escala de Demonstração)...")
    
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
        _seed_events(db, esg_engine, vehicles, faker)
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
