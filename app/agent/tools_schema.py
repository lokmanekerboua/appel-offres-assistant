TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_past_references",
            "description": (
                "Recherche dans la base de projets passés de l'entreprise ceux qui "
                "correspondent le mieux aux mots-clés d'un appel d'offres."
            ),
            "parameters": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "check_eligibility",
            "description": (
                "Vérifie si l'entreprise est éligible à répondre à l'appel d'offres "
                "en comparant les certifications requises et le budget avec le profil de l'entreprise."
            ),
            "parameters": {
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
    },
]