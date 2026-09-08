# Financial AI Guardrails

The current guardrail layer checks the user prompt before sending it to Gemini.

Blocked financial claims include phrases such as:

- guarantee
- guaranteed return
- 100% return
- double my money
- multibagger
- sure shot
- tomorrow stock

Prompt-injection phrases include:

- ignore previous instructions
- system prompt
- jailbreak
- bypass
- developer mode
- reveal your prompt

When a blocked phrase is detected, the LLM is not called and a safe response is returned.
