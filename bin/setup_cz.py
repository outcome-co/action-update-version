"""Set up Commitizen.

If there is a pyproject.toml file in the directory, we'll use that to store the cz config,
otherwise we'll use .cz.toml.

The script will detect the version files to update, either pyproject.toml, package.json, or VERSION.
"""

import json
import logging
from pathlib import Path
import sys

import toml

cz_toml = Path('.cz.toml')
pyproject = Path('pyproject.toml')
package_json = Path('package.json')
version_other = Path('VERSION')

default_version = '0.1.0'


def main():
    if pyproject.exists():
        if not is_cz_in_toml(pyproject):
            add_cz_config(pyproject)
        else:
            logging.info(f'cz already configured in {pyproject}')

    elif cz_toml.exists():
        if not is_cz_in_toml(cz_toml):
            logging.error(f'{cz_toml} exists, but does not contain valid config!')
            sys.exit(-1)

        logging.info(f'cz already configured in {cz_toml}')

    else:
        add_cz_config(cz_toml)


def is_cz_in_toml(toml_file):
    """Check if the TOML file contains CZ config.

    Args:
        toml_file (Path): The TOML file to check.

    Returns:
        bool: True if the file contains CZ config
    """
    parsed_toml = toml.load(toml_file)
    return 'commitizen' in parsed_toml['tool'].keys()


def add_cz_config(toml_file):
    logging.info(f'Adding Commitizen config to {toml_file}')

    version, version_file = get_current_version_info()
    logging.info(f'Version set to {version} with filepath {version_file}')

    cz_config = cz_config_template(version, version_file)

    existing_config = {}

    if toml_file.exists():
        with open(toml_file, 'r') as toml_file_handle:
            existing_config = toml.load(toml_file_handle)

    config = {**existing_config, **cz_config}

    with open(toml_file, 'w') as toml_file_handle:
        toml.dump(config, toml_file_handle)


def get_current_version_info():
    """Determines the version file and current version.

    Returns:
        Tuple[str, Path]: The current version number and the version file.
    """
    if pyproject.exists():
        parsed_toml = toml.load(pyproject)
        return parsed_toml['tool']['poetry']['version'], f'{pyproject}:version'

    if package_json.exists():
        parsed_json = json.load(open(package_json))  # noqa: WPS515
        return parsed_json['version'], f'{package_json}:version'

    if version_other.exists():
        version = open(version_other, 'r').read().strip()  # noqa: WPS515
        return version, version_other

    with open(version_other, 'w') as version_other_handle:
        version_other_handle.write(f'{default_version}\n')

    return default_version, version_other


def cz_config_template(version, version_file):
    return {
        'tool': {
            'commitizen': {
                'name': 'cz_conventional_commits',
                'version': version,
                'tag_format': 'v$version',
                'bump_message': 'chore(version): $current_version → $new_version',
                'version_files': [version_file],
            },
        },
    }


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
