from cost_manager import CostManager
from demo_llm_service import DemoLLMService
from cost_storage import CostStorage
from cost_report import MonthlyCostReport


def print_separator(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# --------------------------------------------------
# Initialize components
# --------------------------------------------------

manager = CostManager()
llm_service = DemoLLMService()
storage = CostStorage()


# --------------------------------------------------
# Test 1: First request
# --------------------------------------------------

print_separator("TEST 1 - FIRST LLM REQUEST")

result1 = manager.process_llm_request(
    user_id="TEST001",
    user_tier="premium",
    feature="jargon",
    llm_service=llm_service,
    prompt="Explain SIP in simple terms",
    input_cost_per_1k=1.0,
    output_cost_per_1k=1.5
)

print("Response:", result1["response"])
print("Model:", result1["model"])
print("Input Tokens:", result1["input_tokens"])
print("Output Tokens:", result1["output_tokens"])
print("Total Tokens:", result1["total_tokens"])
print("Cost:", result1["cost_inr"])
print("Cached:", result1["cached"])


# --------------------------------------------------
# Test 2: Same request - cache
# --------------------------------------------------

print_separator("TEST 2 - SAME REQUEST / CACHE TEST")

result2 = manager.process_llm_request(
    user_id="TEST001",
    user_tier="premium",
    feature="jargon",
    llm_service=llm_service,
    prompt="Explain SIP in simple terms",
    input_cost_per_1k=1.0,
    output_cost_per_1k=1.5
)

print("Response:", result2["response"])
print("Model:", result2["model"])
print("Cost:", result2["cost_inr"])
print("Cached:", result2["cached"])


# --------------------------------------------------
# Test 3: Different request
# --------------------------------------------------

print_separator("TEST 3 - DIFFERENT REQUEST")

result3 = manager.process_llm_request(
    user_id="TEST002",
    user_tier="free",
    feature="portfolio",
    llm_service=llm_service,
    prompt="What is portfolio diversification?",
    input_cost_per_1k=1.0,
    output_cost_per_1k=1.5
)

print("Response:", result3["response"])
print("Model:", result3["model"])
print("Input Tokens:", result3["input_tokens"])
print("Output Tokens:", result3["output_tokens"])
print("Total Tokens:", result3["total_tokens"])
print("Cost:", result3["cost_inr"])
print("Cached:", result3["cached"])


# --------------------------------------------------
# Test 4: Verify storage
# --------------------------------------------------

print_separator("TEST 4 - STORAGE")

records = storage.get_records()

print("Total stored records:", len(records))

latest_records = records[-2:]

for record in latest_records:
    print(
        record["user_id"],
        "|",
        record["feature"],
        "|",
        record["model"],
        "|",
        record["cost_inr"]
    )


# --------------------------------------------------
# Test 5: Generate monthly report
# --------------------------------------------------

print_separator("TEST 5 - MONTHLY COST REPORT")

report = MonthlyCostReport(records).generate_report()

print("Total Cost:", report["total_cost_inr"])

print("\nCost by Feature:")
print(report["cost_by_feature"])

print("\nCost by User:")
print(report["cost_by_user"])

print("\nCost by Month:")
print(report["cost_by_month"])


# --------------------------------------------------
# Final validation
# --------------------------------------------------

print_separator("FINAL VALIDATION")

if result1["cached"] is False:
    print("PASS - First request was processed normally")
else:
    print("FAIL - First request should not be cached")


if result2["cached"] is True and result2["cost_inr"] == 0:
    print("PASS - Cache avoided the second LLM cost")
else:
    print("FAIL - Cache test failed")


if result3["cached"] is False and result3["cost_inr"] > 0:
    print("PASS - Different request generated a new LLM cost")
else:
    print("FAIL - Different request test failed")


if len(records) >= 2:
    print("PASS - Usage records are stored")
else:
    print("FAIL - Records were not stored")


if report["total_cost_inr"] > 0:
    print("PASS - Monthly cost report generated")
else:
    print("FAIL - Monthly report failed")


print_separator("COMPLETE TEST FINISHED")