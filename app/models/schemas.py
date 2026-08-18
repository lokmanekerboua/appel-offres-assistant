from pydantic import BaseModel, Field


class TenderRequest(BaseModel):
    tender_text: str = Field(..., description="Raw text of the tender / cahier des charges")


class Requirement(BaseModel):
    deadline: str | None = None
    budget: str | None = None
    required_certifications: list[str] = []
    deliverables: list[str] = []
    keywords: list[str] = []


class MatchedReference(BaseModel):
    project_name: str
    client: str
    relevance_score: float


class EligibilityResult(BaseModel):
    is_eligible: bool
    missing_certifications: list[str] = []
    risk_notes: list[str] = []


class AnalysisResponse(BaseModel):
    requirements: Requirement
    eligibility: EligibilityResult
    matched_references: list[MatchedReference]
    draft_intro: str
    tool_calls_made: list[str]