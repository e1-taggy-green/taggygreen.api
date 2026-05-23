import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database.session import get_db
from src.models import Base, Lead

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


@pytest.fixture(autouse=True)
def mock_fuel_price():
    """Mock do preço médio do combustível para garantir determinismo nos testes."""
    with patch("src.services.fuel_service.FuelPriceService.get_average_gasoline_price", return_value=5.50):
        yield


def test_simulador_success_case(client, db_session):
    """
    Testa o cenário de sucesso da simulação com dados válidos,
    validando o cálculo matemático acumulado de pedágio e estacionamento
    e verificando se os dados do Lead e da simulação foram salvos no banco.
    """
    payload = {
        "lead": {
            "nome": "João Silva",
            "email": "joao@empresa.com",
            "telefone": "(11) 99999-9999",
            "endereco": "Av. Paulista, 1000"
        },
        "frota": {
            "qtd_carros": 10,
            "qtd_caminhoes": 5,
            "eventos_pedagio_carros": 20,
            "eventos_estacionamento_carros": 10,
            "eventos_pedagio_caminhoes": 20,
            "eventos_estacionamento_caminhoes": 10
        }
    }
    
    response = client.post("/api/v1/simulador/simulacao", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # Validações matemáticas:
    assert data["economia_co2_kg"] == 183.28
    assert data["economia_gasolina_litros"] == 72.5
    assert data["economia_tempo_minutos"] == 1050.0
    assert data["dinheiro_economizado"] == 1273.75

    # Validações no banco de dados (persistência)
    leads = db_session.query(Lead).all()
    assert len(leads) == 1
    lead_db = leads[0]
    assert lead_db.nome == "João Silva"
    assert lead_db.email == "joao@empresa.com"
    assert lead_db.telefone == "(11) 99999-9999"
    assert lead_db.endereco == "Av. Paulista, 1000"
    assert lead_db.qtd_carros == 10
    assert lead_db.qtd_caminhoes == 5
    assert lead_db.eventos_pedagio_carros == 20
    assert lead_db.eventos_estacionamento_carros == 10
    assert lead_db.eventos_pedagio_caminhoes == 20
    assert lead_db.eventos_estacionamento_caminhoes == 10
    assert lead_db.economia_co2_kg == 183.28
    assert lead_db.economia_gasolina_litros == 72.5
    assert lead_db.economia_tempo_minutos == 1050.0
    assert lead_db.dinheiro_economizado == 1273.75


def test_simulador_validation_frota_vazia(client):
    """
    Testa se a API retorna erro de validação (422) quando a frota
    contém 0 carros e 0 caminhões.
    """
    payload = {
        "lead": {
            "nome": "João Silva",
            "email": "joao@empresa.com"
        },
        "frota": {
            "qtd_carros": 0,
            "qtd_caminhoes": 0,
            "eventos_pedagio_carros": 10,
            "eventos_estacionamento_carros": 10,
            "eventos_pedagio_caminhoes": 10,
            "eventos_estacionamento_caminhoes": 10
        }
    }
    response = client.post("/api/v1/simulador/simulacao", json=payload)
    assert response.status_code == 422
    assert "A frota hipotética deve conter ao menos 1 veículo" in response.text


def test_simulador_validation_valores_negativos(client):
    """
    Testa se a API retorna erro de validação (422) ao enviar valores negativos
    para quantidade de veículos ou eventos.
    """
    # Cenário A: qtd_carros negativa
    payload_a = {
        "lead": {
            "nome": "João Silva",
            "email": "joao@empresa.com"
        },
        "frota": {
            "qtd_carros": -5,
            "qtd_caminhoes": 5,
            "eventos_pedagio_carros": 10,
            "eventos_estacionamento_carros": 10,
            "eventos_pedagio_caminhoes": 10,
            "eventos_estacionamento_caminhoes": 10
        }
    }
    response = client.post("/api/v1/simulador/simulacao", json=payload_a)
    assert response.status_code == 422

    # Cenário B: eventos negativos
    payload_b = {
        "lead": {
            "nome": "João Silva",
            "email": "joao@empresa.com"
        },
        "frota": {
            "qtd_carros": 5,
            "qtd_caminhoes": 0,
            "eventos_pedagio_carros": -10,
            "eventos_estacionamento_carros": 10,
            "eventos_pedagio_caminhoes": 10,
            "eventos_estacionamento_caminhoes": 10
        }
    }
    response = client.post("/api/v1/simulador/simulacao", json=payload_b)
    assert response.status_code == 422


def test_simulador_validation_email_invalido(client):
    """
    Testa se o validador de e-mail integrado da Pydantic rejeita e-mails inválidos.
    """
    payload = {
        "lead": {
            "nome": "João Silva",
            "email": "email_invalido"
        },
        "frota": {
            "qtd_carros": 5,
            "qtd_caminhoes": 0,
            "eventos_pedagio_carros": 10,
            "eventos_estacionamento_carros": 10,
            "eventos_pedagio_caminhoes": 10,
            "eventos_estacionamento_caminhoes": 10
        }
    }
    response = client.post("/api/v1/simulador/simulacao", json=payload)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.text
