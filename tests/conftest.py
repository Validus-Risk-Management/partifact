from dataclasses import asdict

import pytest
import tomlkit

from partifact.config import Configuration, CONFIG_PATH


@pytest.fixture()
def write_conf(fs):
    """Fixture to write a configuration entry."""

    def _write(repository: str, **kwargs):
        config = {"tool": {"partifact": {"repository": {repository: kwargs}}}}

        with open(CONFIG_PATH, "w") as f:
            f.write(tomlkit.dumps(config))

    return _write


@pytest.fixture()
def add_conf(write_conf):
    """Fixture to add a test configuration entry."""

    def _add(repository: str, config: Configuration):
        write_conf(repository, **asdict(config))

    return _add


class MockSession:
    def __init__(self, aws, **kwargs):
        """Creates a mock session.

        This stores the kwargs it was created with so assertions can be made about it.
        """
        self._aws = aws
        self.kwargs = kwargs

    def client(self, service: str):
        """Returns a client for an expected service or raises an exception otherwise."""
        if service == "sts":
            return MockSTSClient(self._aws)
        elif service == "codeartifact":
            return MockCodeArtifactClient(self._aws)
        else:
            raise ValueError("trying to create client for unexpected service")


class DummyAWS:
    def __init__(self):
        """Creates a dummy AWS object."""
        self._sessions = []
        self._repositories = {}
        self.assumed_role = None

    @property
    def sessions(self):
        """A tuple of the sessions created."""
        return tuple(self._sessions)

    def add_repository(self, domain, domain_owner, token):
        """Add an expected CodeArtifact repository.

        Args:
            domain: The CodeArtifact domain.
            domain_owner: The domain owner.
            token: The token we should generate for this repository for assertions.
        """
        self._repositories[(domain_owner, domain)] = token

    def new_session(self, **kwargs) -> MockSession:
        """Registers and returns a mock session."""
        s = MockSession(self, **kwargs)
        self._sessions.append(s)
        return s

    def register_role(self, role):
        """Keeps track of assumed roles."""
        self.assumed_role = role

    def _get_authorization_token(self, domain, domain_owner):
        token = self._repositories.get((domain_owner, domain))
        assert token is not None

        return {"authorizationToken": token}


class MockSTSClient:
    def __init__(self, aws):
        """Creates a mock STS client allowing roles to be assumed."""
        self.aws = aws

    def assume_role(
        self, RoleArn=None, RoleSessionName=None  # noqa : boto3 argument naminge
    ):
        """Mimicking boto3.client('sts')."""
        self.aws.register_role(RoleArn)
        return {
            "Credentials": {
                "AccessKeyId": "test_access_key",
                "SecretAccessKey": "test_secret_key",
                "SessionToken": "test_token",
            }
        }


class MockCodeArtifactClient:
    def __init__(self, aws):
        """Creates a mock CodeArtifact client."""
        self.aws = aws

    def get_authorization_token(
        self, domain=None, domainOwner=None  # noqa : boto3 argument naminge
    ):
        """Mimicking boto3.client('codeartifact')."""
        return self.aws._get_authorization_token(domain, domainOwner)


@pytest.fixture()
def aws(mocker):
    """Swaps boto3 with a dummy implementation."""
    dummy_aws = DummyAWS()
    mock = mocker.patch("boto3.Session")
    mock.side_effect = dummy_aws.new_session
    return dummy_aws


@pytest.fixture()
def subprocess_mock(mocker):
    """Patches subprocess.run so that it does not execute anything."""
    mock = mocker.patch("subprocess.run")
    return mock
