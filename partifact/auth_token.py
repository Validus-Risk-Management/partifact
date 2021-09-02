import boto3

from partifact.config import Configuration

AWS_ROLE_TEMPLATE = "arn:aws:iam::{account}:role/{role_name}"


def get_token(configuration: Configuration) -> str:
    """Returns a valid CodeArtifact token.

    Args:
        configuration: The partifact configuration to use.

    Returns:
        A valid CodeArtifact token.
    """
    session = boto3.Session(
        profile_name=configuration.aws_profile, region_name=configuration.aws_region
    )

    if configuration.aws_role_name:
        role_arn = AWS_ROLE_TEMPLATE.format(
            account=configuration.aws_account,
            role_name=configuration.aws_role_name,
        )
        session = _assume_role(session, role_arn, configuration.aws_region)

    client = session.client("codeartifact")
    response = client.get_authorization_token(
        domain=configuration.code_artifact_domain,
        domainOwner=configuration.aws_account,
    )
    return response["authorizationToken"]


def _assume_role(session: boto3.Session, role_arn: str, region: str) -> boto3.Session:
    client = session.client("sts")
    response = client.assume_role(RoleArn=role_arn, RoleSessionName="partifact-session")

    return boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
        region_name=region,
    )
