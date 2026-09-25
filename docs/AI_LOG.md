# AI Development & Engineering Decision Log

**Candidate:** Gauri Nitin Gulhane  
**Technical Test:** LLM Application — Document Intake Assistant  
**Repository:** [github.com/gaurigulhane/Document_Intake_Assistant](https://github.com/gaurigulhane/Document_Intake_Assistant)  
**Date:** September 2026  

---

## Overview

This document provides a transparent, chronological record of the engineering progression, architectural choices, prompt instructions, AI tool iterations, bug resolutions, and testing milestones throughout the development of the **Document Intake Assistant**.

---

## AI Tools & Frameworks Used
- **ChatGPT (GPT-4o)**: Used for initial architecture design, Pydantic schema validation patterns, and prompt engineering strategy.
- **Claude 3.5 Sonnet**: Used for designing the LangGraph workflow state machine, conflict detection logic, and ReportLab PDF layout rules.
- **GitHub Copilot / Cursor**: Used for inline autocompletion, React hooks boilerplate, and FastAPI route structure.

---

## Development Trajectory by Phase

### Phase 1 — Architecture & System Design
- **Objective**: Establish core architectural philosophy and component boundary separations.
- **Key Decisions**:
  - Adopted rule: *The LLM is an extraction engine, never the source of truth.*
  - Decoupled application state (`WishesState`) from conversation history (`MessageModel`).
  - Defined a responsive 2-panel split UI layout (Interactive Chat + Live Structured State & Preview).
- **Prompt / Direction**: Senior engineer review proposing data flow, API design, folder structure, and edge case risk analysis before writing code.

---

### Phase 2 — Pydantic Schemas & Structured State
- **Objective**: Create strongly typed contracts for structured state, candidate LLM extractions, session tracking, and REST payloads.
- **Key Decisions**:
  - Replaced unstructured dictionaries with typed `ExtractedInformation` and `WishesStateData`.
  - Added field status enums (`unknown`, `captured`, `needs_confirmation`, `confirmed`, `conflicted`).
  - Sanitized string inputs to strip leading/trailing whitespace.
- **Tests Created**: `tests/test_extraction.py`.
- **Result**: Passed.

---

### Phase 3 — State Engine & Deterministic Validation
- **Objective**: Implement in-memory state tracking and deterministic `ValidationEngine`.
- **Key Decisions**:
  - Single-turn transactional updates: candidate fields must pass validation rules before modifying structured state.
  - Implemented conflict detection: contradictory input (e.g. declaring no children, then naming a daughter) is flagged as `conflicted` without silently overwriting confirmed state.
  - Preserved partial executor information (`name` without `relationship` and vice versa).
- **Tests Created**: `tests/test_state.py` and `tests/test_conflicts.py`.
- **Result**: All passed.

---

### Phase 4 — Fallback Mock LLM & Provider Abstraction
- **Objective**: Create abstract `LLMService` contract and deterministic `MockLLMProvider`.
- **Key Decisions**:
  - Designed `MockLLMProvider` to handle natural language extraction without external API keys, ensuring 100% offline testability.
  - Implemented active-target field scoping so generic answers (`"no"`, `"yes"`, `"none"`) only apply to the question currently being asked.
- **Tests Created**: Parameterized tests in `tests/test_extraction.py`.
- **Result**: All passed.

---

### Phase 5 — LangGraph Workflow Orchestration
- **Objective**: Implement LangGraph state machine mediating Session, LLM, Validation, and State layers.
- **Key Decisions**:
  - Graph flow: `receive_message` → `extract_information` → `validate_extraction` → `check_conflicts` → `update_state` → `calculate_completion` → `check_missing_information` → `generate_next_question`.
  - Safe error boundaries preventing state corruption during service failures.
- **Tests Created**: Integration pipeline tests in Pytest.
- **Result**: All passed.

---

### Phase 6 — Document Draft & PDF Generation Engine
- **Objective**: Implement `DocumentGenerator` and `PDFExporter` rendering the draft Personal Wishes Document.
- **Key Decisions**:
  - Implemented text document generation as a pure Python template renderer (zero LLM token usage, zero formatting hallucinations).
  - Built ReportLab PDF engine (`PDFExporter`) producing downloadable styled PDF files.
  - Enforced mandatory legal disclaimers (*FICTIONAL DOCUMENT*, *NOT LEGAL ADVICE*).
- **Tests Created**: `tests/test_document.py` and `tests/test_pdf.py`.
- **Result**: All passed.

---

### Phase 7 — FastAPI REST API Layer
- **Objective**: Expose application capabilities via REST endpoints (`/api/sessions`, `/api/sessions/{id}/messages`, `/api/sessions/{id}/state`, `/api/sessions/{id}/conflicts`, `/api/sessions/{id}/document`, `/api/sessions/{id}/email`).
- **Key Decisions**:
  - Implemented clean exception handlers returning structured JSON payloads.
  - Added CORS middleware with explicit development origins.
- **Result**: All passed.

---

### Phase 8 — React 18 + Vite Frontend
- **Objective**: Build a responsive 2-panel split UI with real-time state preview.
- **Key Decisions**:
  - Real-time synchronization: every chat turn updates Chat stream, State cards, Progress bar ($0\% - 100\%$), and Draft Document viewer.
  - Direct UI State Editing: added `[Edit]` buttons beside fields allowing direct `PATCH` updates.
  - Glassmorphic dark theme CSS design system with Lucide icons.

---

### Phase 9 — Email Service & SMTP Integration
- **Objective**: Implement optional email dispatch sending PDF attachments.
- **Key Decisions**:
  - Implemented `EmailService` using Python `smtplib` / `email.mime`.
  - Configured STARTTLS (Port 587) with fallback to SMTP_SSL (Port 465) for Google App Password support.
- **Result**: Functional email delivery.

---

### Phase 10 — Real Bug Fixes & Refinements
- **Real Bugs Discovered & Resolved**:
  1. **Cross-Field Triggering on "No"**: Plain `"no"` to worldwide assets previously updated `has_children`, `specific_gifts`, and `additional_wishes`.  
     *Fix*: Scoped generic responses strictly to `active_target_field`.
  2. **Comma-Separated Executor Parsing**: Comma inputs like `"james, brother"` needed to extract both name and relation simultaneously without misclassifying children names `"bob, james"`.  
     *Fix*: Added relationship keyword guards (`brother`, `sister`, `friend`, etc.) to comma matching.
  3. **Greedy Address Substring Match**: Substrings like `"st"` inside words (e.g. `"assistant"`, `"executor"`) triggered false address conflicts.  
     *Fix*: Replaced substring search with word boundary regex `\b(?:street|st|road|rd|avenue|ave|lane|ln|drive|dr|blvd|way|court|ct)\b`.
  4. **Specific Gifts Parsing**: Generic inputs like `"yes gifts like letters"` failed to extract gifts.  
     *Fix*: Added cleaner regex stripping filler phrases and extracting substantive gift descriptions.

---

### Phase 11 — Docker Containerization & Audit
- **Objective**: Multi-stage containerization and final security audit.
- **Key Actions**:
  - Created multi-stage `Dockerfile` (Node.js React builder + Python 3.11-slim runtime).
  - Created `docker-compose.yml` and `.dockerignore`.
  - Verified `.gitignore` prevents tracking `.env`, `node_modules`, `__pycache__`, `.venv`, and `.db`.
- **Final Test Count**: **8/8 Pytest modules passing 100%**.

---

## AI Suggestions Questioned & Corrected

1. **Silent Overwriting of Conflicting Fields**:
   - *AI Suggestion*: Automatically overwrite existing state values with the latest extracted entities from user chat.
   - *My Correction*: Rejected silent overwrite. Implemented explicit conflict detection. When a user contradicts previously confirmed data, a conflict record is created (`status="conflicted"`) and an interactive UI modal allows the user to choose `Keep Previous` vs `Use New Value`.

2. **PDF Disclaimer Labeling**:
   - *AI Suggestion*: Render header as "Official Personal Wishes Will & Testament".
   - *My Correction*: Enforced mandatory disclaimer `FICTIONAL DOCUMENT — NOT LEGAL ADVICE` across all drafts, UI banners, and ReportLab PDF exports.

3. **Database Threading in Pytest**:
   - *AI Suggestion*: Use default SQLite in-memory setup in Pytest fixtures.
   - *My Correction*: Configured `StaticPool` in `conftest.py` to ensure shared test memory state across multi-threaded FastAPI test client calls.
