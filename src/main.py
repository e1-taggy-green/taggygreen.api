from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.v1.simulador import router as simulador_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API para o Motor ESG e Plataformas B2C/B2B do projeto Taggy-Green.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulador_router)

@app.get("/", tags=["Health Check"])
async def root() -> dict[str, str]:
    """
    Endpoint raiz para verificação rápida de status (Health Check).
    Útil para load balancers e monitoramento de infraestrutura.
    """
    return {
        "message": f"Bem-vindo à {settings.PROJECT_NAME}",
        "status": "online",
        "version": settings.VERSION
    }
