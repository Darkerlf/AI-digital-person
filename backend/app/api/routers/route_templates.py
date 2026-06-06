from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.route_template import RouteTemplateCreate, RouteTemplateRead, RouteTemplateUpdate
from app.services.route_template_service import RouteTemplateService

router = APIRouter(prefix="/route-templates", tags=["route-templates"])


@router.post("", response_model=RouteTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: RouteTemplateCreate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return RouteTemplateService(db).create(payload, current_user=current_user)


@router.get("")
def list_templates(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": RouteTemplateService(db).list_all()}


@router.get("/{template_id}", response_model=RouteTemplateRead)
def get_template(
    template_id: int,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return RouteTemplateService(db).get_read(template_id)


@router.put("/{template_id}", response_model=RouteTemplateRead)
def update_template(
    template_id: int,
    payload: RouteTemplateUpdate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return RouteTemplateService(db).update(template_id, payload, current_user=current_user)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    RouteTemplateService(db).delete(template_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
