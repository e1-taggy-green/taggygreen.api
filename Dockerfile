FROM python:3.11-slim

WORKDIR /app

# Instala o Poetry de forma simplificada via pip
RUN pip install poetry

# Copia apenas os arquivos do Poetry primeiro (para otimizar o cache)
COPY pyproject.toml poetry.lock ./

# Desativa a criação de ambiente virtual e instala as dependências do projeto
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# Copia todo o resto do código para dentro da imagem
COPY . .

# Executa as migrations e inicia a aplicação (Render injeta a variável PORT)
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
