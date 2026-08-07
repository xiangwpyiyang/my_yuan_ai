from pydantic import BaseModel
from typing import Optional, Any, List, Dict


class CommandRequest(BaseModel):
    command: str
    history: Optional[List[Dict[str, str]]] = None


class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    action: Optional[str] = None