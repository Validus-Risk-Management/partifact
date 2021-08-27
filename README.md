# pArtifact

pArtifact is a tool to help with configuring and authenticating CodeArtifact as a repository for [Poetry](https://github.com/python-poetry/poetry) and [pip](https://pip.pypa.io/en/stable/).

[AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/codeartifact/login.html) offers functionality to configure CodeArtifact for pip.
This tool offers the following improvements over the CLI:
1. Poetry support.
1. Assuming an AWS role to get the token. This is handy in automated pipelines, which may have the access key and secret key as environment variables,
  but want to install packages from CodeArtifact on a different account.
1. Configuration persisted in a config file, making the tool more convenient to use than the CLI with the options it requires to be passed in from the command line.
