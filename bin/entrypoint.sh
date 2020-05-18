#! /bin/bash

if [ -n "$GITHUB_WORKSPACE" ]; then
    cd $GITHUB_WORKSPACE
    echo "Switching to Github Workspace: ${GITHUB_WORKSPACE}"
fi

PYPROJECT=pyproject.toml
PYPROJECT_CZ_CONFIG="[tool.commitizen]"
PYPROJECT_CONFIG=$"\n\
[tool.commitizen]\n\
name = 'cz_conventional_commits'\n\
version = '0.1.0'\n\
tag_format = '\$version'\n\
bump_message = 'chore: bump version \$current_version → \$new_version'\n\
version_files = [\n\
  'pyproject.toml:version'\n\
]"

PACKAGE_JSON=package.json

if test -f "$PYPROJECT"; then
    if ! grep -Fxq "$PYPROJECT_CZ_CONFIG" "$PYPROJECT"; then
        echo -e "$PYPROJECT_CONFIG" >> "$PYPROJECT"
    fi
elif test -f "$PACKAGE_JSON"; then
    echo To be implemented
fi

git fetch --tags
cz bump --no-verify --yes
if [ $? -ne 0 ]; then
echo ::set-output name=updated::false
else
echo ::set-output name=updated::true
fi
echo ::set-output name=version::$(cz version --project)
