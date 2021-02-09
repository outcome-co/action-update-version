"""Set up Commitizen.

If there is a pyproject.toml file in the directory, we'll use that to store the cz config,
otherwise we'll use .cz.toml.

The script will detect the version files to update, either pyproject.toml, package.json, or config.cfg.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple, Type, TypeVar, Union, cast

import tomlkit
import typer
from commitizen import cmd
from tomlkit.container import Container
from tomlkit.items import Item, String, Table
from tomlkit.toml_document import TOMLDocument

app = typer.Typer()
_read_mode = 'r'


@app.command()
def bump():
    # Retrieve existing tags
    run('git fetch --tags')

    # Run commitizen
    result = run('cz bump --no-verify --yes')
    updated = not any(line == 'increment detected: None' for line in result.out.splitlines())

    _set_github_output_variable('updated', str(updated).lower())

    current_version = run('cz version --project')

    _set_github_output_variable('version', current_version.out)


def run(command: str) -> cmd.Command:
    result = cmd.run(command)
    assert result.return_code == 0  # noqa: S101
    return result


def _set_github_output_variable(key: str, value: str):
    typer.echo(f'::set-output name={key}::{value}')


cz_toml = Path('.cz.toml')
pyproject = Path('pyproject.toml')
package_json = Path('package.json')
version_other = Path('config.cfg')

default_version = '0.1.0'

CZ_TEMPLATE = """[tool.commitizen]
name = "cz_conventional_commits"
version = ""
tag_format = "v$version"
bump_message = "chore(version): $current_version → $new_version"
version_files = ["README.md:version-badge"]
\n"""


def _pyproject_exists():
    return pyproject.exists()


def _cz_toml_exists():
    return cz_toml.exists()


def _package_json_exists():
    return package_json.exists()


def _version_other_exists():
    return version_other.exists()


_already_exists_exit_code = 10
_misconfigured = 11


@app.command()
def init() -> None:  # noqa: WPS231 - too high complexity
    if _pyproject_exists():
        if is_cz_in_toml(pyproject):
            typer.echo(f'cz already configured in {pyproject}', err=True)
            sys.exit(_already_exists_exit_code)
        else:
            add_cz_config(pyproject)

    elif _cz_toml_exists():
        if not is_cz_in_toml(cz_toml):
            typer.echo(f'{cz_toml} exists, but does not contain valid config!', err=True)
            sys.exit(_misconfigured)

        typer.echo(f'cz already configured in {cz_toml}', err=True)
        sys.exit(_already_exists_exit_code)

    else:
        add_cz_config(cz_toml)


T = TypeVar('T', Table, Container, Item)


def get_from_toml(toml: Union[Container, Table], key: str, expected_type: Type[T]) -> T:
    result = toml[key]
    assert isinstance(result, expected_type)  # noqa: S101
    return result


def is_cz_in_toml(toml_file: Path) -> bool:
    """Check if the TOML file contains CZ config.

    Args:
        toml_file (Path): The TOML file to check.

    Returns:
        bool: True if the file contains CZ config
    """
    with open(toml_file, _read_mode) as file:
        toml_str = file.read()
    toml_parsed = tomlkit.loads(toml_str)

    tool = get_from_toml(toml_parsed, 'tool', Table)
    return 'commitizen' in tool.keys()


def add_cz_config(toml_file: Path) -> None:
    typer.echo(f'Adding Commitizen config to {toml_file}')

    version, version_file = get_current_version_info()
    typer.echo(f'Version set to {version} with filepath {version_file}')

    cz_config = get_cz_config(version, version_file)
    current_config = get_current_config(toml_file)

    new_config = merge_current_and_cz(current_config, cz_config)
    write_new_config(toml_file, new_config)


def get_current_version_info() -> Tuple[str, str]:
    if _pyproject_exists():
        with open(pyproject, _read_mode) as py_file:
            py_toml_str = py_file.read()
        parsed_toml = tomlkit.loads(py_toml_str)

        tool = get_from_toml(parsed_toml, 'tool', Table)
        poetry = get_from_toml(tool, 'poetry', Table)
        version = get_from_toml(poetry, 'version', String)

        return str(version), f'{pyproject}:version'

    if _package_json_exists():
        parsed_json = json.load(open(package_json))  # noqa: WPS515
        return parsed_json['version'], f'{package_json}:version'

    if _version_other_exists():
        version = open(version_other, _read_mode).read().strip()  # noqa: WPS515
        return version, str(version_other)

    with open(version_other, 'w') as version_other_handle:
        version_other_handle.write(f'{default_version}\n')

    return default_version, str(version_other)


def get_cz_config(version: str, version_file: str) -> TOMLDocument:
    cz_parsed = tomlkit.parse(CZ_TEMPLATE)

    tool = get_from_toml(cz_parsed, 'tool', Table)
    commitizen = get_from_toml(tool, 'commitizen', Table)

    commitizen['version'] = version

    version_files = cast(List[str], commitizen['version_files'])
    version_files.append((version_file))

    return cz_parsed


def get_current_config(toml_file: Path) -> TOMLDocument:
    if toml_file.exists():
        with open(toml_file, _read_mode) as f_read:
            return tomlkit.parse(f_read.read())
    return tomlkit.document()


def merge_current_and_cz(current_config: TOMLDocument, cz_config: TOMLDocument) -> TOMLDocument:
    # As current_config and cz_config are both already TOMLDocuments, the format returned by tomlkit method
    # "as_string()" will include every details needed to preserve the TOMLDocument style when merging
    merged = current_config.as_string() + cz_config.as_string()
    # Then we ensure the format is still valid by parsing the merged string in a TOMLDocument again
    return tomlkit.parse(merged)


def write_new_config(toml_file: Path, new_config: TOMLDocument) -> None:
    with open(toml_file, 'w') as f_write:
        f_write.write(tomlkit.dumps(new_config))


if __name__ == '__main__':  # pragma: no cover
    app()
