import logging

from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.tools_schema import TOOLS
from app.core.config import settings
from app.core.llm_client import call_claude
from app.tools.check_eligibility import check_eligibility
from app.tools.search_references import search_past_references

logger = logging.getLogger(__name__)

TOOL_DISPATCH = {
    "search_past_references": lambda inp: search_past_references(inp["keywords"]),
    "check_eligibility": lambda inp: check_eligibility(inp["requirements"]),
}


def run_agent(requirements: dict) -> dict:
    """
    Core agent loop: send requirements to Claude, execute any tool_use
    blocks it requests, feed results back, repeat until Claude returns
    a final text answer (or we hit max_tool_loops as a safety guardrail).
    """
    messages = [
        {
            "role": "user",
            "content": (
                "Voici les exigences extraites de l'appel d'offres :\n"
                f"{requirements}\n\n"
                "Analyse l'éligibilité, trouve les références pertinentes, "
                "puis rédige le paragraphe d'introduction."
            ),
        }
    ]

    tool_calls_made = []

    for loop_index in range(settings.max_tool_loops):
        response = call_claude(messages=messages, tools=TOOLS, system=AGENT_SYSTEM_PROMPT)

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            final_text = "".join(block.text for block in response.content if block.type == "text")
            return {
                "draft_intro": final_text.strip(),
                "tool_calls_made": tool_calls_made,
            }

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input
            logger.info(f"tool_call: {tool_name} | input={tool_input}")
            tool_calls_made.append(tool_name)

            try:
                handler = TOOL_DISPATCH[tool_name]
                result = handler(tool_input)
            except Exception as e:
                logger.error(f"tool_execution_failed: {tool_name} | {e}")
                result = {"error": str(e)}

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                }
            )

        messages.append({"role": "user", "content": tool_results})

    logger.warning("max_tool_loops_reached")
    return {
        "draft_intro": "Analyse incomplète : nombre maximal d'appels d'outils atteint.",
        "tool_calls_made": tool_calls_made,
    }