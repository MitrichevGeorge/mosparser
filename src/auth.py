from datetime import date, datetime

import httpx
from pydantic import UUID4, BaseModel, EmailStr, Field, HttpUrl

from .helpers import BASE_HEADERS
from .vault import get_tokens, save_vault


class RequestServerError(RuntimeError):
    """Ошибка выполнения api запроса"""

class RefreshTokenRevoked(RuntimeError):
    """Скорее всего устаревший токен"""

class RefreshTokenGetError(RequestServerError):
    """Общая ошибка получения aupd токена"""

class WrongAupdToken(RuntimeError):
    """Ошибка для всех случаев когда неверный aupd_token"""


async def req_aupd_token() -> None:
    tokens = get_tokens()
    async with httpx.AsyncClient(headers=BASE_HEADERS, timeout=10.0) as client:
        try:
            resp = await client.post(
                "https://school.mos.ru/v3/token/refresh", 
                cookies={'aupd_refresh_token': tokens.refresh_token},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            raise RefreshTokenGetError(str(e)) from e
    
    if 'msg' in data:
        if data['msg'] == 'token_revoked':
            raise RefreshTokenRevoked
        raise RefreshTokenGetError(f"API error:{data['msg']}")
    if not ('access_token' in data and 'refresh_token' in data):
        raise RefreshTokenGetError("Strange answer")

    tokens.aupd_token = data['access_token']
    tokens.refresh_token = data['refresh_token']

    save_vault()

class UserInfoProfilePicture(BaseModel):
    medium: HttpUrl
    large: HttpUrl

class UserInfoProfile(BaseModel):
    email: EmailStr
    phone: str = Field(pattern=r"^9\d{9}$")
    name: str #ФИО
    family_name: str #Ф
    given_name: str  #И
    middle_name: str #О
    gender: str #male/female
    education: list[dict]
    children: list
    birth_date: date
    updated_at: datetime
    picture: UserInfoProfilePicture

    agents: list
    sub: int
    broles: list[int]
    person_id: UUID4

async def req_get_profile() -> UserInfoProfile:
    tokens = get_tokens()
    async with httpx.AsyncClient(headers=BASE_HEADERS, timeout=10.0) as client:
        try:
            resp = await client.get(
                "https://school.mos.ru/v1/oauth/userinfo", 
                headers={'Authorization': f'Bearer {tokens.aupd_token}'},
            )
            if resp.status_code == 401:
                raise WrongAupdToken()
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            raise RequestServerError(str(e)) from e

    user_info = UserInfoProfile.model_validate(data)
    tokens.person_id = user_info.person_id
    return user_info

class UserMaxProfile(BaseModel):
    max_id: int
    max_link: HttpUrl

async def req_check_for_max() -> UserMaxProfile:
    tokens = get_tokens()
    if tokens.person_id is None:
        await req_get_profile()
    async with httpx.AsyncClient(headers=BASE_HEADERS, timeout=10.0) as client:
        try:
            resp = await client.get(
                "https://school.mos.ru/v2/external-partners/check-for-max-user",
                params={
                    "person_id": str(tokens.person_id),
                    "staff_id": "",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            raise RequestServerError(str(e)) from e

    max_profile = UserMaxProfile.model_validate(data)
    return max_profile
