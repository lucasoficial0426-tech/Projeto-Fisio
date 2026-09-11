from .paciente_routes import router as paciente_router
from .profissional_routes import router as profissional_router
from .sala_routes import router as sala_router
from .convenio_routes import router as convenio_router
from .pacote_routes import router as pacote_router
from .sessao_routes import router as sessao_router
from .evolucao_clinica_routes import router as evolucao_clinica_router
from .falta_routes import router as falta_router
from .lote_routes import router as lote_router
from .fatura_routes import router as fatura_router

__all__ = [
    "paciente_router",
    "profissional_router",
    "sala_router",
    "convenio_router",
    "pacote_router",
    "sessao_router",
    "evolucao_clinica_router",
    "falta_router",
    "lote_router",
    "fatura_router",
]
