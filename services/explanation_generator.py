import logging

from services.llm_client import LLMClient
from prompts.prompt_templates import FUND_EXPLANATION_PROMPT, FINANCIAL_GUARDRAILS
from utils.content_filter import check_content

logger = logging.getLogger("ai-service")

llm_client = LLMClient()


def generate_fund_explanation(fund, risk_profile):

    prompt = FUND_EXPLANATION_PROMPT.format(
        guardrails=FINANCIAL_GUARDRAILS,
        risk_profile=risk_profile,
        fund_name=fund.get("scheme_name"),
        category=fund.get("category"),
        risk_level=fund.get("risk_level"),
        return_1y=fund.get("return_1y") or "N/A",
        return_3y=fund.get("return_3y") or "N/A",
        sharpe_ratio=fund.get("sharpe_ratio") or "N/A",
        expense_ratio=fund.get("expense_ratio") or "N/A"
    )

    try:
        response = llm_client.generate_response(prompt)
        filtered = check_content(response)
        if filtered["blocked"]:
            return filtered["message"]
        return filtered["content"].strip()

    except Exception as error:

        logger.error(
            f"Fund explanation generation failed: {error}"
        )

        return (
            f"{fund.get('scheme_name')} matches your "
            f"{risk_profile} risk profile based on available "
            "fund performance and risk metrics."
        )