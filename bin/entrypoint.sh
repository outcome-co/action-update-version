#! /bin/bash

if [ -n "$GITHUB_WORKSPACE" ]; then
    cd $GITHUB_WORKSPACE
    echo "Switching to Github Workspace: ${GITHUB_WORKSPACE}"
fi


# Check which mode is run : init or default (bump)
if [ $# == 1 ] && [ $@ == 'init' ]; then
## Initialize repo ##
python ../app/bin/setup_cz.py
exit 0
fi

## Bump version ##

# Get tags from repo
git fetch --tags

# Bump version with Commitizen: checks git log messages since last tag to determine new version
# Then commits a bump version message locally, and tags the new version locally
cz bump --no-verify --yes

# The syntax "::set-output name=[key]::[value]" allows to set outputs inside the Github Workflow
if [ $? -ne 0 ]; then
echo ::set-output name=updated::false
else
echo ::set-output name=updated::true
fi

echo ::set-output name=version::$(cz version --project)
