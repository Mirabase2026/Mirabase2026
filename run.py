# run.py
# =========================
# MIRA BASE – MAIN ENTRYPOINT (v1)
# =========================
#
# Responsibilities:
# - wire Brain -> Execution
# - NO logic
# - NO language
# - NO decisions
#

from typing import Dict, Any

import logic
import execution_layer


def run_once(text: str, context: Dict[str, Any] | None = None) -> str:
    """
    Single-turn execution.
    """
    contract = logic.run(text, context)
    output_text = execution_layer.render(contract)
    return output_text


if __name__ == "__main__":
    # simple manual test
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue

            result = run_once(user_input)
            print(result)

        except KeyboardInterrupt:
            print("\nbye")
            break
