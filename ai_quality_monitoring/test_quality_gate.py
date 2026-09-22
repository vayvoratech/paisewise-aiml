from quality_gate import QualityGate


gate = QualityGate()


print("Score 4.5:")
print(
    gate.evaluate(
        "jargon",
        4.5
    )
)


print("\nScore 3.3:")
print(
    gate.evaluate(
        "portfolio",
        3.3
    )
)


print("\nScore 2.8:")
print(
    gate.evaluate(
        "market_context",
        2.8
    )
)