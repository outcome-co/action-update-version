"""Setup Commitizen."""

import json
import logging
import os
import sys

import toml

cz_toml = '.cz.toml'
pyproject = 'pyproject.toml'

version_node = 'package.json'
version_other = 'VERSION'
default_version = '0.1.0'


def setup_cz():
    if is_cz_config_needed(pyproject):
        add_cz_config(pyproject)
    elif is_cz_config_needed(cz_toml):
        add_cz_config(cz_toml)
    else:
        add_cz_config(cz_toml)


def is_cz_config_needed(toml_file):
    if os.path.exists(toml_file):
        logging.info(f'{toml_file} exists')

        if is_cz_in_toml(toml_file):
            logging.info(f'{toml_file} already configured with Commitizen')
            sys.exit()

        logging.info(f'{toml_file} not configured with Commitizen')
        return True

    logging.info(f'{toml_file} not found')
    return False


def is_cz_in_toml(toml_file):
    parsed_toml = toml.load(toml_file)
    if 'commitizen' in parsed_toml['tool'].keys():
        return True
    return False


def add_cz_config(toml_file):
    version, version_file = get_version_and_filepath(toml_file)
    logging.info(f'Version set to {version} with filepath {version_file}')

    cz_config = cz_config_template(version, version_file)
    with open(toml_file, 'a') as filename:
        filename.write(cz_config)
    logging.info(f'Commitizen config added to {toml_file}')


def get_version_and_filepath(toml_file):
    if toml_file == pyproject:
        parsed_toml = toml.load(toml_file)
        return parsed_toml['tool']['poetry']['version'], [f'{toml_file}:version']

    elif os.path.exists(version_node):
        parsed_json = json.load(open(version_node))  # noqa: WPS515
        return parsed_json['version'], [f'{version_node}:version']

    create_version_other_if_needed()
    file = open(version_other, 'r')  # noqa: WPS515
    return file.readline(), [version_other]


def create_version_other_if_needed():
    if not os.path.exists(version_other):
        with open(version_other, 'w') as file:
            file.write(default_version)


def cz_config_template(version, version_file):
    cz_config = {
        'tool': {
            'commitizen': {
                'name': 'cz_conventional_commits',
                'version': version,
                'tag_format': '$version',
                'bump_message': 'chore(version): $current_version → $new_version',
                'version_files': version_file,
            },
        },
    }
    cz_config_formatted = toml.dumps(cz_config)
    return '\n{0}'.format(cz_config_formatted)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    setup_cz()
