# cli.py
from logic import run_pipeline
from memory import load_short, load_long

def print_block(title, content):
    print(f"\n{title}")
    print("-" * len(title))
    if content is None:
        print("none")
    elif isinstance(content, list):
        for i, item in enumerate(content[-5:], 1):
            print(f"{i}. {item}")
    else:
        print(content)

def main():
    print("🧠 MiraBase — DEBUG BRAIN MODE")
    print("Piš text a Enter. Příkazy: :history :memory :long :clear exit\n")

    while True:
        cmd = input("🗣️ > ").strip()

        if cmd.lower() in ("exit", "quit"):
            break

        if cmd.startswith(":"):
            if cmd == ":history":
                print_block("📚 HISTORY (short)", load_short())
            elif cmd == ":memory":
                print_block("🧠 SHORT MEMORY", load_short())
            elif cmd == ":long":
                print_block("🧠 LONG MEMORY", load_long())
            elif cmd == ":clear":
                from memory import clear_all
                clear_all()
                print("🧹 Paměť vyčištěna.")
            else:
                print("❓ Neznámý příkaz.")
            continue

        result = run_pipeline(
            text=cmd,
            session="cli-debug",
            source="cli"
        )

        print_block("🧠 INPUT", cmd)
        print_block("🧭 DECISION", result.get("action"))
        print_block("🤖 RESPONSE", result.get("response"))
        print_block("📥 MEMORY READ", result.get("memory_read"))
        print_block("📤 MEMORY WRITE", result.get("memory_write"))

        status = "✅ PIPELINE OK" if not result.get("error") else "❌ ERROR"
        print(f"\n{status}")
        if result.get("error"):
            print(result["error"])

        print("\n" + "=" * 40 + "\n")

if __name__ == "__main__":
    main()
