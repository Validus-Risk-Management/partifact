from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from parse import parse
from tomlkit import parse as parse_toml
from tomlkit.exceptions import TOMLKitError

CONFIG_PATH = "./pyproject.toml"
URL_TEMPLATE = "https://{code_artifact_domain}-{aws_account}.d.codeartifact.{aws_region}.amazonaws.com/pypi/{code_artifact_repository}/simple/"


@dataclass(frozen=True)
class Configuration:
    """Data for a repository entry in the config file.

    Attributes:
        aws_account (str):
            The AWS account hosting the CodeArtifact repository.
        aws_region (str):
            The AWS region of the CodeArtifact repository.
        code_artifact_domain (str): The name of the CodeArtifact domain.
        code_artifact_repository (str): The name of the CodeArtifact repository.
        aws_profile (str, optional):
            The AWS profile to use. If no profile is specified, the session
            will follow the resolution logic as boto3.
        aws_role_name (str, optional):
            If specified, this role will be assumed to get the authorisation
            token.
    """

    aws_account: str
    aws_region: str
    code_artifact_domain: str
    code_artifact_repository: str
    aws_profile: Optional[str] = None
    aws_role_name: Optional[str] = None

    @classmethod
    def load(
        cls,
        repository: str,
        profile: Optional[str] = None,
        role_name: Optional[str] = None,
    ) -> Configuration:
        """Loads the configuration for the supplied repository.

        Args:
            repository (str): The name of the section in the configuration file,
                which should match the name of the poetry repository.
            profile (Optional[str]): The AWS profile to use.
            role_name (Optional[str]): The name of the AWS role to use.
        """
        try:
            with open(CONFIG_PATH, "r") as f:
                config = parse_toml(f.read())
        except FileNotFoundError:
            raise MissingConfiguration("no pyproject.toml found")
        except TOMLKitError:
            raise MissingConfiguration("invalid pyproject.toml")

        try:
            source = config["tool"]["poetry"]["source"]  # type: ignore
            repo = next(s for s in source if s["name"] == repository)  # type: ignore
            url = repo["url"]
        except (TOMLKitError, StopIteration):
            raise MissingConfiguration(f"no configuration found for {repository}")

        parsed_url = parse(URL_TEMPLATE, url)
        if not parsed_url:
            raise InvalidConfiguration(
                f"failed to parse source URL, make sure it's in the format of {URL_TEMPLATE}"
            )

        return Configuration(aws_profile=profile, aws_role_name=role_name, **parsed_url.named)  # type: ignore


class MissingConfiguration(Exception):
    """Raised if the configuration file is missing or does not contain the repository."""

    pass


class InvalidConfiguration(Exception):
    """Raised if a key is missing from the repository's configuration."""

    pass
