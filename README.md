# action-update-version
![ci-badge-checks](https://github.com/outcome-co/action-update-version/workflows/Checks/badge.svg) ![ci-badge-release](https://github.com/outcome-co/action-update-version/workflows/Release/badge.svg)

This Github Action automatically updates the versions of your repositories.

## Description

At each push on the `master` branch, it checks all the commits that have occurred since the previous tag, deduces the new version according to the [semantic convention](https://semver.org/) (`MAJOR.MINOR.PATCH`), then bumps the version :
- Update the config file (depending on your [programming language](https://github.com/outcome-co/action-update-version#supported-languages))
- Commit the changes with the message : "chore: bump version `{previous_version}` &rarr; `{new_version}`"
- Add a new tag associated to this commit

> If no tag is found at the first run, by default the first version will be `0.1.0`.

The increments are based on commit types, with the following configuration: 

| Increment | Description                 | Conventional commit map             |
| --------- | --------------------------- | ----------------------------------- |
| `MAJOR`   | Breaking changes introduced | `BREAKING CHANGE` or `!` before type|
| `MINOR`   | New features                | `feat`                              |
| `PATCH`   | Fixes                       | `fix`, `refactor` or `perf`         |

Other types don't trigger any version bump.

### Supported languages

For the moment, only Python projects with a `pyproject.toml` config file are supported.

## Usage

The Action should be added to your Github Workflow in a YAML file : 

```yaml
name: "Update Version"

on:
  push:
    branches:
      - master

jobs:
    update_version:
      name: "Update Version"
      runs-on: ubuntu-latest
      if: "!contains(github.event.head_commit.message, 'chore: bump version')"

      steps:
        - name: "Check out code"
          uses: actions/checkout@v2
          with:
            token: ${{ secrets.OTTO_TOKEN }}
            fetch-depth: 0

        - name: "Log Otto"
          run: |
            git config --local user.email "otc-builder@outcome.co"
            git config --local user.name "Otto the Bot"

        - name: "Bump version"
          id: bump_version
          uses: outcome-co/action-update-version@master

        - name: "Push new version"
          if: ${{ steps.bump_version.outputs.updated == 'true' }}
          run: git push && git push --follow-tags --tags
```

**Don't forget to adapt the other Actions to avoid the creation of Github Actions loops.**

For example, a `Release` Action is only run on `master`, if there is a new version to deploy.
To do this, we can trigger the Action only if the commit message contains "chore: bump version". So the beginning of `release.yaml` will look like :

```yaml
name: Release

on:
  push:
    branches:
      - master

jobs:
    build_push:
      name: "Build & push Docker image"
      runs-on: ubuntu-latest
      if: "contains(github.event.head_commit.message, 'chore: bump version')"
```

## Development

Remember to run `./pre-commit.sh` when you clone the repository.
