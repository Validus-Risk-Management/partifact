import typer

from partifact.auth_token import get_token
from partifact.config import Configuration
from partifact.shell_commands import configure_pip, configure_poetry

app = typer.Typer()


@app.command()
def login(repository: str):
    """Log into CodeArtifact.

    This configures pip and poetry to make use of the created CodeArtifact session.
    """
    config = Configuration.load(repository)
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
