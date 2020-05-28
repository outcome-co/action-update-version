"""Test module Setup Commitizen."""

from unittest.mock import patch

import pytest

from bin import setup_cz


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
        def side_effect(arg):  # noqa: WPS430
            if arg == setup_cz.pyproject:
                return False
            return True

        mock_path_exists.side_effect = side_effect
        setup_cz.main()
        mock_logging_info.assert_called()

    @patch('pathlib.Path.exists', autospec=True)
    @patch('bin.setup_cz.is_cz_in_toml', return_value=False, autospec=True)
    @patch('logging.error', autospec=True)
    def test_cz_toml_exist_and_not_configured(self, mock_logging_error, mock_is_cz_in_toml, mock_path_exists):
        def side_effect(arg):  # noqa: WPS430
            if arg == setup_cz.pyproject:
                return False
            return True

        mock_path_exists.side_effect = side_effect
        with pytest.raises(SystemExit):
            setup_cz.main()
            mock_logging_error.assert_called()

    @patch('pathlib.Path.exists', return_value=False, autospec=True)
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    def test_else(self, mock_add_cz_config, mock_path_exists):
        setup_cz.main()
        mock_add_cz_config.assert_called_with(setup_cz.cz_toml)


class TestCzInToml:
    test_toml_file_configured = {'tool': {'commitizen': {'name': 'test'}}}
    test_toml_file_not_configured = {'tool': {'poetry': {'name': 'test'}}}

    @patch('toml.load', return_value=test_toml_file_configured, autospec=True)
    def test_cz_is_in_toml(self, mock_toml_load):
        assert setup_cz.is_cz_in_toml('toml_file_configured') is True

    @patch('toml.load', return_value=test_toml_file_not_configured, autospec=True)
    def test_cz_is_not_in_toml(self, mock_toml_load):
        assert setup_cz.is_cz_in_toml('toml_file_not_configured') is False
