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

# Janela usada pelo gráfico de rastro-histórico do B2C
# (B2CService.MONTHS_WINDOW / getUserRastroHistorico): mês corrente + 3 anteriores.
MESES_JANELA = 4

# --- Helpers de distribuição temporal ---

def _gerar_datas_distribuidas_4_meses(total_eventos: int) -> list[datetime]:
    """
    Distribui `total_eventos` IGUALMENTE entre os últimos 4 meses
    (mês corrente + 3 anteriores) e devolve uma lista de datetimes aleatórios.

    É esse ingrediente que faz o gráfico de rastro-histórico do B2C
    (getUserRastroHistorico -> EventRepository.get_monthly_savings_by_user, que
    agrupa por mês dentro de uma janela de 4 meses) aparecer com dados em TODOS
    os meses. Sem a distribuição os eventos se concentram em poucos meses e o
    gráfico fica com "buracos".

    Regras:
      - Cada mês recebe ~ total_eventos / 4 eventos. O resto da divisão é
        distribuído nos primeiros meses da janela para somar exatamente
        `total_eventos`.
      - As datas de cada mês caem entre o 1º dia (00:00:00) e o último instante
        do mês (23:59:59).
      - No mês corrente nunca geramos datas no futuro: o limite superior é
        datetime.now().
    """
    hoje = datetime.now()
    datas: list[datetime] = []

    # Índice absoluto do mês atual ("meses desde o ano 0"), mesmo cálculo usado
    # em B2CService._calcular_data_corte para delimitar a janela de 4 meses.
    indice_mes_atual = hoje.year * 12 + (hoje.month - 1)
    indice_mes_inicial = indice_mes_atual - (MESES_JANELA - 1)  # 3 meses antes do atual

    por_mes = total_eventos // MESES_JANELA
    resto = total_eventos % MESES_JANELA

    for i in range(MESES_JANELA):
        indice = indice_mes_inicial + i
        ano = indice // 12
        mes = indice % 12 + 1

        inicio = datetime(ano, mes, 1)  # 1º dia do mês às 00:00:00

        if ano == hoje.year and mes == hoje.month:
            # Mês corrente: não ultrapassa o "agora" (evita datas no futuro).
            fim = hoje
        else:
            # Último instante do mês = 1º dia do mês seguinte - 1 segundo.
            indice_prox = indice + 1
            fim = datetime(indice_prox // 12, indice_prox % 12 + 1, 1) - timedelta(seconds=1)

        # Distribui o resto da divisão nos primeiros meses da janela.
        qtd_mes = por_mes + (1 if i < resto else 0)

        intervalo_segundos = max(int((fim - inicio).total_seconds()), 0)
        for _ in range(qtd_mes):
            offset = random.randint(0, intervalo_segundos)
            datas.append(inicio + timedelta(seconds=offset))

    return datas

# --- Seeding for individual tables ---

def _seed_users(db: Session, faker: Faker) -> list[User]:
    """Generates and saves user records."""
    print("👤 Gerando Usuários (Fixos e Aleatórios)...")
    users = []

    # --- Usuários Fixos para Demonstração ---
    demo_b2c = User(name="Carlos Teste (B2C)", email="teste.b2c@taggy.com", user_type='b2c', points=50000)
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

def _seed_events(db: Session, esg_engine: ESGEngine, vehicles: list[Vehicle], faker: Faker) -> float:
    """
    Generates and saves event records in batches.

    Retorna o total de CO2 (kg) acumulado pelo veículo do B2C demo, que é
    exatamente o "saldo base" do Marketplace, já que
    saldo_real = SUM(Event.co2_saved do user) - SUM(custo dos resgates).
    """
    print("🛣️ Gerando Eventos (distribuídos nos últimos 4 meses)...")

    events_batch = []

    def gerar_evento(vehicle: Vehicle, data: datetime, occurrences: int) -> Event:
        # O event_type define o tempo-base perdido na guarita (2 min toll / 3 min
        # parking) e `occurrences` multiplica a economia. Toda a matemática de
        # CO2/combustível/tempo vem do ESGEngine — nada é inventado manualmente.
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
            created_at=data
        )

    # --- 1. Eventos do B2C demo (B2C-0001, car) ---
    # Matemática do CO2 médio por evento de CARRO
    # (fatores: emission 2.30 kg/l, idle 0.02 l/min, accel/brake 0.05 l):
    #   - toll    (2 min): ((0.02*2) + 0.05) * 2.30 = 0.207 kg / ocorrência
    #   - parking (3 min): ((0.02*3) + 0.05) * 2.30 = 0.253 kg / ocorrência
    #   - média entre os dois tipos               ≈ 0.230 kg / ocorrência
    # Com occurrences = random(1..5) (média 3), cada EVENTO rende ~0.69 kg.
    # Para superar com folga os 5000 kg exigidos pelo Marketplace, geramos 7500
    # eventos (~7500 * 0.69 ≈ 5175 kg de CO2 acumulado).
    NUM_EVENTOS_B2C = 7500
    co2_total_b2c = 0.0
    b2c_vehicle = next((v for v in vehicles if v.license_plate == "B2C-0001"), None)
    if b2c_vehicle:
        for data in _gerar_datas_distribuidas_4_meses(NUM_EVENTOS_B2C):
            evento = gerar_evento(b2c_vehicle, data, occurrences=random.randint(1, 5))
            co2_total_b2c += evento.co2_saved
            events_batch.append(evento)

    # --- 2. Frota B2B demo: 55 veículos x 30 eventos ---
    # Cada veículo recebe suas 30 passagens distribuídas nos mesmos 4 meses, para
    # manter histórico mensal consistente também nos dashboards B2B.
    b2b_vehicles = [v for v in vehicles if v.license_plate.startswith("B2B-")]
    for b2b_v in b2b_vehicles:
        for data in _gerar_datas_distribuidas_4_meses(30):
            events_batch.append(gerar_evento(b2b_v, data, occurrences=1))

    # --- 3. Eventos aleatórios para a massa restante (usuários não testados no front) ---
    other_vehicles = [v for v in vehicles if not v.license_plate.startswith("B2C-") and not v.license_plate.startswith("B2B-")]
    if other_vehicles:
        for _ in range(500):
            date_obj = faker.date_time_between(start_date='-6m', end_date='now')
            events_batch.append(gerar_evento(random.choice(other_vehicles), date_obj, occurrences=1))

    # bulk_save_objects: inserção massiva e performática (~9.6k eventos).
    db.bulk_save_objects(events_batch)
    db.commit()
    print(f"   -> {len(events_batch)} eventos salvos com sucesso!")
    print(f"   -> CO2 acumulado pelo B2C demo: {co2_total_b2c:.2f} kg (saldo base do Marketplace)")
    return round(co2_total_b2c, 4)

