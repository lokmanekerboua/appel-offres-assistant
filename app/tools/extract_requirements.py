import json
import logging

from app.core.llm_client import call_claude

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """Tu extrais des informations structurées d'un appel d'offres.
Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, au format :
{
  "deadline": "string ou null",
  "budget": "string ou null",
  "required_certifications": ["liste de strings"],
  "deliverables": ["liste de strings"],
  "keywords": ["5 à 8 mots-clés représentant le secteur et la nature du projet"]
}"""


def extract_requirements(tender_text: str) -> dict:
    """
    LLM call that pulls structured requirements out of raw tender text.
    Not exposed as a Claude 'tool' in the agent loop — called directly
    since it's always the first step of the pipeline.
    """
    response = call_claude(
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": tender_text}],
    )

    raw_text = "".join(block.text for block in response.content if block.type == "text")

    try:
        cleaned = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"failed_to_parse_requirements: {e} | raw={raw_text[:200]}")
        return {
            "deadline": None,
            "budget": None,
            "required_certifications": [],
            "deliverables": [],
            "keywords": [],
        }