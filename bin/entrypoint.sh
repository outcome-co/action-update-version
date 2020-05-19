#! /bin/bash

if [ -n "$GITHUB_WORKSPACE" ]; then
    cd $GITHUB_WORKSPACE
    echo "Switching to Github Workspace: ${GITHUB_WORKSPACE}"
fi

git fetch --tags
cz bump --no-verify --yes
if [ $? -ne 0 ]; then
echo ::set-output name=updated::false
else
echo ::set-output name=updated::true
fi
echo ::set-output name=version::$(cz version --project)
