from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import StructuredStateModel, SessionModel
from app.models.pydantic_models import (
    StructuredStateResponse, DirectStateUpdateRequest, FieldStatusEnum, WishesStateData
)
from app.graph.workflow import TOTAL_ITEMS_COUNT
from app.api.endpoints.sessions import format_state_response

router = APIRouter(prefix="/sessions", tags=["Structured State"])

@router.get("/{session_id}/state", response_model=StructuredStateResponse)
def get_state(session_id: str, db: Session = Depends(get_db)):
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    if not state_record:
        raise HTTPException(status_code=404, detail="Structured state not found")

    return format_state_response(session_id, state_record.state_json)

@router.patch("/{session_id}/state", response_model=StructuredStateResponse)
def update_state_directly(session_id: str, body: DirectStateUpdateRequest, db: Session = Depends(get_db)):
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    if not state_record:
        raise HTTPException(status_code=404, detail="Structured state not found")

    state_json = dict(state_record.state_json)
    data = dict(state_json.get("data", {}))
    statuses = dict(state_json.get("statuses", {}))

    field = body.field
    val = body.value

    if field == "executor_name":
        ex = data.get("executor") or {}
        ex["name"] = str(val) if val else None
        data["executor"] = ex
        statuses["executor"] = FieldStatusEnum.CONFIRMED.value
    elif field == "executor_relationship":
        ex = data.get("executor") or {}
        ex["relationship"] = str(val) if val else None
        data["executor"] = ex
        statuses["executor"] = FieldStatusEnum.CONFIRMED.value
    elif field in data:
        data[field] = val
        statuses[field] = FieldStatusEnum.CONFIRMED.value
    else:
        raise HTTPException(status_code=400, detail=f"Invalid field name '{field}'")

    # Recalculate completion
    confirmed_items = 0
    all_fields = ["full_name", "home_address", "covers_worldwide_assets", "has_children", "executor", "specific_gifts", "additional_wishes"]
    for f in all_fields:
        st = statuses.get(f, "unknown")
        if st in ["confirmed", "captured"]:
            if f == "executor":
                ex = data.get("executor") or {}
                if ex.get("name") and ex.get("relationship"):
                    confirmed_items += 1
            else:
                if data.get(f) is not None:
                    confirmed_items += 1

    pct = round((confirmed_items / TOTAL_ITEMS_COUNT) * 100.0, 1)

    state_json["data"] = data
    state_json["statuses"] = statuses
    state_json["confirmed_count"] = confirmed_items
    state_json["completion_percentage"] = pct

    state_record.state_json = state_json
    db.commit()

    return format_state_response(session_id, state_json)
