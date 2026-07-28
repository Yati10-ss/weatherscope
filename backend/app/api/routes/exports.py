from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, get_export_service
from app.services.export_service import ExportFile, ExportService


router = APIRouter(prefix="/exports", tags=["Exports"])


def _download_response(export_file: ExportFile) -> Response:
    return Response(
        content=export_file.content,
        media_type=export_file.media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{export_file.filename}"'
            )
        },
    )


@router.get(
    "/weather-searches.json",
    summary="Export all saved searches as JSON",
    description="Downloads all persisted weather searches and their daily rows.",
)
def export_all_json(
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    return _download_response(service.all_json(session=session))


@router.get(
    "/weather-searches.csv",
    summary="Export all saved searches as CSV",
    description="Downloads one flattened CSV row per saved weather day.",
)
def export_all_csv(
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    return _download_response(service.all_csv(session=session))


@router.get(
    "/weather-searches/{search_id}.json",
    summary="Export one saved search as JSON",
    responses={404: {"description": "The saved weather search does not exist."}},
)
def export_one_json(
    search_id: Annotated[int, Path(ge=1)],
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    return _download_response(
        service.one_json(session=session, search_id=search_id)
    )


@router.get(
    "/weather-searches/{search_id}.csv",
    summary="Export one saved search as CSV",
    responses={404: {"description": "The saved weather search does not exist."}},
)
def export_one_csv(
    search_id: Annotated[int, Path(ge=1)],
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ExportService, Depends(get_export_service)],
) -> Response:
    return _download_response(
        service.one_csv(session=session, search_id=search_id)
    )
