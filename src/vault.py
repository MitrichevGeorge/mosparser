import atexit
from pathlib import Path

from pydantic import UUID4, BaseModel, Field

__all__ = ["FileModel", "get_tokens", "init_vault", "save_vault"]

class FileModel(BaseModel):
    refresh_token: str
    aupd_token: str | None = None
    temp_token: str | None = Field(default=None, exclude=True)
    person_id: UUID4 | None = None

tokens_file = Path(".tokens")
tokens: FileModel | None = None

def init_vault():
    global tokens
    if not tokens_file.exists():
        raise FileNotFoundError("Нужно написать .tokens")
    
    tokens = FileModel.model_validate_json(tokens_file.read_text())
    atexit.register(save_vault)

def save_vault():
    if tokens:
        tokens_file.write_text(tokens.model_dump_json())

def get_tokens() -> FileModel:
    if tokens is None:
        raise RuntimeError("нужно вызвать init_vault")
    return tokens