from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from partifact.config import Configuration
from partifact.main import app

runner = CliRunner()


@pytest.fixture()
def load_config_mock(mocker) -> Mock:
    """Patches the load method of Configuration."""
    test_config = Configuration(
        aws_account="test_account",
        aws_region="eu-west-1",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_repo",
    )

    load_mock = mocker.patch("partifact.main.Configuration.load")
    load_mock.return_value = test_config
    return load_mock


@pytest.fixture()
def token_mock(mocker):
    """Patches token generation."""
    test_token = "TEST_TOKEN"

    mock = mocker.patch("partifact.main.get_token")
    mock.return_value = test_token

    return mock


@pytest.mark.usefixtures("subprocess_mock")
def test_login_generates_token_with_correct_inputs(
    load_config_mock: Mock, token_mock: Mock
):
    """Tests that the login command generates the token with correct inputs."""
    test_poetry_repo = "TEST_POETRY_REPO"

    result = runner.invoke(app, ["login", test_poetry_repo])
    assert result.exit_code == 0

    load_config_mock.assert_called_once_with(test_poetry_repo, None, None)
    config: Configuration = load_config_mock.return_value
    token_mock.assert_called_once_with(config)


@pytest.mark.usefixtures("subprocess_mock")
def test_login_generates_token_with_correct_inputs_with_profile(
    load_config_mock: Mock, token_mock: Mock
):
    """Tests that the login command generates the token with correct inputs."""
    test_poetry_repo = "TEST_POETRY_REPO"
    test_profile = "test-profile"

    result = runner.invoke(app, ["login", test_poetry_repo, "--profile", test_profile])
    assert result.exit_code == 0

    load_config_mock.assert_called_once_with(test_poetry_repo, test_profile, None)
    config: Configuration = load_config_mock.return_value
    token_mock.assert_called_once_with(config)


@pytest.mark.usefixtures("subprocess_mock")
def test_login_generates_token_with_correct_inputs_with_role(
    load_config_mock: Mock, token_mock: Mock
):
    """Tests that the login command generates the token with correct inputs."""
    test_poetry_repo = "TEST_POETRY_REPO"
    test_role = "test-role"

    result = runner.invoke(app, ["login", test_poetry_repo, "--role", test_role])
    assert result.exit_code == 0

    load_config_mock.assert_called_once_with(test_poetry_repo, None, test_role)
    config: Configuration = load_config_mock.return_value
    token_mock.assert_called_once_with(config)


def test_login_command_configures_pip(
    subprocess_mock: Mock, load_config_mock: Mock, token_mock: Mock
):
    """Tests that expected shell command is invoked to configure pip."""
    result = runner.invoke(app, ["login", "whatever"])
    assert result.exit_code == 0

    config: Configuration = load_config_mock.return_value

    expected_pip_url = f"https://aws:{token_mock.return_value}@{config.code_artifact_domain}-{config.aws_account}.d.codeartifact.eu-west-1.amazonaws.com/pypi/{config.code_artifact_repository}/simple/"
    expected_pip_command = [
        "pip",
        "config",
        "set",
        "global.index-url",
        expected_pip_url,
    ]
    subprocess_mock.assert_any_call(
        expected_pip_command, capture_output=True, text=True, check=True
    )


@pytest.mark.usefixtures("load_config_mock")
def test_login_command_configures_poetry(subprocess_mock: Mock, token_mock: Mock):
    """Tests that expected shell command is invoked to configure poetry."""
    test_poetry_repo = "TEST_POETRY_REPO"
    result = runner.invoke(app, ["login", test_poetry_repo])
    assert result.exit_code == 0

    expected_poetry_command = [
        "poetry",
        "config",
        f"http-basic.{test_poetry_repo}",
        "aws",
        token_mock.return_value,
    ]
    subprocess_mock.assert_any_call(
        expected_poetry_command, capture_output=True, text=True, check=True
    )
