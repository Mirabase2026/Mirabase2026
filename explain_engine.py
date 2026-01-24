# explain_engine.py
# Explain engine – returns plain text only

def run(text: str) -> str:
    return (
        "Vysvětlení: architektura je rozdělená do vrstev, "
        "aby každá měla jasnou odpovědnost. "
        "Behavior rozpozná záměr, router rozhodne směr "
        "a engine provede konkrétní akci."
    )
