# action-update-version
![ci-badge-checks](https://github.com/outcome-co/action-update-version/workflows/Checks/badge.svg) ![ci-badge-release](https://github.com/outcome-co/action-update-version/workflows/Release/badge.svg)

This Github Action automatically updates the versions of your repositories.

## Description

At each push on the `master` branch, it checks all the commits that have occurred since the previous tag with [Commitizen](https://github.com/commitizen-tools/commitizen), deduces the new version according to the [semantic convention](https://semver.org/) (`MAJOR.MINOR.PATCH`), then bumps the version :
- Update the config and project version (depending on the [use case](https://github.com/outcome-co/action-update-version#use-cases))
- Commit the changes with the message : "chore: bump version `{previous_version}` &rarr; `{new_version}`"
- Add a new tag associated to this commit

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

First, the repo should have [Commitizen](https://github.com/commitizen-tools/commitizen) setup for the Action to work.
You can use `bin/cz_init.sh` to help setup your repo.

Then the Action should be used in a YAML in your Github Workflow: 

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
