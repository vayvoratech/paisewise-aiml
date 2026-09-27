from datetime import datetime, timezone
from pathlib import Path
import json
import shutil


class ModelRegistryService:
    def __init__(self, registry_path: str = "data/model_registry.json"):
        self.path = Path(registry_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def register(self, model_name: str, model_path: str, metrics: dict, dataset_version: str) -> dict:
        data = json.loads(self.path.read_text()) if self.path.exists() else {}
        version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        entry = {"version": version, "date": datetime.now(timezone.utc).isoformat(), "metrics": metrics, "dataset_version": dataset_version, "path": model_path}
        data.setdefault(model_name, []).append(entry)
        self.path.write_text(json.dumps(data, indent=2))
        return entry

    def latest(self, model_name: str):
        data = json.loads(self.path.read_text()) if self.path.exists() else {}
        entries = data.get(model_name, [])
        return entries[-1] if entries else None

    def shadow_compare(self, current, candidate, threshold: float = 0.05) -> dict:
        return {"candidate": candidate, "current": current, "difference": candidate - current, "anomaly": abs(candidate - current) > threshold}

    def rollback(self, current_path: str, previous_path: str) -> None:
        shutil.copy2(previous_path, current_path)
