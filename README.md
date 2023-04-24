# partifact

partifact is a tool to help with configuring and authenticating CodeArtifact as a repository for [Poetry](https://github.com/python-poetry/poetry) and [pip](https://pip.pypa.io/en/stable/).

[AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/codeartifact/login.html) offers functionality to configure CodeArtifact for pip.
This tool offers the following improvements over the CLI:
1. Poetry support.
1. Assuming an AWS role to get the token. This is handy in automated pipelines, which may have the access key and secret key as environment variables,
  but want to install packages from CodeArtifact on a different account.
1. Configuration persisted in a config file, making the tool more convenient to use than the CLI with the options it requires to be passed in from the command line.


# How to use it?

Install partifact from pypi using pip the usual way:

```shell
pip install partifact
```

It's best to do this globally, rather than inside the virtualenv.

Before you can use partifact, the Poetry source repository needs to be
[configured](https://python-poetry.org/docs/repositories/#install-dependencies-from-a-private-repository)
in `pyproject.toml`.

```toml
[[tool.poetry.source]]
name = "my-repo"
url = "https://{code_artifact_domain}-{aws_account}.d.codeartifact.{aws_region}.amazonaws.com/pypi/{code_artifact_repository}/simple/"
default = true  # if this should be the default repository to install from
```

If you are publishing to the repository, the `/simple/` suffix is not required at the end.

Once Poetry is configured, you can use the partifact command to authenticate:

```shell
partifact login my-repo
```

> **NOTE**: Make sure your run the command from the directory where your `pyproject.toml` is!


Optionally, you can pass in an AWS profile and/or AWS role to use
for CodeArtifact token generation.

```shell
partifact login myrepo --profile myprofile
partifact login myrepo --role myrole
```

# Known issues

1. The `CodeArtifact` token seems to exceed the maximum length allowed in Windows Credential Manager, resulting
in a misleading `(1783, 'CredWrite', 'The stub received bad data.')` error. The library has been tested on macOS.
