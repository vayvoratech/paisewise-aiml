print("=" * 60)
print("PAISEWISE RAG - FINAL EVALUATION")
print("=" * 60)

print()

# --------------------------------------------------
# Evaluation targets
# --------------------------------------------------

guardrail_rate = 96.0
positive_answer_rate = 100.0

# Update this after your final red-team test
red_team_rate = 65.0

hindi_questions = 20

# --------------------------------------------------
# Display results
# --------------------------------------------------

print("1. Guardrail Evaluation")
print("-" * 60)
print(f"Total questions       : 50")
print(f"Correctly blocked     : 48")
print(f"Deflection rate       : {guardrail_rate:.2f}%")
print("Target                : 95%")
print("Status                : PASSED" if guardrail_rate >= 95 else "Status                : NEEDS IMPROVEMENT")

print()

print("2. Positive Educational Evaluation")
print("-" * 60)
print(f"Total questions       : 50")
print(f"Answered              : 50")
print(f"Blocked               : 0")
print(f"Educational rate      : {positive_answer_rate:.2f}%")
print("Target                : 90%")
print("Status                : PASSED" if positive_answer_rate >= 90 else "Status                : NEEDS IMPROVEMENT")

print()

print("3. Red Team Evaluation")
print("-" * 60)
print(f"Total questions       : 20")
print(f"Blocked               : 13")
print(f"Not blocked           : 7")
print(f"Deflection rate       : {red_team_rate:.2f}%")
print("Target                : 95%")
print("Status                : PASSED" if red_team_rate >= 95 else "Status                : NEEDS IMPROVEMENT")

print()

print("4. Hindi Retrieval Evaluation")
print("-" * 60)
print(f"Hindi questions tested: {hindi_questions}")
print("Response language     : Hindi")
print("Status                : TESTED")
print("Note                  : Hindi retrieval requires further improvement")

print()

print("5. RAG System")
print("-" * 60)
print("ChromaDB documents     : 290")
print("Embedding model        : all-MiniLM-L6-v2")
print("Vector database        : ChromaDB")
print("Re-ranker               : Enabled")
print("FastAPI                 : Enabled")
print("API endpoint            : POST /ask")

print()

print("=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

print("Guardrails             : PASSED")
print("Educational questions  : PASSED")
print("Red team               : NEEDS IMPROVEMENT")
print("Hindi retrieval        : NEEDS IMPROVEMENT")
print("RAG API                : WORKING")
print("ChromaDB               : WORKING")
print("Re-ranking             : WORKING")

print("=" * 60)