def _seed_redemptions(db: Session, users: list[User], products: list[Product]):
    """
    Generates and saves product redemption records.

    IMPORTANTE: o B2C demo (teste.b2c@taggy.com) NÃO recebe nenhum resgate aqui.
    O front precisa testar o PRIMEIRO resgate com o saldo cheio e, como
    saldo_real = SUM(eventos) - SUM(custo dos resgates), qualquer resgate criado
    no seed reduziria esse saldo e contaminaria o teste do Marketplace.
    """
    print("🔄 Gerando Resgates de Produtos (exceto B2C demo)...")
    redemptions = []

    # Candidatos = todos menos o B2C demo, para preservar seu saldo_real intacto.
    candidatos = [u for u in users if u.email != "teste.b2c@taggy.com"]

    # Resgates aleatórios usando User.points como proxy de saldo. Esses usuários
    # não passam pela validação real do Marketplace no front, então o proxy basta.
    for _ in range(40):
        user = random.choice(candidatos)
        product = random.choice(products)
        if user.points >= product.cost_points:
            redemptions.append(Redemption(
                user_id=user.id,
                product_id=product.id
            ))
            user.points -= product.cost_points  # Update user points

    db.add_all(redemptions)
    db.commit()
    print(f"   -> {len(redemptions)} resgates criados (nenhum para o B2C demo).")

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
        co2_total_b2c = _seed_events(db, esg_engine, vehicles, faker)
        _seed_redemptions(db, users, products)

        # 1 kg de CO2 = 1 ponto de carbono no Marketplace.
        print(f"\n💰 Saldo real do B2C demo no Marketplace: ~{co2_total_b2c:.2f} pontos.")
        print("\n✅ Seeding finalizado com Sucesso!")
    except Exception as e:
        print(f"❌ Erro durante o seeding: {e}")
        db.rollback()
    finally:
        print("🔒 Fechando conexão com o banco.")
        db.close()

if __name__ == "__main__":
    run_seeder()
