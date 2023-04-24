import pytest
import tomlkit

from partifact.config import (
    CONFIG_PATH,
    Configuration,
    InvalidConfiguration,
    MissingConfiguration,
    parse_url,
)


def test_config_with_mandatory_fields(write_conf):
    """Test that a config entry with all fields defined is successfully parsed."""
    write_conf(
        "test_repo",
        aws_account="123456789",
        aws_region="eu-west-1",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_ca_repo",
    )
    conf = Configuration.load("test_repo")

    assert conf.aws_account == "123456789"
    assert conf.aws_region == "eu-west-1"
    assert conf.code_artifact_domain == "test_domain"
    assert conf.code_artifact_repository == "test_ca_repo"
    assert conf.aws_profile is None
    assert conf.aws_role_name is None


def test_config_with_aws_profile(write_conf):
    """Test that the AWS profile is overridden with the value in config."""
    write_conf(
        "test_repo",
        aws_account="123456789",
        aws_region="eu-west-1",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_ca_repo",
    )
    conf = Configuration.load("test_repo", profile="dummy_profile")

    assert conf.aws_profile == "dummy_profile"


def test_config_with_role(write_conf):
    """Test that the AWS role ARN is overridden with the value in config."""
    role_name = "test_role"
    write_conf(
        "test_repo",
        aws_account="123456789",
        aws_region="eu-west-1",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_ca_repo",
    )
    conf = Configuration.load("test_repo", role_name=role_name)

    assert conf.aws_role_name == role_name


def test_missing_config_file():
    """Test that an appropriate exception is raised when the config file is missing."""
    with pytest.raises(MissingConfiguration, match=r"no configuration .*"):
        Configuration.load("test_repo")


def test_incorrect_url_format(fs):
    """Test that an appropriate exception is raised when the poetry URL is incorrect."""
    repo_name = "test-repo"
    sources = [{"url": "https://wrong-url", "name": repo_name}]
    config = {"tool": {"poetry": {"source": sources}}}

    with open(CONFIG_PATH, "w") as f:
        f.write(tomlkit.dumps(config))

    with pytest.raises(
        InvalidConfiguration,
        match=r"failed to parse source URL.*",
    ):
        Configuration.load(repo_name)


@pytest.mark.parametrize(
    "url",
    [
        "https://test_domain-123456789.d.codeartifact.eu-west-1.amazonaws.com/pypi/test_ca_repo",
        "https://test_domain-123456789.d.codeartifact.eu-west-1.amazonaws.com/pypi/test_ca_repo/",
        "https://test_domain-123456789.d.codeartifact.eu-west-1.amazonaws.com/pypi/test_ca_repo/simple",
        "https://test_domain-123456789.d.codeartifact.eu-west-1.amazonaws.com/pypi/test_ca_repo/simple/",
    ],
)
def test_parse_url(url):
    actual = parse_url(url)
    expected = {
        "code_artifact_domain": "test_domain",
        "code_artifact_repository": "test_ca_repo",
        "aws_account": "123456789",
        "aws_region": "eu-west-1",
    }
    assert actual == expected

@pytest.mark.parametrize(
    "url",
    [
        "https://test-domain-123456789.d.codeartifact.eu-west-1.amazonaws.com/pypi/test_ca_repo/simple/"
    ],
)
def test_parse_url_edgecase(url):
    actual = parse_url(url)
    expected = {
        "code_artifact_domain": "test-domain",
        "code_artifact_repository": "test_ca_repo",
        "aws_account": "123456789",
        "aws_region": "eu-west-1",
    }
    assert actual == expected