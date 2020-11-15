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
version_files = ["README.md:version-badge", "pyproject.toml:version"]
\n"""


@patch('bin.setup_cz.Path.exists', return_value=False, autospec=True)
class TestMain:
    @patch('bin.setup_cz.is_cz_in_toml', return_value=True, autospec=True)
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_pyproject_exist_and_configured(self, mock_add_cz_config, mock_is_cz_in_toml, mock_path_exists):
        with patch('bin.setup_cz._pyproject_exists', return_value=True, autospec=True):
            setup_cz.main()
            mock_add_cz_config.assert_not_called()

    @patch('bin.setup_cz.is_cz_in_toml', return_value=False, autospec=True)
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_pyproject_exist_and_not_configured(self, mock_add_cz_config, mock_is_cz_in_toml, mock_path_exists):
        with patch('bin.setup_cz._pyproject_exists', return_value=True, autospec=True):
            setup_cz.main()
            mock_add_cz_config.assert_called_with(setup_cz.pyproject)

    @patch('bin.setup_cz.is_cz_in_toml', return_value=True, autospec=True)
    @patch('logging.info', autospec=True)
    def test_cz_toml_exist_and_configured(self, mock_logging_info, mock_is_cz_in_toml, mock_path_exists):
        with patch('bin.setup_cz._cz_toml_exists', return_value=True, autospec=True) as mock_cz_exists:
            setup_cz.main()
            mock_cz_exists.assert_called_once()
            mock_logging_info.assert_called()

    @patch('bin.setup_cz.is_cz_in_toml', return_value=False, autospec=True)
    @patch('logging.error', autospec=True)
    def test_cz_toml_exist_and_not_configured(self, mock_logging_error, mock_is_cz_in_toml, mock_path_exists):
        with patch('bin.setup_cz._cz_toml_exists', return_value=True, autospec=True) as mock_cz_exists:
            with pytest.raises(SystemExit):
                setup_cz.main()
                mock_cz_exists.assert_called_once()
                mock_logging_error.assert_called()

    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_else(self, mock_add_cz_config, mock_path_exists):
        setup_cz.main()
        mock_add_cz_config.assert_called_with(setup_cz.cz_toml)


class TestCzInToml:
    toml_configured = {'tool': {'commitizen': {'name': 'test'}}}
    toml_not_configured = {'tool': {'poetry': {'name': 'test'}}}

    @pytest.mark.parametrize('test_input, expected', [(toml_configured, True), (toml_not_configured, False)])
    @patch('bin.setup_cz.tomlkit.loads', autospec=True)
    @patch('builtins.open', autospec=True)
    def test_cz_is_in_toml(self, mock_open, mock_tomlkit_loads, test_input, expected):
        mock_tomlkit_loads.return_value = test_input
        assert setup_cz.is_cz_in_toml('toml_file_configured') is expected


@patch('bin.setup_cz.Path.exists', return_value=False, autospec=True)
@patch('builtins.open', autospec=True)
class TestGetCurrentVersion:
    @patch('bin.setup_cz.tomlkit.loads', autospec=True)
    def test_pyproject_exists(self, mock_tomlkit_loads, mock_open, mock_path_exists):
        with patch('bin.setup_cz._pyproject_exists', return_value=True, autospec=True):
            mock_tomlkit_loads.return_value = {'tool': {'poetry': {'version': '1.1.1'}}}
            results = setup_cz.get_current_version_info()
            assert results == ('1.1.1', f'{setup_cz.pyproject}:version')

    @patch('bin.setup_cz.json.load', autospec=True)
    def test_package_json_exists(self, mock_json_load, mock_open, mock_path_exists):
        with patch('bin.setup_cz._package_json_exists', return_value=True, autospec=True):
            mock_json_load.return_value = {'version': '1.1.1'}
            results = setup_cz.get_current_version_info()
            assert results == ('1.1.1', f'{setup_cz.package_json}:version')

    def test_other_exists(self, mock_open, mock_path_exists):
        with patch('bin.setup_cz._version_other_exists', return_value=True, autospec=True):
            mock_open.return_value.read.return_value.strip.return_value = '1.1.1'
            results = setup_cz.get_current_version_info()
            assert results == ('1.1.1', str(setup_cz.version_other))

    def test_else(self, mock_open, mock_path_exists):
        results = setup_cz.get_current_version_info()
        assert results == (setup_cz.default_version, str(setup_cz.version_other))


class TestGetCzConfig:
    def test_template(self):
        version, version_file = '1.1.1', 'pyproject.toml:version'
        template = setup_cz.get_cz_config(version, version_file)
        assert isinstance(template, tomlkit.toml_document.TOMLDocument)
        assert tomlkit.dumps(template) == TEST_CZ_TEMPLATE


class TestMergeCurrentAndCz:
    @pytest.fixture
    def init_configs(self):
        return tomlkit.document(), tomlkit.document()

    def test_merge_empty_docs(self, init_configs):
        merged = setup_cz.merge_current_and_cz(init_configs[0], init_configs[1])
        assert merged == tomlkit.document()

    def test_merge_docs(self, init_configs):
        init_configs[0].add('test_0', '0')
        init_configs[1].add('test_1', '1')
        merged = setup_cz.merge_current_and_cz(init_configs[0], init_configs[1])
        assert merged == {'test_0': '0', 'test_1': '1'}
