import asyncio
from .cli import run_cli
from .vault import get_tokens, init_vault

init_vault()
tokens = get_tokens()
asyncio.run(run_cli())

# if args.get_tk:
#     asyncio.run(req_aupd_token())
#     print(tokens.aupd_token)
#     sys.exit(0)

# rich_print(asyncio.run(req_get_profile()))

# asyncio.run(req_aupd_token())
# print(tokens.refresh_token)