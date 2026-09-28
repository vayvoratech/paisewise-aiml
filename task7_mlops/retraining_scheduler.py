from dataclasses import dataclass


@dataclass
class RetrainingSchedule:
    model_name: str
    frequency: str
    review_required: bool


class RetrainingScheduler:
    def __init__(self):
        self.schedules = {
            "Topic Detection": RetrainingSchedule(
                model_name="Topic Detection",
                frequency="Monthly",
                review_required=True,
            ),
            "Churn Score": RetrainingSchedule(
                model_name="Churn Score",
                frequency="Weekly",
                review_required=True,
            ),
            "News Sentiment": RetrainingSchedule(
                model_name="News Sentiment",
                frequency="Weekly",
                review_required=True,
            ),
            "RAG Embedding": RetrainingSchedule(
                model_name="RAG Embedding",
                frequency="Monthly",
                review_required=True,
            ),
            "Portfolio Health": RetrainingSchedule(
                model_name="Portfolio Health",
                frequency="Monthly",
                review_required=True,
            ),
        }

    def get_schedule(self, model_name: str) -> RetrainingSchedule:
        if model_name not in self.schedules:
            raise ValueError(f"Unknown model: {model_name}")

        return self.schedules[model_name]

    def get_all_schedules(self):
        return list(self.schedules.values())