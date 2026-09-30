@'
# Task 10.1 — Pre-Deployment Feedback Analysis

## Purpose

This analysis identifies the 10 improvements to be implemented for the AI platform before production deployment.

The current `chat_feedback` database contains test/random feedback data and is therefore not treated as genuine beta-user feedback. The improvements below are derived from the existing AI-service behavior, product requirements, and expected user experience.

This document is a pre-deployment engineering feedback analysis. Once real beta users are available, their questions and feedback should be added to the evaluation dataset.

---

## Analysis Method

Each improvement is evaluated using:

- User impact
- AI response quality
- Reliability
- Safety
- Feature coverage
- Ability to measure improvement

Priority levels:

- Critical — directly affects correctness, safety, or core AI usefulness
- High — materially affects user experience or AI quality
- Medium — improves usability or explanation quality

---

## Prioritized Improvements

| # | Feedback Theme | Affected Feature | Priority | Proposed Improvement |
|---|---|---|---|---|
| 1 | Answer relevance | AI Chat | Critical | Improve evaluation and prompting so responses directly address the user's question and provided context. |
| 2 | Topic/question understanding | Topic Detection | Critical | Improve classification coverage and handling of unsupported or ambiguous questions. |
| 3 | Retrieved context relevance | RAG | Critical | Evaluate retrieved chunks for relevance and prevent weak context from unnecessarily influencing answers. |
| 4 | Explanation clarity | AI Chat / Portfolio Health | High | Make explanations easier to understand while preserving factual grounding. |
| 5 | Response conciseness | AI Chat | High | Reduce unnecessary response content while retaining information required to answer the question. |
| 6 | Personalization quality | AI Chat / User Context | High | Ensure responses use available user context only when it is relevant and grounded. |
| 7 | Conversation continuity | AI Chat | High | Improve handling of previous conversation context so follow-up questions remain coherent. |
| 8 | Insufficient-knowledge handling | RAG / AI Chat | Critical | Strengthen abstention behavior when the available knowledge does not support an answer. |
| 9 | News sentiment consistency | News Sentiment | High | Improve evaluation of positive, negative, and neutral sentiment classification for supplied articles. |
| 10 | AI explanation of risk factors | Portfolio Health / Churn | High | Provide clearer explanations of the factors contributing to portfolio-health and churn outputs without inventing data or recommendations. |

---

## Improvement 1 — Answer Relevance

### Problem

An AI response should directly address the user's question instead of producing information that is only loosely related.

### Affected Component

`ChatService`

### Improvement

Introduce measurable answer-relevance evaluation using representative questions and expected answer criteria.

### Success Measurement

- Question is directly addressed.
- Response is grounded in available context.
- No unrelated information is introduced.

---

## Improvement 2 — Topic / Question Understanding

### Problem

The topic classifier currently supports a fixed set of financial categories. Questions outside the recognized patterns require better handling.

### Affected Component

`TopicClassifier`

### Improvement

Expand classification evaluation and add test cases for ambiguous, mixed-topic, and unsupported questions.

### Success Measurement

Measure classification accuracy against a versioned evaluation dataset.

---

## Improvement 3 — RAG Context Relevance

### Problem

The vector store currently retrieves the highest-scoring chunks, but retrieval does not apply a minimum relevance criterion.

### Affected Component

`RAGService` / `VectorStore`

### Improvement

Evaluate retrieval quality and introduce relevance-aware retrieval behavior where appropriate.

### Success Measurement

- Relevant context is retrieved.
- Weakly related context is reduced.
- Retrieval evaluation is repeatable.

---

## Improvement 4 — Explanation Clarity

### Problem

Correct information can still be difficult for users to understand if explanations are unnecessarily complex.

### Affected Components

`ChatService`

`PortfolioHealthService`

### Improvement

Add evaluation cases for explanation clarity and plain-language communication.

### Success Measurement

Responses should be understandable, structured, and factually grounded.

---

## Improvement 5 — Response Conciseness

### Problem

AI responses should provide the required information without unnecessary repetition.

### Affected Component

`ChatService`

### Improvement

Add response-length and conciseness criteria to the quality evaluation.

### Success Measurement

Responses remain complete while avoiding unnecessary repetition or irrelevant detail.

---

## Improvement 6 — Personalization Quality

### Problem

The platform supports user context such as goals, level, KYC information, and holdings. This context should be used only when relevant.

### Affected Component

`PromptBuilder` / `ChatService`

### Improvement

Create evaluation cases where user context is relevant, irrelevant, missing, or incomplete.

### Success Measurement

- Relevant context is used.
- Missing information is not invented.
- Unnecessary personal information is not introduced into responses.

---

## Improvement 7 — Conversation Continuity

### Problem

Follow-up questions depend on previous conversation context.

### Affected Component

`ChatService`

### Improvement

Add multi-turn evaluation cases covering references to previous questions, answers, and topics.

### Success Measurement

The response correctly uses relevant previous context without confusing unrelated conversations.

---

## Improvement 8 — Insufficient-Knowledge Handling

### Problem

The system should not invent financial information when the available knowledge does not support an answer.

### Affected Components

`RAGService`

`PromptBuilder`

`ResponseValidator`

### Improvement

Add explicit evaluation cases where the required information is absent from the available knowledge.

### Success Measurement

The system correctly indicates insufficient information instead of fabricating an answer.

---

## Improvement 9 — News Sentiment Consistency

### Problem

News sentiment classification must consistently return valid sentiment labels for supplied articles.

### Affected Component

`NewsSentimentService`

### Improvement

Create a versioned sentiment evaluation set containing positive, negative, and neutral examples.

### Success Measurement

Compare model output against expected sentiment labels and track the evaluation result between versions.

---

## Improvement 10 — Risk-Factor Explainability

### Problem

Portfolio-health and churn outputs should make their underlying factors understandable to the user.

### Affected Components

`PortfolioHealthService`

`ChurnService`

### Improvement

Add evaluation criteria for factor coverage and explanation quality while preventing unsupported claims.

### Success Measurement

- Important input factors are reflected in the explanation.
- No unsupported factors are invented.
- No personalized investment recommendation is generated.

---

## Important Pre-Deployment Limitation

The Task 10 requirement refers to updating the golden test set with real user questions from beta users.

The product is currently pre-deployment, so genuine beta-user questions are not yet available.

Therefore:

1. A pre-deployment evaluation dataset can be created now.
2. The dataset should be version controlled.
3. Real beta questions should be added when beta testing begins.
4. The full quality evaluation should then be rerun against the expanded dataset.
5. Improvement results must be compared against a recorded pre-improvement baseline.

The random/test feedback currently present in the database must not be presented as real customer feedback.

---

## Next Implementation Step

The 10 improvements above become the requirements for Task 10.1 implementation.

The next component will be a versioned evaluation dataset containing representative pre-deployment user questions for these 10 improvement areas.

'@ | Set-Content docs\task10_feedback_analysis.md -Encoding UTF8