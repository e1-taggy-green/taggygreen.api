import datetime
from unittest.mock import patch, MagicMock
import pytest
import httpx
from src.services.fuel_service import FuelPriceService

@pytest.fixture(autouse=True)
def reset_fuel_service_cache():
    """
    Limpa o cache da classe FuelPriceService antes e depois de cada teste.
    """
    FuelPriceService._cached_price = None
    FuelPriceService._last_updated = None
    yield
    FuelPriceService._cached_price = None
    FuelPriceService._last_updated = None

def test_get_average_gasoline_price_success():
    """
    Testa o cenário em que a API externa responde com sucesso e o cálculo da média
    é executado corretamente (excluindo a chave 'br' e convertendo o formato de vírgula).
    """
    mock_response_data = {
        "error": False,
        "precos": {
            "gasolina": {
                "br": "6.50",  # Ignorado no cálculo da média dos estados
                "sp": "6,00",
                "rj": "7,00",
                "mg": "6,20",
                "invalid": "broken_value"  # Deve ser ignorado sem quebrar
            }
        }
    }

    # Média esperada: (6.00 + 7.00 + 6.20) / 3 = 19.20 / 3 = 6.40

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data

    service = FuelPriceService()

    # Patch do httpx.Client.get
    with patch("httpx.Client.get", return_value=mock_response) as mock_get:
        price = service.get_average_gasoline_price()
        
        # Verificar chamada
        mock_get.assert_called_once_with(
            "https://combustivelapi.com.br/api/precos/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
                "Accept": "application/json"
            }
        )
        
        assert price == pytest.approx(6.40)
        assert FuelPriceService._cached_price == pytest.approx(6.40)
        assert FuelPriceService._last_updated is not None

def test_get_average_gasoline_price_caching():
    """
    Testa se o cache em memória é respeitado e evita chamadas subsequentes à API.
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "precos": {
            "gasolina": {
                "sp": "6,00",
                "rj": "7,00"
            }
        }
    }

    service = FuelPriceService()

    with patch("httpx.Client.get", return_value=mock_response) as mock_get:
        # Primeira chamada: deve bater na API
        price1 = service.get_average_gasoline_price()
        assert price1 == pytest.approx(6.50)
        assert mock_get.call_count == 1

        # Segunda chamada: deve retornar o cache diretamente
        price2 = service.get_average_gasoline_price()
        assert price2 == pytest.approx(6.50)
        assert mock_get.call_count == 1

def test_get_average_gasoline_price_fallback():
    """
    Testa a política de contingência se a API externa falhar (retornar erro ou timeout).
    """
    service = FuelPriceService()

    # Simular uma exceção no httpx.Client.get (ex: Timeout)
    with patch("httpx.Client.get", side_effect=httpx.ConnectTimeout("Timeout ao conectar")):
        price = service.get_average_gasoline_price()
        
        # Deve retornar o valor de fallback padrão seguro (R$ 5,50)
        assert price == 5.50
        assert FuelPriceService._cached_price is None

def test_get_average_gasoline_price_fallback_with_old_cache():
    """
    Testa se, em caso de erro da API, o serviço utiliza o cache antigo
    em vez de reverter imediatamente para o fallback padrão.
    """
    service = FuelPriceService()

    # Preencher cache antigo manualmente
    FuelPriceService._cached_price = 6.80
    FuelPriceService._last_updated = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=25) # Expirado

    # Simular erro na API ao tentar atualizar
    with patch("httpx.Client.get", side_effect=httpx.HTTPStatusError("Erro", request=MagicMock(), response=MagicMock())):
        price = service.get_average_gasoline_price()
        
        # Como o cache estava expirado e a API falhou, deve manter o cache antigo (6.80) ao invés do fallback padrão (5.50)
        assert price == 6.80
