# action-update-version
![ci-badge-checks](https://github.com/outcome-co/action-update-version/workflows/Release/badge.svg?branch=v0.9.0) ![version-badge](https://img.shields.io/badge/version-0.9.0-brightgreen)

This Github Action automatically updates the versions of your repositories.

## Description

At each push on the chosen branches, it checks all the commits (using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)) that have occurred since the previous tag with [Commitizen](https://github.com/commitizen-tools/commitizen), deduces the new version according to the [Semantic Versioning](https://semver.org/), then bumps the version:
- Updates the config and project version (depending on the [use case](https://github.com/outcome-co/action-update-version#use-cases))
- Commits the changes with the message : "chore(version): `{previous_version}` &rarr; `{new_version}`"
- Adds a new tag associated to this commit

The increments are based on commit types, with the following configuration: 

| Increment | Description                 | Conventional commit map             |
| --------- | --------------------------- | ----------------------------------- |
| `MAJOR`   | Breaking changes introduced | `BREAKING CHANGE` or `!` before type|
| `MINOR`   | New features                | `feat`                              |
| `PATCH`   | Fixes                       | `fix`, `refactor` or `perf`         |

Other types don't trigger any version bump.

### Use Cases

3 use cases currently exist:
- For Python projects, both the project version and commitizen config are in `pyproject.toml`
- For Node projects, the project version is updated in `package.json`, and Commitizen config is in `.cz.toml`
- For other projects, the project version is updated in `VERSION`, and Commitizen config is in `.cz.toml`

## Usage

### Setup
The repo should have [Commitizen](https://github.com/commitizen-tools/commitizen) set up for the Action to work.

To set up Commitizen on a repo, you can run
```bash
docker run -v $(pwd):/work -w /work outcomeco/action-update-version:latest init
```
This will add the configuration in `pyproject.toml` or `.cz.toml`.
> Note: If Commitizen is already configured, it won't update the configuration.

### Github Action
The Action should be used in a YAML in your Github Workflow:

```yaml
name: "Update Version"

on:
  push:
    branches:
      - [your_branch]

# If you have other Actions running on the same branch, don't forget to adapt them to avoid the creation
# of Github Actions loops. For example, if you have a Release Action, the condition could be :
# on:
#   push:
#     branches:
#       - [your_branch]
#     tags:
#       - "*"

jobs:
    update_version:
      name: "Update Version"
      runs-on: ubuntu-latest
      if: "!contains(github.event.head_commit.message, 'chore(version): ')"

      steps:
        - name: "Check out code"
          uses: actions/checkout@v2
          with:
            token: ${{ secrets.TOKEN }}
            fetch-depth: 0

        - name: "Configure Git User"
          run: |
            git config --local user.email "your@email.com"
            git config --local user.name "Your Name"

        - name: "Bump version"
          id: bump_version
          uses: outcome-co/action-update-version@master

        - name: "Push new version"
          if: ${{ steps.bump_version.outputs.updated == 'true' }}
          run: git push && git push --follow-tags --tags
```

## Personal Access Token

To use the Action, you'll need a personal access token: `${{ secrets.TOKEN }}`.

If you want to use the Action on protected branches, the token should have push access to the repo. It will be used to clone it, commit the changes, add tags, and push back on the repo.

Otherwise, you can just use the [Github Action Token](https://help.github.com/en/actions/configuring-and-managing-workflows/authenticating-with-the-github_token).

## Development

Remember to run `./pre-commit.sh` when you clone the repository.
