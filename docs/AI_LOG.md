# AI Development Log

**Candidate:** Gauri Nitin Gulhane  
**Technical Test:** LLM Application — Document Intake Assistant  
**Date:** September 2026  

---

## 1. AI Tools & Assistants Used
- **ChatGPT (GPT-4o)**: Used for architecture brainstorming, Pydantic schema validation design, and prompt engineering strategy.
- **Claude 3.5 Sonnet**: Used for designing the LangGraph workflow state machine, conflict detection logic, and ReportLab PDF layout rules.
- **GitHub Copilot / Cursor**: Used for inline autocompletion, React hooks boilerplate, and FastAPI route structure.

---

## 2. Key Prompts & Iterations

### Prompt 1: LangGraph Workflow Design
> *"Design a LangGraph state graph for a document intake assistant that extracts user information, validates it with Pydantic, checks if any newly extracted value contradicts confirmed values, updates structured state, and calculates document completion percentage."*

- **Iteration Outcome**: Initial graph draft attempted to store state directly inside conversation messages. I refactored it so that `StructuredStateModel` is strictly isolated as the source of truth, separate from raw message logs.

### Prompt 2: Robust Extraction & Ambiguity Handling
> *"How can an LLM extraction function handle uncertainty in user messages, such as 'My executor is maybe my brother James'?"*

- **Iteration Outcome**: Added a `certainty` flag (`certain`, `uncertain`, `ambiguous`) in the `ExtractedInformation` Pydantic model. When uncertainty is detected, the field status is marked as `needs_confirmation` rather than `confirmed`.

### Prompt 3: Deterministic Fallback Mock Provider
> *"Create a deterministic mock LLM provider that extracts fields using regex and natural language heuristics so the backend can run and pass all automated unit tests without requiring an active OpenAI or Gemini API key."*

- **Iteration Outcome**: Implemented `MockLLMProvider` which extracts full names, home addresses, worldwide asset preferences, children info, executor details, gifts, and wishes. Fallback kicks in automatically if no API key is specified in `.env`.

---

## 3. AI Suggestions Questioned & Corrected

1. **Silent Overwriting of Conflicting Fields**:
   - *AI Suggestion*: Automatically overwrite existing state values with the latest extracted entities from user chat.
   - *My Correction*: Rejected silent overwrite. Implemented explicit conflict detection (`check_conflicts_node`). When a user contradicts previously confirmed data, a conflict record is created (`status="conflicted"`) and an interactive UI modal allows the user to explicitly choose `Keep Previous` vs `Use New Value`.

2. **PDF Disclaimer Labeling**:
   - *AI Suggestion*: Render the document header as "Official Personal Wishes Will & Testament".
   - *My Correction*: Updated header styling to explicitly enforce the mandatory label `FICTIONAL DOCUMENT — NOT LEGAL ADVICE` across all document drafts and ReportLab PDF exports.

3. **Database Threading in Pytest**:
   - *AI Suggestion*: Use default SQLite in-memory setup in Pytest fixtures.
   - *My Correction*: SQLite in-memory standard connections create isolated databases per thread, breaking multi-threaded FastAPI test client calls. Configured `StaticPool` in `conftest.py` to ensure shared test memory state across test routes.

---

## 4. Key Engineering Decisions
- **Source of Truth Separation**: State is held in structured JSON tables, not unparsed text history.
- **Direct Editing & Multi-Turn Synergy**: Users can either chat to fill in missing details or click `[Edit]` beside any field in the live sidebar preview to make direct adjustments.
- **Zero Lock-in LLM Architecture**: Pluggable LLM provider architecture supporting Gemini, OpenAI, Anthropic, or Mock modes.
