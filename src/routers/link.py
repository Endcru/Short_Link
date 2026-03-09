from typing import Optional
from fastapi import APIRouter, status, Query, Depends, HTTPException
from services.schemas import UserCreate, UserUpdate, UserResponse, UserList
from services.user_service import UserService
from services.user_service import get_current_user, get_optional_current_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database.models import User, Link
from services.link_service import LinkService
from services.schemas import LinkCreate, LinkResponse, LinkList
from fastapi.responses import RedirectResponse

SHORT_CODES_BLOCK = ["all", "project"] #Эти шорт коды нельзя использовать так как они совпадают к роутами

router = APIRouter(
    prefix="/link",
    tags=["link"],
    responses={404: {"description": "Link not found / Ссылка не найдена"}}
)

link_service = LinkService()

@router.post(
    "/shorten",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new link / Создать ссылку",
    description="Create a new link with original URL and short code / Создать ссылку с оригинальной URL и коротким кодом"
)
async def create_link(link_data: LinkCreate, current_user: User = Depends(get_optional_current_user)) -> LinkResponse:
    if current_user:
        if link_data.short_code:
            short_code_exists = await link_service.check_short_code_exists(link_data.short_code)
            if short_code_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Short code already exists / Короткий код уже существует"
                )
            if link_data.short_code in SHORT_CODES_BLOCK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This short code can not be used / Этот короткий код не может быть использован"
                )
        link = await link_service.create_link_authorized(link_data, current_user)
    else:
        if link_data.short_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short code is not supported for unauthorized users / Короткий код не поддерживается для неавторизованных пользователей"
            )
        link = await link_service.create_link_unauthorized(link_data)
    return LinkResponse.model_validate(link)


@router.get(
    "/{short_code}/stats",
    response_model=LinkResponse,
    summary="Get link stats / Получить статистику ссылки",
    description="Get link stats / Получить статистику ссылки"
)
async def get_link_stats(short_code: str) -> LinkResponse:
    link = await link_service.get_link_by_short_code(short_code)
    return LinkResponse.model_validate(link)

@router.get(
    "/all",
    response_model=LinkList,
    summary="Get all links / Получить все ссылки",
    description="Get all links / Получить все ссылки"
)
async def get_all_links(
    skip: int = Query(0, ge=0, description="Number of records to skip / Количество записей пропустить"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return / Максимум записей вернуть"),
) -> LinkList:
    links, total = await link_service.get_all_links(skip, limit)
    link_responses = [LinkResponse.model_validate(link) for link in links]
    return LinkList(total=total, links=link_responses)

@router.get(
    "/{short_code}",
    response_model=LinkResponse,
    summary="Redirext to original URL / Перенаправление на оригинальную URL-адрес",
    description="Redirect to original URL / Перенаправление на оригинальную URL-адрес"
)
async def redirect_to_original_url(short_code: str) -> RedirectResponse:
    original_url = await link_service.use_short_code(short_code)
    return RedirectResponse(url=original_url)

@router.delete(
    "/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete link / Удалить ссылку",
    description="Delete link by short_code / Удалить ссылку по short_code"
)
async def delete_link(short_code: str, current_user: User = Depends(get_current_user)) -> None:
    await link_service.delete_link(short_code, current_user)
    # Return 204 No Content / Вернуть 204 No Content
