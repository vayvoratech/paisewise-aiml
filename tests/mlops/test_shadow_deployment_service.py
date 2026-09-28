import pytest

from app.services.mlops.shadow_deployment_service import ShadowDeploymentService


def test_compare_matching_outputs():
    def current_model(data):
        return "approved"

    def shadow_model(data):
        return "approved"

    result = ShadowDeploymentService.compare(
        current_model,
        shadow_model,
        {"amount": 1000},
    )

    assert result.current_output == "approved"
    assert result.shadow_output == "approved"
    assert result.outputs_match is True


def test_compare_different_outputs():
    def current_model(data):
        return "approved"

    def shadow_model(data):
        return "rejected"

    result = ShadowDeploymentService.compare(
        current_model,
        shadow_model,
        {"amount": 1000},
    )

    assert result.current_output == "approved"
    assert result.shadow_output == "rejected"
    assert result.outputs_match is False


def test_rejects_non_callable_current_model():
    with pytest.raises(TypeError, match="current_model must be callable"):
        ShadowDeploymentService.compare(
            None,
            lambda data: "approved",
            {"amount": 1000},
        )


def test_rejects_non_callable_shadow_model():
    with pytest.raises(TypeError, match="shadow_model must be callable"):
        ShadowDeploymentService.compare(
            lambda data: "approved",
            None,
            {"amount": 1000},
        )