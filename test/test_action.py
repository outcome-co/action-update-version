"""Test module Setup Commitizen."""

import json
from typing import Generator, List, Optional

import pytest
import tomlkit
from click.testing import Result
from commitizen import cmd
from py import path
from syrupy.assertion import SnapshotAssertion
from tomlkit.items import String, Table
from typer.testing import CliRunner

from src import action

TEST_CZ_TEMPLATE = """[tool.commitizen]
name = "cz_conventional_commits"
version = "1.1.1"
tag_format = "v$version"
bump_message = "chore(version): $current_version → $new_version"
version_files = ["README.md:version-badge", "pyproject.toml:version"]
\n"""


PYPROJECT_TOML = """[tool.poetry]
name = "action-update-version"
version = "0.10.8"
\n"""

runner = CliRunner(mix_stderr=False)

_already_exists_exit_code = 10
_misconfigured = 11


@pytest.fixture()
def clean_dir(tmpdir: path.local) -> Generator[path.local, None, None]:
    with tmpdir.as_cwd():
        yield tmpdir


@pytest.fixture()
def tmp_git_project(clean_dir: path.local) -> Generator[path.local, None, None]:
    with clean_dir.as_cwd():
        cmd.run('git init')
        yield clean_dir


@pytest.fixture()
def tmp_commitizen_project(tmp_git_project: path.local) -> Generator[path.local, None, None]:
    with tmp_git_project.as_cwd():
        tmp_commitizen_cfg_file = tmp_git_project.join('pyproject.toml')
        tmp_commitizen_cfg_file.write('[tool.commitizen]\nversion="0.1.0"\n')

        cmd.run('git add pyproject.toml')
        cmd.run('git commit -m "build: add pyproject.toml"')

        yield tmp_git_project


def github_variable_set(result: Result, key: str, value: str) -> bool:
    o = f'::set-output name={key}::{value}'
    return any(line == o for line in result.output.splitlines())


def commitizen_in_toml(path: path.local, version: str, version_files: Optional[List[str]] = None) -> bool:
    contents = path.read_text('utf-8')
    parsed = tomlkit.parse(contents)

    try:
        tool = action.get_from_toml(parsed, 'tool', Table)
        commitizen = action.get_from_toml(tool, 'commitizen', Table)
        read_version = action.get_from_toml(commitizen, 'version', String)

        if version_files:
            read_version_files = commitizen['version_files']
            assert isinstance(read_version_files, list)

            if set(version_files) != set(read_version_files):
                return False

        return version == read_version
    except Exception:
        return False


def poetry_in_toml(path: path.local) -> bool:
    contents = path.read_text('utf-8')
    parsed = tomlkit.parse(contents)

    tool = action.get_from_toml(parsed, 'tool', Table)

    return 'poetry' in tool.keys()


def check_success(result: Result) -> None:
    if result.exit_code == 0:
        return

    print(result.stderr)  # noqa: T001, WPS421
    print(result.stdout)  # noqa: T001, WPS421

    if result.exception:
        print(result.exception)  # noqa: T001, WPS421

    assert result.exit_code == 0


@pytest.mark.usefixtures('tmp_commitizen_project')
class TestBump:
    def test_bump(self, tmp_commitizen_project: path.local):
        some_file = tmp_commitizen_project.join('some_file')
        some_file.write('content')

        cmd.run('git add some_file')
        cmd.run('git commit -m "feat: add some_file"')

        result = runner.invoke(action.app, ['bump'])

        assert result.exit_code == 0
        assert github_variable_set(result, 'updated', 'true')
        assert github_variable_set(result, 'version', '0.2.0')

    def test_no_bump(self, tmp_commitizen_project: path.local):
        some_file = tmp_commitizen_project.join('some_file')
        some_file.write('content')

        cmd.run('git add some_file')
        cmd.run('git commit -m "chore: add some_file"')

        result = runner.invoke(action.app, ['bump'])

        assert result.exit_code == 0
        assert github_variable_set(result, 'updated', 'false')
        assert github_variable_set(result, 'version', '0.1.0')


class TestInitPyProject:
    def test_already_exists(self, clean_dir: path.local):
        pyproject = clean_dir.join('pyproject.toml')
        pyproject.write(TEST_CZ_TEMPLATE)

        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == _already_exists_exit_code
        assert 'cz already configured' in result.stderr

    def test_add_config(self, clean_dir: path.local):
        pyproject = clean_dir.join('pyproject.toml')
        pyproject.write(PYPROJECT_TOML)

        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == 0
        assert 'Adding Commitizen config to' in result.stdout
        assert commitizen_in_toml(pyproject, '0.10.8')
        assert poetry_in_toml(pyproject)


class TestInitNonPyproject:
    def test_add_config(self, clean_dir: path.local):
        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == 0
        assert 'Adding Commitizen config to' in result.stdout

        cz_toml = clean_dir.join('.cz.toml')
        assert commitizen_in_toml(cz_toml, '0.1.0')

    def test_misconfigured(self, clean_dir: path.local):
        cz_toml = clean_dir.join('.cz.toml')
        cz_toml.write(PYPROJECT_TOML)

        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == _misconfigured
        assert 'but does not contain valid config' in result.stderr

    def test_already_configured(self, clean_dir: path.local):
        cz_toml = clean_dir.join('.cz.toml')
        cz_toml.write(TEST_CZ_TEMPLATE)

        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == _already_exists_exit_code
        assert 'cz already configured in' in result.stderr


class TestGetCurrentVersion:
    def test_get_package_json_version(self, clean_dir: path.local):
        package_json = clean_dir.join('package.json')
        package_json.write(json.dumps({'version': '0.1.2'}))
        assert action.get_current_version_info() == ('0.1.2', 'package.json:version')

    def test_get_pyproject_version(self, clean_dir: path.local):
        package_json = clean_dir.join('pyproject.toml')
        package_json.write(PYPROJECT_TOML)
        assert action.get_current_version_info() == ('0.10.8', 'pyproject.toml:version')

    def test_get_other_version(self, clean_dir: path.local):
        version_file = clean_dir.join('config.cfg')
        version_file.write('1.0.0')
        assert action.get_current_version_info() == ('1.0.0', 'config.cfg')

    def test_get_no_version(self, clean_dir: path.local):
        version_file = clean_dir.join('config.cfg')

        assert not version_file.exists()
        assert action.get_current_version_info() == ('0.1.0', 'config.cfg')
        assert version_file.exists()


class TestAddCzInfo:
    def test_correct_version_is_added(self, clean_dir: path.local):
        version_file = clean_dir.join('config.cfg')
        version_file.write('1.2.3')

        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == 0

        cz_toml = clean_dir.join('.cz.toml')
        assert commitizen_in_toml(cz_toml, '1.2.3', ['config.cfg', 'README.md:version-badge'])

    def test_snapshot(self, clean_dir: path.local, snapshot: SnapshotAssertion):
        pyproject = clean_dir.join('pyproject.toml')
        pyproject.write(PYPROJECT_TOML)

        result = runner.invoke(action.app, ['init'])

        assert result.exit_code == 0

        contents = pyproject.read_text('utf-8')
        assert contents == snapshot
