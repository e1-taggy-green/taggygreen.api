import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database.session import get_db
from src.models import Base, User, Vehicle, Event

# Setup database SQLite em memória para testes com StaticPool
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


def test_b2c_usuarios_inexistentes(client):
    """
    Testa se os endpoints B2C retornam 404 quando o e-mail não corresponde a nenhum usuário cadastrado.
    """
    # Usuário inexistente informado por e-mail
    response = client.get("/api/v1/b2c/user?email=nonexistent.b2c@taggy.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"

    response = client.get("/api/v1/b2c/user/rastro-historico?email=nonexistent.b2c@taggy.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"

    response = client.get("/api/v1/b2c/user/extrato?email=nonexistent.b2c@taggy.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"


def test_b2c_fluxo_completo(db_session, client):
    """
    Cria uma massa de testes de B2C e valida os retornos, filtragens
    e agrupamentos dos três endpoints contratuais de B2C.
    """
    # 1. Criar usuário B2C de teste
    user = User(name="Clarice B2C", email="clarice.b2c@taggy.com", user_type="b2c", points=1000)
    db_session.add(user)
    db_session.commit()

    # 2. Criar veículo associado
    v_car = Vehicle(license_plate="B2C-1234", vehicle_type="car", user_id=user.id)
    db_session.add(v_car)
    db_session.commit()

    # 3. Criar eventos em datas dinâmicas para testar a janela de 4 meses
    hoje = datetime.now()
    mes_atual = hoje
    mes_anterior = hoje - timedelta(days=32)
    mes_fora_janela = hoje - timedelta(days=150) # ~5 meses atrás, fora da janela de 4 meses

    # Evento no mês atual: tipo pedágio (toll), co2 = 1.5
    event1 = Event(vehicle_id=v_car.id, event_type="toll", co2_saved=1.5, fuel_saved=0.6, time_saved=10.0, created_at=mes_atual)
    # Evento no mês anterior: tipo estacionamento (parking), co2 = 2.0
    event2 = Event(vehicle_id=v_car.id, event_type="parking", co2_saved=2.0, fuel_saved=0.8, time_saved=15.0, created_at=mes_anterior)
    # Evento fora da janela de 4 meses: tipo pedágio (toll), co2 = 3.0
    event3 = Event(vehicle_id=v_car.id, event_type="toll", co2_saved=3.0, fuel_saved=1.2, time_saved=12.0, created_at=mes_fora_janela)

    db_session.add_all([event1, event2, event3])
    db_session.commit()

    # --- Testar GET /user ---
    response = client.get("/api/v1/b2c/user?email=clarice.b2c@taggy.com")
    assert response.status_code == 200
    data = response.json()
    assert data["userName"] == "Clarice B2C"
    # O saldo total acumulado de mitigação deve ser a soma de todos os eventos (1.5 + 2.0 + 3.0 = 6.5)
    assert data["userPoints"] == 6.5

    # --- Testar GET /user/rastro-historico ---
    response = client.get("/api/v1/b2c/user/rastro-historico?email=clarice.b2c@taggy.com")
    assert response.status_code == 200
    rastro_list = response.json()
    
    # Deve conter apenas 2 meses, já que o terceiro evento está a 5 meses atrás (fora da janela dos últimos 4 meses)
    assert len(rastro_list) == 2
    
    # Verificar chaves do Swagger
    assert "mes" in rastro_list[0]
    assert "co2_economizado" in rastro_list[0]

    # Ordenado cronologicamente, então o mes_anterior vem antes do mes_atual
    assert rastro_list[0]["co2_economizado"] == 2.0
    assert rastro_list[1]["co2_economizado"] == 1.5

    # --- Testar GET /user/extrato ---
    response = client.get("/api/v1/b2c/user/extrato?email=clarice.b2c@taggy.com")
    assert response.status_code == 200
    extrato_list = response.json()
    
    # O extrato deve conter todas as 3 passagens, ordenadas decrescentemente por data (mais recente primeiro)
    assert len(extrato_list) == 3
    
    # Primeiro item deve ser a passagem mais recente (mes_atual)
    assert extrato_list[0]["nome"] == "Praça de Pedágio"
    assert extrato_list[0]["registro_economia"] == 1.5
    
    # Segundo item deve ser o mes_anterior
    assert extrato_list[1]["nome"] == "Estacionamento"
    assert extrato_list[1]["registro_economia"] == 2.0
    
    # Terceiro item deve ser o mais antigo (fora da janela)
    assert extrato_list[2]["nome"] == "Praça de Pedágio"
    assert extrato_list[2]["registro_economia"] == 3.0


def test_b2c_default_email(db_session, client):
    """
    Testa se a API assume o e-mail padrão "teste.b2c@taggy.com" quando nenhum e-mail é passado por query parameter.
    """
    # Criar usuário default
    user_default = User(name="Carlos Demo B2C", email="teste.b2c@taggy.com", user_type="b2c", points=50000)
    db_session.add(user_default)
    db_session.commit()

    # Chamar endpoint sem passar e-mail
    response = client.get("/api/v1/b2c/user")
    assert response.status_code == 200
    data = response.json()
    assert data["userName"] == "Carlos Demo B2C"
    assert data["userPoints"] == 0.0
