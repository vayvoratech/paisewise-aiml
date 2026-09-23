"""Optional CloudWatch publisher for daily AI cost metrics."""
import os


def publish_daily_cost(cost_inr: float):
    if os.getenv("AWS_CLOUDWATCH_ENABLED", "false").lower() != "true":
        return False
    import boto3
    client = boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION", "ap-south-1"))
    client.put_metric_data(
        Namespace="PaiseWise/AIService",
        MetricData=[{
            "MetricName": "DailyLLMCostINR",
            "Value": float(cost_inr),
            "Unit": "None",
        }],
    )
    return True
