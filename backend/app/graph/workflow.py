from typing import Dict, Any, List, TypedDict
from app.llm.service import llm_service
from app.models.pydantic_models import FieldStatusEnum

# Required fields for Personal Wishes Document
REQUIRED_FIELDS = [
    "full_name",
    "home_address",
    "covers_worldwide_assets",
    "has_children",
    "executor"
]

TOTAL_ITEMS_COUNT = 7  # name, address, worldwide, children, executor, gifts, wishes

class GraphState(TypedDict):
    session_id: str
    user_message: str
    current_state_data: Dict[str, Any]
    current_statuses: Dict[str, Any]
    extracted_info: Any
    conflicts_detected: List[Dict[str, Any]]
    updated_fields: List[str]
    uncertain_fields: List[str]
    missing_fields: List[str]
    completion_percentage: float
    confirmed_count: int
    total_required_count: int
    assistant_response: str

def receive_message_node(state: GraphState) -> GraphState:
    return state

def extract_information_node(state: GraphState) -> GraphState:
    extracted = llm_service.extract_information(
        state["user_message"],
        state["current_state_data"]
    )
    state["extracted_info"] = extracted
    return state

def validate_extraction_node(state: GraphState) -> GraphState:
    # Basic Pydantic structural validation is handled in extracted_info schema
    return state

def check_conflicts_node(state: GraphState) -> GraphState:
    extracted = state["extracted_info"]
    current_data = state["current_state_data"]
    current_statuses = state["current_statuses"]
    conflicts = []

    # Helper to check conflict
    def check_field(field_name: str, new_val: Any, current_val: Any):
        if new_val is not None:
            status = current_statuses.get(field_name, FieldStatusEnum.UNKNOWN)
            if status == FieldStatusEnum.CONFIRMED and current_val is not None:
                if str(new_val).strip().lower() != str(current_val).strip().lower():
                    conflicts.append({
                        "field": field_name,
                        "old_value": str(current_val),
                        "new_value": str(new_val)
                    })

    if extracted:
        check_field("full_name", extracted.full_name, current_data.get("full_name"))
        check_field("home_address", extracted.home_address, current_data.get("home_address"))
        check_field("covers_worldwide_assets", extracted.covers_worldwide_assets, current_data.get("covers_worldwide_assets"))
        check_field("has_children", extracted.has_children, current_data.get("has_children"))
        
        # Executor check
        if extracted.executor_name or extracted.executor_relationship:
            current_exec = current_data.get("executor") or {}
            old_exec_str = f"{current_exec.get('name', '')} ({current_exec.get('relationship', '')})".strip()
            new_exec_str = f"{extracted.executor_name or current_exec.get('name', '')} ({extracted.executor_relationship or current_exec.get('relationship', '')})".strip()
            
            exec_status = current_statuses.get("executor", FieldStatusEnum.UNKNOWN)
            if exec_status == FieldStatusEnum.CONFIRMED and old_exec_str and old_exec_str != new_exec_str:
                conflicts.append({
                    "field": "executor",
                    "old_value": old_exec_str,
                    "new_value": new_exec_str
                })

    state["conflicts_detected"] = conflicts
    return state

