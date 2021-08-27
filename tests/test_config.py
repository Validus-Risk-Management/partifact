import pytest

from partifact.config import (
    Configuration,
    IncompleteConfiguration,
    MissingConfiguration,
)


def test_config_with_mandatory_fields(write_conf):
    """Test that a config entry with all fields defined is successfully parsed."""
    write_conf(
        "test_repo",
        code_artifact_account="123456789",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_ca_repo",
    )
    conf = Configuration.load("test_repo")

    assert conf.code_artifact_account == "123456789"
    assert conf.code_artifact_domain == "test_domain"
    assert conf.code_artifact_repository == "test_ca_repo"
    assert conf.aws_profile is None
    assert conf.aws_role_arn is None


def test_config_with_aws_profile(write_conf):
    """Test that the AWS profile is overridden with the value in config."""
    write_conf(
        "test_repo",
        code_artifact_account="123456789",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_ca_repo",
        aws_profile="dummy_profile",
    )
    conf = Configuration.load("test_repo")

    assert conf.aws_profile == "dummy_profile"


def test_config_with_role_arn(write_conf):
    """Test that the AWS role ARN is overridden with the value in config."""
    role_arn = "arn:aws:iam::123456789:role/test_role"
    write_conf(
        "test_repo",
        code_artifact_account="123456789",
        code_artifact_domain="test_domain",
        code_artifact_repository="test_ca_repo",
        aws_role_arn=role_arn,
    )
    conf = Configuration.load("test_repo")

    assert conf.aws_role_arn == role_arn


@pytest.mark.usefixtures("write_conf")
def test_missing_config_file():
    """Test that an appropriate exception is raised when the config file is missing."""
    with pytest.raises(MissingConfiguration, match=r"no configuration .*"):
        Configuration.load("test_repo")


def test_missing_mandatory_field(write_conf):
    """Test that an appropriate exception is raised when a mandatory field is missing."""
    write_conf(
        "test_repo",
        code_artifact_account="123456789",
        code_artifact_domain="test_domain",
    )

    with pytest.raises(
        IncompleteConfiguration,
        match=r"missing.*code_artifact_repository.*",
    ):
        Configuration.load("test_repo")
