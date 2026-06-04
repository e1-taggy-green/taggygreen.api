from pydantic import BaseModel, Field


class ProdutoMPItem(BaseModel):
    """
    Contrato de uma única recompensa do Marketplace (getDestaqueMP / getProdutosMP).
    O image_url não é exposto pois não existe coluna correspondente no model Product
    (o front mapeia a imagem a partir do id).
    """
    id: int = Field(..., description="Identificador único do produto/recompensa")
    nome: str = Field(..., description="Nome da recompensa (Product.name)")
    custo_pontos_carbono: int = Field(..., description="Custo em Pontos de Carbono (Product.cost_points)")


class ProdutosPaginadosResponse(BaseModel):
    """Contrato do endpoint getProdutosMP: listagem paginada de recompensas."""
    page: int = Field(..., description="Página atual da listagem")
    size: int = Field(..., description="Quantidade de itens por página")
    total: int = Field(..., description="Total geral de recompensas disponíveis")
    items: list[ProdutoMPItem] = Field(..., description="Recompensas desta página")


class ResgateRequest(BaseModel):
    """Contrato de entrada do endpoint updateSaldo: pedido de resgate de recompensa."""
    user_id: int = Field(..., gt=0, description="Identificador do usuário que está resgatando")
    product_id: int = Field(..., gt=0, description="Identificador da recompensa a ser resgatada")


class ResgateResponse(BaseModel):
    """Contrato de saída do endpoint updateSaldo: confirmação do resgate processado."""
    redemption_id: int = Field(..., description="Identificador do resgate criado")
    user_id: int = Field(..., description="Identificador do usuário que resgatou")
    product_id: int = Field(..., description="Identificador da recompensa resgatada")
    pontos_debitados: int = Field(..., description="Pontos de Carbono abatidos no resgate")
    saldo_restante: float = Field(..., description="Saldo real restante após o débito do resgate")
    mensagem: str = Field(..., description="Mensagem de confirmação do resgate")
