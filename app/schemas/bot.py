from typing import Any

from pydantic import BaseModel


class Bot(BaseModel):
    bot_id: str
    token: str
    state: dict[str, str]
    config: dict[str, Any]

    class Config:
        orm_mode = True
