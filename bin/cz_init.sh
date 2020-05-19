PYPROJECT=pyproject.toml
CZ_TOML=.cz.toml
PACKAGE_JSON=package.json
DEFAULT_VERSION=VERSION

CZ_CONFIG="[tool.commitizen]"
BASE_CONFIG="\n\
[tool.commitizen]\n\
name = 'cz_conventional_commits'\n\
version = '0.1.0'\n\
tag_format = '\$version'"

MESSAGE_CONFIG="bump_message = 'chore: bump version \$current_version → \$new_version'"
VERSION_FILE_PYPROJECT="version_files = ['pyproject.toml:version']"
VERSION_FILE_NPM="version_files = ['package.json:version']"
VERSION_FILE_OTHER="version_files = ['VERSION']"

if test -f "$PYPROJECT" && ! grep -Fxq "$CZ_CONFIG" "$PYPROJECT"; then
    echo "$BASE_CONFIG">> "$PYPROJECT"
    echo "$MESSAGE_CONFIG">> "$PYPROJECT"
    echo "$VERSION_FILE_PYPROJECT">> "$PYPROJECT"

elif ! test -f "$PYPROJECT" && ! test -f "$CZ_TOML"; then
    echo "$BASE_CONFIG">> "$CZ_TOML"
    echo "$MESSAGE_CONFIG">> "$CZ_TOML"

    if test -f "$PACKAGE_JSON"; then
        echo "$VERSION_FILE_NPM">> "$CZ_TOML"

    elif test -f "$DEFAULT_VERSION"; then
        echo "$VERSION_FILE_OTHER">> "$CZ_TOML"
    else
        echo "$VERSION_FILE_OTHER">> "$CZ_TOML"
        echo "0.1.0">> "$DEFAULT_VERSION"
    fi
fi
