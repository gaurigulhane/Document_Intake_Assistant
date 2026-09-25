from typing import Dict, Any

class DocumentGenerator:
    @staticmethod
    def generate_draft(data: Dict[str, Any]) -> str:
        full_name = data.get("full_name") or "[Full Name Not Provided]"
        home_address = data.get("home_address") or "[Address Not Provided]"
        
        worldwide_val = data.get("covers_worldwide_assets")
        if worldwide_val is True:
            worldwide_str = "Yes - Covers all assets worldwide"
        elif worldwide_val is False:
            worldwide_str = "No - Applies only to assets in primary jurisdiction"
        else:
            worldwide_str = "[Not Specified]"

        has_kids = data.get("has_children")
        children = data.get("children") or []
        if has_kids is True:
            children_str = f"Yes ({', '.join(children)})" if children else "Yes (Names not specified)"
        elif has_kids is False:
            children_str = "No children"
        else:
            children_str = "[Not Specified]"

        executor = data.get("executor") or {}
        exec_name = executor.get("name") or "[Name Not Specified]"
        exec_rel = executor.get("relationship") or "[Relationship Not Specified]"
        executor_str = f"{exec_name} ({exec_rel})"

        gifts = data.get("specific_gifts") or []
        gifts_str = "\n".join([f"  • {g}" for g in gifts]) if gifts else "  • None specified"

        wishes = data.get("additional_wishes") or "None specified"

        doc = f"""================================================================================
                       PERSONAL WISHES DOCUMENT
================================================================================
               *** FICTIONAL DOCUMENT — NOT LEGAL ADVICE ***

1. PERSONAL DETAILS
--------------------------------------------------------------------------------
Full Name:     {full_name}
Home Address:  {home_address}

2. ASSET SCOPE
--------------------------------------------------------------------------------
Worldwide Assets: {worldwide_str}

3. FAMILY DETAILS
--------------------------------------------------------------------------------
Children: {children_str}

4. EXECUTOR APPOINTMENT
--------------------------------------------------------------------------------
Appointed Executor: {executor_str}

5. SPECIFIC GIFTS & REQUESTS
--------------------------------------------------------------------------------
{gifts_str}

6. ADDITIONAL WISHES & INSTRUCTIONS
--------------------------------------------------------------------------------
{wishes}

================================================================================
THIS DOCUMENT IS GENERATED AS A FICTIONAL DEMONSTRATION AND DOES NOT
CONSTITUTE LEGAL ADVICE OR A BINDING LEGAL INSTRUMENT.
================================================================================
"""
        return doc
