from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from mpf.commands import game, migrate


class TestCommands(TestCase):

    def test_game(self):
        loader_mock = MagicMock()

        with patch("mpf.commands.game.signal"):
            with patch("mpf.commands.game.logging"):
                with patch("mpf.commands.game.os"):
                    with patch("mpf.commands.game.sys") as sys:
                        with patch("mpf.commands.game.MachineController") as controller:
                            with patch("mpf.commands.game.YamlMultifileConfigLoader", return_value=loader_mock):
                                with patch("asciimatics.screen.Screen.open"):
                                    game.Command("test", "machine", "")
                                    loader_mock.load_mpf_config.assert_called_once_with()
                                    self.assertEqual(loader_mock.load_mpf_config(), controller.call_args[0][1])
                                    sys.exit.assert_called_once_with()
                                    self.assertEqual(call(), sys.exit.call_args)

    def test_migrate(self):
        with patch("mpf.commands.migrate.logging"):
            with patch("mpf.commands.migrate.os"):
                with patch("mpf.commands.migrate.Migrator") as cmd:
                    migrate.Command("test", "machine", "")
                    cmd.assert_called_with("test", "machine")
