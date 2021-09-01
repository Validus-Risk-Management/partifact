from __future__ import annotations

from dataclasses import Field, dataclass, fields
from tomlkit import parse
from tomlkit.exceptions import TOMLKitError
from typing import Optional

CONFIG_PATH = "./pyproject.toml"


@dataclass
class Configuration:
    """Data for a repository entry in the config file.

    Attributes:
        aws_profile (str, optional):
            The AWS profile to use. If no profile is specified, the session
            will follow the resolution logic as boto3.
        aws_role_arn (str, optional):
            If specified, this role will be assumed to get the authorisation
            token.
        code_artifact_account (str):
            The AWS account hosting the CodeArtifact repository.
        code_artifact_domain (str): The name of the CodeArtifact domain.
        code_artifact_repository (str): The name of the CodeArtifact repository.
    """

    code_artifact_account: str
    code_artifact_domain: str
    code_artifact_repository: str
    aws_profile: Optional[str] = None
    aws_role_arn: Optional[str] = None

    @classmethod
    def load(cls, repository: str) -> Configuration:
        """Loads the configuration for the supplied repository.

        Args:
            repository (str): The name of the section in the configuration file,
                which should match the name of the poetry repository.
        """
        try:
            with open(CONFIG_PATH, "r") as f:
                config = parse(f.read())
        except FileNotFoundError:
            raise MissingConfiguration("no pyproject.toml found")
        except TOMLKitError:
            raise MissingConfiguration("invalid pyproject.toml")

        try:
            repo = config["tool"]["partifact"]["repository"][repository]  # type: ignore
        except TOMLKitError:
            raise MissingConfiguration(f"no configuration found for {repository}")

        def validate_field(field: Field) -> bool:
            return "Optional" in field.type or field.name in repo  # type: ignore

        missing_fields = [
            field.name for field in fields(cls) if not validate_field(field)
        ]
        if missing_fields:
            raise IncompleteConfiguration(f"missing fields in config: {missing_fields}")

        return Configuration(**repo)  # type: ignore


class MissingConfiguration(Exception):
    """Raised if the configuration file is missing or does not contain the repository."""

    pass


class IncompleteConfiguration(Exception):
    """Raised if a key is missing from the repository's configuration."""

    pass
