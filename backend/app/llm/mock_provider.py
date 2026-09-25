import re
from typing import Dict, Any, Optional
from app.models.pydantic_models import ExtractedInformation

class MockLLMProvider:
    """
    Deterministic Mock LLM Provider with strict target field scoping across all 7 fields,
    flexible gifts parsing, and comprehensive additional wishes parsing.
    """

    @staticmethod
    def get_active_target_field(current_state: Dict[str, Any]) -> Optional[str]:
        data = current_state or {}
        if not data.get("full_name"):
            return "full_name"
        if not data.get("home_address"):
            return "home_address"
        if data.get("covers_worldwide_assets") is None:
            return "covers_worldwide_assets"
        if data.get("has_children") is None:
            return "has_children"
        
        if data.get("has_children") is True:
            children = data.get("children") or []
            if not children:
                return "children"

        ex = data.get("executor") or {}
        if not ex.get("name") or not ex.get("relationship"):
            return "executor"

        gifts = data.get("specific_gifts")
        if gifts is None or gifts == []:
            return "specific_gifts"

        if data.get("additional_wishes") is None:
            return "additional_wishes"

        return None

    @staticmethod
    def extract_information(user_message: str, current_state: Dict[str, Any], active_target: Optional[str] = None) -> ExtractedInformation:
        text = user_message.lower().strip()
        extracted = ExtractedInformation()
        
        if not active_target:
            active_target = MockLLMProvider.get_active_target_field(current_state)

        # Check certainty
        if any(w in text for w in ["maybe", "perhaps", "might", "not sure", "possibly", "thinking about"]):
            extracted.certainty = "uncertain"

        # Check generic responses
        is_short_no = text in ["no", "no.", "nope", "none", "nothing", "i don't", "don't have any", "no preferences", "no instructions", "no wishes"]
        is_short_yes = text in ["yes", "yes.", "yeah", "yep", "sure", "i do", "true"]

        # 1. Full Name
        name_match = re.search(r"(?:my name is|i am|call me|name:?)\s+([a-zA-Z\s]{2,40})", user_message, re.IGNORECASE)
        if name_match:
            candidate_name = name_match.group(1).strip().title()
            if not any(stop in candidate_name.lower() for stop in ["and", "my", "executor", "brother", "sister", "address", "worldwide", "children"]):
                extracted.full_name = candidate_name
        elif active_target == "full_name" and not is_short_no and not is_short_yes:
            words = user_message.strip().split()
            if 1 <= len(words) <= 4 and not any(kw in text for kw in ["yes", "no", "executor", "street", "road", "city", "gift", "wish", "brother", "sister", "children", "worldwide"]):
                extracted.full_name = user_message.strip().title()

        # 2. Home Address
        is_exec_or_kids_msg = any(k in text for k in ["executor", "appoint", "children", "childeren", "brother", "sister", "gift", "wish"])
        address_match = re.search(r"(?:live at|home address:?|my address is|address is)\s+([^,\.\n]+(?:,\s*[^,\.\n]+)*)", user_message, re.IGNORECASE)
        if address_match:
            addr = address_match.group(1).strip()
            addr = re.sub(r"^(?:is|at)\s+", "", addr, flags=re.IGNORECASE).strip()
            extracted.home_address = addr.title()
        elif active_target == "home_address" and not is_exec_or_kids_msg and not is_short_no and not is_short_yes:
            addr = user_message.strip()
            addr = re.sub(r"^(?:my address is|home address is|it is|is)\s+", "", addr, flags=re.IGNORECASE).strip()
            if len(addr) > 3:
                extracted.home_address = addr.title()

        # 3. Worldwide Assets
        if any(p in text for p in ["no worldwide", "not worldwide", "only uk", "local only", "domestic only", "without worldwide", "no global"]):
            extracted.covers_worldwide_assets = False
        elif any(p in text for p in ["worldwide", "global", "all countries", "everywhere", "international"]):
            extracted.covers_worldwide_assets = True
        elif active_target == "covers_worldwide_assets":
            if is_short_yes or "yes" in text or "worldwide" in text:
                extracted.covers_worldwide_assets = True
            elif is_short_no or "no" in text or "only primary" in text:
                extracted.covers_worldwide_assets = False

        # 4. Has Children & Children Names (Strictly scoped)
        has_explicit_kids_kw = any(p in text for p in ["children", "childeren", "kids", "daughter", "son"])
        if any(p in text for p in ["no children", "no childeren", "no kids", "don't have children", "do not have children", "without children"]):
            extracted.has_children = False
            extracted.children = []
        elif any(p in text for p in ["have children", "have kids", "my daughter", "my son", "my children", "have a son", "have a daughter"]):
            extracted.has_children = True
            names = re.findall(r"(?:daughter|son|child|kids?|named?)\s+([A-Z][a-z]+)", user_message)
            if names:
                extracted.children = list(set(names))
        elif active_target == "has_children" or (has_explicit_kids_kw and active_target not in ["specific_gifts", "additional_wishes"]):
            if is_short_no or "no" in text:
                extracted.has_children = False
                extracted.children = []
            elif is_short_yes or "yes" in text:
                extracted.has_children = True
        
        # Target Field is 'children' (asking for children names specifically)
        if active_target == "children" or (current_state.get("has_children") is True and not extracted.children and active_target not in ["executor", "specific_gifts", "additional_wishes"]):
            raw_input = user_message.strip()
            if not is_short_no:
                cleaned_text = re.sub(r"^(?:my\s+children\s+are|their\s+names\s+are|names:?|children:?)\s*", "", raw_input, flags=re.IGNORECASE)
                parts = re.split(r"[\,\;\&\s]+|\band\b", cleaned_text, flags=re.IGNORECASE)
                parsed_names = [p.strip().title() for p in parts if p.strip() and len(p.strip()) >= 2 and p.lower() not in ["and", "my", "the", "are"]]
                if parsed_names:
                    extracted.has_children = True
                    extracted.children = list(dict.fromkeys(parsed_names))

        # 5. Executor & Relationship
        comma_match = re.search(r"^([a-zA-Z\s]+)\s*[\,\\\/\-\(\)]\s*([a-zA-Z\s]+)$", user_message.strip())
        if comma_match and active_target not in ["children", "specific_gifts", "additional_wishes"]:
            part1, part2 = comma_match.group(1).strip(), comma_match.group(2).strip()
            relations = ["brother", "sister", "friend", "spouse", "wife", "husband", "son", "daughter", "lawyer", "attorney", "father", "mother", "cousin", "uncle", "aunt"]
            
            if part1.lower() in relations:
                extracted.executor_relationship = part1.lower()
                extracted.executor_name = part2.title()
            elif part2.lower() in relations:
                extracted.executor_name = part1.title()
                extracted.executor_relationship = part2.lower()
            elif active_target == "executor":
                extracted.executor_name = part1.title()
                extracted.executor_relationship = part2.lower()

        if active_target == "executor" or any(k in text for k in ["executor", "appoint"]):
            if not extracted.executor_name:
                exec_match = re.search(r"(?:executor|appoint)\s+(?:is|would be|should be)?\s*(?:my\s+([a-zA-Z]+)\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", user_message)
                if exec_match:
                    rel, name = exec_match.groups()
                    if name and name.lower() not in ["executor", "brother", "sister", "friend", "my"]:
                        extracted.executor_name = name.title()
                    if rel:
                        extracted.executor_relationship = rel.lower()

            if not extracted.executor_relationship:
                for rel in ["brother", "sister", "friend", "spouse", "wife", "husband", "son", "daughter", "lawyer", "attorney", "father", "mother", "cousin", "uncle", "aunt"]:
                    if re.search(r"\b" + rel + r"\b", text):
                        extracted.executor_relationship = rel
                        if not extracted.executor_name:
                            rel_name_match = re.search(r"\b" + rel + r"\s+([A-Z][a-z]+)", user_message)
                            if rel_name_match:
                                extracted.executor_name = rel_name_match.group(1).title()

        # 6. Specific Gifts
        if active_target == "specific_gifts" or any(k in text for k in ["gift", "bequest", "leave", "give"]):
            if any(p in text for p in ["no gifts", "no specific gifts", "no bequests", "no", "nope", "nothing", "none"]):
                extracted.specific_gifts = ["None specified"]
            else:
                gifts_match = re.search(r"(?:give|leave|gift)\s+(?:my\s+)?([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+)", user_message, re.IGNORECASE)
                if gifts_match:
                    item, recipient = gifts_match.groups()
                    extracted.specific_gifts = [f"{item.strip().title()} to {recipient.strip().title()}"]
                else:
                    cleaned_gift = re.sub(r"^(?:yes\s+gifts?\s+like\s+|yes\s+gifts?\s+|yes\s+|gifts?:?\s*|i\s+want\s+to\s+leave\s*)", "", user_message.strip(), flags=re.IGNORECASE).strip()
                    if cleaned_gift:
                        extracted.specific_gifts = [cleaned_gift.title()]

        # 7. Additional Wishes (Comprehensive target parsing)
        if active_target == "additional_wishes" or any(k in text for k in ["wish", "funeral", "cremation", "burial", "instruction"]):
            if any(p in text for p in ["no wishes", "no additional wishes", "no instructions", "no", "nope", "nothing", "none"]):
                extracted.additional_wishes = "None specified"
            else:
                cleaned_wish = re.sub(r"^(?:yes\s+wishes?\s+like\s+|yes\s+wishes?\s+|yes\s+|wishes?:?\s*|my\s+wish\s+is\s+|i\s+wish\s+)", "", user_message.strip(), flags=re.IGNORECASE).strip()
                if cleaned_wish:
                    extracted.additional_wishes = cleaned_wish.capitalize()
                elif is_short_yes:
                    extracted.additional_wishes = "Yes"

        return extracted

    @staticmethod
    def generate_response(missing_fields: list, updated_fields: list, uncertain_fields: list, conflict_fields: list) -> str:
        if conflict_fields:
            fields_str = ', '.join([f.replace('_', ' ') for f in conflict_fields])
            return f"I noticed a contradiction regarding your {fields_str}. Please review the alert to resolve which value you would like to keep."

        if uncertain_fields:
            field = uncertain_fields[0]
            field_display = field.replace("_", " ")
            return f"You mentioned something about your {field_display}. Could you please confirm if this is your final decision?"

        if not missing_fields:
            return "Thank you! All required information for your Personal Wishes Document has been collected and confirmed. You can preview, edit, or export your document now."

        next_field = missing_fields[0]

        questions = {
            "full_name": "What is your full legal name?",
            "home_address": "What is your home address?",
            "covers_worldwide_assets": "Does this Personal Wishes Document cover your worldwide assets, or only assets in your primary country?",
            "has_children": "Do you have any children?",
            "children": "Please provide the names of your children.",
            "executor": "Who would you like to appoint as your executor, and what is their relationship to you?",
            "specific_gifts": "Are there any specific gifts or personal belongings you would like to leave to specific individuals?",
            "additional_wishes": "Do you have any additional wishes or instructions (e.g., funeral preferences)?"
        }

        prefix = ""
        if updated_fields:
            captured_names = [f.replace('_', ' ') for f in updated_fields]
            prefix = f"Got it! Updated your {', '.join(captured_names)}. "

        return prefix + questions.get(next_field, "Is there anything else you would like to specify?")
