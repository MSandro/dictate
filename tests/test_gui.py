"""Run with QT_QPA_PLATFORM=offscreen PYNPUT_BACKEND=dummy .venv/bin/python -m unittest discover -s tests -v."""
import unittest
from unittest.mock import patch

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

import core
import gui


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")

    def test_transcription_uses_theme_text_and_background(self):
        original = self.app.palette()
        self.addCleanup(self.app.setPalette, original)
        for background, foreground in (("#ffffff", "#202020"), ("#202020", "#ffffff")):
            with self.subTest(background=background):
                palette = QPalette(original)
                palette.setColor(QPalette.ColorRole.Base, QColor(background))
                palette.setColor(QPalette.ColorRole.Window, QColor(background))
                palette.setColor(QPalette.ColorRole.Text, QColor(foreground))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(foreground))
                self.app.setPalette(palette)
                with patch.object(core, "load_config", return_value=dict(core.DEFAULT_CONFIG)), \
                        patch.object(core, "provider_key", return_value="configured"), \
                        patch.object(gui.MainWindow, "start_listener"), \
                        patch.object(gui.MainWindow, "_preload_local_if_needed"), \
                        patch.object(gui.QSystemTrayIcon, "isSystemTrayAvailable", return_value=False):
                    window = gui.MainWindow()
                try:
                    window.last.setPlainText("Fachwörter: Kubernetes, Deployments, Grüße, äöüß, yz?")
                    window.show()
                    self.app.processEvents()
                    actual = window.last.palette()
                    self.assertEqual(actual.color(QPalette.ColorRole.Base).name(), background)
                    self.assertEqual(actual.color(QPalette.ColorRole.Text).name(), foreground)
                    self.assertEqual(window.info_label.palette().color(QPalette.ColorRole.WindowText).name(), foreground)
                finally:
                    window.close()

    def test_paste_shortcut_round_trips_through_settings(self):
        for shortcut in ("ctrl+v", "ctrl+shift+v"):
            with self.subTest(shortcut=shortcut):
                cfg = dict(core.DEFAULT_CONFIG, paste_shortcut=shortcut)
                dialog = gui.SettingsDialog(cfg)
                try:
                    self.assertEqual(dialog.values()["paste_shortcut"], shortcut)
                finally:
                    dialog.close()


if __name__ == "__main__":
    unittest.main()
