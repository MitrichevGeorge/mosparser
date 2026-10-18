import atexit
from pathlib import Path

from pydantic import BaseModel, Field


class FileModel(BaseModel):
    refresh_token: str
    aupd_token: str | None = None
    temp_token: str | None = Field(default=None, exclude=True)

tokens_file = Path(".tokens")
tokens: FileModel | None = None

def initVault():
    global tokens
    if not tokens_file.exists():
        raise FileNotFoundError("Нужно написать .tokens")
    
    tokens = FileModel.model_validate_json(tokens_file.read_text())
    atexit.register(saveVault)

def saveVault():
    if tokens:
        tokens_file.write_text(tokens.model_dump_json())
