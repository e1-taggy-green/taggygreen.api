import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database.session import get_db
from src.services.market_service import MarketService
from src.models import Base, User, Vehicle, Event, Product, Redemption

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


def _criar_usuario_com_saldo(db_session, co2_total: float) -> User:
    """
    Cria um usuário B2C cujo saldo real de mitigação vem de um único evento.
    O saldo real do Marketplace é SUM(Event.co2_saved) - SUM(custo dos resgates),
    e os eventos só contam via JOIN Event -> Vehicle -> user_id.
    """
    user = User(name="Clara B2C", email="clara.b2c@taggy.com", user_type="b2c", points=0)
    db_session.add(user)
    db_session.commit()

    vehicle = Vehicle(license_plate="CLR-0001", vehicle_type="car", user_id=user.id)
    db_session.add(vehicle)
    db_session.commit()

    evento = Event(vehicle_id=vehicle.id, event_type="toll", co2_saved=co2_total)
    db_session.add(evento)
    db_session.commit()
    return user


# ---------------------------------------------------------------------------
# Testes de Listagem Paginada (GET /api/v1/b2c/marketplace/produtos)
# ---------------------------------------------------------------------------

def test_listagem_paginada_retorna_produtos_com_campos_corretos(db_session, client):
    """
    Cenário 1 — Listagem Paginada de Produtos.
    GIVEN usuário B2C na aba Marketplace
    WHEN getProdutosMP receber ?page=1
    THEN retorna o array de recompensas com Nome e pontos_custo.
    Response contém apenas 'items' e 'total' (sem 'page'/'size').
    """
    produtos = [
        Product(name="Voucher iFood R$25", cost_points=2500),
        Product(name="Crédito Uber R$10", cost_points=1200),
        Product(name="Ingresso Cinemark", cost_points=1800),
    ]
    db_session.add_all(produtos)
    db_session.commit()

    response = client.get("/api/v1/b2c/marketplace/produtos?page=1")
    assert response.status_code == 200
    data = response.json()

    # Response contém apenas 'items' e 'total' (conforme Swagger).
    assert set(data.keys()) == {"items", "total"}
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Cada item deve trazer exatamente os campos contratuais.
    primeiro = data["items"][0]
    assert set(primeiro.keys()) == {"id", "nome", "pontos_custo"}
    assert primeiro["nome"] == "Voucher iFood R$25"
    assert primeiro["pontos_custo"] == 2500


def test_paginacao_respeita_size_e_offset(db_session, client):
    """A paginação deve fatiar os produtos por offset/limit mantendo o total geral."""
    produtos = [Product(name=f"Recompensa {i}", cost_points=100 * i) for i in range(1, 6)]
    db_session.add_all(produtos)
    db_session.commit()

    response = client.get("/api/v1/b2c/marketplace/produtos?page=2&size=2")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 5
    # Página 2 com size 2 traz o 3º e o 4º produtos (offset 2).
    assert [item["nome"] for item in data["items"]] == ["Recompensa 3", "Recompensa 4"]


# ---------------------------------------------------------------------------
# Testes de Destaques (GET /api/v1/b2c/marketplace/destaques)
# ---------------------------------------------------------------------------

def test_destaques_retorna_lista_com_3_produtos_ordenados(db_session, client):
    """
    getDestaqueMP deve retornar uma lista com os 3 produtos de maior cost_points,
    ordenados de forma decrescente.
    """
    db_session.add_all([
        Product(name="Barata", cost_points=500),
        Product(name="Cara", cost_points=3500),
        Product(name="Média", cost_points=1800),
        Product(name="Premium", cost_points=5000),
    ])
    db_session.commit()

    response = client.get("/api/v1/b2c/marketplace/destaques")
    assert response.status_code == 200
    data = response.json()

    # Deve ser uma lista (array) com exatamente 3 itens.
    assert isinstance(data, list)
    assert len(data) == 3

    # Ordenados por pontos_custo decrescente: Premium > Cara > Média.
    nomes = [item["nome"] for item in data]
    assert nomes == ["Premium", "Cara", "Média"]

    # Cada item usa o campo correto pontos_custo.
    assert data[0]["pontos_custo"] == 5000
    assert data[1]["pontos_custo"] == 3500
    assert data[2]["pontos_custo"] == 1800


def test_destaques_retorna_menos_de_3_quando_poucos_produtos(db_session, client):
    """Quando há menos de 3 produtos, retorna todos os existentes."""
    db_session.add_all([
        Product(name="Único", cost_points=1000),
    ])
    db_session.commit()

    response = client.get("/api/v1/b2c/marketplace/destaques")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Único"


# ---------------------------------------------------------------------------
# Testes de Resgate (POST /api/v1/b2c/marketplace/resgatar)
# ---------------------------------------------------------------------------

