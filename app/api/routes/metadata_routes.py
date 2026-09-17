##controler das requisições e deleça as services e exceções

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_metadata_service
from app.core.config import get_settings
from app.core.exceptions import (
    DuplicateMetadataException,
    InvalidMetadataIdException,
    MetadataNotFoundException,
)
from app.schemas.metadata_schemas import (
    MetadataCreateRequest,
    MetadataListResponse,
    MetadataResponse,
    MetadataUpdateRequest,
)
from app.services.metadata_service import MetadataService

router = APIRouter(prefix="/metadata", tags=["Metadata"])


@router.post(
    "",
    response_model=MetadataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo metadado de tabela",
)
async def create_metadata(
    payload: MetadataCreateRequest,
    service: MetadataService = Depends(get_metadata_service),
) -> MetadataResponse:
    try:
        return await service.create_metadata(payload)
    except DuplicateMetadataException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "",
    response_model=MetadataListResponse,
    summary="Listar metadados cadastrados (com paginação e filtros)",
)
async def list_metadata(
    page: int = Query(default=1, ge=1, description="Número da página (inicia em 1)."),
    page_size: Optional[int] = Query(
        default=None, ge=1, description="Quantidade de itens por página."
    ),
    owner: Optional[str] = Query(default=None, description="Filtrar por responsável."),
    domain: Optional[str] = Query(default=None, description="Filtrar por domínio de negócio."),
    tag: Optional[str] = Query(default=None, description="Filtrar por tag."),
    search: Optional[str] = Query(
        default=None, description="Busca textual por nome da tabela ou descrição."
    ),
    service: MetadataService = Depends(get_metadata_service),
) -> MetadataListResponse:
    settings = get_settings()
    effective_page_size = min(page_size or settings.default_page_size, settings.max_page_size)
    return await service.list_metadata(
        page=page,
        page_size=effective_page_size,
        owner=owner,
        domain=domain,
        tag=tag,
        search=search,
    )


@router.get(
    "/{metadata_id}",
    response_model=MetadataResponse,
    summary="Consultar detalhes de um metadado",
)
async def get_metadata(
    metadata_id: str,
    service: MetadataService = Depends(get_metadata_service),
) -> MetadataResponse:
    try:
        return await service.get_metadata(metadata_id)
    except InvalidMetadataIdException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MetadataNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put(
    "/{metadata_id}",
    response_model=MetadataResponse,
    summary="Atualizar um metadado existente",
)
async def update_metadata(
    metadata_id: str,
    payload: MetadataUpdateRequest,
    service: MetadataService = Depends(get_metadata_service),
) -> MetadataResponse:
    try:
        return await service.update_metadata(metadata_id, payload)
    except InvalidMetadataIdException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MetadataNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DuplicateMetadataException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/{metadata_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover um metadado",
)
async def delete_metadata(
    metadata_id: str,
    service: MetadataService = Depends(get_metadata_service),
) -> None:
    try:
        await service.delete_metadata(metadata_id)
    except InvalidMetadataIdException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MetadataNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
