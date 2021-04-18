from pydantic import BaseModel


class User(BaseModel):
    login: str
    password: str
    bots: str  # we have to store string representation of this
