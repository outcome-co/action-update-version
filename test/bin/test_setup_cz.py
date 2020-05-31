"""Test module Setup Commitizen."""

from unittest.mock import patch

import pytest
import tomlkit

from bin import setup_cz

TEST_CZ_TEMPLATE = """[tool.commitizen]
name = "cz_conventional_commits"
version = "1.1.1"
tag_format = "v$version"
bump_message = "chore(version): $current_version → $new_version"
version_files = ["pyproject.toml:version"]
\n"""


def side_effect_pyproject_false(arg):  # noqa: WPS430
    if arg == setup_cz.pyproject:
        return False
    return True


def side_effect_pyproject_and_package_false(arg):  # noqa: WPS430
    if arg in {setup_cz.pyproject, setup_cz.package_json}:
        return False
    return True


class TestMain:
    @patch('pathlib.Path.exists', return_value=True, autospec=True)
    @patch('bin.setup_cz.is_cz_in_toml', return_value=True, autospec=True)
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_pyproject_exist_and_configured(self, mock_add_cz_config, mock_is_cz_in_toml, mock_path_exists):
        setup_cz.main()
        mock_add_cz_config.assert_not_called()

    @patch('pathlib.Path.exists', return_value=True, autospec=True)
    @patch('bin.setup_cz.is_cz_in_toml', return_value=False, autospec=True)
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_pyproject_exist_and_not_configured(self, mock_add_cz_config, mock_is_cz_in_toml, mock_path_exists):
        setup_cz.main()
        mock_add_cz_config.assert_called_with(setup_cz.pyproject)

    @patch('pathlib.Path.exists', autospec=True)
    @patch('bin.setup_cz.is_cz_in_toml', return_value=True, autospec=True)
    @patch('logging.info', autospec=True)
    def test_cz_toml_exist_and_configured(self, mock_logging_info, mock_is_cz_in_toml, mock_path_exists):
        mock_path_exists.side_effect = side_effect_pyproject_false
        setup_cz.main()
        mock_logging_info.assert_called()

    @patch('pathlib.Path.exists', autospec=True)
    @patch('bin.setup_cz.is_cz_in_toml', return_value=False, autospec=True)
    @patch('logging.error', autospec=True)
    def test_cz_toml_exist_and_not_configured(self, mock_logging_error, mock_is_cz_in_toml, mock_path_exists):
        mock_path_exists.side_effect = side_effect_pyproject_false
        with pytest.raises(SystemExit):
            setup_cz.main()
            mock_logging_error.assert_called()

    @patch('pathlib.Path.exists', return_value=False, autospec=True)
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_else(self, mock_add_cz_config, mock_path_exists):
        setup_cz.main()
        mock_add_cz_config.assert_called_with(setup_cz.cz_toml)


class TestCzInToml:
    toml_configured = {'tool': {'commitizen': {'name': 'test'}}}
    toml_not_configured = {'tool': {'poetry': {'name': 'test'}}}

    @pytest.mark.parametrize('test_input, expected', [(toml_configured, True), (toml_not_configured, False)])
    @patch('toml.load', autospec=True)
    def test_cz_is_in_toml(self, mock_toml_load, test_input, expected):
        mock_toml_load.return_value = test_input
        assert setup_cz.is_cz_in_toml('toml_file_configured') is expected


class TestMergeExistingAndCz:
    @pytest.fixture
    def init_configs(self):
        return tomlkit.document(), tomlkit.document()

    def test_merge_empty_docs(self, init_configs):
        merged = setup_cz.merge_existing_and_cz(init_configs[0], init_configs[1])
        assert merged == tomlkit.document()

    def test_merge_docs(self, init_configs):
        init_configs[0].add('test_0', '0')
        init_configs[1].add('test_1', '1')
        merged = setup_cz.merge_existing_and_cz(init_configs[0], init_configs[1])
        assert merged == {'test_0': '0', 'test_1': '1'}


class TestGetCurrentVersion:
    @patch('pathlib.Path.exists', return_value=True, autospec=True)
    @patch('toml.load', autospec=True)
    def test_pyproject_exists(self, mock_toml_load, mock_path_exists):
        mock_toml_load.return_value = {'tool': {'poetry': {'version': '1.1.1'}}}
        results = setup_cz.get_current_version_info()
        assert results == ('1.1.1', f'{setup_cz.pyproject}:version')

    @patch('pathlib.Path.exists', autospec=True)
    @patch('json.load', autospec=True)
    @patch('builtins.open', autospec=True)
    def test_package_json_exists(self, mock_open, mock_json_load, mock_path_exists):
        mock_path_exists.side_effect = side_effect_pyproject_false
        mock_json_load.return_value = {'version': '1.1.1'}
        results = setup_cz.get_current_version_info()
        assert results == ('1.1.1', f'{setup_cz.package_json}:version')

    @patch('pathlib.Path.exists', autospec=True)
    @patch('builtins.open', autospec=True)
    def test_other_exists(self, mock_open, mock_path_exists):
        mock_path_exists.side_effect = side_effect_pyproject_and_package_false
        mock_open.return_value.read.return_value.strip.return_value = '1.1.1'
        results = setup_cz.get_current_version_info()
        assert results == ('1.1.1', str(setup_cz.version_other))

    @patch('pathlib.Path.exists', return_value=False, autospec=True)
    @patch('builtins.open', autospec=True)
    def test_else(self, mock_open, mock_path_exists):
        results = setup_cz.get_current_version_info()
        assert results == (setup_cz.default_version, str(setup_cz.version_other))


class TestCzConfigTemplate:
    def test_template(self):
        version, version_file = '1.1.1', 'pyproject.toml:version'
        template = setup_cz.cz_config_template(version, version_file)
        assert isinstance(template, tomlkit.toml_document.TOMLDocument)
        assert tomlkit.dumps(template) == TEST_CZ_TEMPLATE
