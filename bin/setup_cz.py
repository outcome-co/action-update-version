"""Setup Commitizen."""

import os

import toml

cz_toml = '.cz.toml'
pyproject = 'pyproject.toml'

version_node = 'package.json'
version_other = 'VERSION'
default_version = '0.1.0'


def setup_cz():
    """Set up Commitizen."""
    if os.path.exists(pyproject):
        if not is_cz_configured(pyproject):
            add_cz_config(pyproject)
    elif os.path.exists(cz_toml):
        if not is_cz_configured(cz_toml):
            add_cz_config(cz_toml)
    else:
        open(cz_toml, 'a').close()  # noqa: WPS515
        add_cz_config(cz_toml)


def is_cz_configured(toml_file):
    """Check if Commitizen is configured in TOML file.

    Args:
        toml_file: (string) path to TOML file

    Returns:
        (boolean) True if Commitizen is configured.
    """
    parsed_toml = toml.load(toml_file)
    if 'commitizen' in parsed_toml['tool'].keys():
        return True
    return False


def add_cz_config(toml_file):
    """Configure Commitizen in TOML file.

    Args:
        toml_file: (string) path to TOML file
    """
    cz_config = {
        'tool': {
            'commitizen': {
                'name': 'cz_conventional_commits',
                'version': default_version,
                'tag_format': '$version',
                'bump_message': 'chore(version): $current_version → $new_version',
            },
        },
    }

    cz_config['tool']['commitizen']['version_files'] = choose_version_file(toml_file)
    cz_config_formatted = toml.dumps(cz_config)
    cz_config_formatted = '\n{0}'.format(cz_config_formatted)
    with open(toml_file, 'a') as filename:
        filename.write(cz_config_formatted)


def choose_version_file(toml_file):
    if toml_file == 'pyproject.toml':
        return ['{0}:version'.format(toml_file)]
    elif os.path.exists(version_node):
        return ['{0}:version'.format(version_node)]
    if not os.path.exists(version_other):
        with open(version_other, 'w') as file:
            file.write(default_version)
    return [version_other]


if __name__ == '__main__':
    setup_cz()
