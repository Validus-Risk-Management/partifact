"""Shell commands to configure pip and poetry."""

import subprocess
from functools import reduce
from typing import Dict, List

from partifact.config import Configuration

PIP_COMMAND = [
    "pip",
    "config",
    "set",
    "global.index-url",
    "$URL",
]

POETRY_COMMAND = [
    "poetry",
    "config",
    "http-basic.$REPO",
    "aws",
    "$TOKEN",
]


class ShellCommandException(Exception):
    """Represents a failure in a shell command."""

    pass


PIP_URL_TEMPLATE = "https://aws:{token}@{domain}-{account}.d.codeartifact.{region}.amazonaws.com/pypi/{repo}/simple/"


def configure_pip(config: Configuration, token: str) -> None:
    """Configures pip globally to use CodeArtifact by default."""
    try:
        url = PIP_URL_TEMPLATE.format(
            token=token,
            domain=config.code_artifact_domain,
            account=config.aws_account,
            region=config.aws_region,
            repo=config.code_artifact_repository,
        )
        _run_command(PIP_COMMAND, {"URL": url})
    except subprocess.CalledProcessError as err:
        raise ShellCommandException(f"failed to configure pip: {err.stderr}")


def configure_poetry(repository: str, token: str) -> None:
    """Configures the login credentials for the supplied repo in poetry."""
    try:
        _run_command(POETRY_COMMAND, {"TOKEN": token, "REPO": repository})
    except subprocess.CalledProcessError as err:
        raise ShellCommandException(f"failed to configure poetry: {err.stderr}")


def _run_command(
    command: List[str], env: Dict[str, str]
) -> subprocess.CompletedProcess:
    def expand(v: str) -> str:
        # this tries each environment variable, and if it's found in "v",
        # it replaces the variable with its value specified in the "env" dict
        return reduce(
            lambda s, env_var: s.replace(f"${env_var[0]}", env_var[1]),
            env.items(),
            v,
        )

    command_with_env = [expand(v) for v in command]
    return subprocess.run(command_with_env, capture_output=True, text=True, check=True)
