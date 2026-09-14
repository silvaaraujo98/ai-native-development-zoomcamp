from fastapi import APIRouter

from ..models import ComponentDefault
from ..store import store


router = APIRouter(tags=["Metadata"])


@router.get("/component-defaults", response_model=dict[str, ComponentDefault])
def component_defaults() -> dict[str, ComponentDefault]:
    return store.component_defaults
