"""
JSON schemas passed to the Anthropic API `tools` parameter.
Only search_references and check_eligibility are exposed as agent tools —
extract_requirements always runs first as a deterministic pipeline step.
"""

TOOLS = [
    {
        "name": "search_past_references",
        "description": (
            "Recherche dans la base de projets passés de l'entreprise ceux qui "
            "correspondent le mieux aux mots-clés d'un appel d'offres. "
            "Utilise cet outil pour identifier les références pertinentes à mettre "
            "en avant dans la réponse à l'appel d'offres."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Mots-clés décrivant le secteur et la nature du projet",
                }
            },
            "required": ["keywords"],
        },
    },
    {
        "name": "check_eligibility",
        "description": (
            "Vérifie si l'entreprise est éligible à répondre à l'appel d'offres "
            "en comparant les certifications requises et le budget avec le profil "
            "de l'entreprise."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "object",
                    "description": "Objet requirements extrait de l'appel d'offres",
                }
            },
            "required": ["requirements"],
        },
    },
]