def test_resgate_saldo_insuficiente_retorna_400_e_nao_cria_redemption(db_session, client):
    """
    Cenário 2 — Resgate com Saldo Insuficiente.
    GIVEN Clara possui 20 Pontos de Carbono e tenta resgatar voucher de 50.
    WHEN updateSaldo processar o pedido
    THEN aborta a transação (rollback), retorna 400 "saldo insuficiente",
         NÃO cria Redemption e o saldo NÃO fica negativo.
    """
    user = _criar_usuario_com_saldo(db_session, co2_total=20.0)
    voucher = Product(name="Voucher 50", cost_points=50)
    db_session.add(voucher)
    db_session.commit()

    # Contagem de resgates ANTES da tentativa.
    resgates_antes = db_session.query(Redemption).count()

    response = client.post(
        "/api/v1/b2c/marketplace/resgatar",
        json={"email": user.email, "product_id": voucher.id},
    )

    # Saldo insuficiente -> 400 com a mensagem contratual (minúsculo).
    assert response.status_code == 400
    assert response.json()["detail"] == "saldo insuficiente"

    # Rollback: nenhuma Redemption nova foi persistida.
    resgates_depois = db_session.query(Redemption).count()
    assert resgates_depois == resgates_antes == 0

    # O saldo real permanece intacto e não-negativo (20 - 0 = 20).
    saldo = MarketService(db_session)._get_saldo_real(user.id)
    assert saldo == 20.0
    assert saldo >= 0


def test_resgate_saldo_suficiente_retorna_200_com_saldo_atualizado(db_session, client):
    """
    Cenário extra — Resgate com Saldo Suficiente.
    Cria a Redemption, debita o custo e retorna apenas 'saldo_atualizado'.
    """
    user = _criar_usuario_com_saldo(db_session, co2_total=100.0)
    voucher = Product(name="Voucher 30", cost_points=30)
    db_session.add(voucher)
    db_session.commit()

    resgates_antes = db_session.query(Redemption).count()

    response = client.post(
        "/api/v1/b2c/marketplace/resgatar",
        json={"email": user.email, "product_id": voucher.id},
    )

    # Sucesso → status 200 (conforme Swagger, não 201).
    assert response.status_code == 200
    data = response.json()

    # Response contém apenas 'saldo_atualizado'.
    assert set(data.keys()) == {"saldo_atualizado"}
    # Saldo atualizado = 100 - 30 = 70.
    assert data["saldo_atualizado"] == 70.0

    # A Redemption foi efetivamente persistida (commit).
    resgates_depois = db_session.query(Redemption).count()
    assert resgates_depois == resgates_antes + 1

    # O saldo real recalculado reflete o débito do resgate (100 - 30 = 70).
    saldo = MarketService(db_session)._get_saldo_real(user.id)
    assert saldo == 70.0


def test_resgate_produto_inexistente_retorna_404(db_session, client):
    """updateSaldo deve retornar 404 quando o produto não existe."""
    user = _criar_usuario_com_saldo(db_session, co2_total=100.0)

    response = client.post(
        "/api/v1/b2c/marketplace/resgatar",
        json={"email": user.email, "product_id": 9999},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"


def test_resgate_usuario_inexistente_retorna_404(db_session, client):
    """
    updateSaldo deve retornar 404 quando o email do usuário não existe no banco.
    """
    voucher = Product(name="Voucher 10", cost_points=10)
    db_session.add(voucher)
    db_session.commit()

    response = client.post(
        "/api/v1/b2c/marketplace/resgatar",
        json={"email": "inexistente@taggy.com", "product_id": voucher.id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não encontrado"


def test_resgate_com_email_padrao_default(db_session, client):
    """
    Testa se a API assume o e-mail padrão "teste.b2c@taggy.com" quando nenhum e-mail é fornecido.
    """
    # Criar o usuário de teste correspondente ao email padrão com pontos suficientes
    user = User(name="Carlos Demo B2C", email="teste.b2c@taggy.com", user_type="b2c", points=0)
    db_session.add(user)
    db_session.commit()

    # Criar um veículo e um evento de mitigação para dar saldo real de carbono ao usuário
    vehicle = Vehicle(license_plate="DEF-1234", vehicle_type="car", user_id=user.id)
    db_session.add(vehicle)
    db_session.commit()

    evento = Event(vehicle_id=vehicle.id, event_type="toll", co2_saved=100.0)
    db_session.add(evento)
    db_session.commit()

    voucher = Product(name="Voucher Default 10", cost_points=10)
    db_session.add(voucher)
    db_session.commit()

    # Omitindo o campo email no payload JSON
    response = client.post(
        "/api/v1/b2c/marketplace/resgatar",
        json={"product_id": voucher.id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["saldo_atualizado"] == 90.0

    # A Redemption foi associada ao user_id do usuário default
    redemption = db_session.query(Redemption).filter(Redemption.user_id == user.id).first()
    assert redemption is not None
    assert redemption.product_id == voucher.id
