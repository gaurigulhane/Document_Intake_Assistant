from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import SessionModel, MessageModel, StructuredStateModel, ConflictModel
from app.models.pydantic_models import (
    SessionResponse, MessageCreateRequest, MessageResponse, StructuredStateResponse, WishesStateData, FieldStatusEnum
)
from app.graph.workflow import run_intake_workflow, GraphState, TOTAL_ITEMS_COUNT
import uuid

router = APIRouter(prefix="/sessions", tags=["Sessions"])

def format_state_response(session_id: str, state_json: dict) -> StructuredStateResponse:
    raw_data = state_json.get("data", {})
    raw_statuses = state_json.get("statuses", {})

    wishes_data = WishesStateData(**raw_data)
    statuses = {k: FieldStatusEnum(v) for k, v in raw_statuses.items()}

    confirmed_count = state_json.get("confirmed_count", 0)
    pct = state_json.get("completion_percentage", 0.0)

    return StructuredStateResponse(
        session_id=session_id,
        data=wishes_data,
        statuses=statuses,
        completion_percentage=pct,
        confirmed_count=confirmed_count,
        total_required_count=TOTAL_ITEMS_COUNT
    )

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(db: Session = Depends(get_db)):
    session = SessionModel()
    db.add(session)
    db.flush()

    initial_message = MessageModel(
        session_id=session.id,
        role="assistant",
        content="Hello! I am your Document Intake Assistant. I can help you compile your Personal Wishes Document by asking a few simple questions. What is your full legal name?"
    )
    db.add(initial_message)

    initial_state_json = {
        "data": {
            "full_name": None,
            "home_address": None,
            "covers_worldwide_assets": None,
            "has_children": None,
            "children": [],
            "executor": {"name": None, "relationship": None},
            "specific_gifts": [],
            "additional_wishes": None
        },
        "statuses": {
            "full_name": "unknown",
            "home_address": "unknown",
            "covers_worldwide_assets": "unknown",
            "has_children": "unknown",
            "children": "unknown",
            "executor": "unknown",
            "specific_gifts": "unknown",
            "additional_wishes": "unknown"
        },
        "confirmed_count": 0,
        "completion_percentage": 0.0
    }

    state_record = StructuredStateModel(
        session_id=session.id,
        state_json=initial_state_json
    )
    db.add(state_record)
    db.commit()
    db.refresh(session)

    msgs = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat()
        ) for m in session.messages
    ]

    return SessionResponse(
        id=session.id,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        messages=msgs,
        structured_state=format_state_response(session.id, initial_state_json)
    )

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msgs = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat()
        ) for m in session.messages
    ]

    state_json = session.structured_state.state_json if session.structured_state else {}

    return SessionResponse(
        id=session.id,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        messages=msgs,
        structured_state=format_state_response(session.id, state_json)
    )

@router.post("/{session_id}/messages", response_model=SessionResponse)
def send_message(session_id: str, body: MessageCreateRequest, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save User message
    user_msg = MessageModel(
        session_id=session_id,
        role="user",
        content=body.content
    )
    db.add(user_msg)

    # Fetch current state
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    current_json = state_record.state_json if state_record else {}
    current_data = current_json.get("data", {})
    current_statuses = current_json.get("statuses", {})

    initial_graph_state: GraphState = {
        "session_id": session_id,
        "user_message": body.content,
        "current_state_data": current_data,
        "current_statuses": current_statuses,
        "extracted_info": None,
        "conflicts_detected": [],
        "updated_fields": [],
        "uncertain_fields": [],
        "missing_fields": [],
        "completion_percentage": current_json.get("completion_percentage", 0.0),
        "confirmed_count": current_json.get("confirmed_count", 0),
        "total_required_count": TOTAL_ITEMS_COUNT,
        "assistant_response": ""
    }

    # Execute LangGraph Workflow
    result = run_intake_workflow(initial_graph_state)

    # Save Assistant Response Message
    assistant_msg = MessageModel(
        session_id=session_id,
        role="assistant",
        content=result["assistant_response"]
    )
    db.add(assistant_msg)

    # Save conflicts if detected
    for conf in result["conflicts_detected"]:
        conflict_rec = ConflictModel(
            session_id=session_id,
            field=conf["field"],
            old_value=conf["old_value"],
            new_value=conf["new_value"],
            status="unresolved"
        )
        db.add(conflict_rec)

    # Update State JSON
    new_state_json = {
        "data": result["current_state_data"],
        "statuses": result["current_statuses"],
        "confirmed_count": result["confirmed_count"],
        "completion_percentage": result["completion_percentage"]
    }
    state_record.state_json = new_state_json

    db.commit()
    db.refresh(session)

    msgs = [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat()
        ) for m in session.messages
    ]

    return SessionResponse(
        id=session.id,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        messages=msgs,
        structured_state=format_state_response(session.id, new_state_json)
    )
