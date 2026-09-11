from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db, engine, Base
from .routes import (
    paciente_router,
    profissional_router,
    sala_router,
    convenio_router,
    pacote_router,
    sessao_router,
    evolucao_clinica_router,
    falta_router,
    lote_router,
    fatura_router,
)

# Criar as tabelas no banco de dados (em desenvolvimento)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema Sessão - Clínicas de Fisioterapia",
    description="API para gerenciamento de sessões de fisioterapia com validação de regras de negócio",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir os routers
app.include_router(paciente_router, prefix="/api/pacientes", tags=["Pacientes"])
app.include_router(profissional_router, prefix="/api/profissionais", tags=["Profissionais"])
app.include_router(sala_router, prefix="/api/salas", tags=["Salas"])
app.include_router(convenio_router, prefix="/api/convenios", tags=["Convênios"])
app.include_router(pacote_router, prefix="/api/pacotes", tags=["Pacotes"])
app.include_router(sessao_router, prefix="/api/sessoes", tags=["Sessões"])
app.include_router(evolucao_clinica_router, prefix="/api/evolucoes", tags=["Evoluções Clínicas"])
app.include_router(falta_router, prefix="/api/faltas", tags=["Faltas"])
app.include_router(lote_router, prefix="/api/lotes", tags=["Lotes"])
app.include_router(fatura_router, prefix="/api/faturas", tags=["Faturas"])


@app.get("/api/health")
def health_check():
    """Endpoint de saúde da API"""
    return {"status": "OK", "message": "API do Sistema Sessão está funcionando"}


@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "message": "Bem-vindo ao Sistema Sessão",
        "documentation": "/docs",
        "health_check": "/api/health",
    }
