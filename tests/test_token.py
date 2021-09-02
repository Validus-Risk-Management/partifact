from partifact.auth_token import get_token
from partifact.config import Configuration


def test_token_without_profile(aws):
    """Tests token generation without a named profile or role."""
    expected_token = "test-token"
    conf = Configuration(
        code_artifact_account="1234",
        code_artifact_repository="test-repo",
        code_artifact_domain="test-domain",
    )
    aws.add_repository(
        conf.code_artifact_domain, conf.code_artifact_account, expected_token
    )

    actual_token = get_token(conf)

    assert actual_token == expected_token
    assert aws.assumed_role is None
    assert len(aws.sessions) == 1
    assert aws.sessions[0].kwargs["profile_name"] is None


def test_token_using_profile(aws):
    """Tests that a token is returned as expected when authenticating via a named profile."""
    expected_token = "test-token"
    conf = Configuration(
        code_artifact_account="1234",
        code_artifact_repository="test-repo",
        code_artifact_domain="test-domain",
        aws_profile="test-profile",
    )

    aws.add_repository(
        conf.code_artifact_domain, conf.code_artifact_account, expected_token
    )

    actual_token = get_token(conf)

    assert actual_token == expected_token
    assert aws.assumed_role is None
    assert len(aws.sessions) == 1
    assert aws.sessions[0].kwargs["profile_name"] == conf.aws_profile


def test_token_via_assumed_role(aws):
    """Tests that a token is returned as expected when authenticating via a role."""
    expected_token = "test-token"
    conf = Configuration(
        code_artifact_account="1234",
        code_artifact_repository="test-repo",
        code_artifact_domain="test-domain",
        aws_role_name="test-role",
    )

    aws.add_repository(
        conf.code_artifact_domain, conf.code_artifact_account, expected_token
    )

    actual_token = get_token(conf)

    assert actual_token == expected_token
    assert aws.assumed_role == "arn:aws:iam::1234:role/test-role"
    assert len(aws.sessions) == 2
    assert aws.sessions[0].kwargs["profile_name"] is None


def test_token_via_named_profile_assumed_role(aws):
    """Tests token generation via assumed role from a named profile."""
    expected_token = "test-token"
    conf = Configuration(
        code_artifact_account="1234",
        code_artifact_repository="test-repo",
        code_artifact_domain="test-domain",
        aws_profile="test-profile",
        aws_role_name="test-role",
    )

    aws.add_repository(
        conf.code_artifact_domain, conf.code_artifact_account, expected_token
    )

    actual_token = get_token(conf)

    assert actual_token == expected_token
    assert aws.assumed_role == "arn:aws:iam::1234:role/test-role"
    assert len(aws.sessions) == 2
    assert aws.sessions[0].kwargs["profile_name"] == conf.aws_profile
