import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database.session import get_db
from src.models import Base, User, Vehicle, Event

# Setup database SQLite em memória para testes com StaticPool para compartilhar a conexão
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def fixture_db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def fixture_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_b2b_endpoints_sem_dados(client):
    """
    Testa se os endpoints retornam a estrutura vazia padrão quando o usuário existe
    mas não há eventos registrados ou quando o usuário não existe.
    """
    # Usuário inexistente
    response = client.get("/api/v1/b2b/relatorios/esg?email=nonexistent@b2b.com")
    assert response.status_code == 200
    assert response.json()["co2_evitado_kg"] == 0.0
    assert response.json()["frota_total"] == 0

    response_cat = client.get("/api/v1/b2b/performance/categoria?email=nonexistent@b2b.com")
    assert response_cat.status_code == 404

    response_rank = client.get("/api/v1/b2b/performance/ranking?email=nonexistent@b2b.com")
    assert response_rank.status_code == 404

def test_b2b_endpoints_com_dados(db_session, client):
    """
    Cria uma massa de testes de B2B e valida se os endpoints agregam, traduzem
    e expõem as chaves corretas conforme o contrato OpenAPI.
    """
    # 1. Criar usuário B2B
    user = User(name="Empresa Teste LTDA", email="contato@empresa.com", user_type="b2b", points=0)
    db_session.add(user)
    db_session.commit()

    # 2. Criar veículos (um Carro e um Caminhão)
    v_car = Vehicle(license_plate="CAR-1234", vehicle_type="car", user_id=user.id)
    v_truck = Vehicle(license_plate="TRK-5678", vehicle_type="truck", user_id=user.id)
    db_session.add_all([v_car, v_truck])
    db_session.commit()

    # 3. Criar eventos para os veículos
    # Carro: 2 eventos, total co2 = 3.0, fuel = 1.2
    event_car1 = Event(vehicle_id=v_car.id, event_type="toll", co2_saved=1.5, fuel_saved=0.6, time_saved=2.0)
    event_car2 = Event(vehicle_id=v_car.id, event_type="parking", co2_saved=1.5, fuel_saved=0.6, time_saved=3.0)
    
    # Caminhão: 1 evento, total co2 = 5.0, fuel = 2.0
    event_truck1 = Event(vehicle_id=v_truck.id, event_type="toll", co2_saved=5.0, fuel_saved=2.0, time_saved=2.0)

    db_session.add_all([event_car1, event_car2, event_truck1])
    db_session.commit()

    # --- Testar Relatório ESG Consolidado ---
    response = client.get("/api/v1/b2b/relatorios/esg?email=contato@empresa.com")
    assert response.status_code == 200
    data = response.json()
    assert data["co2_evitado_kg"] == 8.0 # 1.5 + 1.5 + 5.0
    assert data["combustivel_evitado_litros"] == 3.2 # 0.6 + 0.6 + 2.0
    assert data["tempo_economizado_minutos"] == 7.0 # 2.0 + 3.0 + 2.0
    assert data["frota_total"] == 2

    # --- Testar Performance por Categoria ---
    response_cat = client.get("/api/v1/b2b/performance/categoria?email=contato@empresa.com")
    assert response_cat.status_code == 200
    cat_data = response_cat.json()
    assert len(cat_data) == 2

    # Verificar que as chaves foram traduzidas para português ("Carro", "Caminhão")
    car_cat = next(c for c in cat_data if c["categoria"] == "Carro")
    truck_cat = next(c for c in cat_data if c["categoria"] == "Caminhão")

    assert car_cat["co2_evitado_kg"] == 3.0
    assert car_cat["combustivel_evitado_litros"] == 1.2

    assert truck_cat["co2_evitado_kg"] == 5.0
    assert truck_cat["combustivel_evitado_litros"] == 2.0

    # --- Testar Ranking da Frota ---
    response_rank = client.get("/api/v1/b2b/performance/ranking?email=contato@empresa.com")
    assert response_rank.status_code == 200
    rank_data = response_rank.json()
    assert len(rank_data) == 2

    # Veículo com mais transações (CAR-1234 tem 2 transações, TRK-5678 tem 1 transação)
    # Então CAR-1234 deve ser o primeiro
    assert rank_data[0]["posicao"] == 1
    assert rank_data[0]["placa"] == "CAR-1234"
    assert rank_data[0]["tipo"] == "Carro" # Verificar tradução do tipo
    assert rank_data[0]["co2_evitado_kg"] == 3.0
    assert rank_data[0]["transacoes"] == 2

    assert rank_data[1]["posicao"] == 2
    assert rank_data[1]["placa"] == "TRK-5678"
    assert rank_data[1]["tipo"] == "Caminhão" # Verificar tradução do tipo
    assert rank_data[1]["co2_evitado_kg"] == 5.0
    assert rank_data[1]["transacoes"] == 1
