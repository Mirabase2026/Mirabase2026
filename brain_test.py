# =========================
# MIRA BASE – BRAIN TEST CLI
# =========================
#
# IMPORTANT:
# - context MUST persist between turns

from logic import run_pipeline


def main():
    print("-" * 30)

    # 🔑 PERSISTENT CONTEXT
    context = {}

    while True:
        try:
            user_text = input("Uživatel: ").strip()
            if not user_text:
                continue

            result = run_pipeline(user_text, context)

            chrono = result.get("chrono") or {}

            print(
                f"[pipeline={result.get('pipeline')}] "
                f"[actions={result.get('actions')}] "
                f"[intent={result.get('intent')}] "
                f"[chrono={chrono.get('flags')}]"
            )

            print(result.get("text", ""))

        except KeyboardInterrupt:
            print("\nKonec.")
            break
        except Exception as e:
            print("CHYBA:", e)


if __name__ == "__main__":
    main()
