from typing import Optional

import typer
from typing_extensions import Annotated

from partifact.auth_token import get_token
from partifact.config import Configuration
from partifact.shell_commands import configure_pip, configure_poetry

app = typer.Typer()

profile_option = typer.Option(
    "--profile",
    "-p",
    help="The AWS profile to use when getting the CodeArtifact token.",
)

role_option = typer.Option(
    "--role", "-r", help="The AWS role to use when getting the CodeArtifact token."
)

should_configure_pip_option = typer.Option(
    "--configure-pip",
    "-c",
    help="Set global.index-url for pip in addition to configuring poetry.",
)


@app.command()
def login(
    repository: str,
    profile: Annotated[Optional[str], profile_option] = None,
    role: Annotated[Optional[str], role_option] = None,
    should_configure_pip: Annotated[bool, should_configure_pip_option] = False,
) -> None:
    """Log into CodeArtifact.

    This configures pip and poetry to make use of the created CodeArtifact session.
    """
    config = Configuration.load(repository, profile, role)
    token = get_token(config)

    if should_configure_pip:
        configure_pip(config, token)
    configure_poetry(repository, token)


@app.command()
def configure():
    """Setup a repository with the necessary details for login.

    This stores the configuration in a file.
    """
    # TODO: configure a new repository
    pass
