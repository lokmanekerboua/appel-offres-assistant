from fastapi import APIRouter, HTTPException, UploadFile, File

from app.agent.orchestrator import run_agent
from app.models.schemas import AnalysisResponse, TenderRequest
from app.tools.check_eligibility import check_eligibility
from app.tools.extract_requirements import extract_requirements
from app.tools.pdf_extraction import extract_text_from_pdf_bytes
from app.tools.report_generator import generate_analysis_pdf
from app.tools.search_references import search_past_references
from app.tools.storage import save_analysis_to_s3, save_pdf_report_to_s3, generate_presigned_url

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/analyze-tender", response_model=AnalysisResponse)
def analyze_tender(request: TenderRequest):
    if not request.tender_text.strip():
        raise HTTPException(status_code=400, detail="tender_text cannot be empty")

    requirements = extract_requirements(request.tender_text)
    agent_result = run_agent(requirements)
    eligibility = check_eligibility(requirements)
    matched_refs = search_past_references(requirements.get("keywords", []))

    response = AnalysisResponse(
        requirements=requirements,
        eligibility=eligibility,
        matched_references=matched_refs,
        draft_intro=agent_result["draft_intro"],
        tool_calls_made=agent_result["tool_calls_made"],
    )

    pdf_bytes = generate_analysis_pdf(request.tender_text, response.model_dump())  # ou tender_text pour la version PDF
    report_key = save_pdf_report_to_s3(pdf_bytes)
    response.report_pdf_key = report_key
    
    if report_key:
        response.report_pdf_url = generate_presigned_url(report_key)

    return response


@router.post("/analyze-tender-pdf", response_model=AnalysisResponse)
async def analyze_tender_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    pdf_bytes = await file.read()
    tender_text = extract_text_from_pdf_bytes(pdf_bytes)

    if not tender_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF")

    requirements = extract_requirements(tender_text)
    agent_result = run_agent(requirements)
    eligibility = check_eligibility(requirements)
    matched_refs = search_past_references(requirements.get("keywords", []))

    response = AnalysisResponse(
        requirements=requirements,
        eligibility=eligibility,
        matched_references=matched_refs,
        draft_intro=agent_result["draft_intro"],
        tool_calls_made=agent_result["tool_calls_made"],
    )

    report_pdf_bytes = generate_analysis_pdf(tender_text, response.model_dump())
    report_key = save_pdf_report_to_s3(report_pdf_bytes)
    response.report_pdf_key = report_key

    if report_key:
        response.report_pdf_url = generate_presigned_url(report_key)

    return response