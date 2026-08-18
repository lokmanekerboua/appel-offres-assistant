import json
import logging

from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.tools_schema import TOOLS
from app.core.config import settings
from app.core.llm_client import call_groq
from app.tools.check_eligibility import check_eligibility
from app.tools.search_references import search_past_references

logger = logging.getLogger(__name__)

TOOL_DISPATCH = {
    "search_past_references": lambda inp: search_past_references(inp["keywords"]),
    "check_eligibility": lambda inp: check_eligibility(inp["requirements"]),
}


def run_agent(requirements: dict) -> dict:
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Voici les exigences extraites de l'appel d'offres :\n"
                f"{requirements}\n\n"
                "Analyse l'éligibilité, trouve les références pertinentes, "
                "puis rédige le paragraphe d'introduction."
            ),
        },
    ]

    tool_calls_made = []

    for loop_index in range(settings.max_tool_loops):
        response = call_groq(messages=messages, tools=TOOLS)
        choice = response.choices[0]
        message = choice.message

        messages.append(message.model_dump(exclude_none=True))

        if choice.finish_reason != "tool_calls":
            return {
                "draft_intro": (message.content or "").strip(),
                "tool_calls_made": tool_calls_made,
            }

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            logger.info(f"tool_call: {tool_name} | input={tool_input}")
            tool_calls_made.append(tool_name)

            try:
                handler = TOOL_DISPATCH[tool_name]
                result = handler(tool_input)
            except Exception as e:
                logger.error(f"tool_execution_failed: {tool_name} | {e}")
                result = {"error": str(e)}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

    logger.warning("max_tool_loops_reached")
    return {
        "draft_intro": "Analyse incomplète : nombre maximal d'appels d'outils atteint.",
        "tool_calls_made": tool_calls_made,
    }