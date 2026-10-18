import asyncio

from rich import print

from .auth import req_aupd_token, req_get_profile
from .vault import get_tokens, init_vault

init_vault()
tokens = get_tokens()

# asyncio.run(req_aupd_token())
print(asyncio.run(req_get_profile()))
# print(tokens.refresh_token)