from typing import Optional

import typer

from partifact.auth_token import get_token
from partifact.config import Configuration
from partifact.shell_commands import configure_pip, configure_poetry

app = typer.Typer()

profile_option = typer.Option(
    None, help="The AWS profile to use when getting the CodeArtifact token."
)

role_option = typer.Option(
    None, help="The AWS role to use when getting the CodeArtifact token."
)


@app.command()
def login(
    repository: str,
    profile: Optional[str] = profile_option,
    role: Optional[str] = role_option,
) -> None:
    """Log into CodeArtifact.

    This configures pip and poetry to make use of the created CodeArtifact session.
    """
    config = Configuration.load(repository, profile, role)
    token = get_token(config)

    configure_pip(config, token)
    configure_poetry(repository, token)


@app.command()
def configure():
    """Setup a repository with the necessary details for login.

    This stores the configuration in a file.
    """
    # TODO: configure a new repository
    pass
