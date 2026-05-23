import datetime
import logging
import httpx

logger = logging.getLogger(__name__)

class FuelPriceService:
    # Atributos de classe para persistência de cache entre requisições / instâncias
    _cached_price: float | None = None
    _last_updated: datetime.datetime | None = None
    CACHE_TTL_HOURS = 24
    FALLBACK_PRICE = 5.50

    def get_average_gasoline_price(self) -> float:
        """
        Obtém o preço médio da gasolina consultando a CombustivelAPI.
        Se houver cache válido (menor que 24 horas), retorna o valor em cache.
        Caso contrário, realiza a requisição, calcula a média dos estados (excluindo 'br') e atualiza o cache.
        Em caso de falha de conexão, timeout ou dados inválidos, retorna o valor de fallback seguro.
        """
        agora = datetime.datetime.now(datetime.timezone.utc)

        # 1. Verificar validade do cache
        if (
            FuelPriceService._cached_price is not None
            and FuelPriceService._last_updated is not None
            and (agora - FuelPriceService._last_updated) < datetime.timedelta(hours=self.CACHE_TTL_HOURS)
        ):
            return FuelPriceService._cached_price

        # 2. Consultar API externa com headers para evitar HTTP 403/406
        url = "https://combustivelapi.com.br/api/precos/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
            "Accept": "application/json"
        }

        try:
            # Timeout estrito de 2 segundos para não impactar a performance do nosso endpoint
            with httpx.Client(timeout=2.0) as client:
                response = client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                precos_gasolina = data.get("precos", {}).get("gasolina", {})

                # Coletar preços de todos os estados individuais (ignorando a média nacional 'br')
                valores_estados = []
                for key, val in precos_gasolina.items():
                    if key != "br":
                        try:
                            # Tratar o separador decimal brasileiro de vírgula para ponto
                            val_float = float(val.replace(",", "."))
                            valores_estados.append(val_float)
                        except ValueError:
                            continue

                if valores_estados:
                    average_price = sum(valores_estados) / len(valores_estados)
                    # Atualizar cache de classe
                    FuelPriceService._cached_price = average_price
                    FuelPriceService._last_updated = agora
                    return average_price
                else:
                    logger.warning("API de combustíveis respondeu com lista vazia ou sem valores parseáveis.")
            else:
                logger.warning(f"Erro HTTP na API de combustíveis: Status {response.status_code}")

        except Exception as e:
            logger.warning(f"Exceção ao obter preços de combustíveis da API: {e}")

        # 3. Política de Contingência (Resiliência)
        # Se a API falhou mas temos um cache antigo de execuções anteriores, usamos o cache antigo
        if FuelPriceService._cached_price is not None:
            logger.info("Utilizando cache antigo devido à falha na API externa.")
            return FuelPriceService._cached_price

        # Se não houver cache algum, retorna o fallback padrão
        logger.warning(f"Utilizando preço de fallback padrão (R$ {self.FALLBACK_PRICE:.2f}).")
        return self.FALLBACK_PRICE
