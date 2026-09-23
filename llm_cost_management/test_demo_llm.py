from demo_llm_service import DemoLLMService


llm = DemoLLMService()

result = llm.generate_response(
    prompt="Explain SIP in simple terms",
    model="gpt-4o-mini"
)

print("\nResponse:")
print(result["response"])

print("\nInput Tokens:")
print(result["input_tokens"])

print("\nOutput Tokens:")
print(result["output_tokens"])

print("\nTotal Tokens:")
print(result["total_tokens"])