"""Set up Commitizen.

If there is a pyproject.toml file in the directory, we'll use that to store the cz config,
otherwise we'll use .cz.toml.

The script will detect the version files to update, either pyproject.toml, package.json, or VERSION.
"""

import json
import logging
import sys
from pathlib import Path

import toml
import tomlkit
from tomlkit.toml_document import TOMLDocument

cz_toml = Path('.cz.toml')
pyproject = Path('pyproject.toml')
package_json = Path('package.json')
version_other = Path('VERSION')

default_version = '0.1.0'

CZ_TEMPLATE = """[tool.commitizen]
name = "cz_conventional_commits"
version = ""
tag_format = "v$version"
bump_message = "chore(version): $current_version → $new_version"
version_files = []
\n"""


def main() -> None:
    if pyproject.exists():
        if is_cz_in_toml(pyproject):
            logging.info(f'cz already configured in {pyproject}')
        else:
            add_cz_config(pyproject)

    elif cz_toml.exists():
        if not is_cz_in_toml(cz_toml):
            logging.error(f'{cz_toml} exists, but does not contain valid config!')
            sys.exit(-1)

        logging.info(f'cz already configured in {cz_toml}')

    else:
        add_cz_config(cz_toml)


def is_cz_in_toml(toml_file: Path) -> bool:
    """Check if the TOML file contains CZ config.

    Args:
        toml_file (Path): The TOML file to check.

    Returns:
        bool: True if the file contains CZ config
    """
    toml_parsed = toml.load(toml_file)
    return 'commitizen' in toml_parsed['tool'].keys()


def add_cz_config(toml_file: Path) -> None:  # pragma: no cover
    logging.info(f'Adding Commitizen config to {toml_file}')

    version, version_file = get_current_version_info()
    logging.info(f'Version set to {version} with filepath {version_file}')

    cz_config = get_cz_config(version, version_file)
    current_config = get_current_config(toml_file)

    new_config = merge_current_and_cz(current_config, cz_config)
    write_new_config(toml_file, new_config)


def get_current_version_info() -> (str, str):
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
        return version, str(version_other)

    with open(version_other, 'w') as version_other_handle:
        version_other_handle.write(f'{default_version}\n')

    return default_version, str(version_other)


def get_cz_config(version: str, version_file: str) -> TOMLDocument:
    cz_parsed = tomlkit.parse(CZ_TEMPLATE)
    cz_parsed['tool']['commitizen']['version'] = version
    cz_parsed['tool']['commitizen']['version_files'].append(version_file)
    return cz_parsed


def get_current_config(toml_file: Path) -> TOMLDocument:  # pragma: no cover
    if toml_file.exists():
        with open(toml_file, 'r') as f_read:
            return tomlkit.parse(f_read.read())
    return tomlkit.document()


def merge_current_and_cz(current_config: TOMLDocument, cz_config: TOMLDocument) -> TOMLDocument:
    merged = current_config.as_string() + cz_config.as_string()
    return tomlkit.parse(merged)


def write_new_config(toml_file: Path, new_config: TOMLDocument) -> None:  # pragma: no cover
    with open(toml_file, 'w') as f_write:
        f_write.write(tomlkit.dumps(new_config))


if __name__ == '__main__':  # pragma: no cover
    logging.getLogger().setLevel(logging.INFO)
    main()
