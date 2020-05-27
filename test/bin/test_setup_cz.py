"""Test module Setup Commitizen."""

from unittest.mock import patch

from bin import setup_cz


class TestSetupCz:
    @patch('bin.setup_cz.add_cz_config', autospec=True)
    @patch('bin.setup_cz.is_cz_config_needed', return_value=True, autospec=True)
    def test_setup_pyproject(self, mock_is_cz_config_needed, mock_add_cz_config):
        setup_cz.setup_cz()
        mock_add_cz_config.assert_called_with(setup_cz.pyproject)

    @patch('bin.setup_cz.add_cz_config', autospec=True)
    @patch('bin.setup_cz.is_cz_config_needed', autospec=True)
    def test_setup_cz_toml(self, mock_is_cz_config_needed, mock_add_cz_config):
        def side_effect(arg):  # noqa: WPS430
            if arg == setup_cz.pyproject:
                return False
            return True

        mock_is_cz_config_needed.side_effect = side_effect
        setup_cz.setup_cz()
        mock_add_cz_config.assert_called_with(setup_cz.cz_toml)

    @patch('bin.setup_cz.add_cz_config', autospec=True)
    @patch('bin.setup_cz.is_cz_config_needed', return_value=False, autospec=True)
    def test_setup_other(self, mock_is_cz_config_needed, mock_add_cz_config):
        setup_cz.setup_cz()
        mock_add_cz_config.assert_called_with(setup_cz.cz_toml)
