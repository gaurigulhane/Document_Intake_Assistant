from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import ConflictModel, StructuredStateModel
from app.models.pydantic_models import ConflictItem, ConflictResolveRequest, StructuredStateResponse, FieldStatusEnum
from app.api.endpoints.sessions import format_state_response

router = APIRouter(prefix="/sessions", tags=["Conflicts"])

@router.get("/{session_id}/conflicts", response_model=List[ConflictItem])
def get_conflicts(session_id: str, db: Session = Depends(get_db)):
    conflicts = db.query(ConflictModel).filter(ConflictModel.session_id == session_id).all()
    return [
        ConflictItem(
            id=c.id,
            field=c.field,
            old_value=c.old_value,
            new_value=c.new_value,
            status=c.status,
            created_at=c.created_at.isoformat()
        ) for c in conflicts
    ]

@router.post("/{session_id}/conflicts/{conflict_id}/resolve", response_model=StructuredStateResponse)
def resolve_conflict(
    session_id: str,
    conflict_id: str,
    body: ConflictResolveRequest,
    db: Session = Depends(get_db)
):
    conflict = db.query(ConflictModel).filter(
        ConflictModel.id == conflict_id,
        ConflictModel.session_id == session_id
    ).first()

    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")

    if conflict.status == "resolved":
        raise HTTPException(status_code=400, detail="Conflict already resolved")

    # Determine chosen value
    chosen_val = conflict.old_value if body.choice == "keep_old" else conflict.new_value

    conflict.status = "resolved"
    conflict.resolved_value = chosen_val

    # Apply to structured state
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    if state_record:
        state_json = dict(state_record.state_json)
        data = dict(state_json.get("data", {}))
        statuses = dict(state_json.get("statuses", {}))

        field = conflict.field
        if field == "executor":
            # format as name/rel
            ex = data.get("executor") or {}
            ex["name"] = chosen_val
            data["executor"] = ex
        elif field in data:
            data[field] = chosen_val

        statuses[field] = FieldStatusEnum.CONFIRMED.value

        state_json["data"] = data
        state_json["statuses"] = statuses
        state_record.state_json = state_json

    db.commit()

    return format_state_response(session_id, state_record.state_json)
