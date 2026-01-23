# explain_engine.py

def run(context: dict):
    """
    Jednoduchý explain engine.
    Zatím statická odpověď – důkaz toku.
    """

    return {
        "response": (
            "Vysvětlení: architektura je rozdělená do vrstev, "
            "aby každá měla jasnou odpovědnost. "
            "Behavior rozpozná záměr, router rozhodne směr "
            "a engine provede konkrétní akci."
        ),
        "source": "explain_engine"
    }
