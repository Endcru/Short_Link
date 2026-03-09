from typing import Optional
from fastapi_cache.decorator import cache
from fastapi import APIRouter, status, Query, Depends, HTTPException
from services.user_service import get_current_user, get_optional_current_user
from database.models import User, Link
from services.link_service import LinkService
from services.schemas import LinkCreate, LinkResponse, LinkList, LinkUpdate
from fastapi.responses import RedirectResponse

SHORT_CODES_BLOCK = ["all", "project", "search"] #Эти шорт коды нельзя использовать так как они совпадают к роутами

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
        if link_data.custom_alias:
            short_code_exists = await link_service.check_short_code_exists(link_data.custom_alias)
            if short_code_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alias already exists / Короткий код уже существует"
                )
            if link_data.custom_alias in SHORT_CODES_BLOCK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alias can not be used / Этот короткий код не может быть использован"
                )
        link = await link_service.create_link_authorized(link_data, current_user)
    else:
        if link_data.custom_alias:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alias is not supported for unauthorized users / Короткий код не поддерживается для неавторизованных пользователей"
            )
        link = await link_service.create_link_unauthorized(link_data)
    return LinkResponse.model_validate(link)

@router.patch(
    "/{short_code}",
    response_model=LinkResponse,
    summary="Update link / Обновить ссылку",
    description="Update link information / Обновить информацию о ссылке"
)
async def update_link(short_code: str, link_data: LinkUpdate, current_user: User = Depends(get_current_user)) -> LinkResponse:
    link = await link_service.update_link(short_code, link_data, current_user)
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
    "/project/{project_name}",
    response_model=LinkList,
    summary="Get all links from project / Получить все ссылки проекта",
    description="Get all links from project / Получить все ссылки  проекта"
)
async def get_project_links(project_name: str, current_user: User = Depends(get_current_user)) -> LinkList:
    links, total = await link_service.get_project_links(project_name, current_user)
    link_responses = [LinkResponse.model_validate(link) for link in links]
    return LinkList(total=total, links=link_responses)


@router.get(
    "/search",
    response_model=LinkList,
    summary="Get all links of original link / Получить все ссылки оригинальной ссылки",
    description="Get all links of original link / Получить все ссылки оригинальной ссылки"
)
@cache(expire=60)
async def search_original_url(original_url: str, current_user: User = Depends(get_optional_current_user)) -> LinkList:
    links, total = await link_service.search_original_url(original_url, current_user)
    link_responses = [LinkResponse.model_validate(link) for link in links]
    return LinkList(total=total, links=link_responses)

@router.get(
    "/{short_code}",
    response_model=LinkResponse,
    summary="Redirext to original URL / Перенаправление на оригинальную URL-адрес",
    description="Redirect to original URL / Перенаправление на оригинальную URL-адрес"
)
@cache(expire=60)
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