def update_state_node(state: GraphState) -> GraphState:
    extracted = state["extracted_info"]
    data = dict(state["current_state_data"])
    statuses = dict(state["current_statuses"])
    conflicts = state["conflicts_detected"]
    conflicted_fields = {c["field"] for c in conflicts}

    updated = []
    uncertain = []

    if extracted:
        is_uncertain = extracted.certainty in ["uncertain", "ambiguous"]
        target_status = FieldStatusEnum.NEEDS_CONFIRMATION if is_uncertain else FieldStatusEnum.CONFIRMED

        # 1. Full name
        if extracted.full_name is not None and "full_name" not in conflicted_fields:
            data["full_name"] = extracted.full_name
            statuses["full_name"] = target_status
            updated.append("full_name")
            if is_uncertain: uncertain.append("full_name")

        # 2. Address
        if extracted.home_address is not None and "home_address" not in conflicted_fields:
            data["home_address"] = extracted.home_address
            statuses["home_address"] = target_status
            updated.append("home_address")
            if is_uncertain: uncertain.append("home_address")

        # 3. Assets
        if extracted.covers_worldwide_assets is not None and "covers_worldwide_assets" not in conflicted_fields:
            data["covers_worldwide_assets"] = extracted.covers_worldwide_assets
            statuses["covers_worldwide_assets"] = target_status
            updated.append("covers_worldwide_assets")
            if is_uncertain: uncertain.append("covers_worldwide_assets")

        # 4. Children
        if extracted.has_children is not None and "has_children" not in conflicted_fields:
            data["has_children"] = extracted.has_children
            statuses["has_children"] = target_status
            updated.append("has_children")
            if extracted.has_children and extracted.children:
                data["children"] = extracted.children
                statuses["children"] = target_status
            elif not extracted.has_children:
                data["children"] = []
                statuses["children"] = FieldStatusEnum.CONFIRMED

        # 5. Executor
        if (extracted.executor_name or extracted.executor_relationship) and "executor" not in conflicted_fields:
            exec_dict = data.get("executor") or {}
            if extracted.executor_name:
                exec_dict["name"] = extracted.executor_name
            if extracted.executor_relationship:
                exec_dict["relationship"] = extracted.executor_relationship
            data["executor"] = exec_dict
            statuses["executor"] = target_status
            updated.append("executor")

        # 6. Gifts
        if extracted.specific_gifts and "specific_gifts" not in conflicted_fields:
            existing_gifts = data.get("specific_gifts") or []
            data["specific_gifts"] = list(set(existing_gifts + extracted.specific_gifts))
            statuses["specific_gifts"] = target_status
            updated.append("specific_gifts")

        # 7. Wishes
        if extracted.additional_wishes is not None and "additional_wishes" not in conflicted_fields:
            data["additional_wishes"] = extracted.additional_wishes
            statuses["additional_wishes"] = target_status
            updated.append("additional_wishes")

    # Mark conflict statuses
    for c in conflicts:
        statuses[c["field"]] = FieldStatusEnum.CONFLICTED

    state["current_state_data"] = data
    state["current_statuses"] = statuses
    state["updated_fields"] = updated
    state["uncertain_fields"] = uncertain
    return state

def calculate_completion_node(state: GraphState) -> GraphState:
    statuses = state["current_statuses"]
    data = state["current_state_data"]
    
    confirmed_items = 0
    all_fields = ["full_name", "home_address", "covers_worldwide_assets", "has_children", "executor", "specific_gifts", "additional_wishes"]
    
    for f in all_fields:
        st = statuses.get(f, FieldStatusEnum.UNKNOWN)
        if st in [FieldStatusEnum.CONFIRMED, FieldStatusEnum.CAPTURED]:
            if f == "executor":
                ex = data.get("executor") or {}
                if ex.get("name") and ex.get("relationship"):
                    confirmed_items += 1
            elif f == "children":
                if data.get("has_children") is False or (data.get("has_children") and data.get("children")):
                    confirmed_items += 1
            else:
                if data.get(f) is not None:
                    confirmed_items += 1

    total = len(all_fields)
    pct = round((confirmed_items / total) * 100.0, 1)

    state["confirmed_count"] = confirmed_items
    state["total_required_count"] = total
    state["completion_percentage"] = pct
    return state

def check_missing_information_node(state: GraphState) -> GraphState:
    statuses = state["current_statuses"]
    data = state["current_state_data"]
    missing = []

    fields_check = [
        "full_name",
        "home_address",
        "covers_worldwide_assets",
        "has_children",
        "executor",
        "specific_gifts",
        "additional_wishes"
    ]

    for f in fields_check:
        st = statuses.get(f, FieldStatusEnum.UNKNOWN)
        if st in [FieldStatusEnum.UNKNOWN, FieldStatusEnum.NEEDS_CONFIRMATION]:
            missing.append(f)
        elif f == "has_children" and data.get("has_children") is True and not data.get("children"):
            missing.append("children")
        elif f == "executor":
            ex = data.get("executor") or {}
            if not ex.get("name") or not ex.get("relationship"):
                if f not in missing:
                    missing.append("executor")

    state["missing_fields"] = missing
    return state

def generate_next_question_node(state: GraphState) -> GraphState:
    conflict_fields = [c["field"] for c in state.get("conflicts_detected", [])]
    response = llm_service.generate_response(
        missing_fields=state["missing_fields"],
        updated_fields=state["updated_fields"],
        uncertain_fields=state["uncertain_fields"],
        conflict_fields=conflict_fields
    )
    state["assistant_response"] = response
    return state

def run_intake_workflow(initial_state: GraphState) -> GraphState:
    state = receive_message_node(initial_state)
    state = extract_information_node(state)
    state = validate_extraction_node(state)
    state = check_conflicts_node(state)
    state = update_state_node(state)
    state = calculate_completion_node(state)
    state = check_missing_information_node(state)
    state = generate_next_question_node(state)
    return state
