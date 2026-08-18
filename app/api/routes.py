from fastapi import APIRouter, HTTPException

from app.agent.orchestrator import run_agent
from app.models.schemas import AnalysisResponse, TenderRequest
from app.tools.check_eligibility import check_eligibility
from app.tools.extract_requirements import extract_requirements
from app.tools.search_references import search_past_references

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/analyze-tender", response_model=AnalysisResponse)
def analyze_tender(request: TenderRequest):
    if not request.tender_text.strip():
        raise HTTPException(status_code=400, detail="tender_text cannot be empty")

    # Step 1: deterministic first pass — always runs, not part of the agent loop
    requirements = extract_requirements(request.tender_text)

    # Step 2: agent loop decides which tools to call and drafts the intro
    agent_result = run_agent(requirements)

    # Recompute these directly too, so the response always has full structured
    # data even if the agent's own tool calls were partial
    eligibility = check_eligibility(requirements)
    matched_refs = search_past_references(requirements.get("keywords", []))

    return AnalysisResponse(
        requirements=requirements,
        eligibility=eligibility,
        matched_references=matched_refs,
        draft_intro=agent_result["draft_intro"],
        tool_calls_made=agent_result["tool_calls_made"],
    )