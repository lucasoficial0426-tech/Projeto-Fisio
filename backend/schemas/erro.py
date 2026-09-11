from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    detail: str
    regra_negocio: Optional[str] = None
    status_code: Optional[int] = None
