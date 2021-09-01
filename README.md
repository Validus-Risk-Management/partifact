# pArtifact

pArtifact is a tool to help with configuring and authenticating CodeArtifact as a repository for [Poetry](https://github.com/python-poetry/poetry) and [pip](https://pip.pypa.io/en/stable/).

[AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/codeartifact/login.html) offers functionality to configure CodeArtifact for pip.
This tool offers the following improvements over the CLI:
1. Poetry support.
1. Assuming an AWS role to get the token. This is handy in automated pipelines, which may have the access key and secret key as environment variables,
  but want to install packages from CodeArtifact on a different account.
1. Configuration persisted in a config file, making the tool more convenient to use than the CLI with the options it requires to be passed in from the command line.


# How to use?

Install pArtifact from pypi using pip the usual way:

```shell
pip install partifact
```

It's best to do this globally, rather than inside the virtualenv.

Before you can use pArtifact, you need to configure it for your project
in the `pyproject.toml` file.

In the future, this will be done via a configuration tool.
For now, however, add the following to the file manually:

```toml
[tool.partifact.repository.POETRY_REPOSITORY_NAME]
code_artifact_account = "your-aws-account-hosting-codeartifact"
code_artifact_domain = "your-domain-name"
code_artifact_repository = "your-codeartifact-repository"  # not the same as the Poetry repository
aws_profile = "your-aws-profile"  # optional
aws_role_arn = "an-aws-role-to-assume"  # optional
```

Replace `POETRY_REPOSITORY_NAME` with your Poetry repository name. E.g. for the following
Poetry configuration:

```toml
[[tool.poetry.source]]
name = "myrepo"
url = "https://myrepo-codeartifact-url"
```

`POETRY_REPOSITORY_NAME` should be set to "myrepo".

The configuration entries are:
1. `code_artifact_account`: The account hosting the CodeArtifact repository.
2. `code_artifact_domain`: The [CodeArtifact domain](https://docs.aws.amazon.com/codeartifact/latest/ug/domains.html).
3. `code_artifact_repository`: The [CodeArtifact repository](https://docs.aws.amazon.com/codeartifact/latest/ug/repos.html).
4. `aws_profile` (optional): Use a non-default AWS profile to get the CodeArtifact token.
5. `aws_role_arn` (optional): Assume and use this AWS role to get the CodeArtifact token.
This is useful in deployment pipelines, where ENV variables are used for the AWS
access key and secret key and the keys are for the account it's deploying the application
in, rather than the CodeArtifact account.

Once everything is configured, you can log into CodeArtifact using the
pArtifact login command:

```shell
partifact login [POETRY_REPOSITORY_NAME]
```
