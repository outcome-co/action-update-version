"""Setup Commitizen."""

import os

import toml

cz_toml = '.cz.toml'
pyproject = 'pyproject.toml'

version_node = 'package.json'
version_other = 'VERSION'


def setup_cz():
    """Set up Commitizen."""
    if os.path.exists(pyproject):
        if not is_cz_configured(pyproject):
            add_cz_configuration(pyproject)
    elif os.path.exists(cz_toml):
        if not is_cz_configured(cz_toml):
            add_cz_configuration(cz_toml)
    else:
        open(cz_toml, 'a').close()  # noqa: WPS515
        add_cz_configuration(cz_toml)


def is_cz_configured(toml_file):
    """Check if Commitizen is configured in TOML file.

    Args:
        toml_file: (string) path to TOML file

    Returns:
        Boolean. True if Commitizen is configured.
    """
    parsed_toml = toml.load(toml_file)
    if 'commitizen' in parsed_toml['tool'].keys():
        return True
    return False


def add_cz_configuration(toml_file):
    """Configure Commitizen in TOML file.

    Args:
        toml_file: (string) path to TOML file
    """
    cz_configuration = {'tool': {'commitizen': {
        'name': 'cz_conventional_commits',
        'version': '0.1.0',
        'tag_format': '$version',
        'bump_message': 'chore(version): $current_version → $new_version',
        'version_files': ['pyproject.toml:version'],
        }}}
    # TODO: check for version_node / version_other and adapt configuration
    cz_configuration_formatted = toml.dumps(cz_configuration)
    cz_configuration_formatted = '\n{0}'.format(cz_configuration_formatted)
    with open(toml_file, 'a') as filename:
        filename.write(cz_configuration_formatted)


if __name__ == '__main__':
    setup_cz()
