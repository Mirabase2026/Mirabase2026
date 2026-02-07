# test_suite.py
# =========================
# MIRA BASE – GOLDEN TESTS (v1.3)
# =========================
#
# Purpose:
# - verify Brain → Contract → Execution wiring
# - protect against regressions
# - validate FACT expansions (TIME, DATE, DAY, ARITHMETIC)
#

import logic
import execution_layer


GOLDEN_TESTS = [
    # ---------- CORE ----------
    {
        "name": "TIME_NOW",
        "input": "Kolik je hodin?",
        "expect_non_empty": True,
    },
    {
        "name": "GREETING",
        "input": "Ahoj",
        "expect_non_empty": True,
    },
    {
        "name": "UNKNOWN_INPUT",
        "input": "Gugululu",
        "expect_non_empty": True,
    },
    {
        "name": "ARITHMETIC",
        "input": "Kolik je 25 + 75?",
        "expect_non_empty": True,
    },
    {
        "name": "SHORT_INPUT",
        "input": "?",
        "expect_non_empty": True,
    },

    # ---------- GUARD / EDGE CASES ----------
    {
        "name": "EMPTY_STRING",
        "input": "",
        "expect_non_empty": True,
    },
    {
        "name": "WHITESPACE_ONLY",
        "input": "   ",
        "expect_non_empty": True,
    },
    {
        "name": "LONG_INPUT",
        "input": "a" * 500,
        "expect_non_empty": True,
    },

    # ---------- NEW FACTS (A + B) ----------
    {
        "name": "DATE_TODAY",
        "input": "Jaké je dnes datum?",
        "expect_non_empty": True,
    },
    {
        "name": "DAY_TODAY",
        "input": "Jaký je dnes den?",
        "expect_non_empty": True,
    },
]


def run_tests():
    print("\n=== MIRA BASE – GOLDEN TESTS ===\n")

    passed = 0

    for test in GOLDEN_TESTS:
        name = test["name"]
        text = test["input"]

        print(f"[TEST] {name}")
        print(f" input: {repr(text)}")

        try:
            contract = logic.run(text)
            output = execution_layer.render(contract)

            print(f" output: {repr(output)}")

            if test["expect_non_empty"] and not output:
                print(" ❌ FAIL: empty output")
            else:
                print(" ✅ PASS")
                passed += 1

        except Exception as e:
            print(f" ❌ EXCEPTION: {e}")

        print("-" * 40)

    print(f"\nRESULT: {passed}/{len(GOLDEN_TESTS)} tests passed\n")


if __name__ == "__main__":
    run_tests()
