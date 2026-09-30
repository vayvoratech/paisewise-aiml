import pytest

from app.services.fraud_runtime import FraudRuntime


class FakeFraudModel:
    def predict_proba(self, rows):
        return [[0.8, 0.2]]


def test_runtime_can_be_initialized():
    runtime = FraudRuntime()

    model = FakeFraudModel()

    runtime.initialize(model)

    loaded_runtime = runtime.get_runtime()

    assert loaded_runtime.model is model


def test_runtime_reuses_same_instance():
    runtime = FraudRuntime()

    model = FakeFraudModel()

    runtime.initialize(model)

    first = runtime.get_runtime()
    second = runtime.get_runtime()

    assert first is second


def test_runtime_cannot_be_initialized_twice():
    runtime = FraudRuntime()

    runtime.initialize(FakeFraudModel())

    with pytest.raises(
        RuntimeError,
        match="already initialized",
    ):
        runtime.initialize(FakeFraudModel())


def test_runtime_cannot_be_used_before_initialization():
    runtime = FraudRuntime()

    with pytest.raises(
        RuntimeError,
        match="not been initialized",
    ):
        runtime.get_runtime()