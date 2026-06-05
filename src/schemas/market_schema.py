from pydantic import BaseModel, Field


class ProdutoResponse(BaseModel):
    """
    Contrato de um produto/recompensa do Marketplace (Swagger: Produto).
    O front-end resolve a imagem a partir do id — por isso não há campo image_url.
    """
    id: int = Field(..., description="Identificador único do produto")
    nome: str = Field(..., description="Nome da recompensa")
    pontos_custo: int = Field(..., description="Custo em Pontos de Carbono")


class ProdutosPaginadosResponse(BaseModel):
    """Resposta paginada: apenas items e total (conforme Swagger)."""
    items: list[ProdutoResponse] = Field(..., description="Recompensas da página")
    total: int = Field(..., description="Total geral de recompensas")


class ResgateRequest(BaseModel):
    """Payload de entrada do resgate: email + product_id."""
    email: str = Field("teste.b2c@taggy.com", description="E-mail do usuário que está resgatando")
    product_id: int = Field(..., gt=0, description="ID do produto a resgatar")


class ResgateResponse(BaseModel):
    """Payload de saída do resgate: apenas o saldo atualizado (conforme Swagger)."""
    saldo_atualizado: int = Field(..., description="Saldo de pontos após o resgate")
