from guardrail import check_guardrail
from positive_tests import positive_questions
from guardrail_tests import guardrail_questions


# Confusion matrix
true_positive = 0
false_positive = 0
true_negative = 0
false_negative = 0


# --------------------------------------------------
# NEGATIVE / ADVICE QUESTIONS
# Expected result: DEFLECT
# --------------------------------------------------

print("=" * 60)
print("TESTING ADVICE / DEFLECTION QUESTIONS")
print("=" * 60)

for number, question in enumerate(
    guardrail_questions,
    start=1
):

    result = check_guardrail(question)

    if result == "DEFLECT":

        true_positive += 1

    else:

        false_negative += 1

        print(
            f"\nFAILED ADVICE QUESTION {number}:"
        )
        print("Question:", question)
        print("Result:", result)


# --------------------------------------------------
# POSITIVE / EDUCATIONAL QUESTIONS
# Expected result: ALLOW
# --------------------------------------------------

print("\n" + "=" * 60)
print("TESTING EDUCATIONAL QUESTIONS")
print("=" * 60)

for number, question in enumerate(
    positive_questions,
    start=1
):

    result = check_guardrail(question)

    if result == "ALLOW":

        true_negative += 1

    else:

        false_positive += 1

        print(
            f"\nFAILED EDUCATIONAL QUESTION {number}:"
        )
        print("Question:", question)
        print("Result:", result)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("\n" + "=" * 60)
print("GUARDRAIL EVALUATION")
print("=" * 60)

print(
    "Total advice questions:",
    len(guardrail_questions)
)

print(
    "Total educational questions:",
    len(positive_questions)
)

print("\nTrue Positive:", true_positive)
print("False Positive:", false_positive)
print("True Negative:", true_negative)
print("False Negative:", false_negative)


# Precision
if true_positive + false_positive > 0:

    precision = true_positive / (
        true_positive + false_positive
    )

else:

    precision = 0


# Recall
if true_positive + false_negative > 0:

    recall = true_positive / (
        true_positive + false_negative
    )

else:

    recall = 0


print(
    "\nAdvice Deflection Precision:",
    round(precision, 2)
)

print(
    "Advice Deflection Recall:",
    round(recall, 2)
)


# Educational answer rate
if len(positive_questions) > 0:

    educational_answer_rate = (
        true_negative /
        len(positive_questions)
    )

else:

    educational_answer_rate = 0


print(
    "Educational Answer Rate:",
    round(
        educational_answer_rate,
        2
    )
)