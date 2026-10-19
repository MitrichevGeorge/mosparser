import argparse

from .auth import req_check_for_max, req_get_profile
from .helpers import print
from .vault import get_tokens


async def auth_check_max(args):
    print(await req_check_for_max())

async def auth_profile(args):
    print(await req_get_profile())

async def auth_get_refresh_tk(args):
    tokens = get_tokens()
    print(tokens.refresh_token)

async def auth_get_get_aupd_tk(args):
    tokens = get_tokens()
    print(tokens.aupd_token)

async def run_cli():
    argparser = argparse.ArgumentParser(description="mos parser")
    subparsers = argparser.add_subparsers(dest="command", required=True)

    parser_auth = subparsers.add_parser("auth", help="Действия с авторизацией/аккаунтом")
    subparser_auth = parser_auth.add_subparsers(dest="auth_command", required=True)

    subparser_auth.add_parser("check_max", help="Получить информацию о привязке max").set_defaults(func=auth_check_max)
    subparser_auth.add_parser("profile", help="Получить свой профиль(ФИО, др, номер телефона, email, пол, школа, ава, person_id)").set_defaults(func=auth_profile)
    subparser_auth.add_parser("get_refresh_tk", help="Получить aupd_refresh_token").set_defaults(func=auth_get_refresh_tk)
    subparser_auth.add_parser("get_aupd_tk", help="Получить aupd_token").set_defaults(func=auth_get_get_aupd_tk)


    args = argparser.parse_args()
    await args.func(args)
