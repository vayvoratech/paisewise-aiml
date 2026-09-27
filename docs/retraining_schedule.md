# Automated retraining schedule

- Fund recommendation model: every Sunday at 02:00. Latest fund performance is loaded, scoring weights are recalculated, the candidate is validated against the current model and deployment occurs only when the validation score improves by more than 2%.
- Churn model: monthly on the 1st at 03:00. The churn model is retrained from the available recent outcomes, metrics are logged in MLflow and the candidate is registered before deployment.
- Model versions record date, metrics and dataset version in `data/model_registry.json`.
- Shadow comparison and rollback helpers are available in `ModelRegistryService`.
- Retraining notifications use the configured Slack webhook.
