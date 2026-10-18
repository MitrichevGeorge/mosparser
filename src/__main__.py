from .vault import initVault, tokens

initVault()
if tokens is None:
    raise RuntimeError

print(tokens.refresh_token)