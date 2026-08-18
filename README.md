# Appel d'Offres Assistant

Demo API showing an LLM agent with real tool calling: extraction,
eligibility checking, and reference matching for public tenders.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs

## Example request

```bash
curl -X POST http://127.0.0.1:8000/analyze-tender \
  -H "Content-Type: application/json" \
  -d '{"tender_text": "Appel d offres pour la rénovation de l éclairage public de la ville. Budget: 500000 EUR. Deadline: 15 mars 2027. Certification ISO 9001 requise."}'
```

## Architecture notes

- `extract_requirements` runs as a deterministic first step, outside the
  agent loop, since it always happens exactly once.
- `orchestrator.py` implements the actual tool-calling loop against the
  Anthropic API, capped at `max_tool_loops` as a cost/runaway guardrail.
- `check_eligibility` is pure Python — no LLM call — to show that not
  every step needs to go through the model.